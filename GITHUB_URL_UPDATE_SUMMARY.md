# GitHub URL Update Summary

## ✅ All Documentation Updated

All references to the GitHub repository have been updated to use:
**https://github.com/HyphaeAI/HiveTerminal**

## Files Updated

### Installation Scripts
- ✅ `install.sh` - Updated clone URL and usage comment
- ✅ `install.ps1` - Updated clone URL and usage comment
- ✅ `uninstall.sh` - Updated usage comment
- ✅ `uninstall.ps1` - Updated usage comment

### Documentation Files
- ✅ `README.md` - Updated all installation commands and git clone URLs
- ✅ `INSTALL.md` - Updated installation commands
- ✅ `UNINSTALL.md` - Updated uninstall commands
- ✅ `UNINSTALL_SUMMARY.md` - Updated all references
- ✅ `UPDATE.md` - Updated GitHub links
- ✅ `CONTRIBUTING.md` - Updated clone URL
- ✅ `CHANGELOG.md` - Updated release links
- ✅ `GITHUB_SETUP.md` - Updated with new repo info
- ✅ `INSTALLATION_SUMMARY.md` - Updated all references
- ✅ `WINDOWS_SUPPORT.md` - Updated installation commands
- ✅ `PUSH_CHECKLIST.md` - Updated verification URLs
- ✅ `COMMIT_MESSAGE.txt` - Updated installation commands

### Source Code
- ✅ `hiveterminal/cli/entrypoint.py` - Updated changelog URL

## Installation Commands

Users can now install HiveTerminal with:

### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/install.ps1 | iex
```

## Uninstall Commands

### macOS & Linux
```bash
curl -fsSL https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/uninstall.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/HyphaeAI/HiveTerminal/main/uninstall.ps1 | iex
```

## Repository Links

- **Repository**: https://github.com/HyphaeAI/HiveTerminal
- **Releases**: https://github.com/HyphaeAI/HiveTerminal/releases
- **Issues**: https://github.com/HyphaeAI/HiveTerminal/issues
- **Changelog**: https://github.com/HyphaeAI/HiveTerminal/blob/main/CHANGELOG.md

## Next Steps

1. ✅ All URLs updated
2. **Commit changes**: `git add -A && git commit -m "Update all GitHub URLs to HyphaeAI/HiveTerminal"`
3. **Push to GitHub**: `git push origin main`
4. **Test installer**: Verify the one-line installer works from the GitHub URL
5. **Update README badges** (if any): Update any shields.io badges with the new repo URL

## Verification

Run this command to verify no old references remain:
```bash
grep -r "Tushar04-Master\|YOUR_REPO" --exclude-dir=.git --exclude-dir=.venv --exclude-dir=Vibe .
```

Should return no results (except this summary file).

## Status

✅ **Complete** - All documentation and scripts now use the correct GitHub repository URL.
