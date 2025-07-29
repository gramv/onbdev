#!/usr/bin/env python3

import requests
import json
import time

def test_manager_approval_flow():
    """Test complete manager approval flow with Supabase"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Manager Approval Flow with Supabase")
    print("=" * 60)
    
    # Step 1: Login as manager
    print("\n1️⃣ Logging in as manager...")
    try:
        login_data = {
            "email": "manager@hoteltest.com",
            "password": "manager123"
        }
        
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            auth_result = response.json()
            token = auth_result['token']
            print(f"✅ Manager login successful")
            print(f"   User: {auth_result['user']['first_name']} {auth_result['user']['last_name']}")
            print(f"   Role: {auth_result['user']['role']}")
        else:
            print(f"❌ Manager login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Get manager applications
    print(f"\n2️⃣ Getting manager applications...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/manager/applications", headers=headers)
        
        if response.status_code == 200:
            applications = response.json()
            print(f"✅ Found {len(applications)} applications")
            
            # Find a pending application or create one
            pending_apps = [app for app in applications if app.get('status') == 'pending']
            
            if not pending_apps:
                print("❌ No pending applications found. Creating one...")
                
                # Create a test application first
                test_app = {
                    "first_name": "Manager",
                    "last_name": "ApprovalTest",
                    "email": f"manager.test.{int(time.time())}@example.com",
                    "phone": "5550123456",
                    "address": "123 Test St",
                    "city": "Test City",
                    "state": "CA",
                    "zip_code": "90210",
                    "department": "Front Desk",
                    "position": "Front Desk Agent",
                    "work_authorized": "yes",
                    "sponsorship_required": "no",
                    "start_date": "2025-08-01",
                    "shift_preference": "Day",
                    "employment_type": "full_time",
                    "experience_years": "2",
                    "hotel_experience": "yes",
                    "previous_employer": "Test Hotel",
                    "reason_for_leaving": "Career advancement",
                    "additional_comments": "Test application for approval flow"
                }
                
                create_response = requests.post(f"{base_url}/apply/prop_test_001", json=test_app)
                if create_response.status_code == 200:
                    app_data = create_response.json()
                    print(f"✅ Created test application: {app_data['application_id']}")
                    
                    # Get applications again
                    response = requests.get(f"{base_url}/manager/applications", headers=headers)
                    if response.status_code == 200:
                        applications = response.json()
                        pending_apps = [app for app in applications if app.get('status') == 'pending']
                    else:
                        print(f"❌ Failed to get applications after creation: {response.status_code}")
                        return False
                else:
                    print(f"❌ Failed to create application: {create_response.status_code}")
                    print(f"   Response: {create_response.text}")
                    return False
            
            if pending_apps:
                app_to_approve = pending_apps[0]
                app_id = app_to_approve['id']
                print(f"✅ Using application: {app_id}")
                print(f"   Applicant: {app_to_approve['applicant_data']['first_name']} {app_to_approve['applicant_data']['last_name']}")
            else:
                print("❌ Still no pending applications found")
                return False
                
        else:
            print(f"❌ Failed to get applications: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting applications: {e}")
        return False
    
    # Step 3: Test approval
    print(f"\n3️⃣ Testing approval for application {app_id}...")
    try:
        approval_data = {
            "job_title": "Front Desk Agent",
            "start_date": "2024-02-15",
            "start_time": "9:00 AM",
            "pay_rate": 18.50,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Sarah Manager",
            "special_instructions": "Complete onboarding by start date"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{base_url}/applications/{app_id}/approve", data=approval_data, headers=headers)
        
        print(f"📤 Approval request status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Approval successful!")
            print(f"   Message: {result.get('message')}")
            print(f"   Employee ID: {result.get('employee_id')}")
            print(f"   Onboarding URL: {result.get('onboarding', {}).get('onboarding_url', 'Not provided')}")
            print(f"   Talent Pool Moved: {result.get('talent_pool', {}).get('moved_to_talent_pool', 0)}")
            return True
        else:
            print(f"❌ Approval failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during approval: {e}")
        return False

if __name__ == "__main__":
    success = test_manager_approval_flow()
    if success:
        print("\n🎉 Manager approval flow test PASSED!")
        print("✅ Complete Supabase migration is working correctly!")
    else:
        print("\n❌ Manager approval flow test FAILED")
        print("❌ Need to investigate further")