"""Provider detection and utilities for local/alternative model providers.

This module adds support for:
- Ollama (local models)
- llama.cpp (local GGUF models)
- DeepSeek API
- OpenRouter (multi-provider API)

Usage:
    from shared_tools.providers import get_provider_type, is_local_model
    
    model = "litellm/ollama/qwen2.5:72b"
    provider = get_provider_type(model)  # Returns "ollama"
    
    if is_local_model(model):
        print("Running locally - no API key needed")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv


# Provider type aliases
ProviderType = Literal[
    "openai",
    "anthropic", 
    "google",
    "ollama",
    "llamacpp",
    "deepseek",
    "openrouter",
    "litellm",
    "unknown"
]


def _refresh_runtime_env() -> None:
    """Reload environment variables from .env file."""
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=True)
    load_dotenv(override=True)


def get_provider_type(model: str | None) -> ProviderType:
    """Determine provider type from model string.
    
    Args:
        model: Model identifier (e.g., "gpt-5.2", "litellm/ollama/qwen2.5:72b")
        
    Returns:
        Provider type string
        
    Examples:
        >>> get_provider_type("gpt-5.2")
        'openai'
        >>> get_provider_type("litellm/ollama/qwen2.5:72b")
        'ollama'
        >>> get_provider_type("litellm/deepseek/deepseek-chat")
        'deepseek'
        >>> get_provider_type("litellm/openrouter/meta-llama/llama-3-70b-instruct")
        'openrouter'
    """
    _refresh_runtime_env()
    
    if not model:
        return "unknown"
    
    # OpenAI-native models have no slashes
    if "/" not in model:
        return "openai"
    
    # Remove litellm/ prefix if present
    bare = model[len("litellm/"):] if model.startswith("litellm/") else model
    
    # Extract provider from first segment
    parts = bare.split("/", 1)
    provider = parts[0].lower() if parts else ""
    
    # Map to known provider types
    provider_map = {
        "ollama": "ollama",
        "ollama_chat": "ollama",
        "llamacpp": "llamacpp",
        "deepseek": "deepseek",
        "openrouter": "openrouter",
        "anthropic": "anthropic",
        "google": "google",
        "gemini": "google",
        "openai": "openai",
    }
    
    return provider_map.get(provider, "litellm" if provider else "unknown")


def is_local_model(model: str | None) -> bool:
    """Check if model runs locally (no API key required).
    
    Args:
        model: Model identifier
        
    Returns:
        True if model is local (Ollama or llama.cpp)
    """
    provider = get_provider_type(model)
    return provider in ("ollama", "llamacpp")


def is_api_provider(model: str | None) -> bool:
    """Check if model requires an external API key.
    
    Args:
        model: Model identifier
        
    Returns:
        True if model needs API key
    """
    provider = get_provider_type(model)
    return provider in ("deepseek", "openrouter", "anthropic", "google")


def get_required_api_key(model: str | None) -> str | None:
    """Get the environment variable name for required API key.
    
    Args:
        model: Model identifier
        
    Returns:
        Environment variable name or None if no key needed
        
    Examples:
        >>> get_required_api_key("litellm/deepseek/deepseek-chat")
        'DEEPSEEK_API_KEY'
        >>> get_required_api_key("litellm/ollama/qwen2.5:72b")
        None
    """
    provider = get_provider_type(model)
    
    key_map = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "openai": "OPENAI_API_KEY",
    }
    
    if is_local_model(model):
        return None
    
    return key_map.get(provider)


def check_provider_available(model: str | None) -> tuple[bool, str]:
    """Check if a model's provider is available/configured.
    
    Args:
        model: Model identifier
        
    Returns:
        Tuple of (is_available, message)
    """
    _refresh_runtime_env()
    
    if not model:
        return False, "No model specified"
    
    provider = get_provider_type(model)
    
    # Local models just need the service running
    if provider == "ollama":
        # We can't easily check if Ollama is running without making a request
        # Return optimistic result with guidance
        return True, "Ollama detected - ensure 'ollama serve' is running"
    
    if provider == "llamacpp":
        return True, "llama.cpp detected - ensure server is running with model loaded"
    
    # API providers need keys
    required_key = get_required_api_key(model)
    if required_key:
        if os.getenv(required_key):
            return True, f"{provider} configured with API key"
        else:
            return False, f"Missing {required_key} in environment"
    
    # Default case
    return True, f"Provider {provider} available"


def get_model_display_name(model: str | None) -> str:
    """Get a user-friendly display name for a model.
    
    Args:
        model: Model identifier
        
    Returns:
        Display name
    """
    if not model:
        return "Unknown Model"
    
    provider = get_provider_type(model)
    
    if is_local_model(model):
        # Extract model name from Ollama/llama.cpp strings
        bare = model.replace("litellm/", "").replace(f"{provider}/", "")
        return f"{bare} (Local)"
    
    # For API models, show full path
    return model


def list_available_providers() -> dict[ProviderType, dict]:
    """List all supported providers with their status.
    
    Returns:
        Dictionary of provider info
    """
    _refresh_runtime_env()
    
    return {
        "openai": {
            "name": "OpenAI",
            "key_var": "OPENAI_API_KEY",
            "configured": bool(os.getenv("OPENAI_API_KEY")),
            "local": False,
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "key_var": "ANTHROPIC_API_KEY",
            "configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "local": False,
        },
        "google": {
            "name": "Google Gemini",
            "key_var": "GOOGLE_API_KEY",
            "configured": bool(os.getenv("GOOGLE_API_KEY")),
            "local": False,
        },
        "ollama": {
            "name": "Ollama (Local)",
            "key_var": None,
            "configured": True,  # Always "configured" - just needs service running
            "local": True,
        },
        "llamacpp": {
            "name": "llama.cpp (Local)",
            "key_var": None,
            "configured": True,
            "local": True,
        },
        "deepseek": {
            "name": "DeepSeek",
            "key_var": "DEEPSEEK_API_KEY",
            "configured": bool(os.getenv("DEEPSEEK_API_KEY")),
            "local": False,
        },
        "openrouter": {
            "name": "OpenRouter",
            "key_var": "OPENROUTER_API_KEY",
            "configured": bool(os.getenv("OPENROUTER_API_KEY")),
            "local": False,
        },
    }


def get_provider_examples() -> dict[str, list[str]]:
    """Get example model strings for each provider.
    
    Returns:
        Dictionary mapping provider names to example model identifiers
    """
    return {
        "openai": [
            "gpt-5.2",
            "gpt-4.1",
            "o3",
            "o4-mini",
        ],
        "anthropic": [
            "litellm/anthropic/claude-sonnet-4-6",
            "litellm/anthropic/claude-3-5-sonnet-20241022",
        ],
        "google": [
            "litellm/gemini/gemini-3-flash",
            "litellm/gemini/gemini-2.5-flash-image",
            "litellm/gemini/gemini-3-pro-image-preview",
        ],
        "ollama": [
            "litellm/ollama/qwen2.5:72b",
            "litellm/ollama/qwen2.5-coder:32b",
            "litellm/ollama/llama3.1:70b",
            "litellm/ollama/deepseek-coder:33b",
            "litellm/ollama/mixtral:8x7b",
        ],
        "llamacpp": [
            "litellm/llamacpp/path/to/model.gguf",
        ],
        "deepseek": [
            "litellm/deepseek/deepseek-chat",
            "litellm/deepseek/deepseek-coder",
        ],
        "openrouter": [
            "litellm/openrouter/meta-llama/llama-3-70b-instruct",
            "litellm/openrouter/google/gemma-2-9b-it",
            "litellm/openrouter/mistralai/mistral-large",
        ],
    }


def format_setup_instructions(provider: ProviderType) -> str:
    """Get setup instructions for a specific provider.
    
    Args:
        provider: Provider type
        
    Returns:
        Setup instructions as markdown string
    """
    instructions = {
        "ollama": """
