#!/usr/bin/env python
"""
ABSOLUTE MINIMAL - No startup events, no database, just FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Working"}

if __name__ == "__main__":
    import uvicorn
    import time
    start = time.time()
    print(f"Starting at {start}")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
