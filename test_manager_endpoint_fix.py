#!/usr/bin/env python3

import requests
import json

def test_manager_endpoint():
    """Test the manager applications endpoint"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Manager Endpoint Fix")
    print("=" * 40)
    
    # Step 1: Login as manager
    print("\n1. 🔐 Logging in as manager...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    login_data = login_response.json()
    manager_token = login_data["token"]
    print(f"✅ Manager login successful")
    print(f"   User role: {login_data.get('user', {}).get('role')}")
    
    # Step 2: Test manager applications endpoint
    print("\n2. 📋 Testing manager applications endpoint...")
    manager_apps_response = requests.get(f"{base_url}/manager/applications", 
                                        headers={"Authorization": f"Bearer {manager_token}"})
    
    print(f"Manager endpoint status: {manager_apps_response.status_code}")
    
    if manager_apps_response.status_code == 200:
        manager_apps = manager_apps_response.json()
        print(f"✅ Manager endpoint works - found {len(manager_apps)} applications")
        
        for app in manager_apps:
            name = f"{app.get('applicant_data', {}).get('first_name', 'Unknown')} {app.get('applicant_data', {}).get('last_name', 'Unknown')}"
            print(f"   - {app.get('id')}: {name} - {app.get('position')} ({app.get('status')})")
    else:
        print(f"❌ Manager endpoint failed: {manager_apps_response.status_code}")
        print(f"Response: {manager_apps_response.text}")
        return False
    
    # Step 3: Test HR applications endpoint for comparison
    print("\n3. 📋 Testing HR applications endpoint...")
    hr_apps_response = requests.get(f"{base_url}/hr/applications", 
                                   headers={"Authorization": f"Bearer {manager_token}"})
    
    print(f"HR endpoint status: {hr_apps_response.status_code}")
    
    if hr_apps_response.status_code == 200:
        hr_apps = hr_apps_response.json()
        print(f"✅ HR endpoint accessible - found {len(hr_apps)} applications")
    elif hr_apps_response.status_code == 403:
        print("✅ HR endpoint correctly blocked for manager (403 Forbidden)")
    else:
        print(f"⚠️  HR endpoint returned: {hr_apps_response.status_code}")
    
    # Step 4: Create a new application for testing
    print("\n4. 📝 Creating new test application...")
    property_id = "prop_test_001"
    
    app_data = {
        "first_name": "Frontend",
        "last_name": "Test",
        "email": f"frontend.test.{len(manager_apps)}@example.com",
        "phone": "(555) 999-8888",
        "address": "456 Frontend St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-08-15",
        "shift_preference": "evening",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes"
    }
    
    create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
    
    if create_response.status_code == 200:
        new_app_data = create_response.json()
        new_app_id = new_app_data["application_id"]
        print(f"✅ Created new application: {new_app_id}")
        
        # Step 5: Verify it appears in manager endpoint
        print("\n5. 🔄 Verifying new application appears in manager endpoint...")
        updated_apps_response = requests.get(f"{base_url}/manager/applications", 
                                           headers={"Authorization": f"Bearer {manager_token}"})
        
        if updated_apps_response.status_code == 200:
            updated_apps = updated_apps_response.json()
            new_app_found = any(app.get('id') == new_app_id for app in updated_apps)
            
            if new_app_found:
                print(f"✅ New application found in manager endpoint")
                return True
            else:
                print(f"❌ New application not found in manager endpoint")
                return False
        else:
            print(f"❌ Failed to fetch updated applications: {updated_apps_response.status_code}")
            return False
    else:
        print(f"❌ Failed to create application: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False

if __name__ == "__main__":
    success = test_manager_endpoint()
    if success:
        print("\n🎉 Manager endpoint fix is working!")
        print("Frontend should now correctly fetch applications for managers.")
    else:
        print("\n💥 Manager endpoint fix needs more work.")