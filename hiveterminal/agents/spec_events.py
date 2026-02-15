"""Event types for spec-first mode.

This module defines event types that are emitted during the three-phase
workflow of the SpecAgentLoop. These events can be used for logging,
monitoring, and UI updates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime

from hiveterminal.agents.spec_agent import Action


@dataclass
class BaseSpecEvent:
    """Base class for all spec mode events.
    
    Attributes:
        timestamp: When the event occurred
        event_type: Type of event
    """
    timestamp: datetime
    event_type: str
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if not hasattr(self, 'timestamp') or self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class PlanGeneratedEvent(BaseSpecEvent):
    """Event emitted when a plan is generated.
    
    This event is emitted at the end of Phase 1 (Plan Generation).
    
    Attributes:
        plan: The generated markdown plan
        context_chunks: Number of code chunks used for context
        generation_time: Time taken to generate the plan (seconds)
    """
    plan: str
    context_chunks: int = 0
    generation_time: float = 0.0
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "plan_generated"
        super().__post_init__()


@dataclass
class PlanApprovedEvent(BaseSpecEvent):
    """Event emitted when a plan is approved by the user.
    
    This event is emitted at the end of Phase 2 (Approval).
    
    Attributes:
        plan: The approved plan
        approval_time: Time taken for user to approve (seconds)
    """
    plan: str
    approval_time: float = 0.0
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "plan_approved"
        super().__post_init__()


@dataclass
class PlanRejectedEvent(BaseSpecEvent):
    """Event emitted when a plan is rejected by the user.
    
    This event is emitted during Phase 2 (Approval) if user rejects.
    
    Attributes:
        plan: The rejected plan
        reason: Optional reason for rejection
    """
    plan: str
    reason: Optional[str] = None
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "plan_rejected"
        super().__post_init__()


@dataclass
class ActionStartEvent(BaseSpecEvent):
    """Event emitted when an action starts executing.
    
    This event is emitted during Phase 3 (Execution) for each action.
    
    Attributes:
        action: The action being executed
        action_number: Position in execution sequence
        total_actions: Total number of actions in plan
    """
    action: Action
    action_number: int = 0
    total_actions: int = 0
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "action_start"
        super().__post_init__()


@dataclass
class ActionCompleteEvent(BaseSpecEvent):
    """Event emitted when an action completes successfully.
    
    This event is emitted during Phase 3 (Execution) after each successful action.
    
    Attributes:
        action: The completed action
        result: Result data from the action execution
        execution_time: Time taken to execute (seconds)
    """
    action: Action
    result: Dict[str, Any]
    execution_time: float = 0.0
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "action_complete"
        super().__post_init__()


@dataclass
class ActionErrorEvent(BaseSpecEvent):
    """Event emitted when an action fails.
    
    This event is emitted during Phase 3 (Execution) if an action fails.
    
    Attributes:
        action: The failed action
        error: Error message or exception details
        is_recoverable: Whether the error can be recovered from
        retry_count: Number of times this action has been retried
    """
    action: Action
    error: str
    is_recoverable: bool = False
    retry_count: int = 0
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "action_error"
        super().__post_init__()


@dataclass
class ExecutionCompleteEvent(BaseSpecEvent):
    """Event emitted when plan execution completes.
    
    This event is emitted at the end of Phase 3 (Execution).
    
    Attributes:
        total_actions: Total number of actions in plan
        completed_actions: Number of successfully completed actions
        failed_actions: Number of failed actions
        execution_time: Total execution time (seconds)
        files_modified: Number of files modified
    """
    total_actions: int
    completed_actions: int
    failed_actions: int
    execution_time: float
    files_modified: int = 0
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "execution_complete"
        super().__post_init__()


@dataclass
class MemoryIngestEvent(BaseSpecEvent):
    """Event emitted when modified files are ingested into memory.
    
    This event is emitted after execution completes and files are ingested.
    
    Attributes:
        files_ingested: Number of files successfully ingested
        chunks_created: Number of code chunks created
        ingestion_time: Time taken to ingest (seconds)
    """
    files_ingested: int
    chunks_created: int = 0
    ingestion_time: float = 0.0
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "memory_ingest"
        super().__post_init__()


@dataclass
class ContextRetrievalEvent(BaseSpecEvent):
    """Event emitted when context is retrieved from memory.
    
    This event is emitted during Phase 1 when retrieving relevant code context.
    
    Attributes:
        query: The query used for retrieval
        chunks_retrieved: Number of chunks retrieved
        retrieval_time: Time taken to retrieve (seconds)
        top_similarity: Highest similarity score
    """
    query: str
    chunks_retrieved: int
    retrieval_time: float = 0.0
    top_similarity: float = 0.0
    
    def __post_init__(self):
        """Initialize event type."""
        self.event_type = "context_retrieval"
        super().__post_init__()


# Event handler type
EventHandler = callable[[BaseSpecEvent], None]


class SpecEventEmitter:
    """Event emitter for spec mode events.
    
    This class manages event handlers and emits events during the
    three-phase workflow.
    
    Example:
        >>> emitter = SpecEventEmitter()
        >>> emitter.on('plan_generated', lambda e: print(f"Plan: {e.plan}"))
        >>> emitter.emit(PlanGeneratedEvent(plan="# My Plan"))
    """
    
    def __init__(self):
        """Initialize the event emitter."""
        self._handlers: Dict[str, list[EventHandler]] = {}
    
    def on(self, event_type: str, handler: EventHandler) -> None:
        """Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Callback function to handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def off(self, event_type: str, handler: EventHandler) -> None:
        """Unregister an event handler.
        
        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    def emit(self, event: BaseSpecEvent) -> None:
        """Emit an event to all registered handlers.
        
        Args:
            event: Event to emit
        """
        event_type = event.event_type
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # Log but don't fail on handler errors
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Event handler error: {e}")
    
    def clear(self, event_type: Optional[str] = None) -> None:
        """Clear event handlers.
        
        Args:
            event_type: Specific event type to clear, or None to clear all
        """
        if event_type:
            self._handlers.pop(event_type, None)
        else:
            self._handlers.clear()


# Global event emitter instance
_global_emitter = SpecEventEmitter()


def get_event_emitter() -> SpecEventEmitter:
    """Get the global event emitter instance.
    
    Returns:
        Global SpecEventEmitter instance
    """
    return _global_emitter


def emit_event(event: BaseSpecEvent) -> None:
    """Emit an event using the global emitter.
    
    Args:
        event: Event to emit
    """
    _global_emitter.emit(event)


def on_event(event_type: str, handler: EventHandler) -> None:
    """Register a handler with the global emitter.
    
    Args:
        event_type: Type of event to handle
        handler: Callback function
    """
    _global_emitter.on(event_type, handler)
