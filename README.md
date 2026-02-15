# HiveTerminal

A dual-mode terminal-based agentic IDE with shared memory, built on Mistral Vibe.

## What is HiveTerminal?

HiveTerminal is an AI-powered coding assistant that combines the flexibility of conversational workflows with the transparency of spec-first development. Built on top of Mistral Vibe, it adds two key innovations:

1. **Dual-Mode Operation**: Choose between conversational (Vibe Mode) and spec-first (Spec Mode) workflows
2. **Hive Mind Memory**: Shared ChromaDB vector database for intelligent code context retrieval

## Key Features

### 🔄 Dual-Mode Operation

**Vibe Mode (Conversational)**
- Tool-by-tool execution with individual approvals
- Iterative, flexible workflow
- Best for exploration and quick tasks
- Approve each action as the agent works

**Spec Mode (Three-Phase)**
- Plan → Approve → Execute workflow
- Single approval for complete plan
- Structured, transparent approach
- Best for complex, multi-step tasks

### 🧠 Hive Mind Memory System

- **Automatic Indexing**: Code changes are automatically embedded and stored
- **Semantic Search**: Retrieves relevant context for every request
- **Git-Shareable**: Team members share knowledge through version control
- **ChromaDB-Powered**: Fast, local vector database with no external dependencies

### 🌐 Local-First with Ollama

- **100% Local**: Run completely offline with Ollama
- **Privacy-Focused**: Your code never leaves your machine
- **No API Costs**: Free to use with local models
- **Multiple Models**: Support for Qwen, Llama, Mistral, and more

### 🎨 Familiar Interface

- Maintains Vibe's complete UI and UX
- Rich terminal formatting with syntax highlighting
- Interactive prompts and progress indicators
- No learning curve if you know Vibe

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository_url>
cd hiveterminal

# Create virtual environment (Python 3.13 recommended for ChromaDB compatibility)
python3.13 -m venv .venv-3.13
source .venv-3.13/bin/activate  # On Mac/Linux

# Install HiveTerminal and Vibe in editable mode
pip install -e .
pip install -e Vibe/

# Install Ollama (if not already installed)
# Visit https://ollama.ai or use:
# brew install ollama  # On macOS

# Pull a model (recommended: qwen2.5-coder:7b for best results)
ollama pull qwen2.5-coder:7b
# or for smaller/faster: ollama pull qwen2.5-coder:1.5b
```

### First Run

```bash
# Start HiveTerminal
hive

# First time: You'll see onboarding to select your LLM provider
# Choose Ollama and enter your model name (e.g., qwen2.5-coder:7b)

# After setup, you'll see mode selection:
# 1. Conversational Mode (Flexible, Interactive)
# 2. Spec-First Mode (Structured, Transparent)

# Or specify mode directly:
hive --mode conversational  # Conversational mode
hive --mode spec            # Spec-first mode

# Run setup again anytime:
hive --setup
```

## Usage Examples

### Conversational Mode Example

```
You: Refactor the login function to use async/await

Agent: I'll read the file first
→ [Tool: read_file] → You approve

Agent: Now I'll make the changes
→ [Tool: write_file] → You approve

Agent: Let me run the tests
→ [Tool: bash] → You approve

✓ Done! Login function refactored.
```

### Spec Mode Example

```
You: Refactor the login function to use async/await

Agent: Here's my execution plan:

# Execution Plan

## Summary
Refactor login.py to use async/await pattern

## Actions
1. Read login.py
2. Refactor function to async
3. Update all callers
4. Run test suite

## Files Affected
- login.py (Modify)
- auth_handler.py (Modify)

Do you want to proceed? (y/n)

You: y

Agent: Executing plan...
✓ Step 1/4: Read login.py
✓ Step 2/4: Refactored to async
✓ Step 3/4: Updated callers
✓ Step 4/4: Tests passing

✓ Done! All changes applied successfully.
```

## Configuration

HiveTerminal uses a TOML configuration file at `~/.vibe/config.toml`:

```toml
# Active model
active_model = "qwen2.5-coder:7b"

# Ollama Provider
[[providers]]
name = "ollama"
api_base = "http://localhost:11434/v1"
api_key_env_var = ""
backend = "generic"

# Model Configuration
[[models]]
name = "qwen2.5-coder:7b"
provider = "ollama"
alias = "qwen2.5-coder:7b"
temperature = 0.2
input_price = 0.0
output_price = 0.0

