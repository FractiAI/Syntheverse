#!/bin/bash

# Start Ollama API Server
# This script starts the Ollama API server for local LLM access

echo "=========================================="
echo "Starting Ollama API Server"
echo "=========================================="
echo ""

# Check if already running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama API is already running on http://localhost:11434"
    echo ""
    echo "Available models:"
    curl -s http://localhost:11434/api/tags | python3 -m json.tool 2>/dev/null | grep -A 2 '"name"' | head -10
    exit 0
fi

# Check if ollama command exists
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama command not found"
    echo "   Please install Ollama from: https://ollama.ai"
    echo "   On macOS: Download and install Ollama.app"
    exit 1
fi

echo "Starting Ollama server..."
echo "   This will start the API server on http://localhost:11434"
echo "   Press Ctrl+C to stop"
echo ""
echo "=========================================="
echo ""

# Start Ollama server (foreground so we can see output)
ollama serve


