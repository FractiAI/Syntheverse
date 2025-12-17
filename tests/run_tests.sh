#!/bin/bash

# Syntheverse Unified Test Runner
# Runs all test suites with options for filtering and reporting

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
TEST_RESULTS_DIR="$SCRIPT_DIR/results"
FAILED_TESTS=0
PASSED_TESTS=0

# Create results directory
mkdir -p "$TEST_RESULTS_DIR"

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

# Function to check if a command exists
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

# Function to run a single test file
run_test_file() {
    local test_file="$1"
    local test_name="${2:-$(basename "$test_file" .py)}"

    print_status "Running $test_name..."

    local start_time=$(date +%s)
    local output_file="$TEST_RESULTS_DIR/${test_name}_$(date +%Y%m%d_%H%M%S).log"

    # Navigate to project root for tests
    cd_project_root

    # Run the test and capture output
    if python3 "$test_file" > "$output_file" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_status "$test_name PASSED (${duration}s)" "✅"
        ((PASSED_TESTS++))
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_status "$test_name FAILED (${duration}s)" "❌"
        print_status "See details: $output_file"
        ((FAILED_TESTS++))
        return 1
    fi
}

# Function to run shell script tests
run_shell_test() {
    local test_script="$1"
    local test_name="${2:-$(basename "$test_script" .sh)}"

    print_status "Running $test_name..."

    local start_time=$(date +%s)
    local output_file="$TEST_RESULTS_DIR/${test_name}_$(date +%Y%m%d_%H%M%S).log"

    # Navigate to project root for tests
    cd_project_root

    # Make script executable if not already
    chmod +x "$test_script" 2>/dev/null || true

    # Run the test and capture output
    if bash "$test_script" > "$output_file" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_status "$test_name PASSED (${duration}s)" "✅"
        ((PASSED_TESTS++))
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_status "$test_name FAILED (${duration}s)" "❌"
        print_status "See details: $output_file"
        ((FAILED_TESTS++))
        return 1
    fi
}

# Function to run quick tests
run_quick_tests() {
    print_header "🧪 RUNNING QUICK TESTS"

    # Run quick shell tests
    if [[ -f "$SCRIPT_DIR/test_poc_quick.sh" ]]; then
        run_shell_test "$SCRIPT_DIR/test_poc_quick.sh" "poc_quick"
    else
        print_status "Quick test script not found: test_poc_quick.sh" "⚠️"
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    print_header "🌐 RUNNING FRONTEND TESTS"

    if [[ -f "$SCRIPT_DIR/test_poc_frontend.sh" ]]; then
        run_shell_test "$SCRIPT_DIR/test_poc_frontend.sh" "poc_frontend"
    else
        print_status "Frontend test script not found: test_poc_frontend.sh" "⚠️"
    fi
}

# Function to run all Python tests with pytest
run_all_python_tests() {
    print_header "🐍 RUNNING ALL PYTHON TESTS"

    if command_exists python3 && python3 -c "import pytest" 2>/dev/null; then
        print_status "Running Python tests with pytest..."

        # Run all Python tests
        if cd "$PROJECT_ROOT" && python3 -m pytest tests/ -v --tb=short --maxfail=5 \
            --junitxml="$TEST_RESULTS_DIR/python_tests.xml" \
            2>&1 | tee "$TEST_RESULTS_DIR/python_tests.log"; then
            print_status "Python tests completed successfully" "✅"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            local exit_code=$?
            print_status "Python tests failed with exit code: $exit_code" "❌"
            FAILED_TESTS=$((FAILED_TESTS + 1))

            # Show summary of failures
            if [[ -f "$TEST_RESULTS_DIR/python_tests.log" ]]; then
                echo ""
                print_status "Test failures summary:" "ℹ️"
                grep -E "(FAILED|ERROR|passed|failed)" "$TEST_RESULTS_DIR/python_tests.log" | tail -10
            fi

            return $exit_code
        fi
    else
        print_status "pytest not available, falling back to individual test execution" "⚠️"

        # Fallback: run individual Python test files
        local python_tests=(
            "test_anvil_manager.py"
            "test_service_health.py"
            "test_port_manager.py"
            "test_startup_scripts.py"
            "test_deployment_enhanced.py"
            "test_submission.py"
            "test_submission_flow.py"
            "test_full_submission_flow.py"
            "test_rag_api.py"
            "test_rag_pod_query.py"
            "test_rag_timeout.py"
            "test_blockchain.py"
            "test_core_modules.py"
            "test_frontend_integration.py"
            "test_poc_api.py"
        )

        for test_file in "${python_tests[@]}"; do
            local full_path="$SCRIPT_DIR/$test_file"
            if [[ -f "$full_path" ]]; then
                run_test_file "$full_path" "${test_file%.py}"
            else
                print_status "Test file not found: $test_file" "⚠️"
            fi
        done
    fi
}

