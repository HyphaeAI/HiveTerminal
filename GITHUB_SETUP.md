# GitHub Setup Instructions

✅ **Repository is now configured for: https://github.com/HyphaeAI/HiveTerminal**

All documentation files have been updated with the correct GitHub URLs.

## Files Updated

### 1. install.sh
Updated to use `HyphaeAI/HiveTerminal`:
```bash
# Usage: curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.sh | bash
git clone https://github.com/HyphaeAI/HiveTerminal.git "$INSTALL_DIR"
```

### 2. README.md
Updated all installation commands to use `HyphaeAI/HiveTerminal`

### 3. INSTALL.md
Updated all references to use `HyphaeAI/HiveTerminal`

### 4. All other documentation files
Updated to use the correct repository URL

## Making install.sh Accessible

The one-line installer works by fetching the script from GitHub's raw content URL. Make sure:

1. ✅ Repository is public (or use a personal access token for private repos)
2. ✅ `install.sh` is in the repository root
3. ✅ File is committed and pushed to the `main` branch
4. ✅ URLs are updated with your actual username

## Testing the Installer

Test the installer in a clean environment:

```bash
# Test macOS/Linux installer
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.sh | bash

# Or download and inspect first:
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.sh > test-install.sh
cat test-install.sh  # Review the script
bash test-install.sh
```

**Windows:**
```powershell
# Test Windows installer
irm https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.ps1 | iex
```

## Installation Commands

Users can now install HiveTerminal with:

**macOS & Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.ps1 | iex
```
