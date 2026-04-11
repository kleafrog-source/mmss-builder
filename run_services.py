#!/usr/bin/env python3
"""Launch Optimizer and MMSS services in background."""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

# Global list to track processes
processes = []

def cleanup(signum=None, frame=None):
    """Cleanup function to kill all child processes."""
    print("\nShutting down services...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            try:
                proc.kill()
            except:
                pass
    sys.exit(0)

# Register cleanup handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def start_service(name, cwd, port, log_file):
    """Start a service in background."""
    print(f"Starting {name} on port {port}...")
    
    # Open log file
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_fp = open(log_file, 'w')
    
    # Start process
    proc = subprocess.Popen(
        [
            sys.executable, '-m', 'uvicorn',
            'src.api:app',
            '--host', '0.0.0.0',
            '--port', str(port),
            '--reload'
        ],
        cwd=cwd,
        stdout=log_fp,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )
    
    processes.append(proc)
    print(f"  {name} started (PID: {proc.pid}, log: {log_file})")
    return proc

def check_service(url, timeout=5):
    """Check if service is running."""
    import urllib.request
    import ssl
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, method='GET')
        response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return response.status == 200
    except:
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("GEPA-Pezzo-MMSS Service Launcher")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    
    # Start services
    optimizer_proc = start_service(
        "Optimizer Service",
        base_dir / "services" / "optimizer",
        8000,
        "logs/optimizer.log"
    )
    
    mmss_proc = start_service(
        "MMSS Service",
        base_dir / "services" / "mmss",
        8001,
        "logs/mmss.log"
    )
    
    print("\nWaiting for services to start...")
    time.sleep(8)
    
    # Check services
    optimizer_ok = check_service("http://localhost:8000/health")
    mmss_ok = check_service("http://localhost:8001/health")
    
    print("\n" + "=" * 60)
    print("Status Check")
    print("=" * 60)
    print(f"Optimizer Service (:8000): {'✓ RUNNING' if optimizer_ok else '✗ NOT READY'}")
    print(f"MMSS Service (:8001): {'✓ RUNNING' if mmss_ok else '✗ NOT READY'}")
    
    if optimizer_ok and mmss_ok:
        print("\n✅ All services are running!")
        print("\nPress Ctrl+C to stop services")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            cleanup()
    else:
        print("\n⚠️ Some services failed to start.")
        print("Check logs in logs/ directory")
        cleanup()

if __name__ == "__main__":
    main()
