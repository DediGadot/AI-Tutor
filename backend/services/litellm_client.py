#!/usr/bin/env python3
"""
LiteLLM Client Service
Handles communication with the LiteLLM proxy for model routing and management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from dataclasses import dataclass
import httpx
import json
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Model types for different tasks."""
    PLANNING = "planning"
    COACHING = "coaching"
    GRADING = "grading"
    CREATIVE = "creative"


@dataclass
class LLMRequest:
    """Request structure for LLM calls."""
    model_type: ModelType
    messages: List[Dict[str, str]]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Response structure from LLM calls."""
    content: str
    model_used: str
    tokens_used: int
    cost: Optional[float] = None
    latency_ms: int = 0
    metadata: Optional[Dict[str, Any]] = None


class LiteLLMClient:
    """Client for interacting with LiteLLM proxy."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize LiteLLM client with configuration."""
        self.config = config
        self.proxy_url = config.get("proxy_url", "http://localhost:4000")
        self.model_routing = config.get("routing", {})
        self.default_model = config.get("default_model", "gpt-4")

        # HTTP client for API calls
        self.http_client: Optional[httpx.AsyncClient] = None

        # Health status
        self._is_healthy = False

        # Metrics tracking
        self.request_count = 0
        self.error_count = 0
        self.total_tokens = 0

    async def initialize(self):
        """Initialize the LiteLLM client."""
        try:
            # Create HTTP client
            self.http_client = httpx.AsyncClient(
                base_url=self.proxy_url,
                timeout=httpx.Timeout(timeout=30.0),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.config.get('api_key', 'default-key')}"
                }
            )

            # Test connection
            await self._test_connection()
            self._is_healthy = True

            logger.info(f"✅ LiteLLM client initialized successfully with proxy at {self.proxy_url}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize LiteLLM client: {e}")
            self._is_healthy = False
            raise

    async def shutdown(self):
        """Shutdown the LiteLLM client."""
        if self.http_client:
            await self.http_client.aclose()
        self._is_healthy = False
        logger.info("✅ LiteLLM client shutdown complete")

    async def health_check(self) -> bool:
        """Check if the LiteLLM proxy is healthy."""
        try:
            if not self.http_client:
                return False

            response = await self.http_client.get("/health")
            return response.status_code == 200

        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    def _get_model_for_task(self, model_type: ModelType) -> str:
        """Get the appropriate model for a given task type."""
        return self.model_routing.get(model_type.value, self.default_model)

    async def _test_connection(self):
        """Test connection to LiteLLM proxy."""
        try:
            response = await self.http_client.get("/health")
            if response.status_code != 200:
                raise Exception(f"Health check failed: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to connect to LiteLLM proxy: {e}")

    async def chat_completion(self, request: LLMRequest) -> LLMResponse:
        """Make a chat completion request through LiteLLM proxy."""
        if not self.http_client:
            raise Exception("LiteLLM client not initialized")

        try:
            # Get the appropriate model for this task
            model = self._get_model_for_task(request.model_type)

            # Prepare request payload
            payload = {
                "model": model,
                "messages": request.messages,
                "max_tokens": request.max_tokens or self.config.get("max_tokens", 1000),
                "temperature": request.temperature or self.config.get("temperature", 0.7),
                "stream": request.stream,
            }

            # Add optional parameters
            if request.user_id:
                payload["user"] = request.user_id

            # Add metadata for tracking
            if request.metadata:
                payload["metadata"] = request.metadata

            # Make the request
            start_time = asyncio.get_event_loop().time()

            if request.stream:
                return await self._handle_streaming_response(payload, start_time)
            else:
                return await self._handle_regular_response(payload, start_time)

        except Exception as e:
            self.error_count += 1
            logger.error(f"Chat completion failed: {e}")
            raise

    async def _handle_regular_response(self, payload: Dict[str, Any], start_time: float) -> LLMResponse:
        """Handle regular (non-streaming) response."""
        response = await self.http_client.post("/chat/completions", json=payload)

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

        result = response.json()
        latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)

        # Extract response data
        content = result["choices"][0]["message"]["content"]
        model_used = result.get("model", payload["model"])
        tokens_used = result.get("usage", {}).get("total_tokens", 0)

        # Update metrics
        self.request_count += 1
        self.total_tokens += tokens_used

        return LLMResponse(
            content=content,
            model_used=model_used,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            metadata=result.get("metadata", {})
        )

    async def _handle_streaming_response(self, payload: Dict[str, Any], start_time: float) -> AsyncGenerator[str, None]:
        """Handle streaming response (for real-time chat)."""
        async with self.http_client.stream("POST", "/chat/completions", json=payload) as response:
            if response.status_code != 200:
                raise Exception(f"Streaming request failed: {response.status_code}")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta:
                            yield delta["content"]
                    except (json.JSONDecodeError, KeyError):
                        continue

    async def generate_lesson_plan(self, theme: str, difficulty: int, previous_concepts: List[str]) -> Dict[str, Any]:
        """Generate a lesson plan using the planning model."""
        messages = [
            {
                "role": "system",
                "content": self.config.get("prompts", {}).get("planner", {}).get("system", "").format(
                    theme=theme,
                    difficulty=difficulty,
                    previous_concepts=", ".join(previous_concepts)
                )
            },
            {
                "role": "user",
                "content": f"צור תוכנית שיעור בנושא {theme} ברמת קושי {difficulty}"
            }
        ]

        request = LLMRequest(
            model_type=ModelType.PLANNING,
            messages=messages,
            temperature=0.8,
            metadata={"task": "lesson_planning", "theme": theme, "difficulty": difficulty}
        )

        response = await self.chat_completion(request)

        try:
            # Parse the lesson plan JSON from the response
            return json.loads(response.content)
        except json.JSONDecodeError:
            # If JSON parsing fails, return a structured error
            logger.warning("Failed to parse lesson plan JSON, returning structured response")
            return {
                "error": "Failed to parse lesson plan",
                "raw_response": response.content,
                "model_used": response.model_used
            }

    async def generate_hint(self, student_code: str, milestone_goal: str, hint_count: int) -> str:
        """Generate a helpful hint using the coaching model."""
        system_prompt = self.config.get("prompts", {}).get("coach", {}).get("system", "")

        if hint_count == 0:
            hint_type = "gentle"
        elif hint_count <= 2:
            hint_type = "progressive"
        else:
            hint_type = "final"

        hint_template = self.config.get("prompts", {}).get("coach", {}).get("hints", {}).get(hint_type, "{hint}")

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""
המטרה: {milestone_goal}
הקוד הנוכחי של התלמיד:
```javascript
{student_code}
```

