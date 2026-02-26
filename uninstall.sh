#!/bin/bash
# HiveTerminal Uninstaller for macOS/Linux
# Run from anywhere: curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/uninstall.sh | bash

set -e

echo "=================================================="
echo "HiveTerminal Uninstaller"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect installation directory
INSTALL_DIR=""
if [ -d "$HOME/hiveterminal" ]; then
    INSTALL_DIR="$HOME/hiveterminal"
elif [ -d "$HOME/.hiveterminal" ]; then
    INSTALL_DIR="$HOME/.hiveterminal"
elif [ -d "$(pwd)/hiveterminal" ]; then
    INSTALL_DIR="$(pwd)/hiveterminal"
fi

# Confirm uninstall
echo -e "${YELLOW}This will remove:${NC}"
echo "  - HiveTerminal installation directory"
echo "  - Configuration files (~/.vibe/)"
echo "  - Environment files (~/.vibe/.env)"
echo "  - Memory database (.hive_memory/)"
echo "  - Shell aliases and PATH entries"
echo ""
echo -e "${RED}WARNING: This action cannot be undone!${NC}"
echo ""
read -p "Are you sure you want to uninstall HiveTerminal? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "Starting uninstall..."
echo ""

# 1. Remove installation directory
if [ -n "$INSTALL_DIR" ] && [ -d "$INSTALL_DIR" ]; then
    echo -e "${GREEN}[1/7]${NC} Removing installation directory: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
    echo "      ✓ Removed"
else
    echo -e "${YELLOW}[1/7]${NC} Installation directory not found (already removed?)"
fi

# 2. Remove configuration directory
if [ -d "$HOME/.vibe" ]; then
    echo -e "${GREEN}[2/7]${NC} Removing configuration directory: ~/.vibe/"
    rm -rf "$HOME/.vibe"
    echo "      ✓ Removed"
else
    echo -e "${YELLOW}[2/7]${NC} Configuration directory not found"
fi

# 3. Remove memory database (if in current directory)
if [ -d ".hive_memory" ]; then
    echo -e "${GREEN}[3/7]${NC} Removing memory database: .hive_memory/"
    rm -rf .hive_memory
    echo "      ✓ Removed"
else
    echo -e "${YELLOW}[3/7]${NC} Memory database not found in current directory"
fi

# 4. Remove backups and logs (if in current directory)
if [ -d ".hive_backups" ]; then
    echo -e "${GREEN}[4/7]${NC} Removing backups: .hive_backups/"
    rm -rf .hive_backups
    echo "      ✓ Removed"
else
    echo -e "${YELLOW}[4/7]${NC} Backups directory not found"
fi

if [ -d ".hive_logs" ]; then
    echo -e "${GREEN}[4/7]${NC} Removing logs: .hive_logs/"
    rm -rf .hive_logs
    echo "      ✓ Removed"
fi

# 5. Remove shell aliases and PATH entries
echo -e "${GREEN}[5/7]${NC} Removing shell configuration..."

# Detect shell
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

if [ -n "$SHELL_CONFIG" ] && [ -f "$SHELL_CONFIG" ]; then
    # Backup shell config
    cp "$SHELL_CONFIG" "${SHELL_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Remove HiveTerminal entries
    sed -i.bak '/hiveterminal/d' "$SHELL_CONFIG" 2>/dev/null || sed -i '' '/hiveterminal/d' "$SHELL_CONFIG"
    sed -i.bak '/alias hive=/d' "$SHELL_CONFIG" 2>/dev/null || sed -i '' '/alias hive=/d' "$SHELL_CONFIG"
    sed -i.bak '/export PATH.*hiveterminal/d' "$SHELL_CONFIG" 2>/dev/null || sed -i '' '/export PATH.*hiveterminal/d' "$SHELL_CONFIG"
    sed -i.bak '/XIAOMI_MIMO_API_KEY/d' "$SHELL_CONFIG" 2>/dev/null || sed -i '' '/XIAOMI_MIMO_API_KEY/d' "$SHELL_CONFIG"
    
    # Remove backup files created by sed
    rm -f "${SHELL_CONFIG}.bak"
    
    echo "      ✓ Cleaned $SHELL_CONFIG"
    echo "      ✓ Backup saved to ${SHELL_CONFIG}.backup.*"
else
    echo -e "${YELLOW}      Shell configuration file not found${NC}"
fi

# 6. Remove wrapper scripts
echo -e "${GREEN}[6/7]${NC} Removing wrapper scripts..."
if [ -f "$HOME/hiveterminal/hive" ]; then
    rm -f "$HOME/hiveterminal/hive"
    echo "      ✓ Removed ~/hiveterminal/hive"
fi
if [ -f "$HOME/.local/bin/hive" ]; then
    rm -f "$HOME/.local/bin/hive"
    echo "      ✓ Removed ~/.local/bin/hive"
fi
if [ -f "/usr/local/bin/hive" ]; then
    sudo rm -f "/usr/local/bin/hive" 2>/dev/null && echo "      ✓ Removed /usr/local/bin/hive" || echo "      ⚠ Could not remove /usr/local/bin/hive (needs sudo)"
fi

# 7. Remove environment variables from current session
echo -e "${GREEN}[7/7]${NC} Cleaning environment variables..."
unset XIAOMI_MIMO_API_KEY 2>/dev/null || true
unset HIVE_MODE 2>/dev/null || true
echo "      ✓ Cleaned"

echo ""
echo "=================================================="
echo -e "${GREEN}✓ HiveTerminal has been completely uninstalled${NC}"
echo "=================================================="
echo ""
echo "Removed:"
echo "  ✓ Installation directory"
echo "  ✓ Configuration files"
echo "  ✓ Memory database"
echo "  ✓ Shell aliases"
echo "  ✓ Environment variables"
echo ""
echo -e "${YELLOW}Note:${NC} Please restart your terminal or run:"
echo "  source ~/.zshrc  # for zsh"
echo "  source ~/.bashrc # for bash"
echo ""
echo "Thank you for using HiveTerminal!"
echo ""
