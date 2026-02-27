# AI Model Selection Guide

## Quick Recommendations

### 🏆 Best Choice (Recommended)
```bash
ollama pull qwen2.5-coder:7b
```
- **Size**: 4.7GB download
- **RAM**: 8GB+ required
- **Tool Calling**: ✅ Excellent
- **Best for**: Production use, complex coding tasks, reliable tool execution

### ⚡ Fast Alternative
```bash
ollama pull deepseek-coder:6.7b
```
- **Size**: 3.8GB download
- **RAM**: 8GB+ required
- **Tool Calling**: ✅ Excellent
- **Best for**: Fast responses, coding tasks, good balance

### 🔬 Testing/Development
```bash
ollama pull qwen2.5:3b
```
- **Size**: 1.9GB download
- **RAM**: 4GB+ required
- **Tool Calling**: ⚠️ Limited (may have issues)
- **Best for**: Testing, simple tasks, resource-constrained systems

### 🚀 Minimal (Not Recommended)
```bash
ollama pull qwen2.5-coder:1.5b
```
- **Size**: 986MB download
- **RAM**: 2GB+ required
- **Tool Calling**: ❌ Poor (frequent issues)
- **Best for**: Quick tests only, not for actual work

---

## Detailed Comparison

### Performance Metrics

| Model | Parameters | Download | RAM | Speed | Tool Calling | Code Quality |
|-------|-----------|----------|-----|-------|--------------|--------------|
| qwen2.5-coder:7b | 7B | 4.7GB | 8GB+ | Medium | ✅ Excellent | ⭐⭐⭐⭐⭐ |
| deepseek-coder:6.7b | 6.7B | 3.8GB | 8GB+ | Fast | ✅ Excellent | ⭐⭐⭐⭐⭐ |
| qwen2.5:3b | 3B | 1.9GB | 4GB+ | Fast | ⚠️ Limited | ⭐⭐⭐ |
| qwen2.5-coder:1.5b | 1.5B | 986MB | 2GB+ | Very Fast | ❌ Poor | ⭐⭐ |

### Tool Calling Capability

**What is Tool Calling?**
HiveTerminal uses "tools" to interact with your system:
- Read/write files
- Execute bash commands
- Search code
- Manage todos
- And more...

**Why Model Size Matters:**
- **7B+ models**: Understand when and how to use tools correctly
- **3B models**: Sometimes confuse tool usage, may output raw JSON
- **1.5B models**: Frequently fail at tool calling, output malformed responses

### Common Issues by Model Size

#### 7B Models (qwen2.5-coder:7b, deepseek-coder:6.7b)
✅ **No issues** - Works as expected
- Proper tool execution
- Natural language responses
- Understands context

#### 3B Models (qwen2.5:3b)
⚠️ **Occasional issues**:
- May output raw JSON for simple queries
- Sometimes calls tools inappropriately
- Can get confused with complex instructions

**Example Issue:**
```
You: hi
Model: {"name": "ask_user_question", "arguments": {...}}
```
Instead of just saying "Hello!"

#### 1.5B Models (qwen2.5-coder:1.5b)
❌ **Frequent issues**:
- Regularly outputs raw JSON instead of responses
- Calls tools when it shouldn't
- Struggles with multi-step tasks
- Poor code quality

**Not recommended for actual work.**

---

## Installation Commands

### Install Ollama First

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Or download from:** https://ollama.ai

### Download Your Chosen Model

```bash
# Best choice (recommended)
ollama pull qwen2.5-coder:7b

# Fast alternative
ollama pull deepseek-coder:6.7b

# For testing
ollama pull qwen2.5:3b

# Minimal (not recommended)
ollama pull qwen2.5-coder:1.5b
```

### Verify Installation

```bash
# List installed models
ollama list

# Test a model
ollama run qwen2.5-coder:7b "Hello, write a Python hello world"
```

---

## Switching Models

You can switch models anytime:

```bash
# Run setup again
hive --setup

# Select Ollama
# Enter new model name (e.g., "deepseek-coder:6.7b")
```

Or manually edit `~/.vibe/config.toml`:
```toml
active_model = "qwen2.5-coder:7b"

[[models]]
name = "qwen2.5-coder:7b"
provider = "ollama"
alias = "qwen2.5-coder:7b"
temperature = 0.2
input_price = 0.0
output_price = 0.0
```

---

## System Requirements

### Minimum Requirements
- **CPU**: Modern multi-core processor
- **RAM**: 2GB+ (for 1.5B models)
- **Disk**: 3GB+ free space
- **OS**: macOS or Linux

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+ (for 7B models)
- **Disk**: 10GB+ free space
- **OS**: macOS or Linux with recent kernel

### Optimal Setup
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Disk**: SSD with 20GB+ free space
- **GPU**: Optional (Ollama can use GPU acceleration)

---

## Performance Tips

### Speed Up Inference

1. **Use GPU acceleration** (if available):
   ```bash
   # Ollama automatically uses GPU if available
   # Check with: ollama ps
   ```

2. **Reduce context size**:
   - Edit `~/.vibe/config.toml`
   - Lower `max_chars` in `[project_context]`

3. **Use smaller models for simple tasks**:
   - 3B models are 2-3x faster than 7B
   - Good for quick edits and simple queries

### Improve Quality

1. **Use larger models** (7B+)
2. **Lower temperature** (0.1-0.3 for coding)
3. **Provide clear, specific prompts**
4. **Use Spec Mode** for complex tasks

---

## Troubleshooting

### Model outputs raw JSON

**Cause**: Model too small for tool calling

**Solution**: Upgrade to 7B model:
```bash
ollama pull qwen2.5-coder:7b
hive --setup  # Select new model
```

### Model is too slow

**Cause**: Model too large for your system

**Solution**: Try smaller model:
```bash
ollama pull qwen2.5:3b
hive --setup  # Select new model
```

### Out of memory errors

**Cause**: Not enough RAM

**Solutions**:
1. Close other applications
2. Use smaller model (3B instead of 7B)
3. Upgrade RAM

### Model not found (404 error)

**Cause**: Model name mismatch

**Solution**: Check exact name:
```bash
ollama list  # See installed models
hive --setup  # Enter exact name with tag
```

---

## Other Models

### Experimental Models

You can try other Ollama models:

```bash
# Code-focused models
ollama pull codellama:7b
ollama pull starcoder2:7b
ollama pull phind-codellama:34b  # Needs 32GB+ RAM

# General models
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull gemma2:9b
```

**Note**: Not all models work well with tool calling. The recommended models have been tested with HiveTerminal.

### Cloud Alternatives

If local models don't work for you, HiveTerminal also supports:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- OpenRouter (access to many models)
- Google AI Studio
- Groq
- Hugging Face

Run `hive --setup` and select your preferred provider.

---

## Summary

**For most users:**
```bash
ollama pull qwen2.5-coder:7b
```

**For fast systems:**
```bash
ollama pull deepseek-coder:6.7b
```

**For testing only:**
```bash
ollama pull qwen2.5:3b
```

**Avoid for production:**
```bash
# Don't use 1.5B models for actual work
ollama pull qwen2.5-coder:1.5b
```

Choose based on your system resources and use case. When in doubt, go with the 7B model! 🐝
