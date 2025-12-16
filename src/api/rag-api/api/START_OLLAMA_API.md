# Starting Ollama API Server

On macOS, Ollama.app may open the GUI but not start the API server automatically. Here's how to start the API server:

## Option 1: Start via Terminal (Recommended)

```bash
# Start Ollama server in background
ollama serve

# Or run in background:
ollama serve > /tmp/ollama.log 2>&1 &
```

## Option 2: Check Ollama.app Settings

1. Open Ollama.app
2. Check if there's a setting to "Start API Server" or "Enable API"
3. Some versions require the server to be started manually

## Option 3: Verify Installation

```bash
# Check if Ollama is installed
which ollama

# Check version
ollama --version

# If not found, install from: https://ollama.ai
```

## Test API Connection

Once the server is running, test it:

```bash
# Quick test
curl http://localhost:11434/api/tags

# Or use our test script
cd rag-api/api
python3 test_ollama.py
```

## Expected Behavior

When Ollama API is running:
- Port 11434 should be listening
- `curl http://localhost:11434/api/tags` should return JSON with available models
- The test script should pass all three tests

## Troubleshooting

If `ollama serve` doesn't work:
1. Make sure Ollama is properly installed
2. Check if port 11434 is already in use: `lsof -i :11434`
3. Try restarting Ollama.app
4. Check system logs for errors


