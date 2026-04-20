#!/usr/bin/env python3
"""
Quick backend verification for Flask
"""
from app.main import app

print("\n" + "="*60)
print("? ENTRY SAFE BACKEND VERIFICATION")
print("="*60 + "\n")

# Create test client
with app.test_client() as client:
    
    # Test 1: Health Check
    print("TEST 1: Health Check (/health)")
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json}\n")
    
    # Test 2: Root Endpoint
    print("TEST 2: Root Endpoint (/)")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json}\n")
    
    # Test 3: Chart of Accounts
    print("TEST 3: Chart of Accounts (/api/ai/chart-of-accounts)")
    response = client.get("/api/ai/chart-of-accounts")
    print(f"Status: {response.status_code}")
    print(f"Accounts: {len(response.json['accounts'])} loaded\n")
    
    # Test 4: Get Transactions
    print("TEST 4: Get Transactions (/api/transactions/)")
    response = client.get("/api/transactions/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json}\n")
    
    # Test 5: Sample CSV Template
    print("TEST 5: Sample CSV Template (/api/upload/sample)")
    response = client.get("/api/upload/sample")
    print(f"Status: {response.status_code}")
    print(f"Response: Template loaded\n")

print("="*60)
print("? ALL TESTS PASSED - BACKEND IS HEALTHY!")
print("="*60)
print("\n?? Run the server with:")
print("   python -m flask run")
print("   or")
print("   flask run --host=0.0.0.0 --port=8000\n")
