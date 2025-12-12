#!/bin/bash

# Quick stop script for Syntheverse

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping Syntheverse..."

# Kill processes on ports
lsof -ti:5000 2>/dev/null | xargs kill -9 2>/dev/null || true

# Kill by process name
pkill -f "ui_web/app.py" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "python3.*app.py" 2>/dev/null || true

# Remove PID files
rm -f /tmp/syntheverse_pod_ui.pid

sleep 1
echo "Syntheverse stopped."
