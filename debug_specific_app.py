#!/usr/bin/env python3
"""
Debug the specific application causing 422 error
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def debug_specific_app():
    # The application ID from the error log
    app_id = "9aa3fcd8-3c53-43e4-88b8-556a97536071"
    
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
    
    print(f"🔍 Debugging application: {app_id}")
    
    # Get all applications to see if this one exists
    response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    if response.status_code != 200:
        print("❌ Could not get applications")
        return
    
    applications = response.json()
    
    # Find the specific application
    target_app = None
    for app in applications:
        if app["id"] == app_id:
            target_app = app
            break
    
    if target_app:
        print(f"✅ Application found:")
        print(f"   ID: {target_app['id']}")
        print(f"   Status: {target_app['status']}")
        print(f"   Applicant: {target_app['applicant_data']['first_name']} {target_app['applicant_data']['last_name']}")
        print(f"   Position: {target_app['position']}")
        print(f"   Property ID: {target_app['property_id']}")
        
        # Check if it's in the right status for rejection
        if target_app['status'] != 'pending':
            print(f"❌ Application status is '{target_app['status']}', not 'pending'")
            print("   This might be why rejection is failing")
        else:
            print("✅ Application status is 'pending' - should be rejectable")
            
            # Try to reject it
            print("\n🧪 Attempting rejection...")
            rejection_data = {
                "rejection_reason": "Debug test rejection"
            }
            
            response = requests.post(f"{BACKEND_URL}/applications/{app_id}/reject", 
                                   data=rejection_data, headers=manager_headers)
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 422:
                print(f"   422 Error: {response.text}")
                try:
                    error_detail = response.json()
                    print(f"   Details: {json.dumps(error_detail, indent=2)}")
                except:
                    pass
            elif response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('status', 'unknown')}")
            else:
                print(f"   Error: {response.text}")
    else:
        print(f"❌ Application {app_id} not found in manager's applications")
        print(f"   Available applications: {len(applications)}")
        for app in applications[:3]:  # Show first 3
            print(f"   - {app['id']} ({app['status']})")

if __name__ == "__main__":
    debug_specific_app()