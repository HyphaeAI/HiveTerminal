# Requirements Document: HiveTerminal

## Introduction

HiveTerminal is a dual-mode terminal-based agentic IDE built on top of Mistral Vibe. It offers two operation modes:

1. **Vibe Mode**: Conversational workflow with tool-by-tool execution (Vibe's original behavior)
2. **Spec Mode**: Spec-First workflow that enforces Plan → Approve → Execute

Both modes share a powerful memory system (Hive Mind) powered by ChromaDB for intelligent code context retrieval. The system maintains Vibe's complete UI and UX while adding memory capabilities and an optional spec-first workflow.

**Key Principle**: Keep Vibe's proven interface unchanged while extending functionality through dual-mode operation and shared memory.

## Glossary

- **HiveTerminal**: Dual-mode terminal-based agentic IDE built on Mistral Vibe
- **Vibe Mode**: Conversational workflow with tool-by-tool execution (original Vibe behavior)
- **Spec Mode**: Spec-First workflow with Plan → Approve → Execute phases
- **Agent**: The AI-powered component that processes user requests
- **Hive Mind**: The shared ChromaDB vector database memory system
- **Memory_Manager**: Component responsible for embedding, storing, and retrieving code chunks
- **TUI**: Terminal User Interface - Vibe's rich, interactive command-line interface (unchanged)
- **BYOK**: Bring Your Own Key - users provide their own API keys for AI services
- **Vector_Database**: ChromaDB-based local storage for code embeddings (stored in `./.hive_memory`)
- **Three-Phase Loop**: The Plan → Approve → Execute workflow (Spec Mode only)
- **Conversational Loop**: Tool-by-tool execution workflow (Vibe Mode)
- **Ingestion**: The process of embedding and storing code chunks when files are modified
- **Retrieval**: The process of querying the vector database for relevant context
- **LiteLLM**: Multi-provider AI backend supporting OpenAI, Anthropic, Ollama, and more

## Requirements

### Requirement 1: Terminal User Interface

**User Story:** As a developer, I want a beautiful and intuitive terminal interface, so that I can interact with the agentic IDE efficiently without leaving my terminal.

#### Acceptance Criteria

1. THE TUI SHALL use the `rich` library for rendering formatted output, tables, and progress indicators
2. THE TUI SHALL use the `typer` library for command-line argument parsing and interactive prompts
3. WHEN the application starts, THE TUI SHALL display a welcome banner with system status
4. WHEN displaying plans or code, THE TUI SHALL use syntax highlighting and proper formatting
5. WHEN waiting for user input, THE TUI SHALL provide clear prompts with visual indicators
6. THE TUI SHALL support both Mac and Linux operating systems

### Requirement 2: AI Engine Configuration

**User Story:** As a developer, I want to bring my own API keys and choose my preferred AI model, so that I have control over costs and can use local or cloud-based LLMs.

#### Acceptance Criteria

1. THE Config_Manager SHALL read API keys from OS environment variables
2. THE Config_Manager SHALL support OpenAI API keys via `OPENAI_API_KEY` environment variable
3. THE Config_Manager SHALL support Anthropic API keys via `ANTHROPIC_API_KEY` environment variable
4. THE Config_Manager SHALL support local LLM configuration via Ollama
5. THE Config_Manager SHALL use `litellm` library for unified API access across providers
6. WHEN no API key is found, THE Config_Manager SHALL display a helpful error message with setup instructions
7. THE Config_Manager SHALL allow model selection through configuration or command-line arguments
8. THE Config_Manager SHALL validate API keys on startup and report connection status

### Requirement 3: Dual-Mode Operation

**User Story:** As a developer, I want to choose between conversational and spec-first workflows, so that I can use the approach that best fits my current task.

#### Acceptance Criteria

1. THE System SHALL support two operation modes: Conversational Mode and Spec-First Mode
2. WHEN starting without a mode flag, THE System SHALL display an interactive mode selection prompt
3. THE mode selection prompt SHALL show a clear comparison with examples for both modes
4. THE Conversational Mode SHALL use tool-by-tool execution with individual approvals
5. THE Spec-First Mode SHALL use the three-phase loop (Plan → Approve → Execute)
6. WHEN the user selects Conversational Mode, THE System SHALL initialize VibeAgentLoop
7. WHEN the user selects Spec-First Mode, THE System SHALL initialize SpecAgentLoop
8. BOTH modes SHALL share the same Memory Manager for context retrieval
9. BOTH modes SHALL use the same TUI components (no visual differences)
10. THE System SHALL support runtime mode switching via `/mode` command
11. WHEN switching modes, THE System SHALL preserve conversation history
12. THE mode selection SHALL be skippable via `--mode` CLI flag
13. THE default mode SHALL be configurable in the TOML config file
14. THE mode selection prompt SHALL use Rich formatting for clarity

### Requirement 4: Conversational Mode (Vibe Mode)

**User Story:** As a developer, I want a flexible, iterative workflow where I approve each action, so that I can guide the agent step-by-step through complex tasks.

#### Acceptance Criteria

1. WHEN in Conversational Mode, THE Agent SHALL use Vibe's original conversation loop
2. WHEN the Agent needs to execute a tool, THE Agent SHALL request approval for that specific tool
3. WHEN the user approves a tool, THE Agent SHALL execute it and continue
4. WHEN the user rejects a tool, THE Agent SHALL skip it and adapt its approach
5. THE Agent SHALL be able to adapt its strategy based on tool results
6. THE Agent SHALL support streaming responses for real-time feedback
7. BEFORE generating responses, THE Agent SHALL retrieve relevant context from Memory Manager
8. THE retrieved context SHALL be injected into the conversation messages
9. AFTER executing tools that modify files, THE Agent SHALL trigger memory ingestion
10. THE Conversational Mode SHALL maintain full compatibility with Vibe's tool system
11. THE Conversational Mode SHALL support all of Vibe's existing features (MCP, skills, etc.)

### Requirement 5: Spec-First Mode

**User Story:** As a developer, I want the agent to plan all actions upfront, so that I can review and approve the complete approach before any execution.

#### Acceptance Criteria

1. WHEN a user submits a request in Spec-First Mode, THE Agent SHALL enter Phase 1 (Plan Generation)
2. WHEN in Phase 1, THE Agent SHALL retrieve relevant context from Memory Manager
3. WHEN in Phase 1, THE Agent SHALL analyze the request and generate a markdown plan
4. THE plan SHALL include a summary, risk assessment, detailed steps, and affected files
5. WHEN the plan is generated, THE Agent SHALL display it using Vibe's TUI formatting
6. WHEN the plan is displayed, THE Agent SHALL enter Phase 2 (User Approval)
7. WHEN in Phase 2, THE Agent SHALL prompt the user with "Do you want to proceed with this plan? (y/n)"
8. WHEN the user responds "n" or "no", THE Agent SHALL abort execution and return to ready state
9. WHEN the user responds "y" or "yes", THE Agent SHALL enter Phase 3 (Execution)
10. WHEN in Phase 3, THE Agent SHALL parse the plan into executable actions
11. WHEN in Phase 3, THE Agent SHALL execute actions sequentially according to the plan
12. WHEN execution completes, THE Agent SHALL trigger memory ingestion for modified files
13. WHEN execution completes, THE Agent SHALL display a summary of actions taken
14. THE Agent SHALL NOT execute any code or file modifications without explicit plan approval
15. THE Spec-First Mode SHALL reuse Vibe's tool system for action execution

### Requirement 6: Memory Ingestion

**User Story:** As a developer, I want my code changes to be automatically indexed, so that the agent has context about my codebase for future requests.

#### Acceptance Criteria

1. THE Memory_Manager SHALL use ChromaDB for local vector storage
2. THE Memory_Manager SHALL store all vector data in `./.hive_memory` directory
3. WHEN a file is created or modified, THE Memory_Manager SHALL detect the change
4. WHEN a file change is detected, THE Memory_Manager SHALL split the file into semantic chunks
5. WHEN chunks are created, THE Memory_Manager SHALL generate embeddings for each chunk
6. WHEN embeddings are generated, THE Memory_Manager SHALL store them in the Vector_Database with metadata
7. THE Memory_Manager SHALL store file path, chunk content, line numbers, and timestamp as metadata
8. THE Memory_Manager SHALL support incremental updates without re-indexing the entire codebase
9. THE Memory_Manager SHALL handle common programming languages (Python, JavaScript, TypeScript, Java, Go, Rust)

### Requirement 7: Memory Retrieval

**User Story:** As a developer, I want the agent to automatically find relevant code context, so that it can provide informed responses based on my existing codebase.

#### Acceptance Criteria

1. WHEN the Agent receives a user request in ANY mode, THE Memory_Manager SHALL query the Vector_Database for relevant context
2. WHEN querying, THE Memory_Manager SHALL use semantic similarity search with the user's request as the query
3. WHEN results are found, THE Memory_Manager SHALL return the top K most relevant code chunks (configurable, default K=5)
4. WHEN results are returned, THE Memory_Manager SHALL include file paths, line numbers, and chunk content
5. THE Agent SHALL incorporate retrieved context into its prompt before generating responses
6. WHEN no relevant context is found, THE Agent SHALL proceed without additional context
7. THE Memory_Manager SHALL support filtering by file type, directory, or recency
8. THE context retrieval SHALL work identically in both Conversational and Spec-First modes

### Requirement 8: Shared Team Memory

**User Story:** As a team member, I want to share code context with my teammates, so that everyone benefits from the collective knowledge of the codebase.

#### Acceptance Criteria

1. THE Vector_Database SHALL be stored in a `./.hive_memory` directory within the project
2. THE `.hive_memory` directory SHALL be designed to be version-controlled via Git
3. THE Memory_Manager SHALL handle concurrent access safely when multiple users share the database
4. THE Memory_Manager SHALL support merging vector databases from different team members
5. WHEN the `.hive_memory` directory is synced, THE Memory_Manager SHALL automatically detect and load new embeddings
6. THE Memory_Manager SHALL provide a command to rebuild the entire vector database from scratch

### Requirement 9: Plan Generation (Spec-First Mode Only)

**User Story:** As a developer, I want the agent to generate detailed markdown plans, so that I understand exactly what will be done before approving execution.

#### Acceptance Criteria

1. WHEN generating a plan in Spec-First Mode, THE Agent SHALL create a structured markdown document
2. THE plan SHALL include a summary section describing the overall approach
3. THE plan SHALL include a detailed steps section with numbered actions
4. THE plan SHALL specify which files will be created, modified, or deleted
5. THE plan SHALL include shell commands that will be executed
6. THE plan SHALL estimate the complexity and risk level of the changes
7. WHEN displaying the plan, THE TUI SHALL use Vibe's syntax highlighting and formatting for readability
8. THE plan generation SHALL incorporate context from Memory Manager

### Requirement 10: Code Execution

**User Story:** As a developer, I want the agent to safely execute approved actions, so that my codebase is modified according to my approval.

#### Acceptance Criteria

1. WHEN executing in Conversational Mode, THE Agent SHALL execute tools one-by-one with individual approvals
2. WHEN executing in Spec-First Mode, THE Agent SHALL execute all plan actions sequentially
3. WHEN creating a file, THE Agent SHALL write the complete file content using Vibe's tools
4. WHEN modifying a file, THE Agent SHALL apply precise edits using Vibe's tools
5. WHEN executing shell commands, THE Agent SHALL capture stdout and stderr using Vibe's bash tool
6. WHEN a shell command fails, THE Agent SHALL halt execution and report the error
7. WHEN execution completes successfully, THE Agent SHALL trigger Memory_Manager ingestion for modified files
8. THE Agent SHALL provide real-time progress updates during execution using Vibe's TUI
9. THE Agent SHALL create backups of modified files before applying changes (configurable)
10. BOTH modes SHALL use Vibe's existing tool system for all file and command operations

### Requirement 11: Configuration Management

**User Story:** As a developer, I want to configure the system through environment variables and config files, so that I can customize behavior without modifying code.

#### Acceptance Criteria

1. THE Config_Manager SHALL use TOML format (extending Vibe's config.toml)
2. THE Config_Manager SHALL read configuration from environment variables
3. THE Config_Manager SHALL support a `.hive_config.toml` file for project-specific settings
4. THE Config_Manager SHALL allow configuration of default operation mode (conversational or spec)
5. THE Config_Manager SHALL allow configuration of default AI model and provider
6. THE Config_Manager SHALL support multiple providers (OpenAI, Anthropic, Ollama) via LiteLLM
7. THE Config_Manager SHALL allow configuration of embedding model for vector storage
8. THE Config_Manager SHALL allow configuration of chunk size and overlap for code splitting
9. THE Config_Manager SHALL allow configuration of retrieval parameters (top K, similarity threshold)
10. WHEN configuration is invalid, THE Config_Manager SHALL provide clear error messages
11. THE Config_Manager SHALL support configuration validation on startup
12. THE Config_Manager SHALL maintain compatibility with Vibe's existing configuration structure

### Requirement 12: Error Handling and Recovery

**User Story:** As a developer, I want clear error messages and recovery options, so that I can troubleshoot issues and continue working.

#### Acceptance Criteria

1. WHEN an API error occurs, THE Agent SHALL display the error message and suggest solutions
2. WHEN a file operation fails, THE Agent SHALL report the specific file and error reason
3. WHEN the vector database is corrupted, THE Memory_Manager SHALL offer to rebuild it
4. WHEN execution is interrupted, THE Agent SHALL save progress and allow resumption
5. THE Agent SHALL log all errors to a `.hive_logs` directory for debugging
6. WHEN rate limits are encountered, THE Agent SHALL display a helpful message (though BYOK minimizes this)
7. THE TUI SHALL handle terminal resize events gracefully without crashing

### Requirement 13: CLI Entry Point

**User Story:** As a developer, I want a simple command-line interface to start and interact with HiveTerminal, so that I can integrate it into my workflow easily.

#### Acceptance Criteria

1. THE CLI SHALL provide a `hive` command as the main entry point
2. WHEN invoked without arguments and no mode specified, THE CLI SHALL display an interactive mode selection prompt
3. THE mode selection prompt SHALL show clear examples of both Conversational and Spec-First modes
4. THE mode selection prompt SHALL explain when to use each mode
5. WHEN the user selects a mode, THE CLI SHALL start an interactive session in that mode
6. THE CLI SHALL support a `--mode` flag to specify the mode (conversational, spec)
7. THE CLI SHALL support a `--model` flag to specify the AI model
8. THE CLI SHALL support a `--provider` flag to specify the AI provider (openai, anthropic, ollama)
9. THE CLI SHALL support a `--rebuild-memory` flag to rebuild the vector database
10. THE CLI SHALL support a `--memory-stats` flag to display memory statistics
11. THE CLI SHALL support a `--version` flag to display version information
12. THE CLI SHALL support a `--help` flag to display usage information
13. THE CLI SHALL validate all arguments and provide helpful error messages for invalid input
14. WHEN in interactive mode, THE CLI SHALL support a `/mode` command to switch between modes
15. WHEN switching modes, THE CLI SHALL display the mode selection prompt again
16. THE mode selection SHALL use Vibe's existing UI components (Rich, Console, Prompt)

### Requirement 14: Production Readiness

**User Story:** As a developer, I want production-ready, well-documented code, so that I can deploy and maintain HiveTerminal confidently.

#### Acceptance Criteria

1. THE codebase SHALL include comprehensive inline comments explaining complex logic
2. THE codebase SHALL follow PEP 8 style guidelines for Python code
3. THE codebase SHALL include type hints for all function signatures
4. THE codebase SHALL be organized into modular components (config, memory, agent, main)
5. THE codebase SHALL include a `requirements.txt` file with all dependencies
6. THE codebase SHALL include a README.md with setup and usage instructions
7. THE codebase SHALL handle edge cases gracefully (empty files, binary files, large files)
8. THE codebase SHALL include error handling for all external API calls and file operations


### Requirement 15: Visual Consistency

**User Story:** As a developer familiar with Vibe, I want HiveTerminal to look and feel exactly like Vibe, so that I can use it without learning a new interface.

#### Acceptance Criteria

1. THE TUI SHALL use Vibe's complete Textual UI implementation without modifications
2. THE TUI SHALL use Vibe's Rich formatting, colors, and styling
3. THE TUI SHALL use Vibe's syntax highlighting for code and markdown
4. THE TUI SHALL use Vibe's progress indicators and status displays
5. THE TUI SHALL use Vibe's input prompts and interactive elements
6. THE mode selection prompt SHALL use Rich formatting consistent with Vibe's style
7. THE Spec-First Mode plan display SHALL use Vibe's markdown rendering
8. THE memory statistics display SHALL use Vibe's table formatting
9. WHEN switching modes, THE TUI SHALL maintain visual consistency
10. THE only visual additions SHALL be the mode selection prompt and mode indicator
11. THE mode indicator SHALL be subtle and non-intrusive (e.g., dim text in prompt)
12. ALL new UI elements SHALL follow Vibe's design language and color scheme
