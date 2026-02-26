# HiveTerminal

A dual-mode terminal-based agentic IDE with shared memory, built on Mistral Vibe.

**✨ Now with full Windows support!** Works on macOS, Linux, and Windows 10/11.

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

### 🌐 Multiple LLM Providers

HiveTerminal supports a wide range of AI providers:

- **Xiaomi Mimo** - Free 309B parameter model with 256K context (Recommended for coding)
- **OpenAI** - GPT-4, GPT-4o, and other models
- **Anthropic** - Claude models
- **OpenRouter** - Access to Mistral, Llama, and more
- **Groq** - Fast inference
- **GitHub Models** - Free tier available
- **Google AI Studio** - Gemini models
- **Hugging Face** - Open-source models
- **Ollama** - 100% local, offline models

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

### ⚡ Xiaomi Mimo v2 Flash (Recommended)

- **Free API**: No cost during beta period
- **High Performance**: 309B parameter MoE model with 15B active
- **256K Context**: Massive context window for large codebases
- **#1 on SWE-bench**: 73.4% score, best for coding tasks
- **Fast Inference**: 150 tokens/sec
- **Get API Key**: https://platform.xiaomimimo.com/#/console/api-keys

### 🎨 Familiar Interface

- Maintains Vibe's complete UI and UX
- Rich terminal formatting with syntax highlighting
- Interactive prompts and progress indicators
- No learning curve if you know Vibe

## Quick Start

### One-Line Installation

#### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/master/install.sh | sed 's/Tushar04-Master/HyphaeAI/g' | bash
```

#### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Tushar04-Master/HiveTerminal/main/install.ps1 | iex
```

**What the installer does:**
- ✅ Clone HiveTerminal
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Add `hive` command to your PATH
- ✅ Run initial setup

**After installation, you'll need to:**
1. Install Ollama (for local AI models)
2. Download an AI model
3. Restart your terminal/PowerShell

---

### Installing Ollama & AI Models

#### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
- Download from: https://ollama.ai/download/windows
- Run the installer
- Ollama will start automatically

**Or visit:** https://ollama.ai

#### 2. Choose Your AI Model

**For Best Results (Recommended):**
```bash
# Best for coding with tool calling (7B parameters)
ollama pull qwen2.5-coder:7b        # 4.7GB download

# Alternative: Fast and capable
ollama pull deepseek-coder:6.7b     # 3.8GB download
```

**For Faster/Smaller Systems:**
```bash
# Balanced performance (3B parameters)
ollama pull qwen2.5:3b              # 1.9GB download

# Fastest but limited (1.5B parameters - may struggle with tools)
ollama pull qwen2.5-coder:1.5b      # 986MB download
```

**⚠️ Important:** Models smaller than 7B may have issues with tool calling (outputting raw JSON instead of proper responses). For best experience, use 7B+ models.

**📖 Detailed model comparison:** See [MODEL_GUIDE.md](MODEL_GUIDE.md) for comprehensive model selection guide.

#### 3. Start HiveTerminal

**macOS & Linux:**
```bash
# Restart your terminal, then:
hive

# Follow the setup prompts:
# 1. Select "Ollama" as your provider
# 2. Enter your model name (e.g., "qwen2.5-coder:7b")
# 3. Choose your preferred mode
```

**Windows:**
```powershell
# Restart PowerShell, then:
hive

# Follow the setup prompts:
# 1. Select "Ollama" as your provider
# 2. Enter your model name (e.g., "qwen2.5-coder:7b")
# 3. Choose your preferred mode
```

---

### Model Comparison

| Model | Size | RAM Needed | Tool Calling | Speed | Best For |
|-------|------|------------|--------------|-------|----------|
| qwen2.5-coder:7b | 4.7GB | 8GB+ | ✅ Excellent | Medium | Production use, complex tasks |
| deepseek-coder:6.7b | 3.8GB | 8GB+ | ✅ Excellent | Fast | Coding, fast responses |
| qwen2.5:3b | 1.9GB | 4GB+ | ⚠️ Limited | Fast | Simple tasks, testing |
| qwen2.5-coder:1.5b | 986MB | 2GB+ | ❌ Poor | Very Fast | Quick tests only |

---

### Manual Installation

<details>
<summary><b>macOS & Linux</b></summary>

