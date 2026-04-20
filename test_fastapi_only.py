#!/usr/bin/env python
"""TEST 0: Baseline Python + FastAPI import ONLY"""
import time
import sys

print("=" * 60)
print("TEST 0 - BASELINE (FastAPI import only)")
print("=" * 60)

t0 = time.time()
from fastapi import FastAPI
t1 = time.time()
elapsed = t1 - t0

print(f"\n✅ FastAPI import: {elapsed:.3f}s")
print(f"Status: {'FAST ✅' if elapsed < 1 else 'SLOW ⚠️'}")

print("\n" + "=" * 60)
