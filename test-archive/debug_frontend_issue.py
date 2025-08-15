#!/usr/bin/env python3

import requests
import json
import time

def debug_frontend_issue():
    """Debug the frontend issue comprehensively"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Comprehensive Frontend Issue Debug")
    print("=" * 60)
    
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
    user_role = login_data.get('user', {}).get('role')
    
    print(f"✅ Manager login successful")
    print(f"   Token: {manager_token[:20]}...")
    print(f"   Role: {user_role}")
    
    # Step 2: Test both endpoints to see which one frontend should use
    print(f"\n2. 📋 Testing both application endpoints...")
    
    # Test manager endpoint
    print("   Testing /manager/applications...")
    manager_response = requests.get(f"{base_url}/manager/applications", 
                                   headers={"Authorization": f"Bearer {manager_token}"})
    
    print(f"   Manager endpoint status: {manager_response.status_code}")
    
    if manager_response.status_code == 200:
        manager_apps = manager_response.json()
        print(f"   Manager endpoint: {len(manager_apps)} applications")
        for app in manager_apps:
            name = f"{app.get('applicant_data', {}).get('first_name', 'Unknown')} {app.get('applicant_data', {}).get('last_name', 'Unknown')}"
            print(f"     - {app.get('id')}: {name} - {app.get('position')} ({app.get('status')})")
    else:
        print(f"   Manager endpoint failed: {manager_response.text}")
        manager_apps = []
    
    # Test HR endpoint
    print("   Testing /hr/applications...")
    hr_response = requests.get(f"{base_url}/hr/applications", 
                              headers={"Authorization": f"Bearer {manager_token}"})
    
    print(f"   HR endpoint status: {hr_response.status_code}")
    
    if hr_response.status_code == 200:
        hr_apps = hr_response.json()
        print(f"   HR endpoint: {len(hr_apps)} applications")
    elif hr_response.status_code == 403:
        print("   HR endpoint correctly blocked for manager (403)")
    else:
        print(f"   HR endpoint error: {hr_response.text}")
    
    # Step 3: Create a fresh application for testing
    print(f"\n3. 📝 Creating fresh application for frontend testing...")
    property_id = "prop_test_001"
    
    timestamp = int(time.time())
    app_data = {
        "first_name": "Frontend",
        "last_name": f"Debug{timestamp}",
        "email": f"frontend.debug{timestamp}@example.com",
        "phone": "(555) 888-9999",
        "address": "999 Frontend Debug St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-09-01",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes"
    }
    
    create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create application: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False
    
    new_app_id = create_response.json()["application_id"]
    print(f"✅ Created fresh application: {new_app_id}")
    
    # Step 4: Verify it appears in the correct endpoint
    print(f"\n4. 🔄 Verifying application appears in manager endpoint...")
    
    updated_manager_response = requests.get(f"{base_url}/manager/applications", 
                                          headers={"Authorization": f"Bearer {manager_token}"})
    
    if updated_manager_response.status_code == 200:
        updated_apps = updated_manager_response.json()
        new_app = None
        
        for app in updated_apps:
            if app.get('id') == new_app_id:
                new_app = app
                break
        
        if new_app:
            print(f"✅ Application found in manager endpoint")
            print(f"   ID: {new_app.get('id')}")
            print(f"   Status: {new_app.get('status')}")
            print(f"   Name: {new_app.get('applicant_data', {}).get('first_name')} {new_app.get('applicant_data', {}).get('last_name')}")
        else:
            print(f"❌ Application not found in manager endpoint")
            return False
    else:
        print(f"❌ Failed to fetch updated applications: {updated_manager_response.status_code}")
        return False
    
    # Step 5: Test approval with exact frontend format
    print(f"\n5. ✅ Testing approval with exact frontend FormData format...")
    
    # This is exactly what the frontend sends
    job_offer_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-09-01",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Mike Wilson",
        "special_instructions": "Frontend debug test"
    }
    
    print("Job offer data (exactly like frontend):")
    for key, value in job_offer_data.items():
        print(f"   {key}: '{value}'")
    
    # Test the approval
    approve_response = requests.post(
        f"{base_url}/applications/{new_app_id}/approve",
        data=job_offer_data,  # This mimics FormData
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    print(f"\nApproval response status: {approve_response.status_code}")
    
    if approve_response.status_code == 200:
        print("✅ Approval successful!")
        response_data = approve_response.json()
        print(f"   Employee ID: {response_data.get('employee_id')}")
        print(f"   Message: {response_data.get('message')}")
        return True
    else:
        print(f"❌ Approval failed!")
        print(f"   Status: {approve_response.status_code}")
        
        try:
            error_data = approve_response.json()
            print(f"   Error data: {json.dumps(error_data, indent=4)}")
            
            # Detailed error analysis
            if 'detail' in error_data:
                if isinstance(error_data['detail'], list):
                    print("\n   Validation errors:")
                    for error in error_data['detail']:
                        field_path = ' -> '.join(str(x) for x in error.get('loc', []))
                        message = error.get('msg', 'Unknown error')
                        input_value = error.get('input', 'N/A')
                        error_type = error.get('type', 'unknown')
                        
                        print(f"     Field: {field_path}")
                        print(f"     Type: {error_type}")
                        print(f"     Message: {message}")
                        print(f"     Input: {input_value}")
                        print()
                else:
                    print(f"   Detail: {error_data['detail']}")
        except Exception as e:
            print(f"   Raw response: {approve_response.text}")
            print(f"   JSON parse error: {e}")
        
        return False

def test_form_data_variations():
    """Test different FormData variations to find the issue"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("\n🧪 Testing FormData Variations")
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
    
    # Create test application
    property_id = "prop_test_001"
    timestamp = int(time.time())
    
    app_data = {
        "first_name": "FormData",
        "last_name": f"Test{timestamp}",
        "email": f"formdata.test{timestamp}@example.com",
        "phone": "(555) 000-1111",
        "address": "111 FormData Test St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-09-05",
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
    
    # Test different data formats
    test_cases = [
        {
            "name": "String values (like frontend)",
            "data": {
                "job_title": "Front Desk Agent",
                "start_date": "2025-09-05",
                "start_time": "09:00",
                "pay_rate": "18.50",  # String
                "pay_frequency": "bi-weekly",
                "benefits_eligible": "yes",
                "supervisor": "Mike Wilson",
                "special_instructions": "Test case 1"
            }
        },
        {
            "name": "Numeric pay_rate",
            "data": {
                "job_title": "Front Desk Agent",
                "start_date": "2025-09-05",
                "start_time": "09:00",
                "pay_rate": 18.50,  # Number
                "pay_frequency": "bi-weekly",
                "benefits_eligible": "yes",
                "supervisor": "Mike Wilson",
                "special_instructions": "Test case 2"
            }
        },
        {
            "name": "Empty special_instructions",
            "data": {
                "job_title": "Front Desk Agent",
                "start_date": "2025-09-05",
                "start_time": "09:00",
                "pay_rate": "18.50",
                "pay_frequency": "bi-weekly",
                "benefits_eligible": "yes",
                "supervisor": "Mike Wilson",
                "special_instructions": ""  # Empty
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        
        approve_response = requests.post(
            f"{base_url}/applications/{test_app_id}/approve",
            data=test_case['data'],
            headers={"Authorization": f"Bearer {manager_token}"}
        )
        
        print(f"   Status: {approve_response.status_code}")
        
        if approve_response.status_code == 200:
            print("   ✅ Success!")
            break
        else:
            try:
                error_data = approve_response.json()
                if 'detail' in error_data and isinstance(error_data['detail'], list):
                    for error in error_data['detail']:
                        field = error.get('loc', ['unknown'])[-1]
                        message = error.get('msg', 'Unknown')
                        print(f"   ❌ {field}: {message}")
                else:
                    print(f"   ❌ {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   ❌ Raw: {approve_response.text}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Frontend Debug")
    print("=" * 70)
    
    success = debug_frontend_issue()
    
    if not success:
        test_form_data_variations()
    
    if success:
        print("\n🎉 Frontend approval should be working!")
        print("If it's still failing, the issue might be:")
        print("1. Frontend is using stale data")
        print("2. Frontend is not sending the correct token")
        print("3. Frontend is using the wrong endpoint")
    else:
        print("\n💥 There's still an issue with the approval process")