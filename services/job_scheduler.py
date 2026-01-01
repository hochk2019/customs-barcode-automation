"""
Job Scheduler v2.0

Unified background job scheduler using APScheduler.
Consolidates all background tasks into a single scheduler.

Responsibilities:
1. Manage periodic clearance checks
2. Run cleanup tasks
3. Emit events for job completion
"""

import threading
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from logging_system.logger import Logger
from services.event_bus import get_event_bus, EventType


class JobScheduler:
    """
    Unified scheduler for all background jobs.
    
    Consolidates:
    - ClearanceChecker periodic checks
    - Database cleanup tasks
    - Any future periodic tasks
    """
    
    def __init__(self, logger: Logger):
        """
        Initialize job scheduler.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self._scheduler = BackgroundScheduler()
        self._is_running = False
        self._jobs: Dict[str, Any] = {}
    
    def start(self) -> None:
        """Start the scheduler."""
        if self._is_running:
            return
        
        self._scheduler.start()
        self._is_running = True
        self.logger.info("JobScheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler gracefully."""
        if not self._is_running:
            return
        
        self._scheduler.shutdown(wait=True)
        self._is_running = False
        self.logger.info("JobScheduler stopped")
    
    def add_job(
        self,
        job_id: str,
        func: Callable,
        interval_seconds: int,
        args: tuple = None,
        start_immediately: bool = False
    ) -> None:
        """
        Add a periodic job.
        
        Args:
            job_id: Unique job identifier
            func: Function to execute
            interval_seconds: Execution interval
            args: Optional function arguments
            start_immediately: If True, run job immediately on add
        """
        # Remove existing job with same ID if any
        self.remove_job(job_id)
        
        job = self._scheduler.add_job(
            func=func,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id=job_id,
            args=args or (),
            replace_existing=True,
            max_instances=1
        )
        
        self._jobs[job_id] = job
        self.logger.info(f"Added job '{job_id}' with interval {interval_seconds}s")
        
        if start_immediately:
            # Run once immediately
            try:
                func(*args) if args else func()
            except Exception as e:
                self.logger.error(f"Immediate job execution failed: {e}")
    
    def remove_job(self, job_id: str) -> None:
        """Remove a job by ID."""
        if job_id in self._jobs:
            try:
                self._scheduler.remove_job(job_id)
                del self._jobs[job_id]
                self.logger.info(f"Removed job '{job_id}'")
            except Exception as e:
                self.logger.warning(f"Failed to remove job '{job_id}': {e}")
    
    def pause_job(self, job_id: str) -> None:
        """Pause a job."""
        if job_id in self._jobs:
            self._scheduler.pause_job(job_id)
            self.logger.info(f"Paused job '{job_id}'")
    
    def resume_job(self, job_id: str) -> None:
        """Resume a paused job."""
        if job_id in self._jobs:
            self._scheduler.resume_job(job_id)
            self.logger.info(f"Resumed job '{job_id}'")
    
    def run_job_now(self, job_id: str) -> None:
        """Manually trigger a job to run immediately."""
        if job_id in self._jobs:
            job = self._jobs[job_id]
            try:
                job.func(*job.args)
                self.logger.info(f"Manually triggered job '{job_id}'")
            except Exception as e:
                self.logger.error(f"Manual job execution failed: {e}")
    
    def update_job_interval(self, job_id: str, new_interval_seconds: int) -> None:
        """Update the interval for an existing job."""
        if job_id in self._jobs:
            job = self._jobs[job_id]
            self._scheduler.reschedule_job(
                job_id,
                trigger=IntervalTrigger(seconds=new_interval_seconds)
            )
            self.logger.info(f"Updated job '{job_id}' interval to {new_interval_seconds}s")
    
    @property
    def is_running(self) -> bool:
        return self._is_running
    
    @property
    def job_ids(self) -> list:
        return list(self._jobs.keys())


# Global instance
_job_scheduler: Optional[JobScheduler] = None


def get_job_scheduler(logger: Logger = None) -> JobScheduler:
    """Get global job scheduler instance."""
    global _job_scheduler
    if _job_scheduler is None and logger is not None:
        _job_scheduler = JobScheduler(logger)
    return _job_scheduler
