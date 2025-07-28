#!/usr/bin/env python3
"""
Test simple approval to debug the issue
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_PROPERTY_ID = "prop_test_001"

# Proper JWT tokens
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"

def test_simple_approval():
    """Test simple approval"""
    print("🔍 Testing Simple Approval")
    print("=" * 40)
    
    # First, submit a test application
    print("\n📋 Step 1: Submit Test Application")
    test_application = {
        "first_name": "Simple",
        "last_name": "TestUser",
        "email": f"simple.{int(datetime.now().timestamp())}@example.com",
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
            
            # Now try to approve it
            print(f"\n📋 Step 2: Approve Application {app_id}")
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            
            # Try with empty body first
            approve_response = requests.post(
                f"{BACKEND_URL}/hr/applications/{app_id}/approve",
                headers=headers
            )
            
            print(f"   📊 Approval response status: {approve_response.status_code}")
            print(f"   📊 Approval response: {approve_response.text}")
            
            if approve_response.status_code != 200:
                # Try with minimal job offer data
                print(f"\n📋 Step 3: Try with job offer data")
                job_offer = {
                    "job_title": "Front Desk Agent",
                    "start_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "pay_rate": 15.0,
                    "pay_frequency": "hourly",
                    "employment_type": "full_time",
                    "supervisor": "Test Manager"
                }
                
                approve_response2 = requests.post(
                    f"{BACKEND_URL}/hr/applications/{app_id}/approve",
                    json=job_offer,
                    headers=headers
                )
                
                print(f"   📊 Approval with data status: {approve_response2.status_code}")
                print(f"   📊 Approval with data response: {approve_response2.text}")
            
        else:
            print(f"   ❌ Application submission failed: {response.status_code}")
            print(f"   📋 Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_simple_approval()