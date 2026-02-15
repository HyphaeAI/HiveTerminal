"""HiveTerminal CLI entry point.

This module serves as the main entry point for the `hive` command.
It extends Vibe's CLI with HiveTerminal-specific features:
- Memory management commands (--rebuild-memory, --memory-stats)
- Future: Mode selection (conversational vs spec-first)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from vibe import __version__
from vibe.core.agents.models import BuiltinAgentName
from vibe.core.paths.config_paths import unlock_config_paths
from vibe.core.trusted_folders import has_trustable_content, trusted_folders_manager
from vibe.setup.trusted_folders.trust_folder_dialog import (
    TrustDialogQuitException,
    ask_trust_folder,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for HiveTerminal.
    
    Extends Vibe's argument parser with HiveTerminal-specific options.
    """
    parser = argparse.ArgumentParser(description="Run the HiveTerminal interactive CLI")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "initial_prompt",
        nargs="?",
        metavar="PROMPT",
        help="Initial prompt to start the interactive session with.",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        nargs="?",
        const="",
        metavar="TEXT",
        help="Run in programmatic mode: send prompt, auto-approve all tools, "
        "output response, and exit.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        metavar="N",
        help="Maximum number of assistant turns "
        "(only applies in programmatic mode with -p).",
    )
    parser.add_argument(
        "--max-price",
        type=float,
        metavar="DOLLARS",
        help="Maximum cost in dollars (only applies in programmatic mode with -p). "
        "Session will be interrupted if cost exceeds this limit.",
    )
    parser.add_argument(
        "--enabled-tools",
        action="append",
        metavar="TOOL",
        help="Enable specific tools. In programmatic mode (-p), this disables "
        "all other tools. "
        "Can use exact names, glob patterns (e.g., 'bash*'), or "
        "regex with 're:' prefix. Can be specified multiple times.",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json", "streaming"],
        default="text",
        help="Output format for programmatic mode (-p): 'text' "
        "for human-readable (default), 'json' for all messages at end, "
        "'streaming' for newline-delimited JSON per message.",
    )
    parser.add_argument(
        "--agent",
        metavar="NAME",
        default=BuiltinAgentName.DEFAULT,
        help="Agent to use (builtin: default, plan, accept-edits, auto-approve, "
        "or custom from ~/.vibe/agents/NAME.toml)",
    )
    parser.add_argument("--setup", action="store_true", help="Setup API key and exit")
    parser.add_argument(
        "--workdir",
        type=Path,
        metavar="DIR",
        help="Change to this directory before running",
    )

    # Feature flag for teleport, not exposed to the user yet
    parser.add_argument("--teleport", action="store_true", help=argparse.SUPPRESS)

    continuation_group = parser.add_mutually_exclusive_group()
    continuation_group.add_argument(
        "-c",
        "--continue",
        action="store_true",
        dest="continue_session",
        help="Continue from the most recent saved session",
    )
    continuation_group.add_argument(
        "--resume",
        metavar="SESSION_ID",
        help="Resume a specific session by its ID (supports partial matching)",
    )
    
    # HiveTerminal-specific memory management commands
    memory_group = parser.add_argument_group("memory management")
    memory_group.add_argument(
        "--rebuild-memory",
        action="store_true",
        help="Rebuild the Hive Mind vector database from scratch",
    )
    memory_group.add_argument(
        "--memory-stats",
        action="store_true",
        help="Display Hive Mind memory statistics and exit",
    )
    
    # HiveTerminal-specific mode selection
    mode_group = parser.add_argument_group("mode selection")
    mode_group.add_argument(
        "--mode",
        choices=["conversational", "spec", "vibe"],
        metavar="MODE",
        help="Operation mode: 'conversational' for tool-by-tool execution, "
        "'spec' for plan-approve-execute workflow (default: interactive selection)",
    )
    
    return parser.parse_args()


def check_and_resolve_trusted_folder() -> None:
    """Check if current directory is trusted and prompt if needed."""
    try:
        cwd = Path.cwd()
    except FileNotFoundError:
        rprint(
            "[red]Error: Current working directory no longer exists.[/]\n"
            "[yellow]The directory you started hive from has been deleted. "
            "Please change to an existing directory and try again, "
            "or use --workdir to specify a working directory.[/]"
        )
        sys.exit(1)

    if not has_trustable_content(cwd) or cwd.resolve() == Path.home().resolve():
        return

    is_folder_trusted = trusted_folders_manager.is_trusted(cwd)

    if is_folder_trusted is not None:
        return

    try:
        is_folder_trusted = ask_trust_folder(cwd)
    except (KeyboardInterrupt, EOFError, TrustDialogQuitException):
        sys.exit(0)
    except Exception as e:
        rprint(f"[yellow]Error showing trust dialog: {e}[/]")
        return

    if is_folder_trusted is True:
        trusted_folders_manager.add_trusted(cwd)
    elif is_folder_trusted is False:
        trusted_folders_manager.add_untrusted(cwd)


