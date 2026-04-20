#!/usr/bin/env python
"""Measure minimal main.py startup time"""
import time
import sys
import os

# Change to backend directory
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, '.')

print("=" * 60)
print("STARTUP TIME TEST - MINIMAL APP")
print("=" * 60)

# Test 1: Import minimal FastAPI
print("\n[TEST 1] Importing minimal FastAPI app...")
t0 = time.time()
from app.main import app
t1 = time.time()
elapsed = t1 - t0
print(f"✅ Import time: {elapsed:.3f}s")
print(f"Status: {'FAST ✅' if elapsed < 2 else 'SLOW ⚠️'}")

print("\n" + "=" * 60)
print("Baseline measurement complete.")
print("=" * 60)
