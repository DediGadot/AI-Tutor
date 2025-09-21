"""
Hebrew AI Tutor - Error Tracking and Monitoring System
Comprehensive error detection, categorization, and alerting for system reliability
"""

import json
import asyncio
import logging
import traceback
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import sqlite3
from pathlib import Path
import aiohttp
from collections import defaultdict, deque
import threading
import time

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    LLM_API = "llm_api"
    TEST_EXECUTION = "test_execution"
    CANVAS_RENDERING = "canvas_rendering"
    ACCESSIBILITY = "accessibility"
    HEBREW_RENDERING = "hebrew_rendering"
    USER_INPUT = "user_input"
    NETWORK = "network"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    PERFORMANCE = "performance"
    MEMORY = "memory"
    BUSINESS_LOGIC = "business_logic"

class ErrorStatus(Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    IGNORED = "ignored"

@dataclass
class ErrorContext:
    """Contextual information for error tracking"""
    student_id: Optional[str] = None
    session_id: Optional[str] = None
    lesson_id: Optional[str] = None
    milestone_id: Optional[str] = None
    theme: Optional[str] = None
    browser: Optional[str] = None
    user_agent: Optional[str] = None
    url: Optional[str] = None
    hebrew_content: Optional[str] = None
    rtl_mode: bool = True

@dataclass
class ErrorEvent:
    """Individual error event with full context"""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    stack_trace: Optional[str] = None
    context: Optional[ErrorContext] = None

    # Technical details
    component: Optional[str] = None
    function_name: Optional[str] = None
    line_number: Optional[int] = None

    # User impact
    user_facing: bool = False
    blocks_learning: bool = False
    affects_accessibility: bool = False

    # Hebrew-specific
    hebrew_error_message: Optional[str] = None
    rtl_rendering_issue: bool = False

    # Resolution tracking
    status: ErrorStatus = ErrorStatus.NEW
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None

    # Frequency tracking
    occurrence_count: int = 1
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

@dataclass
class ErrorPattern:
    """Pattern detection for recurring errors"""
    pattern_id: str
    error_signature: str
    occurrence_count: int
    affected_users: int
    first_occurrence: datetime
    last_occurrence: datetime
    trending: bool = False
    severity_escalated: bool = False

class ErrorDatabase:
    """SQLite database for error persistence"""

    def __init__(self, db_path: str = "/home/fiod/ai-tutor2/error_tracking.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize error tracking database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS errors (
                    error_id TEXT PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    message TEXT NOT NULL,
                    stack_trace TEXT,
                    context_json TEXT,
                    component TEXT,
                    function_name TEXT,
                    line_number INTEGER,
                    user_facing BOOLEAN DEFAULT FALSE,
                    blocks_learning BOOLEAN DEFAULT FALSE,
                    affects_accessibility BOOLEAN DEFAULT FALSE,
                    hebrew_error_message TEXT,
                    rtl_rendering_issue BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'new',
                    assigned_to TEXT,
                    resolution_notes TEXT,
                    resolved_at TIMESTAMP,
                    occurrence_count INTEGER DEFAULT 1,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    error_signature TEXT NOT NULL,
                    occurrence_count INTEGER DEFAULT 0,
                    affected_users INTEGER DEFAULT 0,
                    first_occurrence TIMESTAMP NOT NULL,
                    last_occurrence TIMESTAMP NOT NULL,
                    trending BOOLEAN DEFAULT FALSE,
                    severity_escalated BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON errors(timestamp);
                CREATE INDEX IF NOT EXISTS idx_errors_category ON errors(category);
                CREATE INDEX IF NOT EXISTS idx_errors_severity ON errors(severity);
                CREATE INDEX IF NOT EXISTS idx_errors_status ON errors(status);
            """)

    def save_error(self, error: ErrorEvent):
        """Save error to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO errors (
                    error_id, timestamp, severity, category, message, stack_trace,
                    context_json, component, function_name, line_number,
                    user_facing, blocks_learning, affects_accessibility,
                    hebrew_error_message, rtl_rendering_issue, status,
                    assigned_to, resolution_notes, resolved_at,
                    occurrence_count, first_seen, last_seen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                error.error_id, error.timestamp, error.severity.value, error.category.value,
                error.message, error.stack_trace,
                json.dumps(asdict(error.context)) if error.context else None,
                error.component, error.function_name, error.line_number,
                error.user_facing, error.blocks_learning, error.affects_accessibility,
                error.hebrew_error_message, error.rtl_rendering_issue, error.status.value,
                error.assigned_to, error.resolution_notes, error.resolved_at,
                error.occurrence_count, error.first_seen, error.last_seen
            ))

    def get_recent_errors(self, hours: int = 24) -> List[ErrorEvent]:
        """Retrieve recent errors from database"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM errors WHERE timestamp > ? ORDER BY timestamp DESC
            """, (cutoff_time,))

            errors = []
            for row in cursor.fetchall():
                context_data = json.loads(row[6]) if row[6] else None
                context = ErrorContext(**context_data) if context_data else None

                error = ErrorEvent(
                    error_id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    severity=ErrorSeverity(row[2]),
                    category=ErrorCategory(row[3]),
                    message=row[4],
                    stack_trace=row[5],
                    context=context,
                    component=row[7],
                    function_name=row[8],
                    line_number=row[9],
                    user_facing=bool(row[10]),
                    blocks_learning=bool(row[11]),
                    affects_accessibility=bool(row[12]),
                    hebrew_error_message=row[13],
                    rtl_rendering_issue=bool(row[14]),
                    status=ErrorStatus(row[15]),
                    assigned_to=row[16],
                    resolution_notes=row[17],
                    resolved_at=datetime.fromisoformat(row[18]) if row[18] else None,
                    occurrence_count=row[19],
                    first_seen=datetime.fromisoformat(row[20]) if row[20] else None,
                    last_seen=datetime.fromisoformat(row[21]) if row[21] else None
                )
                errors.append(error)

            return errors

