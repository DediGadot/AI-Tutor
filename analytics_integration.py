"""
Hebrew AI Tutor - Analytics Integration System
Privacy-compliant tracking for learning effectiveness and user experience
"""

import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class EventType(Enum):
    LESSON_OPENED = "lesson_opened"
    MILESTONE_STARTED = "milestone_started"
    RUN_CLICKED = "run_clicked"
    TESTS_PASSED = "tests_passed"
    TESTS_FAILED = "tests_failed"
    HINT_REQUESTED = "hint_requested"
    HINT_AUTO_SHOWN = "hint_auto_shown"
    MILESTONE_COMPLETED = "milestone_completed"
    BADGE_AWARDED = "badge_awarded"
    SESSION_COMPLETED = "session_completed"
    STREAK_INCREMENTED = "streak_incremented"
    TTS_TOGGLED = "tts_toggled"
    THEME_CHANGED = "theme_changed"
    ACCESSIBILITY_FEATURE_USED = "accessibility_feature_used"
    ERROR_OCCURRED = "error_occurred"

class PrivacyLevel(Enum):
    ANONYMOUS = "anonymous"
    PSEUDONYMOUS = "pseudonymous"
    AGGREGATED_ONLY = "aggregated_only"

@dataclass
class AnalyticsEvent:
    event_type: EventType
    timestamp: datetime
    session_id: str
    user_pseudonym: str  # Hashed identifier, never PII
    properties: Dict[str, Any]
    privacy_level: PrivacyLevel = PrivacyLevel.PSEUDONYMOUS
    hebrew_context: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "user_id": self.user_pseudonym,
            "properties": self.properties,
            "privacy_level": self.privacy_level.value,
            "hebrew_context": self.hebrew_context or {}
        }

