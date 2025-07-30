#!/usr/bin/env python3

import requests
import json

def investigate_data_storage():
    """Investigate what's happening with data storage"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Investigating Data Storage Issue")
    print("=" * 50)
    
    # Step 1: Login as manager
    print("\n1. 🔐 Logging in as manager...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    manager_token = login_response.json()["token"]
    print("✅ Manager login successful")
    
    # Step 2: Create an application via the public endpoint
    print("\n2. 📝 Creating application via public endpoint...")
    property_id = "prop_test_001"
    
    app_data = {
        "first_name": "Storage",
        "last_name": "Investigation",
        "email": "storage.investigation@example.com",
        "phone": "(555) 111-2222",
        "address": "111 Storage St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-09-20",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "1-2",
        "hotel_experience": "yes"
    }
    
    create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create application: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return
    
    new_app_id = create_response.json()["application_id"]
    print(f"✅ Created application: {new_app_id}")
    
    # Step 3: Check if it appears in manager applications immediately
    print("\n3. 📋 Checking if application appears in manager endpoint...")
    
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return
    
    applications = apps_response.json()
    found_app = None
    
    for app in applications:
        if app.get('id') == new_app_id:
            found_app = app
            break
    
    if found_app:
        print(f"✅ Application found in manager endpoint")
        print(f"   Status: {found_app.get('status')}")
        print(f"   Property ID: {found_app.get('property_id')}")
    else:
        print(f"❌ Application NOT found in manager endpoint")
        print(f"Available applications:")
        for app in applications:
            print(f"   - {app.get('id')}: {app.get('applicant_data', {}).get('first_name')} {app.get('applicant_data', {}).get('last_name')} ({app.get('status')})")
        return
    
    # Step 4: Try to approve it immediately
    print(f"\n4. ✅ Trying to approve the application immediately...")
    
    form_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-09-20",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Test Supervisor",
        "special_instructions": "Storage investigation test"
    }
    
    approve_response = requests.post(
        f"{base_url}/applications/{new_app_id}/approve",
        data=form_data,
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    print(f"Approval status: {approve_response.status_code}")
    
    if approve_response.status_code == 200:
        print("✅ Approval successful!")
        response_data = approve_response.json()
        print(f"   Employee ID: {response_data.get('employee_id')}")
        
        # Step 5: Check if the application status changed
        print(f"\n5. 🔄 Checking if application status changed...")
        
        updated_apps_response = requests.get(f"{base_url}/manager/applications", 
                                           headers={"Authorization": f"Bearer {manager_token}"})
        
        if updated_apps_response.status_code == 200:
            updated_applications = updated_apps_response.json()
            updated_app = None
            
            for app in updated_applications:
                if app.get('id') == new_app_id:
                    updated_app = app
                    break
            
            if updated_app:
                print(f"✅ Application status: {updated_app.get('status')}")
                if updated_app.get('status') == 'approved':
                    print("✅ Status correctly updated to approved")
                else:
                    print(f"⚠️  Status is still: {updated_app.get('status')}")
            else:
                print("❌ Application disappeared after approval")
        
        return True
    else:
        print("❌ Approval failed!")
        try:
            error_data = approve_response.json()
            print(f"Error: {json.dumps(error_data, indent=2)}")
            
            if 'detail' in error_data and isinstance(error_data['detail'], list):
                print("\nValidation errors:")
                for error in error_data['detail']:
                    field = error.get('loc', ['unknown'])[-1]
                    message = error.get('msg', 'Unknown')
                    input_val = error.get('input', 'N/A')
                    print(f"   - {field}: {message} (input: {input_val})")
        except:
            print(f"Raw response: {approve_response.text}")
        
        return False

def test_data_persistence():
    """Test if data persists across requests"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔄 Testing Data Persistence")
    print("=" * 30)
    
    # Login
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    manager_token = login_response.json()["token"]
    
    # Get applications count before
    apps_response1 = requests.get(f"{base_url}/manager/applications", 
                                 headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response1.status_code != 200:
        print("❌ Failed to get applications")
        return
    
    apps_before = apps_response1.json()
    print(f"Applications before: {len(apps_before)}")
    
    # Create an application
    property_id = "prop_test_001"
    app_data = {
        "first_name": "Persistence",
        "last_name": "Test",
        "email": "persistence.test@example.com",
        "phone": "(555) 333-4444",
        "address": "333 Persistence St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-09-25",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "1-2",
        "hotel_experience": "yes"
    }
    
    create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create application: {create_response.status_code}")
        return
    
    new_app_id = create_response.json()["application_id"]
    print(f"✅ Created application: {new_app_id}")
    
    # Get applications count after
    apps_response2 = requests.get(f"{base_url}/manager/applications", 
                                 headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response2.status_code != 200:
        print("❌ Failed to get applications after creation")
        return
    
    apps_after = apps_response2.json()
    print(f"Applications after: {len(apps_after)}")
    
    if len(apps_after) > len(apps_before):
        print("✅ Application persisted in memory")
        
        # Find the new application
        new_app = None
        for app in apps_after:
            if app.get('id') == new_app_id:
                new_app = app
                break
        
        if new_app:
            print(f"✅ New application found with status: {new_app.get('status')}")
            return True
        else:
            print("❌ New application not found in list")
            return False
    else:
        print("❌ Application did not persist")
        return False

if __name__ == "__main__":
    print("🚀 Starting Data Storage Investigation")
    print("=" * 60)
    
    success1 = investigate_data_storage()
    success2 = test_data_persistence()
    
    print(f"\n📊 Results:")
    print(f"   Storage investigation: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Data persistence: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n💡 Data storage appears to be working correctly with in-memory database")
        print("The issue might be elsewhere - possibly FormData handling or CORS")
    else:
        print("\n⚠️  There might be a data storage issue")
        print("Check if the backend is using mixed storage (some in-memory, some Supabase)")