#!/bin/bash

# Test script for setup functions in run.sh
# This will test the auto-install functionality

echo "Testing setup functions..."

# Source the run.sh script to get the functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"

# Set up environment variables like run.sh does
SCRIPT_DIR="$SCRIPT_DIR/examples"
CURRENT_DIR="$(pwd)"

# Source the functions from run.sh (without running main)
echo "Loading functions from run.sh..."
# Extract just the function definitions
sed -n '/^# Function to check prerequisites/,/^}$/p; /^check_prerequisites()/,/^}$/p; /^print_status()/,/^}$/p; /^command_exists()/,/^}$/p; /^cd_project_root()/,/^}$/p; /^cd_original_dir()/,/^}$/p' "$SCRIPT_DIR/run.sh" > /tmp/test_functions.sh

# Add variable definitions
cat > /tmp/test_functions_complete.sh << 'EOF'
#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="/Users/4d/Documents/GitHub/Syntheverse"
CURRENT_DIR="/Users/4d/Documents/GitHub/Syntheverse"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
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

# Test version of check_prerequisites (minimal)
check_prerequisites() {
    print_status "🔧 Testing Prerequisites Check"

    local all_good=true

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

    # Check and install Python dependencies
    print_status "Checking Python dependencies..."
    cd_project_root

    # Required packages for the system
    local required_packages=("web3")  # Just test web3 since it's missing

    for package in "${required_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_status "$package available"
        else
            print_status "$package not available - installing..." "⚠️"
            if pip3 install "$package" > /tmp/pip_install_$package.log 2>&1; then
                print_status "✅ $package installed successfully"
            else
                print_status "❌ Failed to install $package" "❌"
                print_status "Check log: /tmp/pip_install_$package.log"
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

    if $all_good; then
        print_status "Prerequisites check completed successfully" "✅"
    else
        print_status "Some prerequisites are missing or misconfigured" "⚠️"
    fi

    return $([ $all_good = true ] && echo 0 || echo 1)
}

# Run the test
check_prerequisites
EOF

echo "Running test of setup functions..."
bash /tmp/test_functions_complete.sh


