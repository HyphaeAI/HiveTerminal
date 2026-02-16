import json
import subprocess
import os

def run_tool(json_string):
    """Parses JSON from the LLM and executes the corresponding tool."""
    try:
        action = json.loads(json_string)
        tool_name = action.get("tool")
        args = action.get("args", {})
        reasoning = action.get("reasoning", "No reasoning provided.")

        print(f"\n🤖 Agent Reasoning: {reasoning}")

        if tool_name == "execute_terminal":
            command = args.get("command")
            print(f"⚡ Executing: {command}")
            
            # Safety Check
            forbidden = ["rm -rf /", "sudo rm", ":(){ :|:& };:"]
            if any(bad in command for bad in forbidden):
                return "❌ Error: Command blocked for safety."

            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.returncode == 0 else result.stderr
            return f"Command Output:\n{output}"

        elif tool_name == "write_file":
            path = args.get("path")
            content = args.get("content")
            print(f"📝 Writing File: {path}")
            try:
                with open(path, "w") as f:
                    f.write(content)
                return f"Success: File '{path}' written."
            except Exception as e:
                return f"Error writing file: {e}"

        elif tool_name == "read_file":
            path = args.get("path")
            print(f"📖 Reading File: {path}")
            if os.path.exists(path):
                with open(path, "r") as f:
                    return f.read()
            return "Error: File not found."

        else:
            return f"Error: Unknown tool '{tool_name}'."

    except json.JSONDecodeError:
        return "❌ Error: Invalid JSON from model."
    except Exception as e:
        return f"❌ System Error: {e}"