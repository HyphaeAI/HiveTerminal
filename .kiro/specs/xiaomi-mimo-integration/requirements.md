# Feature Requirements: Xiaomi Mimo v2 Flash Integration

## Overview
Integrate Xiaomi's Mimo v2 Flash API into HiveTerminal as a provider option, allowing users to leverage the high-performance 309B parameter MoE model for coding assistance. The integration will use LiteLLM (already in HiveTerminal) to connect to Xiaomi's API.

## Context
- **Model**: Mimo v2 Flash (309B total params, 15B active)
- **API Endpoint**: https://platform.xiaomimimo.com
- **Integration Method**: LiteLLM provider (already used by HiveTerminal)
- **Key Features**: 256K context, #1 on SWE-bench, optimized for coding/reasoning
- **Cost**: Free during beta, significantly cheaper than Claude

## User Stories

### 1. Provider Configuration
**As a** HiveTerminal user  
**I want to** configure Xiaomi Mimo as my LLM provider  
**So that** I can use the high-performance Mimo v2 Flash model

**Acceptance Criteria:**
- 1.1 User can select "Xiaomi Mimo" during onboarding/setup
- 1.2 User is prompted to enter their Xiaomi Mimo API key
- 1.3 API key is stored securely in config (environment variable or keyring)
- 1.4 Configuration is saved to `~/.vibe/config.toml`
- 1.5 User can update API key via `hive --setup`

### 2. Model Selection
**As a** user  
**I want to** select Mimo v2 Flash as my active model  
**So that** I can leverage its coding and reasoning capabilities

**Acceptance Criteria:**
- 2.1 Mimo v2 Flash appears in model selection list
- 2.2 Model is configured with appropriate parameters (temperature, top_p, max_tokens)
- 2.3 Model name is displayed as "mimo-v2-flash" in UI
- 2.4 Provider is shown as "Xiaomi Mimo" in configuration

### 3. API Integration
**As a** developer  
**I want** HiveTerminal to communicate with Xiaomi's API via LiteLLM  
**So that** requests are handled efficiently and reliably

**Acceptance Criteria:**
- 3.1 LiteLLM routes requests to Xiaomi Mimo provider
- 3.2 Model identifier is `xiaomi_mimo/mimo-v2-flash`
- 3.3 API key is passed via `XIAOMI_MIMO_API_KEY` environment variable
- 3.4 Streaming responses are supported
- 3.5 Error handling for API failures (rate limits, auth errors, network issues)

### 4. Default Configuration
**As a** user  
**I want** sensible defaults for Mimo v2 Flash  
**So that** I get optimal performance without manual tuning

