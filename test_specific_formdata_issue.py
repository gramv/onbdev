#!/usr/bin/env python3

import requests
import json

def test_formdata_issue():
    """Test the specific FormData issue"""
    
    base_url = "http://127.0.0.1:8000"
    application_id = "5de48b19-1a42-4bc9-8069-48ae94d59953"
    
    print("🔍 Testing FormData Issue")
    print("=" * 40)
    print(f"Application ID: {application_id}")
    
    # Login as manager
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    manager_token = login_response.json()["token"]
    print("✅ Manager login successful")
    
    # Check if this specific application exists
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return
    
    applications = apps_response.json()
    target_app = None
    
    for app in applications:
        if app.get('id') == application_id:
            target_app = app
            break
    
    if not target_app:
        print(f"❌ Application {application_id} not found")
        print("Available applications:")
        for app in applications:
            print(f"   - {app.get('id')}: {app.get('applicant_data', {}).get('first_name')} {app.get('applicant_data', {}).get('last_name')} ({app.get('status')})")
        return
    
    print(f"✅ Found application: {target_app.get('applicant_data', {}).get('first_name')} {target_app.get('applicant_data', {}).get('last_name')}")
    print(f"   Status: {target_app.get('status')}")
    
    # Test with the exact data from the frontend logs
    form_data = {
        "job_title": "Housekeeping Supervisor",
        "start_date": "2025-09-09",
        "start_time": "09:08",
        "pay_rate": "77",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "knk",
        "special_instructions": ""
    }
    
    print("\nTesting with exact frontend data:")
    for key, value in form_data.items():
        print(f"   {key}: '{value}'")
    
    # Test different ways of sending the data
    test_cases = [
        {
            "name": "Form data (like frontend)",
            "method": lambda: requests.post(
                f"{base_url}/applications/{application_id}/approve",
                data=form_data,
                headers={"Authorization": f"Bearer {manager_token}"}
            )
        },
        {
            "name": "Form data with explicit content-type",
            "method": lambda: requests.post(
                f"{base_url}/applications/{application_id}/approve",
                data=form_data,
                headers={
                    "Authorization": f"Bearer {manager_token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
        },
        {
            "name": "JSON data (for comparison)",
            "method": lambda: requests.post(
                f"{base_url}/applications/{application_id}/approve",
                json=form_data,
                headers={"Authorization": f"Bearer {manager_token}"}
            )
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        try:
            response = test_case['method']()
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Success!")
                response_data = response.json()
                print(f"   Employee ID: {response_data.get('employee_id')}")
                return True
            else:
                try:
                    error_data = response.json()
                    if 'detail' in error_data and isinstance(error_data['detail'], list):
                        print("   Validation errors:")
                        for error in error_data['detail']:
                            field = error.get('loc', ['unknown'])[-1]
                            message = error.get('msg', 'Unknown')
                            input_val = error.get('input', 'N/A')
                            print(f"     - {field}: {message} (input: {input_val})")
                    else:
                        print(f"   Error: {error_data.get('detail', 'Unknown')}")
                except:
                    print(f"   Raw response: {response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
    
    return False

def test_backend_form_parsing():
    """Test if the backend is properly parsing form data"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔧 Testing Backend Form Parsing")
    print("=" * 40)
    
    # Login
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    manager_token = login_response.json()["token"]
    
    # Create a fresh application for testing
    property_id = "prop_test_001"
    app_data = {
        "first_name": "FormData",
        "last_name": "ParseTest",
        "email": "formdata.parsetest@example.com",
        "phone": "(555) 444-5555",
        "address": "444 FormData St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-09-15",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "1-2",
        "hotel_experience": "yes"
    }
    
    create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create test application: {create_response.status_code}")
        return
    
    test_app_id = create_response.json()["application_id"]
    print(f"✅ Created test application: {test_app_id}")
    
    # Test form data parsing
    form_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-09-15",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Test Supervisor",
        "special_instructions": "Form parsing test"
    }
    
    print("Testing form data parsing...")
    
    # Try with different approaches
    import urllib.parse
    
    # Method 1: Standard form data
    response1 = requests.post(
        f"{base_url}/applications/{test_app_id}/approve",
        data=form_data,
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    print(f"Method 1 (standard form data): {response1.status_code}")
    
    # Method 2: URL encoded
    encoded_data = urllib.parse.urlencode(form_data)
    response2 = requests.post(
        f"{base_url}/applications/{test_app_id}/approve",
        data=encoded_data,
        headers={
            "Authorization": f"Bearer {manager_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    
    print(f"Method 2 (URL encoded): {response2.status_code}")
    
    # Method 3: Multipart form data (like browser FormData)
    files = {key: (None, value) for key, value in form_data.items()}
    response3 = requests.post(
        f"{base_url}/applications/{test_app_id}/approve",
        files=files,
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    print(f"Method 3 (multipart form data): {response3.status_code}")
    
    # Check which one worked
    for i, response in enumerate([response1, response2, response3], 1):
        if response.status_code == 200:
            print(f"✅ Method {i} worked!")
            return True
        else:
            try:
                error = response.json()
                if 'detail' in error and isinstance(error['detail'], list):
                    print(f"   Method {i} errors:")
                    for err in error['detail'][:3]:  # Show first 3 errors
                        field = err.get('loc', ['unknown'])[-1]
                        input_val = err.get('input')
                        print(f"     - {field}: input = {input_val}")
            except:
                pass
    
    return False

if __name__ == "__main__":
    print("🚀 Starting FormData Issue Debug")
    print("=" * 50)
    
    success1 = test_formdata_issue()
    
    if not success1:
        success2 = test_backend_form_parsing()
        
        if success2:
            print("\n💡 Found the solution! The backend needs multipart form data.")
        else:
            print("\n💥 All form data methods failed.")
    else:
        print("\n🎉 FormData issue resolved!")