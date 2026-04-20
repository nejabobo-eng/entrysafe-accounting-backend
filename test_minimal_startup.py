"""Test minimal startup time"""
import time
import subprocess
import sys
import requests
from threading import Thread

def run_server():
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

# Start server in background
server_thread = Thread(target=run_server, daemon=True)
server_thread.start()

# Wait for server to be ready
time.sleep(2)

# Test health endpoint
try:
    start = time.time()
    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
    elapsed = time.time() - start
    
    print(f"✅ Server responded: {response.json()}")
    print(f"✅ Response time: {elapsed:.3f}s")
    print(f"✅ Status code: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
