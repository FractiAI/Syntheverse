#!/bin/bash

# Syntheverse Interactive Examples & Testing Menu
# Unified access to all examples, tests, and scripts

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CURRENT_DIR="$(pwd)"
LOG_FILE="$PROJECT_ROOT/syntheverse_run.log"

# Function to print colored status messages
print_status() {
    local message="$1"
    local status="${2:-ℹ️}"
    local color="$BLUE"

    case "$status" in
        "✅") color="$GREEN" ;;
        "❌") color="$RED" ;;
        "⚠️") color="$YELLOW" ;;
        "🚀") color="$PURPLE" ;;
        "🔧") color="$CYAN" ;;
    esac

    echo -e "${color}${status} ${message}${NC}"
}

# Function to print section headers
print_header() {
    local title="$1"
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}${title}${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if file exists and is executable
script_exists() {
    local script_path="$1"
    [[ -f "$script_path" && -x "$script_path" ]]
}

# Function to navigate to project root
cd_project_root() {
    cd "$PROJECT_ROOT" || {
        print_status "Failed to navigate to project root: $PROJECT_ROOT" "❌"
        return 1
    }
}

# Function to navigate back to original directory
cd_original_dir() {
    cd "$CURRENT_DIR" || {
        print_status "Failed to navigate back to original directory: $CURRENT_DIR" "❌"
        return 1
    }
}

# Function to wait for user input
wait_for_enter() {
    local message="${1:-Press Enter to continue...}"
    echo ""
    read -p "$message" -r
}

# Function to log messages
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Function to log menu selections and major actions
log_action() {
    local action="$1"
    local details="${2:-}"
    log_message "ACTION" "$action${details:+: $details}"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "🔧 PREREQUISITES CHECK"

    local all_good=true

    # Load environment variables from .env file if it exists
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs 2>/dev/null)
    fi

    # Check Python version
    if command_exists python3; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        local python_major=$(echo "$python_version" | cut -d. -f1)
        local python_minor=$(echo "$python_version" | cut -d. -f2)

        if [[ $python_major -ge 3 && $python_minor -ge 8 ]]; then
            print_status "Python $python_version - OK"
        else
            print_status "Python $python_version - Requires Python 3.8+" "❌"
            all_good=false
        fi
    else
        print_status "Python3 not found" "❌"
        all_good=false
    fi

    # Check Node.js version
    if command_exists node; then
        local node_version=$(node --version 2>&1)
        local node_major=$(echo "$node_version" | sed 's/v//' | cut -d. -f1)

        if [[ $node_major -ge 18 ]]; then
            print_status "Node.js $node_version - OK"
        else
            print_status "Node.js $node_version - Requires Node.js 18+" "❌"
            all_good=false
        fi
    else
        print_status "Node.js not found" "❌"
        all_good=false
    fi

    # Check GROQ_API_KEY
    if [[ -n "${GROQ_API_KEY:-}" ]]; then
        print_status "GROQ_API_KEY is set"
    else
        print_status "GROQ_API_KEY not set (required for AI evaluation)" "⚠️"
        all_good=false
    fi

    # Check and install Python dependencies
    print_status "Checking Python dependencies..."
    cd_project_root

    # Required packages for the system
    local required_packages=("fastapi" "flask" "uvicorn" "requests" "web3")

    for package in "${required_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_status "$package available"
        else
            print_status "$package not available - installing..." "⚠️"
            if pip3 install "$package" > /tmp/pip_install_$package.log 2>&1; then
                print_status "✅ $package installed successfully"
            else
                # Check if it's due to externally managed environment
                if grep -q "externally-managed-environment" /tmp/pip_install_$package.log 2>/dev/null; then
                    print_status "❌ $package installation blocked by system Python policy" "❌"
                    print_status "Consider using a virtual environment:" "ℹ️"
                    echo "  python3 -m venv syntheverse_env"
                    echo "  source syntheverse_env/bin/activate"
                    echo "  pip install $package"
                    print_status "Or install system-wide with: brew install python-$package" "ℹ️"
                else
                    print_status "❌ Failed to install $package" "❌"
                    print_status "Check log: /tmp/pip_install_$package.log"
                fi
                all_good=false
            fi
        fi
    done

    cd_original_dir

    # Check and install Node.js dependencies
    if [[ -f "$PROJECT_ROOT/src/frontend/poc-frontend/package.json" ]]; then
        if [[ -d "$PROJECT_ROOT/src/frontend/poc-frontend/node_modules" ]]; then
            print_status "Frontend dependencies installed"
        else
            print_status "Frontend dependencies not installed - installing..." "⚠️"
            cd_project_root
            cd "src/frontend/poc-frontend" || {
                print_status "Failed to navigate to frontend directory" "❌"
                all_good=false
                cd_original_dir
                return 1
            }

            print_status "Running npm install (this may take a few minutes)..."
            if npm install > /tmp/npm_install.log 2>&1; then
                print_status "✅ Frontend dependencies installed successfully"
                print_status "Installation log saved to: /tmp/npm_install.log"
            else
                print_status "❌ Failed to install frontend dependencies" "❌"
                print_status "Check log: /tmp/npm_install.log"
                all_good=false
            fi
            cd_original_dir
        fi
    else
        print_status "Frontend package.json not found" "⚠️"
        all_good=false
    fi

    # Check port availability
    print_status "Checking port availability..."
    local ports=(3001 5001 5000 8000 8545)

    for port in "${ports[@]}"; do
        if command_exists lsof; then
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                print_status "Port $port in use" "⚠️"
            else
                print_status "Port $port available"
            fi
        else
            print_status "Cannot check port $port (lsof not available)" "⚠️"
        fi
    done

    echo ""
    if $all_good; then
        print_status "All prerequisites checks passed!" "✅"
    else
        print_status "Some prerequisites are missing or misconfigured" "⚠️"
    fi

    wait_for_enter
}

