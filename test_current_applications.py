#!/usr/bin/env python3

import requests
import json

def test_current_applications():
    """Test with current available applications"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Current Applications")
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
    
    manager_token = login_response.json()["token"]
    print("✅ Manager login successful")
    
    # Step 2: Get all applications
    print("\n2. 📋 Getting all applications...")
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return False
    
    applications = apps_response.json()
    print(f"Found {len(applications)} total applications:")
    
    pending_apps = []
    for app in applications:
        status = app.get('status', 'unknown')
        name = f"{app.get('applicant_data', {}).get('first_name', 'Unknown')} {app.get('applicant_data', {}).get('last_name', 'Unknown')}"
        position = app.get('position', 'Unknown')
        print(f"   - {app.get('id')}: {name} - {position} ({status})")
        
        if status == 'pending':
            pending_apps.append(app)
    
    print(f"\nFound {len(pending_apps)} pending applications")
    
    # Step 3: Create a new test application if none are pending
    if not pending_apps:
        print("\n3. 📝 Creating new test application...")
        property_id = "prop_test_001"
        
        app_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": f"test.user.{len(applications)}@example.com",
            "phone": "(555) 123-4567",
            "address": "123 Test St",
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
            "hotel_experience": "yes"
        }
        
        create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
        
        if create_response.status_code == 200:
            new_app_data = create_response.json()
            new_app_id = new_app_data["application_id"]
            print(f"✅ Created new application: {new_app_id}")
            
            # Add to pending apps for testing
            pending_apps.append({"id": new_app_id, "applicant_data": app_data})
        else:
            print(f"❌ Failed to create application: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
    
    # Step 4: Test approval with the first pending application
    if pending_apps:
        test_app = pending_apps[0]
        app_id = test_app["id"]
        
        print(f"\n4. ✅ Testing approval with application: {app_id}")
        
        form_data = {
            "job_title": "Front Desk Agent",
            "start_date": "2025-08-01",
            "start_time": "09:00",
            "pay_rate": "18.50",
            "pay_frequency": "bi-weekly",
            "benefits_eligible": "yes",
            "supervisor": "Mike Wilson",
            "special_instructions": "Welcome to our team!"
        }
        
        print("Form data being sent:")
        for key, value in form_data.items():
            print(f"   {key}: {value}")
        
        approve_response = requests.post(
            f"{base_url}/applications/{app_id}/approve",
            data=form_data,
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        print(f"\nApproval response status: {approve_response.status_code}")
        
        if approve_response.status_code == 200:
            print("✅ Application approval successful!")
            response_data = approve_response.json()
            print(f"✅ Employee ID: {response_data.get('employee_id')}")
            print(f"✅ Message: {response_data.get('message')}")
            return True
        else:
            print(f"❌ Application approval failed: {approve_response.status_code}")
            try:
                error_data = approve_response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response text: {approve_response.text}")
            return False
    else:
        print("❌ No pending applications available for testing")
        return False

if __name__ == "__main__":
    success = test_current_applications()
    if success:
        print("\n🎉 Application approval is working correctly!")
        print("The issue might be that the frontend is trying to approve")
        print("an application that no longer exists or is already processed.")
    else:
        print("\n💥 There's still an issue with application approval.")