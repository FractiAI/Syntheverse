# Lightweight Local LLM Models for Ollama

## Recommended Lightweight Models

### 1. **TinyLlama** (637 MB) ⭐ Smallest
- **Size**: 637 MB
- **Best for**: Fast responses, minimal resources
- **Install**: `ollama pull tinyllama`
- **Use case**: Quick queries, simple tasks

### 2. **Phi-2** (1.6 GB)
- **Size**: 1.6 GB  
- **Best for**: Better quality than TinyLlama, still lightweight
- **Install**: `ollama pull phi-2`
- **Use case**: Better reasoning, Microsoft's efficient model

### 3. **Gemma 2B** (1.4 GB)
- **Size**: 1.4 GB
- **Best for**: Google's efficient model
- **Install**: `ollama pull gemma:2b`
- **Use case**: Balanced performance and size

### 4. **Llama 3.2 1B** (1.3 GB)
- **Size**: 1.3 GB
- **Best for**: Meta's smallest model
- **Install**: `ollama pull llama3.2:1b`
- **Use case**: Good quality in small package

## Current Installation

TinyLlama is being installed (637 MB - smallest option).

## After Installation

Once the model is installed, test it:

```bash
cd rag-api/api
python3 ollama_check.py
```

The test will verify:
- ✅ Ollama connection
- ✅ Model availability
- ✅ Text generation

## Using in RAG API

Once installed, the RAG API will automatically use the model. You can specify which model:

```bash
# In API request
{
  "query": "your question",
  "llm_model": "ollama:tinyllama"
}
```

## Performance Comparison

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| TinyLlama | 637 MB | ⚡⚡⚡ | ⭐⭐ | Fast, simple |
| Phi-2 | 1.6 GB | ⚡⚡ | ⭐⭐⭐ | Balanced |
| Gemma 2B | 1.4 GB | ⚡⚡ | ⭐⭐⭐ | Google quality |
| Llama 3.2 1B | 1.3 GB | ⚡⚡ | ⭐⭐⭐ | Meta quality |

