#!/bin/bash

# Start Ollama Server
# This script helps start Ollama if it's not running

echo "=========================================="
echo "Starting Ollama Server"
echo "=========================================="
echo ""

# Check if Ollama is already running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is already running on http://localhost:11434"
    exit 0
fi

echo "Ollama is not running. Starting..."
echo ""

# Try to start Ollama
if command -v ollama &> /dev/null; then
    echo "Starting Ollama server..."
    ollama serve &
    sleep 3
    
    # Check if it started
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama started successfully"
    else
        echo "⚠️  Ollama may need to be started manually"
        echo "   On macOS: Open Ollama.app from Applications"
        echo "   Or run: ollama serve"
    fi
else
    echo "❌ Ollama command not found"
    echo "   Please install Ollama from: https://ollama.ai"
    echo "   On macOS: Download and install Ollama.app"
fi

echo ""
echo "=========================================="


