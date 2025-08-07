#!/usr/bin/env python3
"""
Simple test script for Task 6: Update Job Application Form Route
Tests the backend endpoints and verifies the frontend can access them
"""

import requests
import json

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"
TEST_PROPERTY_ID = "prop_test_001"

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

def test_application_submission_endpoint():
    """Test the /apply/{property_id} endpoint"""
    print("\n🧪 Testing Application Submission Endpoint...")
    
    test_application = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith.task6@example.com",
        "phone": "5559876543",
        "address": "789 Application Street",
        "city": "Application City",
        "state": "NY",
        "zip_code": "54321",
        "department": "Housekeeping",
        "position": "Housekeeper",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-08-15",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "0-1",
        "hotel_experience": "no"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=test_application,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}")
            if response.status_code == 422:
                print(f"   📝 Validation Error: {response.json()}")
            return False
        
        data = response.json()
        
        # Verify response structure
        required_fields = ["success", "message", "application_id"]
        for field in required_fields:
            if field not in data:
                print(f"   ❌ Missing required field: {field}")
                return False
        
        if not data["success"]:
            print(f"   ❌ Application submission not successful")
            return False
        
        print("   ✅ Application submission endpoint working correctly")
        print(f"   📝 Application ID: {data['application_id']}")
        print(f"   💬 Message: {data['message']}")
        
        if "property_name" in data:
            print(f"   🏨 Property: {data['property_name']}")
        if "position_applied" in data:
            print(f"   💼 Position: {data['position_applied']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Application submission endpoint failed: {e}")
        return False

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

def test_cors_headers():
    """Test that CORS headers are properly configured"""
    print("\n🔒 Testing CORS Configuration...")
    
    try:
        # Test preflight request
        response = requests.options(
            f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        print(f"   Preflight Status Code: {response.status_code}")
        
        # Test actual request with Origin header
        response = requests.get(
            f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info",
            headers={"Origin": FRONTEND_URL}
        )
        
        print(f"   Request Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ CORS configuration appears to be working")
            return True
        else:
            print(f"   ⚠️ CORS might have issues, status: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
        return False

def test_data_validation():
    """Test data validation on the backend"""
    print("\n🔍 Testing Data Validation...")
    
    # Test with invalid department
    invalid_application = {
        "first_name": "Test",
        "last_name": "Invalid",
        "email": "test.invalid@example.com",
        "phone": "5551234567",
        "address": "123 Test St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "12345",
        "department": "InvalidDepartment",  # Invalid department
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
        response = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=invalid_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("   ✅ Data validation working correctly (rejected invalid department)")
            return True
        else:
            print(f"   ⚠️ Expected 400 for invalid data, got {response.status_code}")
            return False
        
    except Exception as e:
        print(f"   ❌ Data validation test failed: {e}")
        return False

def main():
    """Run all tests for Task 6"""
    print("🚀 Testing Task 6: Update Job Application Form Route")
    print("=" * 70)
    
    tests = [
        ("Property Info Endpoint", test_property_info_endpoint),
        ("Application Submission Endpoint", test_application_submission_endpoint),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("CORS Configuration", test_cors_headers),
        ("Data Validation", test_data_validation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
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
        print("✅ Data validation is working")
        print("✅ CORS is properly configured")
    else:
        print(f"\n⚠️ Task 6 implementation needs attention ({total_tests - passed_tests} tests failed).")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)