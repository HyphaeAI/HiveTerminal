# Windows Support for HiveTerminal

## ✅ Windows is Fully Supported!

HiveTerminal now runs on Windows 10/11 with full feature parity with macOS and Linux.

## Quick Installation

### One-Line Install (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Tushar04-Master/hiveterminal/main/install.ps1 | iex
```

## Prerequisites

### Required
1. **Python 3.10+** (3.13 recommended)
   - Download: https://www.python.org/downloads/
   - ⚠️ During installation, check "Add Python to PATH"

2. **Git for Windows**
   - Download: https://git-scm.com/download/win
   - Use default installation options

3. **Ollama** (for local AI models)
   - Download: https://ollama.ai/download/windows
   - Runs as a background service

### Optional
- **Windows Terminal** (recommended for better experience)
  - Install from Microsoft Store
  - Better colors, fonts, and Unicode support

## Installation Process

### Automated (Recommended)

1. **Open PowerShell** (not Command Prompt)
   - Press `Win + X`
   - Select "Windows PowerShell" or "Terminal"

2. **Run the installer:**
   ```powershell
   irm https://raw.githubusercontent.com/Tushar04-Master/hiveterminal/main/install.ps1 | iex
   ```

3. **Follow the prompts:**
   - Installer checks Python and Git
   - Clones repository to `%USERPROFILE%\.hiveterminal`
   - Creates virtual environment
   - Installs dependencies
   - Adds `hive` to PATH
   - Runs initial setup

4. **Install Ollama:**
   - Download from: https://ollama.ai/download/windows
   - Run the installer
   - Ollama starts automatically

5. **Download an AI model:**
   ```powershell
   ollama pull qwen2.5-coder:7b
   ```

6. **Restart PowerShell and start:**
   ```powershell
   hive
   ```

### Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

```powershell
# 1. Install prerequisites (if not already installed)
# - Python 3.10+ from https://www.python.org/downloads/
# - Git from https://git-scm.com/download/win
# - Ollama from https://ollama.ai/download/windows

# 2. Clone repository
git clone https://github.com/Tushar04-Master/hiveterminal.git
cd hiveterminal

# 3. Create virtual environment
python -m venv .venv

# 4. Activate virtual environment
.venv\Scripts\Activate.ps1

# 5. Install dependencies
pip install --upgrade pip
pip install -e .
pip install -e Vibe\

# 6. Download AI model
ollama pull qwen2.5-coder:7b

# 7. Create wrapper script
$installDir = Get-Location
@"
@echo off
cd /d "$installDir"
call .venv\Scripts\activate.bat
python -m hiveterminal.cli.entrypoint %*
"@ | Out-File -FilePath hive.bat -Encoding ASCII

# 8. Add to PATH (run as Administrator)
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir", "User")

# 9. Restart PowerShell and run
hive --setup
```

</details>

## Windows-Specific Features

### Command Wrapper
- Uses `hive.bat` batch file
- Automatically activates virtual environment
- Passes all arguments to HiveTerminal

### PATH Integration
- Adds to User PATH (no admin required)
- Works in PowerShell, Command Prompt, and Windows Terminal

### Ollama Integration
- Runs as Windows service
- Starts automatically on boot
- System tray icon for easy access

## Differences from macOS/Linux

### File Paths
- Config: `%USERPROFILE%\.vibe\config.toml`
- Installation: `%USERPROFILE%\.hiveterminal`
- Logs: `%USERPROFILE%\.vibe\logs`

### Shell
- Uses PowerShell instead of bash/zsh
- Batch file wrapper instead of shell script

### Virtual Environment
- Activation: `.venv\Scripts\Activate.ps1` (not `source .venv/bin/activate`)
- Python: `.venv\Scripts\python.exe` (not `.venv/bin/python`)

## Common Issues & Solutions

### PowerShell Execution Policy

**Error:**
```
cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Reinstall Python from https://www.python.org/downloads/
2. Check "Add Python to PATH" during installation
3. Or add manually:
   - Search "Environment Variables" in Start Menu
   - Edit User PATH
   - Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python313`
   - Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python313\Scripts`

### Git Not Found

**Error:**
```
'git' is not recognized as an internal or external command
```

**Solution:**
1. Install Git for Windows: https://git-scm.com/download/win
2. Use default installation options
3. Restart PowerShell

### Ollama Connection Error

**Error:**
```
API error from ollama: connection refused
```

**Solution:**
1. Check if Ollama is running (system tray icon)
2. If not, start from Start Menu: "Ollama"
3. Or reinstall from: https://ollama.ai/download/windows

### PATH Not Updated

**Error:**
```
'hive' is not recognized
```

**Solution:**
```powershell
# Check current PATH
$env:Path -split ';' | Select-String "hiveterminal"

# If not found, add manually (run as Administrator)
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$env:USERPROFILE\.hiveterminal", "User")

# Restart PowerShell
```

## Performance Notes

### Windows Performance
- Similar performance to macOS/Linux
- Ollama uses GPU acceleration if available (NVIDIA/AMD)
- SSD recommended for best performance

### Recommended Specs
- **CPU**: 4+ cores
- **RAM**: 8GB+ (for 7B models)
- **Disk**: 10GB+ free space (SSD preferred)
- **GPU**: Optional (NVIDIA/AMD for acceleration)

## Windows Terminal (Recommended)

For the best experience, use Windows Terminal:

1. **Install from Microsoft Store:**
   - Search "Windows Terminal"
   - Install (free)

2. **Set as default:**
   - Open Windows Terminal
   - Settings → Startup → Default terminal: Windows Terminal

3. **Benefits:**
   - Better Unicode support (for emojis 🐝)
   - Better colors and fonts
   - Multiple tabs
   - Split panes
   - Customizable themes

## Testing on Windows

The installer has been tested on:
- ✅ Windows 11 (22H2)
- ✅ Windows 10 (21H2)
- ✅ PowerShell 5.1
- ✅ PowerShell 7.x
- ✅ Windows Terminal
- ✅ Command Prompt (via hive.bat)

## Known Limitations

### None!
HiveTerminal has full feature parity on Windows:
- ✅ All tools work (bash, file operations, etc.)
- ✅ Memory system works
- ✅ Dual-mode operation works
- ✅ Ollama integration works
- ✅ All models supported

## Getting Help

If you encounter issues on Windows:

1. **Check this guide** for common solutions
2. **Check README.md** troubleshooting section
3. **Open an issue** on GitHub with:
   - Windows version
   - PowerShell version (`$PSVersionTable`)
   - Python version (`python --version`)
   - Error message
   - Steps to reproduce

## Contributing

Windows-specific improvements welcome!
- Test on different Windows versions
- Improve PowerShell installer
- Add Windows-specific features
- Update documentation

---

**Windows users: Welcome to HiveTerminal!** 🐝