# Function to check service health
check_health() {
    print_header "🔍 HEALTH CHECKS"

    cd_project_root

    # Check PoC API (port 5001)
    print_status "Checking PoC API (port 5001)..."
    if command_exists curl; then
        if curl -s --max-time 5 http://localhost:5001/health >/dev/null 2>&1; then
            print_status "PoC API is running" "✅"
        else
            print_status "PoC API not responding" "❌"
        fi
    else
        print_status "Cannot check PoC API (curl not available)" "⚠️"
    fi

    # Check Frontend (port 3001)
    print_status "Checking Frontend (port 3001)..."
    if command_exists curl; then
        if curl -s --max-time 5 http://localhost:3001 >/dev/null 2>&1; then
            print_status "Frontend is running" "✅"
        else
            print_status "Frontend not responding" "❌"
        fi
    else
        print_status "Cannot check Frontend (curl not available)" "⚠️"
    fi

    # Check Legacy Web UI (port 5000)
    print_status "Checking Legacy Web UI (port 5000)..."
    if command_exists curl; then
        if curl -s --max-time 5 http://localhost:5000 >/dev/null 2>&1; then
            print_status "Legacy Web UI is running" "✅"
        else
            print_status "Legacy Web UI not responding" "❌"
        fi
    else
        print_status "Cannot check Legacy Web UI (curl not available)" "⚠️"
    fi

    # Check RAG API (port 8000)
    print_status "Checking RAG API (port 8000)..."
    if command_exists curl; then
        if curl -s --max-time 5 http://localhost:8000/health >/dev/null 2>&1; then
            print_status "RAG API is running" "✅"
        else
            print_status "RAG API not responding" "❌"
        fi
    else
        print_status "Cannot check RAG API (curl not available)" "⚠️"
    fi

    # Check local blockchain (port 8545)
    print_status "Checking Local Blockchain (port 8545)..."
    if command_exists curl; then
        if curl -s --max-time 5 http://localhost:8545 >/dev/null 2>&1; then
            print_status "Local blockchain is running" "✅"
        else
            print_status "Local blockchain not responding" "❌"
        fi
    else
        print_status "Cannot check Local blockchain (curl not available)" "⚠️"
    fi

    # Check file system access
    print_status "Checking file system access..."

    if [[ -d "src/data" ]]; then
        print_status "Data directory accessible" "✅"
    else
        print_status "Data directory not accessible" "❌"
    fi

    if [[ -d "src/core" ]]; then
        print_status "Core modules accessible" "✅"
    else
        print_status "Core modules not accessible" "❌"
    fi

    cd_original_dir

    echo ""
    print_status "Health check completed"

    wait_for_enter
}

# Function to quickly verify setup without re-running installations
verify_setup_quick() {
    print_status "Performing quick setup verification..."

    local verification_passed=true

    # Check GROQ API Key
    if [[ -n "${GROQ_API_KEY:-}" ]]; then
        print_status "✅ GROQ_API_KEY is set"
    else
        print_status "⚠️ GROQ_API_KEY not set in environment"
        # Try to load from .env file
        if [[ -f "$PROJECT_ROOT/.env" ]]; then
            export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs 2>/dev/null)
            if [[ -n "${GROQ_API_KEY:-}" ]]; then
                print_status "✅ GROQ_API_KEY loaded from .env file"
            else
                print_status "⚠️ GROQ_API_KEY not found in .env file"
                verification_passed=false
            fi
        else
            print_status "⚠️ No .env file found"
            verification_passed=false
        fi
    fi

    # Quick check of key Python packages
    local key_packages=("fastapi" "flask" "requests")
    for package in "${key_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_status "✅ $package available"
        else
            print_status "❌ $package not available" "❌"
            verification_passed=false
        fi
    done

    # Check Node.js dependencies
    if [[ -d "$PROJECT_ROOT/src/frontend/poc-frontend/node_modules" ]]; then
        print_status "✅ Frontend dependencies installed"
    else
        print_status "❌ Frontend dependencies not installed" "❌"
        verification_passed=false
    fi

    # Check for port conflicts
    local ports=(3001 5001 5000 8000 8545)
    local port_conflicts=()
    for port in "${ports[@]}"; do
        if command_exists lsof; then
            local pids=$(lsof -ti:$port 2>/dev/null)
            if [[ -n "$pids" ]]; then
                port_conflicts+=("$port")
            fi
        fi
    done

    if [[ ${#port_conflicts[@]} -gt 0 ]]; then
        print_status "⚠️ Ports in use: ${port_conflicts[*]} - will be cleaned on startup"
    else
        print_status "✅ No port conflicts detected"
    fi

    if $verification_passed; then
        print_status "✅ Setup verification passed!" "✅"
    else
        print_status "⚠️ Setup verification found issues - some features may be limited"
    fi

    return $([ $verification_passed = true ] && echo 0 || echo 1)
}

# Function to check if system is ready to run
check_system_readiness() {
    print_header "🚀 SYSTEM READINESS CHECK"

    local ready=true

    # Run prerequisites check
    print_status "Checking prerequisites..."
    # Capture output to avoid double printing
    local prereq_output
    prereq_output=$(check_prerequisites 2>&1)
    local prereq_exit=$?

    if [[ $prereq_exit -ne 0 ]]; then
        ready=false
    fi

    echo ""
    print_status "Checking service health..."
    # Check if key services are running
    local services=("poc_api" "rag_api" "frontend")
    local services_running=0

    for service in "${services[@]}"; do
        local url_key="${service}_url"
        local url=$(grep "$url_key" "$PROJECT_ROOT/tests/test_config.json" 2>/dev/null | sed 's/.*"http[^"]*".*/\1/' || echo "")
        if [[ -z "$url" ]]; then
            # Fallback URLs
            case $service in
                "poc_api") url="http://localhost:5001" ;;
                "rag_api") url="http://localhost:8000" ;;
                "frontend") url="http://localhost:3001" ;;
            esac
        fi

        if command_exists curl; then
            if curl -s --max-time 3 "$url/health" >/dev/null 2>&1; then
                print_status "✅ $service is running"
                ((services_running++))
            else
                print_status "❌ $service is not running" "❌"
            fi
        else
            print_status "⚠️ Cannot check $service (curl not available)"
        fi
    done

    echo ""
    if $ready && [[ $services_running -eq 3 ]]; then
        print_status "🎉 SYSTEM IS READY TO RUN!" "✅"
        print_status "All prerequisites met and services are running."
    elif $ready && [[ $services_running -gt 0 ]]; then
        print_status "⚠️ SYSTEM PARTIALLY READY" "⚠️"
        print_status "Prerequisites OK, but some services need to be started."
    else
        print_status "❌ SYSTEM NOT READY" "❌"
        print_status "Run comprehensive setup to prepare the system."
    fi

    wait_for_enter
}

