#!/usr/bin/env python3
"""
Clear stale application data and refresh the system
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def clear_stale_data():
    print("🧹 CLEARING STALE APPLICATION DATA")
    print("=" * 50)
    
    # Login as HR to see all applications
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
    
    # Get all applications
    print("\n2️⃣  ANALYZE CURRENT APPLICATIONS")
    response = requests.get(f"{BACKEND_URL}/hr/applications", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get applications")
        return False
    
    all_applications = response.json()
    print(f"✅ Found {len(all_applications)} total applications")
    
    # Analyze application statuses
    status_counts = {}
    for app in all_applications:
        status = app.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n📊 Application Status Breakdown:")
    for status, count in status_counts.items():
        print(f"   {status}: {count}")
    
    # Check for the problematic application ID
    problematic_id = "9aa3fcd8-3c53-43e4-88b8-556a97536071"
    problematic_app = None
    for app in all_applications:
        if app['id'] == problematic_id:
            problematic_app = app
            break
    
    if problematic_app:
        print(f"\n🔍 FOUND PROBLEMATIC APPLICATION:")
        print(f"   ID: {problematic_app['id']}")
        print(f"   Status: {problematic_app['status']}")
        print(f"   Applicant: {problematic_app['applicant_data']['first_name']} {problematic_app['applicant_data']['last_name']}")
        print(f"   Property: {problematic_app['property_id']}")
    else:
        print(f"\n❌ PROBLEMATIC APPLICATION NOT FOUND: {problematic_id}")
        print("   This confirms the application doesn't exist in the backend")
    
    # Login as manager to see what they can access
    print("\n3️⃣  MANAGER PERSPECTIVE")
    manager_login = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=manager_login)
    if response.status_code != 200:
        print("❌ Manager login failed")
        return False
    
    manager_auth = response.json()
    manager_token = manager_auth["token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    print("✅ Manager logged in successfully")
    
    # Get manager applications
    response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    if response.status_code != 200:
        print("❌ Could not get manager applications")
        return False
    
    manager_applications = response.json()
    print(f"✅ Manager can see {len(manager_applications)} applications")
    
    # Show current manager applications
    print("\n📋 CURRENT MANAGER APPLICATIONS:")
    for i, app in enumerate(manager_applications, 1):
        status_emoji = "🟡" if app['status'] == 'pending' else "🟢" if app['status'] == 'approved' else "🔵"
        print(f"   {i}. {status_emoji} {app['applicant_data']['first_name']} {app['applicant_data']['last_name']}")
        print(f"      ID: {app['id']}")
        print(f"      Status: {app['status']}")
        print(f"      Position: {app['position']}")
        print()
    
    # Check if problematic app is in manager's list
    manager_has_problematic = any(app['id'] == problematic_id for app in manager_applications)
    if manager_has_problematic:
        print(f"⚠️  Manager can see the problematic application")
    else:
        print(f"✅ Manager cannot see the problematic application (correct)")
    
    # Show pending applications that can be rejected
    pending_apps = [app for app in manager_applications if app['status'] == 'pending']
    print(f"\n🎯 APPLICATIONS READY FOR TESTING:")
    print(f"   Pending applications: {len(pending_apps)}")
    
    if pending_apps:
        print("\n✅ FRESH APPLICATIONS FOR REJECTION TESTING:")
        for i, app in enumerate(pending_apps, 1):
            print(f"   {i}. {app['applicant_data']['first_name']} {app['applicant_data']['last_name']}")
            print(f"      ID: {app['id']}")
            print(f"      Position: {app['position']}")
            print(f"      ✅ Ready for rejection test")
            print()
    else:
        print("❌ No pending applications available for testing")
        print("   Run: python3 fix_frontend_rejection.py to create fresh test data")
    
    # Summary and recommendations
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS SUMMARY")
    print("=" * 50)
    
    if not problematic_app:
        print("✅ The problematic application ID doesn't exist in backend")
        print("❌ Frontend is trying to reject a non-existent application")
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("   1. Clear browser cache and refresh the page")
        print("   2. Logout and login again to refresh application data")
        print("   3. Use the fresh applications created for testing")
        
    if pending_apps:
        print(f"\n✅ {len(pending_apps)} applications are ready for rejection testing")
        print("🔗 Frontend URL: http://localhost:3000/login")
        print("👤 Manager credentials: manager@hoteltest.com / manager123")
    else:
        print("\n⚠️  No pending applications available")
        print("🔧 Run: python3 fix_frontend_rejection.py")
    
    return True

if __name__ == "__main__":
    clear_stale_data()