#!/bin/bash

# Stop PoC UI System

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Stopping Syntheverse PoC UI System${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Stop API server
if [ -f "/tmp/poc_api.pid" ]; then
    API_PID=$(cat /tmp/poc_api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping API server (PID: $API_PID)...${NC}"
        kill $API_PID
        rm /tmp/poc_api.pid
        echo -e "${GREEN}✓ API server stopped${NC}"
    else
        rm /tmp/poc_api.pid
    fi
fi

# Kill any process on port 5001
if lsof -ti:5001 > /dev/null 2>&1; then
    echo -e "${YELLOW}Killing processes on port 5001...${NC}"
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true
fi

# Stop frontend
if [ -f "/tmp/poc_frontend.pid" ]; then
    FRONTEND_PID=$(cat /tmp/poc_frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID
        rm /tmp/poc_frontend.pid
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    else
        rm /tmp/poc_frontend.pid
    fi
fi

# Kill any process on port 3001
if lsof -ti:3001 > /dev/null 2>&1; then
    echo -e "${YELLOW}Killing processes on port 3001...${NC}"
    lsof -ti:3001 | xargs kill -9 2>/dev/null || true
fi

# Kill any remaining Next.js processes
pkill -f "next dev" 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""
