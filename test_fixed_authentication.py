#!/usr/bin/env python3
"""
Quick test to verify authentication is working with proper JWT tokens
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_PROPERTY_ID = "prop_test_001"

# Proper JWT tokens
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

def test_authentication():
    """Test authentication with proper JWT tokens"""
    print("🔐 Testing Authentication with JWT Tokens")
    print("=" * 50)
    
    # Test HR authentication
    print("\n📋 Testing HR Authentication")
    try:
        headers = {"Authorization": f"Bearer {HR_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/hr/dashboard-stats", headers=headers)
        
        if response.status_code == 200:
            print("   ✅ HR authentication working!")
            data = response.json()
            print(f"   📊 Dashboard stats: {list(data.keys())}")
        else:
            print(f"   ❌ HR authentication failed: {response.status_code}")
            print(f"   📋 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ HR auth error: {e}")
    
    # Test Manager authentication
    print("\n📋 Testing Manager Authentication")
    try:
        headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
        
        if response.status_code == 200:
            print("   ✅ Manager authentication working!")
            data = response.json()
            print(f"   📊 Applications accessible: {len(data)}")
        else:
            print(f"   ❌ Manager authentication failed: {response.status_code}")
            print(f"   📋 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Manager auth error: {e}")
    
    # Test HR applications access
    print("\n📋 Testing HR Applications Access")
    try:
        headers = {"Authorization": f"Bearer {HR_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
        
        if response.status_code == 200:
            print("   ✅ HR can access applications!")
            data = response.json()
            print(f"   📊 Applications found: {len(data)}")
        else:
            print(f"   ❌ HR applications access failed: {response.status_code}")
            print(f"   📋 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ HR applications error: {e}")

def test_application_workflow():
    """Test complete application workflow"""
    print("\n🔄 Testing Application Workflow")
    print("=" * 50)
    
    # Submit test application
    print("\n📋 Step 1: Submit Application")
    test_application = {
        "first_name": "Workflow",
        "last_name": "TestUser",
        "email": f"workflow.{int(datetime.now().timestamp())}@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Test Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=test_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            app_id = result.get('application_id')
            print(f"   ✅ Application submitted: {app_id}")
            
            # Test HR can see the application
            print("\n📋 Step 2: HR Reviews Application")
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
            
            if response.status_code == 200:
                applications = response.json()
                workflow_app = next((app for app in applications if app.get('id') == app_id), None)
                if workflow_app:
                    print("   ✅ HR can see the application!")
                    
                    # Test approval
                    print("\n📋 Step 3: HR Approves Application")
                    approve_response = requests.post(
                        f"{BACKEND_URL}/hr/applications/{app_id}/approve",
                        headers=headers
                    )
                    
                    if approve_response.status_code == 200:
                        print("   ✅ Application approved successfully!")
                        print("   🎉 Complete workflow working!")
                    else:
                        print(f"   ❌ Approval failed: {approve_response.status_code}")
                        print(f"   📋 Error: {approve_response.text}")
                else:
                    print("   ❌ Application not found in HR view")
            else:
                print(f"   ❌ HR review failed: {response.status_code}")
        else:
            print(f"   ❌ Application submission failed: {response.status_code}")
            print(f"   📋 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Workflow error: {e}")

def main():
    """Run authentication and workflow tests"""
    print("🚀 TESTING AUTHENTICATION AND WORKFLOW FIXES")
    print("=" * 60)
    
    test_authentication()
    test_application_workflow()
    
    print("\n" + "=" * 60)
    print("✅ Authentication Testing Complete!")

if __name__ == "__main__":
    main()