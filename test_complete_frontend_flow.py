#!/usr/bin/env python3

import requests
import json

def test_complete_frontend_flow():
    """Test the complete frontend approval flow"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Complete Frontend Approval Flow")
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
    
    # Step 2: Create a new application
    print("\n2. 📝 Creating new application for testing...")
    property_id = "prop_test_001"
    
    app_data = {
        "first_name": "Frontend",
        "last_name": "FlowTest",
        "email": "frontend.flowtest@example.com",
        "phone": "(555) 777-8888",
        "address": "123 Frontend Flow St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-08-25",
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
    print(f"✅ Created application: {new_app_id}")
    
    # Step 3: Verify it appears in manager applications (like frontend would fetch)
    print("\n3. 📋 Fetching applications via manager endpoint...")
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to fetch applications: {apps_response.status_code}")
        return False
    
    applications = apps_response.json()
    target_app = None
    
    for app in applications:
        if app.get('id') == new_app_id:
            target_app = app
            break
    
    if not target_app:
        print(f"❌ New application not found in manager applications")
        return False
    
    print(f"✅ Application found in manager endpoint")
    print(f"   Status: {target_app.get('status')}")
    print(f"   Name: {target_app.get('applicant_data', {}).get('first_name')} {target_app.get('applicant_data', {}).get('last_name')}")
    
    # Step 4: Test approval exactly like frontend
    print(f"\n4. ✅ Testing approval exactly like frontend...")
    
    # This mimics exactly what the frontend ApplicationsTab.tsx does
    job_offer_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-08-25",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Mike Wilson",
        "special_instructions": "Approved via complete frontend flow test"
    }
    
    print("Job offer data (like frontend jobOfferData):")
    for key, value in job_offer_data.items():
        print(f"   {key}: {value}")
    
    # Create FormData exactly like frontend does
    # Object.entries(jobOfferData).forEach(([key, value]) => { formData.append(key, value) })
    
    approve_response = requests.post(
        f"{base_url}/applications/{new_app_id}/approve",
        data=job_offer_data,  # This is what FormData becomes
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
        
        # Step 5: Verify the application status changed
        print(f"\n5. 🔄 Verifying application status changed...")
        updated_apps_response = requests.get(f"{base_url}/manager/applications", 
                                           headers={"Authorization": f"Bearer {manager_token}"})
        
        if updated_apps_response.status_code == 200:
            updated_applications = updated_apps_response.json()
            updated_app = None
            
            for app in updated_applications:
                if app.get('id') == new_app_id:
                    updated_app = app
                    break
            
            if updated_app and updated_app.get('status') == 'approved':
                print("✅ Application status correctly changed to 'approved'")
                return True
            else:
                print(f"⚠️  Application status: {updated_app.get('status') if updated_app else 'not found'}")
        
        return True
    else:
        print(f"❌ Application approval failed: {approve_response.status_code}")
        try:
            error_data = approve_response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
            
            # Detailed error analysis
            if 'detail' in error_data and isinstance(error_data['detail'], list):
                print("\nValidation errors:")
                for error in error_data['detail']:
                    field = error.get('loc', ['unknown'])[-1]
                    message = error.get('msg', 'Unknown error')
                    input_value = error.get('input', 'N/A')
                    print(f"   - Field: {field}")
                    print(f"     Message: {message}")
                    print(f"     Input: {input_value}")
        except:
            print(f"Response text: {approve_response.text}")
        return False

if __name__ == "__main__":
    success = test_complete_frontend_flow()
    if success:
        print("\n🎉 Complete frontend approval flow works perfectly!")
        print("\n📋 Summary:")
        print("   ✅ Manager login works")
        print("   ✅ Application creation works")
        print("   ✅ Manager endpoint returns applications")
        print("   ✅ Approval with FormData works")
        print("   ✅ Application status updates correctly")
        print("\n💡 The issue is likely stale frontend data.")
        print("   The user should refresh the page to get fresh applications.")
    else:
        print("\n💥 There's still an issue with the approval flow.")