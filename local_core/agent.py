import os
from openai import OpenAI
from .tools import run_tool

# Point to your local Ollama instance
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

def load_skill():
    # Dynamically find the SKILL.md file relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    skill_path = os.path.join(current_dir, "local_core/Skill_Gemini3Pro.md")
    try:
        with open(skill_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful assistant."

def run_local_agent():
    print("🚀 Local Agent Started (Qwen 2.5 Coder 3B)")
    print("Type 'exit' to return to main menu.\n")

    history = [{"role": "system", "content": load_skill()}]

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
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # Execute Tool
            result = run_tool(content)
            print(f"✅ Result: {result}")

            # Update Memory
            history.append({"role": "assistant", "content": content})
            history.append({"role": "user", "content": f"Tool execution result: {result}"})

        except Exception as e:
            print(f"❌ Error: {e}")