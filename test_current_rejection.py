#!/usr/bin/env python3
"""
Quick test to check current rejection behavior
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def test_current_rejection():
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
    
    # Test rejection
    rejection_data = {
        "rejection_reason": "Test rejection to check talent pool behavior"
    }
    
    response = requests.post(f"{BACKEND_URL}/hr/applications/{app_id}/reject", 
                           data=rejection_data, headers=manager_headers)
    
    print(f"📊 Rejection Response Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"📋 Response: {json.dumps(result, indent=2)}")
        
        # Check if it went to talent pool
        if result.get('status') == 'talent_pool':
            print("✅ Application correctly moved to talent pool!")
        else:
            print("❌ Application was not moved to talent pool")
    else:
        print(f"❌ Rejection failed: {response.text}")

if __name__ == "__main__":
    test_current_rejection()