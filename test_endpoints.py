#!/usr/bin/env python3
"""
Test available endpoints
"""

import requests

BACKEND_URL = "http://localhost:8000"

def test_endpoints():
    # Login as manager
    manager_login = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=manager_login)
    if response.status_code != 200:
        print("❌ Manager login failed")
        return
    
    manager_auth = response.json()
    manager_token = manager_auth["token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    
    # Test manager property endpoint
    print("🧪 Testing /manager/property")
    response = requests.get(f"{BACKEND_URL}/manager/property", headers=manager_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Manager property endpoint working")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test manager applications
    print("\n🧪 Testing /manager/applications")
    response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        apps = response.json()
        print(f"   ✅ Found {len(apps)} applications")
        if apps:
            app_id = apps[0]["id"]
            print(f"   Testing rejection with app: {app_id}")
            
            # Test rejection endpoint
            rejection_data = {"rejection_reason": "Test rejection"}
            response = requests.post(f"{BACKEND_URL}/applications/{app_id}/reject", 
                                   data=rejection_data, headers=manager_headers)
            print(f"   Rejection Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Rejection working: {result.get('status', 'unknown')}")
            else:
                print(f"   ❌ Rejection failed: {response.text}")
    else:
        print(f"   ❌ Error: {response.text}")

if __name__ == "__main__":
    test_endpoints()