class HebrewErrorTranslator:
    """Translate technical errors to Hebrew for better user experience"""

    ERROR_TRANSLATIONS = {
        "ReferenceError": "שגיאת הפניה",
        "TypeError": "שגיאת סוג",
        "SyntaxError": "שגיאת תחביר",
        "NetworkError": "שגיאת רשת",
        "TimeoutError": "שגיאת זמן קצוב",
        "PermissionError": "שגיאת הרשאה",
        "not defined": "לא מוגדר",
        "is not a function": "אינה פונקציה",
        "Cannot read property": "לא ניתן לקרוא תכונה",
        "Failed to fetch": "נכשל באחזור נתונים",
        "Access denied": "גישה נדחתה"
    }

    CONTEXT_EXPLANATIONS = {
        "vx": "מהירות אופקית (vx)",
        "vy": "מהירות אנכית (vy)",
        "ball": "אובייקט הכדור",
        "canvas": "לוח הציור",
        "draw": "פונקציית הציור",
        "setup": "פונקציית ההגדרה"
    }

    @classmethod
    def translate_error(cls, error_message: str, context: Optional[ErrorContext] = None) -> str:
        """Translate technical error to Hebrew with educational context"""

        hebrew_message = error_message

        # Basic error type translation
        for english, hebrew in cls.ERROR_TRANSLATIONS.items():
            if english in error_message:
                hebrew_message = hebrew_message.replace(english, hebrew)

        # Context-specific translations
        for english, hebrew in cls.CONTEXT_EXPLANATIONS.items():
            if english in error_message:
                hebrew_message = hebrew_message.replace(english, hebrew)

        # Add educational guidance
        if "not defined" in error_message.lower():
            hebrew_message += " - בדוק שהגדרת את המשתנה לפני השימוש בו"
        elif "function" in error_message.lower():
            hebrew_message += " - וודא שהפונקציה הוגדרה נכון"
        elif "canvas" in error_message.lower():
            hebrew_message += " - בעיה בהגדרת לוח הציור"

        return hebrew_message

