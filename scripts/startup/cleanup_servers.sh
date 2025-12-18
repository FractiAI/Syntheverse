#!/bin/bash

# Syntheverse Server Cleanup Script
# Run this before starting servers to ensure clean state

echo "🧹 Cleaning up existing Syntheverse server processes..."

# Kill Python Flask apps
echo "Killing Python Flask processes..."
pkill -f "python.*app.py" || echo "No Python Flask processes found"

# Kill Next.js development servers
echo "Killing Next.js development servers..."
pkill -f "npm.*dev" || echo "No npm dev processes found"
pkill -f "next.*dev" || echo "No Next.js dev processes found"

# Kill any lingering node processes on our ports
echo "Killing Node.js processes..."
pkill -f "node.*3001" || echo "No Node.js processes on port 3001 found"

# Wait for processes to fully terminate
echo "Waiting for processes to terminate..."
sleep 3

# Check if ports are free
echo "Checking port availability..."
lsof -i :3001 || echo "Port 3001 is free"
lsof -i :5001 || echo "Port 5001 is free"
lsof -i :8000 || echo "Port 8000 is free"

echo "✅ Cleanup completed!"
echo "You can now start the servers safely."

