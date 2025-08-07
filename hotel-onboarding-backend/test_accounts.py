#!/usr/bin/env python3
"""
Test script to verify the dummy accounts work
Run this after starting the backend server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print("❌ Backend server responded with error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Start it with: python -m uvicorn app.main_enhanced:app --reload")
        return False

def test_hr_login():
    """Test HR account login"""
    print("\n🧪 Testing HR login...")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "hr@hoteltest.com",
        "password": "password123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ HR login successful")
        print(f"   Token: {data['token']}")
        print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"   Role: {data['user']['role']}")
        return data['token']
    else:
        print(f"❌ HR login failed: {response.text}")
        return None

def test_manager_login():
    """Test Manager account login"""
    print("\n🧪 Testing Manager login...")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "password123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Manager login successful")
        print(f"   Token: {data['token']}")
        print(f"   User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"   Role: {data['user']['role']}")
        print(f"   Property ID: {data['user']['property_id']}")
        return data['token']
    else:
        print(f"❌ Manager login failed: {response.text}")
        return None

def test_get_properties(hr_token):
    """Test getting properties as HR"""
    print("\n🧪 Testing HR - Get Properties...")
    
    headers = {"Authorization": f"Bearer {hr_token}"}
    response = requests.get(f"{BASE_URL}/hr/properties", headers=headers)
    
    if response.status_code == 200:
        properties = response.json()
        print(f"✅ Properties retrieved: {len(properties)} found")
        for prop in properties:
            print(f"   - {prop['name']} (ID: {prop['id']})")
        return properties
    else:
        print(f"❌ Failed to get properties: {response.text}")
        return []

def test_get_applications(manager_token):
    """Test getting applications as Manager"""
    print("\n🧪 Testing Manager - Get Applications...")
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = requests.get(f"{BASE_URL}/applications", headers=headers)
    
    if response.status_code == 200:
        applications = response.json()
        print(f"✅ Applications retrieved: {len(applications)} found")
        for app in applications:
            applicant = app['applicant_data']
            print(f"   - {applicant['first_name']} {applicant['last_name']} - {app['position']} ({app['status']})")
        return applications
    else:
        print(f"❌ Failed to get applications: {response.text}")
        return []

def test_application_form(property_id):
    """Test getting application form"""
    print(f"\n🧪 Testing Application Form (Property: {property_id})...")
    
    response = requests.get(f"{BASE_URL}/apply/{property_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Application form retrieved")
        print(f"   Property: {data['property']['name']}")
        print(f"   Departments: {len(data['departments'])} available")
        print(f"   QR Code URL: {data['property']['qr_code_url']}")
        return True
    else:
        print(f"❌ Failed to get application form: {response.text}")
        return False

def main():
    """Run all tests"""
    print("🏨 Hotel Onboarding System - Account Testing")
    print("=" * 50)
    
    # Test backend health
    if not test_health():
        return
    
    # Test logins
    hr_token = test_hr_login()
    manager_token = test_manager_login()
    
    if not hr_token or not manager_token:
        print("\n❌ Login tests failed. Check if test data was initialized.")
        return
    
    # Test HR functions
    properties = test_get_properties(hr_token)
    
    # Test Manager functions  
    applications = test_get_applications(manager_token)
    
    # Test application form
    if properties:
        test_application_form(properties[0]['id'])
    
    print("\n" + "=" * 50)
    print("🎉 All Tests Complete!")
    print("=" * 50)
    
    print("\n📋 Test Account Summary:")
    print("HR Account:")
    print("  Email: hr@hoteltest.com")
    print("  Password: password123")
    print(f"  Token: {hr_token}")
    
    print("\nManager Account:")
    print("  Email: manager@hoteltest.com")
    print("  Password: password123") 
    print(f"  Token: {manager_token}")
    
    if properties:
        prop = properties[0]
        print(f"\n🏨 Test Property:")
        print(f"  Name: {prop['name']}")
        print(f"  ID: {prop['id']}")
        print(f"  Application URL: {BASE_URL}/apply/{prop['id']}")
    
    if applications:
        app = applications[0]
        print(f"\n📝 Test Application:")
        print(f"  Applicant: {app['applicant_data']['first_name']} {app['applicant_data']['last_name']}")
        print(f"  Position: {app['position']}")
        print(f"  Status: {app['status']}")
        print(f"  ID: {app['id']}")
    
    print(f"\n🔗 Quick API Tests:")
    print(f"# Test HR endpoints")
    print(f"curl -H 'Authorization: Bearer {hr_token}' {BASE_URL}/hr/properties")
    print(f"")
    print(f"# Test Manager endpoints")  
    print(f"curl -H 'Authorization: Bearer {manager_token}' {BASE_URL}/applications")
    
    if applications:
        app_id = applications[0]['id']
        print(f"")
        print(f"# Approve application (as manager)")
        print(f"curl -X POST -H 'Authorization: Bearer {manager_token}' \\")
        print(f"     -F 'job_title=Front Desk Agent' \\")
        print(f"     -F 'start_date=2025-02-01' \\")
        print(f"     -F 'start_time=08:00' \\")
        print(f"     -F 'pay_rate=18.50' \\")
        print(f"     -F 'pay_frequency=hourly' \\")
        print(f"     -F 'benefits_eligible=yes' \\")
        print(f"     -F 'supervisor=Jane Smith' \\")
        print(f"     {BASE_URL}/applications/{app_id}/approve")

if __name__ == "__main__":
    main()