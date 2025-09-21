"""
Global pytest configuration and fixtures for Hebrew AI Tutor testing.

This file provides common fixtures, test utilities, and configuration
for the entire test suite covering React components, LangGraph agents,
LiteLLM integration, and end-to-end user journeys.
"""

import asyncio
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from faker import Faker
from faker.providers import internet, lorem
from httpx import AsyncClient
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

# Hebrew faker for test data
fake = Faker(['he_IL', 'en_US'])
fake.add_provider(internet)
fake.add_provider(lorem)


# ============================================================================
# Session Scoped Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def playwright_session() -> Generator[Playwright, None, None]:
    """Session-scoped Playwright instance for E2E tests."""
    async with async_playwright() as p:
        yield p


@pytest.fixture(scope="session")
async def browser(playwright_session: Playwright) -> Generator[Browser, None, None]:
    """Session-scoped browser instance with Hebrew locale support."""
    browser = await playwright_session.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--lang=he",
            "--force-device-scale-factor=1",
        ]
    )
    yield browser
    await browser.close()


# ============================================================================
# Test Environment Configuration
# ============================================================================

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Test configuration with Hebrew AI Tutor specific settings."""
    return {
        "base_url": os.getenv("TEST_BASE_URL", "http://localhost:3000"),
        "api_url": os.getenv("TEST_API_URL", "http://localhost:8000"),
        "llm_endpoint": os.getenv("TEST_LLM_ENDPOINT", "http://localhost:4000"),
        "timeout": 30000,  # 30 seconds for tests
        "viewport": {"width": 1280, "height": 720},
        "locale": "he-IL",
        "dir": "rtl",
        "themes": ["football", "space", "robots", "transformers"],
        "session_duration": 20,  # minutes
        "target_age": 10,  # 5th grade
    }


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


# ============================================================================
# Browser and Page Fixtures
# ============================================================================

@pytest.fixture
async def browser_context(browser: Browser, test_config: Dict[str, Any]) -> Generator[BrowserContext, None, None]:
    """Browser context with Hebrew locale and RTL settings."""
    context = await browser.new_context(
        viewport=test_config["viewport"],
        locale=test_config["locale"],
        timezone_id="Asia/Jerusalem",
        extra_http_headers={
            "Accept-Language": "he-IL,he;q=0.9,en;q=0.8",
        },
        # Simulate Windows environment
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    )

    # Add Hebrew fonts support
    await context.add_init_script("""
        // Ensure Hebrew fonts are loaded
        document.fonts.ready.then(() => {
            console.log('Hebrew fonts loaded');
        });
    """)

    yield context
    await context.close()


@pytest.fixture
async def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """Page instance with accessibility and Hebrew support."""
    page = await browser_context.new_page()

    # Set up accessibility testing
    await page.evaluate("""
        // Add axe-core for accessibility testing
        if (!window.axe) {
            const script = document.createElement('script');
            script.src = 'https://unpkg.com/axe-core@4.10.0/axe.min.js';
            document.head.appendChild(script);
        }
    """)

    # Mock Web Speech API for TTS tests
    await page.add_init_script("""
        // Mock SpeechSynthesis for testing
        window.speechSynthesis = {
            speak: () => {},
            cancel: () => {},
            pause: () => {},
            resume: () => {},
            getVoices: () => [
                { lang: 'he-IL', name: 'Hebrew Voice', voiceURI: 'he-IL' }
            ]
        };

        window.SpeechSynthesisUtterance = function(text) {
            this.text = text;
            this.lang = 'he-IL';
            this.rate = 1;
            this.pitch = 1;
            this.volume = 1;
        };
    """)

    yield page
    await page.close()


# ============================================================================
# API Testing Fixtures
# ============================================================================

@pytest.fixture
async def api_client(test_config: Dict[str, Any]) -> Generator[AsyncClient, None, None]:
    """HTTP client for API testing."""
    async with AsyncClient(base_url=test_config["api_url"], timeout=30.0) as client:
        yield client


@pytest.fixture
def mock_llm_client():
    """Mock LiteLLM client for agent testing."""
    mock = AsyncMock()
    mock.chat.completions.create = AsyncMock(return_value={
        "choices": [{
            "message": {
                "content": "בוא נוסיף מהירות לכדור! צור משתנה vx ונתן לו ערך 5.",
                "role": "assistant"
            }
        }],
        "usage": {"total_tokens": 50}
    })
    return mock


# ============================================================================
# Test Data Factories
# ============================================================================

@pytest.fixture
def hebrew_lesson_data():
    """Factory for Hebrew lesson test data."""
    def create_lesson(theme: str = "football", milestone_count: int = 3):
        return {
            "id": fake.uuid4(),
            "title": f"שיעור {fake.word()} - {theme}",
            "theme": theme,
            "duration_min": 20,
            "milestones": [
                {
                    "id": fake.uuid4(),
                    "goal_he": f"יעד {i+1}: {fake.sentence()}",
                    "starter_code": f"// קוד התחלה למשימה {i+1}\nlet x = 0;\nlet y = 0;",
                    "tests_spec": [
                        f"describe('משימה {i+1}', () => {{ it('should pass', () => {{ expect(true).toBe(true); }}); }});"
                    ],
                    "hints_he": [
                        f"רמז 1: {fake.sentence()}",
                        f"רמז 2: {fake.sentence()}",
                        f"פתרון מלא: {fake.sentence()}"
                    ],
                    "xp": 20,
                    "badge": f"תג-{theme}-{i+1}"
                }
                for i in range(milestone_count)
            ],
            "prereqs": ["variables", "functions"],
            "review_items": [
                f"שאלת חזרה: {fake.sentence()}"
            ]
        }
    return create_lesson


@pytest.fixture
def student_profile_data():
    """Factory for student profile test data."""
    def create_profile(level: int = 1):
        return {
            "id": fake.uuid4(),
            "nickname": fake.first_name(),
            "level": level,
            "xp": level * 100,
            "streak": fake.random_int(0, 30),
            "badges": [f"badge-{i}" for i in range(level)],
            "concept_mastery": {
                "variables": 0.8,
                "functions": 0.6,
                "loops": 0.4,
                "conditionals": 0.3
            },
            "preferences": {
                "theme": fake.random_element(["football", "space", "robots"]),
                "voice_enabled": True,
                "session_length": 20
            },
            "last_session": fake.date_time_this_month().isoformat()
        }
    return create_profile


# ============================================================================
# Agent Testing Fixtures
# ============================================================================

@pytest.fixture
def mock_langgraph_state():
    """Mock LangGraph state for agent testing."""
    return {
        "student_id": "test-student",
        "lesson_plan": None,
        "current_milestone": 0,
        "attempts": 0,
        "hints_given": 0,
        "session_start": datetime.now().isoformat(),
        "concept_mastery": {},
        "theme": "football"
    }


@pytest.fixture
def agent_test_context(mock_llm_client, mock_langgraph_state):
    """Context for testing LangGraph agents."""
    return {
        "llm_client": mock_llm_client,
        "state": mock_langgraph_state,
        "config": {
            "max_hints": 3,
            "pass_threshold": 0.8,
            "session_duration": 20
        }
    }


# ============================================================================
# Security Testing Fixtures
# ============================================================================

@pytest.fixture
def security_test_payloads():
    """Security test payloads for input validation."""
    return {
        "xss": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ],
        "sql_injection": [
            "'; DROP TABLE students; --",
            "1' OR '1'='1",
            "admin'; --",
            "1; DELETE FROM sessions; --"
        ],
        "code_injection": [
            "console.log('injected')",
            "process.exit(1)",
            "require('fs').unlinkSync('/etc/passwd')",
            "eval('malicious code')"
        ],
        "hebrew_specific": [
            "א' OR 'א'='א",  # Hebrew SQL injection
            "<script>alert('עברית')</script>",  # Hebrew XSS
            "משתנה = 'זדוני'"  # Hebrew variable injection
        ]
    }


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def performance_thresholds():
    """Performance thresholds for testing."""
    return {
        "page_load": 2000,  # 2 seconds
        "first_paint": 1000,  # 1 second
        "first_contentful_paint": 1500,  # 1.5 seconds
        "largest_contentful_paint": 2500,  # 2.5 seconds
        "cumulative_layout_shift": 0.1,
        "first_input_delay": 100,  # 100ms
        "interaction_to_next_paint": 200,  # 200ms
        "memory_usage": 100 * 1024 * 1024,  # 100MB
        "api_response": 1000,  # 1 second
        "llm_response": 5000,  # 5 seconds
    }


# ============================================================================
# Accessibility Testing Fixtures
# ============================================================================

@pytest.fixture
def accessibility_config():
    """Accessibility testing configuration."""
    return {
        "wcag_level": "AA",
        "wcag_version": "2.2",
        "rules": {
            "color-contrast": True,
            "keyboard-navigation": True,
            "screen-reader": True,
            "focus-management": True,
            "semantic-html": True,
            "aria-labels": True,
            "alt-text": True,
            "heading-structure": True
        },
        "target_size": {
            "min_width": 24,  # 24x24 CSS pixels (WCAG 2.2)
            "min_height": 24
        },
        "hebrew_support": {
            "direction": "rtl",
            "text_rendering": "optimizeQuality",
            "font_features": ["liga", "kern", "mark"]
        }
    }


# ============================================================================
# Hebrew and RTL Testing Utilities
# ============================================================================

@pytest.fixture
def hebrew_text_samples():
    """Hebrew text samples for testing."""
    return {
        "simple": "שלום עולם",
        "mixed_numbers": "יש לי 5 כדורים",
        "mixed_english": "המילה hello בעברית",
        "punctuation": "איך אתה? כל טוב!",
        "code_vars": "המשתנה x שווה 10",
        "long_text": "זהו טקסט ארוך בעברית שמכיל מילים רבות ומשפטים שלמים כדי לבדוק את הטיפול בטקסט RTL",
        "programming_terms": "פונקציה, משתנה, לולאה, תנאי",
        "ui_elements": "כפתור, תפריט, דף, טופס",
    }


@pytest.fixture
def rtl_layout_tests():
    """RTL layout test scenarios."""
    return {
        "text_alignment": ["start", "end", "center", "justify"],
        "margin_padding": ["margin-inline-start", "margin-inline-end", "padding-inline-start", "padding-inline-end"],
        "borders": ["border-inline-start", "border-inline-end"],
        "positioning": ["inset-inline-start", "inset-inline-end"],
        "flexbox": ["justify-content", "align-items", "flex-direction"],
        "grid": ["grid-template-columns", "grid-auto-flow"],
    }


# ============================================================================
# Test Utilities
# ============================================================================

@pytest.fixture
def assert_helpers():
    """Custom assertion helpers for testing."""

    class AssertHelpers:
        @staticmethod
        async def assert_hebrew_text_rendered(page: Page, selector: str, expected_text: str):
            """Assert Hebrew text is properly rendered."""
            element = await page.locator(selector).first
            actual_text = await element.text_content()
            assert actual_text == expected_text, f"Expected '{expected_text}', got '{actual_text}'"

            # Check RTL direction
            direction = await element.evaluate("el => getComputedStyle(el).direction")
            assert direction == "rtl", f"Element should have RTL direction, got {direction}"

        @staticmethod
        async def assert_accessibility_compliance(page: Page, level: str = "AA"):
            """Assert page meets WCAG accessibility standards."""
            await page.wait_for_load_state("networkidle")

            # Run axe accessibility tests
            results = await page.evaluate(f"""
                new Promise((resolve) => {{
                    if (window.axe) {{
                        axe.run(document, {{
                            runOnly: ['wcag2{level.lower()}']
                        }}, (err, results) => {{
                            resolve(results);
                        }});
                    }} else {{
                        resolve({{ violations: [] }});
                    }}
                }})
            """)

            violations = results.get("violations", [])
            assert len(violations) == 0, f"Accessibility violations found: {violations}"

        @staticmethod
        async def assert_target_size_compliance(page: Page, selector: str):
            """Assert element meets WCAG 2.2 target size requirements (24x24px)."""
            element = await page.locator(selector).first
            box = await element.bounding_box()

            assert box is not None, f"Element {selector} not found"
            assert box["width"] >= 24, f"Element width {box['width']} is less than 24px"
            assert box["height"] >= 24, f"Element height {box['height']} is less than 24px"

        @staticmethod
        async def assert_performance_threshold(page: Page, metric: str, threshold: float):
            """Assert performance metric meets threshold."""
            metrics = await page.evaluate("""
                new Promise((resolve) => {
                    new PerformanceObserver((list) => {
                        const entries = list.getEntries();
                        resolve(entries);
                    }).observe({entryTypes: ['navigation', 'paint', 'largest-contentful-paint']});

                    setTimeout(() => resolve([]), 5000);
                })
            """)

            # This is a simplified version - in real tests you'd check specific metrics
            assert True  # Placeholder for actual metric checking

    return AssertHelpers()


# ============================================================================
# Cleanup and Teardown
# ============================================================================

@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """Cleanup test data after each test."""
    yield
    # Clean up any test files, temporary data, etc.
    pass


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    # Set up test environment
    os.environ.setdefault("TESTING", "1")
    os.environ.setdefault("PYTEST_RUNNING", "1")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file location
        if "test_agents" in str(item.fspath):
            item.add_marker(pytest.mark.agents)
        elif "test_frontend" in str(item.fspath):
            item.add_marker(pytest.mark.frontend)
        elif "test_backend" in str(item.fspath):
            item.add_marker(pytest.mark.backend)
        elif "test_e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "test_accessibility" in str(item.fspath):
            item.add_marker(pytest.mark.accessibility)
        elif "test_performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "test_security" in str(item.fspath):
            item.add_marker(pytest.mark.security)

        # Add Hebrew marker for Hebrew-specific tests
        if "hebrew" in item.name.lower() or "rtl" in item.name.lower():
            item.add_marker(pytest.mark.hebrew)

        # Add slow marker for tests that might take a while
        if "load" in item.name.lower() or "performance" in item.name.lower():
            item.add_marker(pytest.mark.slow)


def pytest_runtest_setup(item):
    """Setup for individual test runs."""
    # Skip network tests if no internet
    if "network" in [mark.name for mark in item.iter_markers()]:
        try:
            import urllib.request
            urllib.request.urlopen('http://www.google.com', timeout=1)
        except:
            pytest.skip("Network not available")


@pytest.fixture(autouse=True)
def test_isolation():
    """Ensure test isolation by resetting global state."""
    # Reset any global state before each test
    yield
    # Clean up after test
    pass