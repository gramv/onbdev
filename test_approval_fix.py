#!/usr/bin/env python3

import requests
import json

def test_application_approval():
    """Test the fixed application approval endpoint"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Application Approval Fix")
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
    
    login_data = login_response.json()
    manager_token = login_data["token"]
    print(f"✅ Manager login successful")
    
    # Step 2: Get applications
    print("\n2. 📋 Getting applications...")
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return False
    
    applications = apps_response.json()
    pending_apps = [app for app in applications if app.get("status") == "pending"]
    
    if not pending_apps:
        print("⚠️  No pending applications found")
        return False
    
    application_id = pending_apps[0]["id"]
    print(f"✅ Found pending application: {application_id}")
    
    # Step 3: Test approval with correct form data
    print("\n3. ✅ Testing application approval...")
    
    # Create form data with correct field names
    form_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-02-01",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Mike Wilson",  # Changed from direct_supervisor
        "special_instructions": "Welcome to the team!"
    }
    
    approve_response = requests.post(
        f"{base_url}/applications/{application_id}/approve",
        data=form_data,  # Using data= for form data
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    print(f"Approval response status: {approve_response.status_code}")
    
    if approve_response.status_code == 200:
        print("✅ Application approval successful!")
        response_data = approve_response.json()
        print(f"Employee ID: {response_data.get('employee_id')}")
        print(f"Onboarding URL: {response_data.get('onboarding', {}).get('onboarding_url')}")
        return True
    else:
        print(f"❌ Application approval failed: {approve_response.status_code}")
        print(f"Response: {approve_response.text}")
        return False

if __name__ == "__main__":
    success = test_application_approval()
    if success:
        print("\n🎉 Application approval fix successful!")
    else:
        print("\n💥 Application approval fix failed!")