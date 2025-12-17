"""
Pytest configuration for Syntheverse test suite
"""

import pytest
import os
from pathlib import Path

# Import test configuration
from test_framework import test_config

# Load environment variables from .env file if it exists
def load_env_file():
    try:
        from dotenv import load_dotenv
        import os

        # Try multiple possible paths for .env file
        possible_paths = [
            Path(__file__).parent.parent / ".env",  # tests/../.env
            Path.cwd() / ".env",                     # current working directory
            Path(os.path.expanduser("~")) / ".env",  # home directory (fallback)
        ]

        for env_path in possible_paths:
            if env_path.exists():
                result = load_dotenv(env_path)
                groq_key = os.getenv('GROQ_API_KEY')
                if groq_key:
                    print(f"✓ Loaded GROQ_API_KEY from {env_path}")
                    return True
                else:
                    print(f"⚠️  .env file found at {env_path} but GROQ_API_KEY not set")

        print("⚠️  .env file not found or GROQ_API_KEY not set in any expected location")
        return False

    except ImportError:
        print("⚠️  python-dotenv not installed, environment variables not loaded from .env")
        return False
    except Exception as e:
        print(f"⚠️  Error loading .env: {e}")
        return False

# Load environment at module import time
load_env_file()


def pytest_sessionstart(session):
    """Set up Python path and validate GROQ_API_KEY at the start of the test session"""
    import sys
    from pathlib import Path

    # Set up Python path for imports
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src" / "core"))
    sys.path.insert(0, str(project_root / "src" / "blockchain"))
    sys.path.insert(0, str(project_root / "src"))

    # Validate GROQ_API_KEY
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        pytest.fail("GROQ_API_KEY environment variable is required for tests. Set it in .env file or environment.", pytrace=False)

    # Test the key using the same OpenAI client configuration as PODServer
    try:
        from openai import OpenAI
        test_client = OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )
        # Test connection with a quick API call
        test_client.models.list()
        print("✓ GROQ_API_KEY validated successfully")
    except Exception as e:
        pytest.fail(f"GROQ_API_KEY is invalid or Groq API is unreachable: {e}", pytrace=False)


def pytest_addoption(parser):
    """Add command-line options for service handling"""
    parser.addoption(
        "--mock-services",
        action="store_true",
        default=False,
        help="Run tests with mocked services even when real services are unavailable"
    )
    parser.addoption(
        "--skip-service-checks",
        action="store_true",
        default=False,
        help="Skip all service availability checks"
    )
    parser.addoption(
        "--auto-start-services",
        action="store_true",
        default=True,
        help="Automatically start required services for integration tests"
    )
    parser.addoption(
        "--no-auto-start-services",
        action="store_false",
        dest="auto_start_services",
        help="Do not automatically start required services"
    )

# Suppress warnings for utility classes in test framework
collect_ignore = [
    "test_framework.py",
    "test_runner.py",
]

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "requires_service: Test requires specific service to be running")
    config.addinivalue_line("markers", "requires_rag_api: Test requires RAG API service")
    config.addinivalue_line("markers", "requires_poc_api: Test requires PoC API service")
    config.addinivalue_line("markers", "requires_frontend: Test requires frontend service")
    config.addinivalue_line("markers", "requires_blockchain: Test requires blockchain services")


@pytest.fixture(scope="session")
def check_service_availability():
    """Fixture to check service availability"""
    def _check_service(url, timeout=5):
        """Check if a service is available at the given URL"""
        import requests
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    return _check_service


@pytest.fixture(scope="session")
def rag_api_available(check_service_availability):
    """Check if RAG API is available"""
    rag_api_url = test_config.get("api_urls.rag_api")
    return check_service_availability(f"{rag_api_url}/health")


@pytest.fixture(scope="session")
def poc_api_available(check_service_availability):
    """Check if PoC API is available"""
    poc_api_url = test_config.get("api_urls.poc_api")
    return check_service_availability(f"{poc_api_url}/health")


@pytest.fixture(scope="session")
def frontend_available(check_service_availability):
    """Check if frontend is available"""
    frontend_url = test_config.get("api_urls.frontend")
    return check_service_availability(frontend_url)


