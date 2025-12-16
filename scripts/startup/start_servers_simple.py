#!/usr/bin/env python3
"""
Simple Syntheverse Server Startup - Keeps servers running
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def start_servers():
    project_root = Path(__file__).parent

    print("🚀 Starting Syntheverse Servers...")

    # Start Flask API on port 5001
    print("Starting Flask API (port 5001)...")
    env = os.environ.copy()
    env['PYTHONPATH'] = f"{project_root}/src/core:{project_root}/src:{project_root}"
    env['FLASK_SKIP_DOTENV'] = '1'
    env['GROQ_API_KEY'] = 'YOUR_GROQ_API_KEY_HERE'

    flask_cmd = [sys.executable, "src/api/poc-api/app.py"]
    flask_proc = subprocess.Popen(flask_cmd, cwd=project_root, env=env)

    # Wait for Flask to start
    time.sleep(5)

    # Start Next.js on port 3000
    print("Starting Next.js Frontend (port 3000)...")
    frontend_dir = project_root / "src" / "frontend" / "poc-frontend"
    nextjs_cmd = ["npm", "run", "dev"]
    nextjs_proc = subprocess.Popen(nextjs_cmd, cwd=frontend_dir,
                                   env={**os.environ, "PORT": "3000"})

    # Wait for Next.js to start
    time.sleep(10)

    print("\n✅ SERVERS STARTED:")
    print("🌐 Flask API: http://127.0.0.1:5001")
    print("🎯 Next.js UI: http://127.0.0.1:3000")
    print("\nPress Ctrl+C to stop servers...")

    try:
        # Keep running until interrupted
        flask_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        flask_proc.terminate()
        nextjs_proc.terminate()
        flask_proc.wait()
        nextjs_proc.wait()
        print("✅ Servers stopped.")

if __name__ == "__main__":
    start_servers()
