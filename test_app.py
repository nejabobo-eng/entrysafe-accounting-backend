#!/usr/bin/env python
"""
Minimal startup test - NO MongoDB, NO fancy config
Pure FastAPI only
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Entry Safe Test",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Test API running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting test backend (NO MongoDB)...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")
