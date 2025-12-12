#!/bin/bash

# Syntheverse PoD System - Service Manager
# Manages all services: RAG API, PoD Submission UI (includes L1/L2)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables from .env if it exists
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ports
RAG_API_PORT=8000
POD_UI_PORT=5000

# PID files
RAG_API_PID_FILE="/tmp/syntheverse_rag_api.pid"
POD_UI_PID_FILE="/tmp/syntheverse_pod_ui.pid"

# Function to check if port is in use
check_port() {
    local port=$1
    lsof -ti:$port > /dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}Killing processes on port $port...${NC}"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Function to stop all services
stop_all() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Stopping All Syntheverse Services${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Stop RAG API
    if check_port $RAG_API_PORT; then
        echo -e "${YELLOW}Stopping RAG API (port $RAG_API_PORT)...${NC}"
        kill_port $RAG_API_PORT
        rm -f "$RAG_API_PID_FILE"
    else
        echo -e "${GREEN}RAG API not running${NC}"
    fi
    
    # Stop PoD UI
    if check_port $POD_UI_PORT; then
        echo -e "${YELLOW}Stopping PoD Submission UI (port $POD_UI_PORT)...${NC}"
        kill_port $POD_UI_PORT
        rm -f "$POD_UI_PID_FILE"
    else
        echo -e "${GREEN}PoD Submission UI not running${NC}"
    fi
    
    # Kill any remaining Python processes related to these services
    echo -e "${YELLOW}Cleaning up any remaining processes...${NC}"
    pkill -f "rag_api.py" 2>/dev/null || true
    pkill -f "ui_web/app.py" 2>/dev/null || true
    pkill -f "python.*app.py" 2>/dev/null || true
    
    sleep 2
    echo -e "${GREEN}All services stopped${NC}"
    echo ""
}

