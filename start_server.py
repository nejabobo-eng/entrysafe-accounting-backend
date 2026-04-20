#!/usr/bin/env python
"""
Quick server starter for testing
"""
import uvicorn
import sys

if __name__ == "__main__":
    print("🚀 Starting Entry Safe Backend...")
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="debug"
        )
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)
