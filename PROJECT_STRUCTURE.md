# HiveTerminal Project Structure

## Root Directory

```
HiveTerminal/
├── README.md                    # Main documentation
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # Contribution guidelines
├── pyproject.toml              # Python package configuration
├── .gitignore                  # Git ignore rules
├── .hive_config.toml           # Example configuration
│
├── install.sh                  # macOS/Linux installer
├── install.ps1                 # Windows installer
├── uninstall.sh                # macOS/Linux uninstaller
├── uninstall.ps1               # Windows uninstaller
│
├── docs/                       # Documentation
│   ├── INSTALL.md              # Detailed installation guide
│   ├── UNINSTALL.md            # Uninstallation guide
│   ├── MODEL_GUIDE.md          # Model selection guide
│   ├── STATE_MANAGEMENT_QUICK_START.md  # State management guide
│   └── FINAL_SUMMARY_FOR_JUDGES.md      # Judge submission summary
│
├── hiveterminal/               # Main source code
│   ├── __init__.py
│   ├── cli/                    # CLI interface
│   ├── core/                   # Core functionality
│   ├── memory/                 # Memory management
│   ├── agents/                 # Agent implementations
│   ├── prompts/                # System prompts
│   ├── state/                  # State management (Phase 2)
│   └── tools/                  # Custom tools
│
├── Vibe/                       # Mistral Vibe dependency
│   └── vibe/                   # Vibe source code
│
└── tests/                      # Test suite (optional)
```

## Key Files

### User-Facing
- **README.md**: Complete project overview, features, installation
- **docs/INSTALL.md**: Detailed installation instructions
- **docs/MODEL_GUIDE.md**: AI model selection guide
- **docs/STATE_MANAGEMENT_QUICK_START.md**: Token optimization guide

### Installation
- **install.sh**: One-line installer for macOS/Linux
- **install.ps1**: One-line installer for Windows
- **uninstall.sh**: Uninstaller for macOS/Linux
- **uninstall.ps1**: Uninstaller for Windows

### Configuration
- **.hive_config.toml**: Example configuration file
- **pyproject.toml**: Python package metadata

### Development
- **CONTRIBUTING.md**: How to contribute
- **CHANGELOG.md**: Version history
- **LICENSE**: MIT License

### For Judges
- **docs/FINAL_SUMMARY_FOR_JUDGES.md**: Complete submission summary

## Source Code Structure

### hiveterminal/
```
hiveterminal/
├── __init__.py
├── cli/
│   ├── entrypoint.py           # Main entry point
│   └── ...
├── core/
│   ├── llm/                    # LLM backend
│   └── ...
├── memory/
│   ├── manager.py              # Memory management
│   └── ...
├── agents/
│   ├── spec_agent.py           # Spec mode agent
│   └── ...
├── prompts/
│   └── system_prompts.md       # System prompts
├── state/                      # Phase 2: State management
│   ├── __init__.py
│   └── manager.py              # State manager
└── tools/                      # Phase 2: Custom tools
    ├── __init__.py
    ├── state_tool.py           # State management tool
    └── prompts/
        └── state_tool.md       # Tool documentation
```

## Runtime Directories (Created Automatically)

These directories are created when HiveTerminal runs:

```
.hive_memory/                   # Vector database (ChromaDB)
.hive_state/                    # Local state storage (Phase 2)
.hive_backups/                  # File backups (Spec mode)
.hive_logs/                     # Session logs
```

## Excluded from Git

The following are excluded via `.gitignore`:

- Virtual environments (`.venv/`, `.venv-*/`)
- Python cache (`__pycache__/`, `*.pyc`)
- IDE files (`.vscode/`, `.idea/`, `.DS_Store`)
- Test cache (`.pytest_cache/`)
- Runtime directories (`.hive_memory/`, `.hive_state/`, etc.)
- Development files (`test_*.py`, `*_SUMMARY.md`, etc.)

## Documentation Organization

### Root Level
- **README.md**: First thing users see, complete overview

### docs/ Folder
- **INSTALL.md**: Detailed installation (linked from README)
- **UNINSTALL.md**: Uninstallation guide
- **MODEL_GUIDE.md**: Model selection guide
- **STATE_MANAGEMENT_QUICK_START.md**: Feature guide
- **FINAL_SUMMARY_FOR_JUDGES.md**: Judge submission

## Clean Project Principles

1. **Root is clean**: Only essential files at root level
2. **Docs organized**: All documentation in `docs/` folder
3. **No test files**: Test files excluded from distribution
4. **No dev files**: Development summaries and scripts removed
5. **Clear structure**: Easy to navigate and understand
6. **Git-friendly**: Proper `.gitignore` for development files

## For Users

When users clone the repository, they see:
- Clean root directory with README
- Clear installation scripts
- Organized documentation in `docs/`
- Source code in `hiveterminal/`
- No clutter or confusion

## For Judges

Judges can easily find:
- **README.md**: Complete overview and innovation
- **docs/FINAL_SUMMARY_FOR_JUDGES.md**: Detailed submission summary
- **docs/STATE_MANAGEMENT_QUICK_START.md**: Token optimization guide
- Clean, professional project structure

## For Developers

Developers can easily:
- Navigate source code in `hiveterminal/`
- Find documentation in `docs/`
- Understand structure from this file
- Contribute using `CONTRIBUTING.md`

---

**Status**: ✅ Project structure cleaned and organized
