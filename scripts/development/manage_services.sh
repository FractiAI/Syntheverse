#!/bin/bash

# Syntheverse Service Manager
# Unified script for managing all development services
# Consolidates start_poc_ui.sh, start_all_services.sh, Syntheverse.sh and their stop counterparts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables from .env if it exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ports for different service combinations
POC_API_PORT=5001
FRONTEND_PORT=3001
RAG_API_PORT=8000

# PID files
POC_API_PID_FILE="/tmp/syntheverse_poc_api.pid"
FRONTEND_PID_FILE="/tmp/syntheverse_frontend.pid"
RAG_API_PID_FILE="/tmp/syntheverse_rag_api.pid"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

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
        print_warning "Killing processes on port $port..."
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# Function to auto-install dependencies
install_dependencies() {
    print_info "Installing dependencies..."

    # Install Python dependencies using the new installer
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found"
        return 1
    fi

    # Run dependency installer
    if ! $PYTHON_CMD "$SCRIPT_DIR/../utilities/install_deps.py"; then
        print_error "Failed to install dependencies"
        return 1
    fi

    print_status "Dependencies installed"
    return 0
}

# Function to start PoC API
start_poc_api() {
    print_info "Starting PoC API Server..."

    if check_port $POC_API_PORT; then
        print_warning "PoC API already running on port $POC_API_PORT"
        return 0
    fi

    cd "$PROJECT_ROOT/src/api/poc-api"

    # Determine Python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found"
        return 1
    fi

    # Start in background and capture PID
    $PYTHON_CMD app.py > /tmp/syntheverse_poc_api.log 2>&1 &
    POC_API_PID=$!
    echo $POC_API_PID > "$POC_API_PID_FILE"

    # Wait for server to start
    print_info "Waiting for PoC API to start..."
    for i in {1..10}; do
        sleep 1
        if curl -s http://localhost:$POC_API_PORT/health > /dev/null 2>&1; then
            print_status "PoC API started successfully (PID: $POC_API_PID)"
            print_info "  API: http://localhost:$POC_API_PORT"
            print_info "  Logs: tail -f /tmp/syntheverse_poc_api.log"
            return 0
        fi
        # Check if process is still running
        if ! kill -0 $POC_API_PID 2>/dev/null; then
            print_error "PoC API process died. Check logs:"
            tail -20 /tmp/syntheverse_poc_api.log
            return 1
        fi
    done

    print_error "PoC API failed to start"
    return 1
}

# Function to start Next.js frontend
start_frontend() {
    print_info "Starting Next.js Frontend..."

    if check_port $FRONTEND_PORT; then
        print_warning "Next.js Frontend already running on port $FRONTEND_PORT"
        return 0
    fi

    cd "$PROJECT_ROOT/src/frontend/poc-frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_info "Installing frontend dependencies..."
        npm install
    fi

    # Start in background and capture PID
    PORT=$FRONTEND_PORT npm run dev > /tmp/syntheverse_frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

    # Wait for server to start (takes longer for Next.js)
    print_info "Waiting for Next.js Frontend to start..."
    for i in {1..15}; do
        sleep 2
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            print_status "Next.js Frontend started successfully (PID: $FRONTEND_PID)"
            print_info "  UI: http://localhost:$FRONTEND_PORT"
            print_info "  Logs: tail -f /tmp/syntheverse_frontend.log"
            return 0
        fi
        # Check if process is still running
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            print_error "Next.js Frontend process died. Check logs:"
            tail -20 /tmp/syntheverse_frontend.log
            return 1
        fi
    done

    print_warning "Next.js Frontend may still be starting..."
    print_info "  Check logs: tail -f /tmp/syntheverse_frontend.log"
    return 0
}

