#!/usr/bin/env python
"""
Test if uvicorn can start without hanging
"""
import time
import threading
import requests

def start_server():
    """Start uvicorn in a thread"""
    import uvicorn
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False,
            workers=1
        )
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()

# Start server in background
print("Starting backend in background...")
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Wait for startup
print("Waiting 5 seconds for startup...")
time.sleep(5)

# Try to hit health endpoint
try:
    print("Testing /health endpoint...")
    response = requests.get("http://localhost:8000/health", timeout=2)
    print(f"✅ Response: {response.status_code}")
    print(f"   Body: {response.json()}")
except Exception as e:
    print(f"❌ Connection failed: {e}")

print("\nKeep server running (Ctrl+C to stop)...")
try:
    server_thread.join()
except KeyboardInterrupt:
    print("\nShutdown")
