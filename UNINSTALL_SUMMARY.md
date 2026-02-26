# HiveTerminal Uninstall - Complete

## ✅ Uninstall Scripts Created

### Files Created
1. **`uninstall.sh`** - macOS/Linux uninstaller (executable)
2. **`uninstall.ps1`** - Windows PowerShell uninstaller
3. **`UNINSTALL.md`** - Comprehensive uninstall documentation
4. **`README.md`** - Updated with uninstall section

---

## 🚀 One-Liner Uninstall Commands

### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/uninstall.sh | bash
```

**Or locally:**
```bash
cd ~/hiveterminal && ./uninstall.sh
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/uninstall.ps1 | iex
```

**Or locally:**
```powershell
cd ~\hiveterminal
.\uninstall.ps1
```

---

## 🗑️ What Gets Removed

### Files & Directories
- ✓ Installation directory (`~/hiveterminal` or `~/.hiveterminal`)
- ✓ Configuration files (`~/.vibe/`)
- ✓ Environment files (`~/.vibe/.env`)
- ✓ Memory database (`.hive_memory/`)
- ✓ Backups (`.hive_backups/`)
- ✓ Logs (`.hive_logs/`)

### System Configuration
- ✓ Shell aliases (`alias hive=...`)
- ✓ PATH entries
- ✓ Environment variables (`XIAOMI_MIMO_API_KEY`, etc.)
- ✓ Wrapper scripts (`hive` command)

---

## 📋 Uninstall Process

The script performs these steps:

1. **Confirms uninstall** - Asks for user confirmation
2. **Removes installation** - Deletes HiveTerminal directory
3. **Cleans configuration** - Removes `~/.vibe/`
4. **Removes databases** - Deletes memory, backups, logs
5. **Cleans shell config** - Removes aliases and PATH entries (with backup)
6. **Removes wrappers** - Deletes `hive` command scripts
7. **Cleans environment** - Removes environment variables

### Safety Features

- ✅ **Confirmation prompt** - Prevents accidental uninstall
- ✅ **Backup shell config** - Creates `.backup` file before modifying
- ✅ **Graceful failures** - Continues even if some files don't exist
- ✅ **Clear output** - Shows what's being removed
- ✅ **Verification** - Confirms successful removal

---

## 🧪 Testing the Uninstaller

### Test on macOS/Linux
```bash
# 1. Make sure you have HiveTerminal installed
which hive

# 2. Run uninstaller
./uninstall.sh

# 3. Confirm when prompted
# Type 'y' and press Enter

# 4. Verify removal
which hive  # Should show: hive not found
ls -la ~/.vibe  # Should show: No such file or directory
```

### Test on Windows
```powershell
# 1. Make sure you have HiveTerminal installed
where.exe hive

# 2. Run uninstaller (as Administrator)
.\uninstall.ps1

# 3. Confirm when prompted
# Type 'y' and press Enter

# 4. Verify removal
where.exe hive  # Should show: INFO: Could not find files
dir $env:USERPROFILE\.vibe  # Should show: cannot find the path
```

---

## 📖 Documentation Updates

### README.md
Added comprehensive "Uninstalling HiveTerminal" section with:
- One-liner uninstall commands
- What gets removed
- Manual uninstall instructions (macOS/Linux/Windows)
- Post-uninstall verification
- Optional Ollama removal

### UNINSTALL.md
Created detailed uninstall guide with:
- Quick uninstall (one-liner)
- Detailed uninstall process
- Manual uninstall steps for each platform
- Verification procedures
- Partial uninstall (keeping config)
- Ollama removal instructions
- Troubleshooting section
- Reinstall instructions

---

## 🔍 Verification Commands

### After Uninstall

**Check command removed:**
```bash
# macOS/Linux:
which hive  # Should show: hive not found

# Windows:
where.exe hive  # Should show: INFO: Could not find files
```

**Check directories removed:**
```bash
# macOS/Linux:
ls -la ~/hiveterminal  # Should show: No such file or directory
ls -la ~/.vibe         # Should show: No such file or directory

# Windows:
dir $env:USERPROFILE\hiveterminal  # Should show: cannot find the path
dir $env:USERPROFILE\.vibe         # Should show: cannot find the path
```

**Check environment cleaned:**
```bash
# macOS/Linux:
echo $XIAOMI_MIMO_API_KEY  # Should be empty