class ErrorAggregator:
    """Aggregate and analyze error patterns"""

    def __init__(self):
        self.error_buckets: Dict[str, List[ErrorEvent]] = defaultdict(list)
        self.pattern_cache: Dict[str, ErrorPattern] = {}

    def add_error(self, error: ErrorEvent):
        """Add error to aggregation buckets"""
        signature = self._generate_error_signature(error)
        self.error_buckets[signature].append(error)
        self._update_pattern(signature, error)

    def _generate_error_signature(self, error: ErrorEvent) -> str:
        """Generate unique signature for error pattern matching"""
        components = [
            error.category.value,
            error.component or "unknown",
            error.function_name or "unknown",
            self._normalize_error_message(error.message)
        ]
        return hashlib.md5("|".join(components).encode()).hexdigest()[:12]

    def _normalize_error_message(self, message: str) -> str:
        """Normalize error message for pattern matching"""
        # Remove specific values, keep the pattern
        import re
        normalized = re.sub(r'\d+', 'N', message)  # Replace numbers
        normalized = re.sub(r'"[^"]*"', '"STR"', normalized)  # Replace strings
        normalized = re.sub(r'line \d+', 'line N', normalized)  # Replace line numbers
        return normalized.lower()

    def _update_pattern(self, signature: str, error: ErrorEvent):
        """Update error pattern statistics"""
        if signature not in self.pattern_cache:
            self.pattern_cache[signature] = ErrorPattern(
                pattern_id=signature,
                error_signature=signature,
                occurrence_count=0,
                affected_users=0,
                first_occurrence=error.timestamp,
                last_occurrence=error.timestamp
            )

        pattern = self.pattern_cache[signature]
        pattern.occurrence_count += 1
        pattern.last_occurrence = error.timestamp

        # Track unique users
        if error.context and error.context.student_id:
            # This is simplified - in practice, you'd track unique users properly
            pattern.affected_users = len(set(
                e.context.student_id for e in self.error_buckets[signature]
                if e.context and e.context.student_id
            ))

    def get_trending_errors(self, hours: int = 24) -> List[ErrorPattern]:
        """Identify trending error patterns"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        trending = []

        for pattern in self.pattern_cache.values():
            recent_errors = [
                e for e in self.error_buckets[pattern.pattern_id]
                if e.timestamp > cutoff_time
            ]

            if len(recent_errors) >= 5:  # Threshold for trending
                pattern.trending = True
                trending.append(pattern)

        return sorted(trending, key=lambda p: p.occurrence_count, reverse=True)

class AlertManager:
    """Manage error alerts and notifications"""

    def __init__(self):
        self.alert_rules: List[Dict[str, Any]] = [
            {
                "name": "critical_error_burst",
                "condition": lambda errors: len([e for e in errors if e.severity == ErrorSeverity.CRITICAL]) >= 3,
                "message": "זוהו 3 או יותר שגיאות קריטיות בשעה האחרונה",
                "cooldown_minutes": 15
            },
            {
                "name": "learning_blocking_errors",
                "condition": lambda errors: len([e for e in errors if e.blocks_learning]) >= 5,
                "message": "זוהו שגיאות החוסמות למידה - דרושה התערבות מיידית",
                "cooldown_minutes": 10
            },
            {
                "name": "hebrew_rendering_issues",
                "condition": lambda errors: len([e for e in errors if e.rtl_rendering_issue]) >= 2,
                "message": "בעיות בתצוגת עברית/RTL - יש לבדוק התאמה לדפדפנים",
                "cooldown_minutes": 30
            },
            {
                "name": "accessibility_failures",
                "condition": lambda errors: len([e for e in errors if e.affects_accessibility]) >= 3,
                "message": "זוהו בעיות נגישות - עלול להשפיע על תלמידים עם צרכים מיוחדים",
                "cooldown_minutes": 20
            }
        ]

        self.alert_history: Dict[str, datetime] = {}

    async def check_and_send_alerts(self, recent_errors: List[ErrorEvent]):
        """Check alert conditions and send notifications"""
        current_time = datetime.now()

        for rule in self.alert_rules:
            rule_name = rule["name"]
            cooldown = timedelta(minutes=rule["cooldown_minutes"])

            # Check cooldown
            if rule_name in self.alert_history:
                if current_time - self.alert_history[rule_name] < cooldown:
                    continue

            # Check condition
            if rule["condition"](recent_errors):
                await self._send_alert(rule["message"], rule_name)
                self.alert_history[rule_name] = current_time

    async def _send_alert(self, message: str, alert_type: str):
        """Send alert notification (placeholder for actual implementation)"""
        logger.critical(f"ALERT [{alert_type}]: {message}")

        # In a real implementation, this would send:
        # - Email notifications
        # - Slack/Discord messages
        # - SMS for critical alerts
        # - Dashboard notifications

class ErrorMonitor:
    """Main error monitoring orchestrator"""

    def __init__(self, db_path: str = "/home/fiod/ai-tutor2/error_tracking.db"):
        self.db = ErrorDatabase(db_path)
        self.translator = HebrewErrorTranslator()
        self.aggregator = ErrorAggregator()
        self.alert_manager = AlertManager()

        self.error_queue = deque(maxlen=1000)  # Recent errors in memory
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

    def start_monitoring(self):
        """Start background error monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Error monitoring started")

    def stop_monitoring(self):
        """Stop background error monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Error monitoring stopped")

    def track_error(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[ErrorContext] = None,
        stack_trace: Optional[str] = None,
        **kwargs
    ) -> str:
        """Track a new error event"""

        error_id = hashlib.md5(
            f"{message}_{category.value}_{datetime.now().timestamp()}".encode()
        ).hexdigest()[:16]

        # Translate error message to Hebrew if needed
        hebrew_message = None
        if context and any(char in message for char in "אבגדהוזחטיכלמנסעפצקרשת"):
            hebrew_message = message
        else:
            hebrew_message = self.translator.translate_error(message, context)

        error = ErrorEvent(
            error_id=error_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            message=message,
            stack_trace=stack_trace,
            context=context,
            hebrew_error_message=hebrew_message,
            **kwargs
        )

        # Store in memory queue
        self.error_queue.append(error)

        # Add to aggregator
        self.aggregator.add_error(error)

        # Save to database
        self.db.save_error(error)

        logger.error(f"Error tracked: {error_id} - {message}")
        return error_id

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for alerts every 60 seconds
                recent_errors = list(self.error_queue)
                asyncio.run(self.alert_manager.check_and_send_alerts(recent_errors))

                # Clean up old errors from memory
                cutoff_time = datetime.now() - timedelta(hours=2)
                while (self.error_queue and
                       self.error_queue[0].timestamp < cutoff_time):
                    self.error_queue.popleft()

                time.sleep(60)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of recent errors"""
        recent_errors = self.db.get_recent_errors(hours)

        summary = {
            "total_errors": len(recent_errors),
            "by_severity": defaultdict(int),
            "by_category": defaultdict(int),
            "by_status": defaultdict(int),
            "critical_issues": [],
            "trending_patterns": [],
            "hebrew_specific_issues": 0,
            "accessibility_issues": 0,
            "learning_blocking_issues": 0
        }

        for error in recent_errors:
            summary["by_severity"][error.severity.value] += 1
            summary["by_category"][error.category.value] += 1
            summary["by_status"][error.status.value] += 1

            if error.severity == ErrorSeverity.CRITICAL:
                summary["critical_issues"].append({
                    "error_id": error.error_id,
                    "message": error.message,
                    "hebrew_message": error.hebrew_error_message,
                    "timestamp": error.timestamp.isoformat()
                })

            if error.rtl_rendering_issue or error.hebrew_error_message:
                summary["hebrew_specific_issues"] += 1

            if error.affects_accessibility:
                summary["accessibility_issues"] += 1

            if error.blocks_learning:
                summary["learning_blocking_issues"] += 1

        # Add trending patterns
        trending = self.aggregator.get_trending_errors(hours)
        summary["trending_patterns"] = [
            {
                "pattern_id": p.pattern_id,
                "occurrence_count": p.occurrence_count,
                "affected_users": p.affected_users
            } for p in trending[:5]
        ]

        return dict(summary)

    def generate_health_report(self) -> str:
        """Generate system health report"""
        summary = self.get_error_summary(24)

        report = f"""
Hebrew AI Tutor - System Health Report
=====================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Overall Health: {'🔴 CRITICAL' if summary['by_severity']['critical'] > 0 else '🟡 WARNING' if summary['total_errors'] > 50 else '🟢 HEALTHY'}

Last 24 Hours Summary:
- Total Errors: {summary['total_errors']}
- Critical: {summary['by_severity']['critical']}
- High: {summary['by_severity']['high']}
- Medium: {summary['by_severity']['medium']}
- Low: {summary['by_severity']['low']}

Hebrew-Specific Issues:
- RTL/Hebrew Rendering Issues: {summary['hebrew_specific_issues']}
- Accessibility Impact: {summary['accessibility_issues']}
- Learning-Blocking Errors: {summary['learning_blocking_issues']}

Top Error Categories:
"""

        for category, count in sorted(summary['by_category'].items(), key=lambda x: x[1], reverse=True)[:5]:
            report += f"- {category}: {count}\n"

        if summary['critical_issues']:
            report += "\nCritical Issues Requiring Immediate Attention:\n"
            for issue in summary['critical_issues'][:3]:
                report += f"- {issue['error_id']}: {issue['hebrew_message'] or issue['message']}\n"

        if summary['trending_patterns']:
            report += "\nTrending Error Patterns:\n"
            for pattern in summary['trending_patterns']:
                report += f"- Pattern {pattern['pattern_id']}: {pattern['occurrence_count']} occurrences, {pattern['affected_users']} users\n"

        report += "\nRecommendations:\n"
        if summary['learning_blocking_issues'] > 0:
            report += "- HIGH PRIORITY: Address learning-blocking errors immediately\n"
        if summary['hebrew_specific_issues'] > 5:
            report += "- Review Hebrew/RTL rendering system for compatibility issues\n"
        if summary['accessibility_issues'] > 0:
            report += "- Audit accessibility features to ensure inclusive learning\n"
        if summary['total_errors'] > 100:
            report += "- Consider increasing monitoring frequency and alert thresholds\n"

        return report

