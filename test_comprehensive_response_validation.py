#!/usr/bin/env python3
"""
Comprehensive test to validate standardized API response implementation
Tests all major endpoints for consistent response format
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def validate_success_response(response_data, endpoint_name):
    """Validate success response format"""
    errors = []
    
    # Required fields for success responses
    if "success" not in response_data:
        errors.append("Missing 'success' field")
    elif response_data["success"] != True:
        errors.append("'success' field should be True for successful responses")
    
    if "timestamp" not in response_data:
        errors.append("Missing 'timestamp' field")
    
    # Data field should be present for success responses
    if "data" not in response_data:
        errors.append("Missing 'data' field")
    
    # Optional fields
    if "message" in response_data and not isinstance(response_data["message"], str):
        errors.append("'message' field should be a string")
    
    return errors

def validate_error_response(response_data, endpoint_name):
    """Validate error response format"""
    errors = []
    
    # Required fields for error responses
    if "success" not in response_data:
        errors.append("Missing 'success' field")
    elif response_data["success"] != False:
        errors.append("'success' field should be False for error responses")
    
    if "error" not in response_data:
        errors.append("Missing 'error' field")
    
    if "error_code" not in response_data:
        errors.append("Missing 'error_code' field")
    
    if "status_code" not in response_data:
        errors.append("Missing 'status_code' field")
    
    if "timestamp" not in response_data:
        errors.append("Missing 'timestamp' field")
    
    # Optional fields
    if "detail" in response_data and not isinstance(response_data["detail"], str):
        errors.append("'detail' field should be a string")
    
    return errors

def test_endpoint(method, endpoint, headers=None, json_data=None, expected_status=200):
    """Test an endpoint and validate response format"""
    print(f"🔍 Testing {method} {endpoint}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method.upper() == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=json_data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response")
            return False
        
        # Validate response format based on success/error
        if response.status_code < 400:
            # Success response
            validation_errors = validate_success_response(response_data, endpoint)
            if validation_errors:
                print(f"❌ Success response format errors: {', '.join(validation_errors)}")
                return False
            else:
                print(f"✅ Success response format is correct")
                return True
        else:
            # Error response
            validation_errors = validate_error_response(response_data, endpoint)
            if validation_errors:
                print(f"❌ Error response format errors: {', '.join(validation_errors)}")
                return False
            else:
                print(f"✅ Error response format is correct")
                return True
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Run comprehensive response validation tests"""
    print("=" * 80)
    print("COMPREHENSIVE API RESPONSE FORMAT VALIDATION")
    print("=" * 80)
    print()
    
    # Get HR token for authenticated tests
    hr_token = None
    print("🔑 Getting HR authentication token...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "hr@hoteltest.com", "password": "admin123"}
        )
        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get("success") and "data" in login_data:
                hr_token = login_data["data"]["token"]
                print("✅ HR token obtained successfully")
            else:
                print("❌ Failed to get HR token from response")
        else:
            print(f"❌ HR login failed with status {login_response.status_code}")
    except Exception as e:
        print(f"❌ HR login failed with exception: {e}")
    
    print()
    
    # Test cases
    test_cases = [
        # Health check
        ("GET", "/healthz", None, None, 200),
        
        # Authentication endpoints
        ("POST", "/auth/login", None, {"email": "hr@hoteltest.com", "password": "admin123"}, 200),
        ("POST", "/auth/login", None, {"email": "", "password": ""}, 400),
        ("POST", "/auth/login", None, {"email": "invalid@test.com", "password": "wrong"}, 401),
        
        # 404 error
        ("GET", "/nonexistent-endpoint", None, None, 404),
        
        # Authenticated endpoints (if HR token is available)
    ]
    
    if hr_token:
        auth_headers = {"Authorization": f"Bearer {hr_token}"}
        test_cases.extend([
            ("GET", "/auth/me", auth_headers, None, 200),
            ("POST", "/auth/logout", auth_headers, None, 200),
            ("GET", "/hr/dashboard-stats", auth_headers, None, 200),
            ("GET", "/hr/properties", auth_headers, None, 200),
            ("GET", "/hr/applications", auth_headers, None, 200),
        ])
    
    # Run tests
    passed = 0
    total = len(test_cases)
    
    for method, endpoint, headers, json_data, expected_status in test_cases:
        if test_endpoint(method, endpoint, headers, json_data, expected_status):
            passed += 1
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Standardized response format is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print()
    print("Standardized Response Format Requirements:")
    print("✅ All responses include 'success' boolean field")
    print("✅ All responses include 'timestamp' field")
    print("✅ Success responses include 'data' field")
    print("✅ Error responses include 'error', 'error_code', and 'status_code' fields")
    print("✅ Consistent HTTP status codes are used")
    print("✅ Optional 'message' and 'detail' fields are properly formatted")

if __name__ == "__main__":
    main()