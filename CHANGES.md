# OpenSwarm — Local Models & Alternative Providers Support

## Summary

This update adds comprehensive support for running OpenSwarm with **local models** (Ollama, llama.cpp) and **alternative API providers** (DeepSeek, OpenRouter), in addition to the existing OpenAI, Anthropic, and Google support.

---

## Files Created

### 1. `QWEN.md` — Qwen Coder Setup Guide (444 lines)
Comprehensive documentation for Qwen Coder including:
- Architecture overview
- Model configuration system
- Tool development patterns
- Local model setup instructions (Ollama, llama.cpp)
- Alternative provider configuration (DeepSeek, OpenRouter)
- Common modification patterns
- Testing & debugging guide

### 2. `LOCAL_MODELS.md` — Quick Reference Guide (391 lines)
Practical quick-start guide for:
- Ollama installation and setup
- llama.cpp installation and setup
- DeepSeek API configuration
- OpenRouter configuration
- Model recommendations by use case
- Troubleshooting common issues
- Performance optimization tips

### 3. `shared_tools/providers.py` — Provider Detection Module (416 lines)
Utility module providing:
- `get_provider_type()` - Detect provider from model string
- `is_local_model()` - Check if model runs locally
- `is_api_provider()` - Check if model needs API key
- `get_required_api_key()` - Get env var name for API key
- `check_provider_available()` - Verify provider configuration
- `get_model_display_name()` - User-friendly model names
- `list_available_providers()` - List all providers with status
- `get_provider_examples()` - Example model strings per provider
- `format_setup_instructions()` - Markdown setup guides
- Convenience functions: `ollama_available()`, `deepseek_available()`, `openrouter_available()`

---

## Files Modified

### 1. `.env.example`
Added new environment variable sections:
```bash
# ── Local & Alternative Providers ─────────────

# Ollama — for running local models (no API key needed, just set DEFAULT_MODEL)
# Example: DEFAULT_MODEL=litellm/ollama/qwen2.5:72b
# Make sure Ollama is running: ollama serve

# llama.cpp — for running local GGUF models (no API key needed)
# Example: DEFAULT_MODEL=litellm/llamacpp/path/to/model.gguf
# Make sure llama.cpp server is running with the model loaded

# DeepSeek — set this if using DeepSeek models via their API.
DEEPSEEK_API_KEY=

# OpenRouter — set this to access 100+ models through OpenRouter.
OPENROUTER_API_KEY=
```

Updated model selection examples to include:
- Ollama examples
- DeepSeek examples
- OpenRouter examples

### 2. `config.py`
Enhanced with new functions:
- Added imports from `shared_tools.providers`
- `get_configured_provider()` - Get current provider type
- `is_using_local_model()` - Check if using local model
- Updated docstrings to mention new providers
- Updated `_resolve()` to handle local models via LiteLLM

### 3. `shared_tools/__init__.py`
Exported all provider utility functions for easy access across the codebase.

### 4. `README.md`
Updated "API Keys & Setup" section to include:
- Local models as a free alternative (no API key needed)
- Ollama setup instructions
- llama.cpp setup instructions
- DeepSeek API information
- OpenRouter information

### 5. `AGENTS.md`
Updated customization guide to:
- Mention Qwen Coder alongside other coding assistants
- Highlight local model support
- Add references to new documentation files (QWEN.md, LOCAL_MODELS.md)
- Document local models and alternative providers in conventions

---

## Supported Providers

### Local Models (No API Key Required)

| Provider | Format | Example |
|----------|--------|---------|
| **Ollama** | `litellm/ollama/{model}` | `litellm/ollama/qwen2.5:72b` |
| **llama.cpp** | `litellm/llamacpp/{path}` | `litellm/llamacpp/path/to/model.gguf` |

### API Providers