# Memory Configuration
[memory]
database_path = "./.hive_memory"
embedding_model = "text-embedding-ada-002"  # or "all-MiniLM-L6-v2" for local
chunk_size = 1000
top_k_results = 5
```

**Note**: For best results with tool calling, use models with 7B+ parameters. Smaller models (1.5B-3B) may struggle with complex tool interactions.

## Memory System

### How It Works

1. **Ingestion**: When you modify files, HiveTerminal automatically:
   - Splits code into semantic chunks
   - Generates embeddings
   - Stores in local ChromaDB

2. **Retrieval**: For every request, HiveTerminal:
   - Searches for relevant code context
   - Injects top results into the agent's prompt
   - Provides informed, context-aware responses

3. **Sharing**: The `.hive_memory` directory can be:
   - Committed to Git
   - Shared with team members
   - Merged across branches

### Memory Commands

```bash
# View memory statistics
hive --memory-stats

# Rebuild memory database
hive --rebuild-memory
```

## CLI Reference

```bash
# Start interactive session
hive

# Run onboarding/setup
hive --setup

# Specify mode
hive --mode conversational  # Conversational mode
hive --mode spec            # Spec-first mode

# Memory management
hive --memory-stats         # Show memory statistics
hive --rebuild-memory       # Rebuild vector database

# Help
hive --help
hive --version
```

## When to Use Each Mode

### Use Vibe Mode (Conversational) When:
- Exploring unfamiliar code
- Making quick, iterative changes
- Experimenting with different approaches
- You want fine-grained control over each action
- The task is simple or exploratory

### Use Spec Mode (Three-Phase) When:
- Making complex, multi-file changes
- You want to review the complete plan first
- Transparency is important
- The task has multiple dependent steps
- You want batch execution after approval

### Switch Modes Anytime

```
# In any session, type:
/mode

# You'll see the mode selection prompt again
```

## What Makes HiveTerminal Different?

### vs. Vibe
- ✅ Adds Spec Mode for structured workflows
- ✅ Adds Hive Mind memory system
- ✅ Adds multi-provider support (OpenAI, Anthropic, Ollama)
- ✅ Keeps 100% of Vibe's UI and features
- ✅ Maintains full compatibility with Vibe's tools and MCP

### vs. Other AI Coding Assistants
- ✅ Dual-mode operation (conversational + spec-first)
- ✅ Local, git-shareable memory
- ✅ Terminal-native with rich UI
- ✅ BYOK (no rate limits)
- ✅ Works offline with Ollama

## Architecture

```
┌─────────────────────────────────────────┐
│         CLI Layer (main.py)             │
│     --mode [vibe|spec] flag             │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      TUI Layer (Vibe's Textual UI)      │
│         (NO VISUAL CHANGES)             │
└──────────────────┬──────────────────────┘
                   │
            ┌──────┴──────┐
            │             │
┌───────────▼──┐    ┌─────▼────────────┐
│  Vibe Mode   │    │   Spec Mode      │
│(Conversational)   │ (Three-Phase)    │
└──────┬───────┘    └──────┬───────────┘
       │                   │
       └────────┬──────────┘
                │
┌───────────────▼──────────────────────┐
│     Shared Components (Vibe)         │
│  Tool Manager | Config | LLM Backend │
└───────────────┬──────────────────────┘
                │
┌───────────────▼──────────────────────┐
│   Memory Manager (ChromaDB)          │
│   - Code Ingestion & Chunking        │
│   - Semantic Retrieval               │
│   - Git-Shareable Hive Mind          │
└──────────────────────────────────────┘
```

## Project Structure

```
hiveterminal/
├── core/           # Core functionality and LLM backend
├── cli/            # Command-line interface
├── memory/         # Memory management system
├── agents/         # Agent implementations
└── prompts/        # System prompts

.hive_memory/       # Vector database (created at runtime)
.hive_backups/      # File backups (created at runtime)
.hive_logs/         # Log files (created at runtime)
.hive_config.toml   # Configuration file (optional)
```

## Requirements

- Python 3.13+ (recommended for ChromaDB compatibility)
- macOS or Linux
- Ollama installed and running
- Recommended: 8GB+ RAM for 7B models, 4GB+ for smaller models

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[License information to be added]

## Acknowledgments

Built on top of [Mistral Vibe](https://github.com/mistralai/vibe) - a powerful terminal-based agentic IDE.

## Support

- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)
- **Documentation**: [Full Documentation](link-to-docs)

---

**Ready to get started?** Run `hive` and choose your workflow mode!
