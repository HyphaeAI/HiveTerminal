import os
import json
import re
from openai import OpenAI
# Assuming your tools are in a sibling file named 'tools.py'
from .tools import run_tool

# Point to your local Ollama instance
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def load_skill():
    # Dynamically find the SKILL.md file relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Make sure this filename matches your actual skill file
    skill_path = os.path.join(current_dir, "SKILL.md") 
    try:
        with open(skill_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful assistant."

def parse_and_fix_response(response_text):
    """
    Normalizes the model's output into the standard format:
    { "tool_name": "...", "tool_args": {...} }
    """
    # 1. Clean Markdown and stray text
    clean_text = re.sub(r'```json\s*', '', response_text)
    clean_text = re.sub(r'```', '', clean_text).strip()
    
    # 2. Attempt JSON Parse
    try:
        data = json.loads(clean_text)
    except json.JSONDecodeError:
        print(f"❌ JSON Parse Error. Raw Output: {response_text}")
        return None

    # --- NORMALIZATION LAYER (The Fix) ---
    
    # Fix 1: Normalize key names (Model used "name" instead of "tool_name")
    if "name" in data and "tool_name" not in data:
        data["tool_name"] = data.pop("name")
    if "arguments" in data and "tool_args" not in data:
        data["tool_args"] = data.pop("arguments")

    # Fix 2: Handle "list" or "ls" hallucination
    # The model output you shared: "name": "list", "arguments": { "path": "..." }
    if data.get("tool_name") in ["list", "list_files", "ls", "dir"]:
        print(f"⚠️  Normalizing tool '{data['tool_name']}' -> 'execute_terminal'...")
        
        # Extract path or default to current directory
        target_path = data.get("tool_args", {}).get("path", ".")
        
        # Rewrite to correct tool
        data["tool_name"] = "execute_terminal"
        data["tool_args"] = {"command": f"ls -F {target_path}"}

    # Fix 3: Handle "todo" hallucination
    elif data.get("tool_name") == "todo":
         print(f"⚠️  Normalizing tool 'todo' -> 'write_file'...")
         data["tool_name"] = "write_file"
         if "content" not in data.get("tool_args", {}):
             data["tool_args"]["content"] = "# TODO\n"

    return data
def run_local_agent():
    print("🚀 Local Agent Started (Qwen 2.5 Coder 3B)")
    print("Type 'exit' to return to main menu.\n")

    # Load system prompt
    system_prompt = load_skill()
    history = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("\n👤 You (Local): ")
        if user_input.lower() in ["exit", "quit"]:
            break

        history.append({"role": "user", "content": user_input})

        try:
            print("⏳ Thinking...")
            response = client.chat.completions.create(
                model="qwen2.5-coder:3b",
                messages=history,
                temperature=0.1, 
                # Keep JSON mode on, it helps Qwen stick to format
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content
            
            # --- NEW PARSING STEP ---
            # Parse and fix the content BEFORE executing
            action_data = parse_and_fix_response(raw_content)

            if action_data:
                # Pass the CLEANED dictionary to your tool runner
                # (You might need to update run_tool to accept a dict, or convert back to string)
                
                # Option A: If run_tool expects a JSON string:
                clean_json_str = json.dumps(action_data)
                result = run_tool(clean_json_str) 
                
                # Option B: If run_tool can take the dict directly (Better):
                # result = run_tool(action_data)

                print(f"✅ Result: {result}")

                # Update Memory with the CORRECTED action
                history.append({"role": "assistant", "content": json.dumps(action_data)})
                history.append({"role": "user", "content": f"Tool execution result: {result}"})
            else:
                print("⚠️  Model output invalid JSON. Retrying...")

        except Exception as e:
            print(f"❌ Error: {e}")