# Function to start RAG API
start_rag_api() {
    echo -e "${BLUE}Starting RAG API Server...${NC}"
    
    if check_port $RAG_API_PORT; then
        echo -e "${YELLOW}RAG API already running on port $RAG_API_PORT${NC}"
        return 0
    fi
    
    cd "$SCRIPT_DIR/rag-api/api"
    
    # Determine Python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python not found${NC}"
        return 1
    fi
    
    # Load environment variables from .env if it exists
    if [ -f "$SCRIPT_DIR/.env" ]; then
        echo -e "${YELLOW}Loading environment variables from .env...${NC}"
        set -a
        source "$SCRIPT_DIR/.env"
        set +a
    fi
    
    # Check if GROQ_API_KEY is set
    if [ -z "$GROQ_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  GROQ_API_KEY not set. Groq will be unavailable.${NC}"
        echo -e "${YELLOW}   Set GROQ_API_KEY environment variable or add it to .env file${NC}"
    else
        echo -e "${GREEN}✓ GROQ_API_KEY found - Groq will be available${NC}"
    fi
    
    # Start in background and capture PID
    $PYTHON_CMD rag_api.py > /tmp/syntheverse_rag_api.log 2>&1 &
    RAG_PID=$!
    echo $RAG_PID > "$RAG_API_PID_FILE"
    
    # Wait for server to start (give it more time)
    echo -e "${YELLOW}Waiting for RAG API to start (this may take 10-15 seconds)...${NC}"
    for i in {1..15}; do
        sleep 1
        if curl -s http://localhost:$RAG_API_PORT/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ RAG API started successfully (PID: $RAG_PID)${NC}"
            echo -e "   Health: http://localhost:$RAG_API_PORT/health"
            return 0
        fi
        # Check if process is still running
        if ! kill -0 $RAG_PID 2>/dev/null; then
            echo -e "${RED}❌ RAG API process died. Check logs:${NC}"
            tail -20 /tmp/syntheverse_rag_api.log
            return 1
        fi
    done
    
    echo -e "${RED}❌ RAG API failed to start${NC}"
    echo -e "   Check logs: tail -f /tmp/syntheverse_rag_api.log"
    return 1
}

# Function to start PoD UI
start_pod_ui() {
    echo -e "${BLUE}Starting PoD Submission UI...${NC}"
    
    if check_port $POD_UI_PORT; then
        echo -e "${YELLOW}PoD UI already running on port $POD_UI_PORT${NC}"
        return 0
    fi
    
    cd "$SCRIPT_DIR/ui_web"
    
    # Determine Python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python not found${NC}"
        return 1
    fi
    
    # Start in background and capture PID
    $PYTHON_CMD app.py > /tmp/syntheverse_pod_ui.log 2>&1 &
    UI_PID=$!
    echo $UI_PID > "$POD_UI_PID_FILE"
    
    # Wait for server to start
    echo -e "${YELLOW}Waiting for PoD UI to start...${NC}"
    for i in {1..10}; do
        sleep 2
        if curl -s http://localhost:$POD_UI_PORT/api/status > /dev/null 2>&1; then
            echo -e "${GREEN}✅ PoD Submission UI started successfully (PID: $UI_PID)${NC}"
            echo -e "   UI: http://localhost:$POD_UI_PORT"
            return 0
        fi
        # Check if process is still running
        if ! kill -0 $UI_PID 2>/dev/null; then
            echo -e "${RED}❌ PoD UI process died. Check logs:${NC}"
            tail -20 /tmp/syntheverse_pod_ui.log
            return 1
        fi
    done
    
    echo -e "${RED}❌ PoD UI failed to start${NC}"
    echo -e "   Check logs: tail -f /tmp/syntheverse_pod_ui.log"
    return 1
}

# Function to start all services
start_all() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Starting All Syntheverse Services${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Start RAG API first (PoD UI depends on it)
    start_rag_api
    echo ""
    
    # Start PoD UI
    start_pod_ui
    echo ""
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Service Status:${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    if check_port $RAG_API_PORT; then
        echo -e "${GREEN}✅ RAG API: http://localhost:$RAG_API_PORT${NC}"
    else
        echo -e "${RED}❌ RAG API: Not running${NC}"
    fi
    
    if check_port $POD_UI_PORT; then
        echo -e "${GREEN}✅ PoD Submission UI: http://localhost:$POD_UI_PORT${NC}"
    else
        echo -e "${RED}❌ PoD Submission UI: Not running${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Logs:${NC}"
    echo -e "  RAG API: tail -f /tmp/syntheverse_rag_api.log"
    echo -e "  PoD UI:  tail -f /tmp/syntheverse_pod_ui.log"
    echo ""
}

# Function to restart all services
restart_all() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Restarting All Syntheverse Services${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    stop_all
    echo ""
    sleep 2
    start_all
}

# Function to show status
show_status() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Syntheverse Services Status${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # RAG API
    if check_port $RAG_API_PORT; then
        echo -e "${GREEN}✅ RAG API${NC}"
        echo -e "   Port: $RAG_API_PORT"
        echo -e "   URL: http://localhost:$RAG_API_PORT"
        if [ -f "$RAG_API_PID_FILE" ]; then
            echo -e "   PID: $(cat $RAG_API_PID_FILE)"
        fi
        # Test health
        HEALTH=$(curl -s http://localhost:$RAG_API_PORT/health 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -o '"status":"[^"]*"' || echo "")
        if [ ! -z "$HEALTH" ]; then
            echo -e "   Health: $HEALTH"
        fi
    else
        echo -e "${RED}❌ RAG API: Not running${NC}"
    fi
    echo ""
    
    # PoD UI
    if check_port $POD_UI_PORT; then
        echo -e "${GREEN}✅ PoD Submission UI${NC}"
        echo -e "   Port: $POD_UI_PORT"
        echo -e "   URL: http://localhost:$POD_UI_PORT"
        if [ -f "$POD_UI_PID_FILE" ]; then
            echo -e "   PID: $(cat $POD_UI_PID_FILE)"
        fi
    else
        echo -e "${RED}❌ PoD Submission UI: Not running${NC}"
    fi
    echo ""
}

# Main command handler
case "${1:-start}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status"
        exit 1
        ;;
esac
