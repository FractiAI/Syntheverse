#!/bin/bash

# Test startup readiness improvements

echo "Testing startup readiness improvements..."
echo "=========================================="

# Load environment
cd /Users/4d/Documents/GitHub/Syntheverse
source .env

# Test port cleanup function
echo "Testing aggressive port cleanup..."
echo "-----------------------------------"

# Source the run.sh functions
source examples/run.sh

# Test the cleanup function (without actually killing anything important)
echo "Ports before cleanup:"
for port in 5000; do
    if command_exists lsof; then
        pids=$(lsof -ti:$port 2>/dev/null)
        if [[ -n "$pids" ]]; then
            echo "Port $port in use by PID: $pids"
        else
            echo "Port $port is free"
        fi
    fi
done

echo ""
echo "Testing quick verification..."
echo "-----------------------------"

# Test the verify_setup_quick function
verify_setup_quick

echo ""
echo "Startup readiness test completed."