def rebuild_memory_database() -> None:
    """Rebuild the Hive Mind vector database from scratch."""
    from hiveterminal.core.config import HiveTerminalConfig
    from hiveterminal.memory.manager import MemoryManager
    
    console = Console()
    
    try:
        console.print("\n[bold cyan]Rebuilding Hive Mind Memory Database[/bold cyan]\n")
        
        # Load configuration
        config = HiveTerminalConfig.load()
        memory_config = config.memory
        
        # Initialize memory manager
        console.print(f"Database path: {memory_config.database_path}")
        manager = MemoryManager(memory_config)
        manager.initialize_database()
        
        # Rebuild database
        console.print("\n[yellow]This will delete all existing chunks and re-ingest the codebase.[/yellow]")
        console.print("[yellow]This may take several minutes for large codebases.[/yellow]\n")
        
        with console.status("[bold green]Rebuilding database..."):
            results = manager.rebuild_database()
        
        # Display results
        console.print("\n[bold green]✓ Database rebuild complete![/bold green]\n")
        
        table = Table(title="Rebuild Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Files Ingested", str(results["files_ingested"]))
        table.add_row("Total Chunks", str(results["total_chunks"]))
        table.add_row("Database Size", f"{results['database_size_mb']:.2f} MB")
        
        if results["languages"]:
            lang_str = ", ".join(f"{lang}: {count}" for lang, count in results["languages"].items())
            table.add_row("Languages", lang_str)
        
        console.print(table)
        console.print()
        
        manager.close()
        
    except Exception as e:
        console.print(f"\n[bold red]Error rebuilding database:[/bold red] {e}\n")
        sys.exit(1)


def display_memory_stats() -> None:
    """Display Hive Mind memory statistics."""
    from hiveterminal.core.config import HiveTerminalConfig
    from hiveterminal.memory.manager import MemoryManager
    
    console = Console()
    
    try:
        console.print("\n[bold cyan]Hive Mind Memory Statistics[/bold cyan]\n")
        
        # Load configuration
        config = HiveTerminalConfig.load()
        memory_config = config.memory
        
        # Initialize memory manager
        manager = MemoryManager(memory_config)
        manager.initialize_database()
        
        # Get statistics
        stats = manager.get_database_stats()
        
        # Display general stats
        table = Table(title="Database Overview")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Database Path", str(memory_config.database_path))
        table.add_row("Total Chunks", str(stats.total_chunks))
        table.add_row("Total Files", str(stats.total_files))
        table.add_row("Database Size", f"{stats.database_size_mb():.2f} MB")
        table.add_row("Avg Chunks/File", f"{stats.average_chunks_per_file():.1f}")
        
        if stats.last_updated:
            table.add_row("Last Updated", stats.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
        if stats.oldest_chunk:
            table.add_row("Oldest Chunk", stats.oldest_chunk.strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(table)
        
        # Display language breakdown
        if stats.languages:
            console.print()
            lang_table = Table(title="Language Breakdown")
            lang_table.add_column("Language", style="cyan")
            lang_table.add_column("Chunks", style="green")
            lang_table.add_column("Percentage", style="yellow")
            
            sorted_langs = sorted(stats.languages.items(), key=lambda x: x[1], reverse=True)
            for lang, count in sorted_langs:
                percentage = (count / stats.total_chunks * 100) if stats.total_chunks > 0 else 0
                lang_table.add_row(lang, str(count), f"{percentage:.1f}%")
            
            console.print(lang_table)
        
        console.print()
        manager.close()
        
    except Exception as e:
        console.print(f"\n[bold red]Error retrieving statistics:[/bold red] {e}\n")
        sys.exit(1)


def main() -> None:
    """Main entry point for the hive command."""
    args = parse_arguments()

    if args.workdir:
        workdir = args.workdir.expanduser().resolve()
        if not workdir.is_dir():
            rprint(
                f"[red]Error: --workdir does not exist or is not a directory: {workdir}[/]"
            )
            sys.exit(1)
        os.chdir(workdir)

    # Handle memory management commands
    if args.rebuild_memory:
        rebuild_memory_database()
        return
    
    if args.memory_stats:
        display_memory_stats()
        return

    is_interactive = args.prompt is None
    if is_interactive:
        check_and_resolve_trusted_folder()
    unlock_config_paths()

    # Initialize memory manager
    memory_manager = None
    try:
        from hiveterminal.core.config import HiveTerminalConfig
        from hiveterminal.memory.manager import MemoryManager
        
        config = HiveTerminalConfig.load()
        memory_config = config.memory
        
        memory_manager = MemoryManager(memory_config)
        memory_manager.initialize_database()
    except Exception as e:
        rprint(f"[yellow]Warning: Could not initialize memory system: {e}[/]")
        rprint("[yellow]Continuing without memory integration...[/]")
    
    # Determine mode
    # Priority: CLI flag > Environment variable > Config file > Interactive prompt
    mode = args.mode or os.getenv("HIVE_MODE")
    
    # Normalize mode names (vibe -> conversational)
    if mode == "vibe":
        mode = "conversational"
    
    # If no mode specified and interactive, will show selection in run_hive_cli
    if is_interactive and mode is None:
        mode = None  # Will trigger interactive selection
    elif mode is None:
        # Non-interactive mode defaults to conversational
        mode = "conversational"
    
    # Run HiveTerminal CLI with mode and memory manager
    from hiveterminal.cli.cli import run_hive_cli
    
    run_hive_cli(args, mode=mode, memory_manager=memory_manager)


if __name__ == "__main__":
    main()
