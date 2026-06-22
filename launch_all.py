#!/usr/bin/env python3
"""Launch all services locally with proper environment setup."""

import subprocess
import sys
import time
import os
from pathlib import Path

# Setup environment (load from .env or existing shell variable)
from dotenv import load_dotenv
load_dotenv()

if not os.environ.get("MISTRAL_API_KEY"):
    print("[WARN] MISTRAL_API_KEY not set. Create .env from .env.example or export the variable.")
os.environ["OPTIMIZER_URL"] = "http://localhost:8000"

# Get project root
project_root = Path(__file__).parent.resolve()
data_dir = project_root / "data" / "prompts"
os.environ["PROMPT_DATA_DIR"] = str(data_dir)

print("=" * 60)
print("🚀 Launching ALL Services (LOCAL with REAL GEPA)")
print("=" * 60)
print()
print(f"📁 Project: {project_root}")
print(f"📂 Data dir: {data_dir}")
print(f"🔑 Mistral API: {'set' if os.environ.get('MISTRAL_API_KEY') else 'NOT SET'}")
print()

# Start Optimizer
print("[1/2] Starting Optimizer Service with REAL GEPA...")
optimizer_cmd = [
    sys.executable, "-m", "uvicorn",
    "services.optimizer.src.api:app",
    "--host", "0.0.0.0",
    "--port", "8000"
]
optimizer_proc = subprocess.Popen(
    optimizer_cmd,
    cwd=project_root,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

time.sleep(3)

# Start Prompt Manager
print("[2/2] Starting Prompt Manager...")
pm_cmd = [
    sys.executable, "-m", "uvicorn",
    "services.prompt_manager.src.api:app",
    "--host", "0.0.0.0",
    "--port", "8002"
]
pm_proc = subprocess.Popen(
    pm_cmd,
    cwd=project_root,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)

time.sleep(2)

print()
print("=" * 60)
print("✅ All services started!")
print("=" * 60)
print()
print("📊 Services:")
print("   • Optimizer:  http://localhost:8000")
print("   • Prompt Manager: http://localhost:8002")
print()
print("🌐 Open UI:")
print("   start http://localhost:8002")
print()
print("Press Ctrl+C to stop...")

# Wait for interrupt
try:
    while True:
        time.sleep(1)
        # Check if processes are still running
        if optimizer_proc.poll() is not None:
            print("⚠️ Optimizer stopped!")
            break
        if pm_proc.poll() is not None:
            print("⚠️ Prompt Manager stopped!")
            break
except KeyboardInterrupt:
    print("\n\n🛑 Stopping services...")
    optimizer_proc.terminate()
    pm_proc.terminate()
    print("✅ Done!")
