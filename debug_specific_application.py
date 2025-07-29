#!/usr/bin/env python3

import requests
import json

def debug_specific_application():
    """Debug the specific application that's failing"""
    
    base_url = "http://127.0.0.1:8000"
    application_id = "5de48b19-1a42-4bc9-8069-48ae94d59953"
    
    print("🔍 Debugging Specific Application")
    print("=" * 50)
    print(f"Application ID: {application_id}")
    
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
    
    # Step 2: Check if application exists in manager applications
    print(f"\n2. 📋 Checking if application exists in manager applications...")
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return False
    
    applications = apps_response.json()
    target_app = None
    
    print(f"Found {len(applications)} total applications:")
    for app in applications:
        name = f"{app.get('applicant_data', {}).get('first_name', 'Unknown')} {app.get('applicant_data', {}).get('last_name', 'Unknown')}"
        status = app.get('status', 'unknown')
        print(f"   - {app.get('id')}: {name} - {app.get('position')} ({status})")
        
        if app.get('id') == application_id:
            target_app = app
    
    if not target_app:
        print(f"❌ Application {application_id} not found in manager applications")
        return False
    
    print(f"✅ Found target application:")
    print(f"   Name: {target_app.get('applicant_data', {}).get('first_name')} {target_app.get('applicant_data', {}).get('last_name')}")
    print(f"   Status: {target_app.get('status')}")
    print(f"   Position: {target_app.get('position')}")
    print(f"   Department: {target_app.get('department')}")
    
    # Step 3: Test approval with detailed debugging
    print(f"\n3. 🧪 Testing approval with detailed debugging...")
    
    if target_app.get('status') != 'pending':
        print(f"⚠️  Application status is '{target_app.get('status')}', not 'pending'")
        print("This might be why the approval is failing")
        return False
    
    # Test different form data scenarios
    test_cases = [
        {
            "name": "Complete form data (like frontend)",
            "data": {
                "job_title": "Front Desk Agent",
                "start_date": "2025-08-15",
                "start_time": "09:00",
                "pay_rate": "18.50",
                "pay_frequency": "bi-weekly",
                "benefits_eligible": "yes",
                "supervisor": "Mike Wilson",
                "special_instructions": "Welcome to the team!"
            }
        },
        {
            "name": "Minimal required data",
            "data": {
                "job_title": "Front Desk Agent",
                "start_date": "2025-08-15",
                "start_time": "09:00",
                "pay_rate": "18.50",
                "pay_frequency": "bi-weekly",
                "benefits_eligible": "yes",
                "supervisor": "Mike Wilson"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        
        # Create FormData-like request
        approve_response = requests.post(
            f"{base_url}/applications/{application_id}/approve",
            data=test_case['data'],
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        print(f"   Status: {approve_response.status_code}")
        
        if approve_response.status_code == 200:
            print("   ✅ Success!")
            response_data = approve_response.json()
            print(f"   Employee ID: {response_data.get('employee_id')}")
            return True
        else:
            print(f"   ❌ Failed")
            try:
                error_data = approve_response.json()
                print(f"   Error: {json.dumps(error_data, indent=6)}")
                
                # Check for specific validation errors
                if 'detail' in error_data:
                    if isinstance(error_data['detail'], list):
                        print("   Validation errors:")
                        for error in error_data['detail']:
                            field = error.get('loc', ['unknown'])[-1]
                            message = error.get('msg', 'Unknown error')
                            print(f"     - {field}: {message}")
                    else:
                        print(f"   Detail: {error_data['detail']}")
            except:
                print(f"   Raw response: {approve_response.text}")
    
    return False

def test_backend_endpoint_directly():
    """Test the backend endpoint directly to see what's expected"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔧 Testing Backend Endpoint Directly")
    print("=" * 40)
    
    # Login as manager
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    manager_token = login_response.json()["token"]
    
    # Create a fresh application for testing
    print("Creating fresh application for testing...")
    property_id = "prop_test_001"
    
    app_data = {
        "first_name": "Debug",
        "last_name": "Test",
        "email": "debug.test@example.com",
        "phone": "(555) 111-2222",
        "address": "789 Debug St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-08-20",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "1-2",
        "hotel_experience": "yes"
    }
    
    create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create test application: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return
    
    new_app_id = create_response.json()["application_id"]
    print(f"✅ Created test application: {new_app_id}")
    
    # Test approval
    form_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-08-20",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Mike Wilson",
        "special_instructions": "Debug test"
    }
    
    print("Testing approval with fresh application...")
    approve_response = requests.post(
        f"{base_url}/applications/{new_app_id}/approve",
        data=form_data,
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    print(f"Approval status: {approve_response.status_code}")
    
    if approve_response.status_code == 200:
        print("✅ Fresh application approval works!")
        return True
    else:
        print("❌ Fresh application approval failed")
        try:
            error_data = approve_response.json()
            print(f"Error: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw response: {approve_response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Specific Application Debug")
    print("=" * 60)
    
    success1 = debug_specific_application()
    success2 = test_backend_endpoint_directly()
    
    if success1 or success2:
        print("\n🎉 At least one test passed - the backend is working")
        print("The issue might be with the specific application or frontend data")
    else:
        print("\n💥 Both tests failed - there's a deeper issue")