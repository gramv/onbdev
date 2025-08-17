#!/usr/bin/env python3
"""Test manager login after fixing API endpoint"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test manager login"""
    print("Testing manager login at /auth/login...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "manager@demo.com",
            "password": "Manager123!"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"   Token: {data.get('access_token', 'No token')[:50]}...")
        print(f"   User role: {data.get('user', {}).get('role', 'Unknown')}")
        return True
    else:
        print(f"❌ Login failed: {response.text}")
        return False

if __name__ == "__main__":
    test_login()
