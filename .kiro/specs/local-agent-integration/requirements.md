# Feature Requirements: Local Brain Mode

## Overview
Document and validate the "Local Brain" mode - a lightweight, privacy-focused operational mode in HiveTerminal that uses a local Ollama model (Qwen 2.5 Coder 3B) with strict JSON-based tool calling. This mode is optimized for 8GB RAM systems and enables completely offline coding assistance.

## Context
The `local_core/` subsystem has been integrated into HiveTerminal's main menu, providing a third operational mode alongside Conversational and Spec-First modes. This mode uses:
- **SKILL.md**: Few-shot prompt manual teaching the local model to output strict JSON
- **tools.py**: Execution layer for parsing JSON and handling subprocess/file operations
- **agent.py**: Orchestration loop connecting to Ollama with conversation history management
- **JSON enforcement**: `response_format={"type": "json_object"}` for stable tool calling on limited RAM

## User Stories

### 1. Mode Selection and Access
**As a** HiveTerminal user  
**I want to** access "Local Brain" mode from the main menu  
**So that** I can work completely offline with privacy-focused local AI

**Acceptance Criteria:**
- 1.1 Main menu displays "Local Brain" option alongside other modes
- 1.2 Selecting Local Brain mode launches the local agent loop
- 1.3 Mode displays clear indicator showing "Local Brain" is active
- 1.4 User can exit back to main menu with 'exit' or 'quit' commands

### 2. JSON-Based Tool Execution
**As a** user in Local Brain mode  
**I want** the agent to execute tools using strict JSON responses  
**So that** I get fast, deterministic tool execution optimized for 8GB RAM

**Acceptance Criteria:**
- 2.1 Agent responds with strict JSON format: `{"tool": "name", "args": {...}, "reasoning": "..."}`
- 2.2 Ollama client enforces `response_format={"type": "json_object"}` for stability
- 2.3 Agent supports three tools: `execute_terminal`, `write_file`, `read_file`
- 2.4 Agent displays reasoning before executing each tool
- 2.5 Agent executes one tool per turn and waits for result before proceeding
- 2.6 Terminal commands include safety checks blocking dangerous operations (`rm -rf /`, `sudo rm`, fork bombs)

### 3. Few-Shot Skill System
**As a** developer  
**I want** the local agent to load few-shot examples from SKILL.md  
**So that** the smaller model learns proper JSON tool calling patterns

**Acceptance Criteria:**
- 3.1 Agent loads skill from `local_core/SKILL.md` (or `Skill_Gemini3Pro.md`) on startup
- 3.2 If skill file not found, agent uses fallback: "You are a helpful assistant."
- 3.3 Skill file path is correctly resolved relative to module location (fix double `local_core/` bug)
- 3.4 Skill content is injected as system message in conversation history
- 3.5 Few-shot examples teach the model to output only JSON (no conversational filler)

### 4. Ollama Integration (8GB RAM Optimized)
**As a** user with 8GB RAM  
**I want** Local Brain mode to use Qwen 2.5 Coder 3B efficiently  
**So that** I can run AI assistance without memory pressure

**Acceptance Criteria:**
- 4.1 Local agent connects to Ollama at `http://localhost:11434/v1`
- 4.2 Default model is `qwen2.5-coder:3b` (optimized for 8GB RAM)
- 4.3 Agent enforces `response_format={"type": "json_object"}` to prevent memory overhead from conversational responses
- 4.4 Agent uses `temperature=0.1` for deterministic, focused responses
- 4.5 OpenAI client library is used for Ollama compatibility

### 5. Error Handling and Safety
**As a** user  
**I want** clear error messages and safety protections  
**So that** I can troubleshoot issues and avoid dangerous operations

**Acceptance Criteria:**
- 5.1 Invalid JSON from model displays: "❌ Error: Invalid JSON from model."
- 5.2 Unknown tool names display: "Error: Unknown tool '{tool_name}'." with available tools
- 5.3 File operation errors show specific exception details
- 5.4 Ollama connection errors provide troubleshooting guidance
- 5.5 Forbidden commands display: "❌ Error: Command blocked for safety."
- 5.6 Safety checks block: `rm -rf /`, `sudo rm`, `:(){ :|:& };:` (fork bomb)
- 5.7 All errors are caught and displayed without crashing the agent loop

### 6. User Experience and Visual Feedback
**As a** user  
**I want** Local Brain mode to provide clear visual feedback  
**So that** I understand what the agent is doing at each step

