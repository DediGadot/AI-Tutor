#!/usr/bin/env python3
"""
Hebrew AI Tutor - Main FastAPI Application
Integrates LiteLLM proxy with LangGraph agents for educational Hebrew tutoring.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

import yaml
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import our custom modules
from agents.tutor_agent import TutorAgent
from services.litellm_client import LiteLLMClient
from services.database import DatabaseService
from models.lesson_models import LessonRequest, LessonResponse, MilestoneResult
from utils.config_loader import load_config
from utils.hebrew_utils import HebrewTextProcessor
from utils.monitoring import MetricsCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
config: Dict[str, Any] = {}
litellm_client: Optional[LiteLLMClient] = None
database_service: Optional[DatabaseService] = None
tutor_agent: Optional[TutorAgent] = None
metrics_collector: Optional[MetricsCollector] = None
hebrew_processor: Optional[HebrewTextProcessor] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management - startup and shutdown."""
    global config, litellm_client, database_service, tutor_agent, metrics_collector, hebrew_processor

    logger.info("🚀 Starting Hebrew AI Tutor Backend...")

    try:
        # Load configuration
        config = load_config()
        logger.info("✅ Configuration loaded")

        # Initialize services
        litellm_client = LiteLLMClient(config["llm"])
        await litellm_client.initialize()
        logger.info("✅ LiteLLM client initialized")

        database_service = DatabaseService(config["database"])
        await database_service.initialize()
        logger.info("✅ Database service initialized")

        hebrew_processor = HebrewTextProcessor()
        logger.info("✅ Hebrew text processor initialized")

        metrics_collector = MetricsCollector(config["monitoring"])
        await metrics_collector.initialize()
        logger.info("✅ Metrics collector initialized")

        # Initialize tutor agent with all dependencies
        tutor_agent = TutorAgent(
            llm_client=litellm_client,
            database=database_service,
            hebrew_processor=hebrew_processor,
            config=config["agent"]
        )
        await tutor_agent.initialize()
        logger.info("✅ Tutor agent initialized")

        logger.info("🎉 Hebrew AI Tutor Backend started successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize backend: {e}")
        raise

    yield

    # Shutdown
    logger.info("🔄 Shutting down Hebrew AI Tutor Backend...")

    if tutor_agent:
        await tutor_agent.shutdown()
    if database_service:
        await database_service.shutdown()
    if litellm_client:
        await litellm_client.shutdown()
    if metrics_collector:
        await metrics_collector.shutdown()

    logger.info("✅ Backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Hebrew AI Tutor",
    description="AI-powered Hebrew coding tutor for 5th grade students",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class SessionStartRequest(BaseModel):
    """Request to start a new tutoring session."""
    student_nickname: str = Field(..., min_length=1, max_length=50)
    theme: str = Field(..., pattern="^(football|space|robots)$")
    lesson_id: Optional[str] = None
    difficulty_level: int = Field(default=1, ge=1, le=5)


class SessionStartResponse(BaseModel):
    """Response when starting a new session."""
    session_id: str
    lesson_plan: Dict[str, Any]
    first_milestone: Dict[str, Any]
    message: str


class CodeSubmissionRequest(BaseModel):
    """Request to submit code for evaluation."""
    session_id: str
    milestone_id: str
    code: str
    test_results: Optional[Dict[str, Any]] = None


class CodeSubmissionResponse(BaseModel):
    """Response to code submission."""
    success: bool
    feedback: str
    hint: Optional[str] = None
    next_milestone: Optional[Dict[str, Any]] = None
    xp_awarded: int = 0
    badge_earned: Optional[str] = None


class HintRequest(BaseModel):
    """Request for a hint."""
    session_id: str
    milestone_id: str
    current_code: str


class HintResponse(BaseModel):
    """Response with a hint."""
    hint: str
    hint_count: int
    max_hints_reached: bool


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check all services
        health_status = {
            "status": "healthy",
            "services": {
                "litellm": await litellm_client.health_check() if litellm_client else False,
                "database": await database_service.health_check() if database_service else False,
                "agent": tutor_agent.is_healthy() if tutor_agent else False,
            },
            "timestamp": metrics_collector.get_timestamp() if metrics_collector else None
        }

        # Check if all services are healthy
        all_healthy = all(health_status["services"].values())
        if not all_healthy:
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# Tutoring session endpoints
@app.post("/api/sessions/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest, background_tasks: BackgroundTasks):
    """Start a new tutoring session."""
    try:
        logger.info(f"Starting session for {request.student_nickname}, theme: {request.theme}")

        # Track metrics
        if metrics_collector:
            background_tasks.add_task(
                metrics_collector.track_event,
                "session_started",
                {"theme": request.theme, "difficulty": request.difficulty_level}
            )

        # Create session using tutor agent
        session_result = await tutor_agent.start_session(
            student_nickname=request.student_nickname,
            theme=request.theme,
            lesson_id=request.lesson_id,
            difficulty_level=request.difficulty_level
        )

        return SessionStartResponse(
            session_id=session_result["session_id"],
            lesson_plan=session_result["lesson_plan"],
            first_milestone=session_result["first_milestone"],
            message=session_result["welcome_message"]
        )

    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@app.post("/api/sessions/submit-code", response_model=CodeSubmissionResponse)
async def submit_code(request: CodeSubmissionRequest, background_tasks: BackgroundTasks):
    """Submit code for evaluation and get feedback."""
    try:
        logger.info(f"Code submission for session {request.session_id}, milestone {request.milestone_id}")

        # Track metrics
        if metrics_collector:
            background_tasks.add_task(
                metrics_collector.track_event,
                "code_submitted",
                {"session_id": request.session_id, "milestone_id": request.milestone_id}
            )

        # Process code submission through tutor agent
        result = await tutor_agent.process_code_submission(
            session_id=request.session_id,
            milestone_id=request.milestone_id,
            code=request.code,
            test_results=request.test_results
        )

        # Track additional metrics based on result
        if metrics_collector:
            if result["success"]:
                background_tasks.add_task(
                    metrics_collector.track_event,
                    "milestone_completed",
                    {"session_id": request.session_id, "xp_awarded": result["xp_awarded"]}
                )
            else:
                background_tasks.add_task(
                    metrics_collector.track_event,
                    "code_evaluation_failed",
                    {"session_id": request.session_id}
                )

        return CodeSubmissionResponse(**result)

    except Exception as e:
        logger.error(f"Failed to process code submission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process code: {str(e)}")


@app.post("/api/sessions/hint", response_model=HintResponse)
async def get_hint(request: HintRequest, background_tasks: BackgroundTasks):
    """Get a hint for the current milestone."""
    try:
        logger.info(f"Hint requested for session {request.session_id}, milestone {request.milestone_id}")

        # Track metrics
        if metrics_collector:
            background_tasks.add_task(
                metrics_collector.track_event,
                "hint_requested",
                {"session_id": request.session_id, "milestone_id": request.milestone_id}
            )

        # Get hint from tutor agent
        hint_result = await tutor_agent.get_hint(
            session_id=request.session_id,
            milestone_id=request.milestone_id,
            current_code=request.current_code
        )

        return HintResponse(**hint_result)

    except Exception as e:
        logger.error(f"Failed to get hint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get hint: {str(e)}")


@app.get("/api/sessions/{session_id}/progress")
async def get_session_progress(session_id: str):
    """Get current session progress and statistics."""
    try:
        progress = await tutor_agent.get_session_progress(session_id)
        return progress

    except Exception as e:
        logger.error(f"Failed to get session progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@app.post("/api/sessions/{session_id}/complete")
async def complete_session(session_id: str, background_tasks: BackgroundTasks):
    """Complete a tutoring session."""
    try:
        logger.info(f"Completing session {session_id}")

        # Track metrics
        if metrics_collector:
            background_tasks.add_task(
                metrics_collector.track_event,
                "session_completed",
                {"session_id": session_id}
            )

        result = await tutor_agent.complete_session(session_id)
        return result

    except Exception as e:
        logger.error(f"Failed to complete session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")


# Admin and monitoring endpoints
@app.get("/api/admin/metrics")
async def get_metrics():
    """Get system metrics (admin only)."""
    if not metrics_collector:
        raise HTTPException(status_code=503, detail="Metrics collector not available")

    try:
        metrics = await metrics_collector.get_all_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@app.get("/api/admin/agent-status")
async def get_agent_status():
    """Get detailed agent status (admin only)."""
    if not tutor_agent:
        raise HTTPException(status_code=503, detail="Tutor agent not available")

    try:
        status = await tutor_agent.get_detailed_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with Hebrew-friendly error messages."""
    error_message = str(exc.detail)

    # Translate common errors to Hebrew if Hebrew processor is available
    if hebrew_processor:
        error_message = hebrew_processor.translate_error_message(error_message)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_message,
            "error_code": exc.status_code,
            "timestamp": metrics_collector.get_timestamp() if metrics_collector else None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}")

    error_message = "אירעה שגיאה בלתי צפויה. אנא נסה שוב."  # "An unexpected error occurred. Please try again."

    return JSONResponse(
        status_code=500,
        content={
            "error": error_message,
            "error_code": 500,
            "timestamp": metrics_collector.get_timestamp() if metrics_collector else None
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Load configuration for server settings
    try:
        config = load_config()
        api_config = config.get("api", {})

        uvicorn.run(
            "main:app",
            host=api_config.get("host", "0.0.0.0"),
            port=api_config.get("port", 8000),
            reload=api_config.get("reload", False),
            workers=api_config.get("workers", 1) if not api_config.get("reload") else None,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise