# OpenSwarm — Local Models & Alternative Providers Guide

Quick reference for running OpenSwarm with local models (Ollama, llama.cpp) and alternative providers (DeepSeek, OpenRouter).

---

## 🚀 Quick Start: Run with Local Models (Free!)

### Option 1: Ollama (Recommended for most users)

**1. Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**2. Pull a model:**
```bash
# Best all-around performance
ollama pull qwen2.5:72b

# Best for coding tasks
ollama pull qwen2.5-coder:32b

# Good balance of speed/quality
ollama pull llama3.1:70b

# Specialized for code
ollama pull deepseek-coder:33b
```

**3. Configure OpenSwarm:**
```bash
cd /workspace
echo "DEFAULT_MODEL=litellm/ollama/qwen2.5:72b" > .env
```

**4. Start Ollama server:**
```bash
ollama serve
```

**5. Run OpenSwarm:**
```bash
python swarm.py
```

---

### Option 2: llama.cpp (For custom GGUF models)

**1. Install llama.cpp:**
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```

**2. Download a GGUF model:**
```bash
# Example: Qwen 2.5 72B (quantized)
wget https://huggingface.co/Qwen/Qwen2.5-72B-Instruct-GGUF/resolve/main/qwen2.5-72b-instruct-q5_k_m.gguf
```

**3. Start llama.cpp server:**
```bash
./server -m qwen2.5-72b-instruct-q5_k_m.gguf --host 0.0.0.0 --port 8080
```

**4. Configure OpenSwarm:**
```bash
cd /workspace
echo "DEFAULT_MODEL=litellm/llamacpp/path/to/qwen2.5-72b-instruct-q5_k_m.gguf" > .env
```

**5. Run OpenSwarm:**
```bash
python swarm.py
```

---

## 🔑 Alternative API Providers

### DeepSeek (Cost-effective API)

**1. Get API key:** Sign up at https://platform.deepseek.com

**2. Configure:**
```bash
cd /workspace
cat >> .env << EOF
DEEPSEEK_API_KEY=sk-your-key-here
DEFAULT_MODEL=litellm/deepseek/deepseek-chat
EOF
```

**3. Run:**
```bash
python swarm.py
```

---

### OpenRouter (Access 100+ models)

**1. Get API key:** Sign up at https://openrouter.ai

**2. Configure:**
```bash
cd /workspace
cat >> .env << EOF
OPENROUTER_API_KEY=sk-or-your-key-here
DEFAULT_MODEL=litellm/openrouter/meta-llama/llama-3-70b-instruct
EOF
```

**3. Browse models:** https://openrouter.ai/models

**4. Run:**
```bash
python swarm.py
```

---

## 📊 Model Recommendations

| Use Case | Recommended Model | Provider | VRAM Required |
|----------|------------------|----------|---------------|
| **General Tasks** | Qwen 2.5 72B | Ollama | 48GB+ (or use q4_K_M quant) |
| **Coding** | Qwen 2.5 Coder 32B | Ollama | 24GB+ |
| **Balanced** | Llama 3.1 70B | Ollama | 48GB+ |
| **Budget API** | DeepSeek Chat | DeepSeek API | N/A |
| **Variety** | Any via OpenRouter | OpenRouter | N/A |
| **Low VRAM** | Qwen 2.5 7B/14B | Ollama | 8-16GB |
| **Best Quality** | Qwen 2.5 72B (q5_K_M) | llama.cpp | 52GB+ |

---

## ⚙️ Configuration Reference

### Environment Variables (.env)

```bash
# === LOCAL MODELS (No API key needed) ===

# Ollama
DEFAULT_MODEL=litellm/ollama/qwen2.5:72b

# llama.cpp
DEFAULT_MODEL=litellm/llamacpp/path/to/model.gguf


# === ALTERNATIVE APIs ===

# DeepSeek
DEEPSEEK_API_KEY=sk-...
DEFAULT_MODEL=litellm/deepseek/deepseek-chat

# OpenRouter
OPENROUTER_API_KEY=sk-or-...
DEFAULT_MODEL=litellm/openrouter/meta-llama/llama-3-70b-instruct


# === TRADITIONAL PROVIDERS ===

# OpenAI
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-5.2

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=litellm/anthropic/claude-sonnet-4-6

# Google
GOOGLE_API_KEY=...
DEFAULT_MODEL=litellm/gemini/gemini-3-flash
```

---

## 🔍 Checking Provider Status

Use the built-in provider utilities:

```python
from shared_tools.providers import (
    get_provider_type,
    is_local_model,
    check_provider_available,
    list_available_providers,
)