@pytest.fixture(scope="session")
def blockchain_available():
    """Check if blockchain modules are available"""
    try:
        from layer1.node import SyntheverseNode
        return True
    except ImportError:
        return False


@pytest.fixture(scope="session", autouse=True)
def ensure_environment_loaded():
    """Ensure environment variables are loaded at the start of the test session"""
    # GROQ_API_KEY validation is now handled by pytest_sessionstart
    pass


@pytest.fixture(scope="session", autouse=True)
def service_bootstrapper(request):
    """Automatically start and stop required services for integration tests"""
    import subprocess
    import signal
    import time
    import sys
    from pathlib import Path

    auto_start = request.config.getoption("--auto-start-services")
    mock_services = request.config.getoption("--mock-services")
    skip_checks = request.config.getoption("--skip-service-checks")

    if skip_checks or mock_services or not auto_start:
        yield
        return

    # Get the project root
    project_root = Path(__file__).parent.parent

    # Detect which services are needed by scanning for markers in collected tests
    services_needed = set()
    for item in request.session.items:
        if hasattr(item, 'get_closest_marker'):
            if item.get_closest_marker("requires_rag_api"):
                services_needed.add("rag_api")
            if item.get_closest_marker("requires_poc_api"):
                services_needed.add("poc_api")
            if item.get_closest_marker("requires_frontend"):
                services_needed.add("frontend")

    if not services_needed:
        yield
        return

    print(f"Services needed for tests: {', '.join(services_needed)}")

    # Track started services for cleanup
    started_services = []
    processes = []  # list[tuple[str, subprocess.Popen, str|None]] -> (service_name, proc, log_path)
    unavailable_services = set()

    def _is_service_healthy(url: str, timeout: float = 2.0) -> bool:
        try:
            import requests
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False

    def _tail_log(log_path: str, lines: int = 40) -> None:
        try:
            if os.path.exists(log_path):
                print(f"📋 Last {lines} lines of log ({log_path}):")
                with open(log_path, "r") as f:
                    content = f.readlines()
                for line in content[-lines:]:
                    print(f"   {line.rstrip()}")
            else:
                print(f"📋 Log file not found: {log_path}")
        except Exception as e:
            print(f"   ⚠️ Could not read log file {log_path}: {e}")

    try:
        # NOTE:
        # - We only auto-start backend services (RAG API + PoC API).
        # - We do NOT auto-start the frontend (Next.js dev server) during "all tests" because it's heavy and
        #   the interactive menu already provides a dedicated frontend test mode.
        # - If a service fails to start, we do NOT hard-fail the entire session; instead, tests that require
        #   that service will be skipped by `skip_unavailable_services`.

        # Start RAG API if needed (FastAPI) — start only the API, not the legacy UI bundle
        if "rag_api" in services_needed:
            rag_api_base = test_config.get("api_urls.rag_api", "http://localhost:8000")
            rag_health_url = f"{rag_api_base}/health"

            if _is_service_healthy(rag_health_url, timeout=2):
                print(f"✓ RAG API already running at {rag_health_url}")
            else:
                print("Starting RAG API service (FastAPI)...")
                rag_api_cwd = project_root / "src" / "api" / "rag-api" / "api"
                rag_log = "/tmp/syntheverse_rag_api_test.log"
                rag_log_f = open(rag_log, "w")
                proc = subprocess.Popen(
                    [sys.executable, "rag_api.py"],
                    cwd=rag_api_cwd,
                    stdout=rag_log_f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
                # Parent can close its handle; child keeps the FD
                try:
                    rag_log_f.close()
                except Exception:
                    pass
                processes.append(("rag_api", proc, rag_log))
                started_services.append("rag_api")

            # Wait for RAG API to be ready
            timeout_seconds = test_config.get("timeouts.service_startup", 60)
            print(f"Waiting for RAG API at {rag_health_url}... (timeout: {timeout_seconds}s)")
            for _ in range(int(timeout_seconds)):
                if _is_service_healthy(rag_health_url, timeout=2):
                    print("✓ RAG API is ready")
                    break
                time.sleep(1)
            else:
                print("❌ RAG API failed to start within timeout (tests will be skipped)")
                _tail_log("/tmp/syntheverse_rag_api_test.log", lines=60)
                unavailable_services.add("rag_api")

        # Start PoC API if needed (Flask). Do not auto-start Next.js frontend here.
        if "poc_api" in services_needed:
            poc_api_base = test_config.get("api_urls.poc_api", "http://localhost:5001")
            poc_health_url = f"{poc_api_base}/health"

            if _is_service_healthy(poc_health_url, timeout=2):
                print(f"✓ PoC API already running at {poc_health_url}")
            else:
                print("Starting PoC API service (Flask)...")
                poc_api_cwd = project_root / "src" / "api" / "poc-api"
                poc_log = "/tmp/syntheverse_poc_api_test.log"
                poc_log_f = open(poc_log, "w")
                proc = subprocess.Popen(
                    [sys.executable, "app.py"],
                    cwd=poc_api_cwd,
                    stdout=poc_log_f,
                    stderr=subprocess.STDOUT,
                    start_new_session=True
                )
                try:
                    poc_log_f.close()
                except Exception:
                    pass
                processes.append(("poc_api", proc, poc_log))
                started_services.append("poc_api")

            # Wait for services to be ready
            timeout_seconds = test_config.get("timeouts.service_startup", 60)
            print(f"Waiting for PoC API at {poc_health_url}... (timeout: {timeout_seconds}s)")
            for _ in range(int(timeout_seconds)):
                if _is_service_healthy(poc_health_url, timeout=2):
                    print("✓ PoC API is ready")
                    break
                time.sleep(1)
            else:
                print("❌ PoC API failed to start within timeout (tests will be skipped)")
                _tail_log("/tmp/syntheverse_poc_api_test.log", lines=80)
                unavailable_services.add("poc_api")

        if unavailable_services:
            print(f"⚠️ Some services are unavailable: {', '.join(sorted(unavailable_services))}")
            print("   Tests requiring those services will be skipped.")
        else:
            print("All required services are running")
        yield

    finally:
        # Cleanup: stop all started services
        print("Stopping services...")
        for service_name, proc, log_path in processes:
            try:
                if proc.poll() is None:
                    # Kill the entire process group/session when possible
                    if hasattr(os, "killpg"):
                        try:
                            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                        except Exception:
                            proc.terminate()
                    else:
                        proc.terminate()
                    time.sleep(2)
                    if proc.poll() is None:
                        if hasattr(os, "killpg"):
                            try:
                                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                            except Exception:
                                proc.kill()
                        else:
                            proc.kill()
                print(f"✓ Stopped {service_name}{f' (log: {log_path})' if log_path else ''}")
            except Exception as e:
                print(f"⚠️ Error stopping {service_name}: {e}")

        # Best-effort: do not run global stop scripts here, as they can kill user-managed dev servers.
        # We only terminate processes we started in this session.

        print("Service cleanup complete")

@pytest.fixture(autouse=True)
def skip_unavailable_services(request, rag_api_available, poc_api_available, frontend_available, blockchain_available):
    """Automatically skip tests that require unavailable services"""
    # Check command-line options
    mock_services = request.config.getoption("--mock-services")
    skip_checks = request.config.getoption("--skip-service-checks")

    if skip_checks:
        return  # Skip all checks

    if mock_services:
        return  # Allow tests to run with mocked services

    # Normal service availability checks
    if request.node.get_closest_marker("requires_rag_api") and not rag_api_available:
        pytest.skip("RAG API service not available (use --mock-services to run with mocks)")
    elif request.node.get_closest_marker("requires_poc_api") and not poc_api_available:
        pytest.skip("PoC API service not available (use --mock-services to run with mocks)")
    elif request.node.get_closest_marker("requires_frontend") and not frontend_available:
        pytest.skip("Frontend service not available (use --mock-services to run with mocks)")
    elif request.node.get_closest_marker("requires_blockchain") and not blockchain_available:
        pytest.skip("Blockchain modules not available (use --mock-services to run with mocks)")