# Example usage and error simulation
def simulate_hebrew_tutor_errors():
    """Simulate common errors in Hebrew AI Tutor system"""

    monitor = ErrorMonitor()
    monitor.start_monitoring()

    # Simulate various types of errors
    error_scenarios = [
        {
            "message": "ReferenceError: vx is not defined",
            "category": ErrorCategory.TEST_EXECUTION,
            "severity": ErrorSeverity.MEDIUM,
            "context": ErrorContext(
                student_id="student_123",
                session_id="session_456",
                lesson_id="football_lesson_01",
                milestone_id="milestone_02",
                theme="football",
                hebrew_content="הגדרת מהירות אופקית"
            ),
            "blocks_learning": True
        },
        {
            "message": "Failed to render Hebrew text with correct direction",
            "category": ErrorCategory.HEBREW_RENDERING,
            "severity": ErrorSeverity.HIGH,
            "context": ErrorContext(
                student_id="student_456",
                browser="Safari",
                rtl_mode=True,
                hebrew_content="בעיה בתצוגת טקסט עברי"
            ),
            "rtl_rendering_issue": True,
            "affects_accessibility": True
        },
        {
            "message": "LLM API timeout after 30 seconds",
            "category": ErrorCategory.LLM_API,
            "severity": ErrorSeverity.CRITICAL,
            "context": ErrorContext(
                student_id="student_789",
                session_id="session_101",
                lesson_id="space_lesson_03"
            ),
            "blocks_learning": True
        }
    ]

    for scenario in error_scenarios:
        monitor.track_error(**scenario)

    # Wait a moment for processing
    time.sleep(2)

    # Generate and print health report
    report = monitor.generate_health_report()
    print(report)

    # Get error summary
    summary = monitor.get_error_summary()
    print(f"\nError Summary: {json.dumps(summary, indent=2, default=str)}")

    monitor.stop_monitoring()

if __name__ == "__main__":
    simulate_hebrew_tutor_errors()