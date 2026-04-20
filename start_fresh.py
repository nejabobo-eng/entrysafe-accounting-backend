#!/usr/bin/env python
"""
Entry Safe Backend Starter
Times the actual startup
"""
import time
import sys

start_time = time.time()
print(f"[{start_time:.1f}] Starting backend...")

try:
    import uvicorn
    elapsed_import = time.time() - start_time
    print(f"[+{elapsed_import:.2f}s] uvicorn imported")
    
    print(f"[+{(time.time() - start_time):.2f}s] Running uvicorn...")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False
    )
except KeyboardInterrupt:
    elapsed_total = time.time() - start_time
    print(f"\n[STOPPED] Total time: {elapsed_total:.1f}s")
except Exception as e:
    elapsed_total = time.time() - start_time
    print(f"\n❌ ERROR after {elapsed_total:.1f}s: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
