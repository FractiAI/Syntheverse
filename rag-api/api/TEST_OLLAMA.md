# Testing Ollama API

This document explains how to test if Ollama is working correctly before using it in the RAG API.

## Quick Test

Run the test script:

```bash
cd rag-api/api
python3 test_ollama.py
```

## What the Test Does

The test script performs three checks:

1. **Connection Test**: Verifies Ollama API is reachable at `http://localhost:11434`
2. **Models Test**: Lists all available Ollama models
3. **Generation Test**: Tests that a model can actually generate text

## Expected Output

If everything is working:

```
============================================================
Ollama API Test
============================================================

Test 1: Checking Ollama connection...
✅ Ollama is reachable

Test 2: Checking available models...
✅ Found 1 model(s):
   1. llama2 (3825 MB)

Test 3: Testing model generation...
ℹ️  Using first available model: llama2
🔄 Testing generation with model: llama2...
✅ Generation successful!
   Prompt: Say 'Hello, Syntheverse!' in one sentence.
   Response: Hello, Syntheverse!

============================================================
✅ All tests passed! Ollama is ready to use.
============================================================

Recommended model for Syntheverse RAG:
   llama2

You can now use Ollama in the RAG API with:
   llm_model: 'ollama:llama2'
```

## Troubleshooting

### "Cannot connect to Ollama"

**Problem**: Ollama is not running or not accessible.

**Solutions**:
- On macOS: Open **Ollama.app** from Applications folder
- Or run: `ollama serve` in terminal
- Check if port 11434 is in use: `lsof -i :11434`

### "No models found"

**Problem**: Ollama is running but no models are installed.

**Solution**: Install a model:
```bash
ollama pull llama2
# or
ollama pull mistral
# or
ollama pull codellama
```

### "Generation failed"

**Problem**: Model exists but can't generate text.

**Solutions**:
- Check if model is fully downloaded: `ollama list`
- Try a different model
- Check system resources (RAM, disk space)

## Manual Testing

You can also test Ollama manually:

```bash
# List models
curl http://localhost:11434/api/tags

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Hello, world!",
  "stream": false
}'
```

## Next Steps

Once the test passes:
1. Ollama is ready to use in the RAG API
2. The RAG API will automatically use Ollama for answer generation
3. You can specify which model to use in API requests

