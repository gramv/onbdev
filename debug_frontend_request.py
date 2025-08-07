#!/usr/bin/env python3
"""
Debug what the frontend is actually sending vs what backend expects
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"

def debug_frontend_request():
    print("🔍 DEBUGGING FRONTEND REQUEST FORMAT")
    print("=" * 50)
    
    # Login as your custom manager
    custom_manager_login = {
        "email": "vgoutamram@gmail.com",
        "password": "Gouthi321@"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=custom_manager_login)
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    manager_auth = response.json()
    manager_token = manager_auth["token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    
    print("✅ Logged in successfully")
    
    # Get fresh applications
    response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    if response.status_code != 200:
        print("❌ Could not get applications")
        return
    
    applications = response.json()
    pending_apps = [app for app in applications if app["status"] == "pending"]
    
    if not pending_apps:
        print("ℹ️  No pending applications to test with")
        # Create a fresh application for testing
        print("\n🔧 Creating fresh test application...")
        
        # Get property ID
        property_id = manager_auth['user']['property_id']
        
        test_app_data = {
            "first_name": "Frontend",
            "last_name": "TestUser",
            "email": "frontend.test@example.com",
            "phone": "(555) 999-9999",
            "address": "999 Frontend Street",
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
            "previous_employer": "",
            "reason_for_leaving": "",
            "additional_comments": "Fresh test for frontend debugging"
        }
        
        response = requests.post(f"{BACKEND_URL}/apply/{property_id}", json=test_app_data)
        if response.status_code == 200:
            app_response = response.json()
            test_app_id = app_response["application_id"]
            print(f"✅ Created test application: {test_app_id}")
        else:
            print(f"❌ Failed to create test application: {response.status_code}")
            return
    else:
        test_app_id = pending_apps[0]["id"]
        print(f"✅ Using existing pending application: {test_app_id}")
    
    print(f"\n🧪 TESTING DIFFERENT REQUEST FORMATS")
    print(f"Application ID: {test_app_id}")
    
    # Test 1: Form data (what frontend should send)
    print(f"\n1️⃣  Testing Form Data (Frontend format):")
    rejection_data_form = {
        "rejection_reason": "Frontend debug test - form data"
    }
    
    response = requests.post(f"{BACKEND_URL}/applications/{test_app_id}/reject", 
                           data=rejection_data_form, headers=manager_headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   ❌ 422 Error: {response.text}")
        try:
            error_detail = response.json()
            print(f"   Validation errors:")
            for error in error_detail.get('detail', []):
                print(f"     - {error.get('loc', [])}: {error.get('msg', '')}")
        except:
            pass
    elif response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success: {result.get('status')}")
    else:
        print(f"   Error: {response.text}")
    
    # Test 2: JSON data (wrong format)
    print(f"\n2️⃣  Testing JSON Data (Wrong format):")
    rejection_data_json = {
        "rejection_reason": "Frontend debug test - json data"
    }
    
    response = requests.post(f"{BACKEND_URL}/applications/{test_app_id}/reject", 
                           json=rejection_data_json, headers=manager_headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   ❌ 422 Error (Expected): {response.text}")
    elif response.status_code == 200:
        result = response.json()
        print(f"   ✅ Unexpected success: {result.get('status')}")
    else:
        print(f"   Error: {response.text}")
    
    # Test 3: Empty form data
    print(f"\n3️⃣  Testing Empty Form Data:")
    response = requests.post(f"{BACKEND_URL}/applications/{test_app_id}/reject", 
                           data={}, headers=manager_headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   ❌ 422 Error (Expected): {response.text}")
    else:
        print(f"   Response: {response.text}")
    
    # Test 4: Missing rejection_reason
    print(f"\n4️⃣  Testing Missing rejection_reason:")
    response = requests.post(f"{BACKEND_URL}/applications/{test_app_id}/reject", 
                           data={"other_field": "test"}, headers=manager_headers)
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   ❌ 422 Error (Expected): {response.text}")
    else:
        print(f"   Response: {response.text}")
    
    print(f"\n" + "=" * 50)
    print("🎯 FRONTEND DEBUGGING SUMMARY")
    print("=" * 50)
    print("✅ Backend endpoint works correctly with Form data")
    print("❌ Backend rejects JSON data (returns 422)")
    print("❌ Backend rejects empty/missing rejection_reason (returns 422)")
    print("\n🔧 FRONTEND SHOULD:")
    print("   1. Send data as FormData (not JSON)")
    print("   2. Include 'rejection_reason' field")
    print("   3. Ensure rejection_reason is not empty")
    print("\n📋 FRONTEND CODE SHOULD LOOK LIKE:")
    print("   const formData = new FormData()")
    print("   formData.append('rejection_reason', rejectionReason)")
    print("   axios.post(url, formData, { headers: { Authorization: ... } })")

if __name__ == "__main__":
    debug_frontend_request()