**Acceptance Criteria:**
- 6.1 Startup message displays: "🚀 Local Agent Started (Qwen 2.5 Coder 3B)"
- 6.2 Exit instructions shown: "Type 'exit' to return to main menu."
- 6.3 User prompt displays: "👤 You (Local): "
- 6.4 Thinking indicator shows: "⏳ Thinking..."
- 6.5 Agent reasoning displays: "🤖 Agent Reasoning: {reasoning}"
- 6.6 Tool execution shows: "⚡ Executing: {command}" or "📝 Writing File: {path}" or "📖 Reading File: {path}"
- 6.7 Success results show: "✅ Result: {result}"
- 6.8 Errors display: "❌ Error: {error_message}"
- 6.9 User can exit with 'exit' or 'quit' commands (case-insensitive)

### 7. Tool Implementation Details
**As a** developer  
**I want** each tool to have clear, predictable behavior  
**So that** the agent can reliably accomplish coding tasks

**Acceptance Criteria:**

**7.1 execute_terminal tool:**
- Accepts `command` argument (string)
- Runs command via `subprocess.run(shell=True, capture_output=True, text=True)`
- Returns stdout if returncode=0, stderr otherwise
- Blocks dangerous commands before execution
- Returns formatted output: "Command Output:\n{output}"

**7.2 write_file tool:**
- Accepts `path` and `content` arguments (strings)
- Opens file in write mode ('w') and writes content
- Returns: "Success: File '{path}' written." on success
- Returns: "Error writing file: {exception}" on failure
- Creates parent directories if needed (implicit via open())

**7.3 read_file tool:**
- Accepts `path` argument (string)
- Checks if file exists with `os.path.exists()`
- Returns file contents if found
- Returns: "Error: File not found." if missing
- Reads entire file content (no line limits)

## Technical Constraints

### Must Have
- Python 3.10+ compatibility
- Modular design: `local_core/` as self-contained subsystem
- No breaking changes to existing Conversational or Spec-First modes
- Ollama must be running and accessible at `http://localhost:11434/v1`
- OpenAI Python client for Ollama compatibility

### Should Have
- Separation of concerns: agent.py (orchestration), tools.py (execution), SKILL.md (prompts)
- Conversation history management for context retention
- Graceful error handling without crashes
- macOS compatibility (primary platform)

### Could Have
- Memory integration (Hive Mind) for local agent
- Custom skill file selection via CLI flag
- Tool execution history/logging
- Windows/Linux compatibility testing

## Out of Scope
- Creating new tools beyond the three existing ones (execute_terminal, write_file, read_file)
- Web-based UI for Local Brain mode
- Multi-turn planning (that's Spec-First Mode's job)
- Integration with Vibe's MCP system
- Model fine-tuning or training
- GPU acceleration

## Dependencies
- **Python Packages:**
  - `openai` - For Ollama client compatibility
  - Standard library: `os`, `subprocess`, `json`
- **External Services:**
  - Ollama running at `http://localhost:11434/v1`
  - Qwen 2.5 Coder 3B model pulled: `ollama pull qwen2.5-coder:3b`
- **System Requirements:**
  - 8GB RAM (minimum for Qwen 2.5 Coder 3B)
  - macOS (primary platform, others untested)

## Success Metrics
- ✅ Local Brain mode is accessible from main menu
- ✅ Agent successfully executes all three tools (execute_terminal, write_file, read_file)
- ✅ JSON enforcement prevents conversational responses
- ✅ Memory usage stays within 8GB RAM limits
- ✅ Error handling provides clear, actionable feedback
- ✅ Safety checks block dangerous commands
- ✅ User can complete basic coding tasks (read code, modify files, run tests)

## Known Issues to Address
1. **Path Bug**: `agent.py` line 10 has double `local_core/` in skill path
   - Current: `skill_path = os.path.join(current_dir, "local_core/Skill_Gemini3Pro.md")`
   - Should be: `skill_path = os.path.join(current_dir, "Skill_Gemini3Pro.md")`
2. **File naming inconsistency**: Documentation mentions `SKILL.md` but code uses `Skill_Gemini3Pro.md`
3. **No parent directory creation**: `write_file` may fail if parent directories don't exist

## Future Enhancements (Not in Current Scope)
1. Memory integration (Hive Mind) for context-aware suggestions
2. Custom skill file selection via `--skill` flag
3. Tool execution logging for debugging
4. Additional tools (search_files, list_directory, git operations)
5. Windows/Linux compatibility testing
6. Integration with HiveTerminal's mode switching system (`/mode` command)