# Function to start RAG API
start_rag_api() {
    print_info "Starting RAG API Server..."

    if check_port $RAG_API_PORT; then
        print_warning "RAG API already running on port $RAG_API_PORT"
        return 0
    fi

    cd "$PROJECT_ROOT/src/api/rag-api/api"

    # Determine Python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python not found"
        return 1
    fi

    # Check if GROQ_API_KEY is set
    if [ -z "$GROQ_API_KEY" ]; then
        print_warning "GROQ_API_KEY not set. RAG API may have limited functionality."
    else
        print_status "GROQ_API_KEY configured"
    fi

    # Start in background and capture PID
    $PYTHON_CMD rag_api.py > /tmp/syntheverse_rag_api.log 2>&1 &
    RAG_API_PID=$!
    echo $RAG_API_PID > "$RAG_API_PID_FILE"

    # Wait for server to start
    print_info "Waiting for RAG API to start..."
    for i in {1..15}; do
        sleep 1
        if curl -s http://localhost:$RAG_API_PORT/health > /dev/null 2>&1; then
            print_status "RAG API started successfully (PID: $RAG_API_PID)"
            print_info "  API: http://localhost:$RAG_API_PORT"
            print_info "  Docs: http://localhost:$RAG_API_PORT/docs"
            print_info "  Logs: tail -f /tmp/syntheverse_rag_api.log"
            return 0
        fi
        # Check if process is still running
        if ! kill -0 $RAG_API_PID 2>/dev/null; then
            print_error "RAG API process died. Check logs:"
            tail -20 /tmp/syntheverse_rag_api.log
            return 1
        fi
    done

    print_error "RAG API failed to start"
    return 1
}


# Function to stop PoC services
stop_poc() {
    print_info "Stopping PoC services..."

    # Stop PoC API
    if [ -f "$POC_API_PID_FILE" ]; then
        POC_API_PID=$(cat "$POC_API_PID_FILE")
        if kill -0 $POC_API_PID 2>/dev/null; then
            print_info "Stopping PoC API (PID: $POC_API_PID)..."
            kill $POC_API_PID
            rm "$POC_API_PID_FILE"
            print_status "PoC API stopped"
        else
            rm "$POC_API_PID_FILE"
        fi
    fi

    # Kill any process on port 5001
    if check_port $POC_API_PORT; then
        print_warning "Killing processes on port $POC_API_PORT..."
        kill_port $POC_API_PORT
    fi

    # Stop Frontend
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_info "Stopping Frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
            rm "$FRONTEND_PID_FILE"
            print_status "Frontend stopped"
        else
            rm "$FRONTEND_PID_FILE"
        fi
    fi

    # Kill any process on port 3001
    if check_port $FRONTEND_PORT; then
        print_warning "Killing processes on port $FRONTEND_PORT..."
        kill_port $FRONTEND_PORT
    fi

    # Kill any remaining Next.js processes
    pkill -f "next dev" 2>/dev/null || true

    print_status "PoC services stopped"
}

# Function to stop all services
stop_all() {
    print_info "Stopping all services..."

    # Stop RAG API
    if [ -f "$RAG_API_PID_FILE" ]; then
        RAG_API_PID=$(cat "$RAG_API_PID_FILE")
        if kill -0 $RAG_API_PID 2>/dev/null; then
            print_info "Stopping RAG API (PID: $RAG_API_PID)..."
            kill $RAG_API_PID
            rm "$RAG_API_PID_FILE"
            print_status "RAG API stopped"
        else
            rm "$RAG_API_PID_FILE"
        fi
    fi

    # Kill processes on ports
    if check_port $RAG_API_PORT; then
        print_warning "Killing processes on port $RAG_API_PORT..."
        kill_port $RAG_API_PORT
    fi

    # Kill by process name
    pkill -f "rag_api.py" 2>/dev/null || true
    pkill -f "ui_web/app.py" 2>/dev/null || true
    pkill -f "python.*app.py" 2>/dev/null || true

    print_status "All services stopped"
}


