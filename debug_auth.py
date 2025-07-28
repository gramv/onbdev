#!/usr/bin/env python3
"""
Debug authentication to see what's happening
"""

import requests
import json

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"

# Proper JWT tokens
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"

def debug_auth():
    """Debug authentication"""
    print("🔍 Debugging Authentication")
    print("=" * 40)
    
    # Test auth/me endpoint to see user info
    print("\n📋 Testing /auth/me endpoint")
    try:
        headers = {"Authorization": f"Bearer {HR_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print("   ✅ User info retrieved:")
            print(f"   📊 User ID: {user_info.get('id')}")
            print(f"   📊 Role: {user_info.get('role')}")
            print(f"   📊 Email: {user_info.get('email')}")
            print(f"   📊 Full info: {json.dumps(user_info, indent=2)}")
        else:
            print(f"   ❌ Auth/me failed: {response.status_code}")
            print(f"   📋 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Auth/me error: {e}")

if __name__ == "__main__":
    debug_auth()