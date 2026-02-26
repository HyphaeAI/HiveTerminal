# HiveTerminal Uninstall Guide

Complete guide for removing HiveTerminal from your system.

## Quick Uninstall (One-Liner)

### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/main/uninstall.sh | bash
```

Or if you have the repository:
```bash
cd ~/hiveterminal && ./uninstall.sh
```

### Windows (PowerShell - Run as Administrator)
```powershell
irm https://raw.githubusercontent.com/YOUR_REPO/main/uninstall.ps1 | iex
```

Or if you have the repository:
```powershell
cd ~\hiveterminal
.\uninstall.ps1
```

---

## What Gets Removed

The uninstaller removes all HiveTerminal components:

### Files & Directories
- ✓ **Installation directory**
  - `~/hiveterminal` or `~/.hiveterminal` (macOS/Linux)
  - `%USERPROFILE%\hiveterminal` (Windows)
  
- ✓ **Configuration files**
  - `~/.vibe/config.toml`
  - `~/.vibe/.env`
  - All other config files in `~/.vibe/`

- ✓ **Memory database**
  - `.hive_memory/` (in project directories)
  
- ✓ **Backups & Logs**
  - `.hive_backups/`
  - `.hive_logs/`

### System Configuration
- ✓ **Shell aliases** (macOS/Linux)
  - `alias hive=...` from `~/.zshrc` or `~/.bashrc`
  
- ✓ **PATH entries**
  - Removes HiveTerminal from system PATH
  
- ✓ **Environment variables**
  - `XIAOMI_MIMO_API_KEY`
  - `HIVE_MODE`
  - Other HiveTerminal-related variables

### Commands
- ✓ **Wrapper scripts**
  - `hive` command
  - `hive.bat` (Windows)

---

## Detailed Uninstall Process

### Automatic Uninstall (Recommended)

The uninstall script performs these steps automatically:

1. **Confirms uninstall** - Asks for confirmation before proceeding
2. **Removes installation** - Deletes the HiveTerminal directory
3. **Cleans configuration** - Removes `~/.vibe/` directory
4. **Removes databases** - Deletes memory, backups, and logs
5. **Cleans shell config** - Removes aliases and PATH entries
6. **Removes wrappers** - Deletes `hive` command scripts
7. **Cleans environment** - Removes environment variables

### Manual Uninstall

If you prefer manual removal or the script fails:

<details>
<summary><b>macOS Manual Uninstall</b></summary>

```bash
# 1. Remove installation directory
rm -rf ~/hiveterminal
# or if installed elsewhere:
rm -rf ~/.hiveterminal

# 2. Remove configuration
rm -rf ~/.vibe

# 3. Remove memory database (in project directories)
cd ~/your-project
rm -rf .hive_memory .hive_backups .hive_logs

# 4. Edit shell configuration
nano ~/.zshrc  # or ~/.bashrc

# Remove these lines:
# - export PATH="$HOME/hiveterminal:$PATH"
# - alias hive="..."
# - export XIAOMI_MIMO_API_KEY="..."

# 5. Remove wrapper script (if exists)
rm -f ~/hiveterminal/hive
rm -f ~/.local/bin/hive
sudo rm -f /usr/local/bin/hive  # if installed system-wide

# 6. Reload shell configuration
source ~/.zshrc  # or source ~/.bashrc

# 7. Verify removal
which hive  # Should show: hive not found
```

</details>

<details>
<summary><b>Linux Manual Uninstall</b></summary>

```bash
# 1. Remove installation directory
rm -rf ~/hiveterminal
# or if installed elsewhere:
rm -rf ~/.hiveterminal

# 2. Remove configuration
rm -rf ~/.vibe

# 3. Remove memory database (in project directories)
cd ~/your-project
rm -rf .hive_memory .hive_backups .hive_logs

# 4. Edit shell configuration
nano ~/.bashrc  # or ~/.zshrc

# Remove these lines:
# - export PATH="$HOME/hiveterminal:$PATH"
# - alias hive="..."
# - export XIAOMI_MIMO_API_KEY="..."

# 5. Remove wrapper script (if exists)
rm -f ~/hiveterminal/hive
rm -f ~/.local/bin/hive
sudo rm -f /usr/local/bin/hive  # if installed system-wide

# 6. Reload shell configuration
source ~/.bashrc  # or source ~/.zshrc

# 7. Verify removal
which hive  # Should show: hive not found
```

</details>

<details>
<summary><b>Windows Manual Uninstall</b></summary>

**PowerShell (Run as Administrator):**

```powershell
# 1. Remove installation directory
Remove-Item -Path "$env:USERPROFILE\hiveterminal" -Recurse -Force

# 2. Remove configuration
Remove-Item -Path "$env:USERPROFILE\.vibe" -Recurse -Force

# 3. Remove memory database (in project directories)
cd C:\your-project
Remove-Item -Path ".hive_memory" -Recurse -Force
Remove-Item -Path ".hive_backups" -Recurse -Force
Remove-Item -Path ".hive_logs" -Recurse -Force

# 4. Remove environment variables
[Environment]::SetEnvironmentVariable("XIAOMI_MIMO_API_KEY", $null, "User")
[Environment]::SetEnvironmentVariable("HIVE_MODE", $null, "User")

# 5. Remove from PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = ($currentPath -split ';' | Where-Object { $_ -notlike "*hiveterminal*" }) -join ';'
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# 6. Remove wrapper scripts
Remove-Item -Path "$env:USERPROFILE\hiveterminal\hive.bat" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\.local\bin\hive.bat" -Force -ErrorAction SilentlyContinue

