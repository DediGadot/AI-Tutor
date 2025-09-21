#!/usr/bin/env python3
"""
Basic backend tests for Hebrew AI Tutor
Tests core components without external dependencies.
"""

import sys
import os
import asyncio
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_config_loader():
    """Test configuration loading."""
    try:
        from utils.config_loader import load_config, substitute_env_vars

        # Test environment variable substitution
        test_content = "host: ${HOST:-localhost}\nport: ${PORT:-8000}"
        result = substitute_env_vars(test_content)

        assert "localhost" in result
        assert "8000" in result
        print("✅ Config loader test passed")

    except Exception as e:
        print(f"❌ Config loader test failed: {e}")
        assert False, f"Config loader test failed: {e}"

def test_hebrew_utils():
    """Test Hebrew text processing utilities."""
    try:
        from utils.hebrew_utils import HebrewTextProcessor

        processor = HebrewTextProcessor()

        # Test Hebrew text detection
        hebrew_text = "ברוך הבא למערכת"
        english_text = "Hello World"

        assert processor.is_hebrew_text(hebrew_text) == True
        assert processor.is_hebrew_text(english_text) == False

        # Test text cleaning (should include RTL markers)
        messy_text = "   ברוך    הבא   "
        cleaned = processor.clean_hebrew_text(messy_text)
        # Check that whitespace is cleaned and RTL markers are added
        assert "ברוך הבא" in cleaned
        assert len(cleaned.strip()) > len("ברוך הבא")  # RTL markers add characters

        # Test error translation
        error = "Syntax error"
        translated = processor.translate_error_message(error)
        assert translated == "שגיאת תחביר"

        print("✅ Hebrew utils test passed")

    except Exception as e:
        print(f"❌ Hebrew utils test failed: {e}")
        assert False, f"Hebrew utils test failed: {e}"

def test_lesson_models():
    """Test Pydantic models for lessons."""
    try:
        from models.lesson_models import LessonPlan, Milestone, TestSpec, Hint

        # Create test objects
        hint = Hint(text="זה רמז", reveal_after_attempts=1)
        test_spec = TestSpec(name="Test 1", description="בדיקה ראשונה", code="expect(true).toBe(true)")

        milestone = Milestone(
            id="milestone_1",
            goal_he="יצירת כדור",
            starter_code="// קוד התחלתי",
            tests=[test_spec],
            hints=[hint]
        )

        lesson = LessonPlan(
            id="lesson_1",
            title="First Lesson",
            title_he="שיעור ראשון",
            theme="football",
            milestones=[milestone]
        )

        # Validate
        assert lesson.theme == "football"
        assert len(lesson.milestones) == 1
        assert lesson.milestones[0].goal_he == "יצירת כדור"

        print("✅ Lesson models test passed")

    except Exception as e:
        print(f"❌ Lesson models test failed: {e}")
        assert False, f"Lesson models test failed: {e}"

def test_database_models():
    """Test database service (without actual DB)."""
    try:
        from services.database import DatabaseService

        # Test configuration parsing
        config = {
            "sqlite": {
                "enabled": True,
                "path": ":memory:",
                "backup_enabled": False
            }
        }

        db_service = DatabaseService(config)

        # Test basic configuration
        assert db_service.db_path == ":memory:"
        assert db_service.backup_enabled == False

        print("✅ Database models test passed")

    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        assert False, f"Database models test failed: {e}"

def test_monitoring_utils():
    """Test monitoring and metrics utilities."""
    try:
        from utils.monitoring import MetricsCollector, MetricPoint

        # Test metric point creation
        metric = MetricPoint(
            name="test.metric",
            value=42.0,
            timestamp="2024-01-01T00:00:00Z"
        )

        assert metric.name == "test.metric"
        assert metric.value == 42.0

        # Test metrics collector config
        config = {
            "metrics": {"enabled": True, "collection_interval_seconds": 30},
            "thresholds": {"cpu_percent": 80}
        }

        collector = MetricsCollector(config)
        assert collector.enabled == True
        assert collector.collection_interval == 30

        print("✅ Monitoring utils test passed")

    except Exception as e:
        print(f"❌ Monitoring utils test failed: {e}")
        assert False, f"Monitoring utils test failed: {e}"

async def main():
    """Run all basic tests."""
    print("🧪 Running Hebrew AI Tutor Backend Tests...")
    print("=" * 50)

    tests = [
        ("Config Loader", test_config_loader),
        ("Hebrew Utils", test_hebrew_utils),
        ("Lesson Models", test_lesson_models),
        ("Database Models", test_database_models),
        ("Monitoring Utils", test_monitoring_utils),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All backend tests passed!")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)