```bash
# 1. Install Ollama
# macOS:
brew install ollama

# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Clone the repository
git clone https://github.com/Tushar04-Master/HiveTerminal.git
cd hiveterminal

# 3. Create virtual environment (Python 3.10+ required, 3.13 recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Mac/Linux

# 4. Install HiveTerminal and Vibe in editable mode
pip install -e .
pip install -e Vibe/

# 5. Download an AI model (choose based on your needs)
# Recommended for best results:
ollama pull qwen2.5-coder:7b        # 4.7GB - Best for coding

# Or alternatives:
ollama pull deepseek-coder:6.7b     # 3.8GB - Fast & capable
ollama pull qwen2.5:3b              # 1.9GB - Balanced
ollama pull qwen2.5-coder:1.5b      # 986MB - Fastest (limited)

# 6. Add to PATH (choose your shell config file)
echo 'export PATH="$HOME/hiveterminal:$PATH"' >> ~/.zshrc   # for zsh
# or
echo 'export PATH="$HOME/hiveterminal:$PATH"' >> ~/.bashrc  # for bash

# 7. Create alias for easy access
echo 'alias hive="cd ~/hiveterminal && source .venv/bin/activate && python -m hiveterminal.cli.entrypoint"' >> ~/.zshrc
# or for bash:
echo 'alias hive="cd ~/hiveterminal && source .venv/bin/activate && python -m hiveterminal.cli.entrypoint"' >> ~/.bashrc

# 8. Reload shell configuration
source ~/.zshrc  # or source ~/.bashrc

# 9. Run setup
hive --setup
```

</details>

<details>
<summary><b>Windows</b></summary>

