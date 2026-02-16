# HiveTerminal Installation Guide

## Quick Installation (Recommended)

### One-Line Install

**macOS & Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/master/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/master/install.ps1 | iex
```

This automated installer will:
1. ✅ Detect your operating system
2. ✅ Check Python version (3.10+ required, 3.13 recommended)
3. ✅ Check for Ollama (optional, shows install link if missing)
4. ✅ Clone HiveTerminal to `~/.hiveterminal` (macOS/Linux) or `%USERPROFILE%\.hiveterminal` (Windows)
5. ✅ Create Python virtual environment
6. ✅ Install all dependencies
7. ✅ Add `hive` command to your PATH
8. ✅ Run initial setup

**After installation, you need to:**
1. Install Ollama: https://ollama.ai
2. Download an AI model (see recommendations below)
3. Restart your terminal/PowerShell

### Choosing Your AI Model

**For Best Results (Recommended):**
```bash
# Best for coding with excellent tool calling
ollama pull qwen2.5-coder:7b        # 4.7GB, needs 8GB+ RAM

# Alternative: Fast and capable
ollama pull deepseek-coder:6.7b     # 3.8GB, needs 8GB+ RAM
```

**For Faster/Smaller Systems:**
```bash
# Balanced performance
ollama pull qwen2.5:3b              # 1.9GB, needs 4GB+ RAM

# Fastest (may struggle with tool calling)
ollama pull qwen2.5-coder:1.5b      # 986MB, needs 2GB+ RAM
```

**Model Comparison:**

| Model | Size | RAM | Tool Calling | Best For |
|-------|------|-----|--------------|----------|
| qwen2.5-coder:7b | 4.7GB | 8GB+ | ✅ Excellent | Production, complex tasks |
| deepseek-coder:6.7b | 3.8GB | 8GB+ | ✅ Excellent | Fast coding tasks |
| qwen2.5:3b | 1.9GB | 4GB+ | ⚠️ Limited | Testing, simple tasks |
| qwen2.5-coder:1.5b | 986MB | 2GB+ | ❌ Poor | Quick tests only |

**After installation:**
```bash
# Restart your terminal, then:
hive
```

---

## Manual Installation

### Prerequisites

1. **Python 3.10+** (3.13 recommended)
   ```bash
   python3 --version
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **Ollama**
   - macOS: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Or visit: https://ollama.ai

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/HyphaeAI/HiveTerminal.git
cd hiveterminal
```

#### 2. Create Virtual Environment
```bash
# Using Python 3.13 (recommended)
python3.13 -m venv .venv

# Or use your default Python 3
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install HiveTerminal
pip install -e .

# Install Vibe (required dependency)
pip install -e Vibe/
```

#### 4. Download AI Model
```bash
# Start Ollama service (if not running)
ollama serve &

# Pull recommended model (7B - best results)
ollama pull qwen2.5-coder:7b

# Or smaller/faster alternatives:
# ollama pull qwen2.5-coder:1.5b  # 986 MB - may struggle with tools
# ollama pull qwen2.5:3b           # 1.9 GB - better than 1.5b
```

#### 5. Add to PATH

Choose one method:

**Method A: Shell Alias (Recommended)**

For **zsh** (macOS default):
```bash
echo 'alias hive="cd ~/hiveterminal && source .venv/bin/activate && python -m hiveterminal.cli.entrypoint"' >> ~/.zshrc
source ~/.zshrc
```

For **bash** (Linux default):
```bash
echo 'alias hive="cd ~/hiveterminal && source .venv/bin/activate && python -m hiveterminal.cli.entrypoint"' >> ~/.bashrc
source ~/.bashrc
```

**Method B: Wrapper Script**

```bash
# Create wrapper script
cat > ~/hiveterminal/hive << 'EOF'
#!/bin/bash
cd ~/hiveterminal
source .venv/bin/activate
python -m hiveterminal.cli.entrypoint "$@"
EOF

# Make executable
chmod +x ~/hiveterminal/hive

# Add to PATH
echo 'export PATH="$HOME/hiveterminal:$PATH"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc  # or source ~/.bashrc
```

#### 6. Run Initial Setup
```bash
hive --setup
```

Follow the prompts to:
1. Select Ollama as your provider
2. Enter your model name (e.g., `qwen2.5-coder:7b`)
3. Complete setup

#### 7. Start Using HiveTerminal
```bash
hive
```

---

## Verification

### Check Installation
```bash
# Check if hive command works
hive --version

# Check Ollama
ollama list

# Check Python environment
which python  # Should show path to .venv
```

### Test Basic Functionality
```bash
# Start HiveTerminal
hive

# Try a simple command
> hi

# Should respond normally (not with raw JSON)
```

---

## Updating HiveTerminal

```bash
cd ~/hiveterminal
git pull origin main
source .venv/bin/activate
pip install -e . --upgrade
pip install -e Vibe/ --upgrade
```

---

## Uninstallation

```bash
# Remove installation directory
rm -rf ~/.hiveterminal

# Remove from shell config
# Edit ~/.zshrc or ~/.bashrc and remove HiveTerminal lines

# Optionally remove Ollama
# macOS: brew uninstall ollama
# Linux: sudo rm /usr/local/bin/ollama
```

---

## Platform-Specific Notes

### macOS

- **Homebrew required** for automatic Ollama installation
- **Default shell**: zsh (use `~/.zshrc`)
- **Python**: Install via Homebrew: `brew install python@3.13`

### Linux

- **Default shell**: Usually bash (use `~/.bashrc`)
- **Python**: Install via package manager:
  - Ubuntu/Debian: `sudo apt install python3.13 python3.13-venv`
  - Fedora: `sudo dnf install python3.13`
  - Arch: `sudo pacman -S python`

---

## Troubleshooting

### Installation Script Fails

**Check prerequisites:**
```bash
# Python version
python3 --version  # Should be 3.10+

# Git
git --version

# Internet connection
ping -c 1 github.com
```

**Run with verbose output:**
```bash
bash -x install.sh
```

### Permission Denied

```bash
# Make script executable
chmod +x install.sh

# Or run with bash
bash install.sh
```

### Ollama Installation Fails

**Manual installation:**
- macOS: Visit https://ollama.ai and download the app
- Linux: Follow instructions at https://ollama.ai/download/linux

### Python Version Too Old

**Install Python 3.13:**

macOS:
```bash
brew install python@3.13
```

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.13 python3.13-venv
```

### Virtual Environment Issues

**Recreate environment:**
```bash
cd ~/hiveterminal
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e Vibe/
```

---

## Getting Help

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check README.md and CURRENT_STATUS.md
- **Ollama Docs**: https://ollama.ai/docs

---

## Next Steps

After successful installation:

1. **Read the README**: `cat ~/hiveterminal/README.md`
2. **Try the examples**: Start with simple tasks
3. **Explore modes**: Try both Conversational and Spec modes
4. **Check memory stats**: `hive --memory-stats`
5. **Join the community**: Star the repo and contribute!

Happy coding! 🐝
