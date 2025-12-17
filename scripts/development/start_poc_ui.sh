#!/bin/bash

# Start PoC UI System
# Starts both the API server and the Next.js frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Starting Syntheverse PoC UI System${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Load GROQ_API_KEY from .env file if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    GROQ_API_KEY=$(grep '^GROQ_API_KEY=' "$PROJECT_ROOT/.env" | cut -d'=' -f2)
    if [ ! -z "$GROQ_API_KEY" ]; then
        export GROQ_API_KEY
        echo -e "${GREEN}✓ Loaded GROQ_API_KEY from .env file${NC}"
    else
        echo -e "${YELLOW}⚠️  GROQ_API_KEY not found in .env file${NC}"
    fi
fi

# Check for GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GROQ_API_KEY not set${NC}"
    echo -e "${YELLOW}   Set it with: export GROQ_API_KEY=your-key${NC}"
    echo ""
fi

echo -e "${BLUE}Killing any existing processes...${NC}"
if lsof -ti:5001 > /dev/null 2>&1; then
    echo -e "${YELLOW}Killing processes on port 5001...${NC}"
    kill $(lsof -ti:5001) 2>/dev/null || true
fi
if lsof -ti:3001 > /dev/null 2>&1; then
    echo -e "${YELLOW}Killing processes on port 3001...${NC}"
    kill $(lsof -ti:3001) 2>/dev/null || true
fi
# Wait for ports to be freed
sleep 2
echo ""

echo -e "${BLUE}Starting API server...${NC}"
    cd "$PROJECT_ROOT/src/api/poc-api"
    
    # Use the project-level virtual environment
    if [ -f "$PROJECT_ROOT/syntheverse_test_env/bin/activate" ]; then
        source "$PROJECT_ROOT/syntheverse_test_env/bin/activate"
        echo -e "${GREEN}✓ Using project virtual environment${NC}"
    else
        echo -e "${YELLOW}⚠️  Project venv not found, using system Python${NC}"
    fi
    
    # Start API server in background with environment variables
    echo -e "${GREEN}✓ Starting API with GROQ_API_KEY (length: ${#GROQ_API_KEY})${NC}"
    GROQ_API_KEY="$GROQ_API_KEY" python app.py > /tmp/poc_api.log 2>&1 &
    API_PID=$!
    echo $API_PID > /tmp/poc_api.pid
    
    echo -e "${GREEN}✓ API server started (PID: $API_PID)${NC}"
    echo -e "   API: http://localhost:5001"
    echo -e "   Logs: tail -f /tmp/poc_api.log"
    echo ""
    
    # Wait for API to be ready
    echo -e "${YELLOW}Waiting for API server to be ready...${NC}"
    for i in {1..10}; do
        sleep 2
        if curl -s http://localhost:5001/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ API server is ready${NC}"
            break
        fi
        if [ $i -eq 10 ]; then
            echo -e "${RED}❌ API server failed to start${NC}"
            echo -e "   Check logs: tail -f /tmp/poc_api.log"
            exit 1
        fi
    done

echo -e "${BLUE}Starting Next.js frontend...${NC}"
    cd "$PROJECT_ROOT/src/frontend/poc-frontend"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install
    fi
    
    # Start frontend in background (Next.js defaults to 3000, but we'll set PORT env var)
    PORT=3001 npm run dev > /tmp/poc_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/poc_frontend.pid
    
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
    echo -e "   UI: http://localhost:3001"
    echo -e "   Logs: tail -f /tmp/poc_frontend.log"
    echo ""
    
    # Wait for frontend to be ready
    echo -e "${YELLOW}Waiting for frontend to be ready...${NC}"
    for i in {1..15}; do
        sleep 2
        if curl -s http://localhost:3001 > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend is ready${NC}"
            break
        fi
        if [ $i -eq 15 ]; then
            echo -e "${YELLOW}⚠️  Frontend may still be starting...${NC}"
            echo -e "   Check logs: tail -f /tmp/poc_frontend.log"
        fi
    done

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ PoC UI System is running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Frontend: ${GREEN}http://localhost:3001${NC}"
echo -e "API:      ${GREEN}http://localhost:5001${NC}"
echo ""
echo -e "To stop:  ${YELLOW}./stop_poc_ui.sh${NC}"
echo ""
