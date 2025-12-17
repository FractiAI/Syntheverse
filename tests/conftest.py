"""
Pytest configuration for Syntheverse test suite
NO SKIPS POLICY: Tests must never skip - they install dependencies or fail with clear errors
"""

import pytest
import os
from pathlib import Path

# Import test framework with dependency management
from test_framework import test_config, ensure_dependency, ensure_service_running, ensure_module_available

# Load environment variables from .env file if it exists
def load_env_file():
    """Load environment variables with fallback for missing python-dotenv"""
    try:
        # Try to ensure python-dotenv is available, but don't fail if it can't be installed
        try:
            ensure_dependency("python-dotenv")
            dotenv_available = True
        except RuntimeError:
            dotenv_available = False
            print("⚠️  python-dotenv not available, using manual .env parsing")

        if dotenv_available:
            from dotenv import load_dotenv
            load_dotenv_func = load_dotenv
        else:
            # Fallback: manual .env parsing
            def load_dotenv_func(env_path):
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    os.environ[key.strip()] = value.strip()
                    return True
                except Exception:
                    return False

        # Try multiple possible paths for .env file
        possible_paths = [
            Path(__file__).parent.parent / ".env",  # tests/../.env
            Path.cwd() / ".env",                     # current working directory
            Path(os.path.expanduser("~")) / ".env",  # home directory (fallback)
        ]

        for env_path in possible_paths:
            if env_path.exists():
                result = load_dotenv_func(env_path)
                groq_key = os.getenv('GROQ_API_KEY')
                if groq_key:
                    print(f"✓ Loaded GROQ_API_KEY from {env_path}")
                    return True
                else:
                    print(f"⚠️  .env file found at {env_path} but GROQ_API_KEY not set")

        print("⚠️  .env file not found or GROQ_API_KEY not set in any expected location")
        return False

    except Exception as e:
        print(f"⚠️  Error loading .env: {e}")
        return False

# Load environment at module import time
load_env_file()

def pytest_sessionstart(session):
    """Set up Python path, validate environment, and ensure dependencies"""
    import sys
    from pathlib import Path

    # Set up Python path for imports
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src" / "core"))
    sys.path.insert(0, str(project_root / "src" / "blockchain"))
    sys.path.insert(0, str(project_root / "src"))
    sys.path.insert(0, str(project_root / "scripts" / "development"))

    # Ensure critical dependencies are available
    print("🔧 Ensuring critical dependencies are available...")
    critical_deps = ["requests", "pytest", "openai"]
    for dep in critical_deps:
        try:
            ensure_dependency(dep)
        except RuntimeError as e:
            pytest.fail(f"Critical dependency {dep} could not be installed: {e}", pytrace=False)

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
    """Add command-line options (removed mock and skip options per no-skips policy)"""
    # No options for mocking or skipping - tests must run with real dependencies
    pass

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


@pytest.fixture(scope="session", autouse=True)
def ensure_environment_loaded():
    """Ensure environment variables are loaded at the start of the test session"""
    # Environment validation is now handled by pytest_sessionstart
    pass


@pytest.fixture(scope="session", autouse=True)
def service_bootstrapper(request):
    """Automatically start and stop required services for integration tests - FAILS HARD if services cannot start"""
    import subprocess
    import signal
    import time
    import sys
    from pathlib import Path

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

    print(f"🚀 Starting required services: {', '.join(services_needed)}")

    # Track started services for cleanup
    processes = []  # list[tuple[str, subprocess.Popen, str|None]] -> (service_name, proc, log_path)

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
        # Start RAG API if needed (FastAPI) — FAIL HARD if it cannot start
        if "rag_api" in services_needed:
            rag_api_base = test_config.get("api_urls.rag_api", "http://localhost:8000")
            rag_health_url = f"{rag_api_base}/health"

            if _is_service_healthy(rag_health_url, timeout=2):
                print(f"✓ RAG API already running at {rag_health_url}")
            else:
                print("Starting RAG API service (FastAPI)...")

                # Ensure the service can be started
                startup_command = [sys.executable, "rag_api.py"]
                startup_cwd = project_root / "src" / "api" / "rag-api" / "api"

                try:
                    ensure_service_running(
                        service_name="rag_api",
                        startup_command=startup_command,
                        health_url=rag_health_url,
                        startup_timeout=test_config.get("timeouts.service_startup", 60)
                    )
                except RuntimeError as e:
                    pytest.fail(f"CRITICAL: RAG API service could not be started: {e}", pytrace=False)

        # Start PoC API if needed (Flask) — FAIL HARD if it cannot start
        if "poc_api" in services_needed:
            poc_api_base = test_config.get("api_urls.poc_api", "http://localhost:5001")
            poc_health_url = f"{poc_api_base}/health"

            if _is_service_healthy(poc_health_url, timeout=2):
                print(f"✓ PoC API already running at {poc_health_url}")
            else:
                print("Starting PoC API service (Flask)...")

                # Ensure the service can be started
                startup_command = [sys.executable, "app.py"]
                startup_cwd = project_root / "src" / "api" / "poc-api"

                try:
                    ensure_service_running(
                        service_name="poc_api",
                        startup_command=startup_command,
                        health_url=poc_health_url,
                        startup_timeout=test_config.get("timeouts.service_startup", 60)
                    )
                except RuntimeError as e:
                    pytest.fail(f"CRITICAL: PoC API service could not be started: {e}", pytrace=False)

        print("✅ All required services are running and healthy")
        yield

    finally:
        # Cleanup: stop all started services
        print("🛑 Stopping services...")
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

        print("Service cleanup complete")
