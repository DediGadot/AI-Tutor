#!/usr/bin/env python3
"""
Monitoring and Metrics Utilities
Handles performance monitoring, metrics collection, and system health tracking.
"""

import time
import asyncio
import logging
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point."""
    name: str
    value: float
    timestamp: str
    tags: Dict[str, str] = None
    metadata: Dict[str, Any] = None


class MetricsCollector:
    """Collects and manages system metrics."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize metrics collector."""
        self.config = config
        self.enabled = config.get("metrics", {}).get("enabled", True)
        self.collection_interval = config.get("metrics", {}).get("collection_interval_seconds", 30)
        self.retention_days = config.get("metrics", {}).get("retention_days", 7)

        # In-memory metrics storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)

        # System monitoring
        self.system_metrics = {}
        self._monitor_task: Optional[asyncio.Task] = None

        # Thresholds for alerting
        self.thresholds = config.get("thresholds", {})

    async def initialize(self):
        """Initialize the metrics collector."""
        if not self.enabled:
            logger.info("📊 Metrics collection disabled")
            return

        try:
            # Start background monitoring
            self._monitor_task = asyncio.create_task(self._background_monitor())
            logger.info("✅ Metrics collector initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize metrics collector: {e}")
            raise

    async def shutdown(self):
        """Shutdown the metrics collector."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("✅ Metrics collector shutdown complete")

    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()

    async def track_event(self, event_name: str, properties: Dict[str, Any] = None):
        """Track an analytics event."""
        if not self.enabled:
            return

        timestamp = self.get_timestamp()

        # Increment counter
        self.counters[f"events.{event_name}"] += 1

        # Store event details
        metric_point = MetricPoint(
            name=f"event.{event_name}",
            value=1.0,
            timestamp=timestamp,
            tags={"event": event_name},
            metadata=properties or {}
        )

        self.metrics[f"events.{event_name}"].append(metric_point)
        logger.debug(f"📊 Event tracked: {event_name}")

    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a custom metric."""
        if not self.enabled:
            return

        timestamp = self.get_timestamp()

        metric_point = MetricPoint(
            name=name,
            value=value,
            timestamp=timestamp,
            tags=tags or {}
        )

        self.metrics[name].append(metric_point)

    def start_timer(self, name: str) -> str:
        """Start a timer for measuring duration."""
        timer_id = f"{name}_{int(time.time() * 1000000)}"
        self.timers[timer_id] = [time.time()]
        return timer_id

    def end_timer(self, timer_id: str, tags: Dict[str, str] = None):
        """End a timer and record the duration."""
        if timer_id not in self.timers:
            return

        start_time = self.timers[timer_id][0]
        duration = time.time() - start_time

        # Extract the base name
        base_name = timer_id.rsplit('_', 1)[0]

        # Record the duration
        self.record_metric(f"duration.{base_name}", duration * 1000, tags)  # Convert to milliseconds

        # Clean up
        del self.timers[timer_id]

    async def record_response_time(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """Record API response time metrics."""
        tags = {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code)
        }

        self.record_metric("api.response_time", duration_ms, tags)
        self.counters[f"api.requests.{status_code}"] += 1

        # Check thresholds
        threshold = self.thresholds.get("api_response_time_ms", 5000)
        if duration_ms > threshold:
            await self._trigger_alert("slow_response", {
                "endpoint": endpoint,
                "duration_ms": duration_ms,
                "threshold_ms": threshold
            })

    async def _background_monitor(self):
        """Background task to collect system metrics."""
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                await asyncio.sleep(self.collection_interval)

    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("system.cpu_percent", cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.record_metric("system.memory_percent", memory.percent)
            self.record_metric("system.memory_available_mb", memory.available / (1024 * 1024))

            # Disk usage
            disk = psutil.disk_usage('/')
            self.record_metric("system.disk_percent", disk.percent)
            self.record_metric("system.disk_free_gb", disk.free / (1024 * 1024 * 1024))

            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            self.record_metric("process.memory_rss_mb", process_memory.rss / (1024 * 1024))
            self.record_metric("process.memory_vms_mb", process_memory.vms / (1024 * 1024))

            # Check thresholds
            await self._check_thresholds({
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_usage_mb": process_memory.rss / (1024 * 1024)
            })

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

    async def _check_thresholds(self, current_metrics: Dict[str, float]):
        """Check if any metrics exceed thresholds."""
        # CPU threshold
        cpu_threshold = self.thresholds.get("cpu_percent", 80)
        if current_metrics.get("cpu_percent", 0) > cpu_threshold:
            await self._trigger_alert("high_cpu", {
                "current": current_metrics["cpu_percent"],
                "threshold": cpu_threshold
            })

        # Memory threshold
        memory_threshold = self.thresholds.get("memory_percent", 80)
        if current_metrics.get("memory_percent", 0) > memory_threshold:
            await self._trigger_alert("high_memory", {
                "current": current_metrics["memory_percent"],
                "threshold": memory_threshold
            })

        # Process memory threshold
        process_memory_threshold = self.thresholds.get("memory_usage_mb", 500)
        if current_metrics.get("memory_usage_mb", 0) > process_memory_threshold:
            await self._trigger_alert("high_process_memory", {
                "current": current_metrics["memory_usage_mb"],
                "threshold": process_memory_threshold
            })

    async def _trigger_alert(self, alert_type: str, data: Dict[str, Any]):
        """Trigger an alert for threshold violations."""
        if not self.config.get("alerts", {}).get("enabled", True):
            return

        alert_data = {
            "alert_type": alert_type,
            "timestamp": self.get_timestamp(),
            "data": data,
            "severity": self._get_alert_severity(alert_type)
        }

        # Log the alert
        logger.warning(f"🚨 Alert triggered: {alert_type} - {data}")

        # Track as an event
        await self.track_event("alert_triggered", alert_data)

        # TODO: Send to external alerting system (webhook, email, etc.)
        webhook_url = self.config.get("alerts", {}).get("webhook_url")
        if webhook_url:
            # Send webhook notification
            await self._send_webhook_alert(webhook_url, alert_data)

    def _get_alert_severity(self, alert_type: str) -> str:
        """Get severity level for alert type."""
        severity_map = {
            "high_cpu": "warning",
            "high_memory": "warning",
            "high_process_memory": "warning",
            "slow_response": "warning",
            "system_error": "error",
            "agent_failure": "critical"
        }
        return severity_map.get(alert_type, "info")

    async def _send_webhook_alert(self, webhook_url: str, alert_data: Dict[str, Any]):
        """Send alert to webhook endpoint."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    webhook_url,
                    json=alert_data,
                    timeout=10.0
                )
            logger.info(f"Alert sent to webhook: {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        if not self.enabled:
            return {"enabled": False}

        # Get recent metrics (last 100 points for each metric)
        recent_metrics = {}
        for metric_name, points in self.metrics.items():
            recent_metrics[metric_name] = [asdict(point) for point in list(points)[-100:]]

        # Get counter values
        counter_values = dict(self.counters)

        # Get current system stats
        current_system = await self._get_current_system_stats()

        return {
            "enabled": True,
            "collection_interval_seconds": self.collection_interval,
            "total_metrics": len(self.metrics),
            "total_events": sum(self.counters.values()),
            "recent_metrics": recent_metrics,
            "counters": counter_values,
            "current_system": current_system,
            "thresholds": self.thresholds
        }

    async def _get_current_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()

            # Memory
            memory = psutil.virtual_memory()

            # Disk
            disk = psutil.disk_usage('/')

            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()

            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total_gb": memory.total / (1024 ** 3),
                    "available_gb": memory.available / (1024 ** 3),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": disk.total / (1024 ** 3),
                    "free_gb": disk.free / (1024 ** 3),
                    "percent": disk.percent
                },
                "process": {
                    "memory_rss_mb": process_memory.rss / (1024 ** 2),
                    "memory_vms_mb": process_memory.vms / (1024 ** 2),
                    "pid": process.pid
                }
            }

        except Exception as e:
            logger.error(f"Failed to get current system stats: {e}")
            return {}

    def get_metric_summary(self, metric_name: str, minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for a specific metric over the last N minutes."""
        if metric_name not in self.metrics:
            return {"error": f"Metric {metric_name} not found"}

        # Filter points from the last N minutes
        cutoff_time = datetime.now(timezone.utc).timestamp() - (minutes * 60)
        recent_points = [
            point for point in self.metrics[metric_name]
            if datetime.fromisoformat(point.timestamp.replace('Z', '+00:00')).timestamp() > cutoff_time
        ]

        if not recent_points:
            return {"error": "No recent data points"}

        values = [point.value for point in recent_points]

        return {
            "metric_name": metric_name,
            "period_minutes": minutes,
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else None,
            "latest_timestamp": recent_points[-1].timestamp if recent_points else None
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # Check recent system metrics
            cpu_summary = self.get_metric_summary("system.cpu_percent", 5)
            memory_summary = self.get_metric_summary("system.memory_percent", 5)

            # Determine health status
            status = "healthy"
            issues = []

            # Check CPU
            if not cpu_summary.get("error") and cpu_summary.get("avg", 0) > 80:
                status = "degraded"
                issues.append("High CPU usage")

            # Check memory
            if not memory_summary.get("error") and memory_summary.get("avg", 0) > 80:
                status = "degraded"
                issues.append("High memory usage")

            # Check for recent errors
            error_count = self.counters.get("events.error", 0)
            if error_count > 10:  # More than 10 errors
                status = "degraded"
                issues.append(f"High error count: {error_count}")

            return {
                "status": status,
                "issues": issues,
                "uptime_seconds": time.time() - self.start_time if hasattr(self, 'start_time') else 0,
                "metrics_enabled": self.enabled,
                "last_collection": self.get_timestamp()
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "metrics_enabled": self.enabled
            }

    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        self.metrics.clear()
        self.counters.clear()
        self.timers.clear()
        logger.info("📊 All metrics reset")