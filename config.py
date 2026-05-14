"""Shared model configuration helpers — read by all agents at startup.

Supports OpenAI, Anthropic, Google, Ollama (local), llama.cpp (local),
DeepSeek API, and OpenRouter via LiteLLM routing.
"""
import os

from shared_tools.providers import get_provider_type, is_local_model


def get_default_model(fallback: str | None = None):
    """Return the configured default model for standard agents.
    
    Args:
        fallback: Default model to use if DEFAULT_MODEL env var not set.
                  Defaults to "gpt-5.2" for backwards compatibility.
    
    Returns:
        Model identifier (string or LitellmModel instance)
    """
    if fallback is None:
        fallback = "gpt-5.2"
    model = os.getenv("DEFAULT_MODEL", fallback)
    return _resolve(model)


def is_openai_provider() -> bool:
    """Return True when the configured provider is OpenAI (not LiteLLM).

    OpenAI model IDs never contain a slash (e.g. 'gpt-5.2', 'o3').
    Any 'provider/model' string (e.g. 'anthropic/claude-sonnet-4-6',
    'litellm/gemini/gemini-3-flash', 'litellm/ollama/qwen2.5:72b') 
    is treated as a LiteLLM-routed model.
    """
    return "/" not in os.getenv("DEFAULT_MODEL", "")


def get_configured_provider():
    """Get the provider type for the currently configured model.
    
    Returns:
        Provider type string (e.g., 'openai', 'ollama', 'deepseek', 'openrouter')
    """
    model = os.getenv("DEFAULT_MODEL")
    return get_provider_type(model)


def is_using_local_model() -> bool:
    """Check if currently configured model runs locally.
    
    Returns:
        True if using Ollama or llama.cpp
    """
    model = os.getenv("DEFAULT_MODEL")
    return is_local_model(model)


def _resolve(model: str):
    """Route 'provider/model' strings through LitellmModel.

    Handles both explicit 'litellm/<model>' and bare 'provider/model' forms.
    OpenAI model IDs contain no slash, so they pass through unchanged.
    Local models (Ollama, llama.cpp) are also routed through LiteLLM.
    """
    if "/" not in model:
        return model
    bare = model[len("litellm/"):] if model.startswith("litellm/") else model
    try:
        from agency_swarm import LitellmModel  # noqa: PLC0415
        return LitellmModel(model=bare)
    except ImportError:
        return model
