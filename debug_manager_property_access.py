#!/usr/bin/env python3
"""
Debug manager property access for the specific application
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def debug_manager_property_access():
    print("🔍 DEBUGGING MANAGER PROPERTY ACCESS")
    print("=" * 60)
    
    # The problematic application and property
    app_id = "9aa3fcd8-3c53-43e4-88b8-556a97536071"
    property_id = "8611833c-8b4d-4edc-8770-34a84d0955ec"
    
    print(f"🎯 Target Application: {app_id}")
    print(f"🏨 Target Property: {property_id}")
    
    # Login as HR to get full system view
    print("\n1️⃣  HR SYSTEM ANALYSIS")
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
    
    # Get property details
    print(f"\n🏨 PROPERTY ANALYSIS: {property_id}")
    response = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get properties")
        return False
    
    properties = response.json()
    target_property = None
    for prop in properties:
        if prop["id"] == property_id:
            target_property = prop
            break
    
    if target_property:
        print(f"✅ Property found: {target_property['name']}")
        print(f"   Address: {target_property['address']}")
        print(f"   Manager IDs: {target_property.get('manager_ids', [])}")
        print(f"   Is Active: {target_property.get('is_active', 'unknown')}")
    else:
        print(f"❌ Property {property_id} not found")
        return False
    
    # Get application details
    print(f"\n📋 APPLICATION ANALYSIS: {app_id}")
    response = requests.get(f"{BACKEND_URL}/hr/applications", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get applications")
        return False
    
    applications = response.json()
    target_application = None
    for app in applications:
        if app["id"] == app_id:
            target_application = app
            break
    
    if target_application:
        print(f"✅ Application found")
        print(f"   Applicant: {target_application['applicant_data']['first_name']} {target_application['applicant_data']['last_name']}")
        print(f"   Status: {target_application['status']}")
        print(f"   Property ID: {target_application['property_id']}")
        print(f"   Position: {target_application['position']}")
        print(f"   Applied At: {target_application['applied_at']}")
        
        # Verify property linkage
        if target_application['property_id'] == property_id:
            print("✅ Application correctly linked to target property")
        else:
            print(f"❌ Application linked to wrong property: {target_application['property_id']}")
    else:
        print(f"❌ Application {app_id} not found")
        return False
    
    # Get all managers and find who should have access
    print(f"\n👥 MANAGER ANALYSIS")
    response = requests.get(f"{BACKEND_URL}/hr/managers", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get managers")
        return False
    
    managers = response.json()
    print(f"✅ Found {len(managers)} total managers")
    
    # Find managers assigned to this property
    assigned_managers = []
    for manager in managers:
        if manager["id"] in target_property.get('manager_ids', []):
            assigned_managers.append(manager)
    
    print(f"📊 Managers assigned to property '{target_property['name']}':")
    if assigned_managers:
        for manager in assigned_managers:
            print(f"   ✅ {manager['first_name']} {manager['last_name']} ({manager['email']})")
            print(f"      Manager ID: {manager['id']}")
            print(f"      Property ID: {manager.get('property_id', 'Not set')}")
    else:
        print("   ❌ No managers assigned to this property")
    
    # Test with each assigned manager
    for manager in assigned_managers:
        print(f"\n🧪 TESTING MANAGER ACCESS: {manager['email']}")
        
        # Login as this manager
        manager_login = {
            "email": manager["email"],
            "password": "manager123"  # Assuming default password
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=manager_login)
        if response.status_code != 200:
            print(f"   ❌ Login failed for {manager['email']}")
            continue
        
        manager_auth = response.json()
        manager_token = manager_auth["token"]
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        print(f"   ✅ Logged in as {manager['email']}")
        print(f"   Manager Property ID: {manager_auth['user'].get('property_id', 'Not set')}")
        
        # Get manager's applications
        response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
        if response.status_code != 200:
            print(f"   ❌ Could not get applications: {response.status_code}")
            continue
        
        manager_applications = response.json()
        print(f"   ✅ Manager can see {len(manager_applications)} applications")
        
        # Check if target application is visible
        target_visible = any(app["id"] == app_id for app in manager_applications)
        if target_visible:
            print(f"   ✅ Target application IS visible to this manager")
            
            # Try to reject the application
            print(f"   🧪 Testing rejection...")
            rejection_data = {
                "rejection_reason": "Debug test rejection"
            }
            
            response = requests.post(f"{BACKEND_URL}/applications/{app_id}/reject", 
                                   data=rejection_data, headers=manager_headers)
            
            print(f"   Rejection Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Rejection successful: {result.get('status', 'unknown')}")
            elif response.status_code == 422:
                print(f"   ❌ 422 Validation Error: {response.text}")
                try:
                    error_detail = response.json()
                    print(f"   Error Details: {json.dumps(error_detail, indent=6)}")
                except:
                    pass
            else:
                print(f"   ❌ Rejection failed: {response.status_code} - {response.text}")
        else:
            print(f"   ❌ Target application NOT visible to this manager")
            print(f"   Available applications:")
            for app in manager_applications[:3]:  # Show first 3
                print(f"      - {app['applicant_data']['first_name']} {app['applicant_data']['last_name']} ({app['id']})")
    
    # Summary
    print(f"\n" + "=" * 60)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if target_property and target_application:
        print(f"✅ Property and Application exist")
        print(f"✅ Application linked to correct property")
        
        if assigned_managers:
            print(f"✅ {len(assigned_managers)} managers assigned to property")
            print(f"\n🔧 NEXT STEPS:")
            print(f"   1. Login as one of the assigned managers")
            print(f"   2. Check if the application appears in their dashboard")
            print(f"   3. If visible, try rejection again")
            print(f"   4. If not visible, there's a filtering issue")
        else:
            print(f"❌ No managers assigned to property")
            print(f"\n🔧 FIX REQUIRED:")
            print(f"   1. Assign a manager to property {property_id}")
            print(f"   2. Use: POST /hr/properties/{property_id}/managers")
    
    return True

if __name__ == "__main__":
    debug_manager_property_access()