# Function to show status
show_status() {
    echo "=========================================="
    echo "Syntheverse Services Status"
    echo "=========================================="
    echo ""

    # PoC API
    if check_port $POC_API_PORT; then
        echo -e "${GREEN}✅ PoC API${NC}"
        echo "   Port: $POC_API_PORT"
        echo "   URL: http://localhost:$POC_API_PORT"
        if [ -f "$POC_API_PID_FILE" ]; then
            echo "   PID: $(cat $POC_API_PID_FILE)"
        fi
    else
        echo -e "${RED}❌ PoC API: Not running${NC}"
    fi
    echo ""

    # Frontend
    if check_port $FRONTEND_PORT; then
        echo -e "${GREEN}✅ Next.js Frontend${NC}"
        echo "   Port: $FRONTEND_PORT"
        echo "   URL: http://localhost:$FRONTEND_PORT"
        if [ -f "$FRONTEND_PID_FILE" ]; then
            echo "   PID: $(cat $FRONTEND_PID_FILE)"
        fi
    else
        echo -e "${RED}❌ Next.js Frontend: Not running${NC}"
    fi
    echo ""

    # RAG API
    if check_port $RAG_API_PORT; then
        echo -e "${GREEN}✅ RAG API${NC}"
        echo "   Port: $RAG_API_PORT"
        echo "   URL: http://localhost:$RAG_API_PORT"
        if [ -f "$RAG_API_PID_FILE" ]; then
            echo "   PID: $(cat $RAG_API_PID_FILE)"
        fi
    else
        echo -e "${RED}❌ RAG API: Not running${NC}"
    fi
    echo ""

}

# Main command handler
COMMAND=$1
SERVICE=$2

case "$COMMAND" in
    start)
        # Install dependencies first
        if ! install_dependencies; then
            exit 1
        fi

        case "$SERVICE" in
            poc)
                echo "=========================================="
                echo "Starting Syntheverse PoC UI System"
                echo "=========================================="
                echo ""

                start_poc_api
                echo ""
                start_frontend
                echo ""

                echo "=========================================="
                print_status "PoC UI System is running!"
                echo ""
                print_info "Frontend: http://localhost:$FRONTEND_PORT"
                print_info "API:      http://localhost:$POC_API_PORT"
                echo ""
                ;;
            all)
                echo "=========================================="
                echo "Starting All Syntheverse Services"
                echo "=========================================="
                echo ""

                start_rag_api
                echo ""

                echo "=========================================="
                print_status "All services are running!"
                echo ""
                print_info "RAG API:   http://localhost:$RAG_API_PORT"
                echo ""
                ;;
            *)
                echo "Usage: $0 start {poc|all}"
                echo ""
                echo "Services:"
                echo "  poc     - PoC API + Next.js Frontend"
                echo "  all     - RAG API"
                exit 1
                ;;
        esac
        ;;
    stop)
        case "$SERVICE" in
            poc)
                echo "=========================================="
                echo "Stopping Syntheverse PoC UI System"
                echo "=========================================="
                echo ""
                stop_poc
                ;;
            all)
                echo "=========================================="
                echo "Stopping All Syntheverse Services"
                echo "=========================================="
                echo ""
                stop_all
                ;;
            *)
                echo "Usage: $0 stop {poc|all}"
                echo ""
                echo "Services:"
                echo "  poc     - PoC API + Next.js Frontend"
                echo "  all     - RAG API"
                exit 1
                ;;
        esac
        ;;
    restart)
        case "$SERVICE" in
            poc|all)
                echo "=========================================="
                echo "Restarting Syntheverse $SERVICE Services"
                echo "=========================================="
                echo ""

                # Stop services
                case "$SERVICE" in
                    poc) stop_poc ;;
                    all) stop_all ;;
                esac
                echo ""
                sleep 2

                # Start services
                case "$SERVICE" in
                    poc) start_poc_api && echo "" && start_frontend ;;
                    all) start_rag_api ;;
                esac
                echo ""

                print_status "$SERVICE services restarted!"
                ;;
            *)
                echo "Usage: $0 restart {poc|all}"
                exit 1
                ;;
        esac
        ;;
    status)
        show_status
        ;;
    *)
        echo "Syntheverse Service Manager"
        echo "==========================="
        echo ""
        echo "Usage: $0 {start|stop|restart|status} [service]"
        echo ""
        echo "Commands:"
        echo "  start   - Start services"
        echo "  stop    - Stop services"
        echo "  restart - Restart services"
        echo "  status  - Show service status"
        echo ""
        echo "Services:"
        echo "  poc     - PoC API + Next.js Frontend (port 5001 + 3001)"
        echo "  all     - RAG API (port 8000)"
        echo ""
        echo "Examples:"
        echo "  $0 start poc      # Start PoC UI system"
        echo "  $0 stop poc       # Stop PoC UI system"
        echo "  $0 start all      # Start all services"
        echo "  $0 restart poc    # Restart PoC system"
        echo "  $0 status         # Show all service status"
        exit 1
        ;;
esac