**Acceptance Criteria:**
- 4.1 Default temperature: 0.3 (focused, deterministic)
- 4.2 Default top_p: 0.95 (balanced creativity)
- 4.3 Default max_tokens: 4096 (sufficient for most tasks)
- 4.4 Context window: 256K (model's maximum)
- 4.5 Pricing: $0.00 (free during beta)

### 5. Onboarding Experience
**As a** new user  
**I want** clear guidance on setting up Xiaomi Mimo  
**So that** I can start using it quickly

**Acceptance Criteria:**
- 5.1 Setup wizard includes "Xiaomi Mimo" option
- 5.2 Instructions link to https://platform.xiaomimimo.com/#/console/api-keys
- 5.3 API key validation on entry (test request)
- 5.4 Success message confirms connection
- 5.5 Fallback to other providers if setup fails

### 6. Error Handling
**As a** user  
**I want** clear error messages when API issues occur  
**So that** I can troubleshoot problems quickly

**Acceptance Criteria:**
- 6.1 Invalid API key: "Authentication failed. Check your Xiaomi Mimo API key."
- 6.2 Rate limit: "Rate limit exceeded. Please wait and try again."
- 6.3 Network error: "Cannot connect to Xiaomi Mimo API. Check your internet connection."
- 6.4 Model unavailable: "Mimo v2 Flash is currently unavailable. Try another model."
- 6.5 All errors logged for debugging

### 7. Documentation
**As a** user  
**I want** documentation on using Xiaomi Mimo  
**So that** I understand its capabilities and limitations

**Acceptance Criteria:**
- 7.1 README updated with Xiaomi Mimo section
- 7.2 Setup instructions included
- 7.3 Model capabilities documented (256K context, coding focus)
- 7.4 Pricing information (free beta, future costs)
- 7.5 Comparison with other providers

## Technical Constraints

### Must Have
- LiteLLM integration (already present in HiveTerminal)
- Secure API key storage (environment variable or keyring)
- OpenAI-compatible API format (LiteLLM handles this)
- Error handling and retry logic

### Should Have
- Streaming support for real-time responses
- Token usage tracking
- Cost estimation (when pricing is announced)
- Model performance metrics

### Could Have
- Multiple Xiaomi models support (if they release more)
- Custom endpoint configuration
- Proxy support for enterprise users
- Model fine-tuning integration

## Out of Scope
- Self-hosting Mimo v2 Flash (use API only)
- Model training or fine-tuning
- Custom model variants
- Non-LiteLLM integration methods

## Dependencies
- **Existing**: LiteLLM (already in HiveTerminal dependencies)
- **Existing**: HiveTerminal configuration system
- **External**: Xiaomi Mimo API (https://platform.xiaomimimo.com)
- **External**: Valid Xiaomi Mimo API key

## Implementation Details

### Configuration Format (config.toml)
```toml
# Active model
active_model = "mimo-v2-flash"

# Xiaomi Mimo Provider
[[providers]]
name = "xiaomi_mimo"
api_key_env_var = "XIAOMI_MIMO_API_KEY"
backend = "litellm"

# Model Configuration
[[models]]
name = "mimo-v2-flash"
provider = "xiaomi_mimo"
alias = "xiaomi_mimo/mimo-v2-flash"  # LiteLLM format
temperature = 0.3
top_p = 0.95
max_tokens = 4096
context_window = 262144  # 256K
input_price = 0.0  # Free during beta
output_price = 0.0  # Free during beta
```

### Environment Variable
```bash
export XIAOMI_MIMO_API_KEY="your-api-key-here"
```

### LiteLLM Usage
```python
from litellm import completion

response = completion(
    model="xiaomi_mimo/mimo-v2-flash",
    messages=[{"role": "user", "content": "Hello"}],
    api_key=os.environ['XIAOMI_MIMO_API_KEY'],
    temperature=0.3,
    top_p=0.95,
    max_tokens=4096,
    stream=True
)
```

## Success Metrics
- ✅ User can select Xiaomi Mimo during setup
- ✅ API key is stored and loaded correctly
- ✅ Requests successfully reach Xiaomi's API
- ✅ Streaming responses work in HiveTerminal UI
- ✅ Error messages are clear and actionable
- ✅ Documentation is complete and accurate
- ✅ Performance is comparable to other providers

## Known Considerations

### API Availability
- Currently in free beta
- May have rate limits (undocumented)
- Future pricing TBD

### Model Characteristics
- Optimized for coding and reasoning
- 256K context window (very large)
- Fast inference (150 tokens/sec claimed)
- #1 on SWE-bench Verified (73.4%)

### Integration Points
1. `hiveterminal/core/config.py` - Add Xiaomi provider config
2. `vibe/setup/onboarding.py` - Add to provider selection
3. `vibe/core/config.py` - Ensure LiteLLM handles xiaomi_mimo prefix
4. `README.md` - Add documentation

## Future Enhancements (Not in Current Scope)
1. Support for additional Xiaomi models (if released)
2. Advanced configuration (custom endpoints, proxies)
3. Performance benchmarking vs other providers
4. Cost tracking when pricing is announced
5. Model comparison tool
6. Automatic provider selection based on task type

---

**Status**: Ready for implementation
**Priority**: High (user requested)
**Estimated Effort**: Small (LiteLLM already integrated)
