"""Mode switching functionality for HiveTerminal.

This module provides utilities for switching between conversational and
spec-first modes during runtime.
"""

from __future__ import annotations

import logging
from typing import Optional

from rich.console import Console

from hiveterminal.cli.mode_selection import show_mode_selection, show_mode_indicator

logger = logging.getLogger(__name__)


class ModeSwitcher:
    """Handles mode switching during runtime.
    
    This class manages the state and logic for switching between
    conversational and spec-first modes while preserving conversation
    history and memory manager instance.
    
    Example:
        >>> switcher = ModeSwitcher(current_mode="conversational")
        >>> new_mode = switcher.prompt_mode_switch()
        >>> if new_mode != switcher.current_mode:
        ...     switcher.switch_mode(new_mode)
    """
    
    def __init__(self, current_mode: str):
        """Initialize the mode switcher.
        
        Args:
            current_mode: Current operation mode ('conversational' or 'spec')
        """
        self.current_mode = current_mode
        self.console = Console()
    
    def prompt_mode_switch(self) -> str:
        """Prompt user to select a new mode.
        
        Returns:
            Selected mode ('conversational' or 'spec')
        """
        self.console.print("\n[bold cyan]Mode Selection[/bold cyan]\n")
        self.console.print(f"Current mode: [yellow]{self.current_mode}[/yellow]\n")
        
        return show_mode_selection()
    
    def switch_mode(self, new_mode: str) -> bool:
        """Switch to a new mode.
        
        Args:
            new_mode: New mode to switch to
            
        Returns:
            True if mode was changed, False if already in that mode
        """
        if new_mode == self.current_mode:
            self.console.print(
                f"\n[yellow]Already in {new_mode} mode.[/yellow]\n"
            )
            return False
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        
        self.console.print(
            f"\n[green]✓ Switched from {old_mode} to {new_mode} mode[/green]\n"
        )
        
        show_mode_indicator(new_mode)
        
        logger.info(f"Mode switched: {old_mode} -> {new_mode}")
        
        return True
    
    def handle_mode_command(self, user_input: str) -> tuple[bool, Optional[str]]:
        """Handle /mode command from user input.
        
        Args:
            user_input: User's input string
            
        Returns:
            Tuple of (is_mode_command, new_mode)
            - is_mode_command: True if input was a /mode command
            - new_mode: New mode if switched, None otherwise
        """
        if not user_input.strip().startswith("/mode"):
            return False, None
        
        # Prompt for mode selection
        new_mode = self.prompt_mode_switch()
        
        # Switch if different
        if self.switch_mode(new_mode):
            return True, new_mode
        
        return True, None


def detect_mode_command(user_input: str) -> bool:
    """Detect if user input is a mode switch command.
    
    Args:
        user_input: User's input string
        
    Returns:
        True if input is a /mode command
    """
    return user_input.strip().startswith("/mode")


def create_mode_switcher(initial_mode: str) -> ModeSwitcher:
    """Create a ModeSwitcher instance.
    
    Args:
        initial_mode: Initial operation mode
        
    Returns:
        ModeSwitcher instance
    """
    return ModeSwitcher(initial_mode)