# Windows:
$env:XIAOMI_MIMO_API_KEY  # Should be empty
```

---

## 🛡️ Safety & Backup

### Shell Configuration Backup
The uninstaller automatically creates a backup before modifying shell config:

**macOS/Linux:**
```bash
~/.zshrc.backup.YYYYMMDD_HHMMSS
~/.bashrc.backup.YYYYMMDD_HHMMSS
```

**To restore:**
```bash
cp ~/.zshrc.backup.20260216_174300 ~/.zshrc
source ~/.zshrc
```

### Configuration Backup (Manual)
Before uninstalling, you can backup your configuration:

```bash
# macOS/Linux:
cp -r ~/.vibe ~/.vibe.backup

# Windows:
Copy-Item -Path "$env:USERPROFILE\.vibe" -Destination "$env:USERPROFILE\.vibe.backup" -Recurse
```

---

## 🔄 Reinstall After Uninstall

### Fresh Install
```bash
# macOS/Linux:
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.sh | bash

# Windows:
irm https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.ps1 | iex
```

### Restore Configuration
If you kept `~/.vibe/` or created a backup:

1. Reinstall HiveTerminal
2. Configuration is automatically detected
3. Run `hive --setup` to verify
4. API keys and preferences restored

---

## 📊 Uninstaller Features

### Cross-Platform Support
- ✅ macOS (Bash)
- ✅ Linux (Bash)
- ✅ Windows (PowerShell)

### Comprehensive Removal
- ✅ Installation files
- ✅ Configuration files
- ✅ Database files
- ✅ Shell configuration
- ✅ Environment variables
- ✅ PATH entries
- ✅ Wrapper scripts

### User-Friendly
- ✅ Confirmation prompt
- ✅ Clear progress indicators
- ✅ Color-coded output
- ✅ Backup creation
- ✅ Graceful error handling
- ✅ Post-uninstall instructions

### Safe & Reliable
- ✅ Backs up shell config
- ✅ Continues on errors
- ✅ No sudo required (except for system-wide installs)
- ✅ Verifies removal
- ✅ Provides rollback instructions

---

## 🐛 Troubleshooting

### Permission Denied
```bash
# macOS/Linux:
sudo ./uninstall.sh

# Windows:
# Run PowerShell as Administrator
```

### Files Still Exist
```bash
# Force remove (macOS/Linux):
sudo rm -rf ~/hiveterminal ~/.vibe

# Force remove (Windows, as Administrator):
Remove-Item -Path "$env:USERPROFILE\hiveterminal" -Recurse -Force
Remove-Item -Path "$env:USERPROFILE\.vibe" -Recurse -Force
```

### Command Still Works
```bash
# Clear shell cache (macOS/Linux):
hash -r  # bash
rehash   # zsh

# Windows:
# Restart PowerShell
```

---

## 📝 Usage Examples

### Standard Uninstall
```bash
# macOS/Linux:
cd ~/hiveterminal
./uninstall.sh
# Type 'y' when prompted

# Windows:
cd ~\hiveterminal
.\uninstall.ps1
# Type 'y' when prompted
```

### Silent Uninstall (No Confirmation)
```bash
# macOS/Linux:
echo "y" | ./uninstall.sh

# Windows:
echo "y" | .\uninstall.ps1
```

### Verbose Uninstall (Debug)
```bash
# macOS/Linux:
bash -x uninstall.sh

# Windows:
Set-PSDebug -Trace 1
.\uninstall.ps1
```

---

## 🎯 Summary

### Created Files
1. ✅ `uninstall.sh` - Bash uninstaller (macOS/Linux)
2. ✅ `uninstall.ps1` - PowerShell uninstaller (Windows)
3. ✅ `UNINSTALL.md` - Comprehensive documentation
4. ✅ `README.md` - Updated with uninstall section

### Features
- ✅ One-liner uninstall command
- ✅ Cross-platform support (macOS/Linux/Windows)
- ✅ Comprehensive removal (files, config, env vars)
- ✅ Safe (confirmation, backups, graceful errors)
- ✅ User-friendly (clear output, progress indicators)
- ✅ Well-documented (README + UNINSTALL.md)

### Testing
- ✅ Scripts are executable
- ✅ Syntax validated
- ✅ Safety features implemented
- ✅ Documentation complete

---

**Status:** ✅ Complete and Ready to Use  
**Date:** February 16, 2026  
**Platforms:** macOS, Linux, Windows  
**Documentation:** README.md + UNINSTALL.md
