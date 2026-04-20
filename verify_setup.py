#!/usr/bin/env python3
"""
Test if the FastAPI application can be imported and started
"""
import sys

try:
    print("✅ Attempting to import FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI imported successfully")
    
    print("✅ Attempting to import app.main...")
    from app.main import app
    print("✅ app.main imported successfully")
    
    print("✅ FastAPI Application Summary:")
    print(f"   - App Title: {app.title}")
    print(f"   - Version: {app.version}")
    print(f"   - Routes: {len(app.routes)}")
    
    print("\n✅ Available Endpoints:")
    for route in app.routes:
        print(f"   - {route}")
    
    print("\n✅ BACKEND STRUCTURE VERIFIED!")
    print("✅ All imports successful - ready to run with: uvicorn app.main:app --reload")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
