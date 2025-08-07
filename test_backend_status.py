#!/usr/bin/env python3
"""
Test backend server status and check if changes are applied
"""

import requests
import json

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"

# Proper JWT tokens
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"

def test_backend_status():
    """Test backend server status"""
    print("🔍 Testing Backend Server Status")
    print("=" * 50)
    
    # Test health check
    print("\n📋 Testing Health Check")
    try:
        response = requests.get(f"{BACKEND_URL}/healthz")
        if response.status_code == 200:
            print("   ✅ Backend server is running")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend server not accessible: {e}")
        return
    
    # Test HR authentication
    print("\n📋 Testing HR Authentication")
    try:
        headers = {"Authorization": f"Bearer {HR_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"   ✅ HR user authenticated: {user_info.get('role')}")
        else:
            print(f"   ❌ HR authentication failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Auth test error: {e}")
    
    # Test HR applications access
    print("\n📋 Testing HR Applications Access")
    try:
        headers = {"Authorization": f"Bearer {HR_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
        if response.status_code == 200:
            applications = response.json()
            print(f"   ✅ HR can access applications: {len(applications)} found")
        else:
            print(f"   ❌ HR applications access failed: {response.status_code}")
            print(f"   📋 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Applications test error: {e}")
    
    # Test HR application statistics
    print("\n📋 Testing HR Application Statistics")
    try:
        headers = {"Authorization": f"Bearer {HR_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/hr/applications/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ HR can access application stats")
            print(f"   📊 Stats keys: {list(stats.keys())}")
        else:
            print(f"   ❌ HR application stats failed: {response.status_code}")
            print(f"   📋 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Stats test error: {e}")
    
    # Test simple approval (to check if role fix is applied)
    print("\n📋 Testing Simple Approval (Role Fix Check)")
    try:
        # First submit a test application
        test_app = {
            "first_name": "Role", "last_name": "TestUser",
            "email": f"role.test.{int(requests.get(f'{BACKEND_URL}/healthz').elapsed.total_seconds())}@example.com",
            "phone": "(555) 123-4567", "address": "123 Test St",
            "city": "New York", "state": "NY", "zip_code": "10001",
            "department": "Front Desk", "position": "Front Desk Agent",
            "work_authorized": "yes", "sponsorship_required": "no",
            "start_date": "2025-08-01", "shift_preference": "morning",
            "employment_type": "full_time", "experience_years": "2-5",
            "hotel_experience": "yes"
        }
        
        submit_response = requests.post(f"{BACKEND_URL}/apply/prop_test_001", json=test_app)
        if submit_response.status_code == 200:
            app_id = submit_response.json().get('application_id')
            print(f"   ✅ Test application submitted: {app_id}")
            
            # Try to approve it
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            approve_response = requests.post(f"{BACKEND_URL}/hr/applications/{app_id}/approve", headers=headers)
            
            if approve_response.status_code == 200:
                print("   ✅ HR approval working - role fix applied!")
            else:
                print(f"   ❌ HR approval failed: {approve_response.status_code}")
                print(f"   📋 Error: {approve_response.text}")
                if "Manager access required" in approve_response.text:
                    print("   🔄 Backend server needs restart to apply role fixes")
        else:
            print(f"   ❌ Test application submission failed: {submit_response.status_code}")
    except Exception as e:
        print(f"   ❌ Approval test error: {e}")

if __name__ == "__main__":
    test_backend_status()