# Check what provider you're using
model = "litellm/ollama/qwen2.5:72b"
provider = get_provider_type(model)  # Returns: "ollama"

# Check if it's a local model
is_local = is_local_model(model)  # Returns: True

# Check availability
available, message = check_provider_available(model)
print(message)

# List all configured providers
providers = list_available_providers()
for name, info in providers.items():
    status = "✓" if info["configured"] else "✗"
    print(f"{status} {info['name']}: {'Local' if info['local'] else 'API'}")
```

---

## 🛠️ Troubleshooting

### Ollama Issues

**Problem:** Connection refused
```bash
# Make sure Ollama is running
ollama serve

# Check if it's listening
curl http://localhost:11434/api/tags
```

**Problem:** Model not found
```bash
# Pull the model
ollama pull qwen2.5:72b

# Verify it's available
ollama list
```

**Problem:** Out of memory
```bash
# Use a smaller/quantized model
ollama pull qwen2.5:7b      # Smallest
ollama pull qwen2.5:14b     # Medium
ollama pull qwen2.5:72b-q4_K_M  # Quantized large model
```

### llama.cpp Issues

**Problem:** Server won't start
```bash
# Check model path
ls -la path/to/model.gguf

# Try with fewer layers on GPU
./server -m model.gguf --n-gpu-layers 20
```

**Problem:** Slow inference
```bash
# Increase context size if you have RAM
./server -m model.gguf --ctx-size 8192

# Use more CPU threads
./server -m model.gguf --threads 16
```

### General Issues

**Problem:** Model not responding
```bash
# Test direct connection (Ollama)
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:72b",
  "prompt": "Hello",
  "stream": false
}'

# Check DEFAULT_MODEL setting
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DEFAULT_MODEL'))"
```

**Problem:** Agent errors with local models
- Local models may have weaker function calling support
- Try simpler prompts first
- Adjust agent instructions if needed
- Consider using a larger/better model

---

## 📈 Performance Tips

### For Ollama

1. **Use quantized models** for lower memory:
   - `q4_K_M` - Good quality, low memory
   - `q5_K_M` - Better quality, moderate memory
   - `q6_K` / `q8_0` - Best quality, high memory

2. **Set appropriate context:**
   ```bash
   ollama run qwen2.5:72b --num_ctx 8192
   ```

3. **GPU offloading** (if you have NVIDIA):
   ```bash
   OLLAMA_NUM_GPU=99 ollama serve
   ```

### For llama.cpp

1. **Optimize GPU layers:**
   ```bash
   ./server -m model.gguf --n-gpu-layers 35
   ```

2. **Use flash attention:**
   ```bash
   ./server -m model.gguf --flash-attn
   ```

3. **Batch processing:**
   ```bash
   ./server -m model.gguf --batch-size 512
   ```

---

## 🔧 Developer Utilities

### Provider Detection in Code

```python
from config import get_configured_provider, is_using_local_model

provider = get_configured_provider()
if is_using_local_model():
    print(f"Running locally with {provider}")
else:
    print(f"Using API provider: {provider}")
```

### Setup Instructions Programmatically

```python
from shared_tools.providers import format_setup_instructions

print(format_setup_instructions("ollama"))
print(format_setup_instructions("deepseek"))
```

### Model Examples

```python
from shared_tools.providers import get_provider_examples

examples = get_provider_examples()
print("Ollama models:", examples["ollama"])
print("OpenRouter models:", examples["openrouter"])
```

---

## 📚 Additional Resources

- **Ollama:** https://ollama.com
- **llama.cpp:** https://github.com/ggerganov/llama.cpp
- **DeepSeek:** https://platform.deepseek.com
- **OpenRouter:** https://openrouter.ai
- **GGUF Models:** https://huggingface.co/models?library=gguf
- **Qwen Models:** https://huggingface.co/Qwen

---

## ✅ Verification Checklist

Before running with local models:

- [ ] Ollama or llama.cpp installed
- [ ] Model downloaded/pulled
- [ ] Server running (`ollama serve` or `./server`)
- [ ] `.env` configured with correct `DEFAULT_MODEL`
- [ ] Test direct API access works
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)

Then run:
```bash
python swarm.py
```

---

**Questions?** See `QWEN.md` for detailed documentation or check the provider utilities in `shared_tools/providers.py`.
