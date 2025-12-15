#!/bin/bash

# Test script for PoC Frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Testing Syntheverse PoC Frontend${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GROQ_API_KEY not set${NC}"
    echo -e "${YELLOW}   Set it with: export GROQ_API_KEY=your-key${NC}"
    echo ""
fi

# Check Python dependencies
echo -e "${BLUE}Checking Python dependencies...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing API server dependencies...${NC}"
    cd ui-poc-api
    pip install -q -r requirements.txt
    cd ..
fi

# Check Node dependencies
echo -e "${BLUE}Checking Node dependencies...${NC}"
if [ ! -d "ui-poc/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd ui-poc
    npm install
    cd ..
fi

echo ""
echo -e "${GREEN}✓ Dependencies checked${NC}"
echo ""

# Start API server in background
echo -e "${BLUE}Starting API server on port 5001...${NC}"
cd ui-poc-api
python3 server.py > /tmp/poc_api.log 2>&1 &
API_PID=$!
cd ..

# Wait for API server to start
sleep 3

# Check if API server is running
if ! curl -s http://localhost:5001/ > /dev/null 2>&1; then
    echo -e "${RED}❌ API server failed to start${NC}"
    echo "Check logs: tail -f /tmp/poc_api.log"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ API server running (PID: $API_PID)${NC}"
echo ""

# Start Next.js dev server
echo -e "${BLUE}Starting Next.js frontend on port 3000...${NC}"
cd ui-poc
PORT=3000 npm run dev > /tmp/poc_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

# Check if frontend is running
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo "Check logs: tail -f /tmp/poc_frontend.log"
    kill $API_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ Frontend running (PID: $FRONTEND_PID)${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Services Running${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}API:${NC}      http://localhost:5001"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo "  Frontend: tail -f /tmp/poc_frontend.log"
echo "  API:      tail -f /tmp/poc_api.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${BLUE}Stopping services...${NC}"
    kill $API_PID $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}

trap cleanup INT TERM

# Wait
wait
