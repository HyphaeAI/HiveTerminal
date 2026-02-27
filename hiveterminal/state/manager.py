"""Local state management for HiveTerminal.

This module provides persistent state storage for agentic tasks,
reducing reliance on chat history and minimizing token usage.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class StateEntry(BaseModel):
    """A single state entry with metadata."""
    
    key: str
    value: Any
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    description: str | None = None


class WorkingState(BaseModel):
    """The current working state for an agentic session."""
    
    session_id: str
    entries: Dict[str, StateEntry] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def set(self, key: str, value: Any, description: str | None = None) -> None:
        """Set a state value."""
        now = datetime.now()
        if key in self.entries:
            self.entries[key].value = value
            self.entries[key].updated_at = now
            if description:
                self.entries[key].description = description
        else:
            self.entries[key] = StateEntry(
                key=key,
                value=value,
                created_at=now,
                updated_at=now,
                description=description
            )
        self.updated_at = now
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        entry = self.entries.get(key)
        return entry.value if entry else default
    
    def delete(self, key: str) -> bool:
        """Delete a state entry."""
        if key in self.entries:
            del self.entries[key]
            self.updated_at = datetime.now()
            return True
        return False
    
    def clear(self) -> None:
        """Clear all state entries."""
        self.entries.clear()
        self.updated_at = datetime.now()
    
    def to_context_string(self) -> str:
        """Convert state to a compact string for prompt injection."""
        if not self.entries:
            return ""
        
        lines = ["## Current Working State"]
        for key, entry in self.entries.items():
            desc = f" ({entry.description})" if entry.description else ""
            value_str = self._format_value(entry.value)
            lines.append(f"- **{key}**{desc}: {value_str}")
        
        return "\n".join(lines)
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display in context."""
        if isinstance(value, (dict, list)):
            # For complex objects, show compact JSON
            json_str = json.dumps(value, indent=None)
            if len(json_str) > 200:
                return json_str[:197] + "..."
            return json_str
        elif isinstance(value, str) and len(value) > 200:
            return value[:197] + "..."
        else:
            return str(value)


class StateManager:
    """Manages local state for agentic tasks.
    
    Provides persistent storage for working state, reducing token usage
    by storing data locally instead of in chat history.
    """
    
    def __init__(self, state_dir: Path | str = ".hive_state"):
        """Initialize the state manager.
        
        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._current_state: WorkingState | None = None
        logger.debug(f"StateManager initialized with state_dir: {self.state_dir}")
    
    def get_state_file(self, session_id: str) -> Path:
        """Get the state file path for a session."""
        return self.state_dir / f"{session_id}.json"
    
    def load_state(self, session_id: str) -> WorkingState:
        """Load state for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            WorkingState for the session
        """
        state_file = self.get_state_file(session_id)
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                state = WorkingState.model_validate(data)
                logger.debug(f"Loaded state for session {session_id}: {len(state.entries)} entries")
                self._current_state = state
                return state
            except Exception as e:
                logger.warning(f"Failed to load state for session {session_id}: {e}")
        
        # Create new state
        state = WorkingState(session_id=session_id)
        self._current_state = state
        logger.debug(f"Created new state for session {session_id}")
        return state
    
    def save_state(self, state: WorkingState) -> None:
        """Save state to disk.
        
        Args:
            state: The state to save
        """
        state_file = self.get_state_file(state.session_id)
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state.model_dump(mode='json'), f, indent=2, default=str)
            logger.debug(f"Saved state for session {state.session_id}: {len(state.entries)} entries")
        except Exception as e:
            logger.error(f"Failed to save state for session {state.session_id}: {e}")
    
    def get_current_state(self) -> WorkingState | None:
        """Get the current working state."""
        return self._current_state
    
    def set_current_state(self, state: WorkingState) -> None:
        """Set the current working state."""
        self._current_state = state
    
    def set_value(self, key: str, value: Any, description: str | None = None) -> None:
        """Set a value in the current state.
        
        Args:
            key: The state key
            value: The value to store
            description: Optional description of what this state represents
        """
        if not self._current_state:
            raise RuntimeError("No current state loaded. Call load_state() first.")
        
        self._current_state.set(key, value, description)
        self.save_state(self._current_state)
        logger.debug(f"Set state value: {key} = {self._format_value_for_log(value)}")
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a value from the current state.
        
        Args:
            key: The state key
            default: Default value if key doesn't exist
            
        Returns:
            The stored value or default
        """
        if not self._current_state:
            return default
        
        return self._current_state.get(key, default)
    
    def delete_value(self, key: str) -> bool:
        """Delete a value from the current state.
        
        Args:
            key: The state key
            
        Returns:
            True if deleted, False if key didn't exist
        """
        if not self._current_state:
            return False
        
        deleted = self._current_state.delete(key)
        if deleted:
            self.save_state(self._current_state)
            logger.debug(f"Deleted state value: {key}")
        return deleted
    
    def clear_state(self) -> None:
        """Clear all state for the current session."""
        if not self._current_state:
            return
        
        self._current_state.clear()
        self.save_state(self._current_state)
        logger.debug(f"Cleared state for session {self._current_state.session_id}")
    
    def get_context_string(self) -> str:
        """Get a formatted string of current state for prompt injection.
        
        Returns:
            Formatted state string for inclusion in prompts
        """
        if not self._current_state:
            return ""
        
        return self._current_state.to_context_string()
    
    def list_sessions(self) -> list[str]:
        """List all session IDs with saved state.
        
        Returns:
            List of session IDs
        """
        return [f.stem for f in self.state_dir.glob("*.json")]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete state for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            True if deleted, False if session didn't exist
        """
        state_file = self.get_state_file(session_id)
        if state_file.exists():
            state_file.unlink()
            logger.debug(f"Deleted state for session {session_id}")
            return True
        return False
    
    def _format_value_for_log(self, value: Any) -> str:
        """Format a value for logging (truncated)."""
        value_str = str(value)
        if len(value_str) > 100:
            return value_str[:97] + "..."
        return value_str


# Global state manager instance
_state_manager: StateManager | None = None


def get_state_manager(state_dir: Path | str = ".hive_state") -> StateManager:
    """Get or create the global state manager instance.
    
    Args:
        state_dir: Directory to store state files
        
    Returns:
        StateManager instance
    """
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager(state_dir)
    return _state_manager
