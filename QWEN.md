# OpenSwarm — Qwen Coder Setup Guide

This file provides Qwen Coder with everything needed to understand, modify, and extend this multi-agent swarm system.

---

## Quick Start for Qwen Coder

**Before making any changes:**
1. Read this entire file first
2. Check `.cursor/rules/agency-swarm-workflow.mdc` for agent creation guidelines
3. Review existing agent implementations in their respective folders
4. Understand the model routing system in `config.py`

---

## What is OpenSwarm?

OpenSwarm is a multi-agent AI coordination system built on the **Agency Swarm** framework. It features:

- **8 specialized agents** coordinated by an orchestrator
- **Shared tools** available to all agents
- **Agent-specific tools** for specialized tasks
- **Flexible model routing** via LiteLLM (supports OpenAI, Anthropic, Google, and more)
- **Terminal UI** and **FastAPI server** interfaces

---

## Architecture Overview

### Core Files

```
swarm.py                  ← Main agency configuration: imports agents, defines communication flows
config.py                 ← Model configuration and routing logic
run_utils.py              ← Runtime utilities for CLI execution
server.py                 ← FastAPI server entry point
onboard.py                ← Interactive setup wizard
shared_instructions.md    ← System context shared across all agents
```

### Agent Structure

Each agent follows this pattern:

```
agent_name/
  __init__.py             ← Exports create_agent() factory function
  agent_name.py           ← Agent definition (imports instructions, defines model, tools)
  instructions.md         ← System prompt for this agent
  tools/                  ← Agent-specific tools
    ToolName.py           ← Individual tool implementations
```

### Current Agents

| Agent | Folder | Purpose |
|-------|--------|---------|
| Orchestrator | `orchestrator/` | Routes tasks to specialists |
| Virtual Assistant | `virtual_assistant/` | Email, calendar, Slack, files + Composio integrations |
| Deep Research | `deep_research/` | Web research with citations |
| Data Analyst | `data_analyst_agent/` | Data analysis, visualization, statistics |
| Docs Agent | `docs_agent/` | Document creation (Word, PDF) |
| Slides Agent | `slides_agent/` | PowerPoint/HTML slide generation |
| Image Generation | `image_generation_agent/` | AI image generation/editing |
| Video Generation | `video_generation_agent/` | AI video generation/editing |

---

## Model Configuration System

### How Models Work

OpenSwarm uses a flexible model routing system through `config.py`:

1. **OpenAI-native models**: Plain model names without slashes (e.g., `gpt-5.2`, `o3`)
2. **LiteLLM-routed models**: Provider/model format (e.g., `anthropic/claude-sonnet-4-6`, `litellm/gemini/gemini-3-flash`)

### Environment Variables

Set in `.env` (copy from `.env.example`):

```bash
# Required (choose one primary provider)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Model selection
DEFAULT_MODEL=gpt-5.2                    # OpenAI native
DEFAULT_MODEL=litellm/anthropic/claude-sonnet-4-6  # Via LiteLLM
DEFAULT_MODEL=litellm/gemini/gemini-3-flash        # Via LiteLLM

# Optional providers
COMPOSIO_API_KEY=...      # 10,000+ integrations
SEARCH_API_KEY=...        # Web search
FAL_KEY=...               # Image/video generation
```

### Config Functions

```python
from config import get_default_model, is_openai_provider

model = get_default_model()  # Returns configured model (auto-routes via LiteLLM if needed)
if is_openai_provider():
    # Use OpenAI-specific features like reasoning summaries
```

---

## Communication Flows

Defined in `swarm.py`:

1. **SendMessage flows**: Orchestrator → Specialists (one-way messages)
2. **Handoff flows**: Any agent → Any other agent (full mesh)

Example modification pattern:

```python
# In swarm.py
send_message_flows = [
    (orchestrator, specialist, SendMessage)
    for specialist in all_agents
    if specialist is not orchestrator
]

handoff_flows = [
    (a > b, Handoff)
    for a in all_agents
    for b in all_agents
    if a is not b
]
```

---

## Tool Development

### Tool Structure

Tools are Python classes with specific methods:

```python
from agency_swarm.tools import BaseTool

class MyTool(BaseTool):
    """Tool description for the agent."""
    
    # Define parameters with pydantic
    param1: str = Field(..., description="Parameter description")
    
    def run(self):
        """Execute the tool logic."""
        # Your implementation here
        return result
```

### Tool Categories

1. **Shared Tools** (`shared_tools/`): Available to all agents
   - Composio integrations
   - File operations
   - Connection management

2. **Agent-Specific Tools** (`agent_name/tools/`): Only for that agent
   - Specialized operations
   - Domain-specific functionality

### Tool Discovery

Agents auto-load tools from their `tools/` folder. No manual registration needed.

---

## Adding New Providers (Ollama, llama.cpp, DeepSeek, OpenRouter)

### Supported Provider Patterns

The system supports multiple provider types through LiteLLM:

#### 1. **Ollama (Local Models)**

```bash
# .env
DEFAULT_MODEL=litellm/ollama/qwen2.5:7b
# or
DEFAULT_MODEL=litellm/ollama_chat/qwen2.5:7b
```

**Requirements:**
- Ollama running locally: `ollama serve`
- Model pulled: `ollama pull qwen2.5:7b`

#### 2. **llama.cpp (Local Models)**

```bash
# .env
DEFAULT_MODEL=litellm/llamacpp/path/to/model.gguf
```

**Requirements:**
- llama.cpp server running
- Model file downloaded

#### 3. **DeepSeek (API)**

```bash
# .env
DEEPSEEK_API_KEY=sk-...
DEFAULT_MODEL=litellm/deepseek/deepseek-chat
# or
DEFAULT_MODEL=litellm/deepseek/deepseek-coder
```