# Function to run quick start (setup + startup)
run_quick_start() {
    print_header "⚡ QUICK START - COMPLETE SYSTEM LAUNCH"

    print_status "This will run comprehensive setup and start the full system."
    echo ""
    read -p "Continue? (y/n): " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Quick start cancelled."
        wait_for_enter
        return
    fi

    # Run comprehensive setup
    run_comprehensive_setup

    # Check if setup was successful
    if [[ $? -eq 0 ]]; then
        # Start the full system
        print_status "Starting full system..."
        run_startup_script "start_servers.py" "Full System Startup"
    else
        print_status "Setup failed - not starting system." "❌"
        wait_for_enter
    fi
}

# Function to show setup & validation menu
show_setup_validation_menu() {
    while true; do
        print_header "🔧 SETUP & VALIDATION"
        echo "Choose an option:"
        echo ""
        echo "1) 🔍 Check Prerequisites      - Verify Python, Node.js, dependencies"
        echo "2) ❤️  Check Health            - Verify running services"
        echo "3) 🔄 Check All               - Run both checks"
        echo "4) 🚀 Check System Readiness  - Comprehensive readiness check"
        echo "5) 🔧 Run Comprehensive Setup - Install all dependencies, set API keys, prepare environment"
        echo "6) ⚡ Quick Start             - Complete setup + system startup"
        echo "7) ↩️  Back to Main Menu"
        echo ""

        read -p "Enter your choice (1-7): " choice

        case "$choice" in
            1) check_prerequisites ;;
            2) check_health ;;
            3) check_prerequisites && check_health ;;
            4) check_system_readiness ;;
            5) run_comprehensive_setup ;;
            6) run_quick_start ;;
            7) return ;;
            *) print_status "Invalid choice. Please select 1-7." "❌" ;;
        esac
    done
}

# Function to show main menu
show_main_menu() {
    clear
    echo -e "${PURPLE}🌟 SYNTHVERSE INTERACTIVE MENU${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${CYAN}Project Root:${NC} $PROJECT_ROOT"
    echo -e "${CYAN}Current Dir:${NC} $CURRENT_DIR"
    echo ""

    echo "Choose a category:"
    echo ""
    echo "1) 🔧 Setup & Validation    - Check prerequisites and health"
    echo "2) 📚 Examples              - Run demo scripts and view interfaces"
    echo "3) 🧪 Tests                 - Run test suites and validation"
    echo "4) 🚀 Startup Scripts       - Start system services"
    echo "5) 🔧 Service Management    - Check and manage running services"
    echo "6) 💻 Development Scripts   - Development workflow tools"
    echo "7) 📦 Deployment Scripts    - Deploy contracts and services"
    echo "8) 🔧 Utilities             - Maintenance and cleanup tools"
    echo "9) ❌ Exit"
    echo ""
}

# Function to handle menu selection
handle_menu_selection() {
    local choice="$1"

    case "$choice" in
        1) log_action "Menu Selection" "Setup & Validation"; show_setup_validation_menu ;;
        2) log_action "Menu Selection" "Examples"; show_examples_menu ;;
        3) log_action "Menu Selection" "Tests"; show_tests_menu ;;
        4) log_action "Menu Selection" "Startup Scripts"; show_startup_menu ;;
        5) log_action "Menu Selection" "Service Management"; show_service_management_menu ;;
        6) log_action "Menu Selection" "Development Scripts"; show_development_menu ;;
        7) log_action "Menu Selection" "Deployment Scripts"; show_deployment_menu ;;
        8) log_action "Menu Selection" "Utilities"; show_utilities_menu ;;
        9) log_action "Menu Selection" "Exit"; exit_menu ;;
        *) print_status "Invalid choice. Please select 1-9." "❌" ;;
    esac
}

# Placeholder functions for sub-menus (to be implemented)

# Function to run demo PoC system
run_demo_poc_system() {
    print_header "🚀 RUNNING PoC SYSTEM DEMO"

    local demo_script="$SCRIPT_DIR/demo_poc_system.py"

    if [[ -f "$demo_script" ]]; then
        print_status "Running demo_poc_system.py..."
        cd_project_root
        python3 "$demo_script"
        cd_original_dir
        echo ""
        print_status "Demo completed"
    else
        print_status "Demo script not found: $demo_script" "❌"
    fi

    wait_for_enter
}

# Function to open HTML demo in browser
open_html_demo() {
    local demo_name="$1"
    local html_file="$SCRIPT_DIR/${demo_name}.html"

    print_header "🌐 OPENING $demo_name DEMO"

    if [[ -f "$html_file" ]]; then
        print_status "Opening $html_file in browser..."

        # Try different browser commands
        if command_exists xdg-open; then
            xdg-open "$html_file" 2>/dev/null &
        elif command_exists open; then
            open "$html_file" 2>/dev/null &
        elif command_exists start; then
            start "$html_file" 2>/dev/null &
        else
            print_status "Could not open browser automatically" "⚠️"
            print_status "Please open manually: $html_file"
        fi

        print_status "HTML demo opened (or open manually if browser didn't launch)"
    else
        print_status "HTML demo file not found: $html_file" "❌"
    fi

    wait_for_enter
}

# Function to show examples menu
show_examples_menu() {
    while true; do
        print_header "📚 EXAMPLES"
        echo "Choose an example to run:"
        echo ""
        echo "1) 🐍 Run PoC System Demo    - demo_poc_system.py simulation"
        echo "2) 🌐 Open Interface Demo    - demo_interface.html in browser"
        echo "3) 🧪 Open Test UI Demo      - test_ui.html in browser"
        echo "4) ↩️  Back to Main Menu"
        echo ""

        read -p "Enter your choice (1-4): " choice

        case "$choice" in
            1) run_demo_poc_system ;;
            2) open_html_demo "demo_interface" ;;
            3) open_html_demo "test_ui" ;;
            4) return ;;
            *) print_status "Invalid choice. Please select 1-4." "❌" ;;
        esac
    done
}