| Provider | Env Variable | Format | Example |
|----------|-------------|--------|---------|
| **DeepSeek** | `DEEPSEEK_API_KEY` | `litellm/deepseek/{model}` | `litellm/deepseek/deepseek-chat` |
| **OpenRouter** | `OPENROUTER_API_KEY` | `litellm/openrouter/{model}` | `litellm/openrouter/meta-llama/llama-3-70b-instruct` |
| **Anthropic** | `ANTHROPIC_API_KEY` | `litellm/anthropic/{model}` | `litellm/anthropic/claude-sonnet-4-6` |
| **Google** | `GOOGLE_API_KEY` | `litellm/gemini/{model}` | `litellm/gemini/gemini-3-flash` |
| **OpenAI** | `OPENAI_API_KEY` | `{model}` (native) | `gpt-5.2` |

---

## Usage Examples

### Quick Start with Ollama

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull a model
ollama pull qwen2.5:72b

# 3. Configure OpenSwarm
echo "DEFAULT_MODEL=litellm/ollama/qwen2.5:72b" > .env

# 4. Start Ollama and run
ollama serve &
python swarm.py
```

### Using Provider Utilities in Code

```python
from shared_tools.providers import (
    get_provider_type,
    is_local_model,
    check_provider_available,
    list_available_providers,
)

# Check provider type
provider = get_provider_type("litellm/ollama/qwen2.5:72b")
# Returns: "ollama"

# Check if local
is_local = is_local_model("litellm/ollama/qwen2.5:72b")
# Returns: True

# Check availability
available, message = check_provider_available("litellm/deepseek/deepseek-chat")
# Returns: (False, "Missing DEEPSEEK_API_KEY in environment")

# List all providers
providers = list_available_providers()
for name, info in providers.items():
    print(f"{info['name']}: {'✓' if info['configured'] else '✗'}")
```

### Configuration Helper Functions

```python
from config import get_configured_provider, is_using_local_model

# Get current provider
provider = get_configured_provider()

# Check if using local model
if is_using_local_model():
    print("Running on local hardware - no API costs!")
```

---

## Recommended Models

### For General Tasks
- **Ollama**: `qwen2.5:72b` (best), `llama3.1:70b` (balanced)
- **API**: `deepseek/deepseek-chat` (cost-effective)

### For Coding
- **Ollama**: `qwen2.5-coder:32b`, `deepseek-coder:33b`
- **API**: `deepseek/deepseek-coder`

### For Low VRAM (<16GB)
- **Ollama**: `qwen2.5:7b`, `qwen2.5:14b`
- **Quantized**: `qwen2.5:72b-q4_K_M`

---

## Testing Performed

Verified provider detection for all supported providers:
```
✓ gpt-5.2                                            -> openai       (local=False)
✓ litellm/ollama/qwen2.5:72b                         -> ollama       (local=True)
✓ litellm/llamacpp/path/to/model.gguf                -> llamacpp     (local=True)
✓ litellm/deepseek/deepseek-chat                     -> deepseek     (local=False)
✓ litellm/openrouter/meta-llama/llama-3-70b-instruct -> openrouter   (local=False)
✓ litellm/anthropic/claude-sonnet-4-6                -> anthropic    (local=False)
✓ litellm/gemini/gemini-3-flash                      -> google       (local=False)
```

All tests passed ✓

---

## Next Steps for Users

1. **Choose a provider**: Local (free) or API (paid)
2. **Follow setup guide**: See `LOCAL_MODELS.md` for detailed instructions
3. **Configure .env**: Set `DEFAULT_MODEL` and any required API keys
4. **Run OpenSwarm**: `python swarm.py`

For developers wanting to extend support:
- See `QWEN.md` for architecture details
- See `shared_tools/providers.py` for implementation patterns
- See `AGENTS.md` for agent customization guide

---

## Backwards Compatibility

✅ All existing configurations continue to work unchanged:
- OpenAI models work as before
- Anthropic models work as before  
- Google models work as before
- Existing `.env` files remain valid

New features are additive only - no breaking changes.
