# Ollama Integration

The RAG API uses Ollama for local LLM inference instead of local embeddings.

## Testing Ollama

Before using the RAG API, test that Ollama is working:

```bash
cd rag-api/api
python3 test_ollama.py
```

This will:
1. Check if Ollama API is reachable
2. List available models
3. Test model generation

## Starting Ollama

If Ollama is not running:

### macOS
1. Open **Ollama.app** from Applications folder
2. Or run: `./start_ollama.sh`
3. Or manually: `ollama serve`

### Verify it's running
```bash
curl http://localhost:11434/api/tags
```

## Installing Models

If no models are available, install one:

```bash
ollama pull llama2
# or
ollama pull mistral
# or
ollama pull codellama
```

## Using Ollama in RAG API

Once Ollama is running and models are installed:

1. Start the RAG API:
```bash
python rag_api.py
```

2. Use Ollama models in queries:
- Set `llm_model` to `"ollama:llama2"` (or your model name)
- Or use `"ollama"` to use the default model

## Troubleshooting

### "Connection refused"
- Ollama is not running
- Start Ollama.app or run `ollama serve`

### "No models available"
- Install a model: `ollama pull llama2`

### "Model not found"
- Check available models: `ollama list`
- Use correct model name in API calls

