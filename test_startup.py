#!/usr/bin/env python
"""
Minimal test to see if uvicorn can start
"""
import asyncio
from app.main import app
from app.core.database import connect_to_mongo, close_mongo_connection

async def test_startup():
    print("Testing app startup...")
    try:
        await connect_to_mongo()
        print("✅ Startup successful")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_startup())
