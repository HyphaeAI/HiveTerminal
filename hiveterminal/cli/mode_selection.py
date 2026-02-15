"""Mode selection UI for HiveTerminal.

This module provides an interactive mode selection interface that allows
users to choose between Conversational Mode and Spec-First Mode.
"""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Prompt


def show_mode_selection() -> str:
    """Display interactive mode selection with examples.
    
    This function presents the user with a clear comparison of both modes
    and prompts them to select their preferred workflow.
    
    Returns:
        Selected mode: "conversational" or "spec"
    """
    console = Console()
    
    console.print("\n[bold cyan]Welcome to HiveTerminal![/bold cyan]\n")
    console.print("Choose your workflow mode:\n")
    
    # Option 1: Conversational Mode
    console.print("[bold green]1. Conversational Mode[/bold green] (Flexible, Interactive)")
    console.print("   [dim]→ Agent executes tools one-by-one with your approval[/dim]")
    console.print("\n   [yellow]Example:[/yellow]")
    console.print("   [dim]You: 'Refactor the login function'[/dim]")
    console.print("   [dim]Agent: 'I'll read the file first' → [Tool: read_file] → You approve[/dim]")
    console.print("   [dim]Agent: 'Now I'll make changes' → [Tool: write_file] → You approve[/dim]")
    console.print("   [dim]Agent: 'Let me run tests' → [Tool: bash] → You approve[/dim]")
    console.print("   [dim]✓ Best for: Exploration, quick tasks, iterative development[/dim]\n")
    
    # Option 2: Spec-First Mode
    console.print("[bold blue]2. Spec-First Mode[/bold blue] (Structured, Transparent)")
    console.print("   [dim]→ Agent creates complete plan, you approve once, then executes all[/dim]")
    console.print("\n   [yellow]Example:[/yellow]")
    console.print("   [dim]You: 'Refactor the login function'[/dim]")
    console.print("   [dim]Agent shows plan:[/dim]")
    console.print("   [dim]  # Execution Plan[/dim]")
    console.print("   [dim]  1. Read login.py[/dim]")
    console.print("   [dim]  2. Refactor to use async/await[/dim]")
    console.print("   [dim]  3. Update tests[/dim]")
    console.print("   [dim]  4. Run test suite[/dim]")
    console.print("   [dim]You: Approve plan (y/n) → 'y'[/dim]")
    console.print("   [dim]Agent: Executes all steps automatically[/dim]")
    console.print("   [dim]✓ Best for: Complex tasks, batch operations, transparency[/dim]\n")
    
    console.print("[dim]You can switch modes anytime with /mode command[/dim]\n")
    
    # Get user choice
    choice = Prompt.ask(
        "Select mode",
        choices=["1", "2", "conversational", "spec"],
        default="1"
    )
    
    if choice in ["1", "conversational"]:
        console.print("\n[green]✓ Conversational Mode selected[/green]\n")
        return "conversational"
    else:
        console.print("\n[blue]✓ Spec-First Mode selected[/blue]\n")
        return "spec"


def show_mode_indicator(mode: str) -> str:
    """Get a mode indicator string for display in the prompt.
    
    Args:
        mode: Current mode ("conversational" or "spec")
        
    Returns:
        Formatted mode indicator string
    """
    if mode == "conversational":
        return "[dim][Conversational][/dim]"
    elif mode == "spec":
        return "[dim][Spec][/dim]"
    else:
        return ""


def confirm_mode_switch(current_mode: str, new_mode: str) -> bool:
    """Confirm mode switch with the user.
    
    Args:
        current_mode: Current mode
        new_mode: New mode to switch to
        
    Returns:
        True if user confirms, False otherwise
    """
    console = Console()
    
    console.print(f"\n[yellow]Switch from {current_mode} to {new_mode} mode?[/yellow]")
    console.print("[dim]Conversation history will be preserved.[/dim]\n")
    
    response = Prompt.ask(
        "Confirm",
        choices=["y", "n", "yes", "no"],
        default="y"
    )
    
    return response in ["y", "yes"]
