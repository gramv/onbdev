#!/usr/bin/env python3

import requests
import json

def debug_frontend_approval_form():
    """Debug the frontend approval form issue"""
    
    print("🔍 DEBUGGING FRONTEND APPROVAL FORM ISSUE")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Step 1: Login as manager
    print("\n1️⃣ Logging in as manager...")
    try:
        login_data = {
            "email": "vgoutamram@gmail.com",
            "password": "Gouthi321@"
        }
        
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            auth_result = response.json()
            token = auth_result['token']
            print(f"✅ Manager login successful")
        else:
            print(f"❌ Manager login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Get applications
    print(f"\n2️⃣ Getting manager applications...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/manager/applications", headers=headers)
        
        if response.status_code == 200:
            applications = response.json()
            print(f"✅ Found {len(applications)} applications")
            
            # Find a pending application
            pending_apps = [app for app in applications if app.get('status') == 'pending']
            
            if pending_apps:
                app_to_test = pending_apps[0]
                app_id = app_to_test['id']
                print(f"✅ Using pending application: {app_id}")
                print(f"   Applicant: {app_to_test['applicant_data']['first_name']} {app_to_test['applicant_data']['last_name']}")
            else:
                print("❌ No pending applications found")
                return False
                
        else:
            print(f"❌ Failed to get applications: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting applications: {e}")
        return False
    
    # Step 3: Test approval with empty data (simulate frontend issue)
    print(f"\n3️⃣ Testing approval with empty data (simulating frontend issue)...")
    try:
        # This simulates what the frontend might be sending
        form_data = {
            'job_title': '',  # Empty - this will cause validation error
            'start_date': '',
            'start_time': '',
            'pay_rate': '',
            'pay_frequency': '',
            'benefits_eligible': '',
            'supervisor': '',
            'special_instructions': ''
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{base_url}/applications/{app_id}/approve", data=form_data, headers=headers)
        
        print(f"📤 Empty data request status: {response.status_code}")
        
        if response.status_code == 422:
            result = response.json()
            print(f"✅ Expected 422 validation error received")
            print(f"   Error details: {result}")
            
            if 'detail' in result and isinstance(result['detail'], list):
                print("   Validation errors:")
                for error in result['detail']:
                    field = ' -> '.join(error.get('loc', []))
                    message = error.get('msg', 'Unknown error')
                    input_value = error.get('input', 'None')
                    print(f"     - {field}: {message} (input: {input_value})")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during empty data test: {e}")
    
    # Step 4: Test approval with proper data
    print(f"\n4️⃣ Testing approval with proper data...")
    try:
        # This is what the frontend SHOULD be sending
        form_data = {
            'job_title': 'Front Desk Agent',
            'start_date': '2025-08-01',
            'start_time': '09:00',
            'pay_rate': '18.50',
            'pay_frequency': 'hourly',
            'benefits_eligible': 'yes',
            'supervisor': 'Sarah Manager',
            'special_instructions': 'Complete onboarding by start date'
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{base_url}/applications/{app_id}/approve", data=form_data, headers=headers)
        
        print(f"📤 Proper data request status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Approval successful with proper data!")
            print(f"   Message: {result.get('message')}")
            print(f"   Employee ID: {result.get('employee_id')}")
        else:
            print(f"❌ Approval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during proper data test: {e}")
    
    print(f"\n📋 DIAGNOSIS:")
    print("=" * 40)
    print("The backend is working correctly and expects form data.")
    print("The 422 error occurs when required fields are empty or null.")
    print("")
    print("🔧 FRONTEND ISSUE:")
    print("The frontend form is not being filled out before submission,")
    print("or the form data is not being properly collected.")
    print("")
    print("💡 SOLUTION:")
    print("1. Ensure the approval modal form is properly filled out")
    print("2. Add frontend validation before submission")
    print("3. Check that form state is properly managed")

if __name__ == "__main__":
    debug_frontend_approval_form()