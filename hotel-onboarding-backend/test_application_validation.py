#!/usr/bin/env python3
"""
Test script for job application validation edge cases
"""
import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:8000"

def test_application_validation():
    """Test various validation scenarios for job application submission"""
    
    property_id = "prop_test_001"  # From test data
    
    print("🧪 Testing Job Application Validation Edge Cases")
    print("=" * 60)
    
    # Base valid application
    base_application = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone": "555-123-4567",
        "address": "123 Test Street",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes"
    }
    
    # Test 1: Invalid email format
    print("\n1. Testing invalid email format...")
    invalid_email_app = base_application.copy()
    invalid_email_app["email"] = "invalid-email"
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=invalid_email_app,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print("   ✅ Invalid email format correctly rejected")
    else:
        print("   ❌ Invalid email should have been rejected")
    
    # Test 2: Invalid phone number
    print("\n2. Testing invalid phone number...")
    invalid_phone_app = base_application.copy()
    invalid_phone_app["email"] = "test2@example.com"
    invalid_phone_app["phone"] = "123"  # Too short
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=invalid_phone_app,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print("   ✅ Invalid phone number correctly rejected")
    else:
        print("   ❌ Invalid phone number should have been rejected")
    
    # Test 3: Past start date
    print("\n3. Testing past start date...")
    past_date_app = base_application.copy()
    past_date_app["email"] = "test3@example.com"
    past_date_app["start_date"] = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=past_date_app,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print("   ✅ Past start date correctly rejected")
    else:
        print("   ❌ Past start date should have been rejected")
    
    # Test 4: Invalid work authorization value
    print("\n4. Testing invalid work authorization...")
    invalid_auth_app = base_application.copy()
    invalid_auth_app["email"] = "test4@example.com"
    invalid_auth_app["work_authorized"] = "maybe"  # Should be yes/no
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=invalid_auth_app,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print("   ✅ Invalid work authorization correctly rejected")
    else:
        print("   ❌ Invalid work authorization should have been rejected")
    
    # Test 5: Missing required fields
    print("\n5. Testing missing required fields...")
    incomplete_app = {
        "first_name": "Test",
        "last_name": "User"
        # Missing many required fields
    }
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=incomplete_app,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print("   ✅ Missing required fields correctly rejected")
        error_detail = response.json().get("detail", [])
        missing_fields = [error["loc"][-1] for error in error_detail if error["type"] == "missing"]
        print(f"   ✅ Missing fields detected: {missing_fields[:5]}...")  # Show first 5
    else:
        print("   ❌ Missing required fields should have been rejected")
    
    # Test 6: Valid application with optional fields
    print("\n6. Testing valid application with optional fields...")
    complete_app = base_application.copy()
    complete_app["email"] = "complete@example.com"
    complete_app["previous_employer"] = "Previous Hotel"
    complete_app["reason_for_leaving"] = "Career growth"
    complete_app["additional_comments"] = "Looking forward to joining!"
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=complete_app,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Complete application with optional fields accepted")
        print(f"   ✅ Application ID: {result['application_id']}")
    else:
        print("   ❌ Complete application should have been accepted")
        print(f"   ❌ Error: {response.text}")
    
    print("\n" + "=" * 60)
    print("🏁 Job Application Validation Tests Complete")

if __name__ == "__main__":
    test_application_validation()