#### 4. **OpenRouter (Multi-Provider API)**

```bash
# .env
OPENROUTER_API_KEY=sk-or-...
DEFAULT_MODEL=litellm/openrouter/meta-llama/llama-3-70b-instruct
# or any OpenRouter model
DEFAULT_MODEL=litellm/openrouter/google/gemma-2-9b-it
```

### Implementation Notes

1. **LiteLLM handles routing**: Just use `litellm/provider/model` format
2. **Custom base URLs**: Some providers need custom endpoints
3. **API key validation**: Add checks in tools that depend on specific providers
4. **Model capabilities**: Different models support different features (JSON mode, function calling, etc.)

### Example: Adding Provider Detection

```python
# In config.py or a new providers.py
def get_provider_type(model: str) -> str:
    """Determine provider type from model string."""
    if not model or "/" not in model:
        return "openai"
    
    parts = model.replace("litellm/", "").split("/")
    if len(parts) >= 2:
        return parts[0]  # ollama, deepseek, openrouter, etc.
    return "unknown"

def is_local_model(model: str) -> bool:
    """Check if model runs locally."""
    provider = get_provider_type(model)
    return provider in ("ollama", "llamacpp", "local")
```

---

## Common Modification Patterns

### 1. Add a New Agent

Follow `.cursor/rules/agency-swarm-workflow.mdc`:

```bash
# Create agent folder structure
mkdir new_agent
cd new_agent
touch __init__.py new_agent.py instructions.md
mkdir tools
```

Update `swarm.py`:
```python
from new_agent import create_new_agent
new_agent = create_new_agent()
all_agents.append(new_agent)
```

### 2. Change Default Model

Edit `.env`:
```bash
DEFAULT_MODEL=litellm/ollama/qwen2.5:72b
```

Or modify `config.py` fallback:
```python
def get_default_model(fallback: str = "litellm/ollama/qwen2.5:72b"):
```

### 3. Add Custom Tool

Create `agent_name/tools/MyTool.py`:
```python
from agency_swarm.tools import BaseTool

class MyTool(BaseTool):
    """Description."""
    param: str = Field(..., description="...")
    
    def run(self):
        return f"Result: {self.param}"
```

### 4. Modify Agent Behavior

Edit `agent_name/instructions.md` - this is the system prompt that defines behavior.

---

## Testing & Debugging

### Run Options

```bash
# Terminal UI (interactive)
python swarm.py

# API Server
python server.py

# Specific agent test
python -m orchestrator.orchestrator
```

### Environment Validation

```bash
# Check .env loaded correctly
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('DEFAULT_MODEL'))"

# Test model connectivity
python -c "from config import get_default_model; print(get_default_model())"
```

### Common Issues

1. **Model not found**: Check DEFAULT_MODEL format and provider API keys
2. **Tool errors**: Verify tool parameters match schema
3. **Communication failures**: Check swarm.py flow definitions
4. **Import errors**: Ensure virtual environment activated

---

## Best Practices

### Code Style
- Use type hints
- Follow existing patterns in similar agents/tools
- Keep tools focused (single responsibility)
- Document tool purposes clearly

### Model Selection
- Use `get_default_model()` instead of hardcoding
- Check `is_openai_provider()` for OpenAI-specific features
- Gracefully degrade when models lack capabilities

### Tool Development
- Validate inputs thoroughly
- Provide clear error messages
- Handle missing API keys gracefully
- Use `model_availability.py` patterns for provider checks

### Agent Instructions
- Write clear, specific system prompts
- Include examples of expected behavior
- Define scope and limitations
- Update when adding new tools

---

## Extending for Local Models

### Key Considerations

1. **Context Length**: Local models may have smaller contexts
2. **Function Calling**: Not all local models support it natively
3. **Speed**: Local inference is slower than API calls
4. **Memory**: Large models need significant RAM/VRAM

### Recommended Local Models

- **Qwen 2.5 72B**: Excellent general performance
- **Qwen 2.5 Coder**: Best for code tasks
- **Llama 3.1 70B**: Strong all-rounder
- **DeepSeek Coder**: Specialized for programming
- **Mixtral 8x7B**: Good speed/quality balance

### Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull qwen2.5:72b
ollama pull qwen2.5-coder:32b
ollama pull deepseek-coder:33b

# Start server
ollama serve
```

### Performance Tips

1. Use quantized models (q4_K_M, q5_K_M) for lower memory
2. Set appropriate context windows in Ollama
3. Batch requests when possible
4. Cache frequent responses

---

## File Reference Summary

| File | Purpose | Modify When |
|------|---------|-------------|
| `swarm.py` | Agency configuration | Adding/removing agents, changing flows |
| `config.py` | Model routing | Adding providers, changing defaults |
| `.env` | Environment variables | Setting API keys, choosing models |
| `shared_instructions.md` | Shared context | Updating cross-agent knowledge |
| `agent_name/instructions.md` | Agent system prompt | Changing agent behavior |
| `agent_name/tools/*.py` | Tool implementations | Adding/modifying capabilities |
| `requirements.txt` | Dependencies | Adding new libraries |

---

## Next Steps

To modify this codebase for local models:

1. **Install Ollama/llama.cpp** and pull desired models
2. **Update `.env`** with local model configuration
3. **Test connectivity** with simple prompts
4. **Adjust agent instructions** if needed for local model quirks
5. **Add provider detection** in tools that need it
6. **Document limitations** in relevant files

For questions about specific modifications, refer to:
- `.cursor/rules/agency-swarm-workflow.mdc` - Agent creation guide
- `AGENTS.md` - Customization overview
- This file - Qwen-specific guidance

---

**Built on Agency Swarm Framework** - https://github.com/VRSEN/agency-swarm
