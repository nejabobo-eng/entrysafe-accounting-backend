#!/usr/bin/env python
"""
ULTRA MINIMAL - just FastAPI, no imports except FastAPI
"""
import time
from fastapi import FastAPI

print(f"[{time.time()}] Creating FastAPI app...")

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print(f"[{time.time()}] Starting uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")
