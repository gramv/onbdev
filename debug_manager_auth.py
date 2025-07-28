#!/usr/bin/env python3
"""
Debug manager authentication issues
"""

import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

def test_manager_endpoints():
    headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    
    print("🔍 Testing manager endpoints...")
    
    # Test 1: Manager dashboard stats
    print("\n1. Testing /manager/dashboard-stats")
    try:
        response = requests.get(f"{BACKEND_URL}/manager/dashboard-stats", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Manager applications
    print("\n2. Testing /manager/applications")
    try:
        response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            apps = response.json()
            print(f"   Applications found: {len(apps)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: Check if manager exists in properties
    print("\n3. Testing property manager assignment")
    try:
        # Use HR token to check properties
        hr_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"
        hr_headers = {"Authorization": f"Bearer {hr_token}"}
        
        response = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
        if response.status_code == 200:
            properties = response.json()
            for prop in properties:
                if prop.get('id') == 'prop_test_001':
                    print(f"   Property manager_ids: {prop.get('manager_ids', [])}")
                    if 'mgr_test_001' in prop.get('manager_ids', []):
                        print("   ✅ Manager is assigned to property")
                    else:
                        print("   ❌ Manager NOT assigned to property")
                    break
        else:
            print(f"   Error getting properties: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_manager_endpoints()