class AnalyticsProvider(ABC):
    """Abstract base class for analytics providers"""

    @abstractmethod
    async def track_event(self, event: AnalyticsEvent) -> bool:
        pass

    @abstractmethod
    async def track_page_view(self, path: str, title: str, properties: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def anonymize_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

class PostHogProvider(AnalyticsProvider):
    """PostHog analytics integration with privacy controls"""

    def __init__(self, api_key: str, host: str = "https://app.posthog.com"):
        self.api_key = api_key
        self.host = host.rstrip('/')
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Send event to PostHog with privacy-first approach"""
        try:
            session = await self._get_session()

            payload = {
                "api_key": self.api_key,
                "event": event.event_type.value,
                "properties": {
                    **event.properties,
                    "timestamp": event.timestamp.isoformat(),
                    "session_id": event.session_id,
                    "$set": {
                        "privacy_level": event.privacy_level.value,
                        "hebrew_interface": True,
                        "target_age_group": "grade_5"
                    }
                },
                "distinct_id": event.user_pseudonym
            }

            # Add Hebrew-specific context
            if event.hebrew_context:
                payload["properties"]["hebrew_context"] = event.hebrew_context

            # Privacy filtering
            payload = self.anonymize_user_data(payload)

            async with session.post(
                f"{self.host}/capture/",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                success = response.status == 200
                if not success:
                    logger.error(f"PostHog tracking failed: {response.status}")
                return success

        except Exception as e:
            logger.error(f"PostHog tracking error: {e}")
            return False

    async def track_page_view(self, path: str, title: str, properties: Dict[str, Any]) -> bool:
        """Track page views with Hebrew RTL context"""
        event_properties = {
            "$current_url": path,
            "$title": title,
            "language": "he",
            "text_direction": "rtl",
            **properties
        }

        page_view_event = AnalyticsEvent(
            event_type=EventType.LESSON_OPENED,  # Generic for page views
            timestamp=datetime.now(timezone.utc),
            session_id=properties.get("session_id", ""),
            user_pseudonym=properties.get("user_pseudonym", ""),
            properties=event_properties
        )

        return await self.track_event(page_view_event)

    def anonymize_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or hash any potentially identifying information"""
        # Remove IP tracking
        if "properties" in data:
            data["properties"]["$ip"] = None

        # Ensure user ID is already hashed
        if "distinct_id" in data and not data["distinct_id"].startswith("hash_"):
            data["distinct_id"] = f"hash_{hashlib.sha256(data['distinct_id'].encode()).hexdigest()[:16]}"

        return data

class MatomoProvider(AnalyticsProvider):
    """Matomo analytics with GDPR compliance"""

    def __init__(self, site_id: str, tracker_url: str, token_auth: Optional[str] = None):
        self.site_id = site_id
        self.tracker_url = tracker_url.rstrip('/')
        self.token_auth = token_auth
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Send event to Matomo with privacy controls"""
        try:
            session = await self._get_session()

            params = {
                "idsite": self.site_id,
                "rec": 1,
                "action_name": event.event_type.value,
                "url": f"https://hebrew-tutor.local/{event.event_type.value}",
                "cid": event.user_pseudonym[:16],  # Visitor ID (hashed)
                "rand": int(datetime.now().timestamp() * 1000000) % 1000000,
                "apiv": 1,
                "lang": "he",
                "send_image": 0,
                # Privacy settings
                "dp": 1,  # Disable cookies
                "cip": 1,  # Anonymize IP
            }

            # Add custom dimensions for Hebrew learning context
            if event.hebrew_context:
                params.update({
                    "dimension1": event.hebrew_context.get("concept", ""),
                    "dimension2": event.hebrew_context.get("theme", ""),
                    "dimension3": event.hebrew_context.get("difficulty", "")
                })

            # Event-specific tracking
            if event.event_type in [EventType.MILESTONE_COMPLETED, EventType.BADGE_AWARDED]:
                params.update({
                    "e_c": "Learning",
                    "e_a": event.event_type.value,
                    "e_n": event.properties.get("milestone_name", ""),
                    "e_v": event.properties.get("score", 0)
                })

            if self.token_auth:
                params["token_auth"] = self.token_auth

            params = self.anonymize_user_data(params)

            async with session.get(
                f"{self.tracker_url}/matomo.php",
                params=params
            ) as response:
                success = response.status == 200
                if not success:
                    logger.error(f"Matomo tracking failed: {response.status}")
                return success

        except Exception as e:
            logger.error(f"Matomo tracking error: {e}")
            return False

    async def track_page_view(self, path: str, title: str, properties: Dict[str, Any]) -> bool:
        """Track page view in Matomo"""
        try:
            session = await self._get_session()

            params = {
                "idsite": self.site_id,
                "rec": 1,
                "action_name": title,
                "url": f"https://hebrew-tutor.local{path}",
                "cid": properties.get("user_pseudonym", "anonymous")[:16],
                "rand": int(datetime.now().timestamp() * 1000000) % 1000000,
                "lang": "he",
                "dp": 1,  # Disable cookies
                "cip": 1,  # Anonymize IP
            }

            async with session.get(
                f"{self.tracker_url}/matomo.php",
                params=params
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Matomo page view error: {e}")
            return False

    def anonymize_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure GDPR compliance"""
        # IP is already anonymized with cip=1
        # Visitor ID is already hashed
        return data

class PlausibleProvider(AnalyticsProvider):
    """Plausible Analytics - Privacy-first, cookie-free"""

    def __init__(self, domain: str, api_host: str = "https://plausible.io"):
        self.domain = domain
        self.api_host = api_host.rstrip('/')
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def track_event(self, event: AnalyticsEvent) -> bool:
        """Send event to Plausible (simplified, privacy-first)"""
        try:
            session = await self._get_session()

            payload = {
                "domain": self.domain,
                "name": event.event_type.value,
                "url": f"https://{self.domain}/learn",
                "props": {
                    "milestone": event.properties.get("milestone_name", ""),
                    "theme": event.properties.get("theme", ""),
                    "language": "he",
                    "session_duration": event.properties.get("session_duration", 0)
                }
            }

            # Plausible is already privacy-first by design
            async with session.post(
                f"{self.api_host}/api/event",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Hebrew-AI-Tutor/1.0"
                }
            ) as response:
                success = response.status == 202  # Plausible returns 202
                if not success:
                    logger.error(f"Plausible tracking failed: {response.status}")
                return success

        except Exception as e:
            logger.error(f"Plausible tracking error: {e}")
            return False

    async def track_page_view(self, path: str, title: str, properties: Dict[str, Any]) -> bool:
        """Track page view in Plausible"""
        try:
            session = await self._get_session()

            payload = {
                "domain": self.domain,
                "name": "pageview",
                "url": f"https://{self.domain}{path}",
                "props": {
                    "title": title,
                    "language": "he"
                }
            }

            async with session.post(
                f"{self.api_host}/api/event",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 202

        except Exception as e:
            logger.error(f"Plausible page view error: {e}")
            return False

    def anonymize_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Plausible is privacy-first by default"""
        return data

class AnalyticsOrchestrator:
    """Coordinate multiple analytics providers with privacy controls"""

    def __init__(self):
        self.providers: List[AnalyticsProvider] = []
        self.privacy_mode = PrivacyLevel.PSEUDONYMOUS
        self.hebrew_learning_context = {
            "target_grade": 5,
            "language": "he",
            "text_direction": "rtl",
            "curriculum_focus": "coding_games"
        }

    def add_provider(self, provider: AnalyticsProvider) -> None:
        """Add analytics provider to the orchestration"""
        self.providers.append(provider)
        logger.info(f"Added analytics provider: {provider.__class__.__name__}")

    async def track_learning_milestone(self, milestone_data: Dict[str, Any]) -> None:
        """Track educational milestone completion"""
        event = AnalyticsEvent(
            event_type=EventType.MILESTONE_COMPLETED,
            timestamp=datetime.now(timezone.utc),
            session_id=milestone_data.get("session_id", ""),
            user_pseudonym=self._generate_user_pseudonym(milestone_data.get("student_id", "")),
            properties={
                "milestone_name": milestone_data.get("milestone_name", ""),
                "concept_learned": milestone_data.get("concept", ""),
                "attempts_required": milestone_data.get("attempts", 1),
                "hints_used": milestone_data.get("hints_used", 0),
                "completion_time_seconds": milestone_data.get("completion_time", 0),
                "theme": milestone_data.get("theme", "football"),
                "difficulty_level": milestone_data.get("difficulty", "beginner")
            },
            hebrew_context={
                "concept_he": milestone_data.get("concept_hebrew", ""),
                "milestone_he": milestone_data.get("milestone_hebrew", ""),
                "theme_he": milestone_data.get("theme_hebrew", "")
            }
        )

        await self._distribute_event(event)

    async def track_performance_metrics(self, performance_data: Dict[str, Any]) -> None:
        """Track system performance for optimization"""
        event = AnalyticsEvent(
            event_type=EventType.RUN_CLICKED,
            timestamp=datetime.now(timezone.utc),
            session_id=performance_data.get("session_id", ""),
            user_pseudonym=self._generate_user_pseudonym(performance_data.get("student_id", "")),
            properties={
                "load_time_ms": performance_data.get("load_time", 0),
                "test_execution_time_ms": performance_data.get("test_time", 0),
                "canvas_render_time_ms": performance_data.get("render_time", 0),
                "memory_usage_mb": performance_data.get("memory_usage", 0),
                "browser": performance_data.get("browser", "unknown"),
                "device_type": performance_data.get("device_type", "desktop")
            },
            privacy_level=PrivacyLevel.AGGREGATED_ONLY
        )

        await self._distribute_event(event)

    async def track_accessibility_usage(self, accessibility_data: Dict[str, Any]) -> None:
        """Track accessibility feature usage for compliance monitoring"""
        event = AnalyticsEvent(
            event_type=EventType.ACCESSIBILITY_FEATURE_USED,
            timestamp=datetime.now(timezone.utc),
            session_id=accessibility_data.get("session_id", ""),
            user_pseudonym=self._generate_user_pseudonym(accessibility_data.get("student_id", "")),
            properties={
                "feature_type": accessibility_data.get("feature", ""),
                "rtl_mode": accessibility_data.get("rtl_enabled", True),
                "high_contrast": accessibility_data.get("high_contrast", False),
                "reduced_motion": accessibility_data.get("reduced_motion", False),
                "tts_enabled": accessibility_data.get("tts_enabled", False),
                "font_size": accessibility_data.get("font_size", "normal")
            },
            hebrew_context={
                "accessibility_feature_he": accessibility_data.get("feature_hebrew", "")
            }
        )

        await self._distribute_event(event)

    async def track_error(self, error_data: Dict[str, Any]) -> None:
        """Track errors for system reliability monitoring"""
        event = AnalyticsEvent(
            event_type=EventType.ERROR_OCCURRED,
            timestamp=datetime.now(timezone.utc),
            session_id=error_data.get("session_id", ""),
            user_pseudonym=self._generate_user_pseudonym(error_data.get("student_id", "")),
            properties={
                "error_type": error_data.get("error_type", ""),
                "error_category": error_data.get("category", ""),
                "component": error_data.get("component", ""),
                "browser": error_data.get("browser", ""),
                "severity": error_data.get("severity", "medium")
            },
            privacy_level=PrivacyLevel.AGGREGATED_ONLY
        )

        await self._distribute_event(event)

    async def _distribute_event(self, event: AnalyticsEvent) -> None:
        """Send event to all configured providers"""
        tasks = [provider.track_event(event) for provider in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Provider {i} failed: {result}")
            elif not result:
                logger.warning(f"Provider {i} returned False")

    def _generate_user_pseudonym(self, student_id: str) -> str:
        """Generate privacy-safe user identifier"""
        if not student_id:
            return "anonymous"

        # Hash with salt for privacy
        salt = os.getenv("ANALYTICS_SALT", "hebrew_tutor_default_salt")
        pseudonym = hashlib.sha256(f"{student_id}_{salt}".encode()).hexdigest()[:16]
        return f"student_{pseudonym}"

class AnalyticsConfig:
    """Configuration management for analytics setup"""

    @staticmethod
    def load_from_env() -> Dict[str, Any]:
        """Load analytics configuration from environment variables"""
        return {
            "posthog": {
                "api_key": os.getenv("POSTHOG_API_KEY"),
                "host": os.getenv("POSTHOG_HOST", "https://app.posthog.com")
            },
            "matomo": {
                "site_id": os.getenv("MATOMO_SITE_ID"),
                "tracker_url": os.getenv("MATOMO_TRACKER_URL"),
                "token_auth": os.getenv("MATOMO_TOKEN_AUTH")
            },
            "plausible": {
                "domain": os.getenv("PLAUSIBLE_DOMAIN"),
                "api_host": os.getenv("PLAUSIBLE_API_HOST", "https://plausible.io")
            }
        }

    @staticmethod
    def setup_analytics(config: Dict[str, Any]) -> AnalyticsOrchestrator:
        """Set up analytics orchestrator with configured providers"""
        orchestrator = AnalyticsOrchestrator()

        # PostHog setup
        if config["posthog"]["api_key"]:
            posthog = PostHogProvider(
                api_key=config["posthog"]["api_key"],
                host=config["posthog"]["host"]
            )
            orchestrator.add_provider(posthog)

        # Matomo setup
        if config["matomo"]["site_id"] and config["matomo"]["tracker_url"]:
            matomo = MatomoProvider(
                site_id=config["matomo"]["site_id"],
                tracker_url=config["matomo"]["tracker_url"],
                token_auth=config["matomo"]["token_auth"]
            )
            orchestrator.add_provider(matomo)

        # Plausible setup
        if config["plausible"]["domain"]:
            plausible = PlausibleProvider(
                domain=config["plausible"]["domain"],
                api_host=config["plausible"]["api_host"]
            )
            orchestrator.add_provider(plausible)

        return orchestrator

# Example usage
async def demo_analytics_usage():
    """Demonstrate analytics integration for Hebrew AI Tutor"""

    # Load configuration
    config = AnalyticsConfig.load_from_env()
    analytics = AnalyticsConfig.setup_analytics(config)

    # Track milestone completion
    await analytics.track_learning_milestone({
        "session_id": "session_123",
        "student_id": "student_456",
        "milestone_name": "ball_physics_basics",
        "milestone_hebrew": "יסודות פיזיקת הכדור",
        "concept": "vectors",
        "concept_hebrew": "וקטורים",
        "attempts": 2,
        "hints_used": 1,
        "completion_time": 180,
        "theme": "football",
        "theme_hebrew": "כדורגל"
    })

    # Track performance metrics
    await analytics.track_performance_metrics({
        "session_id": "session_123",
        "student_id": "student_456",
        "load_time": 1800,
        "test_time": 450,
        "render_time": 16,
        "memory_usage": 45,
        "browser": "Chrome",
        "device_type": "desktop"
    })

    # Track accessibility feature usage
    await analytics.track_accessibility_usage({
        "session_id": "session_123",
        "student_id": "student_456",
        "feature": "high_contrast_mode",
        "feature_hebrew": "מצב ניגודיות גבוהה",
        "rtl_enabled": True,
        "high_contrast": True,
        "tts_enabled": True
    })

if __name__ == "__main__":
    asyncio.run(demo_analytics_usage())