# Function to run all tests
run_all_tests() {
    print_header "🚀 RUNNING ALL TESTS"

    FAILED_TESTS=0
    PASSED_TESTS=0

    # Note: Quick tests (service integration) require services to be running
    # They are not included in --all to avoid failures when services aren't started
    print_status "Note: Service integration tests skipped (use --quick with services running)" "ℹ️"

    # Run frontend tests (also integration tests)
    print_status "Frontend tests also require services - skipping for --all" "ℹ️"

    # Run all Python unit tests
    run_all_python_tests

    # Print summary
    print_header "📊 TEST SUMMARY"
    print_status "Passed: $PASSED_TESTS" "✅"
    print_status "Failed: $FAILED_TESTS" "❌"
    print_status "Total: $((PASSED_TESTS + FAILED_TESTS))"

    if [[ $FAILED_TESTS -eq 0 ]]; then
        print_status "All available tests passed!" "✅"
        print_status "For integration tests: start services first, then use --quick" "ℹ️"
        return 0
    else
        print_status "Some tests failed. Check logs in: $TEST_RESULTS_DIR" "❌"
        return 1
    fi
}

# Function to clean test results
clean_test_results() {
    print_status "Cleaning test results directory..."
    rm -rf "$TEST_RESULTS_DIR"/*
    print_status "Test results cleaned" "✅"
}

# Function to show usage
show_usage() {
    echo "Syntheverse Unified Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all              Run all tests (default)"
    echo "  --quick            Run quick validation tests only"
    echo "  --frontend         Run frontend tests only"
    echo "  --python           Run Python tests only"
    echo "  --submission       Run submission test only"
    echo "  --flow             Run submission flow test only"
    echo "  --full-flow        Run full submission flow test only"
    echo "  --rag-api          Run RAG API test only"
    echo "  --rag-query        Run RAG PoD query test only"
    echo "  --rag-timeout      Run RAG timeout test only"
    echo "  --clean            Clean test results directory"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all           # Run all tests"
    echo "  $0 --quick         # Run quick tests only"
    echo "  $0 --clean --all   # Clean and run all tests"
}

# Main function
main() {
    local run_all=true
    local run_quick=false
    local run_frontend=false
    local run_python=false
    local clean_first=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                run_all=true
                shift
                ;;
            --quick)
                run_quick=true
                run_all=false
                shift
                ;;
            --frontend)
                run_frontend=true
                run_all=false
                shift
                ;;
            --python)
                run_python=true
                run_all=false
                shift
                ;;
            --submission)
                run_test_file "$SCRIPT_DIR/test_submission.py" "submission_test"
                exit $?
                ;;
            --flow)
                run_test_file "$SCRIPT_DIR/test_submission_flow.py" "submission_flow_test"
                exit $?
                ;;
            --full-flow)
                run_test_file "$SCRIPT_DIR/test_full_submission_flow.py" "full_submission_flow_test"
                exit $?
                ;;
            --rag-api)
                run_test_file "$SCRIPT_DIR/test_rag_api.py" "rag_api_test"
                exit $?
                ;;
            --rag-query)
                run_test_file "$SCRIPT_DIR/test_rag_pod_query.py" "rag_pod_query_test"
                exit $?
                ;;
            --rag-timeout)
                run_test_file "$SCRIPT_DIR/test_rag_timeout.py" "rag_timeout_test"
                exit $?
                ;;
            --clean)
                clean_first=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_status "Unknown option: $1" "❌"
                show_usage
                exit 1
                ;;
        esac
    done

    # Clean if requested
    if $clean_first; then
        clean_test_results
    fi

    # Run requested tests
    if $run_all; then
        run_all_tests
        exit $?
    elif $run_quick; then
        run_quick_tests
        exit $?
    elif $run_frontend; then
        run_frontend_tests
        exit $?
    elif $run_python; then
        run_all_python_tests
        exit $?
    fi
}

# Run main function
main "$@"
