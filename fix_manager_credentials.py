#!/usr/bin/env python3
"""
Fix manager credentials and test access
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def fix_manager_credentials():
    print("🔧 FIXING MANAGER CREDENTIALS")
    print("=" * 50)
    
    # Login as HR
    print("\n1️⃣  HR LOGIN")
    hr_login = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=hr_login)
    if response.status_code != 200:
        print("❌ HR login failed")
        return False
    
    hr_auth = response.json()
    hr_token = hr_auth["token"]
    hr_headers = {"Authorization": f"Bearer {hr_token}"}
    print("✅ HR logged in successfully")
    
    # Get all managers
    print("\n2️⃣  ANALYZE MANAGERS")
    response = requests.get(f"{BACKEND_URL}/hr/managers", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get managers")
        return False
    
    managers = response.json()
    print(f"✅ Found {len(managers)} managers:")
    
    for manager in managers:
        print(f"\n📋 Manager: {manager['first_name']} {manager['last_name']}")
        print(f"   Email: {manager['email']}")
        print(f"   ID: {manager['id']}")
        print(f"   Property ID: {manager.get('property_id', 'Not set')}")
        print(f"   Is Active: {manager.get('is_active', 'unknown')}")
        
        # Test login with different passwords
        test_passwords = ["manager123", "admin123", "password", "123456"]
        
        for password in test_passwords:
            test_login = {
                "email": manager["email"],
                "password": password
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=test_login)
            if response.status_code == 200:
                print(f"   ✅ Login successful with password: {password}")
                
                # Get manager's applications
                manager_auth = response.json()
                manager_token = manager_auth["token"]
                manager_headers = {"Authorization": f"Bearer {manager_token}"}
                
                response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
                if response.status_code == 200:
                    applications = response.json()
                    print(f"   ✅ Can access {len(applications)} applications")
                    
                    # Check for the problematic application
                    target_app_id = "9aa3fcd8-3c53-43e4-88b8-556a97536071"
                    has_target = any(app["id"] == target_app_id for app in applications)
                    
                    if has_target:
                        print(f"   ✅ Can see target application: {target_app_id}")
                        
                        # Try rejection
                        print(f"   🧪 Testing rejection...")
                        rejection_data = {
                            "rejection_reason": "Test rejection to fix credentials issue"
                        }
                        
                        response = requests.post(f"{BACKEND_URL}/applications/{target_app_id}/reject", 
                                               data=rejection_data, headers=manager_headers)
                        
                        print(f"   Rejection Status: {response.status_code}")
                        if response.status_code == 200:
                            result = response.json()
                            print(f"   ✅ REJECTION SUCCESSFUL: {result.get('status', 'unknown')}")
                            print(f"   Message: {result.get('message', '')}")
                            return True
                        elif response.status_code == 422:
                            print(f"   ❌ 422 Error: {response.text}")
                            try:
                                error_detail = response.json()
                                print(f"   Details: {json.dumps(error_detail, indent=6)}")
                            except:
                                pass
                        else:
                            print(f"   ❌ Rejection failed: {response.text}")
                    else:
                        print(f"   ❌ Cannot see target application")
                        print(f"   Available applications:")
                        for app in applications[:3]:
                            print(f"      - {app['applicant_data']['first_name']} {app['applicant_data']['last_name']} ({app['id']})")
                else:
                    print(f"   ❌ Cannot access applications: {response.status_code}")
                
                break  # Found working password, no need to try others
            else:
                print(f"   ❌ Login failed with password: {password}")
    
    # If we get here, no manager could access the target application
    print(f"\n" + "=" * 50)
    print("🎯 CREDENTIAL FIX SUMMARY")
    print("=" * 50)
    
    print("❌ Could not access target application with any manager")
    print("\n🔧 POSSIBLE SOLUTIONS:")
    print("   1. The manager may not be properly assigned to the property")
    print("   2. The application filtering logic may have an issue")
    print("   3. The manager's property_id may not be set correctly")
    
    # Try to fix the manager assignment
    print(f"\n3️⃣  ATTEMPTING TO FIX MANAGER ASSIGNMENT")
    
    target_property_id = "8611833c-8b4d-4edc-8770-34a84d0955ec"
    target_manager_id = "bb9aed67-1137-4f4a-bb5a-f87e054715e2"
    
    print(f"   Assigning manager {target_manager_id} to property {target_property_id}")
    
    assign_data = {"manager_id": target_manager_id}
    response = requests.post(f"{BACKEND_URL}/hr/properties/{target_property_id}/managers", 
                           data=assign_data, headers=hr_headers)
    
    if response.status_code == 200:
        print("   ✅ Manager assignment successful")
        
        # Try the test again
        print("   🔄 Retrying manager access test...")
        
        # Login with working password (try manager123 first)
        manager_login = {
            "email": "vgoutamram@gmail.com",
            "password": "manager123"
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=manager_login)
        if response.status_code == 200:
            manager_auth = response.json()
            manager_token = manager_auth["token"]
            manager_headers = {"Authorization": f"Bearer {manager_token}"}
            
            response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
            if response.status_code == 200:
                applications = response.json()
                target_app_id = "9aa3fcd8-3c53-43e4-88b8-556a97536071"
                has_target = any(app["id"] == target_app_id for app in applications)
                
                if has_target:
                    print("   ✅ Manager can now see target application!")
                    return True
                else:
                    print("   ❌ Manager still cannot see target application")
    else:
        print(f"   ❌ Manager assignment failed: {response.status_code} - {response.text}")
    
    return False

if __name__ == "__main__":
    fix_manager_credentials()