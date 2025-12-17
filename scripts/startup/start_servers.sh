#!/bin/bash

# Syntheverse PoC System Startup Script
# This script starts all necessary servers for the Syntheverse PoC system

echo "🌟 SYNTHVERSE PoC SYSTEM STARTUP"
echo "=================================="

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local name=$2

    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        print_warning "Killing $name process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
        sleep 1
    fi
}

# Function to check if port is available
check_port() {
    local port=$1
    local name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Port $port ($name) is still in use"
        return 1
    else
        print_status "Port $port ($name) is available"
        return 0
    fi
}

# Function to start server in background
start_server() {
    local command=$1
    local name=$2
    local port=$3

    print_info "Starting $name on port $port..."

    # Start server in background
    eval "$command" &
    local pid=$!

    # Wait a moment for server to start
    sleep 3

    # Check if server is running
    if kill -0 $pid 2>/dev/null; then
        print_status "$name started successfully (PID: $pid)"

        # Test server connectivity
        if curl -s --max-time 5 "http://127.0.0.1:$port" > /dev/null 2>&1; then
            print_status "$name is responding on port $port"
        else
            print_warning "$name started but may not be fully ready yet"
        fi
    else
        print_error "$name failed to start"
        return 1
    fi
}

# Main startup sequence
main() {
    echo ""
    print_info "Step 1: Cleaning up existing processes..."

    # Kill any existing servers
    kill_port 5000 "Web UI"
    kill_port 5001 "PoC API"
    kill_port 3001 "Next.js Frontend"
    kill_port 8000 "Demo Server"

    echo ""
    print_info "Step 2: Checking port availability..."

    # Check if ports are now free
    check_port 5000 "Web UI" || exit 1
    check_port 5001 "PoC API" || exit 1
    check_port 3001 "Next.js Frontend" || exit 1

    echo ""
    print_info "Step 3: Starting Syntheverse servers..."

    # Start PoC API server
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    POC_API_CMD="cd $PROJECT_ROOT && FLASK_SKIP_DOTENV=1 PYTHONPATH=$PROJECT_ROOT/src/core:$PROJECT_ROOT/src:$PROJECT_ROOT python3 src/api/poc-api/app.py"
    start_server "$POC_API_CMD" "PoC API Server" "5001"

    # Start Web UI server (legacy)
    WEB_UI_CMD="cd $PROJECT_ROOT && FLASK_SKIP_DOTENV=1 python3 src/frontend/web-legacy/app.py"
    start_server "$WEB_UI_CMD" "Web UI Server (Legacy)" "5000"
    
    # Start Next.js Frontend
    FRONTEND_DIR="$PROJECT_ROOT/src/frontend/poc-frontend"
    if [ -d "$FRONTEND_DIR" ]; then
        NEXTJS_CMD="cd $FRONTEND_DIR && PORT=3001 npm run dev"
        start_server "$NEXTJS_CMD" "Next.js Frontend" "3001"
    fi

    echo ""
    print_info "Step 4: System startup complete!"

    echo ""
    echo "🌐 SYNTHVERSE SERVERS RUNNING:"
    echo "================================"
    print_status "Web UI (Legacy): http://127.0.0.1:5000"
    print_status "PoC API:         http://127.0.0.1:5001"
    print_status "Next.js UI:      http://127.0.0.1:3001"
    print_status "API Status:      http://127.0.0.1:5001/api/status"
    echo ""
    print_info "Open http://127.0.0.1:3001 in your browser to access the Syntheverse UI (Next.js)"
    print_info "Or http://127.0.0.1:5000 for the legacy UI"
    echo ""
    print_info "Press Ctrl+C to stop all servers"
    echo ""

    # Wait for user input to keep script running
    print_info "Servers are running in background. Press Enter to stop..."
    read -r

    # Cleanup on exit
    print_info "Shutting down servers..."
    kill_port 5000 "Web UI"
    kill_port 5001 "PoC API"
    kill_port 3001 "Next.js Frontend"
    print_status "All servers stopped. Goodbye! 👋"
}

# Run main function
main "$@"
