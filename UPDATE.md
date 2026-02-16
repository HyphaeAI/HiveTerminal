# Updating HiveTerminal

## Quick Update

### Automatic Update (Recommended)

```bash
hive --update
```

This will:
1. Check for updates
2. Pull latest changes from GitHub
3. Update dependencies
4. Show changelog

### Manual Update

**macOS & Linux:**
```bash
cd ~/.hiveterminal
git pull origin master
source .venv/bin/activate
pip install -e . --upgrade
pip install -e Vibe/ --upgrade
```

**Windows:**
```powershell
cd $env:USERPROFILE\.hiveterminal
git pull origin master
.venv\Scripts\Activate.ps1
pip install -e . --upgrade
pip install -e Vibe\ --upgrade
```

## Check Current Version

```bash
hive --version
```

## Check for Updates

```bash
hive --check-updates
```

This will check if a new version is available without updating.

## What Gets Updated

- ✅ HiveTerminal core code
- ✅ Vibe dependency
- ✅ Python dependencies
- ✅ Bug fixes and features
- ❌ Your config files (preserved)
- ❌ Your AI models (preserved)
- ❌ Your memory database (preserved)

## Update Notifications

HiveTerminal automatically checks for updates:
- On startup (once per day)
- Shows a notification if update available
- Non-intrusive, doesn't interrupt work

To disable update checks:
```bash
# Edit ~/.vibe/config.toml
enable_update_checks = false
```

## Viewing Changelog

```bash
hive --changelog
```

Or visit: https://github.com/Tushar04-Master/HiveTerminal/blob/main/CHANGELOG.md

## Rollback to Previous Version

If an update causes issues:

```bash
cd ~/.hiveterminal  # or %USERPROFILE%\.hiveterminal on Windows
git log --oneline -10  # See recent commits
git checkout <commit-hash>  # Rollback to specific version
```

Example:
```bash
git checkout b7b00cf  # Rollback to specific commit
```

To return to latest:
```bash
git checkout master
```

## Update Frequency

We recommend updating:
- **Weekly** - For latest features and bug fixes
- **Monthly** - For stable, tested releases
- **When notified** - For critical security updates

## Troubleshooting Updates

### Update fails with "uncommitted changes"

**Solution:**
```bash
cd ~/.hiveterminal
git stash  # Save your changes
git pull origin master
git stash pop  # Restore your changes
```

### Dependencies fail to install

**Solution:**
```bash
cd ~/.hiveterminal
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install --upgrade pip
pip install -e . --force-reinstall
pip install -e Vibe/ --force-reinstall
```

### "Already up to date" but issues persist

**Solution:**
```bash
cd ~/.hiveterminal
git fetch origin
git reset --hard origin/master  # WARNING: Discards local changes
pip install -e . --force-reinstall
pip install -e Vibe/ --force-reinstall
```

## Staying Informed

### GitHub Releases
Watch the repository for release notifications:
https://github.com/Tushar04-Master/HiveTerminal/releases

### Star the Repository
Get notified of major updates:
https://github.com/Tushar04-Master/HiveTerminal

### Check Issues
See known issues and upcoming features:
https://github.com/Tushar04-Master/HiveTerminal/issues

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Automatic Updates (Future)

Coming soon:
- `hive --auto-update` - Enable automatic updates
- Background updates
- Update scheduling
- Rollback on failure

---

**Keep HiveTerminal up to date for the best experience!** 🐝
