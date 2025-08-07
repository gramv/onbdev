#!/usr/bin/env python3
"""
Test script to verify applications are stored correctly and accessible to managers
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_application_storage():
    """Test that submitted applications are stored and accessible"""
    
    print("🧪 Testing Application Storage and Retrieval")
    print("=" * 50)
    
    # First, login as manager to get token
    print("\n1. Logging in as manager...")
    login_data = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Login Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   ❌ Failed to login: {response.text}")
        return
    
    login_result = response.json()
    token = login_result["token"]
    print(f"   ✅ Manager logged in successfully")
    
    # Get applications list
    print("\n2. Retrieving applications list...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/applications", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        applications = response.json()
        print(f"   ✅ Found {len(applications)} applications")
        
        # Look for our test applications (from our test scripts)
        test_applications = [app for app in applications if "example.com" in app.get("applicant_email", "").lower()]
        print(f"   ✅ Found {len(test_applications)} test applications from our tests")
        
        # Show details of all applications
        for i, app in enumerate(applications):
            print(f"   📋 Application {i+1}: {app['applicant_name']}")
            print(f"      Email: {app['applicant_email']}")
            print(f"      Position: {app['position']} - {app['department']}")
            print(f"      Status: {app['status']}")
            print(f"      Applied: {app['applied_at'][:19]}")
            print(f"      Days since applied: {app['days_since_applied']}")
            print()
    else:
        print(f"   ❌ Failed to get applications: {response.text}")
    
    print("=" * 50)
    print("🏁 Application Storage Test Complete")

if __name__ == "__main__":
    test_application_storage()