# Function to run all tests
run_all_tests() {
    print_header "🚀 RUNNING ALL TESTS"

    if command_exists python3 && python3 -c "import pytest" 2>/dev/null; then
        print_status "Running complete test suite with pytest..."

        cd "$PROJECT_ROOT"
        # Enable pipefail to propagate pytest exit code through the pipeline
        set -o pipefail
        if python3 -m pytest tests/ -v --tb=short --maxfail=10 \
            --junitxml="$PROJECT_ROOT/tests/results/all_tests.xml" \
            2>&1 | tee "$PROJECT_ROOT/tests/results/all_tests.log"; then
            print_status "All tests completed successfully!" "✅"
        else
            local exit_code=$?
            print_status "Some tests failed (exit code: $exit_code)" "❌"
            print_status "Check detailed results in: $PROJECT_ROOT/tests/results/" "ℹ️"
            if [[ -f "$PROJECT_ROOT/tests/results/all_tests.log" ]]; then
                echo ""
                print_status "Recent failures:" "ℹ️"
                grep -E "(FAILED|ERROR|passed|failed)" "$PROJECT_ROOT/tests/results/all_tests.log" | tail -5
            fi
        fi
        # Reset pipefail to default behavior
        set +o pipefail
    else
        print_status "pytest not available, falling back to shell-based tests" "⚠️"

        local test_script="$PROJECT_ROOT/tests/run_tests.sh"
        if [[ -f "$test_script" ]]; then
            print_status "Running basic test suite..."
            bash "$test_script" --all
        else
            print_status "Test runner not found: $test_script" "❌"
        fi
    fi

    wait_for_enter
}

# Function to run service integration tests
run_service_tests() {
    print_header "🔗 RUNNING SERVICE INTEGRATION TESTS"

    print_status "⚠️  NOTE: These tests require services to be running first!" "⚠️"
    print_status "Start services using: Main Menu → 4) 🚀 Startup Scripts" "ℹ️"
    echo ""

    local test_script="$PROJECT_ROOT/tests/run_tests.sh"

    if [[ -f "$test_script" ]]; then
        print_status "Running service integration tests..."
        bash "$test_script" --quick
    else
        print_status "Test runner not found: $test_script" "❌"
    fi

    wait_for_enter
}

# Function to run Python unit tests only
run_unit_tests() {
    print_header "🧪 RUNNING PYTHON UNIT TESTS"

    if command_exists python3 && python3 -c "import pytest" 2>/dev/null; then
        print_status "Running Python unit tests with pytest..."

        cd "$PROJECT_ROOT"
        if python3 -m pytest tests/ -v --tb=short --maxfail=5 \
            --ignore=tests/test_poc_quick.sh \
            --ignore=tests/test_poc_frontend.sh \
            --junitxml="$PROJECT_ROOT/tests/results/unit_tests.xml" \
            2>&1 | tee "$PROJECT_ROOT/tests/results/unit_tests.log"; then
            print_status "Unit tests completed successfully!" "✅"
        else
            local exit_code=$?
            print_status "Some unit tests failed (exit code: $exit_code)" "❌"
            print_status "Check detailed results in: $PROJECT_ROOT/tests/results/" "ℹ️"
        fi
    else
        print_status "pytest not available" "❌"
    fi

    wait_for_enter
}

# Function to run frontend tests
run_frontend_tests() {
    print_header "🌐 RUNNING FRONTEND TESTS"

    local test_script="$PROJECT_ROOT/tests/run_tests.sh"

    if [[ -f "$test_script" ]]; then
        print_status "Running frontend tests..."
        bash "$test_script" --frontend
    else
        print_status "Test runner not found: $test_script" "❌"
    fi

    wait_for_enter
}

# Function to run individual test
run_individual_test() {
    local test_option="$1"
    local test_name="$2"

    print_header "🧪 RUNNING $test_name"

    local test_script="$PROJECT_ROOT/tests/run_tests.sh"

    if [[ -f "$test_script" ]]; then
        print_status "Running $test_name..."
        bash "$test_script" "$test_option"
    else
        print_status "Test runner not found: $test_script" "❌"
    fi

    wait_for_enter
}

# Function to show tests menu
show_tests_menu() {
    while true; do
        print_header "🧪 TESTS"
        echo "Choose a test option:"
        echo ""
        echo "1) 🚀 Run All Tests         - Complete test suite (unit + integration)"
        echo "2) ⚡ Run Service Tests      - Integration tests (requires services running)"
        echo "3) 🌐 Run Frontend Tests    - UI and interface tests"
        echo "4) 🐍 Run Unit Tests         - Python unit tests only"
        echo ""
        echo "Individual Tests:"
        echo "5) 📝 Submission Test       - Basic submission functionality"
        echo "6) 🔄 Flow Test             - Submission flow validation"
        echo "7) 🌊 Full Flow Test        - End-to-end submission process"
        echo "8) 🤖 RAG API Test          - RAG API connectivity"
        echo "9) ❓ RAG Query Test        - RAG PoD query functionality"
        echo "10) ⏱️  RAG Timeout Test     - RAG timeout handling"
        echo ""
        echo "11) 🧹 Clean Test Results    - Remove old test outputs"
        echo "12) ↩️  Back to Main Menu"
        echo ""

        read -p "Enter your choice (1-12): " choice

        case "$choice" in
            1) run_all_tests ;;
            2) run_service_tests ;;
            3) run_frontend_tests ;;
            4) run_individual_test "--python" "Python Tests" ;;
            5) run_individual_test "--submission" "Submission Test" ;;
            6) run_individual_test "--flow" "Flow Test" ;;
            7) run_individual_test "--full-flow" "Full Flow Test" ;;
            8) run_individual_test "--rag-api" "RAG API Test" ;;
            9) run_individual_test "--rag-query" "RAG Query Test" ;;
            10) run_individual_test "--rag-timeout" "RAG Timeout Test" ;;
            11)
                print_header "🧹 CLEANING TEST RESULTS"
                bash "$PROJECT_ROOT/tests/run_tests.sh" --clean
                wait_for_enter
                ;;
            12) return ;;
            *) print_status "Invalid choice. Please select 1-12." "❌" ;;
        esac
    done
}

