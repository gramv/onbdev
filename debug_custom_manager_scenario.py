#!/usr/bin/env python3
"""
Debug the custom manager scenario where rejection is failing
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def debug_custom_manager_scenario():
    print("🔍 DEBUGGING CUSTOM MANAGER SCENARIO")
    print("=" * 60)
    
    # The problematic application ID from your error
    problematic_app_id = "9aa3fcd8-3c53-43e4-88b8-556a97536071"
    
    # Login with your custom manager credentials
    print("\n1️⃣  LOGIN WITH CUSTOM MANAGER")
    custom_manager_login = {
        "email": "vgoutamram@gmail.com",  # From the analysis
        "password": "Gouthi321@"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=custom_manager_login)
    if response.status_code != 200:
        print(f"❌ Custom manager login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    manager_auth = response.json()
    manager_token = manager_auth["token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    
    print("✅ Custom manager logged in successfully")
    print(f"   Manager: {manager_auth['user']['first_name']} {manager_auth['user']['last_name']}")
    print(f"   Email: {manager_auth['user']['email']}")
    print(f"   Property ID: {manager_auth['user'].get('property_id', 'None')}")
    
    # Get manager's applications
    print("\n2️⃣  GET MANAGER'S APPLICATIONS")
    response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    if response.status_code != 200:
        print(f"❌ Could not get manager applications: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    manager_applications = response.json()
    print(f"✅ Manager can see {len(manager_applications)} applications")
    
    # Check if the problematic application is in the list
    problematic_app = None
    for app in manager_applications:
        if app['id'] == problematic_app_id:
            problematic_app = app
            break
    
    if problematic_app:
        print(f"\n✅ FOUND PROBLEMATIC APPLICATION IN MANAGER'S LIST:")
        print(f"   ID: {problematic_app['id']}")
        print(f"   Status: {problematic_app['status']}")
        print(f"   Applicant: {problematic_app['applicant_data']['first_name']} {problematic_app['applicant_data']['last_name']}")
        print(f"   Position: {problematic_app['position']}")
        print(f"   Property ID: {problematic_app['property_id']}")
        
        # Try to reject this specific application
        print(f"\n3️⃣  ATTEMPT REJECTION OF PROBLEMATIC APPLICATION")
        
        rejection_data = {
            "rejection_reason": "Debug test - checking why rejection fails"
        }
        
        print(f"   Sending rejection request...")
        print(f"   URL: {BACKEND_URL}/applications/{problematic_app_id}/reject")
        print(f"   Data: {rejection_data}")
        
        response = requests.post(f"{BACKEND_URL}/applications/{problematic_app_id}/reject", 
                               data=rejection_data, headers=manager_headers)
        
        print(f"   Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 422:
            print(f"   ❌ 422 Validation Error:")
            try:
                error_detail = response.json()
                print(f"   Error Details: {json.dumps(error_detail, indent=4)}")
                
                # Check what validation is failing
                if 'detail' in error_detail and isinstance(error_detail['detail'], list):
                    for error in error_detail['detail']:
                        print(f"   - Field: {error.get('loc', 'unknown')}")
                        print(f"     Type: {error.get('type', 'unknown')}")
                        print(f"     Message: {error.get('msg', 'unknown')}")
                        print(f"     Input: {error.get('input', 'unknown')}")
            except:
                print(f"   Raw response: {response.text}")
                
        elif response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', '')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    else:
        print(f"\n❌ PROBLEMATIC APPLICATION NOT FOUND IN MANAGER'S LIST")
        print(f"   Application ID: {problematic_app_id}")
        print(f"   This means the manager doesn't have access to this application")
        
        # Show what applications the manager can see
        print(f"\n📋 APPLICATIONS MANAGER CAN SEE:")
        for i, app in enumerate(manager_applications, 1):
            print(f"   {i}. {app['applicant_data']['first_name']} {app['applicant_data']['last_name']}")
            print(f"      ID: {app['id']}")
            print(f"      Status: {app['status']}")
            print(f"      Property: {app['property_id']}")
            print()
    
    # Get HR view to compare
    print("\n4️⃣  GET HR VIEW FOR COMPARISON")
    hr_login = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=hr_login)
    if response.status_code == 200:
        hr_auth = response.json()
        hr_token = hr_auth["token"]
        hr_headers = {"Authorization": f"Bearer {hr_token}"}
        
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=hr_headers)
        if response.status_code == 200:
            all_applications = response.json()
            
            # Find the problematic application in HR view
            hr_problematic_app = None
            for app in all_applications:
                if app['id'] == problematic_app_id:
                    hr_problematic_app = app
                    break
            
            if hr_problematic_app:
                print(f"✅ HR CAN SEE THE PROBLEMATIC APPLICATION:")
                print(f"   ID: {hr_problematic_app['id']}")
                print(f"   Status: {hr_problematic_app['status']}")
                print(f"   Property ID: {hr_problematic_app['property_id']}")
                print(f"   Applicant: {hr_problematic_app['applicant_data']['first_name']} {hr_problematic_app['applicant_data']['last_name']}")
                
                # Check property details
                response = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
                if response.status_code == 200:
                    properties = response.json()
                    target_property = None
                    for prop in properties:
                        if prop['id'] == hr_problematic_app['property_id']:
                            target_property = prop
                            break
                    
                    if target_property:
                        print(f"\n🏨 PROPERTY DETAILS:")
                        print(f"   Property ID: {target_property['id']}")
                        print(f"   Property Name: {target_property['name']}")
                        print(f"   Manager IDs: {target_property.get('manager_ids', [])}")
                        
                        # Check if custom manager is assigned to this property
                        manager_user_id = manager_auth['user']['id']
                        if manager_user_id in target_property.get('manager_ids', []):
                            print(f"   ✅ Custom manager IS assigned to this property")
                        else:
                            print(f"   ❌ Custom manager is NOT assigned to this property")
                            print(f"   Manager User ID: {manager_user_id}")
                            print(f"   Property Manager IDs: {target_property.get('manager_ids', [])}")
            else:
                print(f"❌ HR cannot see the problematic application either")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if problematic_app:
        print("✅ Manager can see the application")
        print("❌ But rejection is failing with 422 error")
        print("\n🔧 LIKELY CAUSES:")
        print("   1. Form validation issue in the endpoint")
        print("   2. Missing required fields in the request")
        print("   3. Application status not allowing rejection")
        print("   4. Property access validation failing")
    else:
        print("❌ Manager cannot see the application")
        print("\n🔧 LIKELY CAUSES:")
        print("   1. Manager not properly assigned to the property")
        print("   2. Application belongs to different property")
        print("   3. Manager filtering logic issue")
    
    return True

if __name__ == "__main__":
    debug_custom_manager_scenario()