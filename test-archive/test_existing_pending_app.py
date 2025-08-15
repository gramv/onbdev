#!/usr/bin/env python3

import requests
import json

def test_existing_pending_application():
    """Test approval with the existing pending application"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Existing Pending Application")
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
    
    # Step 2: Get the pending application
    print("\n2. 📋 Getting pending applications...")
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return False
    
    applications = apps_response.json()
    pending_apps = [app for app in applications if app.get('status') == 'pending']
    
    if not pending_apps:
        print("⚠️  No pending applications found")
        return False
    
    target_app = pending_apps[0]
    app_id = target_app['id']
    
    print(f"✅ Found pending application: {app_id}")
    print(f"   Name: {target_app.get('applicant_data', {}).get('first_name')} {target_app.get('applicant_data', {}).get('last_name')}")
    print(f"   Position: {target_app.get('position')}")
    print(f"   Status: {target_app.get('status')}")
    
    # Step 3: Test approval with exact frontend data format
    print(f"\n3. ✅ Testing approval with frontend-style data...")
    
    # This is exactly what the frontend should be sending
    form_data = {
        "job_title": target_app.get('position', 'Front Desk Agent'),
        "start_date": "2025-08-20",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Mike Wilson",
        "special_instructions": "Approved via frontend test"
    }
    
    print("Form data being sent:")
    for key, value in form_data.items():
        print(f"   {key}: {value}")
    
    approve_response = requests.post(
        f"{base_url}/applications/{app_id}/approve",
        data=form_data,  # Using data= for form data (like frontend FormData)
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
    success = test_existing_pending_application()
    if success:
        print("\n🎉 The approval functionality is working correctly!")
        print("\nThe issue is that the frontend has stale data.")
        print("The user needs to refresh the page or the applications list.")
        print("\nSuggested solutions:")
        print("1. Refresh the browser page")
        print("2. Click on a different tab and back to Applications")
        print("3. Use the search/filter to refresh the data")
    else:
        print("\n💥 There's still an issue with the approval functionality.")