# Function to run comprehensive setup
run_comprehensive_setup() {
    print_header "🔧 COMPREHENSIVE SYSTEM SETUP"

    local setup_success=true

    # Step 1: Environment setup
    print_status "Step 1: Setting up environment variables..."

    # First try to load from .env file
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        print_status "Loading environment from .env file..."
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs 2>/dev/null)
        if [[ -n "${GROQ_API_KEY:-}" ]]; then
            print_status "✅ Environment variables loaded from .env file"
        else
            print_status "⚠️ .env file found but GROQ_API_KEY not set"
        fi
    fi

    if [[ -z "${GROQ_API_KEY:-}" ]]; then
        print_status "GROQ_API_KEY not set. Please set it:" "⚠️"
        echo "export GROQ_API_KEY='your-api-key-here'"
        echo ""
        read -p "Do you want to set GROQ_API_KEY now? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter your GROQ API key: " groq_key
            if [[ -n "$groq_key" ]]; then
                export GROQ_API_KEY="$groq_key"
                print_status "✅ GROQ_API_KEY set for this session"
                # Also add to .env file for persistence
                if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
                    echo "# Syntheverse Environment Configuration" > "$PROJECT_ROOT/.env"
                    echo "" >> "$PROJECT_ROOT/.env"
                fi
                # Update or add GROQ_API_KEY in .env file
                if grep -q "^GROQ_API_KEY=" "$PROJECT_ROOT/.env" 2>/dev/null; then
                    sed -i.bak "s/^GROQ_API_KEY=.*/GROQ_API_KEY=$groq_key/" "$PROJECT_ROOT/.env"
                    rm -f "$PROJECT_ROOT/.env.bak"
                else
                    echo "GROQ_API_KEY=$groq_key" >> "$PROJECT_ROOT/.env"
                fi
                print_status "✅ GROQ_API_KEY saved to .env file"
            else
                print_status "⚠️ GROQ_API_KEY not set - some features will be limited"
            fi
        else
            print_status "⚠️ Skipping GROQ_API_KEY setup - some features will be limited"
        fi
    else
        print_status "✅ GROQ_API_KEY is set"
    fi

    # Step 2: Clean up existing processes
    print_status "Step 2: Cleaning up existing processes..."
    local ports=(3001 5001 5000 8000 8545)
    for port in "${ports[@]}"; do
        if command_exists lsof; then
            local pids=$(lsof -ti:$port 2>/dev/null)
            if [[ -n "$pids" ]]; then
                print_status "Killing process on port $port (PID: $pids)" "⚠️"
                kill -9 $pids 2>/dev/null
                sleep 1
            fi
        fi
    done

    # Step 3: Install all dependencies
    print_status "Step 3: Installing all dependencies..."

    # Python dependencies
    print_status "Installing Python dependencies..."
    cd_project_root
    local python_packages=("fastapi" "flask" "uvicorn" "requests" "web3" "pydantic" "python-multipart")
    local venv_recommended=false

    for package in "${python_packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            print_status "Installing $package..."
            if pip3 install "$package" > /tmp/setup_pip_$package.log 2>&1; then
                print_status "✅ $package installed"
            else
                # Check for externally managed environment
                if grep -q "externally-managed-environment" /tmp/setup_pip_$package.log 2>/dev/null; then
                    if [[ "$venv_recommended" == false ]]; then
                        print_status "⚠️ System Python is externally managed" "⚠️"
                        print_status "Consider creating a virtual environment:" "ℹ️"
                        echo "  python3 -m venv syntheverse_env"
                        echo "  source syntheverse_env/bin/activate"
                        echo "  pip install -r requirements.txt"
                        venv_recommended=true
                    fi
                    print_status "❌ $package blocked by system policy - see venv instructions above" "❌"
                else
                    print_status "❌ Failed to install $package" "❌"
                fi
                setup_success=false
            fi
        else
            print_status "$package already installed"
        fi
    done

    # Node.js dependencies
    if [[ -f "src/frontend/poc-frontend/package.json" ]]; then
        print_status "Installing Node.js dependencies..."
        cd "src/frontend/poc-frontend"
        if [[ ! -d "node_modules" ]]; then
            print_status "Running npm install..."
            if npm install > /tmp/setup_npm_install.log 2>&1; then
                print_status "✅ Frontend dependencies installed"
            else
                print_status "❌ Failed to install frontend dependencies" "❌"
                setup_success=false
            fi
        else
            print_status "Frontend dependencies already installed"
        fi
        cd_project_root
    fi

    cd_original_dir

    # Step 4: Verify setup
    print_status "Step 4: Verifying setup..."
    verify_setup_quick

    if $setup_success; then
        print_status "🎉 COMPREHENSIVE SETUP COMPLETED SUCCESSFULLY!" "✅"
        print_status "The system is now ready to run."
    else
        print_status "⚠️ Setup completed with some issues. Please review the logs above."
    fi

    wait_for_enter
}

