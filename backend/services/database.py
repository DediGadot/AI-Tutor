#!/usr/bin/env python3
"""
Database Service
Handles SQLite database operations for session data, progress tracking, and metrics.
"""

import sqlite3
import json
import logging
import asyncio
import aiosqlite
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for the Hebrew AI Tutor."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize database service."""
        self.config = config
        self.db_path = config.get("sqlite", {}).get("path", "./data/tutor.db")
        self.backup_enabled = config.get("sqlite", {}).get("backup_enabled", True)

        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Connection pool (for async operations)
        self._connection = None

    async def initialize(self):
        """Initialize the database and create tables."""
        try:
            # Create database tables
            await self._create_tables()

            # Test connection
            await self._test_connection()

            logger.info(f"✅ Database service initialized with SQLite at {self.db_path}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise

    async def shutdown(self):
        """Shutdown database connections."""
        if self._connection:
            await self._connection.close()
        logger.info("✅ Database service shutdown complete")

    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
                return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False

    async def _create_tables(self):
        """Create necessary database tables."""
        async with aiosqlite.connect(self.db_path) as db:
            # Sessions table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    student_nickname TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    lesson_id TEXT,
                    difficulty_level INTEGER,
                    state_data TEXT,  -- JSON blob for agent state
                    created_at TEXT,
                    last_updated TEXT,
                    completed_at TEXT,
                    completed BOOLEAN DEFAULT FALSE
                )
            """)

            # Milestones table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    milestone_id TEXT,
                    milestone_data TEXT,  -- JSON blob for milestone details
                    status TEXT,  -- active, completed, failed
                    attempts INTEGER DEFAULT 0,
                    hints_used INTEGER DEFAULT 0,
                    completed_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)

            # Student progress table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS student_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_nickname TEXT,
                    concept TEXT,
                    mastery_level REAL,
                    last_practiced TEXT,
                    practice_count INTEGER DEFAULT 0,
                    xp_earned INTEGER DEFAULT 0
                )
            """)

            # Badges table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_nickname TEXT,
                    badge_name TEXT,
                    badge_category TEXT,
                    earned_at TEXT,
                    session_id TEXT
                )
            """)

            # Analytics events table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_name TEXT,
                    session_id TEXT,
                    student_nickname TEXT,
                    event_data TEXT,  -- JSON blob
                    timestamp TEXT
                )
            """)

            # System metrics table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT,
                    metric_value REAL,
                    metric_data TEXT,  -- JSON blob for additional data
                    timestamp TEXT
                )
            """)

            await db.commit()

    async def _test_connection(self):
        """Test database connection."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM sessions")
            result = await cursor.fetchone()
            logger.info(f"Database test successful. Sessions count: {result[0]}")

    # Session Management

    async def save_session(self, session_id: str, state: Dict[str, Any]):
        """Save session state to database."""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO sessions
                    (session_id, student_nickname, theme, lesson_id, difficulty_level,
                     state_data, created_at, last_updated, completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    state.get("student_nickname"),
                    state.get("theme"),
                    state.get("lesson_id"),
                    state.get("difficulty_level"),
                    json.dumps(state, ensure_ascii=False),
                    state.get("created_at", timestamp),
                    timestamp,
                    state.get("completed", False)
                ))

                await db.commit()

        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            raise

    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session state from database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT state_data FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                result = await cursor.fetchone()

                if result:
                    return json.loads(result[0])
                return None

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    async def get_session_list(self, student_nickname: str = None) -> List[Dict[str, Any]]:
        """Get list of sessions, optionally filtered by student."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if student_nickname:
                    cursor = await db.execute("""
                        SELECT session_id, student_nickname, theme, created_at,
                               last_updated, completed
                        FROM sessions
                        WHERE student_nickname = ?
                        ORDER BY created_at DESC
                    """, (student_nickname,))
                else:
                    cursor = await db.execute("""
                        SELECT session_id, student_nickname, theme, created_at,
                               last_updated, completed
                        FROM sessions
                        ORDER BY created_at DESC
                    """)

                rows = await cursor.fetchall()
                return [
                    {
                        "session_id": row[0],
                        "student_nickname": row[1],
                        "theme": row[2],
                        "created_at": row[3],
                        "last_updated": row[4],
                        "completed": row[5]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get session list: {e}")
            return []

    # Milestone Tracking

    async def save_milestone(self, session_id: str, milestone_id: str,
                           milestone_data: Dict[str, Any], status: str):
        """Save milestone progress."""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO milestones
                    (session_id, milestone_id, milestone_data, status, completed_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    milestone_id,
                    json.dumps(milestone_data, ensure_ascii=False),
                    status,
                    timestamp if status == "completed" else None
                ))

                await db.commit()

        except Exception as e:
            logger.error(f"Failed to save milestone {milestone_id}: {e}")
            raise

    # Student Progress Tracking

    async def update_student_progress(self, student_nickname: str, concept: str,
                                    mastery_change: float, xp_gained: int = 0):
        """Update student's progress for a specific concept."""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                # Check if record exists
                cursor = await db.execute("""
                    SELECT mastery_level, practice_count, xp_earned
                    FROM student_progress
                    WHERE student_nickname = ? AND concept = ?
                """, (student_nickname, concept))

                existing = await cursor.fetchone()

                if existing:
                    # Update existing record
                    new_mastery = min(1.0, max(0.0, existing[0] + mastery_change))
                    new_practice_count = existing[1] + 1
                    new_xp = existing[2] + xp_gained

                    await db.execute("""
                        UPDATE student_progress
                        SET mastery_level = ?, practice_count = ?,
                            xp_earned = ?, last_practiced = ?
                        WHERE student_nickname = ? AND concept = ?
                    """, (new_mastery, new_practice_count, new_xp, timestamp,
                          student_nickname, concept))
                else:
                    # Create new record
                    await db.execute("""
                        INSERT INTO student_progress
                        (student_nickname, concept, mastery_level, practice_count,
                         xp_earned, last_practiced)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (student_nickname, concept, max(0.0, mastery_change),
                          1, xp_gained, timestamp))

                await db.commit()

        except Exception as e:
            logger.error(f"Failed to update student progress: {e}")
            raise

    async def get_student_mastery(self, student_nickname: str) -> Dict[str, Any]:
        """Get student's mastery data for all concepts."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT concept, mastery_level, practice_count, xp_earned, last_practiced
                    FROM student_progress
                    WHERE student_nickname = ?
                """, (student_nickname,))

                rows = await cursor.fetchall()
                return {
                    row[0]: {
                        "mastery_level": row[1],
                        "practice_count": row[2],
                        "xp_earned": row[3],
                        "last_practiced": row[4]
                    }
                    for row in rows
                }

        except Exception as e:
            logger.error(f"Failed to get student mastery: {e}")
            return {}

    # Badge Management

    async def award_badge(self, student_nickname: str, badge_name: str,
                         badge_category: str, session_id: str):
        """Award a badge to a student."""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                # Check if badge already awarded
                cursor = await db.execute("""
                    SELECT id FROM badges
                    WHERE student_nickname = ? AND badge_name = ?
                """, (student_nickname, badge_name))

                if not await cursor.fetchone():
                    await db.execute("""
                        INSERT INTO badges
                        (student_nickname, badge_name, badge_category, earned_at, session_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (student_nickname, badge_name, badge_category, timestamp, session_id))

                    await db.commit()
                    return True

            return False  # Badge already exists

        except Exception as e:
            logger.error(f"Failed to award badge: {e}")
            return False

    async def get_student_badges(self, student_nickname: str) -> List[Dict[str, Any]]:
        """Get all badges for a student."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT badge_name, badge_category, earned_at, session_id
                    FROM badges
                    WHERE student_nickname = ?
                    ORDER BY earned_at DESC
                """, (student_nickname,))

                rows = await cursor.fetchall()
                return [
                    {
                        "badge_name": row[0],
                        "badge_category": row[1],
                        "earned_at": row[2],
                        "session_id": row[3]
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get student badges: {e}")
            return []

    # Analytics and Metrics

    async def log_event(self, event_name: str, session_id: str = None,
                       student_nickname: str = None, event_data: Dict[str, Any] = None):
        """Log an analytics event."""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO analytics_events
                    (event_name, session_id, student_nickname, event_data, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    event_name,
                    session_id,
                    student_nickname,
                    json.dumps(event_data or {}, ensure_ascii=False),
                    timestamp
                ))

                await db.commit()

        except Exception as e:
            logger.error(f"Failed to log event {event_name}: {e}")

    async def log_metric(self, metric_name: str, metric_value: float,
                        metric_data: Dict[str, Any] = None):
        """Log a system metric."""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO system_metrics
                    (metric_name, metric_value, metric_data, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (
                    metric_name,
                    metric_value,
                    json.dumps(metric_data or {}, ensure_ascii=False),
                    timestamp
                ))

                await db.commit()

        except Exception as e:
            logger.error(f"Failed to log metric {metric_name}: {e}")

    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours."""
        try:
            # Calculate timestamp for N hours ago
            from datetime import timedelta
            cutoff_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

            async with aiosqlite.connect(self.db_path) as db:
                # Session metrics
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM sessions WHERE created_at > ?
                """, (cutoff_time,))
                new_sessions = (await cursor.fetchone())[0]

                cursor = await db.execute("""
                    SELECT COUNT(*) FROM sessions WHERE completed_at > ?
                """, (cutoff_time,))
                completed_sessions = (await cursor.fetchone())[0]

                # Milestone metrics
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM milestones WHERE completed_at > ? AND status = 'completed'
                """, (cutoff_time,))
                completed_milestones = (await cursor.fetchone())[0]

                # Badge metrics
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM badges WHERE earned_at > ?
                """, (cutoff_time,))
                badges_awarded = (await cursor.fetchone())[0]

                return {
                    "period_hours": hours,
                    "new_sessions": new_sessions,
                    "completed_sessions": completed_sessions,
                    "completed_milestones": completed_milestones,
                    "badges_awarded": badges_awarded,
                    "completion_rate": completed_sessions / max(new_sessions, 1)
                }

        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}