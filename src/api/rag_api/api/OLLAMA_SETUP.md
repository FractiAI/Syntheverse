# Ollama API Setup Instructions

## Current Issue

The Ollama API server is not starting automatically when Ollama.app is opened on macOS.

## Solution

You need to manually start the Ollama API server. Here are the options:

### Option 1: Start via Terminal (Recommended)

Open a new terminal window and run:

```bash
ollama serve
```

**Keep this terminal window open** - the server runs in the foreground.

### Option 2: Check Ollama.app Settings

1. Open Ollama.app
2. Look for settings/preferences
3. Check if there's an option to "Start API Server" or "Enable API"
4. Some versions may require manual activation

### Option 3: Use Background Process

If you want to run it in the background:

```bash
nohup ollama serve > /tmp/ollama.log 2>&1 &
```

Then check if it's running:
```bash
curl http://localhost:11434/api/tags
```

## Verify It's Working

Once the server is running, test it:

```bash
cd rag-api/api
python3 ollama_check.py
```

You should see:
- ✅ Ollama is reachable
- ✅ Found X model(s)
- ✅ Generation successful

## Troubleshooting

### Permission Denied Error

If you get "Permission denied" when running `ollama serve`:

1. Check permissions:
   ```bash
   ls -la /usr/local/bin/ollama
   ```

2. Fix permissions if needed:
   ```bash
   sudo chmod +x /usr/local/bin/ollama
   ```

### Port Already in Use

If port 11434 is already in use:
```bash
lsof -i :11434
# Kill the process if needed
kill <PID>
```

### No Models Installed

If the API works but no models are found:
```bash
ollama pull llama2
# or
ollama pull mistral
```

## Next Steps

Once the API is working:
1. The RAG API can use Ollama for answer generation
2. Run `python3 ollama_check.py` to verify
3. Start the RAG API: `python rag_api.py`


