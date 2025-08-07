#!/usr/bin/env python3

import requests
import json

def test_approval_fix():
    """Simple test of the approval fix"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Application Approval Fix (Simple)")
    print("=" * 50)
    
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
    
    # Step 2: Get existing applications
    print("\n2. 📋 Getting applications...")
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return False
    
    applications = apps_response.json()
    pending_apps = [app for app in applications if app.get("status") == "pending"]
    
    print(f"Found {len(applications)} total applications")
    print(f"Found {len(pending_apps)} pending applications")
    
    if not pending_apps:
        print("⚠️  No pending applications found. Creating one...")
        
        # Create a simple test application
        property_id = "prop_test_001"
        app_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": f"jane.smith.{len(applications)}@test.com",  # Unique email
            "phone": "(555) 987-6543",
            "address": "456 Test Ave",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-02-01",
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "1-2",
            "hotel_experience": "no"
        }
        
        create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
        if create_response.status_code == 200:
            app_id = create_response.json()["application_id"]
            print(f"✅ Created test application: {app_id}")
        else:
            print(f"❌ Failed to create application: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
    else:
        app_id = pending_apps[0]["id"]
        print(f"✅ Using existing pending application: {app_id}")
    
    # Step 3: Test approval with correct form data
    print("\n3. ✅ Testing application approval with fixed form data...")
    
    form_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-02-01",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Mike Wilson",  # Fixed field name
        "special_instructions": "Welcome to the team!"
    }
    
    print("Form data being sent:")
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
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
        
        if 'onboarding' in response_data:
            print(f"✅ Onboarding URL: {response_data['onboarding'].get('onboarding_url')}")
        
        return True
    else:
        print(f"❌ Application approval failed: {approve_response.status_code}")
        try:
            error_data = approve_response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Response text: {approve_response.text}")
        return False

if __name__ == "__main__":
    success = test_approval_fix()
    if success:
        print("\n🎉 Application approval fix is working!")
        print("\n📋 Fix Summary:")
        print("   • Frontend now sends 'supervisor' instead of 'direct_supervisor'")
        print("   • Form validation includes supervisor field")
        print("   • Backend correctly processes the approval request")
        print("   • 422 error should be resolved")
    else:
        print("\n💥 Application approval fix needs more work!")