#!/usr/bin/env python3
"""
Test specific endpoints for user story validation
"""

import requests

BACKEND_URL = "http://127.0.0.1:8000"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

def test_endpoints():
    headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    
    print("🔍 Testing specific endpoints for user story validation...")
    
    # Test 1: Manager access to HR properties (should be restricted)
    print("\n1. Manager accessing /hr/properties (should be 403)")
    try:
        response = requests.get(f"{BACKEND_URL}/hr/properties", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ Correctly restricted")
        else:
            print(f"   ❌ Not restricted: {response.text[:100]}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Manager access to their own applications
    print("\n2. Manager accessing /manager/applications")
    try:
        response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Can access own applications")
        else:
            print(f"   ❌ Cannot access: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Manager dashboard stats
    print("\n3. Manager accessing /manager/dashboard-stats")
    try:
        response = requests.get(f"{BACKEND_URL}/manager/dashboard-stats", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Can access dashboard stats")
        else:
            print(f"   ❌ Cannot access: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_endpoints()