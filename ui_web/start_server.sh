#!/bin/bash
# Start Syntheverse PoD Web UI Server

cd "$(dirname "$0")"

echo "=================================="
echo "Syntheverse PoD Web UI Server"
echo "=================================="
echo ""
echo "Starting server..."
echo "Open your browser and go to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

python app.py