**Prerequisites:**
- Python 3.10+ ([Download](https://www.python.org/downloads/))
  - During installation, check "Add Python to PATH"
- Git for Windows ([Download](https://git-scm.com/download/win))
- Ollama ([Download](https://ollama.ai/download/windows))

**Installation Steps:**

```powershell
# 1. Install Ollama
# Download and install from: https://ollama.ai/download/windows

# 2. Clone the repository
git clone https://github.com/Tushar04-Master/HiveTerminal.git
cd hiveterminal

# 3. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 4. Install HiveTerminal and Vibe
pip install -e .
pip install -e Vibe\

# 5. Download an AI model
# Recommended for best results:
ollama pull qwen2.5-coder:7b        # 4.7GB - Best for coding

# Or alternatives:
ollama pull deepseek-coder:6.7b     # 3.8GB - Fast & capable
ollama pull qwen2.5:3b              # 1.9GB - Balanced
ollama pull qwen2.5-coder:1.5b      # 986MB - Fastest (limited)

# 6. Create wrapper script
@"
@echo off
cd /d "$PWD"
call .venv\Scripts\activate.bat
python -m hiveterminal.cli.entrypoint %*
"@ | Out-File -FilePath hive.bat -Encoding ASCII

# 7. Add to PATH (run as Administrator)
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$PWD", "User")

# 8. Restart PowerShell and run setup
hive --setup
```

</details>

### First Run

```bash
# If you used the one-line installer, just type:
hive

# If you installed manually, activate the environment first:
cd ~/hiveterminal
source .venv/bin/activate
python -m hiveterminal.cli.entrypoint

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

### Adding to PATH (Manual Installation)

To use `hive` from anywhere, add it to your PATH:

**For zsh (macOS default):**
```bash
# Add to ~/.zshrc
echo 'alias hive="cd ~/hiveterminal && source .venv/bin/activate && python -m hiveterminal.cli.entrypoint"' >> ~/.zshrc
source ~/.zshrc
```

**For bash (Linux default):**
```bash
# Add to ~/.bashrc
echo 'alias hive="cd ~/hiveterminal && source .venv/bin/activate && python -m hiveterminal.cli.entrypoint"' >> ~/.bashrc
source ~/.bashrc
```

**Alternative: Create a wrapper script**
```bash
# Create wrapper script
cat > ~/hiveterminal/hive << 'EOF'
#!/bin/bash
cd ~/hiveterminal
source .venv/bin/activate
python -m hiveterminal.cli.entrypoint "$@"
EOF

# Make it executable
chmod +x ~/hiveterminal/hive

# Add to PATH
echo 'export PATH="$HOME/hiveterminal:$PATH"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc  # or source ~/.bashrc
```

Now you can run `hive` from any directory!

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

### All Platforms
- Python 3.10+ (3.13 recommended for ChromaDB compatibility)
- Git
- Ollama (install from https://ollama.ai)

### System Requirements by Model

| Model | Download | RAM | Disk | Tool Calling |
|-------|----------|-----|------|--------------|
| 7B models | 4-5GB | 8GB+ | 10GB+ | ✅ Excellent |
| 3B models | 2GB | 4GB+ | 5GB+ | ⚠️ Limited |
| 1.5B models | 1GB | 2GB+ | 3GB+ | ❌ Poor |

### Platform-Specific

**macOS:**
- macOS 10.15 (Catalina) or later
- Homebrew (recommended for easy installation)

**Linux:**
- Ubuntu 20.04+, Debian 11+, Fedora 35+, or equivalent
- systemd (for Ollama service management)

**Windows:**
- Windows 10 (version 1809) or later
- Windows 11 (recommended)
- PowerShell 5.1 or later (comes with Windows)
- Administrator access (for PATH modification)

## Choosing the Right Model

### For Production Use
- **qwen2.5-coder:7b** (4.7GB) - Best overall, excellent tool calling
- **deepseek-coder:6.7b** (3.8GB) - Fast and capable alternative

### For Development/Testing
- **qwen2.5:3b** (1.9GB) - Good balance of speed and capability
- **qwen2.5-coder:1.5b** (986MB) - Fast but limited, may struggle with tools

### System Requirements by Model

| Model | Download | RAM | Disk | Tool Calling |
|-------|----------|-----|------|--------------|
| 7B models | 4-5GB | 8GB+ | 10GB+ | ✅ Excellent |
| 3B models | 2GB | 4GB+ | 5GB+ | ⚠️ Limited |
| 1.5B models | 1GB | 2GB+ | 3GB+ | ❌ Poor |

**Note:** Smaller models (< 7B) may output raw JSON instead of proper responses and struggle with complex tool interactions.

## Troubleshooting

### `hive: command not found` (macOS/Linux) or `'hive' is not recognized` (Windows)

**Solution 1**: Restart your terminal/PowerShell after installation

**Solution 2**: Manually source your shell config (macOS/Linux):
```bash
source ~/.zshrc  # for zsh
# or
source ~/.bashrc  # for bash
```

**Solution 3** (Windows): Check if PATH was updated:
```powershell
$env:Path -split ';' | Select-String "hiveterminal"
```

If not found, add manually:
```powershell
# Run as Administrator
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$env:USERPROFILE\.hiveterminal", "User")
```

**Solution 4**: Check if the alias was added (macOS/Linux):
```bash
grep "hive" ~/.zshrc  # or ~/.bashrc
```

### Ollama connection errors

**Check if Ollama is running:**
```bash
# macOS/Linux:
ollama list

# Windows:
ollama list
```

**Start Ollama service:**

**macOS:**
```bash
brew services start ollama
```

**Linux:**
```bash
ollama serve &
```

**Windows:**
- Ollama runs as a background service automatically
- Check system tray for Ollama icon
- If not running, start from Start Menu: "Ollama"

### Model not found (404 error)

**List available models:**
```bash
ollama list
```

**Pull the model:**
```bash
ollama pull qwen2.5-coder:7b
```

**Make sure model name matches exactly** (including tag):
```bash
# Wrong: qwen2.5-coder
# Right: qwen2.5-coder:7b
```

### Small model issues (tool calling problems)

If using models smaller than 7B (like 1.5B or 3B), you may experience:
- Raw JSON output instead of proper responses
- Inappropriate tool calls
- Confusion about when to use tools

**Solution**: Use a larger model (7B+ recommended):
```bash
ollama pull qwen2.5-coder:7b
hive --setup  # Select the new model
```

### Python version issues

**Check Python version:**
```bash
# macOS/Linux:
python3 --version

# Windows:
python --version
```

**Install Python 3.13** (recommended):

**macOS:**
```bash
brew install python@3.13
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.13 python3.13-venv
```

**Windows:**
- Download from: https://www.python.org/downloads/
- During installation, check "Add Python to PATH"
- Restart PowerShell after installation

### Windows-Specific Issues

**PowerShell Execution Policy Error:**
```
cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Python not found after installation (Windows):**

**Solution:** Add Python to PATH manually:
1. Search for "Environment Variables" in Start Menu
2. Click "Environment Variables"
3. Under "User variables", select "Path" and click "Edit"
4. Click "New" and add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python313`
5. Click "New" and add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\Scripts`
6. Click "OK" and restart PowerShell

**Git not found (Windows):**

**Solution:** Install Git for Windows:
- Download from: https://git-scm.com/download/win
- Use default installation options
- Restart PowerShell after installation

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
