#!/bin/bash
set -e

# HiveTerminal One-Line Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.sh | bash

echo "🐝 Installing HiveTerminal..."
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

if [ "$MACHINE" = "UNKNOWN:${OS}" ]; then
    echo "❌ Unsupported operating system: ${OS}"
    exit 1
fi

echo "✓ Detected OS: $MACHINE"

# Check Python version
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD=python3.13
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        PYTHON_CMD=python3
    else
        echo "❌ Python 3.10+ required. Found: $PYTHON_VERSION"
        echo "Please install Python 3.13 for best compatibility:"
        if [ "$MACHINE" = "Mac" ]; then
            echo "  brew install python@3.13"
        else
            echo "  Visit https://www.python.org/downloads/"
        fi
        exit 1
    fi
else
    echo "❌ Python 3 not found. Please install Python 3.10+ first."
    exit 1
fi

echo "✓ Using Python: $PYTHON_CMD ($($PYTHON_CMD --version 2>&1))"

# Check if Ollama is installed (optional)
if ! command -v ollama &> /dev/null; then
    echo ""
    echo "ℹ️  Ollama not found (optional for local AI models)"
    echo "   To install Ollama later, visit: https://ollama.ai"
else
    echo "✓ Ollama detected"
fi

# Clone repository
INSTALL_DIR="$HOME/.hiveterminal"

if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "⚠️  HiveTerminal already installed at $INSTALL_DIR"
    read -p "Do you want to reinstall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        echo "Installation cancelled."
        exit 0
    fi
fi

echo ""
echo "📦 Cloning HiveTerminal..."
git clone https://github.com/HyphaeAI/HiveTerminal.git "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
$PYTHON_CMD -m venv .venv
source .venv/bin/activate

# Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -e . > /dev/null 2>&1
pip install -e Vibe/ > /dev/null 2>&1

echo "✓ Dependencies installed"

# Create wrapper script
echo ""
echo "🔗 Creating hive command..."
WRAPPER_SCRIPT="$INSTALL_DIR/hive-wrapper.sh"
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
source "$HOME/.hiveterminal/.venv/bin/activate"
cd "$HOME/.hiveterminal"
python -m hiveterminal.cli.entrypoint "$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Add to PATH
SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_CONFIG="$HOME/.bash_profile"
fi

if [ -n "$SHELL_CONFIG" ]; then
    if ! grep -q "hiveterminal" "$SHELL_CONFIG"; then
        echo "" >> "$SHELL_CONFIG"
        echo "# HiveTerminal" >> "$SHELL_CONFIG"
        echo "export PATH=\"\$HOME/.hiveterminal:\$PATH\"" >> "$SHELL_CONFIG"
        echo "alias hive=\"\$HOME/.hiveterminal/hive-wrapper.sh\"" >> "$SHELL_CONFIG"
        echo "✓ Added to $SHELL_CONFIG"
    else
        echo "✓ Already in $SHELL_CONFIG"
    fi
fi

# Run initial setup
echo ""
echo "⚙️  Running initial setup..."
echo ""
echo "You'll be prompted to:"
echo "  1. Choose your AI provider (Ollama recommended for local/free)"
echo "  2. Select or enter your model name"
echo ""
source .venv/bin/activate
python -m hiveterminal.cli.entrypoint --setup

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎉 HiveTerminal is ready to use!"
echo ""
echo "📝 Next steps:"
echo "  1. Restart your terminal (or run: source $SHELL_CONFIG)"
echo "  2. Install Ollama if you haven't: https://ollama.ai"
echo "  3. Download an AI model (see recommendations below)"
echo "  4. Type: hive"
echo ""
echo "🤖 Recommended AI Models:"
echo ""
echo "  For best results (7B+ parameters):"
echo "    ollama pull qwen2.5-coder:7b        # 4.7GB - Best for coding"
echo "    ollama pull deepseek-coder:6.7b     # 3.8GB - Fast & capable"
echo ""
echo "  For faster/smaller (may struggle with tools):"
echo "    ollama pull qwen2.5-coder:1.5b      # 986MB - Fastest"
echo "    ollama pull qwen2.5:3b              # 1.9GB - Balanced"
echo ""
echo "Quick commands:"
echo "  hive              - Start HiveTerminal"
echo "  hive --setup      - Run setup again"
echo "  hive --help       - Show help"
echo ""
echo "Happy coding! 🐝"