# 7. Restart PowerShell and verify
# Close and reopen PowerShell, then:
hive --version  # Should show: 'hive' is not recognized
```

</details>

---

## Verification

After uninstalling, verify that HiveTerminal is completely removed:

### Check Command
```bash
# macOS/Linux:
which hive
# Should output: hive not found

# Windows:
where.exe hive
# Should output: INFO: Could not find files for the given pattern(s).
```

### Check Directories
```bash
# macOS/Linux:
ls -la ~/hiveterminal  # Should show: No such file or directory
ls -la ~/.vibe         # Should show: No such file or directory

# Windows:
dir $env:USERPROFILE\hiveterminal  # Should show: cannot find the path
dir $env:USERPROFILE\.vibe         # Should show: cannot find the path
```

### Check Environment
```bash
# macOS/Linux:
echo $XIAOMI_MIMO_API_KEY  # Should be empty

# Windows:
$env:XIAOMI_MIMO_API_KEY  # Should be empty
```

---

## Keeping Configuration (Partial Uninstall)

If you want to remove HiveTerminal but keep your configuration for later:

### macOS & Linux
```bash
# Remove only the installation, keep config
rm -rf ~/hiveterminal

# Keep these:
# - ~/.vibe/config.toml (your settings)
# - ~/.vibe/.env (your API keys)
```

### Windows
```powershell
# Remove only the installation, keep config
Remove-Item -Path "$env:USERPROFILE\hiveterminal" -Recurse -Force

# Keep these:
# - %USERPROFILE%\.vibe\config.toml (your settings)
# - %USERPROFILE%\.vibe\.env (your API keys)
```

---

## Removing Ollama (Optional)

If you installed Ollama for HiveTerminal and no longer need it:

### macOS
```bash
# Stop Ollama service
brew services stop ollama

# Uninstall Ollama
brew uninstall ollama

# Remove Ollama data (optional)
rm -rf ~/.ollama
```

### Linux
```bash
# Stop Ollama service
sudo systemctl stop ollama

# Remove Ollama binary
sudo rm -rf /usr/local/bin/ollama

# Remove Ollama data (optional)
rm -rf ~/.ollama
```

### Windows
1. Open **Settings** → **Apps**
2. Search for "Ollama"
3. Click **Uninstall**
4. Optionally delete: `%USERPROFILE%\.ollama`

---

## Troubleshooting Uninstall

### "Permission Denied" Errors

**macOS/Linux:**
```bash
# Use sudo for system-wide installations
sudo rm -rf /usr/local/bin/hive
sudo rm -rf /opt/hiveterminal
```

**Windows:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → "Run as Administrator"
```

### Files Still Exist After Uninstall

**Check for hidden files:**
```bash
# macOS/Linux:
ls -la ~/hiveterminal
ls -la ~/.vibe

# Windows:
dir /a $env:USERPROFILE\hiveterminal
```

**Force remove:**
```bash
# macOS/Linux:
sudo rm -rf ~/hiveterminal ~/.vibe

# Windows (as Administrator):
Remove-Item -Path "$env:USERPROFILE\hiveterminal" -Recurse -Force
Remove-Item -Path "$env:USERPROFILE\.vibe" -Recurse -Force
```

### Command Still Works After Uninstall

**Clear shell cache:**
```bash
# macOS/Linux:
hash -r  # bash
rehash   # zsh

# Windows:
# Restart PowerShell
```

**Check for multiple installations:**
```bash
# macOS/Linux:
which -a hive  # Shows all hive commands in PATH

# Windows:
where.exe hive  # Shows all hive.bat files
```

### Environment Variables Persist

**macOS/Linux:**
```bash
# Check current shell session
env | grep -i hive
env | grep -i xiaomi

# Unset manually
unset XIAOMI_MIMO_API_KEY
unset HIVE_MODE

# Check shell config files
grep -r "XIAOMI_MIMO_API_KEY" ~/.zshrc ~/.bashrc ~/.profile
```

**Windows:**
```powershell
# Check environment variables
Get-ChildItem Env: | Where-Object { $_.Name -like "*HIVE*" -or $_.Name -like "*XIAOMI*" }

# Remove manually (as Administrator)
[Environment]::SetEnvironmentVariable("XIAOMI_MIMO_API_KEY", $null, "User")
[Environment]::SetEnvironmentVariable("HIVE_MODE", $null, "User")
```

---

## Reinstalling After Uninstall

If you want to reinstall HiveTerminal after uninstalling:

### Fresh Install
```bash
# macOS/Linux:
curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/main/install.sh | bash

# Windows:
irm https://raw.githubusercontent.com/YOUR_REPO/main/install.ps1 | iex
```

### Restore Previous Configuration

If you kept your `~/.vibe/` directory:

1. Reinstall HiveTerminal (see above)
2. Your previous configuration will be automatically detected
3. Run `hive --setup` to verify settings
4. Your API keys and preferences should be restored

---

## Support

If you encounter issues during uninstall:

1. **Check the troubleshooting section** above
2. **Run the uninstall script with verbose output:**
   ```bash
   # macOS/Linux:
   bash -x uninstall.sh
   
   # Windows:
   Set-PSDebug -Trace 1
   .\uninstall.ps1
   ```
3. **Open an issue** on GitHub with:
   - Your operating system
   - Error messages
   - Output from the uninstall script

---

## Feedback

We're sorry to see you go! If you have a moment, please let us know why you're uninstalling:

- **GitHub Issues**: Report bugs or issues
- **GitHub Discussions**: Share feedback or suggestions
- **Email**: [your-email@example.com]

Your feedback helps us improve HiveTerminal for everyone.

---

**Thank you for using HiveTerminal!** 🙏

---

**Last Updated:** February 16, 2026  
**Version:** 1.0.0
