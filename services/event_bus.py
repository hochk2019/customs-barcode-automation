"""
Event Bus v2.0

Simple publish/subscribe event bus for decoupled communication.
Used for notification coordination across components.
"""

import threading
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """Global event types."""
    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_PROGRESS = "workflow.progress"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_ERROR = "workflow.error"
    
    # Clearance events
    CLEARANCE_CHECKED = "clearance.checked"
    CLEARANCE_CLEARED = "clearance.cleared"
    
    # Tracking events
    TRACKING_ADDED = "tracking.added"
    TRACKING_UPDATED = "tracking.updated"
    
    # Notification events
    NOTIFICATION_SHOW = "notification.show"


@dataclass
class Event:
    """
    Generic event container.
    
    Attributes:
        event_type: Type of event
        timestamp: When event was created
        data: Event payload
        source: Component that emitted the event
    """
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "unknown"
    
    @classmethod
    def create(cls, event_type: EventType, data: Dict[str, Any], source: str = "unknown") -> 'Event':
        """Create a new event."""
        return cls(
            event_type=event_type,
            timestamp=datetime.now(),
            data=data,
            source=source
        )


class EventBus:
    """
    Thread-safe publish/subscribe event bus.
    
    Usage:
        bus = EventBus()
        bus.subscribe(EventType.WORKFLOW_COMPLETED, my_handler)
        bus.publish(EventType.WORKFLOW_COMPLETED, {"success": 10})
    """
    
    def __init__(self):
        """Initialize event bus."""
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._lock = threading.RLock()
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Function to call when event occurs
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        with self._lock:
            if event_type in self._subscribers:
                if handler in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(handler)
    
    def publish(self, event_type: EventType, data: Dict[str, Any] = None, source: str = "unknown") -> None:
        """
        Publish an event.
        
        Args:
            event_type: Type of event
            data: Event payload
            source: Component emitting the event
        """
        event = Event.create(event_type, data or {}, source)
        
        with self._lock:
            handlers = self._subscribers.get(event_type, []).copy()
        
        # Call handlers outside lock to prevent deadlocks
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Event handler error: {e}")
    
    def clear(self, event_type: EventType = None) -> None:
        """
        Clear subscribers.
        
        Args:
            event_type: Specific type to clear, or None for all
        """
        with self._lock:
            if event_type:
                self._subscribers[event_type] = []
            else:
                self._subscribers.clear()


# Global event bus instance
_event_bus: EventBus = None
_bus_lock = threading.Lock()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        with _bus_lock:
            if _event_bus is None:
                _event_bus = EventBus()
    return _event_bus
