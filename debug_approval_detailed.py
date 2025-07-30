#!/usr/bin/env python3

import requests
import json

def debug_approval_issue():
    """Debug the approval issue in detail"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Debugging Application Approval Issue")
    print("=" * 50)
    
    # Step 1: Login as manager
    print("\n1. 🔐 Logging in as manager...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    manager_token = login_response.json()["token"]
    print("✅ Manager login successful")
    
    # Step 2: Get the specific application that's failing
    application_id = "f232e624-a201-4bae-8522-3ae523c350fd"
    
    print(f"\n2. 📋 Checking application {application_id}...")
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return False
    
    applications = apps_response.json()
    target_app = None
    
    for app in applications:
        if app.get("id") == application_id:
            target_app = app
            break
    
    if target_app:
        print(f"✅ Found application: {target_app.get('applicant_data', {}).get('first_name')} {target_app.get('applicant_data', {}).get('last_name')}")
        print(f"   Status: {target_app.get('status')}")
        print(f"   Position: {target_app.get('position')}")
        print(f"   Department: {target_app.get('department')}")
    else:
        print(f"❌ Application {application_id} not found")
        print("Available applications:")
        for app in applications:
            print(f"   - {app.get('id')}: {app.get('applicant_data', {}).get('first_name')} {app.get('applicant_data', {}).get('last_name')} ({app.get('status')})")
        return False
    
    # Step 3: Test different form data combinations
    print(f"\n3. 🧪 Testing different form data combinations...")
    
    test_cases = [
        {
            "name": "Complete form data",
            "data": {
                "job_title": "Front Desk Agent",
                "start_date": "2025-02-01",
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
                "start_date": "2025-02-01",
                "start_time": "09:00",
                "pay_rate": "18.50",
                "pay_frequency": "bi-weekly",
                "benefits_eligible": "yes",
                "supervisor": "Mike Wilson"
            }
        },
        {
            "name": "Missing supervisor (should fail)",
            "data": {
                "job_title": "Front Desk Agent",
                "start_date": "2025-02-01",
                "start_time": "09:00",
                "pay_rate": "18.50",
                "pay_frequency": "bi-weekly",
                "benefits_eligible": "yes"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        print(f"   Data: {test_case['data']}")
        
        # Test with form data (like frontend)
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
            break
        else:
            print(f"   ❌ Failed")
            try:
                error_data = approve_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw response: {approve_response.text}")
    
    # Step 4: Check if the application still exists and is pending
    print(f"\n4. 🔄 Checking application status after tests...")
    apps_response2 = requests.get(f"{base_url}/manager/applications", 
                                 headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response2.status_code == 200:
        applications2 = apps_response2.json()
        target_app2 = None
        
        for app in applications2:
            if app.get("id") == application_id:
                target_app2 = app
                break
        
        if target_app2:
            print(f"   Current status: {target_app2.get('status')}")
            if target_app2.get('status') == 'pending':
                print("   ✅ Application is still pending and available for approval")
            else:
                print(f"   ⚠️  Application status changed to: {target_app2.get('status')}")
        else:
            print("   ❌ Application no longer found")
    
    return True

if __name__ == "__main__":
    debug_approval_issue()