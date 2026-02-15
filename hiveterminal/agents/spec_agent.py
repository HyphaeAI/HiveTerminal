"""Spec-first mode agent with three-phase workflow.

This module implements the SpecAgentLoop, which provides a structured
Plan → Approve → Execute workflow for complex, multi-step tasks.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass

from hiveterminal.memory.manager import MemoryManager
from hiveterminal.memory.models import CodeChunk

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions that can be executed in a plan."""
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    EXECUTE_COMMAND = "execute_command"
    CREATE_DIRECTORY = "create_directory"
    READ_FILE = "read_file"


@dataclass
class Action:
    """Represents a single action in an execution plan.
    
    Attributes:
        action_type: Type of action to perform
        target: File path or command to execute
        details: Additional details specific to the action type
        order: Execution order (1-indexed)
        description: Human-readable description of the action
    """
    action_type: ActionType
    target: str
    details: Dict[str, Any]
    order: int
    description: str = ""
    
    def __str__(self) -> str:
        """String representation of the action."""
        return f"{self.order}. {self.action_type.value}: {self.target}"


class SpecAgentLoop:
    """Spec-first agent with three-phase workflow.
    
    This class implements a structured workflow:
    1. Phase 1: Generate a detailed execution plan
    2. Phase 2: Get user approval for the plan
    3. Phase 3: Execute the approved plan
    
    The agent maintains full compatibility with Vibe's tool system while
    providing transparency and control through upfront planning.
    
    Example:
        >>> from hiveterminal.memory.manager import MemoryManager
        >>> from hiveterminal.core.config import HiveTerminalConfig
        >>> 
        >>> config = HiveTerminalConfig.load()
        >>> memory_manager = MemoryManager(config.memory)
        >>> memory_manager.initialize_database()
        >>> 
        >>> agent = SpecAgentLoop(memory_manager=memory_manager)
        >>> plan = agent.generate_plan("Refactor the login function")
        >>> if agent.get_approval(plan):
        ...     agent.execute_plan(plan)
    """
    
    # Plan generation prompt template
    PLAN_GENERATION_PROMPT = """You are HiveTerminal, a spec-first agentic IDE assistant.

Your task is to analyze the user's request and generate a detailed execution plan.

CRITICAL RULES:
1. Always generate a plan in markdown format
2. Be specific about file paths and operations
3. Include risk assessment
4. Provide rollback instructions
5. Use the exact format specified below

PLAN FORMAT:
# Execution Plan

## Summary
[High-level description of what will be done]

## Risk Assessment
- Complexity: [Low/Medium/High]
- Risk Level: [Low/Medium/High]
- Estimated Time: [X minutes]

## Actions

### 1. [Action Type]: [Description]
**File**: `path/to/file.py`
**Operation**: [Create/Modify/Delete/Read]
**Details**:
- [Specific change 1]
- [Specific change 2]

### 2. [Action Type]: [Description]
**Command**: `command to execute`
**Purpose**: [Why this command is needed]

## Files Affected
- `file1.py` (Create)
- `file2.py` (Modify)
- `file3.py` (Delete)

## Rollback Plan
[How to undo these changes if needed]

Context from codebase:
{context}

User request:
{user_input}

Generate a detailed execution plan following the specified format.
"""
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        enable_memory: bool = True,
        **kwargs
    ):
        """Initialize the SpecAgentLoop.
        
        Args:
            memory_manager: MemoryManager instance for code context retrieval
            enable_memory: Whether to enable memory integration (default: True)
            **kwargs: Additional arguments for future extensions
        """
        self.memory_manager = memory_manager
        self.enable_memory = enable_memory and memory_manager is not None
        self._modified_files: set[str] = set()
        self._current_plan: Optional[str] = None
        self._current_actions: List[Action] = []
        
        logger.info(
            f"SpecAgentLoop initialized with memory "
            f"{'enabled' if self.enable_memory else 'disabled'}"
        )
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[CodeChunk]:
        """Retrieve relevant code context for a query.
        
        Args:
            query: User query or message
            top_k: Maximum number of chunks to retrieve
            
        Returns:
            List of relevant CodeChunk objects
        """
        if not self.enable_memory or not self.memory_manager:
            return []
        
        try:
            chunks = self.memory_manager.retrieve_context(query, top_k=top_k)
            logger.info(f"Retrieved {len(chunks)} relevant chunks for query")
            return chunks
        except Exception as e:
            logger.warning(f"Failed to retrieve context: {e}")
            return []
    
    def generate_plan(self, user_input: str) -> str:
        """Generate an execution plan for the user's request.
        
        Phase 1 of the three-phase workflow.
        
        Args:
            user_input: User's request or task description
            
        Returns:
            Markdown-formatted execution plan
        """
        logger.info(f"Generating plan for: {user_input[:100]}...")
        
        # Retrieve relevant context
        chunks = self.retrieve_context(user_input)
        
        # Format context
        context = ""
        if chunks and self.memory_manager:
            context = self.memory_manager.format_context_for_prompt(chunks)
        
        # Generate plan prompt
        prompt = self.PLAN_GENERATION_PROMPT.format(
            context=context if context else "[No relevant context found]",
            user_input=user_input
        )
        
        # In a real implementation, this would call the LLM
        # For now, return a template plan
        plan = self._generate_template_plan(user_input, chunks)
        
        self._current_plan = plan
        logger.info("Plan generated successfully")
        
        return plan
    
    def _generate_template_plan(self, user_input: str, chunks: List[CodeChunk]) -> str:
        """Generate a template plan (placeholder for LLM integration).
        
        Args:
            user_input: User's request
            chunks: Retrieved code chunks
            
        Returns:
            Template plan in markdown format
        """
        return f"""# Execution Plan

## Summary
Process the user request: "{user_input}"

## Risk Assessment
- Complexity: Medium
- Risk Level: Low
- Estimated Time: 5 minutes

## Actions

### 1. Read File: Analyze relevant code
**Operation**: Read
**Details**:
- Read files to understand current implementation
- Identify areas that need modification

### 2. Modify File: Implement changes
**Operation**: Modify
**Details**:
- Apply requested changes
- Ensure code quality and consistency

### 3. Execute Command: Run tests
**Command**: `pytest tests/`
**Purpose**: Verify changes don't break existing functionality

## Files Affected
{self._format_affected_files(chunks)}

## Rollback Plan
- Restore from .hive_backups/ if needed
- Revert changes using git if version controlled
"""
    
    def _format_affected_files(self, chunks: List[CodeChunk]) -> str:
        """Format affected files list from chunks.
        
        Args:
            chunks: Code chunks that may be affected
            
        Returns:
            Formatted list of files
        """
        if not chunks:
            return "- [To be determined based on analysis]"
        
        files = set(chunk.file_path for chunk in chunks)
        return "\n".join(f"- `{file}` (Modify)" for file in sorted(files))
    
    def get_approval(self, plan: str) -> bool:
        """Get user approval for the plan.
        
        Phase 2 of the three-phase workflow.
        
        Args:
            plan: The execution plan to approve
            
        Returns:
            True if approved, False otherwise
        """
        from rich.console import Console
        from rich.markdown import Markdown
        from rich.prompt import Prompt
        
        console = Console()
        
        # Display the plan
        console.print("\n[bold cyan]Execution Plan Generated[/bold cyan]\n")
        console.print(Markdown(plan))
        console.print()
        
        # Get approval
        response = Prompt.ask(
            "[bold yellow]Do you want to proceed with this plan?[/bold yellow]",
            choices=["y", "n", "yes", "no"],
            default="n"
        )
        
        approved = response in ["y", "yes"]
        
        if approved:
            logger.info("Plan approved by user")
            console.print("\n[green]✓ Plan approved. Starting execution...[/green]\n")
        else:
            logger.info("Plan rejected by user")
            console.print("\n[yellow]✗ Plan rejected. No changes will be made.[/yellow]\n")
        
        return approved
    
    def parse_plan(self, plan: str) -> List[Action]:
        """Parse a markdown plan into executable actions.
        
        Uses the plan_parser module for robust parsing.
        
        Args:
            plan: Markdown-formatted execution plan
            
        Returns:
            List of Action objects
        """
        from hiveterminal.agents.plan_parser import parse_plan, handle_malformed_plan
        
        logger.info("Parsing plan into actions")
        
        try:
            actions = parse_plan(plan)
        except ValueError as e:
            logger.warning(f"Standard parsing failed: {e}, attempting recovery")
            actions = handle_malformed_plan(plan)
        
        self._current_actions = actions
        logger.info(f"Parsed {len(actions)} actions from plan")
        
        return actions
    
    def execute_plan(self, plan: str) -> Dict[str, Any]:
        """Execute the approved plan.
        
        Phase 3 of the three-phase workflow.
        
        Args:
            plan: The approved execution plan
            
        Returns:
            Execution results dictionary with detailed information
        """
        from rich.console import Console
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        console = Console()
        logger.info("Starting plan execution")
        
        # Parse plan into actions
        actions = self.parse_plan(plan)
        
        results = {
            "total_actions": len(actions),
            "completed": 0,
            "failed": 0,
            "errors": [],
            "action_results": []
        }
        
        # Execute each action with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for action in actions:
                task = progress.add_task(
                    f"[cyan]{action.description}[/cyan]",
                    total=1
                )
                
                try:
                    action_result = self._execute_action(action)
                    results["completed"] += 1
                    results["action_results"].append({
                        "action": action.description,
                        "status": "success",
                        "result": action_result
                    })
                    
                    progress.update(task, completed=1)
                    console.print(f"[green]✓[/green] {action.description}")
                    
                except Exception as e:
                    results["failed"] += 1
                    error_msg = str(e)
                    results["errors"].append({
                        "action": action.description,
                        "error": error_msg
                    })
                    results["action_results"].append({
                        "action": action.description,
                        "status": "failed",
                        "error": error_msg
                    })
                    
                    logger.error(f"Action failed: {action.description}: {e}")
                    progress.update(task, completed=1)
                    console.print(f"[red]✗[/red] {action.description}: {error_msg}")
                    
                    # Stop on first error
                    console.print("\n[yellow]Stopping execution due to error.[/yellow]")
                    break
        
        # Ingest modified files
        if self._modified_files:
            console.print("\n[cyan]Updating memory with modified files...[/cyan]")
            ingested = self.ingest_modified_files()
            console.print(f"[green]✓[/green] Ingested {ingested} files into memory")
        
        # Display summary
        console.print("\n[bold cyan]Execution Summary[/bold cyan]")
        console.print(f"Total actions: {results['total_actions']}")
        console.print(f"[green]Completed: {results['completed']}[/green]")
        console.print(f"[red]Failed: {results['failed']}[/red]")
        
        if results['errors']:
            console.print("\n[bold red]Errors:[/bold red]")
            for error in results['errors']:
                console.print(f"  • {error['action']}: {error['error']}")
        
        console.print()
        
        logger.info(f"Plan execution complete: {results}")
        return results
    
    def _execute_action(self, action: Action) -> Dict[str, Any]:
        """Execute a single action.
        
        Routes the action to the appropriate execution handler based on type.
        
        Args:
            action: Action to execute
            
        Returns:
            Dictionary with execution results
            
        Raises:
            RuntimeError: If action execution fails
        """
        logger.info(f"Executing action {action.order}: {action.description}")
        
        try:
            if action.action_type == ActionType.READ_FILE:
                return self._execute_read_file(action)
            elif action.action_type == ActionType.CREATE_FILE:
                return self._execute_create_file(action)
            elif action.action_type == ActionType.MODIFY_FILE:
                return self._execute_modify_file(action)
            elif action.action_type == ActionType.DELETE_FILE:
                return self._execute_delete_file(action)
            elif action.action_type == ActionType.CREATE_DIRECTORY:
                return self._execute_create_directory(action)
            elif action.action_type == ActionType.EXECUTE_COMMAND:
                return self._execute_command(action)
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")
        
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            raise RuntimeError(f"Failed to execute {action.description}: {e}")
    
    def _execute_read_file(self, action: Action) -> Dict[str, Any]:
        """Execute a read file action.
        
        Args:
            action: Read file action
            
        Returns:
            Dictionary with file content
        """
        from pathlib import Path
        
        file_path = Path(action.target)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path.read_text()
        
        logger.info(f"Read file: {file_path} ({len(content)} chars)")
        
        return {
            'action': 'read_file',
            'file': str(file_path),
            'size': len(content),
            'success': True
        }
    
    def _execute_create_file(self, action: Action) -> Dict[str, Any]:
        """Execute a create file action.
        
        Args:
            action: Create file action
            
        Returns:
            Dictionary with creation results
        """
        from pathlib import Path
        
        file_path = Path(action.target)
        
        if file_path.exists():
            raise FileExistsError(f"File already exists: {file_path}")
        
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get content from details if provided
        content = action.details.get('content', '')
        
        file_path.write_text(content)
        self._modified_files.add(str(file_path))
        
        logger.info(f"Created file: {file_path}")
        
        return {
            'action': 'create_file',
            'file': str(file_path),
            'success': True
        }
    
    def _execute_modify_file(self, action: Action) -> Dict[str, Any]:
        """Execute a modify file action.
        
        Args:
            action: Modify file action
            
        Returns:
            Dictionary with modification results
        """
        from pathlib import Path
        import shutil
        from datetime import datetime
        
        file_path = Path(action.target)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create backup
        backup_dir = Path('.hive_backups')
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"{file_path.name}.{timestamp}.backup"
        shutil.copy2(file_path, backup_path)
        
        # Get new content from details if provided
        if 'content' in action.details:
            file_path.write_text(action.details['content'])
        
        self._modified_files.add(str(file_path))
        
        logger.info(f"Modified file: {file_path} (backup: {backup_path})")
        
        return {
            'action': 'modify_file',
            'file': str(file_path),
            'backup': str(backup_path),
            'success': True
        }
    
    def _execute_delete_file(self, action: Action) -> Dict[str, Any]:
        """Execute a delete file action.
        
        Args:
            action: Delete file action
            
        Returns:
            Dictionary with deletion results
        """
        from pathlib import Path
        import shutil
        from datetime import datetime
        
        file_path = Path(action.target)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create backup before deletion
        backup_dir = Path('.hive_backups')
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f"{file_path.name}.{timestamp}.backup"
        shutil.copy2(file_path, backup_path)
        
        # Delete the file
        file_path.unlink()
        
        logger.info(f"Deleted file: {file_path} (backup: {backup_path})")
        
        return {
            'action': 'delete_file',
            'file': str(file_path),
            'backup': str(backup_path),
            'success': True
        }
    
    def _execute_create_directory(self, action: Action) -> Dict[str, Any]:
        """Execute a create directory action.
        
        Args:
            action: Create directory action
            
        Returns:
            Dictionary with creation results
        """
        from pathlib import Path
        
        dir_path = Path(action.target)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created directory: {dir_path}")
        
        return {
            'action': 'create_directory',
            'directory': str(dir_path),
            'success': True
        }
    
    def _execute_command(self, action: Action) -> Dict[str, Any]:
        """Execute a shell command action.
        
        Args:
            action: Execute command action
            
        Returns:
            Dictionary with command results
        """
        import subprocess
        
        command = action.target
        timeout = action.details.get('timeout', 300)  # 5 minute default
        
        logger.info(f"Executing command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            
            if not success:
                logger.warning(f"Command failed with exit code {result.returncode}")
            
            return {
                'action': 'execute_command',
                'command': command,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': success
            }
        
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise RuntimeError(f"Command execution failed: {e}")
    
    def ingest_modified_files(self) -> int:
        """Ingest all tracked modified files into memory.
        
        Returns:
            Number of files successfully ingested
        """
        if not self.enable_memory or not self.memory_manager:
            return 0
        
        if not self._modified_files:
            return 0
        
        logger.info(f"Ingesting {len(self._modified_files)} modified files")
        
        ingested = 0
        for file_path in self._modified_files:
            try:
                from pathlib import Path
                path = Path(file_path)
                if path.exists() and path.is_file():
                    self.memory_manager.ingest_file(str(path), incremental=True)
                    ingested += 1
            except Exception as e:
                logger.warning(f"Failed to ingest {file_path}: {e}")
        
        # Clear tracked files
        self._modified_files.clear()
        
        logger.info(f"Successfully ingested {ingested} files")
        return ingested
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """Process a user request through the three-phase workflow.
        
        This is the main entry point for spec-first mode.
        
        Args:
            user_input: User's request or task description
            
        Returns:
            Results dictionary with execution details
        """
        # Phase 1: Generate Plan
        plan = self.generate_plan(user_input)
        
        # Phase 2: Get Approval
        approved = self.get_approval(plan)
        
        if not approved:
            return {
                "approved": False,
                "plan": plan,
                "executed": False
            }
        
        # Phase 3: Execute Plan
        results = self.execute_plan(plan)
        
        return {
            "approved": True,
            "plan": plan,
            "executed": True,
            "results": results
        }
    
    def cleanup(self) -> None:
        """Clean up resources and ingest any remaining modified files."""
        if self._modified_files:
            self.ingest_modified_files()
        
        logger.info("SpecAgentLoop cleanup complete")


# Convenience function for creating spec agent with memory
def create_spec_agent(
    memory_manager: Optional[MemoryManager] = None,
    **kwargs
) -> SpecAgentLoop:
    """Create a SpecAgentLoop with memory integration.
    
    Args:
        memory_manager: MemoryManager instance
        **kwargs: Additional arguments for the agent
        
    Returns:
        Configured SpecAgentLoop instance
    """
    return SpecAgentLoop(memory_manager=memory_manager, **kwargs)
