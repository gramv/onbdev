#!/usr/bin/env python3
"""
Test script for job application submission endpoint
"""
import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:8000"

def test_job_application_submission():
    """Test the job application submission endpoint"""
    
    # First, get property info to ensure the property exists
    property_id = "prop_test_001"  # From test data
    
    print("🧪 Testing Job Application Submission Endpoint")
    print("=" * 50)
    
    # Test 1: Get property info (should work)
    print("\n1. Testing property info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/properties/{property_id}/info")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            property_info = response.json()
            print(f"   ✅ Property: {property_info['property']['name']}")
            print(f"   ✅ Available departments: {list(property_info['departments_and_positions'].keys())}")
        else:
            print(f"   ❌ Failed to get property info: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error getting property info: {e}")
        return
    
    # Test 2: Submit valid job application
    print("\n2. Testing valid job application submission...")
    
    valid_application = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
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
        "hotel_experience": "yes",
        "previous_employer": "Test Hotel",
        "reason_for_leaving": "Career advancement",
        "additional_comments": "Excited to join your team!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/apply/{property_id}",
            json=valid_application,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Application submitted successfully!")
            print(f"   ✅ Application ID: {result['application_id']}")
            print(f"   ✅ Property: {result['property_name']}")
            print(f"   ✅ Position: {result['position_applied']}")
            print(f"   ✅ Message: {result['message']}")
        else:
            print(f"   ❌ Failed to submit application: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error submitting application: {e}")
    
    # Test 3: Test duplicate application prevention
    print("\n3. Testing duplicate application prevention...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/apply/{property_id}",
            json=valid_application,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 400:
            print(f"   ✅ Duplicate application correctly rejected")
            print(f"   ✅ Error message: {response.json()['detail']}")
        else:
            print(f"   ❌ Duplicate application should have been rejected")
            
    except Exception as e:
        print(f"   ❌ Error testing duplicate: {e}")
    
    # Test 4: Test invalid department
    print("\n4. Testing invalid department validation...")
    
    invalid_dept_application = valid_application.copy()
    invalid_dept_application["email"] = "different@example.com"  # Different email to avoid duplicate
    invalid_dept_application["department"] = "Invalid Department"
    
    try:
        response = requests.post(
            f"{BASE_URL}/apply/{property_id}",
            json=invalid_dept_application,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 400:
            print(f"   ✅ Invalid department correctly rejected")
            print(f"   ✅ Error message: {response.json()['detail']}")
        else:
            print(f"   ❌ Invalid department should have been rejected")
            
    except Exception as e:
        print(f"   ❌ Error testing invalid department: {e}")
    
    # Test 5: Test invalid position
    print("\n5. Testing invalid position validation...")
    
    invalid_pos_application = valid_application.copy()
    invalid_pos_application["email"] = "another@example.com"  # Different email
    invalid_pos_application["position"] = "Invalid Position"
    
    try:
        response = requests.post(
            f"{BASE_URL}/apply/{property_id}",
            json=invalid_pos_application,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 400:
            print(f"   ✅ Invalid position correctly rejected")
            print(f"   ✅ Error message: {response.json()['detail']}")
        else:
            print(f"   ❌ Invalid position should have been rejected")
            
    except Exception as e:
        print(f"   ❌ Error testing invalid position: {e}")
    
    # Test 6: Test nonexistent property
    print("\n6. Testing nonexistent property...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/apply/nonexistent-property",
            json=valid_application,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 404:
            print(f"   ✅ Nonexistent property correctly rejected")
            print(f"   ✅ Error message: {response.json()['detail']}")
        else:
            print(f"   ❌ Nonexistent property should have been rejected")
            
    except Exception as e:
        print(f"   ❌ Error testing nonexistent property: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Job Application Submission Tests Complete")

if __name__ == "__main__":
    test_job_application_submission()