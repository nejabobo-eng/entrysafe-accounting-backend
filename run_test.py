#!/usr/bin/env python
"""
Start minimal test app and print startup timestamp
"""
import uvicorn
import time

start = time.time()
print(f"[{start}] Starting test backend...")

try:
    uvicorn.run(
        "test_app:app",
        host="127.0.0.1",
        port=8000,
        log_level="critical",
        timeout_keep_alive=5
    )
except KeyboardInterrupt:
    elapsed = time.time() - start
    print(f"\n[STOPPED] Ran for {elapsed:.1f} seconds")
