# State Management Tool

Use this tool to store and retrieve working state locally, reducing token usage by avoiding chat history bloat.

## When to Use

**Use state management for:**
- Todo lists, task queues, or work items
- File paths, directory structures, or project information
- Multi-step workflow tracking
- JSON objects, configurations, or data structures
- Any data that needs to persist across turns

**Benefits:**
- Reduces token usage (state is injected only when needed, not full history)
- Persists across conversation turns
- Survives session restarts
- Keeps chat history clean and focused

## Operations

### Set State
Store a value with a key:
```
state(operation="set", key="todos", value=["task1", "task2"], description="Current todo list")
```

### Get State
Retrieve a stored value:
```
state(operation="get", key="todos")
```

### List State
See all stored keys:
```
state(operation="list")
```

### Delete State
Remove a specific key:
```
state(operation="delete", key="todos")
```

### Clear State
Remove all state:
```
state(operation="clear")
```

## Best Practices

1. **Use descriptive keys**: `current_todos`, `project_files`, `workflow_step`
2. **Add descriptions**: Help future you understand what the state represents
3. **Store structured data**: Use JSON objects/arrays for complex data
4. **Clean up**: Delete state when tasks are complete
5. **Check state first**: Use `list` to see what's already stored

## Examples

### Todo List Management
```python
# Store todos
state(operation="set", key="todos", value=[
    {"id": 1, "task": "Fix bug", "done": false},
    {"id": 2, "task": "Write tests", "done": false}
], description="Project todo list")

# Later, retrieve and update
todos = state(operation="get", key="todos")
# ... modify todos ...
state(operation="set", key="todos", value=updated_todos)
```

### File Tracking
```python
# Remember files being worked on
state(operation="set", key="current_files", value={
    "main": "src/main.py",
    "test": "tests/test_main.py",
    "config": "config.yaml"
}, description="Files in current task")
```

### Workflow State
```python
# Track multi-step workflow
state(operation="set", key="workflow", value={
    "step": 2,
    "total_steps": 5,
    "completed": ["analyze", "design"],
    "next": "implement"
}, description="Current workflow progress")
```

## State Injection

State is automatically injected into your prompts, so you don't need to ask "what were the todos again?" - they're always available in the context.

## Token Savings

**Without state management:**
- Turn 1: Store todos in chat (100 tokens)
- Turn 5: Full history including todos (500 tokens)
- Turn 10: Full history including todos (1000 tokens)

**With state management:**
- Turn 1: Store todos in state (50 tokens)
- Turn 5: State injected (50 tokens)
- Turn 10: State injected (50 tokens)

**Savings: 80-95% for long sessions!**