זה הרמז מספר {hint_count + 1}. תן רמז מתאים ברמה זו:
- רמז 1-2: עדין ומכוון
- רמז 3+: יותר מפורט עם דוגמה
"""
            }
        ]

        request = LLMRequest(
            model_type=ModelType.COACHING,
            messages=messages,
            temperature=0.6,
            metadata={"task": "hint_generation", "hint_count": hint_count}
        )

        response = await self.chat_completion(request)
        return response.content

    async def grade_submission(self, student_code: str, test_results: Dict[str, Any], milestone_goal: str) -> Dict[str, Any]:
        """Grade a code submission using the grading model."""
        system_prompt = self.config.get("prompts", {}).get("grader", {}).get("system", "")

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"""
בדוק את קוד התלמיד:

מטרת הציון דרך: {milestone_goal}

קוד התלמיד:
```javascript
{student_code}
```

תוצאות הבדיקות:
{json.dumps(test_results, ensure_ascii=False, indent=2)}

החזר מבנה JSON עם:
- success: true/false
- feedback: משוב בעברית
- xp_awarded: נקודות ניסיון (0-25)
- concepts_learned: רשימת מושגים שנלמדו
"""
            }
        ]

        request = LLMRequest(
            model_type=ModelType.GRADING,
            messages=messages,
            temperature=0.3,
            metadata={"task": "code_grading"}
        )

        response = await self.chat_completion(request)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback response if JSON parsing fails
            return {
                "success": False,
                "feedback": "שגיאה בעיבוד התוצאה. נסה שוב.",
                "xp_awarded": 0,
                "concepts_learned": [],
                "error": "JSON parsing failed",
                "raw_response": response.content
            }

    async def generate_creative_content(self, theme: str, content_type: str) -> Dict[str, Any]:
        """Generate creative content (scenarios, examples) using the creative model."""
        messages = [
            {
                "role": "system",
                "content": f"Generate creative {content_type} content for {theme} theme for 5th grade students"
            },
            {
                "role": "user",
                "content": f"Create engaging {content_type} content for the {theme} theme that will help students learn programming concepts"
            }
        ]

        request = LLMRequest(
            model_type=ModelType.CREATIVE,
            messages=messages,
            temperature=0.9,
            metadata={"task": "creative_generation", "theme": theme, "content_type": content_type}
        )

        response = await self.chat_completion(request)

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "content": response.content,
                "theme": theme,
                "content_type": content_type,
                "model_used": response.model_used
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics."""
        return {
            "is_healthy": self._is_healthy,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "total_tokens": self.total_tokens,
            "error_rate": self.error_count / max(self.request_count, 1),
            "proxy_url": self.proxy_url
        }