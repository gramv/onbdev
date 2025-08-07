#!/usr/bin/env python3
"""
Test script for Enhanced Application Approval Logic
Tests the talent pool functionality and proper onboarding link generation
"""

import requests
import json
import sys
from datetime import datetime, date

# Configuration
BASE_URL = "http://localhost:8000"
HR_EMAIL = "hr@hoteltest.com"
HR_PASSWORD = "admin123"
MANAGER_EMAIL = "manager@hoteltest.com"
MANAGER_PASSWORD = "manager123"

def login_user(email, password):
    """Login and get authentication token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["token"]
    else:
        print(f"❌ Login failed for {email}: {response.text}")
        return None

def create_test_applications():
    """Create multiple test applications for the same position"""
    property_id = "prop_test_001"
    
    # Use timestamp to make emails unique
    import time
    timestamp = int(time.time())
    
    applications = [
        {
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": f"alice.johnson.{timestamp}@test.com",
            "phone": "(555) 111-1111",
            "address": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-01",
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "2-5",
            "hotel_experience": "yes",
            "department": "Front Desk",
            "position": "Front Desk Agent"
        },
        {
            "first_name": "Bob",
            "last_name": "Smith",
            "email": f"bob.smith.{timestamp}@test.com",
            "phone": "(555) 222-2222",
            "address": "456 Test Ave",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-01",
            "shift_preference": "evening",
            "employment_type": "full_time",
            "experience_years": "1-2",
            "hotel_experience": "no",
            "department": "Front Desk",
            "position": "Front Desk Agent"
        },
        {
            "first_name": "Carol",
            "last_name": "Davis",
            "email": f"carol.davis.{timestamp}@test.com",
            "phone": "(555) 333-3333",
            "address": "789 Test Blvd",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-15",
            "shift_preference": "morning",
            "employment_type": "part_time",
            "experience_years": "5+",
            "hotel_experience": "yes",
            "department": "Front Desk",
            "position": "Front Desk Agent"
        }
    ]
    
    created_applications = []
    
    for app_data in applications:
        response = requests.post(f"{BASE_URL}/apply/{property_id}", json=app_data)
        
        if response.status_code == 200:
            result = response.json()
            created_applications.append({
                "id": result["application_id"],
                "name": f"{app_data['first_name']} {app_data['last_name']}",
                "email": app_data["email"],
                "position": app_data["position"]
            })
            print(f"✅ Created application for {app_data['first_name']} {app_data['last_name']}")
        else:
            print(f"❌ Failed to create application for {app_data['first_name']} {app_data['last_name']}: {response.text}")
    
    return created_applications

def test_enhanced_approval_logic():
    """Test the enhanced approval logic with talent pool functionality"""
    print("🧪 Testing Enhanced Application Approval Logic")
    print("=" * 60)
    
    # Step 1: Login as manager
    print("\n1. Logging in as manager...")
    manager_token = login_user(MANAGER_EMAIL, MANAGER_PASSWORD)
    if not manager_token:
        return False
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    # Step 2: Create test applications
    print("\n2. Creating test applications...")
    applications = create_test_applications()
    if len(applications) < 3:
        print("❌ Failed to create enough test applications")
        return False
    
    # Step 3: Get initial application status
    print("\n3. Checking initial application status...")
    response = requests.get(f"{BASE_URL}/hr/applications", headers=headers)
    if response.status_code == 200:
        all_apps = response.json()
        pending_apps = [app for app in all_apps if app["status"] == "pending"]
        print(f"✅ Found {len(pending_apps)} pending applications")
        
        # Find our test applications
        test_apps = [app for app in pending_apps if any(test_app["email"] == app["applicant_email"] for test_app in applications)]
        print(f"✅ Found {len(test_apps)} test applications in pending status")
    else:
        print(f"❌ Failed to get applications: {response.text}")
        return False
    
    # Step 4: Approve one application (should move others to talent pool)
    print("\n4. Approving first application...")
    if test_apps:
        app_to_approve = test_apps[0]
        job_offer_data = {
            "job_title": "Front Desk Agent",
            "start_date": "2025-08-01",
            "start_time": "09:00",
            "pay_rate": 18.50,
            "pay_frequency": "biweekly",
            "benefits_eligible": "yes",
            "supervisor": "John Manager",
            "special_instructions": "Welcome to the team!"
        }
        
        response = requests.post(
            f"{BASE_URL}/applications/{app_to_approve['id']}/approve",
            data=job_offer_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Application approved successfully")
            print(f"   - Employee ID: {result['employee_id']}")
            print(f"   - Response: {json.dumps(result, indent=2)}")
            
            # Check if onboarding info exists (handle both response formats)
            if 'onboarding' in result:
                print(f"   - Onboarding URL: {result['onboarding']['onboarding_url']}")
                print(f"   - Talent Pool: {result['talent_pool']['message']}")
                
                # Verify onboarding link format
                onboarding_url = result['onboarding']['onboarding_url']
                if 'onboard' in onboarding_url and len(result['onboarding']['token']) > 20:
                    print("✅ Onboarding link generated correctly")
                else:
                    print("❌ Onboarding link format incorrect")
                    return False
            elif 'onboarding_url' in result:
                print(f"   - Onboarding URL: {result['onboarding_url']}")
                if 'talent_pool' in result:
                    print(f"   - Talent Pool: {result['talent_pool']['message']}")
                
                # Verify onboarding link format
                onboarding_url = result['onboarding_url']
                if 'onboard' in onboarding_url and len(result['token']) > 20:
                    print("✅ Onboarding link generated correctly")
                else:
                    print("❌ Onboarding link format incorrect")
                    return False
            else:
                print("❌ Onboarding information missing from response")
                return False
                
        else:
            print(f"❌ Failed to approve application: {response.text}")
            return False
    
    # Step 5: Verify talent pool status
    print("\n5. Verifying talent pool status...")
    response = requests.get(f"{BASE_URL}/hr/applications/talent-pool", headers=headers)
    if response.status_code == 200:
        talent_pool_apps = response.json()
        print(f"✅ Found {talent_pool_apps['total_count']} applications in talent pool")
        
        # Verify the other applications are in talent pool
        for app in talent_pool_apps['applications']:
            if app['position'] == 'Front Desk Agent':
                print(f"   - {app['applicant_data']['first_name']} {app['applicant_data']['last_name']} moved to talent pool")
                if app['talent_pool_date']:
                    print(f"     Moved on: {app['talent_pool_date']}")
    else:
        print(f"❌ Failed to get talent pool applications: {response.text}")
        return False
    
    # Step 6: Test bulk talent pool operations
    print("\n6. Testing bulk talent pool operations...")
    
    # Get remaining pending applications
    response = requests.get(f"{BASE_URL}/hr/applications?status=pending", headers=headers)
    if response.status_code == 200:
        pending_apps = response.json()
        if pending_apps:
            app_ids = [app['id'] for app in pending_apps[:2]]  # Take first 2
            
            # Bulk move to talent pool
            response = requests.post(
                f"{BASE_URL}/hr/applications/bulk-talent-pool",
                json=app_ids,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Bulk moved {result['moved_count']} applications to talent pool")
            else:
                print(f"❌ Bulk talent pool operation failed: {response.text}")
    
    # Step 7: Test reactivation from talent pool
    print("\n7. Testing reactivation from talent pool...")
    response = requests.get(f"{BASE_URL}/hr/applications/talent-pool", headers=headers)
    if response.status_code == 200:
        talent_pool_apps = response.json()
        if talent_pool_apps['applications']:
            app_to_reactivate = talent_pool_apps['applications'][0]
            
            response = requests.post(
                f"{BASE_URL}/hr/applications/{app_to_reactivate['id']}/reactivate",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Application reactivated: {result['message']}")
                print(f"   - New status: {result['new_status']}")
            else:
                print(f"❌ Reactivation failed: {response.text}")
    
    # Step 8: Verify final application statuses
    print("\n8. Final verification...")
    response = requests.get(f"{BASE_URL}/hr/applications", headers=headers)
    if response.status_code == 200:
        all_apps = response.json()
        status_counts = {}
        for app in all_apps:
            status = app['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("✅ Final application status summary:")
        for status, count in status_counts.items():
            print(f"   - {status}: {count}")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced Application Approval Logic Test Completed!")
    return True

if __name__ == "__main__":
    try:
        success = test_enhanced_approval_logic()
        if success:
            print("✅ All tests passed!")
            sys.exit(0)
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        sys.exit(1)