#!/usr/bin/env python3
"""
Check what's in the database for the manager user
"""

import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

def check_manager_info():
    print("🔍 Checking manager user information...")
    
    # Test 1: Get manager info using auth/me endpoint
    print("\n1. Getting manager user info")
    try:
        headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"   Manager info: {json.dumps(user_info, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Get HR managers list to see manager details
    print("\n2. Getting managers list from HR")
    try:
        hr_headers = {"Authorization": f"Bearer {HR_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/hr/managers", headers=hr_headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            managers = response.json()
            print(f"   Managers found: {len(managers)}")
            for manager in managers:
                if manager.get('id') == 'mgr_test_001':
                    print(f"   Target manager: {json.dumps(manager, indent=2)}")
                    break
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    check_manager_info()