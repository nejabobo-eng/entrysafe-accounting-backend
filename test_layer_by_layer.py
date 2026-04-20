#!/usr/bin/env python
"""TEST 2: What's causing the delay?"""
import time
import sys
import os

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, '.')

print("=" * 60)
print("TEST 2 - LAYER BY LAYER")
print("=" * 60)

# Test 2a: config
print("\n[2a] Importing config...")
t0 = time.time()
from app.config import settings
t1 = time.time()
print(f"config: {t1-t0:.3f}s")

# Test 2b: database
print("[2b] Importing database...")
t0 = time.time()
from app.core.database import connect_to_mongo
t1 = time.time()
print(f"database: {t1-t0:.3f}s")

# Test 2c: routes.transactions
print("[2c] Importing routes.transactions...")
t0 = time.time()
from app.routes import transactions
t1 = time.time()
print(f"routes.transactions: {t1-t0:.3f}s")

# Test 2d: routes.settings
print("[2d] Importing routes.settings...")
t0 = time.time()
from app.routes import settings as settings_routes
t1 = time.time()
print(f"routes.settings: {t1-t0:.3f}s")

print("\n" + "=" * 60)
