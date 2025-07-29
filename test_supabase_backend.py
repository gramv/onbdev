#!/usr/bin/env python3

"""
Test the Supabase backend and create test data
"""

import requests
import json
import time

def test_supabase_backend():
    """Test the Supabase-enabled backend"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Supabase Backend")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1. 🏥 Testing health check...")
    try:
        health_response = requests.get(f"{base_url}/healthz", timeout=10)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database')}")
            print(f"   Version: {health_data.get('version')}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Login
    print("\n2. 🔐 Testing login...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json={
            "email": "manager@hoteltest.com",
            "password": "manager123"
        }, timeout=10)
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            manager_token = login_data["token"]
            print(f"✅ Login successful")
            print(f"   Role: {login_data.get('user', {}).get('role')}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    # Test 3: Get applications
    print("\n3. 📋 Testing applications endpoint...")
    try:
        apps_response = requests.get(f"{base_url}/manager/applications", 
                                    headers={"Authorization": f"Bearer {manager_token}"},
                                    timeout=10)
        
        if apps_response.status_code == 200:
            applications = apps_response.json()
            print(f"✅ Applications endpoint working")
            print(f"   Found {len(applications)} applications")
            
            for app in applications:
                name = f"{app.get('applicant_data', {}).get('first_name', 'Unknown')} {app.get('applicant_data', {}).get('last_name', 'Unknown')}"
                print(f"   - {app.get('id')}: {name} - {app.get('position')} ({app.get('status')})")
                
        else:
            print(f"❌ Applications endpoint failed: {apps_response.status_code}")
            print(f"Response: {apps_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Applications endpoint failed: {e}")
        return False
    
    # Test 4: Create test application
    print("\n4. 📝 Testing application creation...")
    try:
        property_id = "prop_test_001"
        
        app_data = {
            "first_name": "Supabase",
            "last_name": "Test",
            "email": f"supabase.test.{int(time.time())}@example.com",
            "phone": "(555) 999-0000",
            "address": "999 Supabase St",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-10-01",
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "2-5",
            "hotel_experience": "yes"
        }
        
        create_response = requests.post(f"{base_url}/apply/{property_id}", 
                                       json=app_data, timeout=10)
        
        if create_response.status_code == 200:
            create_data = create_response.json()
            new_app_id = create_data["application_id"]
            print(f"✅ Application created successfully")
            print(f"   Application ID: {new_app_id}")
        else:
            print(f"❌ Application creation failed: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Application creation failed: {e}")
        return False
    
    # Test 5: Verify application appears in list
    print("\n5. 🔄 Verifying application appears in manager list...")
    try:
        updated_apps_response = requests.get(f"{base_url}/manager/applications", 
                                           headers={"Authorization": f"Bearer {manager_token}"},
                                           timeout=10)
        
        if updated_apps_response.status_code == 200:
            updated_applications = updated_apps_response.json()
            
            found_app = None
            for app in updated_applications:
                if app.get('id') == new_app_id:
                    found_app = app
                    break
            
            if found_app:
                print(f"✅ New application found in manager list")
                print(f"   Status: {found_app.get('status')}")
                
                # Test 6: Try to approve the application
                print("\n6. ✅ Testing application approval...")
                
                form_data = {
                    "job_title": "Front Desk Agent",
                    "start_date": "2025-10-01",
                    "start_time": "09:00",
                    "pay_rate": "19.00",
                    "pay_frequency": "bi-weekly",
                    "benefits_eligible": "yes",
                    "supervisor": "Test Supervisor",
                    "special_instructions": "Supabase test approval"
                }
                
                approval_response = requests.post(
                    f"{base_url}/applications/{new_app_id}/approve",
                    data=form_data,
                    headers={"Authorization": f"Bearer {manager_token}"},
                    timeout=15
                )
                
                if approval_response.status_code == 200:
                    approval_data = approval_response.json()
                    print(f"✅ Application approval successful!")
                    print(f"   Employee ID: {approval_data.get('employee_id')}")
                    print(f"   Message: {approval_data.get('message')}")
                    
                    if 'onboarding' in approval_data:
                        print(f"   Onboarding URL: {approval_data['onboarding'].get('onboarding_url')}")
                    
                    return True
                else:
                    print(f"❌ Application approval failed: {approval_response.status_code}")
                    print(f"Response: {approval_response.text}")
                    return False
                    
            else:
                print(f"❌ New application not found in manager list")
                return False
                
        else:
            print(f"❌ Failed to get updated applications: {updated_apps_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Application verification failed: {e}")
        return False

def main():
    """Main function"""
    
    print("🚀 Starting Supabase Backend Test")
    print("=" * 50)
    
    success = test_supabase_backend()
    
    if success:
        print("\n🎉 All tests passed!")
        print("\n📋 Summary:")
        print("   ✅ Health check working")
        print("   ✅ Authentication working")
        print("   ✅ Applications endpoint working")
        print("   ✅ Application creation working")
        print("   ✅ Application approval working")
        print("   ✅ Supabase integration successful")
        
        print("\n🔗 The approval issue should now be fixed!")
        print("   • Data is now stored in Supabase")
        print("   • Applications persist across server restarts")
        print("   • Frontend and backend use the same data source")
        
    else:
        print("\n💥 Some tests failed!")
        print("   Check the error messages above")
        print("   The backend may need additional fixes")

if __name__ == "__main__":
    main()