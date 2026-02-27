"""State management tool for HiveTerminal.

Allows the AI to store and retrieve working state locally,
reducing reliance on chat history and minimizing token usage.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# Import from Vibe's core
import sys
from pathlib import Path
vibe_path = Path(__file__).parent.parent.parent / "Vibe"
sys.path.insert(0, str(vibe_path))

from vibe.core.tools.base import BaseTool, BaseToolConfig, BaseToolState, InvokeContext
from vibe.core.types import ToolStreamEvent


class StateOperation(StrEnum):
    """State operations."""
    SET = "set"
    GET = "get"
    DELETE = "delete"
    LIST = "list"
    CLEAR = "clear"


class StateArgs(BaseModel):
    """Arguments for state management tool."""
    
    operation: StateOperation = Field(
        description="The operation to perform: set, get, delete, list, or clear"
    )
    key: str | None = Field(
        default=None,
        description="The state key (required for set, get, delete operations)"
    )
    value: Any | None = Field(
        default=None,
        description="The value to store (required for set operation). Can be any JSON-serializable type."
    )
    description: str | None = Field(
        default=None,
        description="Optional description of what this state represents (for set operation)"
    )


class StateResult(BaseModel):
    """Result from state management tool."""
    
    success: bool = Field(description="Whether the operation succeeded")
    operation: str = Field(description="The operation that was performed")
    key: str | None = Field(default=None, description="The state key (if applicable)")
    value: Any | None = Field(default=None, description="The retrieved value (for get operation)")
    keys: list[str] | None = Field(default=None, description="List of state keys (for list operation)")
    message: str = Field(description="Human-readable result message")


class StateToolConfig(BaseToolConfig):
    """Configuration for state tool."""
    pass


class StateToolState(BaseToolState):
    """State for state tool."""
    pass


class StateTool(BaseTool[StateArgs, StateResult, StateToolConfig, StateToolState]):
    """Tool for managing local working state.
    
    This tool allows storing and retrieving data locally instead of relying
    on chat history, significantly reducing token usage for agentic tasks.
    
    Use cases:
    - Store todo lists, task queues, or work items
    - Remember file paths, directory structures, or project state
    - Keep track of multi-step workflows
    - Store JSON objects, configurations, or data structures
    - Maintain context across conversation turns without bloating history
    
    Examples:
    - state(operation="set", key="todos", value=["task1", "task2"], description="Current todo list")
    - state(operation="get", key="todos")
    - state(operation="list")
    - state(operation="delete", key="todos")
    - state(operation="clear")
    """
    
    description = (
        "Manage local working state to reduce token usage. "
        "Store data locally instead of relying on chat history. "
        "Supports set, get, delete, list, and clear operations."
    )
    
    async def run(
        self, args: StateArgs, ctx: InvokeContext | None = None
    ) -> AsyncGenerator[ToolStreamEvent | StateResult, None]:
        """Execute state management operation."""
        
        # Get state manager from global instance
        try:
            from hiveterminal.state import get_state_manager
            state_manager = get_state_manager()
        except ImportError:
            yield StateResult(
                success=False,
                operation=args.operation,
                message="State manager not available (HiveTerminal not installed)"
            )
            return
        
        if not state_manager or not state_manager.get_current_state():
            yield StateResult(
                success=False,
                operation=args.operation,
                message="State manager not initialized (no active session)"
            )
            return
        
        try:
            if args.operation == StateOperation.SET:
                if not args.key:
                    yield StateResult(
                        success=False,
                        operation=args.operation,
                        message="Key is required for set operation"
                    )
                    return
                
                if args.value is None:
                    yield StateResult(
                        success=False,
                        operation=args.operation,
                        message="Value is required for set operation"
                    )
                    return
                
                state_manager.set_value(args.key, args.value, args.description)
                yield StateResult(
                    success=True,
                    operation=args.operation,
                    key=args.key,
                    message=f"Set state: {args.key}"
                )
            
            elif args.operation == StateOperation.GET:
                if not args.key:
                    yield StateResult(
                        success=False,
                        operation=args.operation,
                        message="Key is required for get operation"
                    )
                    return
                
                value = state_manager.get_value(args.key)
                if value is None:
                    yield StateResult(
                        success=False,
                        operation=args.operation,
                        key=args.key,
                        message=f"State key not found: {args.key}"
                    )
                else:
                    yield StateResult(
                        success=True,
                        operation=args.operation,
                        key=args.key,
                        value=value,
                        message=f"Retrieved state: {args.key}"
                    )
            
            elif args.operation == StateOperation.DELETE:
                if not args.key:
                    yield StateResult(
                        success=False,
                        operation=args.operation,
                        message="Key is required for delete operation"
                    )
                    return
                
                deleted = state_manager.delete_value(args.key)
                if deleted:
                    yield StateResult(
                        success=True,
                        operation=args.operation,
                        key=args.key,
                        message=f"Deleted state: {args.key}"
                    )
                else:
                    yield StateResult(
                        success=False,
                        operation=args.operation,
                        key=args.key,
                        message=f"State key not found: {args.key}"
                    )
            
            elif args.operation == StateOperation.LIST:
                current_state = state_manager.get_current_state()
                if current_state and current_state.entries:
                    keys = list(current_state.entries.keys())
                    yield StateResult(
                        success=True,
                        operation=args.operation,
                        keys=keys,
                        message=f"Found {len(keys)} state entries"
                    )
                else:
                    yield StateResult(
                        success=True,
                        operation=args.operation,
                        keys=[],
                        message="No state entries found"
                    )
            
            elif args.operation == StateOperation.CLEAR:
                state_manager.clear_state()
                yield StateResult(
                    success=True,
                    operation=args.operation,
                    message="Cleared all state"
                )
            
            else:
                yield StateResult(
                    success=False,
                    operation=args.operation,
                    message=f"Unknown operation: {args.operation}"
                )
        
        except Exception as e:
            yield StateResult(
                success=False,
                operation=args.operation,
                message=f"Error: {str(e)}"
            )
    
    @classmethod
    def _get_tool_state_class(cls) -> type[StateToolState]:
        return StateToolState
