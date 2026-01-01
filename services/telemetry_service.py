"""
Telemetry Service v2.0

Simple telemetry for tracking barcode retrieval performance.
Collects metrics without external dependencies.

Metrics collected:
- API success/failure rates
- Response times
- Circuit breaker state changes
"""

import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import deque
import json
import os

from logging_system.logger import Logger


@dataclass
class TelemetryMetric:
    """Single telemetry data point."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)


class TelemetryService:
    """
    Simple telemetry collection service.
    
    Stores metrics in memory with optional file persistence.
    No external dependencies required.
    """
    
    def __init__(
        self, 
        logger: Optional[Logger] = None,
        max_metrics: int = 1000,
        persist_path: str = None
    ):
        """
        Initialize telemetry service.
        
        Args:
            logger: Optional logger
            max_metrics: Max metrics to keep in memory
            persist_path: Optional path to persist metrics
        """
        self.logger = logger
        self.max_metrics = max_metrics
        self.persist_path = persist_path
        
        self._metrics: deque = deque(maxlen=max_metrics)
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def record(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """
        Record a metric value.
        
        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for filtering
        """
        metric = TelemetryMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        
        with self._lock:
            self._metrics.append(metric)
    
    def increment(self, name: str, amount: int = 1) -> None:
        """Increment a counter."""
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + amount
    
    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge value."""
        with self._lock:
            self._gauges[name] = value
    
    def get_counter(self, name: str) -> int:
        """Get counter value."""
        with self._lock:
            return self._counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """Get gauge value."""
        with self._lock:
            return self._gauges.get(name, 0.0)
    
    def get_metrics(self, name: str = None, limit: int = 100) -> List[TelemetryMetric]:
        """
        Get recent metrics.
        
        Args:
            name: Filter by metric name
            limit: Max metrics to return
            
        Returns:
            List of metrics
        """
        with self._lock:
            metrics = list(self._metrics)
        
        if name:
            metrics = [m for m in metrics if m.name == name]
        
        return metrics[-limit:]
    
    def get_summary(self, name: str) -> Dict[str, Any]:
        """
        Get summary statistics for a metric.
        
        Args:
            name: Metric name
            
        Returns:
            Dict with count, min, max, avg
        """
        metrics = self.get_metrics(name)
        if not metrics:
            return {"count": 0, "min": 0, "max": 0, "avg": 0}
        
        values = [m.value for m in metrics]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values)
        }
    
    def time_operation(self, name: str):
        """
        Context manager to time an operation.
        
        Usage:
            with telemetry.time_operation("api_call"):
                response = api.call()
        """
        return OperationTimer(self, name)
    
    def persist(self) -> None:
        """Persist metrics to file."""
        if not self.persist_path:
            return
        
        try:
            data = {
                "counters": self._counters,
                "gauges": self._gauges,
                "metrics_count": len(self._metrics)
            }
            
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            with open(self.persist_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to persist telemetry: {e}")


class OperationTimer:
    """Context manager for timing operations."""
    
    def __init__(self, telemetry: TelemetryService, name: str):
        self.telemetry = telemetry
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.telemetry.record(self.name, duration)
        
        if exc_type:
            self.telemetry.increment(f"{self.name}.errors")
        else:
            self.telemetry.increment(f"{self.name}.success")


# Global instance
_telemetry: Optional[TelemetryService] = None


def get_telemetry(logger: Logger = None) -> TelemetryService:
    """Get global telemetry service."""
    global _telemetry
    if _telemetry is None:
        _telemetry = TelemetryService(logger=logger)
    return _telemetry
