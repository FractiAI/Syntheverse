#!/bin/bash

# Quick stop script for all Syntheverse services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping all Syntheverse services..."

# Kill processes on ports
lsof -ti:5000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null || true

# Kill by process name
pkill -f "rag_api.py" 2>/dev/null || true
pkill -f "ui_web/app.py" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python3.*app.py" 2>/dev/null || true
pkill -f "python3.*rag_api" 2>/dev/null || true

# Remove PID files
rm -f /tmp/syntheverse_rag_api.pid
rm -f /tmp/syntheverse_pod_ui.pid

sleep 1
echo "All services stopped."

