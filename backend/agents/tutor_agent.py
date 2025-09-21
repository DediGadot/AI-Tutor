#!/usr/bin/env python3
"""
Hebrew AI Tutor Agent - LangGraph Implementation
Implements the Planner → Projector → Coach → Grader state machine using LangGraph.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional, List, TypedDict
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

from langgraph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from services.litellm_client import LiteLLMClient, ModelType
from services.database import DatabaseService
from utils.hebrew_utils import HebrewTextProcessor

logger = logging.getLogger(__name__)


class TutorState(TypedDict):
    """State structure for the tutor agent."""
    # Session information
    session_id: str
    student_nickname: str
    theme: str
    lesson_id: Optional[str]
    difficulty_level: int

    # Current lesson state
    lesson_plan: Optional[Dict[str, Any]]
    current_milestone: int
    milestones: List[Dict[str, Any]]
    milestone_status: Dict[str, str]  # milestone_id -> status

    # Student code and progress
    current_code: str
    test_results: Optional[Dict[str, Any]]
    hint_count: int
    attempt_count: int

    # Feedback and grading
    last_feedback: str
    last_hint: str
    xp_earned: int
    badges_earned: List[str]

    # Agent flow control
    current_node: str
    next_action: str
    error_message: Optional[str]
    completed: bool

    # Metadata
    created_at: str
    last_updated: str
    mastery_data: Dict[str, Any]


@dataclass
class MilestoneResult:
    """Result of milestone evaluation."""
    success: bool
    feedback: str
    xp_awarded: int
    badge_earned: Optional[str] = None
    next_milestone: Optional[Dict[str, Any]] = None
    concepts_learned: List[str] = None


class TutorAgent:
    """Main tutor agent implementing the educational flow."""

    def __init__(
        self,
        llm_client: LiteLLMClient,
        database: DatabaseService,
        hebrew_processor: HebrewTextProcessor,
        config: Dict[str, Any]
    ):
        """Initialize the tutor agent."""
        self.llm_client = llm_client
        self.database = database
        self.hebrew_processor = hebrew_processor
        self.config = config

        # Create the state graph
        self.graph = self._create_graph()

        # Active sessions
        self.active_sessions: Dict[str, TutorState] = {}

        # Metrics
        self.session_count = 0
        self.milestone_completions = 0
        self.hint_requests = 0

        logger.info("✅ TutorAgent initialized with LangGraph state machine")

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state machine."""
        graph = StateGraph(TutorState)

        # Add nodes for each agent role
        graph.add_node("planner", self._planner_node)
        graph.add_node("projector", self._projector_node)
        graph.add_node("coach", self._coach_node)
        graph.add_node("grader", self._grader_node)
        graph.add_node("session_manager", self._session_manager_node)

        # Set entry point
        graph.set_entry_point("session_manager")

        # Define transitions
        graph.add_edge("session_manager", "planner")
        graph.add_edge("planner", "projector")
        graph.add_edge("projector", "coach")
        graph.add_edge("coach", "grader")

        # Conditional edges from grader
        graph.add_conditional_edges(
            "grader",
            self._grader_decision,
            {
                "continue": "projector",  # Next milestone
                "hint": "coach",          # Need hint
                "complete": END           # Session complete
            }
        )

        return graph.compile()

    async def initialize(self):
        """Initialize the agent."""
        logger.info("🔄 Initializing TutorAgent...")
        # Additional initialization if needed
        logger.info("✅ TutorAgent initialization complete")

    async def shutdown(self):
        """Shutdown the agent."""
        logger.info("🔄 Shutting down TutorAgent...")
        # Save any active sessions
        for session_id, state in self.active_sessions.items():
            await self._save_session_state(session_id, state)
        self.active_sessions.clear()
        logger.info("✅ TutorAgent shutdown complete")

    def is_healthy(self) -> bool:
        """Check if the agent is healthy."""
        return (
            self.llm_client is not None and
            self.database is not None and
            self.graph is not None
        )

    async def start_session(
        self,
        student_nickname: str,
        theme: str,
        lesson_id: Optional[str] = None,
        difficulty_level: int = 1
    ) -> Dict[str, Any]:
        """Start a new tutoring session."""
        session_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create initial state
        initial_state: TutorState = {
            "session_id": session_id,
            "student_nickname": student_nickname,
            "theme": theme,
            "lesson_id": lesson_id,
            "difficulty_level": difficulty_level,
            "lesson_plan": None,
            "current_milestone": 0,
            "milestones": [],
            "milestone_status": {},
            "current_code": "",
            "test_results": None,
            "hint_count": 0,
            "attempt_count": 0,
            "last_feedback": "",
            "last_hint": "",
            "xp_earned": 0,
            "badges_earned": [],
            "current_node": "session_manager",
            "next_action": "start",
            "error_message": None,
            "completed": False,
            "created_at": timestamp,
            "last_updated": timestamp,
            "mastery_data": {}
        }

        try:
            logger.info(f"Starting session {session_id} for {student_nickname}, theme: {theme}")

            # Run the initial flow through the graph
            result = await self.graph.ainvoke(initial_state)

            # Store the session
            self.active_sessions[session_id] = result
            await self._save_session_state(session_id, result)

            # Update metrics
            self.session_count += 1

            # Prepare response
            return {
                "session_id": session_id,
                "lesson_plan": result["lesson_plan"],
                "first_milestone": result["milestones"][0] if result["milestones"] else None,
                "welcome_message": f"ברוך הבא {student_nickname}! בוא נתחיל ללמוד תכנות עם {theme}!"
            }

        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            raise

    async def process_code_submission(
        self,
        session_id: str,
        milestone_id: str,
        code: str,
        test_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a code submission for evaluation."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        state = self.active_sessions[session_id]

        # Update state with new code and test results
        state["current_code"] = code
        state["test_results"] = test_results
        state["attempt_count"] += 1
        state["next_action"] = "evaluate"
        state["last_updated"] = datetime.now(timezone.utc).isoformat()

        try:
            # Process through grader
            result = await self._grader_node(state)

            # Update session
            self.active_sessions[session_id] = result
            await self._save_session_state(session_id, result)

            # Prepare response
            response = {
                "success": result.get("milestone_completed", False),
                "feedback": result["last_feedback"],
                "hint": result["last_hint"] if result["last_hint"] else None,
                "xp_awarded": result.get("xp_awarded_this_turn", 0),
                "badge_earned": result.get("badge_earned_this_turn"),
                "next_milestone": None
            }

            # If milestone completed, get next milestone
            if response["success"] and result["current_milestone"] < len(result["milestones"]):
                response["next_milestone"] = result["milestones"][result["current_milestone"]]

            return response

        except Exception as e:
            logger.error(f"Failed to process code submission: {e}")
            raise

    async def get_hint(
        self,
        session_id: str,
        milestone_id: str,
        current_code: str
    ) -> Dict[str, str]:
        """Get a hint for the current milestone."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        state = self.active_sessions[session_id]
        state["current_code"] = current_code
        state["next_action"] = "hint"

        try:
            # Process through coach
            result = await self._coach_node(state)

            # Update session
            self.active_sessions[session_id] = result
            await self._save_session_state(session_id, result)

            # Update metrics
            self.hint_requests += 1

            max_hints = self.config.get("hints", {}).get("max_hints_per_milestone", 3)

            return {
                "hint": result["last_hint"],
                "hint_count": result["hint_count"],
                "max_hints_reached": result["hint_count"] >= max_hints
            }

        except Exception as e:
            logger.error(f"Failed to get hint: {e}")
            raise

    async def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get current session progress."""
        if session_id not in self.active_sessions:
            # Try to load from database
            state = await self._load_session_state(session_id)
            if not state:
                raise ValueError(f"Session {session_id} not found")
        else:
            state = self.active_sessions[session_id]

        return {
            "session_id": session_id,
            "student_nickname": state["student_nickname"],
            "theme": state["theme"],
            "current_milestone": state["current_milestone"],
            "total_milestones": len(state["milestones"]),
            "xp_earned": state["xp_earned"],
            "badges_earned": state["badges_earned"],
            "milestone_status": state["milestone_status"],
            "completed": state["completed"],
            "last_updated": state["last_updated"]
        }

    async def complete_session(self, session_id: str) -> Dict[str, Any]:
        """Complete a tutoring session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        state = self.active_sessions[session_id]
        state["completed"] = True
        state["last_updated"] = datetime.now(timezone.utc).isoformat()

        # Save final state
        await self._save_session_state(session_id, state)

        # Remove from active sessions
        del self.active_sessions[session_id]

        return {
            "session_id": session_id,
            "completed": True,
            "final_xp": state["xp_earned"],
            "badges_earned": state["badges_earned"],
            "milestones_completed": sum(1 for status in state["milestone_status"].values() if status == "completed")
        }

    # LangGraph Node Implementations

    async def _session_manager_node(self, state: TutorState) -> TutorState:
        """Manage session initialization and routing."""
        logger.info(f"Session Manager: {state['next_action']}")

        if state["next_action"] == "start":
            # Initialize new session
            state["current_node"] = "session_manager"
            state["next_action"] = "plan"

        return state

    async def _planner_node(self, state: TutorState) -> TutorState:
        """Generate lesson plan for the session."""
        logger.info(f"Planner: Creating lesson plan for {state['theme']}")

        try:
            # Get student's previous concepts from mastery data
            previous_concepts = list(state["mastery_data"].keys())

            # Generate lesson plan using LLM
            lesson_plan = await self.llm_client.generate_lesson_plan(
                theme=state["theme"],
                difficulty=state["difficulty_level"],
                previous_concepts=previous_concepts
            )

            state["lesson_plan"] = lesson_plan
            state["milestones"] = lesson_plan.get("milestones", [])
            state["current_milestone"] = 0
            state["current_node"] = "planner"

            logger.info(f"Lesson plan created with {len(state['milestones'])} milestones")

        except Exception as e:
            logger.error(f"Planner failed: {e}")
            state["error_message"] = f"Failed to create lesson plan: {str(e)}"

        return state

    async def _projector_node(self, state: TutorState) -> TutorState:
        """Project the current milestone and setup tests."""
        logger.info(f"Projector: Setting up milestone {state['current_milestone']}")

        try:
            if state["current_milestone"] < len(state["milestones"]):
                current_milestone = state["milestones"][state["current_milestone"]]

                # Initialize milestone status if not exists
                milestone_id = current_milestone.get("id", f"milestone_{state['current_milestone']}")
                if milestone_id not in state["milestone_status"]:
                    state["milestone_status"][milestone_id] = "active"

                state["current_node"] = "projector"
                logger.info(f"Milestone {milestone_id} is now active")

            else:
                # All milestones completed
                state["completed"] = True
                state["next_action"] = "complete"

        except Exception as e:
            logger.error(f"Projector failed: {e}")
            state["error_message"] = f"Failed to setup milestone: {str(e)}"

        return state

    async def _coach_node(self, state: TutorState) -> TutorState:
        """Provide hints and coaching."""
        logger.info(f"Coach: Providing guidance (hint #{state['hint_count'] + 1})")

        try:
            if state["current_milestone"] < len(state["milestones"]):
                current_milestone = state["milestones"][state["current_milestone"]]
                milestone_goal = current_milestone.get("goal_he", "")

                # Generate hint
                hint = await self.llm_client.generate_hint(
                    student_code=state["current_code"],
                    milestone_goal=milestone_goal,
                    hint_count=state["hint_count"]
                )

                state["last_hint"] = hint
                state["hint_count"] += 1
                state["current_node"] = "coach"

                logger.info(f"Hint provided: {hint[:50]}...")

        except Exception as e:
            logger.error(f"Coach failed: {e}")
            state["error_message"] = f"Failed to generate hint: {str(e)}"

        return state

    async def _grader_node(self, state: TutorState) -> TutorState:
        """Grade the submitted code and provide feedback."""
        logger.info(f"Grader: Evaluating submission for milestone {state['current_milestone']}")

        try:
            if state["current_milestone"] < len(state["milestones"]):
                current_milestone = state["milestones"][state["current_milestone"]]
                milestone_goal = current_milestone.get("goal_he", "")

                # Grade the submission
                grading_result = await self.llm_client.grade_submission(
                    student_code=state["current_code"],
                    test_results=state["test_results"] or {},
                    milestone_goal=milestone_goal
                )

                # Update state based on grading
                state["last_feedback"] = grading_result.get("feedback", "")
                xp_awarded = grading_result.get("xp_awarded", 0)
                state["xp_earned"] += xp_awarded
                state["xp_awarded_this_turn"] = xp_awarded

                # Check if milestone completed
                if grading_result.get("success", False):
                    milestone_id = current_milestone.get("id", f"milestone_{state['current_milestone']}")
                    state["milestone_status"][milestone_id] = "completed"
                    state["current_milestone"] += 1
                    state["milestone_completed"] = True
                    state["hint_count"] = 0  # Reset hint count for next milestone

                    # Update metrics
                    self.milestone_completions += 1

                    # Check for badge
                    concepts_learned = grading_result.get("concepts_learned", [])
                    for concept in concepts_learned:
                        if concept not in state["badges_earned"]:
                            state["badges_earned"].append(concept)
                            state["badge_earned_this_turn"] = concept

                    logger.info(f"Milestone {milestone_id} completed! XP: +{xp_awarded}")
                else:
                    state["milestone_completed"] = False
                    logger.info("Milestone not yet completed")

                state["current_node"] = "grader"

        except Exception as e:
            logger.error(f"Grader failed: {e}")
            state["error_message"] = f"Failed to grade submission: {str(e)}"

        return state

    def _grader_decision(self, state: TutorState) -> str:
        """Decide next action after grading."""
        if state.get("completed", False):
            return "complete"
        elif state.get("milestone_completed", False):
            return "continue"  # Next milestone
        else:
            return "hint"  # Need help

    async def _save_session_state(self, session_id: str, state: TutorState):
        """Save session state to database."""
        try:
            await self.database.save_session(session_id, state)
        except Exception as e:
            logger.error(f"Failed to save session state: {e}")

    async def _load_session_state(self, session_id: str) -> Optional[TutorState]:
        """Load session state from database."""
        try:
            return await self.database.load_session(session_id)
        except Exception as e:
            logger.error(f"Failed to load session state: {e}")
            return None

    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed agent status."""
        return {
            "healthy": self.is_healthy(),
            "active_sessions": len(self.active_sessions),
            "total_sessions": self.session_count,
            "milestone_completions": self.milestone_completions,
            "hint_requests": self.hint_requests,
            "llm_metrics": self.llm_client.get_metrics(),
            "graph_compiled": self.graph is not None
        }