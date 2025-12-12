#!/bin/bash

# Fix Ollama Permissions
# This script fixes the permission issue with the Ollama binary

echo "=========================================="
echo "Fixing Ollama Permissions"
echo "=========================================="
echo ""

# Check current permissions
echo "Current permissions:"
ls -la /Applications/Ollama.app/Contents/Resources/ollama
echo ""

# Fix permissions (requires sudo)
echo "Fixing permissions (you may be prompted for your password)..."
sudo chmod +x /Applications/Ollama.app/Contents/Resources/ollama

# Verify
echo ""
echo "New permissions:"
ls -la /Applications/Ollama.app/Contents/Resources/ollama
echo ""

# Test if it works now
echo "Testing ollama command..."
if /usr/local/bin/ollama --version 2>/dev/null; then
    echo "✅ Permissions fixed! Ollama command now works."
    echo ""
    echo "You can now start the server with:"
    echo "  ollama serve"
else
    echo "❌ Still having issues. Please check manually."
fi


