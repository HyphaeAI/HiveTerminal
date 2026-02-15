# Design Document: HiveTerminal

## 1. System Architecture

### 1.1 High-Level Architecture

HiveTerminal is built on top of Mistral Vibe, extending it with dual-mode operation and a shared memory system:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer (main.py)                      │
│              Typer-based Entry Point (from Vibe)             │
│                  --mode [vibe|spec] flag                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              TUI Layer (Vibe's Textual UI)                   │
│          Rendering, Formatting, User Interaction             │
│                  (NO VISUAL CHANGES)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                ┌──────┴──────┐
                │             │
┌───────────────▼──┐    ┌─────▼────────────────┐
│   Vibe Mode      │    │   Spec Mode          │
│ (Conversational) │    │ (Three-Phase Loop)   │
│                  │    │                      │
│ - Tool-by-tool   │    │ - Plan Generation    │
│ - Iterative      │    │ - Single Approval    │
│ - Flexible       │    │ - Batch Execution    │
└────────┬─────────┘    └──────┬───────────────┘
         │                     │
         └──────────┬──────────┘
                    │
┌───────────────────▼──────────────────────────────────────────┐
│              Shared Components (from Vibe)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Tool Manager │  │ Config Mgr   │  │ LLM Backend  │      │
│  │ (Vibe's)     │  │ (TOML-based) │  │ (LiteLLM)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────────────┐
│              NEW: Memory Manager (memory.py)                  │
│                                                               │
│  - ChromaDB Vector Storage                                   │
│  - Code Ingestion & Chunking                                 │
│  - Semantic Retrieval                                        │
│  - Git-Shareable Hive Mind                                   │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 Dual-Mode Operation

HiveTerminal operates in two modes, selectable via CLI flag:

**Vibe Mode (Default):**
- Uses Vibe's original conversational loop
- Tool-by-tool execution with individual approvals
- Iterative, flexible workflow
- Best for exploration and quick tasks

**Spec Mode:**
- Three-phase loop: Plan → Approve → Execute
- Single approval for entire plan
- Structured, transparent workflow
- Best for complex, multi-step tasks

### 1.3 Component Responsibilities

#### 1.3.1 CLI Layer (`main.py` - Extended from Vibe)
- Entry point with `--mode [vibe|spec]` flag
- Inherits Vibe's argument parsing (Typer)
- Mode selection and initialization
- Session management (from Vibe)

#### 1.3.2 TUI Layer (Vibe's Textual UI - NO CHANGES)
- Reuse Vibe's complete UI system
- Rich-based rendering
- Syntax highlighting
- Progress indicators
- Interactive prompts
- **CRITICAL: Keep all visual elements unchanged**

#### 1.3.3 Vibe Mode (Vibe's AgentLoop - Minimal Changes)
- Use Vibe's original conversational loop
- Tool-by-tool execution
- Individual tool approvals
- Streaming support
- Middleware pipeline
- **Add: Memory context injection before LLM calls**

#### 1.3.4 Spec Mode (New: SpecAgentLoop extends AgentLoop)
- Inherits from Vibe's AgentLoop
- Implements three-phase workflow
- Plan generation with memory context
- Single approval step
- Batch execution
- Plan parsing and action extraction

#### 1.3.5 Config Manager (Vibe's config.py - Light Modifications)
- Keep TOML-based configuration
- Add memory configuration section
- Add mode selection defaults
- Maintain Vibe's provider/model system
- **Replace Mistral backend with LiteLLM**

#### 1.3.6 Memory Manager (NEW: memory.py)
- ChromaDB vector database management
- Code ingestion and chunking
- Embedding generation
- Semantic search
- Git-shareable storage
- **Integrates with both Vibe and Spec modes**

## 2. Data Flow

### 2.1 Vibe Mode Flow (Conversational)

```
User Input → Memory.retrieve_context()
                ↓
         Inject context into messages
                ↓
         Vibe's AgentLoop._conversation_loop()
                ↓
         LLM generates response with tool calls
                ↓
         Display tool call → User approves (per tool)
                ↓
         Execute tool → Add result to conversation
                ↓
         Repeat until no more tool calls
                ↓
         Memory.ingest_changes()
```

### 2.2 Spec Mode Flow (Three-Phase)

```
User Input → Memory.retrieve_context()
                ↓
         SpecAgentLoop.phase1_generate_plan()
                ↓
         LLM generates markdown plan
                ↓
         TUI.display_plan() [Phase 1 Complete]
                ↓
         TUI.prompt_approval() [Phase 2]
                ↓
         User approves (y/n)
                ↓
    ┌────────────┴────────────┐
    │ No                      │ Yes
    ↓                         ↓
  Abort              SpecAgentLoop.phase3_execute()
                              ↓
                     Parse plan into actions
                              ↓
                     Execute actions sequentially
                              ↓
                     Memory.ingest_changes()
                              ↓
                     Display summary [Phase 3 Complete]
```

### 2.3 Memory Ingestion Flow (Shared by Both Modes)

```
File Modified → Memory.detect_change()
                      ↓
              Memory.chunk_file()
                      ↓
              Memory.generate_embeddings()
                      ↓
              Memory.store_in_chromadb()
```

### 2.4 Context Retrieval Flow (Shared by Both Modes)

```
User Request → Memory.query(request_text)
                      ↓
              ChromaDB.similarity_search()
                      ↓
              Memory.format_results()
                      ↓
              Inject into system prompt/messages
                      ↓
              Agent (receives enhanced context)
```

## 3. Detailed Component Design

### 3.1 Config Manager (Extended from Vibe's config.py)

#### 3.1.1 Configuration Schema

```toml
# .hive_config.toml (extends Vibe's config.toml)

# Mode selection
default_mode = "vibe"  # or "spec"

# AI Configuration (uses Vibe's structure)
active_model = "gpt-4"
auto_approve = false

# Providers (extended to support LiteLLM)
[[providers]]
name = "openai"
api_base = "https://api.openai.com/v1"
api_key_env_var = "OPENAI_API_KEY"
backend = "generic"

[[providers]]
name = "anthropic"
api_base = "https://api.anthropic.com/v1"
api_key_env_var = "ANTHROPIC_API_KEY"
backend = "generic"

[[providers]]
name = "ollama"
api_base = "http://localhost:11434/v1"
api_key_env_var = ""
backend = "generic"

# Models (extended for multi-provider)
[[models]]
name = "gpt-4"
provider = "openai"
alias = "gpt-4"
temperature = 0.7
input_price = 30.0
output_price = 60.0

[[models]]
name = "claude-3-5-sonnet-20241022"
provider = "anthropic"
alias = "claude-sonnet"
temperature = 0.7
input_price = 3.0
output_price = 15.0

# NEW: Memory Configuration
[memory]
database_path = "./.hive_memory"
embedding_model = "text-embedding-ada-002"
chunk_size = 1000
chunk_overlap = 200
top_k_results = 5
similarity_threshold = 0.7

# NEW: Spec Mode Configuration
[spec_mode]
create_backups = true
backup_dir = "./.hive_backups"
max_retries = 3
timeout_seconds = 300

# Existing Vibe configurations
[project_context]
max_chars = 40000
# ... (keep all Vibe's settings)

[session_logging]
enabled = true
# ... (keep all Vibe's settings)

# Tools configuration (from Vibe)
[tools]
# ... (keep all Vibe's tool configs)
```

#### 3.1.2 Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)
- `HIVE_CONFIG_PATH`: Custom config file path
- `HIVE_MODE`: Override default mode (vibe or spec)

### 3.2 Memory Manager (`memory.py`)

#### 3.2.1 Class Structure

```python
class MemoryManager:
    """Manages vector database for code context storage and retrieval."""
    
    def __init__(self, config: ConfigManager)
    def initialize_database(self) -> None
    def ingest_file(self, file_path: str) -> None
    def ingest_directory(self, dir_path: str, recursive: bool = True) -> None
    def chunk_code(self, content: str, file_path: str) -> List[CodeChunk]
    def generate_embeddings(self, chunks: List[CodeChunk]) -> List[np.ndarray]
    def store_chunks(self, chunks: List[CodeChunk], embeddings: List[np.ndarray]) -> None
    def retrieve_context(self, query: str, top_k: int = 5) -> List[CodeChunk]
    def rebuild_database(self) -> None
    def get_database_stats(self) -> Dict[str, Any]
```

#### 3.2.2 CodeChunk Data Structure

```python
@dataclass
class CodeChunk:
    """Represents a semantic chunk of code."""
    content: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    timestamp: datetime
    chunk_id: str
```

#### 3.2.3 Chunking Strategy

- **Function-level chunking**: Split code by function/method boundaries
- **Class-level chunking**: Keep entire classes together when possible
- **Sliding window**: For files without clear structure, use overlapping windows
- **Size limits**: Max 1000 tokens per chunk (configurable)
- **Overlap**: 200 tokens overlap between chunks (configurable)

#### 3.2.4 ChromaDB Schema

```python
# Collection: "hive_code_memory"
# Metadata fields:
{
    "file_path": str,
    "start_line": int,
    "end_line": int,
    "language": str,
    "timestamp": str (ISO format),
    "chunk_id": str (UUID)
}
```

### 3.3 Agent Architecture

#### 3.3.1 Vibe Mode (Minimal Changes to Vibe's AgentLoop)

```python
class VibeAgentLoop(AgentLoop):  # Inherits from Vibe's AgentLoop
    """Extended Vibe agent with memory integration."""
    
    def __init__(self, config, memory_manager, **kwargs):
        super().__init__(config, **kwargs)
        self.memory_manager = memory_manager
    
    async def _conversation_loop(self, user_msg: str):
        """Override to inject memory context."""
        # Retrieve relevant context from memory
        context = await self.memory_manager.retrieve_context(user_msg)
        
        # Inject context into user message
        enhanced_msg = self._enhance_with_context(user_msg, context)
        
        # Call parent's conversation loop
        async for event in super()._conversation_loop(enhanced_msg):
            yield event
        
        # Ingest any file changes after execution
        await self._ingest_modified_files()
    
    def _enhance_with_context(self, msg: str, context: List[CodeChunk]) -> str:
        """Add memory context to user message."""
        if not context:
            return msg
        
        context_str = "\n\n".join([
            f"# {chunk.file_path} (lines {chunk.start_line}-{chunk.end_line})\n{chunk.content}"
            for chunk in context
        ])
        
        return f"{msg}\n\n<relevant_context>\n{context_str}\n</relevant_context>"
```

#### 3.3.2 Spec Mode (New: Three-Phase Loop)

```python
class SpecAgentLoop(AgentLoop):  # Inherits from Vibe's AgentLoop
    """Spec-first agent with three-phase workflow."""
    
    def __init__(self, config, memory_manager, **kwargs):
        super().__init__(config, **kwargs)
        self.memory_manager = memory_manager
    
    async def process_request(self, user_input: str) -> AsyncGenerator[BaseEvent]:
        """Three-phase workflow: Plan → Approve → Execute."""
        
        # Phase 1: Generate Plan
        context = await self.memory_manager.retrieve_context(user_input)
        plan = await self.phase1_generate_plan(user_input, context)
        
        yield PlanGeneratedEvent(plan=plan)
        
        # Phase 2: Get Approval
        approved = await self.phase2_get_approval(plan)
        
        if not approved:
            yield PlanRejectedEvent()
            return
        
        yield PlanApprovedEvent()
        
        # Phase 3: Execute Plan
        async for event in self.phase3_execute_plan(plan):
            yield event
        
        # Ingest changes
        await self._ingest_modified_files()
    
    async def phase1_generate_plan(self, user_input: str, context: List[CodeChunk]) -> str:
        """Generate markdown execution plan."""
        plan_prompt = PLAN_GENERATION_PROMPT.format(
            context=self._format_context(context),
            user_input=user_input
        )
        
        # Use parent's _chat method to generate plan
        self.messages.append(LLMMessage(role=Role.user, content=plan_prompt))
        result = await self._chat()
        
        return result.message.content or ""
    
    async def phase2_get_approval(self, plan: str) -> bool:
        """Display plan and get user approval."""
        # Use Vibe's approval callback mechanism
        if not self.approval_callback:
            return False
        
        response, _ = await self.approval_callback("execute_plan", plan, "plan")
        return response == ApprovalResponse.YES
    
    async def phase3_execute_plan(self, plan: str) -> AsyncGenerator[BaseEvent]:
        """Parse and execute plan actions."""
        actions = self.parse_plan(plan)
        
        for action in actions:
            yield ActionStartEvent(action=action)
            
            try:
                result = await self.execute_action(action)
                yield ActionCompleteEvent(action=action, result=result)
            except Exception as e:
                yield ActionErrorEvent(action=action, error=str(e))
                break
    
    def parse_plan(self, plan: str) -> List[Action]:
        """Parse markdown plan into executable actions."""
        # Implementation: Parse markdown sections
        # Extract file operations, shell commands, etc.
        pass
    
    async def execute_action(self, action: Action) -> Any:
        """Execute a single action from the plan."""
        # Implementation: Route to appropriate tool
        # Use Vibe's tool manager
        pass
```

#### 3.3.2 Plan Structure

Generated plans follow this markdown format:

```markdown
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
**Operation**: [Create/Modify/Delete]
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
```

#### 3.3.3 Action Types

```python
class ActionType(Enum):
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    EXECUTE_COMMAND = "execute_command"
    CREATE_DIRECTORY = "create_directory"

@dataclass
class Action:
    """Represents a single action in an execution plan."""
    action_type: ActionType
    target: str  # File path or command
    details: Dict[str, Any]
    order: int
```

#### 3.3.4 LiteLLM Integration

```python
# System prompt for plan generation
PLAN_GENERATION_PROMPT = """
You are HiveTerminal, a spec-first agentic IDE assistant.

Your task is to analyze the user's request and generate a detailed execution plan.

CRITICAL RULES:
1. Always generate a plan in markdown format
2. Be specific about file paths and operations
3. Include risk assessment
4. Provide rollback instructions
5. Use the exact format specified

Context from codebase:
{context}

User request:
{user_input}

Generate a detailed execution plan following the specified format.
"""
```

### 3.4 CLI Entry Point (Extended from Vibe's entrypoint.py)

#### 3.4.1 Command Structure

```python
# Extended from vibe/cli/entrypoint.py

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run HiveTerminal CLI")
    
    # NEW: Mode selection
    parser.add_argument(
        "--mode",
        choices=["vibe", "spec"],
        default=None,  # Uses config default
        help="Operation mode: 'vibe' for conversational, 'spec' for three-phase"
    )
    
    # Existing Vibe arguments
    parser.add_argument("initial_prompt", nargs="?", ...)
    parser.add_argument("-p", "--prompt", ...)
    parser.add_argument("--agent", ...)
    parser.add_argument("--workdir", ...)
    # ... all other Vibe arguments
    
    # NEW: Memory management
    parser.add_argument(
        "--rebuild-memory",
        action="store_true",
        help="Rebuild the vector database from scratch"
    )
    
    parser.add_argument(
        "--memory-stats",
        action="store_true",
        help="Display Hive Mind memory statistics"
    )
    
    return parser.parse_args()

def main() -> None:
    args = parse_arguments()
    
    # Handle memory commands
    if args.rebuild_memory:
        rebuild_memory_database()
        return
    
    if args.memory_stats:
        display_memory_stats()
        return
    
    # Existing Vibe initialization
    if args.workdir:
        os.chdir(args.workdir)
    
    is_interactive = args.prompt is None
    if is_interactive:
        check_and_resolve_trusted_folder()
    unlock_config_paths()
    
    # NEW: Initialize memory manager
    from hiveterminal.memory import MemoryManager
    memory_manager = MemoryManager(config)
    
    # NEW: Mode selection
    # Priority: CLI flag > Environment variable > Config file > Interactive prompt
    mode = args.mode or os.getenv("HIVE_MODE") or config.default_mode
    
    # If interactive and no mode specified, show selection prompt
    if is_interactive and mode is None:
        mode = None  # Will trigger interactive selection in run_cli
    
    # Run CLI with selected mode
    from hiveterminal.cli import run_cli
    run_cli(args, mode=mode, memory_manager=memory_manager)
```

#### 3.4.2 Interactive Mode Selection

When starting HiveTerminal without a mode flag, users are presented with an interactive choice:

```python
def show_mode_selection() -> str:
    """Display interactive mode selection with examples."""
    
    console = Console()
    
    console.print("\n[bold cyan]Welcome to HiveTerminal![/bold cyan]\n")
    console.print("Choose your workflow mode:\n")
    
    # Option 1: Conversational Loop (Vibe Mode)
    console.print("[bold green]1. Conversational Mode[/bold green] (Flexible, Interactive)")
    console.print("   [dim]→ Agent executes tools one-by-one with your approval[/dim]")
    console.print("\n   [yellow]Example:[/yellow]")
    console.print("   [dim]You: 'Refactor the login function'[/dim]")
    console.print("   [dim]Agent: 'I'll read the file first' → [Tool: read_file] → You approve[/dim]")
    console.print("   [dim]Agent: 'Now I'll make changes' → [Tool: write_file] → You approve[/dim]")
    console.print("   [dim]Agent: 'Let me run tests' → [Tool: bash] → You approve[/dim]")
    console.print("   [dim]✓ Best for: Exploration, quick tasks, iterative development[/dim]\n")
    
    # Option 2: Three-Phase Loop (Spec Mode)
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


def interactive_session(mode: str | None, memory_manager: MemoryManager):
    """Main interactive loop."""
    
    # If no mode specified, show interactive selection
    if mode is None:
        mode = show_mode_selection()
    
    # Initialize appropriate agent
    if mode == "conversational":
        agent = VibeAgentLoop(config, memory_manager)
        console.print("[dim]Using Conversational Mode - approve tools one-by-one[/dim]\n")
    else:  # spec mode
        agent = SpecAgentLoop(config, memory_manager)
        console.print("[dim]Using Spec-First Mode - review complete plans before execution[/dim]\n")
    
    # Use Vibe's existing UI
    while True:
        user_input = prompt_user()  # Vibe's prompt
        
        if user_input in ["exit", "quit"]:
            break
        
        # Handle mode switching
        if user_input.startswith("/mode"):
            new_mode = show_mode_selection()
            if new_mode != mode:
                mode = new_mode
                # Reinitialize agent
                if mode == "conversational":
                    agent = VibeAgentLoop(config, memory_manager)
                else:
                    agent = SpecAgentLoop(config, memory_manager)
            continue
        
        # Process through selected agent
        async for event in agent.process_request(user_input):
            display_event(event)  # Vibe's display logic
```

## 4. Implementation Details

### 4.1 File Operations

#### 4.1.1 Safe File Modification

```python
def modify_file_safely(file_path: str, changes: List[Change]) -> None:
    """
    Safely modify a file with automatic backup.
    
    Steps:
    1. Create backup of original file
    2. Read current content
    3. Apply changes
    4. Write to temporary file
    5. Validate syntax (if applicable)
    6. Atomic rename to original path
    7. Trigger memory ingestion
    """
```

#### 4.1.2 Backup Strategy

- Backups stored in `./.hive_backups/`
- Filename format: `{original_name}.{timestamp}.backup`
- Automatic cleanup of backups older than 7 days
- Option to restore from backup

### 4.2 Shell Command Execution

#### 4.2.1 Safe Execution

```python
def execute_command_safely(command: str, timeout: int = 300) -> CommandResult:
    """
    Execute shell command with safety measures.
    
    Safety features:
    1. Timeout enforcement
    2. Capture stdout and stderr
    3. Return exit code
    4. Prevent dangerous commands (rm -rf /, etc.)
    5. Run in subprocess with limited permissions
    """
```

#### 4.2.2 Dangerous Command Detection

Blacklist patterns:
- `rm -rf /`
- `:(){ :|:& };:`
- `chmod -R 777 /`
- `dd if=/dev/zero`

### 4.3 Error Handling

#### 4.3.1 Error Categories

```python
class HiveError(Exception):
    """Base exception for HiveTerminal."""

class ConfigurationError(HiveError):
    """Configuration-related errors."""

class MemoryError(HiveError):
    """Vector database errors."""

class ExecutionError(HiveError):
    """Plan execution errors."""

class APIError(HiveError):
    """AI API errors."""
```

#### 4.3.2 Error Recovery

- **API Errors**: Retry with exponential backoff (max 3 attempts)
- **File Errors**: Restore from backup if available
- **Memory Errors**: Offer to rebuild database
- **Execution Errors**: Halt execution, display error, offer rollback

### 4.4 Logging

#### 4.4.1 Log Structure

```python
# Logs stored in ./.hive_logs/
# Format: hive_{date}.log

# Log levels:
# - DEBUG: Detailed diagnostic information
# - INFO: General informational messages
# - WARNING: Warning messages
# - ERROR: Error messages
# - CRITICAL: Critical errors that prevent operation
```

#### 4.4.2 Logged Events

- User requests and responses
- Plan generation and approval
- Execution steps and results
- Memory operations (ingestion, retrieval)
- API calls and responses
- Errors and exceptions

## 5. Performance Considerations

### 5.1 Memory Optimization

- **Lazy loading**: Load ChromaDB only when needed
- **Batch processing**: Ingest multiple files in batches
- **Caching**: Cache frequently accessed embeddings
- **Incremental updates**: Only re-embed modified files

### 5.2 Embedding Optimization

- **Local embeddings**: Option to use local embedding models (sentence-transformers)
- **Batch embedding**: Generate embeddings for multiple chunks at once
- **Embedding cache**: Cache embeddings to avoid regeneration

### 5.3 Query Optimization

- **Index optimization**: Use ChromaDB's HNSW index for fast similarity search
- **Result limiting**: Limit top_k results to avoid overwhelming context
- **Filtering**: Pre-filter by file type or directory before semantic search

## 6. Security Considerations

### 6.1 API Key Management

- Never log API keys
- Read from environment variables only
- Validate keys on startup
- Clear error messages without exposing keys

### 6.2 Command Execution

- Blacklist dangerous commands
- Run in subprocess with timeout
- Limit file system access
- Validate all file paths (prevent directory traversal)

### 6.3 File Operations

- Validate file paths before operations
- Prevent operations outside project directory
- Create backups before modifications
- Atomic file operations to prevent corruption

## 7. Testing Strategy

### 7.1 Unit Tests

- Config loading and validation
- Memory chunking algorithms
- Plan parsing logic
- File operation safety

### 7.2 Integration Tests

- End-to-end three-phase loop
- Memory ingestion and retrieval
- LiteLLM API integration
- CLI command execution

### 7.3 Property-Based Tests

#### Property 1: Memory Consistency
**Validates: Requirements 4.6, 4.7**

For any file ingested into memory:
- Retrieving with the file's content as query should return that file in top results
- The number of chunks stored should match the expected chunk count based on file size
- Re-ingesting the same file should not create duplicate entries

#### Property 2: Plan Approval Safety
**Validates: Requirements 3.10**

For any user request:
- If approval is denied, no file system changes should occur
- If approval is granted, all planned actions should be attempted
- The system should never execute without explicit approval

#### Property 3: Backup Integrity
**Validates: Requirements 8.8**

For any file modification:
- A backup should exist before modification
- The backup content should match the original file content
- Restoring from backup should return the file to its original state

#### Property 4: Context Retrieval Relevance
**Validates: Requirements 5.2, 5.3**

For any query:
- Results should be ordered by relevance (similarity score)
- All results should meet the similarity threshold
- The number of results should not exceed top_k

## 8. Deployment

### 8.1 Installation

```bash
# Clone repository
git clone <repository_url>
cd hiveterminal

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up API keys
export OPENAI_API_KEY="your-key-here"
# or
export ANTHROPIC_API_KEY="your-key-here"

# Run HiveTerminal
python main.py interactive
```

### 8.2 Project Structure

```
hiveterminal/
├── main.py              # CLI entry point
├── agent.py             # Agent logic
├── config.py            # Configuration management
├── memory.py            # Memory manager
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
├── .hive_config.yaml    # Configuration file (optional)
├── .hive_memory/        # Vector database (created at runtime)
├── .hive_backups/       # File backups (created at runtime)
├── .hive_logs/          # Log files (created at runtime)
└── tests/               # Test suite
    ├── test_config.py
    ├── test_memory.py
    ├── test_agent.py
    └── test_integration.py
```

### 8.3 Dependencies

```toml
# pyproject.toml (extends Vibe's dependencies)

[project]
name = "hiveterminal"
version = "1.0.0"
description = "Dual-mode CLI coding assistant with shared memory"
requires-python = ">=3.12"

dependencies = [
    # Vibe's core dependencies (keep all)
    "agent-client-protocol==0.8.0",
    "anyio>=4.12.0",
    "httpx>=0.28.1",
    "mcp>=1.14.0",
    "pexpect>=4.9.0",
    "packaging>=24.1",
    "pydantic>=2.12.4",
    "pydantic-settings>=2.12.0",
    "pyyaml>=6.0.0",
    "python-dotenv>=1.0.0",
    "rich>=14.0.0",
    "textual>=1.0.0",
    "tomli-w>=1.2.0",
    "watchfiles>=1.1.1",
    "pyperclip>=1.11.0",
    "textual-speedups>=0.2.1",
    "tree-sitter>=0.25.2",
    "tree-sitter-bash>=0.25.1",
    "keyring>=25.6.0",
    "cryptography>=44.0.0",
    "zstandard>=0.25.0",
    "gitpython>=3.1.46",
    "giturlparse>=0.14.0",
    
    # NEW: Replace mistralai with litellm
    "litellm>=1.0.0",
    
    # NEW: Memory system dependencies
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",
    "tiktoken>=0.5.0",
]

[project.scripts]
hive = "hiveterminal.cli.entrypoint:main"
```

## 9. Future Enhancements

### 9.1 Phase 1 Enhancements (Post-MVP)

- **Multi-file editing**: Support for complex refactoring across multiple files
- **Git integration**: Automatic commit of approved changes
- **Undo/redo**: Command history with rollback capability
- **Templates**: Pre-defined plan templates for common tasks

### 9.2 Phase 2 Enhancements

- **Collaborative mode**: Real-time collaboration with team members
- **Plugin system**: Extensible architecture for custom tools
- **Web UI**: Optional web interface alongside TUI
- **Cloud sync**: Optional cloud backup of Hive Mind

### 9.3 Phase 3 Enhancements

- **Multi-agent**: Specialized agents for different tasks
- **Learning**: Agent learns from user feedback and corrections
- **IDE integration**: VSCode/JetBrains plugins
- **Advanced memory**: Graph-based memory for relationship tracking

## 10. Success Metrics

### 10.1 Performance Metrics

- Plan generation time: < 5 seconds
- Context retrieval time: < 1 second
- File ingestion rate: > 100 files/minute
- Memory database size: < 100MB for 10,000 files

### 10.2 Quality Metrics

- Plan approval rate: > 80%
- Execution success rate: > 95%
- Context relevance score: > 0.7 average
- Zero data loss incidents

### 10.3 User Experience Metrics

- Time to first plan: < 10 seconds
- User satisfaction: > 4/5 rating
- Error recovery success: > 90%
- Documentation completeness: 100% of public APIs

## 11. Correctness Properties

### Property 1: Three-Phase Invariant
**Validates: Requirements 3.1-3.10**

```
∀ request ∈ UserRequests:
  Phase1(request) → plan
  Phase2(plan) → approval
  approval = true → Phase3(plan)
  approval = false → NoExecution
```

### Property 2: Memory Consistency
**Validates: Requirements 4.1-4.9**

```
∀ file ∈ ModifiedFiles:
  Ingest(file) → ∃ chunks ∈ VectorDB
  Query(file.content) → chunks ∈ Results
  |chunks| = Expected(file.size, chunk_size)
```

### Property 3: Backup Safety
**Validates: Requirements 8.8**

```
∀ modification ∈ FileModifications:
  ∃ backup: backup.content = original.content
  ∧ backup.timestamp < modification.timestamp
  ∧ Restore(backup) → file.content = original.content
```

### Property 4: Configuration Validity
**Validates: Requirements 2.1-2.8, 9.1-9.8**

```
∀ config ∈ Configurations:
  Validate(config) = true → ∃ api_key ∧ ∃ model
  Validate(config) = false → Error(helpful_message)
```

### Property 5: Execution Atomicity
**Validates: Requirements 8.1-8.8**

```
∀ plan ∈ ExecutionPlans:
  Execute(plan) → (AllActionsSucceed ∨ Rollback)
  ∧ PartialExecution → State = Recoverable
```

## 12. Design Decisions

### 12.1 Why Fork Vibe?

- **70% code reuse**: Tool system, CLI, TUI, configuration
- **Production-ready**: Extensive testing and error handling
- **Mature architecture**: Well-designed, extensible codebase
- **Time savings**: 8 weeks vs 12+ weeks from scratch
- **Community**: Active development and maintenance

### 12.2 Why Dual-Mode Operation?

- **Flexibility**: Users choose workflow that fits their task
- **Vibe mode**: Quick, iterative tasks and exploration
- **Spec mode**: Complex, multi-step tasks requiring transparency
- **Gradual adoption**: Users can start with familiar Vibe mode
- **Best of both worlds**: Conversational flexibility + spec-first rigor

### 12.3 Why Keep Vibe's UI Unchanged?

- **Proven UX**: Vibe's UI is polished and user-tested
- **Reduced risk**: No need to redesign and test UI
- **Faster development**: Focus on core features (memory, spec mode)
- **Consistency**: Users familiar with Vibe feel at home
- **Maintenance**: Easier to merge upstream Vibe improvements

### 12.4 Why LiteLLM?

- **Multi-provider**: OpenAI, Anthropic, Ollama, and more
- **Unified API**: Single interface for all providers
- **BYOK support**: No rate limits with user's own keys
- **Local LLM support**: Works with Ollama for privacy
- **Active development**: Well-maintained, growing ecosystem

### 12.5 Why ChromaDB?

- **Lightweight**: No separate server required
- **Git-friendly**: File-based storage, easy to version control
- **Fast**: HNSW index for efficient similarity search
- **Python-native**: Easy integration with our codebase
- **Embeddable**: Runs in-process, no external dependencies

### 12.6 Why TOML Configuration?

- **Vibe's choice**: Already using TOML, no need to change
- **Better than YAML**: Simpler syntax, less error-prone
- **Type-safe**: Pydantic integration for validation
- **Standard**: Growing adoption in Python ecosystem
- **Readable**: Clear structure for nested configuration

## 13. Conclusion

This design provides a solid foundation for HiveTerminal by extending Mistral Vibe with dual-mode operation and a shared memory system. By forking Vibe, we gain:

1. **Production-ready foundation**: 70% of code reused from mature codebase
2. **Dual-mode flexibility**: Vibe mode for quick tasks, Spec mode for complex workflows
3. **Unchanged UI**: Proven, polished interface that users already love
4. **Shared memory**: ChromaDB-powered Hive Mind for intelligent context
5. **Multi-provider support**: LiteLLM enables OpenAI, Anthropic, Ollama, and more

The key innovations are:

- **Mode selection**: `--mode [vibe|spec]` flag for workflow choice
- **Memory integration**: Automatic context injection in both modes
- **Spec mode**: Three-phase loop (Plan → Approve → Execute) for transparency
- **Git-shareable memory**: Team collaboration through shared vector database

By keeping Vibe's UI and tool system intact while adding memory and spec mode, we achieve the best of both worlds: a familiar, polished interface with powerful new capabilities for spec-first development and team knowledge sharing.

**Implementation Timeline:** 8 weeks
- Week 1-2: Fork Vibe, integrate LiteLLM
- Week 3-4: Build memory system
- Week 5-6: Implement spec mode
- Week 7-8: Testing and polish
