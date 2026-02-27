# State Management Quick Start Guide

## What Is It?
Local state management allows HiveTerminal's AI to store working data on your machine instead of in chat history, reducing token usage by up to 98%.

## How to Use

### 1. Start HiveTerminal
```bash
hive
```

### 2. Ask the AI to Store Data
```
Store a todo list with these tasks: implement auth, add tests, update docs
```

The AI will automatically use the `state_tool` to store your data:
```python
state_tool(operation="set", key="todos", value=["implement auth", "add tests", "update docs"])
```

### 3. Data is Automatically Available
In future messages, the AI can see your stored data without you repeating it:
```
What's on my todo list?
```

The AI sees:
```
## Current Working State
- **todos**: ["implement auth", "add tests", "update docs"]

---

What's on my todo list?
```

### 4. State Persists Across Sessions
Your state is saved to `.hive_state/` and persists even if you restart HiveTerminal.

## Common Use Cases

### Todo Lists
```
Create a todo list for this project
Mark the first task as done
What's left on my todo list?
```

### Multi-Step Tasks
```
I need to refactor the auth system across 5 files
[AI stores progress in state]
Continue where we left off
[AI knows exactly where it was]
```

### Code Analysis
```
Find all TODO comments in the codebase
[AI stores results in state]
Show me the TODOs in main.py
[AI retrieves from state, no re-scanning]
```

### File Tracking
```
I'm working on these files: auth.py, user.py, session.py
[AI stores file list]
What files am I working on?
[AI retrieves from state]
```

## State Tool Operations

The AI can use these operations (you don't need to know the syntax):

- **set**: Store data
- **get**: Retrieve data
- **delete**: Remove data
- **list**: Show all stored keys
- **clear**: Remove all data

## Configuration

### Adjust History Window
Edit `.hive_config.toml`:
```toml
max_conversation_turns = 5  # Keep last 5 turns (default)
```

Lower = more token savings, less context
Higher = more context, higher token usage

### Where State is Stored
- **Location**: `.hive_state/` directory
- **Format**: JSON files (one per session)
- **Persistence**: Survives restarts

## Token Savings

### Example: 20-Turn Todo List Session
- **Without state**: 200,000 tokens ($6.00 at GPT-4 pricing)
- **With state**: 4,000 tokens ($0.12 at GPT-4 pricing)
- **Savings**: 98% ($5.88 saved)

### Why It Works
1. **Sliding window**: Only last 5 turns in history (Phase 1)
2. **Local storage**: Data stored locally, not in history (Phase 2)
3. **Auto-injection**: State injected into context when needed
4. **Persistence**: State survives across sessions

## Troubleshooting

### "state_tool not found"
1. Check `.hive_config.toml` has: `tool_paths = ["./hiveterminal/tools"]`
2. Restart HiveTerminal: `hive`

### State not persisting
1. Check `.hive_state/` directory exists
2. Verify permissions: `ls -la .hive_state/`

### Too much/little context
Adjust `max_conversation_turns` in `.hive_config.toml`:
- **3**: Minimal context, maximum savings
- **5**: Balanced (default)
- **10**: More context, less savings

## Best Practices

### DO:
- ✅ Store todo lists, file paths, and work items in state
- ✅ Use state for multi-step tasks that span multiple turns
- ✅ Let the AI manage state automatically
- ✅ Trust that state persists across sessions

### DON'T:
- ❌ Manually manage state (let the AI do it)
- ❌ Repeat information the AI has in state
- ❌ Worry about token usage (state handles it)
- ❌ Clear state unless starting fresh

## Testing

### Verify State Tool Works
```bash
hive
```

Then:
```
Use state_tool to store a test value, then retrieve it
```

Expected: AI successfully stores and retrieves the value.

### Check State Files
```bash
ls -la .hive_state/
cat .hive_state/*.json
```

You should see JSON files with your stored state.

## Summary

State management is automatic and transparent:
1. AI stores data when needed
2. State is injected into context automatically
3. You save 98% on tokens
4. Everything persists across sessions

Just use HiveTerminal normally - the AI will handle state management for you!

---

**Need Help?**
- Check `PHASE_2_COMPLETE.md` for detailed documentation
- Run `python test_state_management.py` to verify installation
- Review `.hive_state/` directory for stored state