# Function to aggressively clean ports
clean_ports_aggressively() {
    print_status "Performing aggressive port cleanup..."

    local ports=(3001 5001 5000 8000 8545)
    local cleaned_any=false

    for port in "${ports[@]}"; do
        if command_exists lsof; then
            # Get all PIDs using this port
            local pids=$(lsof -ti:$port 2>/dev/null)
            if [[ -n "$pids" ]]; then
                # Show what processes are using the port
                local process_info=$(lsof -i:$port 2>/dev/null | tail -n +2 | awk '{print $1, $2}' | sort -u)
                print_status "Port $port in use by: $process_info" "⚠️"

                # Kill all PIDs using this port
                for pid in $pids; do
                    print_status "Killing PID $pid on port $port" "⚠️"
                    kill -9 $pid 2>/dev/null || true
                done

                cleaned_any=true

                # Wait and verify port is freed
                local attempts=0
                while [[ $attempts -lt 5 ]]; do
                    sleep 1
                    local still_in_use=$(lsof -ti:$port 2>/dev/null)
                    if [[ -z "$still_in_use" ]]; then
                        print_status "✅ Port $port successfully freed"
                        break
                    else
                        print_status "Port $port still in use, retrying..." "⚠️"
                        kill -9 $still_in_use 2>/dev/null || true
                    fi
                    ((attempts++))
                done

                if [[ $attempts -eq 5 ]]; then
                    print_status "❌ Could not free port $port" "❌"
                fi
            else
                print_status "Port $port is free"
            fi
        else
            print_status "lsof not available, cannot check port $port" "⚠️"
        fi
    done

    if $cleaned_any; then
        print_status "Port cleanup completed, waiting for processes to fully terminate..."
        sleep 3
    fi
}

# Function to validate service readiness after startup
validate_services_readiness() {
    print_header "🔍 VALIDATING SERVICE READINESS"

    local services=(
        "PoC API:5001:/health"
        "RAG API:8000:/health"
        "Frontend:3001:/"
        "Legacy UI:5000:/"
    )

    local all_ready=true
    local ready_count=0

    print_status "Checking service health endpoints..."

    for service_info in "${services[@]}"; do
        IFS=':' read -r name port endpoint <<< "$service_info"

        if command_exists curl; then
            local url="http://localhost:$port$endpoint"
            local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null)

            if [[ "$response_code" == "200" ]]; then
                print_status "✅ $name ($port) is responding" "✅"
                ((ready_count++))
            elif [[ "$response_code" == "000" ]]; then
                print_status "❌ $name ($port) is not responding (connection failed)" "❌"
                all_ready=false
            else
                print_status "⚠️ $name ($port) returned HTTP $response_code"
                all_ready=false
            fi
        else
            print_status "⚠️ Cannot check $name (curl not available)"
        fi
    done

    echo ""
    print_status "Readiness Summary: $ready_count/${#services[@]} services ready"

    if $all_ready && [[ $ready_count -eq ${#services[@]} ]]; then
        print_status "🎉 ALL SERVICES ARE RUNNING AND READY!" "✅"
        return 0
    elif [[ $ready_count -gt 0 ]]; then
        print_status "⚠️ SOME SERVICES ARE RUNNING - partial functionality available"
        return 1
    else
        print_status "❌ NO SERVICES ARE RESPONDING" "❌"
        return 2
    fi
}

# Function to run startup script with comprehensive port management
run_startup_script() {
    local script_name="$1"
    local description="$2"
    local script_path="$PROJECT_ROOT/scripts/startup/$script_name"

    print_header "🚀 RUNNING $description"
    log_action "Startup Script" "Starting $description ($script_name)"

    if [[ -f "$script_path" ]]; then
        # Comprehensive pre-startup cleanup
        print_status "Performing comprehensive system preparation..."
        clean_ports_aggressively

        # Load environment variables
        if [[ -f "$PROJECT_ROOT/.env" ]]; then
            print_status "Loading environment configuration..."
            export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs 2>/dev/null)
        fi

        # Final port check
        print_status "Final port availability check..."
        local ports=(3001 5001 5000 8000 8545)
        local ports_clear=true

        for port in "${ports[@]}"; do
            if command_exists lsof; then
                local pids=$(lsof -ti:$port 2>/dev/null)
                if [[ -n "$pids" ]]; then
                    print_status "❌ Port $port still in use after cleanup" "❌"
                    ports_clear=false
                fi
            fi
        done

        if $ports_clear; then
            print_status "✅ All ports are clear, proceeding with startup..."
        else
            print_status "⚠️ Some ports may still be in use - startup may encounter conflicts"
        fi

        print_status "Starting $description..."
        cd_project_root

        # Run the startup script
        if [[ "$script_name" == *.py ]]; then
            python3 "$script_path"
            local startup_exit=$?
        elif [[ "$script_name" == *.sh ]]; then
            bash "$script_path"
            local startup_exit=$?
        fi

        cd_original_dir

        # Validate that services actually started
        if [[ $startup_exit -eq 0 ]]; then
            log_action "Startup Script" "$description completed successfully"
            print_status "Startup script completed, validating services..."
            sleep 3  # Give services time to fully start
            validate_services_readiness
        else
            log_action "Startup Script" "$description failed with exit code $startup_exit"
            print_status "❌ Startup script failed with exit code $startup_exit" "❌"
        fi

    else
        log_action "Startup Script" "$description failed - script not found: $script_path"
        print_status "Startup script not found: $script_path" "❌"
    fi

    wait_for_enter
}

# Function to start RAG API service
start_rag_api_service() {
    print_header "🤖 STARTING RAG API SERVICE"

    RAG_API_DIR="$PROJECT_ROOT/src/api/rag-api/api"

    if [[ ! -d "$RAG_API_DIR" ]]; then
        print_status "RAG API directory not found: $RAG_API_DIR" "❌"
        wait_for_enter
        return 1
    fi

    cd "$RAG_API_DIR"

    # Check for GROQ API key
    if [[ -z "$GROQ_API_KEY" ]]; then
        if [[ -f "$PROJECT_ROOT/.env" ]]; then
            export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs 2>/dev/null)
        fi
        if [[ -z "$GROQ_API_KEY" ]]; then
            print_status "GROQ_API_KEY not found. RAG API may have limited functionality." "⚠️"
            print_status "Set GROQ_API_KEY in .env file or environment" "ℹ️"
        fi
    fi

    if command_exists python3; then
        print_status "Starting RAG API server..." "🚀"
        print_status "API will be available at: http://localhost:8000" "ℹ️"
        print_status "Documentation at: http://localhost:8000/docs" "ℹ️"
        print_status "Press Ctrl+C to stop" "ℹ️"
        echo ""

        python3 rag_api.py
    else
        print_status "Python3 not found - cannot start RAG API" "❌"
        wait_for_enter
    fi
}