## Ollama Setup

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Pull a model:**
   ```bash
   ollama pull qwen2.5:72b
   ollama pull qwen2.5-coder:32b
   ```

3. **Start the server:**
   ```bash
   ollama serve
   ```

4. **Set in .env:**
   ```
   DEFAULT_MODEL=litellm/ollama/qwen2.5:72b
   ```
""",
        "llamacpp": """
## llama.cpp Setup

1. **Install llama.cpp with server support:**
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make
   ```

2. **Download a GGUF model** (e.g., from HuggingFace)

3. **Start the server:**
   ```bash
   ./server -m path/to/model.gguf --host 0.0.0.0 --port 8080
   ```

4. **Set in .env:**
   ```
   DEFAULT_MODEL=litellm/llamacpp/path/to/model.gguf
   ```
""",
        "deepseek": """
## DeepSeek Setup

1. **Get API key:** Sign up at https://platform.deepseek.com

2. **Set in .env:**
   ```
   DEEPSEEK_API_KEY=sk-...
   DEFAULT_MODEL=litellm/deepseek/deepseek-chat
   ```
""",
        "openrouter": """
## OpenRouter Setup

1. **Get API key:** Sign up at https://openrouter.ai

2. **Set in .env:**
   ```
   OPENROUTER_API_KEY=sk-or-...
   DEFAULT_MODEL=litellm/openrouter/meta-llama/llama-3-70b-instruct
   ```

3. **Available models:** Browse at https://openrouter.ai/models
""",
    }
    
    return instructions.get(provider, f"No specific setup instructions for {provider}")


# Convenience functions for common checks

def ollama_available() -> bool:
    """Check if Ollama provider is configured."""
    return True  # Ollama doesn't need a key, just the service running


def deepseek_available() -> bool:
    """Check if DeepSeek API key is configured."""
    _refresh_runtime_env()
    return bool(os.getenv("DEEPSEEK_API_KEY"))


def openrouter_available() -> bool:
    """Check if OpenRouter API key is configured."""
    _refresh_runtime_env()
    return bool(os.getenv("OPENROUTER_API_KEY"))
