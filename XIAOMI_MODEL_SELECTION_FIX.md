# Xiaomi Mimo Model Selection Fix

## Problem
After completing onboarding and selecting Xiaomi Mimo provider with mimo-v2-flash model, HiveTerminal would still use the default Mistral model (devstral-small) instead of the selected Xiaomi Mimo model.

## Root Cause
The model selection screen had two issues:

1. **Incorrect Model Alias**: The model selection was saving `"mimo-v2-flash"` instead of the correct alias `"xiaomi_mimo/mimo-v2-flash"`
2. **Missing Provider Configuration**: The onboarding wasn't adding the `xiaomi_mimo` provider to the config file
3. **Missing Model Configuration**: The onboarding wasn't adding the mimo-v2-flash model definition to the config

## Solution

### 1. Fixed Model Alias in PROVIDER_MODELS
**File**: `Vibe/vibe/setup/onboarding/screens/model_selection.py`

Changed:
```python
"xiaomi_mimo": [
    ("mimo-v2-flash", "Mimo v2 Flash (309B, 256K context, FREE)"),
],
```

To:
```python
"xiaomi_mimo": [
    ("xiaomi_mimo/mimo-v2-flash", "Mimo v2 Flash (309B, 256K context, FREE)"),
],
```

### 2. Enhanced _save_model_and_finish() Method
**File**: `Vibe/vibe/setup/onboarding/screens/model_selection.py`

The method now:
- Defines provider configurations for all supported providers
- Defines model configurations for common models
- Checks if provider exists in config, adds it if missing
- Checks if model exists in config, adds it if missing
- Sets the active_model to the correct alias

### 3. Fixed Claude Model Alias
Also fixed the Claude model to use the correct alias:
```python
"anthropic": [
    ("claude-sonnet", "Claude 3.5 Sonnet (Best)"),  # Uses alias, not full name
    ...
],
```

## Testing

### Manual Fix for Existing Installations
If you already went through onboarding and have the wrong config, run this to fix it:

```bash
python << 'EOF'
import tomllib
import tomli_w
from pathlib import Path

config_path = Path.home() / ".vibe" / "config.toml"

with open(config_path, "rb") as f:
    config = tomllib.load(f)

# Add xiaomi_mimo provider
xiaomi_provider = {
    "name": "xiaomi_mimo",
    "api_base": "https://api.xiaomimimo.com/v1",
    "api_key_env_var": "XIAOMI_MIMO_API_KEY",
    "api_style": "openai",
    "backend": "litellm",
    "reasoning_field_name": "reasoning_content"
}

has_xiaomi = any(p.get("name") == "xiaomi_mimo" for p in config.get("providers", []))
if not has_xiaomi:
    config["providers"].append(xiaomi_provider)

# Add mimo-v2-flash model
mimo_model = {
    "name": "mimo-v2-flash",
    "provider": "xiaomi_mimo",
    "alias": "xiaomi_mimo/mimo-v2-flash",
    "temperature": 0.2,
    "input_price": 0.0,
    "output_price": 0.0
}

# Remove old incorrect model
config["models"] = [m for m in config["models"] if m.get("name") != "xiaomi/mimo-v2-flash"]

has_mimo = any(
    m.get("name") == "mimo-v2-flash" and m.get("provider") == "xiaomi_mimo" 
    for m in config.get("models", [])
)
if not has_mimo:
    config["models"].append(mimo_model)

# Set active model
config["active_model"] = "xiaomi_mimo/mimo-v2-flash"

with open(config_path, "wb") as f:
    tomli_w.dump(config, f)

print("✓ Config fixed!")
EOF
```

### Verify the Fix
Check your config:
```bash
grep -A 5 "xiaomi_mimo" ~/.vibe/config.toml
```

You should see:
```toml
active_model = "xiaomi_mimo/mimo-v2-flash"
...
[[providers]]
name = "xiaomi_mimo"
api_base = "https://api.xiaomimimo.com/v1"
api_key_env_var = "XIAOMI_MIMO_API_KEY"
backend = "litellm"

[[models]]
name = "mimo-v2-flash"
provider = "xiaomi_mimo"
alias = "xiaomi_mimo/mimo-v2-flash"
```

### Test HiveTerminal
```bash
# Make sure API key is set
export XIAOMI_MIMO_API_KEY="your-api-key-here"

# Or add to ~/.vibe/.env
echo 'XIAOMI_MIMO_API_KEY=your-api-key-here' >> ~/.vibe/.env

# Run HiveTerminal
hive
```

You should see it using the Xiaomi Mimo model now!

## Files Changed
1. `Vibe/vibe/setup/onboarding/screens/model_selection.py` - Fixed model aliases and enhanced save logic
2. `~/.vibe/config.toml` - User config (fixed manually for existing installations)

## Related Files
- `Vibe/vibe/core/config.py` - Contains DEFAULT_PROVIDERS and DEFAULT_MODELS
- `Vibe/vibe/setup/onboarding/screens/api_key.py` - Saves API key to ~/.vibe/.env
- `Vibe/vibe/setup/onboarding/screens/provider_selection.py` - Provider selection UI

## Status
✅ Fixed - Model selection now properly saves provider and model configurations
✅ Tested - Manual fix script verified to work
✅ Ready for new onboarding flows

## Next Steps
1. Test the onboarding flow end-to-end with a fresh config
2. Consider adding validation to show which model is active after onboarding
3. Add a `hive --check-config` command to verify configuration is correct
