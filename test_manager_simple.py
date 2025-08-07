#!/usr/bin/env python3
"""
Simple test to check manager authentication
"""

import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

def test_basic_manager_auth():
    headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    
    print("🔍 Testing basic manager authentication...")
    
    # Test if manager can access HR applications (should be restricted)
    print("\n1. Testing manager access to HR endpoint (should fail)")
    try:
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ Manager properly restricted from HR endpoints")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test if we can access any manager endpoint
    print("\n2. Testing if any manager endpoints exist")
    try:
        # Try the old manager endpoint that might exist
        response = requests.get(f"{BACKEND_URL}/manager/pending-reviews", headers=headers)
        print(f"   /manager/pending-reviews Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Manager authentication is working")
        elif response.status_code == 403:
            print("   ❌ Manager authentication failed")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_basic_manager_auth()