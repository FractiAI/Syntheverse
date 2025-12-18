#!/usr/bin/env python3
"""
Simple Syntheverse Server Startup - Keeps servers running
"""

import os
import sys
import subprocess
import time
import signal
import socket
import logging
from pathlib import Path
from typing import Optional

# Import port management module
try:
    from .port_manager import PortManager, free_port, check_port_available as port_check_available
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from port_manager import PortManager, free_port, check_port_available as port_check_available

def setup_logging():
    """Configure logging for the startup script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def check_port_available(port: int, name: str) -> bool:
    """Check if a port is available for use"""
    return port_check_available(port)

def wait_for_server(port: int, name: str, timeout: int = 30, endpoint: str = "/health") -> bool:
    """Wait for a server to become available with retry logic"""
    import requests
    
    max_attempts = timeout // 2
    url = f"http://127.0.0.1:{port}{endpoint}"
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code < 500:
                logging.info(f"{name} is responding on port {port}")
                return True
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            logging.debug(f"Health check attempt {attempt + 1} failed: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    logging.warning(f"{name} did not become available within {timeout} seconds")
    return False

def load_environment(project_root: Path, logger: logging.Logger) -> bool:
    """Load environment variables from .env file and validate required variables"""
    env_file = project_root / ".env"

    if env_file.exists():
        logger.info("Loading environment configuration from .env file...")
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            os.environ[key] = value
            logger.info("Environment variables loaded from .env file")
        except Exception as e:
            logger.warning(f"Failed to load .env file: {e}")

    required_vars = ['GROQ_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set the missing variables in your .env file or environment")
        logger.info("Example: GROQ_API_KEY=your-api-key-here")
        return False

    groq_key = os.getenv('GROQ_API_KEY', '')
    if groq_key:
        masked_key = groq_key[:15] + "..." if len(groq_key) > 15 else groq_key
        logger.info(f"GROQ_API_KEY configured ({masked_key})")
    else:
        logger.error("GROQ_API_KEY not found")
        return False

    return True

def validate_dependencies(project_root: Path, logger: logging.Logger) -> bool:
    """Validate that required files and dependencies exist"""
    validation_passed = True

    required_files = [
        ("PoC API", project_root / "src" / "api" / "poc-api" / "app.py"),
    ]

    for service_name, file_path in required_files:
        if not file_path.exists():
            logger.error(f"Required file not found: {file_path}")
            validation_passed = False
        else:
            logger.info(f"{service_name} file found: {file_path.name}")

    frontend_dir = project_root / "src" / "frontend" / "poc-frontend"
    if frontend_dir.exists():
        logger.info("Next.js frontend directory found")
        if (frontend_dir / "node_modules").exists():
            logger.info("Next.js dependencies installed")
        else:
            logger.warning("Next.js dependencies not installed - run 'npm install' in frontend directory")
        if (frontend_dir / "package.json").exists():
            logger.info("Next.js package.json found")
        else:
            logger.warning("Next.js package.json not found")
    else:
        logger.warning("Next.js frontend directory not found - Next.js UI will not be available")

    required_packages = ['flask', 'flask_cors', 'werkzeug', 'requests']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'flask_cors':
                import flask_cors
            else:
                __import__(package)
            logger.info(f"Python package '{package}' available")
        except ImportError:
            missing_packages.append(package)
            validation_passed = False

    if missing_packages:
        logger.error(f"Missing Python packages: {', '.join(missing_packages)}")
        logger.info("Install with: pip install flask flask-cors werkzeug requests")

    if frontend_dir.exists():
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"Node.js available: {result.stdout.strip()}")
                result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info(f"npm available: {result.stdout.strip()}")
                else:
                    logger.warning("npm not available - Next.js frontend may not start")
            else:
                logger.warning("Node.js not available - Next.js frontend will not start")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Node.js/npm not available - Next.js frontend will not start")

    return validation_passed

def start_server_process(
    command: list,
    name: str,
    port: int,
    cwd: Path,
    env: dict,
    logger: logging.Logger,
    health_endpoint: str = "/health"
) -> Optional[subprocess.Popen]:
    """Start a server process and verify it's running"""
    logger.info(f"Starting {name} on port {port}...")
    
    if not free_port(port, name):
        logger.error(f"Cannot start {name} - port {port} could not be freed")
        return None
    
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(2)
        
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            logger.error(f"{name} failed to start")
            if stderr:
                logger.error(f"Error output: {stderr.decode()[:500]}")
            return None
        
        logger.info(f"{name} process started (PID: {process.pid})")
        
        try:
            if wait_for_server(port, name, timeout=30, endpoint=health_endpoint):
                logger.info(f"{name} is ready and responding")
                return process
            else:
                logger.warning(f"{name} started but health check failed")
                return process
        except ImportError:
            logger.warning(f"{name} started but health check unavailable (requests not installed)")
            return process
            
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}")
        return None

def cleanup_processes(processes: list, logger: logging.Logger):
    """Gracefully terminate all server processes"""
    logger.info("Shutting down servers...")
    for name, process in processes:
        if process and process.poll() is None:
            try:
                logger.info(f"Terminating {name} (PID: {process.pid})...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logger.info(f"{name} terminated successfully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"{name} did not terminate gracefully, forcing kill...")
                    process.kill()
                    process.wait()
                    logger.info(f"{name} killed")
            except Exception as e:
                logger.error(f"Error terminating {name}: {e}")