# Function to show startup scripts menu
show_startup_menu() {
    while true; do
        print_header "🚀 SYSTEM STARTUP SCRIPTS"
        echo "Choose a startup configuration:"
        echo ""
        echo "1) 🌟 Full System + RAG       - start_servers.py (all services)"
        echo "2) ⚡ Core Services Only      - start_servers_simple.py (Flask + Next.js)"
        echo "3) 🎨 Complete UI + RAG       - start_complete_ui.py (full UI experience)"
        echo "4) 🐚 Legacy Shell Startup    - start_servers.sh (basic shell script)"
        echo "5) 🤖 RAG API Only           - Start RAG API service"
        echo "6) ↩️  Back to Main Menu"
        echo ""

        read -p "Enter your choice (1-6): " choice

        case "$choice" in
            1) run_startup_script "start_servers.py" "Full System + RAG Startup" ;;
            2) run_startup_script "start_servers_simple.py" "Core Services Startup" ;;
            3) run_startup_script "start_complete_ui.py" "Complete UI + RAG Startup" ;;
            4) run_startup_script "start_servers.sh" "Legacy Shell Startup" ;;
            5) start_rag_api_service ;;
            6) return ;;
            *) print_status "Invalid choice. Please select 1-6." "❌" ;;
        esac
    done
}

# Function to check all services health
check_all_services_health() {
    print_header "🩺 SERVICE HEALTH CHECK"

    if command_exists python3; then
        cd "$PROJECT_ROOT"
        python3 -c "
import sys
sys.path.insert(0, 'scripts/startup')
try:
    from service_health import print_health_report
    print_health_report()
except Exception as e:
    print(f'Error checking service health: {e}')
"
    else
        print_status "Python3 not available for health check" "❌"
    fi

    wait_for_enter
}

# Function to show service management menu
show_service_management_menu() {
    while true; do
        print_header "🔧 SERVICE MANAGEMENT"
        echo "Monitor and manage Syntheverse services:"
        echo ""
        echo "1) 🩺 Check All Services Health"
        echo "2) 🌐 Check PoC API Status"
        echo "3) 🤖 Check RAG API Status"
        echo "4) 🎨 Check Next.js UI Status"
        echo "5) 🏛️ Check Legacy Web UI Status"
        echo "6) ⛓️ Check Anvil Status"
        echo "7) ↩️ Back to Main Menu"
        echo ""

        read -p "Enter your choice (1-7): " choice

        case "$choice" in
            1) check_all_services_health ;;
            2) check_service_status "poc_api" ;;
            3) check_service_status "rag_api" ;;
            4) check_service_status "nextjs_frontend" ;;
            5) check_service_status "legacy_web_ui" ;;
            6) check_anvil_status ;;
            7) return ;;
            *) print_status "Invalid choice. Please select 1-7." "❌" ;;
        esac
    done
}

# Function to check individual service status
check_service_status() {
    local service_name="$1"

    print_header "🔍 CHECKING $(echo $service_name | tr '_' ' ' | tr '[:lower:]' '[:upper:]') STATUS"

    if command_exists python3; then
        cd "$PROJECT_ROOT"
        python3 -c "
import sys
sys.path.insert(0, 'scripts/startup')
try:
    from service_health import get_service_status
    status = get_service_status('$service_name')
    print(f'Service: {status[\"name\"]}')
    print(f'Port: {status[\"port\"]}')
    print(f'Status: {status[\"status\"]}')
    print(f'Response Time: {status[\"response_time\"]:.2f}s')
    if 'status_code' in status:
        print(f'HTTP Status: {status[\"status_code\"]}')
    if 'error_message' in status:
        print(f'Error: {status[\"error_message\"]}')
except Exception as e:
    print(f'Error checking service status: {e}')
"
    else
        print_status "Python3 not available for service check" "❌"
    fi

    wait_for_enter
}

# Function to run development script
run_development_script() {
    local script_name="$1"
    local description="$2"
    local script_path="$PROJECT_ROOT/scripts/development/$script_name"

    print_header "💻 RUNNING $description"

    if [[ -f "$script_path" ]]; then
        print_status "Starting $description..."
        cd_project_root
        if [[ "$script_name" == *.py ]]; then
            python3 "$script_path"
        elif [[ "$script_name" == *.sh ]]; then
            bash "$script_path"
        fi
        cd_original_dir
    else
        print_status "Development script not found: $script_path" "❌"
    fi

    wait_for_enter
}

# Function to show development scripts menu
show_development_menu() {
    while true; do
        print_header "💻 DEVELOPMENT SCRIPTS"
        echo "Choose a development script to run:"
        echo ""
        echo "1) 🎯 Start PoC UI           - start_poc_ui.sh (Next.js + API)"
        echo "2) 🛑 Stop PoC UI            - stop_poc_ui.sh"
        echo "3) 🌐 Start All Services     - start_all_services.sh (RAG + Legacy)"
        echo "4) 🛑 Stop All Services      - stop_all_services.sh"
        echo "5) 🛑 Stop Syntheverse       - stop_Syntheverse.sh"
        echo "6) 📝 Submit PoD Test        - submit_pod.py (legacy PoD system)"
        echo "7) 🖥️  PoD Submission UI     - ui_pod_submission.py"
        echo "8) ↩️  Back to Main Menu"
        echo ""

        read -p "Enter your choice (1-8): " choice

        case "$choice" in
            1) run_development_script "start_poc_ui.sh" "PoC UI Startup" ;;
            2) run_development_script "stop_poc_ui.sh" "PoC UI Stop" ;;
            3) run_development_script "start_all_services.sh" "All Services Startup" ;;
            4) run_development_script "stop_all_services.sh" "All Services Stop" ;;
            5) run_development_script "stop_Syntheverse.sh" "Syntheverse Stop" ;;
            6) run_development_script "submit_pod.py" "PoD Submission Test" ;;
            7) run_development_script "ui_pod_submission.py" "PoD Submission UI" ;;
            8) return ;;
            *) print_status "Invalid choice. Please select 1-8." "❌" ;;
        esac
    done
}

