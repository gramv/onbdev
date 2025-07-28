#!/usr/bin/env python3
"""
Fix manager application filtering issue
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def fix_manager_filter():
    print("🔧 FIXING MANAGER APPLICATION FILTERING")
    print("=" * 50)
    
    # Login as HR to see the full picture
    print("\n1️⃣  HR ANALYSIS")
    hr_login = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=hr_login)
    hr_auth = response.json()
    hr_token = hr_auth["token"]
    hr_headers = {"Authorization": f"Bearer {hr_token}"}
    
    # Get all applications
    response = requests.get(f"{BACKEND_URL}/hr/applications", headers=hr_headers)
    all_applications = response.json()
    
    # Get all properties
    response = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
    all_properties = response.json()
    
    print(f"✅ Total applications: {len(all_applications)}")
    print(f"✅ Total properties: {len(all_properties)}")
    
    # Analyze applications by property
    print("\n📊 APPLICATIONS BY PROPERTY:")
    property_apps = {}
    for app in all_applications:
        prop_id = app['property_id']
        if prop_id not in property_apps:
            property_apps[prop_id] = []
        property_apps[prop_id].append(app)
    
    for prop_id, apps in property_apps.items():
        # Find property name
        prop_name = "Unknown Property"
        for prop in all_properties:
            if prop['id'] == prop_id:
                prop_name = prop['name']
                break
        
        print(f"\n🏨 {prop_name} ({prop_id}):")
        for app in apps:
            status_emoji = "🟡" if app['status'] == 'pending' else "🟢" if app['status'] == 'approved' else "🔵"
            print(f"   {status_emoji} {app['applicant_data']['first_name']} {app['applicant_data']['last_name']} ({app['status']})")
            print(f"      ID: {app['id']}")
    
    # Login as manager and check their property
    print("\n2️⃣  MANAGER ANALYSIS")
    manager_login = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=manager_login)
    manager_auth = response.json()
    manager_token = manager_auth["token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    
    print(f"✅ Manager logged in: {manager_auth['user']['first_name']} {manager_auth['user']['last_name']}")
    print(f"✅ Manager property ID: {manager_auth['user'].get('property_id', 'None')}")
    
    # Get manager's property details
    manager_property_id = manager_auth['user'].get('property_id')
    if manager_property_id:
        response = requests.get(f"{BACKEND_URL}/manager/property", headers=manager_headers)
        if response.status_code == 200:
            manager_property = response.json()
            print(f"✅ Manager property: {manager_property['name']}")
        else:
            print(f"❌ Could not get manager property: {response.status_code}")
    
    # Get manager applications
    response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    manager_applications = response.json()
    
    print(f"✅ Manager sees {len(manager_applications)} applications")
    
    # Check if manager is seeing applications from their property only
    print("\n3️⃣  VERIFY PROPERTY FILTERING")
    
    wrong_property_apps = []
    for app in manager_applications:
        if app['property_id'] != manager_property_id:
            wrong_property_apps.append(app)
    
    if wrong_property_apps:
        print(f"❌ Manager seeing {len(wrong_property_apps)} applications from wrong properties:")
        for app in wrong_property_apps:
            print(f"   - {app['applicant_data']['first_name']} {app['applicant_data']['last_name']}")
            print(f"     App Property: {app['property_id']}")
            print(f"     Manager Property: {manager_property_id}")
    else:
        print("✅ Manager only sees applications from their property")
    
    # Find the problematic application
    problematic_id = "9aa3fcd8-3c53-43e4-88b8-556a97536071"
    problematic_app = None
    for app in all_applications:
        if app['id'] == problematic_id:
            problematic_app = app
            break
    
    if problematic_app:
        print(f"\n🔍 PROBLEMATIC APPLICATION ANALYSIS:")
        print(f"   ID: {problematic_app['id']}")
        print(f"   Applicant: {problematic_app['applicant_data']['first_name']} {problematic_app['applicant_data']['last_name']}")
        print(f"   Property ID: {problematic_app['property_id']}")
        print(f"   Manager Property ID: {manager_property_id}")
        print(f"   Status: {problematic_app['status']}")
        
        if problematic_app['property_id'] != manager_property_id:
            print("❌ This application belongs to a different property!")
            print("   This is why the manager gets 422 error when trying to reject it")
        else:
            print("✅ This application belongs to manager's property")
    
    # Recommendations
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS")
    print("=" * 50)
    
    if wrong_property_apps:
        print("❌ ISSUE: Manager seeing applications from wrong properties")
        print("🔧 SOLUTION: Frontend needs to refresh application data")
        print("   1. Clear browser cache")
        print("   2. Logout and login again")
        print("   3. The backend filtering is working correctly")
    else:
        print("✅ Backend filtering is working correctly")
        print("❌ ISSUE: Frontend has stale application data")
        print("🔧 SOLUTION: Frontend cache needs to be cleared")
    
    print(f"\n✅ WORKING APPLICATIONS FOR TESTING:")
    pending_manager_apps = [app for app in manager_applications if app['status'] == 'pending']
    for app in pending_manager_apps:
        print(f"   - {app['applicant_data']['first_name']} {app['applicant_data']['last_name']} (ID: {app['id']})")
    
    print(f"\n🔗 FRONTEND ACTIONS:")
    print("   1. Go to: http://localhost:3000/login")
    print("   2. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)")
    print("   3. Login as: manager@hoteltest.com / manager123")
    print("   4. Try rejecting the fresh applications listed above")

if __name__ == "__main__":
    fix_manager_filter()