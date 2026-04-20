#!/usr/bin/env python
"""
DIAGNOSTIC TEST - Measure startup time at each layer
"""
import time
import sys

print("=" * 60)
print("STARTUP TIMING DIAGNOSTIC")
print("=" * 60)

# TEST 1: Ultra minimal (just FastAPI)
print("\n🟩 TEST 1: Ultra Minimal (FastAPI only)")
start = time.time()
try:
    from fastapi import FastAPI
    app1 = FastAPI()
    elapsed = time.time() - start
    print(f"✅ INSTANT: {elapsed:.3f}s")
    test1 = "INSTANT"
except Exception as e:
    print(f"❌ ERROR: {e}")
    test1 = "ERROR"

# TEST 2: FastAPI + CORSMiddleware (no routes)
print("\n🟨 TEST 2: FastAPI + CORS")
start = time.time()
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app2 = FastAPI()
    app2.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    elapsed = time.time() - start
    print(f"✅ INSTANT: {elapsed:.3f}s")
    test2 = "INSTANT"
except Exception as e:
    print(f"❌ ERROR: {e}")
    test2 = "ERROR"

# TEST 3: Import app.config
print("\n🟧 TEST 3: Import app.config")
start = time.time()
try:
    from app.config import settings
    elapsed = time.time() - start
    print(f"✅ CONFIG LOADED: {elapsed:.3f}s")
    print(f"   OPENAI_KEY: {settings.OPENAI_API_KEY[:20]}...")
    print(f"   MONGO_URI: {settings.MONGO_URI[:50]}...")
    test3 = "INSTANT" if elapsed < 2 else "SLOW"
except Exception as e:
    print(f"❌ ERROR: {e}")
    test3 = "ERROR"

# TEST 4: Import AIService (THIS IS THE SUSPECT)
print("\n🔴 TEST 4: Import AIService")
start = time.time()
try:
    from app.services.ai_service import AIService
    elapsed = time.time() - start
    print(f"✅ AI SERVICE IMPORTED: {elapsed:.3f}s")
    test4 = "INSTANT" if elapsed < 2 else "SLOW"
except Exception as e:
    print(f"❌ ERROR: {e}")
    test4 = "ERROR"

# TEST 5: Instantiate AIService
print("\n🔴 TEST 5: Instantiate AIService()")
start = time.time()
try:
    ai_service = AIService()
    elapsed = time.time() - start
    print(f"✅ AI SERVICE INSTANTIATED: {elapsed:.3f}s")
    test5 = "INSTANT" if elapsed < 2 else "SLOW"
except Exception as e:
    print(f"❌ ERROR: {e}")
    test5 = "ERROR"

# TEST 6: Import transactions router (includes AIService init)
print("\n⚠️ TEST 6: Import transactions router")
start = time.time()
try:
    from app.routes import transactions
    elapsed = time.time() - start
    print(f"✅ TRANSACTIONS ROUTER IMPORTED: {elapsed:.3f}s")
    test6 = "INSTANT" if elapsed < 2 else "SLOW"
except Exception as e:
    print(f"❌ ERROR: {e}")
    test6 = "ERROR"

# TEST 7: Import full main.py
print("\n⚠️ TEST 7: Import app.main")
start = time.time()
try:
    from app.main import app
    elapsed = time.time() - start
    print(f"✅ MAIN APP IMPORTED: {elapsed:.3f}s")
    test7 = "INSTANT" if elapsed < 2 else "SLOW"
except Exception as e:
    print(f"❌ ERROR: {e}")
    test7 = "ERROR"

# SUMMARY
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Test 1 (FastAPI):        {test1}")
print(f"Test 2 (FastAPI+CORS):   {test2}")
print(f"Test 3 (config):         {test3}")
print(f"Test 4 (AIService import):{test4}")
print(f"Test 5 (AIService init): {test5}")
print(f"Test 6 (transactions):   {test6}")
print(f"Test 7 (app.main):       {test7}")

# Diagnosis
print("\n" + "=" * 60)
print("DIAGNOSIS")
print("=" * 60)

if test7 == "SLOW":
    if test6 == "SLOW":
        print("❌ PROBLEM: transactions router import is slow")
        print("   Suspect: AIService initialization")
    elif test5 == "SLOW":
        print("❌ PROBLEM: AIService() instantiation is slow")
        print("   Suspect: OpenAI client initialization or network call")
    elif test4 == "SLOW":
        print("❌ PROBLEM: AIService import is slow")
        print("   Suspect: Heavy dependency loading")
    else:
        print("❌ PROBLEM: app.main has slow startup hook")
        print("   Suspect: startup event initialization")
else:
    print("✅ GOOD: All imports are fast")
    print("   Problem might be network latency on first request or uvicorn startup")
