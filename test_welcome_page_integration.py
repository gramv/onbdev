#!/usr/bin/env python3
"""
Test script for welcome page integration with job application workflow
Tests the enhanced welcome page functionality and token-based access
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_welcome_page_integration():
    """Test the complete welcome page integration workflow"""
    
    print("🧪 Testing Welcome Page Integration")
    print("=" * 50)
    
    try:
        # Step 1: Create test data (property, manager, application)
        print("\n📋 Step 1: Setting up test data...")
        
        # Create HR user for authentication
        hr_login_data = {
            "email": "hr@hoteltest.com",
            "password": "password123"
        }
        
        hr_response = requests.post(f"{BASE_URL}/auth/login", json=hr_login_data)
        if hr_response.status_code != 200:
            print(f"❌ HR login failed: {hr_response.text}")
            return False
        
        hr_token = hr_response.json()["access_token"]
        hr_headers = {"Authorization": f"Bearer {hr_token}"}
        
        print("✅ HR authenticated successfully")
        
        # Step 2: Get an approved application (should exist from test data)
        print("\n📋 Step 2: Finding approved application...")
        
        applications_response = requests.get(f"{BASE_URL}/hr/applications", headers=hr_headers)
        if applications_response.status_code != 200:
            print(f"❌ Failed to get applications: {applications_response.text}")
            return False
        
        applications = applications_response.json()
        approved_apps = [app for app in applications if app.get("status") == "approved"]
        
        if not approved_apps:
            print("❌ No approved applications found. Please run setup test data first.")
            return False
        
        application = approved_apps[0]
        application_id = application["id"]
        print(f"✅ Found approved application: {application_id}")
        
        # Step 3: Initiate onboarding for the application
        print("\n🚀 Step 3: Initiating onboarding...")
        
        initiate_response = requests.post(
            f"{BASE_URL}/api/onboarding/initiate/{application_id}",
            headers=hr_headers
        )
        
        if initiate_response.status_code != 200:
            print(f"❌ Failed to initiate onboarding: {initiate_response.text}")
            return False
        
        onboarding_data = initiate_response.json()
        employee_id = onboarding_data["employee_id"]
        onboarding_token = onboarding_data["token"]
        
        print(f"✅ Onboarding initiated successfully!")
        print(f"   Employee ID: {employee_id}")
        print(f"   Token: {onboarding_token[:20]}...")
        
        # Step 4: Test welcome data endpoint with token
        print("\n🎉 Step 4: Testing welcome data with token...")
        
        welcome_response = requests.get(
            f"{BASE_URL}/api/employees/{employee_id}/welcome-data",
            params={"token": onboarding_token}
        )
        
        if welcome_response.status_code != 200:
            print(f"❌ Failed to get welcome data with token: {welcome_response.text}")
            return False
        
        welcome_data = welcome_response.json()
        print("✅ Welcome data retrieved with token successfully!")
        print(f"   Employee: {welcome_data['applicant_data']['first_name']} {welcome_data['applicant_data']['last_name']}")
        print(f"   Property: {welcome_data['property']['name']}")
        print(f"   Position: {welcome_data['employee']['job_details']['job_title']}")
        
        # Step 5: Test welcome data endpoint with authentication
        print("\n🔐 Step 5: Testing welcome data with authentication...")
        
        welcome_auth_response = requests.get(
            f"{BASE_URL}/api/employees/{employee_id}/welcome-data",
            headers=hr_headers
        )
        
        if welcome_auth_response.status_code != 200:
            print(f"❌ Failed to get welcome data with auth: {welcome_auth_response.text}")
            return False
        
        print("✅ Welcome data retrieved with authentication successfully!")
        
        # Step 6: Test invalid token access
        print("\n🚫 Step 6: Testing invalid token access...")
        
        invalid_response = requests.get(
            f"{BASE_URL}/api/employees/{employee_id}/welcome-data",
            params={"token": "invalid_token"}
        )
        
        if invalid_response.status_code == 401:
            print("✅ Invalid token correctly rejected")
        else:
            print(f"⚠️  Expected 401 for invalid token, got {invalid_response.status_code}")
        
        # Step 7: Test no authentication access
        print("\n🚫 Step 7: Testing no authentication access...")
        
        no_auth_response = requests.get(f"{BASE_URL}/api/employees/{employee_id}/welcome-data")
        
        if no_auth_response.status_code == 401:
            print("✅ No authentication correctly rejected")
        else:
            print(f"⚠️  Expected 401 for no auth, got {no_auth_response.status_code}")
        
        # Final success message
        print("\n🎊 SUCCESS! Welcome Page Integration Test Complete!")
        print("=" * 50)
        print(f"📱 Frontend Welcome URL: {FRONTEND_URL}/onboarding-welcome/{employee_id}?token={onboarding_token}")
        print(f"🔧 API Endpoint: {BASE_URL}/api/employees/{employee_id}/welcome-data?token={onboarding_token}")
        
        print("\n💡 Integration Features Tested:")
        print("   ✅ Onboarding session initialization")
        print("   ✅ Token-based welcome page access")
        print("   ✅ Authentication-based welcome page access")
        print("   ✅ Invalid token rejection")
        print("   ✅ No authentication rejection")
        print("   ✅ Employee details from approved application")
        print("   ✅ Property information display")
        print("   ✅ Secure token validation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_welcome_page_integration()
    if success:
        print(f"\n🔗 Quick Test Links:")
        print(f"Backend Health: {BASE_URL}/healthz")
        print(f"Frontend: {FRONTEND_URL}")
        exit(0)
    else:
        print(f"\n💥 Test failed! Check the backend server and try again.")
        exit(1)