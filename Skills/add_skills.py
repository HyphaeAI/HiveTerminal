import os
from openai import OpenAI  # Use this for Ollama too

# 1. Load the Skill File
def load_skill():
    with open("Skills/Skill_Gemini3Pro.md", "r") as f:
        return f.read()

# 2. Setup Client (Points to your local Ollama)
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Required but ignored
)

# 3. The Agent Loop
system_prompt = load_skill()
messages = [{"role": "system", "content": system_prompt}]

def run_agent(user_input):
    # Add user message
    messages.append({"role": "user", "content": user_input})
    
    # Run Inference
    response = client.chat.completions.create(
        model="qwen2.5-coder:3b",
        messages=messages,
        temperature=0.1,       # LOW temperature is critical for JSON!
        response_format={"type": "json_object"} # Forces valid JSON (New Feature)
    )
    
    return response.choices[0].message.content

# Test it
print(run_agent("Make a directory called 'test_project'"))