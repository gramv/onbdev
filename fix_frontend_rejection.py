#!/usr/bin/env python3
"""
Fix frontend rejection issues by creating fresh test data
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def create_fresh_test_data():
    print("🔧 FIXING FRONTEND REJECTION ISSUES")
    print("=" * 50)
    
    # Login as HR to create fresh test data
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
    
    # Get existing property
    print("\n2️⃣  GET PROPERTY")
    response = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get properties")
        return False
    
    properties = response.json()
    if not properties:
        print("❌ No properties found")
        return False
    
    property_id = properties[0]["id"]
    property_name = properties[0]["name"]
    print(f"✅ Using property: {property_name}")
    
    # Create multiple fresh applications for testing
    print("\n3️⃣  CREATE FRESH TEST APPLICATIONS")
    
    test_applications = [
        {
            "first_name": "Alice",
            "last_name": "TestReject1",
            "email": "alice.testreject1@example.com",
            "phone": "(555) 111-1111",
            "address": "111 Test Street",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-01",
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "1-2",
            "hotel_experience": "yes",
            "previous_employer": "Previous Hotel",
            "reason_for_leaving": "Career growth",
            "additional_comments": "Fresh test application for rejection testing"
        },
        {
            "first_name": "Bob",
            "last_name": "TestReject2",
            "email": "bob.testreject2@example.com",
            "phone": "(555) 222-2222",
            "address": "222 Test Avenue",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "department": "Housekeeping",
            "position": "Housekeeper",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-01",
            "shift_preference": "afternoon",
            "employment_type": "full_time",
            "experience_years": "0-1",
            "hotel_experience": "no",
            "previous_employer": "",
            "reason_for_leaving": "",
            "additional_comments": "Another fresh test application"
        },
        {
            "first_name": "Carol",
            "last_name": "TestReject3",
            "email": "carol.testreject3@example.com",
            "phone": "(555) 333-3333",
            "address": "333 Test Boulevard",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "department": "Food & Beverage",
            "position": "Server",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-01",
            "shift_preference": "evening",
            "employment_type": "part_time",
            "experience_years": "2-5",
            "hotel_experience": "yes",
            "previous_employer": "Restaurant Chain",
            "reason_for_leaving": "Better opportunity",
            "additional_comments": "Third fresh test application"
        }
    ]
    
    created_apps = []
    for i, app_data in enumerate(test_applications, 1):
        print(f"   Creating application {i}/3: {app_data['first_name']} {app_data['last_name']}")
        
        response = requests.post(f"{BACKEND_URL}/apply/{property_id}", json=app_data)
        if response.status_code == 200:
            app_response = response.json()
            created_apps.append({
                "id": app_response["application_id"],
                "name": f"{app_data['first_name']} {app_data['last_name']}",
                "position": app_data["position"]
            })
            print(f"   ✅ Created: {app_response['application_id']}")
        else:
            print(f"   ❌ Failed to create application: {response.status_code}")
    
    print(f"\n✅ Created {len(created_apps)} fresh applications")
    
    # Login as manager and verify applications are visible
    print("\n4️⃣  VERIFY MANAGER CAN SEE APPLICATIONS")
    
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
    
    manager_apps = response.json()
    pending_apps = [app for app in manager_apps if app["status"] == "pending"]
    
    print(f"✅ Manager can see {len(manager_apps)} total applications")
    print(f"✅ {len(pending_apps)} applications are pending (rejectable)")
    
    # Test rejection on one of the fresh applications
    if pending_apps:
        print("\n5️⃣  TEST REJECTION ON FRESH APPLICATION")
        
        test_app = pending_apps[0]
        print(f"   Testing rejection on: {test_app['applicant_data']['first_name']} {test_app['applicant_data']['last_name']}")
        print(f"   Application ID: {test_app['id']}")
        
        rejection_data = {
            "rejection_reason": "Testing rejection workflow - moving to talent pool"
        }
        
        response = requests.post(f"{BACKEND_URL}/applications/{test_app['id']}/reject", 
                               data=rejection_data, headers=manager_headers)
        
        print(f"   Rejection Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Rejection successful: {result.get('status', 'unknown')}")
            print(f"   Message: {result.get('message', '')}")
        else:
            print(f"   ❌ Rejection failed: {response.text}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 FRESH TEST DATA SUMMARY")
    print("=" * 50)
    print(f"✅ Property: {property_name} ({property_id})")
    print(f"✅ Created Applications: {len(created_apps)}")
    for app in created_apps:
        print(f"   - {app['name']} ({app['position']}) - ID: {app['id']}")
    print(f"✅ Pending Applications: {len(pending_apps)}")
    print("\n🔗 Frontend can now test rejection with these fresh applications!")
    print("   Go to: http://localhost:3000/login")
    print("   Login as: manager@hoteltest.com / manager123")
    print("   Navigate to Applications tab and try rejecting the new applications")
    
    return True

if __name__ == "__main__":
    create_fresh_test_data()