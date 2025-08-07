#!/usr/bin/env python3
"""
Debug the 422 rejection error
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def debug_rejection():
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
    
    # Get applications
    response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    if response.status_code != 200:
        print("❌ Could not get applications")
        return
    
    applications = response.json()
    pending_apps = [app for app in applications if app["status"] == "pending"]
    
    if not pending_apps:
        print("ℹ️  No pending applications to test with")
        return
    
    app_id = pending_apps[0]["id"]
    print(f"🧪 Testing rejection with application: {app_id}")
    
    # Test rejection with different data formats
    print("\n1️⃣  Testing with Form data (like frontend):")
    rejection_data = {
        "rejection_reason": "Test rejection from debug script"
    }
    
    response = requests.post(f"{BACKEND_URL}/applications/{app_id}/reject", 
                           data=rejection_data, headers=manager_headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   422 Error Details: {response.text}")
        try:
            error_detail = response.json()
            print(f"   Validation Errors: {json.dumps(error_detail, indent=2)}")
        except:
            pass
    elif response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success: {result.get('status', 'unknown')}")
    else:
        print(f"   Error: {response.text}")
    
    print("\n2️⃣  Testing with JSON data:")
    response = requests.post(f"{BACKEND_URL}/applications/{app_id}/reject", 
                           json=rejection_data, headers=manager_headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   422 Error Details: {response.text}")
    elif response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success: {result.get('status', 'unknown')}")
    else:
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    debug_rejection()