def start_servers():
    """Main function to start all Syntheverse servers"""
    logger = setup_logging()
    project_root = Path(__file__).parent.parent.parent
    processes = []

    logger.info("Starting Syntheverse Servers...")

    # Pre-startup cleanup: Always kill existing processes and free ports
    logger.info("Performing pre-startup cleanup...")
    port_manager = PortManager(logger)

    # Free all target ports
    ports_to_free = [
        (5001, "Flask API"),
        (3001, "Next.js Frontend"),
        (8000, "RAG API")
    ]

    for port, name in ports_to_free:
        logger.info(f"Freeing port {port} ({name})...")
        success = port_manager.free_port(port, name)
        if not success:
            logger.warning(f"Could not free port {port} ({name}), but continuing with startup...")
        else:
            logger.info(f"Successfully freed port {port} ({name})")

    # Additional cleanup using system commands if available
    try:
        logger.info("Performing additional process cleanup...")
        # Kill any lingering Python and Node processes
        cleanup_commands = [
            ["pkill", "-f", "python.*app.py"],
            ["pkill", "-f", "npm.*dev"],
            ["pkill", "-f", "next.*dev"]
        ]

        for cmd in cleanup_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=5)
                if result.returncode in [0, 1]:  # 0 = killed processes, 1 = no processes found
                    logger.info(f"Cleanup command succeeded: {' '.join(cmd)}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.debug(f"Cleanup command not available: {' '.join(cmd)}")

        # Wait for cleanup to complete
        time.sleep(2)
        logger.info("Pre-startup cleanup completed")

    except Exception as e:
        logger.warning(f"Additional cleanup failed: {e}")

    if not load_environment(project_root, logger):
        logger.error("Environment validation failed. Please configure required variables.")
        return 1

    if not validate_dependencies(project_root, logger):
        logger.error("Dependency validation failed. Please resolve issues above.")
        return 1

    def signal_handler(sig, frame):
        logger.info("Received interrupt signal")
        cleanup_processes(processes, logger)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    env = os.environ.copy()
    env['PYTHONPATH'] = f"{project_root}/src/core:{project_root}/src:{project_root}"
    env['FLASK_SKIP_DOTENV'] = '1'

    # Start Flask API
    flask_cmd = [sys.executable, "src/api/poc-api/app.py"]
    flask_proc = start_server_process(
        flask_cmd,
        "Flask API",
        5001,
        project_root,
        env,
        logger,
        health_endpoint="/health"
    )

    if flask_proc:
        processes.append(("Flask API", flask_proc))
        logger.info("Flask API started successfully")
    else:
        logger.error("Failed to start Flask API - port may still be in use")
        logger.error("Try running: ./scripts/startup/cleanup_servers.sh")
        cleanup_processes(processes, logger)
        return 1

    # Start Legacy Web UI (for blockchain registration)
    web_ui_cmd = [sys.executable, "src/frontend/web-legacy/app.py"]
    web_ui_proc = start_server_process(
        web_ui_cmd,
        "Legacy Web UI",
        5000,
        project_root,
        env,
        logger,
        health_endpoint="/"
    )

    if web_ui_proc:
        processes.append(("Legacy Web UI", web_ui_proc))
        logger.info("Legacy Web UI started successfully")
    else:
        logger.warning("Failed to start Legacy Web UI - continuing without it")

    # Start RAG API
    rag_api_dir = project_root / "src" / "api" / "rag-api" / "api"
    if rag_api_dir.exists():
        rag_env = env.copy()
        rag_cmd = [sys.executable, "rag_api.py"]
        rag_proc = start_server_process(
            rag_cmd,
            "RAG API",
            8000,
            rag_api_dir,
            rag_env,
            logger,
            health_endpoint="/health"
        )

        if rag_proc:
            processes.append(("RAG API", rag_proc))
        else:
            logger.warning("Failed to start RAG API - continuing without it")

    frontend_dir = project_root / "src" / "frontend" / "poc-frontend"
    if frontend_dir.exists():
        nextjs_env = os.environ.copy()
        nextjs_env['PORT'] = '3001'
        nextjs_cmd = ["npm", "run", "dev"]
        nextjs_proc = start_server_process(
            nextjs_cmd,
            "Next.js Frontend",
            3001,
            frontend_dir,
            nextjs_env,
            logger,
            health_endpoint="/"
        )
        
        if nextjs_proc:
            processes.append(("Next.js Frontend", nextjs_proc))
        else:
            logger.warning("Failed to start Next.js Frontend (continuing with Flask API only)")

    logger.info("")
    logger.info("=" * 50)
    logger.info("SERVERS STARTED:")
    logger.info("=" * 50)
    logger.info("🌐 Flask API: http://127.0.0.1:5001")
    if any(name == "RAG API" for name, _ in processes):
        logger.info("🤖 RAG API: http://127.0.0.1:8000")
    if any(name == "Next.js Frontend" for name, _ in processes):
        logger.info("🎯 Next.js UI: http://127.0.0.1:3001")
    logger.info("")
    logger.info("Press Ctrl+C to stop servers...")
    logger.info("=" * 50)

    try:
        while True:
            time.sleep(1)
            for name, process in processes:
                if process.poll() is not None:
                    logger.error(f"{name} process exited unexpectedly (exit code: {process.returncode})")
                    stdout, stderr = process.communicate()
                    if stderr:
                        logger.error(f"{name} error output: {stderr.decode()[:500]}")
                    cleanup_processes(processes, logger)
                    return 1
    except KeyboardInterrupt:
        logger.info("")
        cleanup_processes(processes, logger)
        logger.info("Servers stopped successfully")
        return 0

if __name__ == "__main__":
    sys.exit(start_servers())
