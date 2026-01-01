"""
Workflow Events v2.0

Event definitions for workflow progress and completion notifications.
Used by WorkflowService to communicate with UI components.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any
from enum import Enum


class WorkflowEventType(Enum):
    """Types of workflow events."""
    STARTED = "started"
    PROGRESS = "progress"
    DECLARATION_PROCESSED = "declaration_processed"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class WorkflowEvent:
    """
    Base class for workflow events.
    
    Attributes:
        event_type: Type of event
        timestamp: When event occurred
        message: Human-readable message
        data: Optional additional data
    """
    event_type: WorkflowEventType
    timestamp: datetime
    message: str
    data: Optional[dict] = None
    
    @classmethod
    def started(cls, total_declarations: int) -> 'WorkflowEvent':
        """Create a started event."""
        return cls(
            event_type=WorkflowEventType.STARTED,
            timestamp=datetime.now(),
            message=f"Workflow started with {total_declarations} declarations",
            data={"total": total_declarations}
        )
    
    @classmethod
    def progress(cls, current: int, total: int, declaration_id: str = None) -> 'WorkflowEvent':
        """Create a progress event."""
        percent = int((current / total) * 100) if total > 0 else 0
        return cls(
            event_type=WorkflowEventType.PROGRESS,
            timestamp=datetime.now(),
            message=f"Processing {current}/{total} ({percent}%)",
            data={
                "current": current,
                "total": total,
                "percent": percent,
                "declaration_id": declaration_id
            }
        )
    
    @classmethod
    def declaration_processed(cls, declaration_id: str, success: bool, file_path: str = None) -> 'WorkflowEvent':
        """Create a declaration processed event."""
        status = "success" if success else "failed"
        return cls(
            event_type=WorkflowEventType.DECLARATION_PROCESSED,
            timestamp=datetime.now(),
            message=f"Declaration {declaration_id}: {status}",
            data={
                "declaration_id": declaration_id,
                "success": success,
                "file_path": file_path
            }
        )
    
    @classmethod
    def completed(cls, success_count: int, error_count: int, duration_seconds: float) -> 'WorkflowEvent':
        """Create a completed event."""
        return cls(
            event_type=WorkflowEventType.COMPLETED,
            timestamp=datetime.now(),
            message=f"Completed: {success_count} success, {error_count} errors in {duration_seconds:.1f}s",
            data={
                "success_count": success_count,
                "error_count": error_count,
                "duration_seconds": duration_seconds
            }
        )
    
    @classmethod
    def error(cls, error_message: str, declaration_id: str = None) -> 'WorkflowEvent':
        """Create an error event."""
        return cls(
            event_type=WorkflowEventType.ERROR,
            timestamp=datetime.now(),
            message=f"Error: {error_message}",
            data={
                "error": error_message,
                "declaration_id": declaration_id
            }
        )
    
    @classmethod
    def cancelled(cls) -> 'WorkflowEvent':
        """Create a cancelled event."""
        return cls(
            event_type=WorkflowEventType.CANCELLED,
            timestamp=datetime.now(),
            message="Workflow cancelled by user"
        )
