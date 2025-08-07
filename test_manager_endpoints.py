#!/usr/bin/env python3
"""
Test script for manager management endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    """Test HR login"""
    response = requests.post(f"{BASE_URL}/login", json={
        "email": "hr@hoteltest.com",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_get_managers(token):
    """Test getting managers list"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/managers", headers=headers)
    print(f"GET /hr/managers: {response.status_code}")
    if response.status_code == 200:
        managers = response.json()
        print(f"Found {len(managers)} managers")
        for manager in managers:
            print(f"  - {manager['first_name']} {manager['last_name']} ({manager['email']})")
    else:
        print(f"Error: {response.text}")

def test_get_properties(token):
    """Test getting properties list"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/properties", headers=headers)
    print(f"GET /hr/properties: {response.status_code}")
    if response.status_code == 200:
        properties = response.json()
        print(f"Found {len(properties)} properties")
        for prop in properties:
            print(f"  - {prop['name']} ({prop['city']}, {prop['state']})")
    else:
        print(f"Error: {response.text}")

def test_dashboard_stats(token):
    """Test dashboard stats endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/dashboard-stats", headers=headers)
    print(f"GET /hr/dashboard-stats: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Dashboard stats: {json.dumps(stats, indent=2)}")
    else:
        print(f"Error: {response.text}")

def main():
    print("Testing Manager Management Endpoints")
    print("=" * 40)
    
    # Test login
    token = test_login()
    if not token:
        return
    
    print(f"Login successful, token: {token[:20]}...")
    print()
    
    # Test endpoints
    test_dashboard_stats(token)
    print()
    test_get_properties(token)
    print()
    test_get_managers(token)

if __name__ == "__main__":
    main()