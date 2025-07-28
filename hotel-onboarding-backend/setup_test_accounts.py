#!/usr/bin/env python3
"""
Setup script to create dummy HR and manager accounts for testing
Run this after starting the backend server to populate test data
"""

import requests
import json
from datetime import datetime

# Backend URL
BASE_URL = "http://localhost:8000"

def create_hr_account():
    """Create HR account using the secret endpoint"""
    print("Creating HR account...")
    
    response = requests.post(f"{BASE_URL}/secret/create-hr", params={
        "email": "hr@hoteltest.com",
        "password": "password123",
        "secret_key": "hotel-admin-2025"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ HR account created: {data['user']['email']}")
        print(f"   User ID: {data['user']['id']}")
        return data['user']
    else:
        print(f"❌ Failed to create HR account: {response.text}")
        return None

def login_as_hr():
    """Login as HR to get token"""
    print("\nLogging in as HR...")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "hr@hoteltest.com",
        "password": "password123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ HR login successful")
        return data['token']
    else:
        print(f"❌ HR login failed: {response.text}")
        return None

def create_property(hr_token):
    """Create a test property"""
    print("\nCreating test property...")
    
    headers = {"Authorization": f"Bearer {hr_token}"}
    data = {
        "name": "Grand Plaza Hotel",
        "address": "123 Main Street",
        "city": "Downtown",
        "state": "CA",
        "zip_code": "90210",
        "phone": "(555) 123-4567"
    }
    
    response = requests.post(f"{BASE_URL}/hr/properties", data=data, headers=headers)
    
    if response.status_code == 200:
        property_data = response.json()
        print(f"✅ Property created: {property_data['name']}")
        print(f"   Property ID: {property_data['id']}")
        print(f"   QR Code URL: {property_data['qr_code_url']}")
        return property_data
    else:
        print(f"❌ Failed to create property: {response.text}")
        return None

def create_manager_account():
    """Create manager account by logging in"""
    print("\nCreating manager account...")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "password123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Manager account created: {data['user']['email']}")
        print(f"   User ID: {data['user']['id']}")
        print(f"   Token: {data['token']}")
        return data['user'], data['token']
    else:
        print(f"❌ Failed to create manager account: {response.text}")
        return None, None

def assign_manager_to_property(hr_token, property_id, manager_email):
    """Assign manager to property"""
    print(f"\nAssigning manager to property...")
    
    headers = {"Authorization": f"Bearer {hr_token}"}
    data = {"manager_email": manager_email}
    
    response = requests.post(
        f"{BASE_URL}/properties/{property_id}/managers", 
        json=data, 
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Manager assigned to property")
        return True
    else:
        print(f"❌ Failed to assign manager: {response.text}")
        return False

def create_test_application(property_id):
    """Create a test job application"""
    print(f"\nCreating test job application...")
    
    data = {
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com",
        "phone": "(555) 987-6543",
        "address": "456 Oak Avenue",
        "city": "Somewhere",
        "state": "CA",
        "zip_code": "90211",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-02-01",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes"
    }
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", data=data)
    
    if response.status_code == 200:
        app_data = response.json()
        print(f"✅ Test application created")
        print(f"   Application ID: {app_data['application_id']}")
        print(f"   Applicant: John Doe - Front Desk Agent")
        return app_data['application_id']
    else:
        print(f"❌ Failed to create application: {response.text}")
        return None

def main():
    """Main setup function"""
    print("🏨 Hotel Onboarding System - Test Account Setup")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        if response.status_code != 200:
            print("❌ Backend server is not responding. Please start it first:")
            print("   cd hotel-onboarding-backend")
            print("   python -m uvicorn app.main_enhanced:app --reload")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Please start it first:")
        print("   cd hotel-onboarding-backend")
        print("   python -m uvicorn app.main_enhanced:app --reload")
        return
    
    print("✅ Backend server is running")
    
    # Create accounts and test data
    hr_user = create_hr_account()
    if not hr_user:
        return
    
    hr_token = login_as_hr()
    if not hr_token:
        return
    
    property_data = create_property(hr_token)
    if not property_data:
        return
    
    manager_user, manager_token = create_manager_account()
    if not manager_user:
        return
    
    # Assign manager to property
    assign_manager_to_property(hr_token, property_data['id'], manager_user['email'])
    
    # Create test application
    application_id = create_test_application(property_data['id'])
    
    print("\n" + "=" * 50)
    print("🎉 Test Setup Complete!")
    print("=" * 50)
    
    print("\n📋 Test Accounts Created:")
    print(f"HR Account:")
    print(f"  Email: hr@hoteltest.com")
    print(f"  Password: password123")
    print(f"  Token: {hr_token}")
    
    print(f"\nManager Account:")
    print(f"  Email: manager@hoteltest.com") 
    print(f"  Password: password123")
    print(f"  Token: {manager_token}")
    
    print(f"\n🏨 Test Property:")
    print(f"  Name: {property_data['name']}")
    print(f"  ID: {property_data['id']}")
    print(f"  Application URL: {BASE_URL}/apply/{property_data['id']}")
    
    if application_id:
        print(f"\n📝 Test Application:")
        print(f"  ID: {application_id}")
        print(f"  Applicant: John Doe")
        print(f"  Position: Front Desk Agent")
    
    print(f"\n🔗 Quick Links:")
    print(f"  Backend API Docs: {BASE_URL}/docs")
    print(f"  Frontend (if running): http://localhost:5173")
    print(f"  Application Form: {BASE_URL}/apply/{property_data['id']}")
    
    print(f"\n📖 Next Steps:")
    print(f"  1. Start frontend: cd hotel-onboarding-frontend && npm run dev")
    print(f"  2. Login as manager to approve the test application")
    print(f"  3. Test the onboarding flow with the generated link")
    
    print(f"\n🧪 API Testing:")
    print(f"  # Get applications (as manager)")
    print(f"  curl -H 'Authorization: Bearer {manager_token}' {BASE_URL}/applications")
    print(f"  ")
    print(f"  # Approve application (as manager)")
    print(f"  curl -X POST -H 'Authorization: Bearer {manager_token}' \\")
    print(f"       -F 'job_title=Front Desk Agent' \\")
    print(f"       -F 'start_date=2025-02-01' \\")
    print(f"       -F 'start_time=08:00' \\")
    print(f"       -F 'pay_rate=18.50' \\")
    print(f"       -F 'pay_frequency=hourly' \\")
    print(f"       -F 'benefits_eligible=yes' \\")
    print(f"       -F 'supervisor=Jane Smith' \\")
    print(f"       {BASE_URL}/applications/{application_id}/approve")

if __name__ == "__main__":
    main()