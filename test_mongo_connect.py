#!/usr/bin/env python
"""
Test if connect_to_mongo completes quickly
"""
import asyncio
import time

async def test_mongo_connect():
    print("Testing MongoDB connection...")
    start = time.time()
    
    try:
        from app.core.database import connect_to_mongo
        await connect_to_mongo()
        elapsed = time.time() - start
        print(f"✅ MongoDB connect completed in {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start
        print(f"⚠️ MongoDB connect failed after {elapsed:.2f}s: {e}")

asyncio.run(test_mongo_connect())
