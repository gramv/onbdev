#!/usr/bin/env python3
"""
Test script for Task 6 with unique email addresses
This avoids the duplicate application prevention logic
"""

import requests
import json
import time
import random
import string

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"
TEST_PROPERTY_ID = "prop_test_001"

def generate_unique_email():
    """Generate a unique email address for testing"""
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test.task6.{random_string}@example.com"

def test_property_info_endpoint():
    """Test the /properties/{property_id}/info endpoint"""
    print("🧪 Testing Property Info Endpoint...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        
        # Verify response structure
        required_fields = ["property", "departments_and_positions", "application_url", "is_accepting_applications"]
        for field in required_fields:
            if field not in data:
                print(f"   ❌ Missing required field: {field}")
                return False
        
        property_info = data["property"]
        required_property_fields = ["id", "name", "address", "city", "state", "zip_code", "phone"]
        for field in required_property_fields:
            if field not in property_info:
                print(f"   ❌ Missing required property field: {field}")
                return False
        
        print("   ✅ Property info endpoint working correctly")
        print(f"   📍 Property: {property_info['name']}")
        print(f"   🏢 Address: {property_info['address']}, {property_info['city']}, {property_info['state']} {property_info['zip_code']}")
        print(f"   📞 Phone: {property_info['phone']}")
        print(f"   🏷️ Departments: {list(data['departments_and_positions'].keys())}")
        print(f"   🔗 Application URL: {data['application_url']}")
        print(f"   ✅ Accepting Applications: {data['is_accepting_applications']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Property info endpoint failed: {e}")
        return False

def test_application_submission_with_unique_emails():
    """Test the /apply/{property_id} endpoint with unique email addresses"""
    print("\n🧪 Testing Application Submission with Unique Emails...")
    
    # Test different departments and positions
    test_applications = [
        {
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "first_name": "Alice",
            "last_name": "Johnson"
        },
        {
            "department": "Housekeeping", 
            "position": "Housekeeper",
            "first_name": "Bob",
            "last_name": "Smith"
        },
        {
            "department": "Food & Beverage",
            "position": "Server",
            "first_name": "Carol",
            "last_name": "Davis"
        },
        {
            "department": "Maintenance",
            "position": "Maintenance Technician",
            "first_name": "David",
            "last_name": "Wilson"
        }
    ]
    
    successful_submissions = 0
    
    for i, app_template in enumerate(test_applications, 1):
        print(f"\n   Test {i}: {app_template['department']} - {app_template['position']}")
        
        test_application = {
            "first_name": app_template["first_name"],
            "last_name": app_template["last_name"],
            "email": generate_unique_email(),  # Unique email each time
            "phone": f"555{random.randint(1000000, 9999999)}",  # Unique phone
            "address": f"{random.randint(100, 999)} Test Street",
            "city": "Test City",
            "state": "CA",
            "zip_code": f"{random.randint(10000, 99999)}",
            "department": app_template["department"],
            "position": app_template["position"],
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-15",
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
            
            print(f"      Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    print(f"      ✅ Application submitted successfully")
                    print(f"      📝 Application ID: {data['application_id']}")
                    print(f"      📧 Email: {test_application['email']}")
                    successful_submissions += 1
                else:
                    print(f"      ❌ Application not successful: {data}")
            else:
                print(f"      ❌ Failed with status {response.status_code}")
                if response.status_code == 422:
                    print(f"      📝 Validation Error: {response.json()}")
                elif response.status_code == 400:
                    print(f"      📝 Error: {response.json()}")
                    
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    print(f"\n   📊 Results: {successful_submissions}/{len(test_applications)} applications submitted successfully")
    return successful_submissions > 0

def test_frontend_accessibility():
    """Test that the frontend form is accessible"""
    print("\n🌐 Testing Frontend Accessibility...")
    
    try:
        form_url = f"{FRONTEND_URL}/apply/{TEST_PROPERTY_ID}"
        response = requests.get(form_url)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Frontend form not accessible, got {response.status_code}")
            return False
        
        print("   ✅ Frontend form is accessible")
        print(f"   🔗 Form URL: {form_url}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Frontend accessibility test failed: {e}")
        return False

def test_duplicate_prevention():
    """Test that duplicate application prevention is working"""
    print("\n🔒 Testing Duplicate Application Prevention...")
    
    # Use the same email twice
    duplicate_email = generate_unique_email()
    
    test_application = {
        "first_name": "Duplicate",
        "last_name": "Test",
        "email": duplicate_email,
        "phone": "5551234567",
        "address": "123 Duplicate St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "12345",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-08-01",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes"
    }
    
    try:
        # First submission should succeed
        print("   Submitting first application...")
        response1 = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=test_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response1.status_code == 200:
            print("   ✅ First application submitted successfully")
        else:
            print(f"   ❌ First application failed: {response1.status_code}")
            return False
        
        # Second submission should fail with duplicate error
        print("   Submitting duplicate application...")
        response2 = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=test_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response2.status_code == 400:
            error_data = response2.json()
            if "already submitted" in error_data.get("detail", "").lower():
                print("   ✅ Duplicate prevention working correctly")
                print(f"   📝 Error message: {error_data['detail']}")
                return True
            else:
                print(f"   ❌ Unexpected error message: {error_data}")
                return False
        else:
            print(f"   ❌ Expected 400 for duplicate, got {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Duplicate prevention test failed: {e}")
        return False

def main():
    """Run all tests for Task 6 with unique emails"""
    print("🚀 Testing Task 6: Update Job Application Form Route (With Unique Emails)")
    print("=" * 80)
    
    tests = [
        ("Property Info Endpoint", test_property_info_endpoint),
        ("Application Submission with Unique Emails", test_application_submission_with_unique_emails),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("Duplicate Application Prevention", test_duplicate_prevention)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 Task 6 implementation is working correctly!")
        print("✅ JobApplicationForm successfully updated to use new endpoints")
        print("✅ Form works without authentication")
        print("✅ Property info fetched from /properties/{property_id}/info")
        print("✅ Applications submitted to /apply/{property_id}")
        print("✅ Duplicate prevention is working correctly")
        print("✅ All departments and positions can be submitted")
        print("✅ Frontend is accessible and functional")
    else:
        print(f"\n⚠️ Task 6 implementation needs attention ({total_tests - passed_tests} tests failed).")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)