# Function to run deployment script
run_deployment_script() {
    local script_name="$1"
    local description="$2"
    local script_path="$PROJECT_ROOT/scripts/deployment/$script_name"

    print_header "📦 RUNNING $description"

    if [[ -f "$script_path" ]]; then
        print_status "Starting $description..."
        cd_project_root
        if [[ "$script_name" == *.py ]]; then
            python3 "$script_path"
        fi
        cd_original_dir
    else
        print_status "Deployment script not found: $script_path" "❌"
    fi

    wait_for_enter
}

# Function to check Anvil status
check_anvil_status() {
    print_header "🔍 CHECKING ANVIL STATUS"

    if command_exists python3; then
        cd "$PROJECT_ROOT"
        python3 -c "
import sys
sys.path.insert(0, 'scripts/startup')
try:
    from anvil_manager import get_anvil_status
    status = get_anvil_status()
    print(f'Anvil Running: {status.running}')
    print(f'Port: {status.port}')
    if status.running:
        print(f'Block Number: {status.block_number}')
        print(f'Accounts: {status.accounts}')
        if status.pid:
            print(f'PID: {status.pid}')
        print(f'Uptime: {status.uptime:.1f}s' if status.uptime else 'Uptime: N/A')
    else:
        print('Anvil is not running')
        print('Run option 2 to start Anvil')
except Exception as e:
    print(f'Error checking Anvil status: {e}')
"
    else
        print_status "Python3 not available for Anvil status check" "❌"
    fi

    wait_for_enter
}

# Function to start Anvil
start_anvil_service() {
    print_header "🚀 STARTING ANVIL"

    if command_exists python3; then
        cd "$PROJECT_ROOT"
        python3 -c "
import sys
sys.path.insert(0, 'scripts/startup')
try:
    from anvil_manager import start_anvil, wait_for_anvil
    print('Starting Anvil...')
    if start_anvil():
        print('✅ Anvil started successfully')
        if wait_for_anvil(timeout=30):
            print('✅ Anvil is ready')
        else:
            print('⚠️ Anvil started but health check failed')
    else:
        print('❌ Failed to start Anvil')
except Exception as e:
    print(f'Error starting Anvil: {e}')
"
    else
        print_status "Python3 not available for Anvil startup" "❌"
    fi

    wait_for_enter
}

# Function to stop Anvil
stop_anvil_service() {
    print_header "🛑 STOPPING ANVIL"

    if command_exists python3; then
        cd "$PROJECT_ROOT"
        python3 -c "
import sys
sys.path.insert(0, 'scripts/startup')
try:
    from anvil_manager import stop_anvil
    print('Stopping Anvil...')
    if stop_anvil():
        print('✅ Anvil stopped successfully')
    else:
        print('⚠️ Anvil may still be running')
except Exception as e:
    print(f'Error stopping Anvil: {e}')
"
    else
        print_status "Python3 not available for Anvil shutdown" "❌"
    fi

    wait_for_enter
}

# Function to show deployment scripts menu
show_deployment_menu() {
    while true; do
        print_header "📦 DEPLOYMENT & BLOCKCHAIN MANAGEMENT"
        echo "Choose an option:"
        echo ""
        echo "1) ⛓️ Deploy Smart Contracts - deploy_contracts.py"
        echo "2) 🔍 Check Anvil Status"
        echo "3) 🚀 Start Anvil"
        echo "4) 🛑 Stop Anvil"
        echo "5) ↩️ Back to Main Menu"
        echo ""

        read -p "Enter your choice (1-5): " choice

        case "$choice" in
            1) run_deployment_script "deploy_contracts.py" "Smart Contract Deployment" ;;
            2) check_anvil_status ;;
            3) start_anvil_service ;;
            4) stop_anvil_service ;;
            5) return ;;
            *) print_status "Invalid choice. Please select 1-2." "❌" ;;
        esac
    done
}

# Function to run utility script
run_utility_script() {
    local script_name="$1"
    local description="$2"
    local script_path="$PROJECT_ROOT/scripts/utilities/$script_name"

    print_header "🔧 RUNNING $description"

    if [[ -f "$script_path" ]]; then
        print_status "Starting $description..."
        cd_project_root
        if [[ "$script_name" == *.py ]]; then
            python3 "$script_path"
        fi
        cd_original_dir
    else
        print_status "Utility script not found: $script_path" "❌"
    fi

    wait_for_enter
}

# Function to show utilities menu
show_utilities_menu() {
    while true; do
        print_header "🔧 UTILITIES"
        echo "Choose a utility script to run:"
        echo ""
        echo "1) 🧹 Clear Persistent Memory - clear_persistent_memory.py"
        echo "2) ↩️ Back to Main Menu"
        echo ""

        read -p "Enter your choice (1-2): " choice

        case "$choice" in
            1) run_utility_script "clear_persistent_memory.py" "Clear Persistent Memory" ;;
            2) return ;;
            *) print_status "Invalid choice. Please select 1-2." "❌" ;;
        esac
    done
}

exit_menu() {
    print_header "👋 GOODBYE"
    print_status "Thanks for using Syntheverse Interactive Menu!"
    exit 0
}

# Function to handle interrupts gracefully
cleanup() {
    echo ""
    print_status "Interrupted by user. Returning to original directory..." "⚠️"
    cd_original_dir
    exit 130
}

# Set up signal handlers
trap cleanup INT TERM

# Main function
main() {
    # Check if we're in the right directory structure
    if [[ ! -f "$PROJECT_ROOT/README.md" ]]; then
        print_status "Error: Cannot find project root. Expected README.md at $PROJECT_ROOT" "❌"
        exit 1
    fi

    print_status "Syntheverse Interactive Menu initialized"
    print_status "Project root: $PROJECT_ROOT"

    # Main menu loop
    while true; do
        show_main_menu

        # Read user input
        read -p "Enter your choice (1-9): " choice

        # Handle empty input
        if [[ -z "$choice" ]]; then
            continue
        fi

        # Process choice
        handle_menu_selection "$choice"

        # Brief pause before showing menu again
        sleep 0.5
    done
}

# Run main function
main "$@"
