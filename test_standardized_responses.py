#!/usr/bin/env python3
"""
Test script to verify standardized API response implementation
Tests the new response format across different endpoints
"""
import asyncio
import json
import requests
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_CREDENTIALS = {
    "hr": {"email": "hr@hoteltest.com", "password": "admin123"},
    "manager": {"email": "manager@hoteltest.com", "password": "manager123"}
}

class ResponseTester:
    def __init__(self):
        self.session = requests.Session()
        self.tokens = {}
    
    def test_health_check(self):
        """Test health check endpoint response format"""
        print("🔍 Testing health check endpoint...")
        
        response = self.session.get(f"{BASE_URL}/healthz")
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify standardized response format
            assert "success" in data, "Missing 'success' field"
            assert "data" in data, "Missing 'data' field"
            assert "timestamp" in data, "Missing 'timestamp' field"
            
            if data["success"]:
                assert data["data"]["status"] == "healthy", "Health status not healthy"
                print("✅ Health check response format is correct")
            else:
                print("❌ Health check failed but response format is correct")
                
        except Exception as e:
            print(f"❌ Health check response format error: {e}")
    
    def test_login_endpoint(self, role="hr"):
        """Test login endpoint response format"""
        print(f"🔍 Testing login endpoint for {role}...")
        
        credentials = TEST_CREDENTIALS[role]
        response = self.session.post(
            f"{BASE_URL}/auth/login",
            json=credentials
        )
        
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify standardized response format
            assert "success" in data, "Missing 'success' field"
            assert "timestamp" in data, "Missing 'timestamp' field"
            
            if data["success"]:
                assert "data" in data, "Missing 'data' field"
                assert "message" in data, "Missing 'message' field"
                
                # Verify login data structure
                login_data = data["data"]
                assert "token" in login_data, "Missing 'token' field in data"
                assert "user" in login_data, "Missing 'user' field in data"
                assert "expires_at" in login_data, "Missing 'expires_at' field in data"
                assert "token_type" in login_data, "Missing 'token_type' field in data"
                
                # Store token for further tests
                self.tokens[role] = login_data["token"]
                print(f"✅ Login response format is correct for {role}")
                
            else:
                assert "error" in data, "Missing 'error' field for failed login"
                assert "error_code" in data, "Missing 'error_code' field for failed login"
                print(f"❌ Login failed but response format is correct for {role}")
                
        except Exception as e:
            print(f"❌ Login response format error for {role}: {e}")
    
    def test_dashboard_stats(self, role="hr"):
        """Test dashboard stats endpoint response format"""
        print(f"🔍 Testing dashboard stats endpoint for {role}...")
        
        if role not in self.tokens:
            print(f"❌ No token available for {role}, skipping test")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = f"{BASE_URL}/{role}/dashboard-stats"
        
        response = self.session.get(endpoint, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify standardized response format
            assert "success" in data, "Missing 'success' field"
            assert "timestamp" in data, "Missing 'timestamp' field"
            
            if data["success"]:
                assert "data" in data, "Missing 'data' field"
                assert "message" in data, "Missing 'message' field"
                
                # Verify dashboard data structure
                stats_data = data["data"]
                if role == "hr":
                    expected_fields = ["totalProperties", "totalManagers", "totalEmployees", "pendingApplications"]
                else:  # manager
                    expected_fields = ["pendingApplications", "approvedApplications", "totalApplications"]
                
                for field in expected_fields:
                    if field in stats_data:
                        assert isinstance(stats_data[field], int), f"Field {field} should be integer"
                
                print(f"✅ Dashboard stats response format is correct for {role}")
                
            else:
                assert "error" in data, "Missing 'error' field for failed request"
                assert "error_code" in data, "Missing 'error_code' field for failed request"
                print(f"❌ Dashboard stats failed but response format is correct for {role}")
                
        except Exception as e:
            print(f"❌ Dashboard stats response format error for {role}: {e}")
    
    def test_applications_endpoint(self, role="manager"):
        """Test applications endpoint response format"""
        print(f"🔍 Testing applications endpoint for {role}...")
        
        if role not in self.tokens:
            print(f"❌ No token available for {role}, skipping test")
            return
        
        headers = {"Authorization": f"Bearer {self.tokens[role]}"}
        endpoint = f"{BASE_URL}/{role}/applications"
        
        response = self.session.get(endpoint, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify standardized response format
            assert "success" in data, "Missing 'success' field"
            assert "timestamp" in data, "Missing 'timestamp' field"
            
            if data["success"]:
                assert "data" in data, "Missing 'data' field"
                assert "message" in data, "Missing 'message' field"
                
                # Verify applications data structure
                applications_data = data["data"]
                assert isinstance(applications_data, list), "Applications data should be a list"
                
                if applications_data:
                    app = applications_data[0]
                    expected_fields = ["id", "property_id", "department", "position", "applicant_data", "status", "applied_at"]
                    for field in expected_fields:
                        assert field in app, f"Missing field {field} in application data"
                
                print(f"✅ Applications response format is correct for {role}")
                
            else:
                assert "error" in data, "Missing 'error' field for failed request"
                assert "error_code" in data, "Missing 'error_code' field for failed request"
                print(f"❌ Applications request failed but response format is correct for {role}")
                
        except Exception as e:
            print(f"❌ Applications response format error for {role}: {e}")
    
    def test_invalid_endpoint(self):
        """Test 404 error response format"""
        print("🔍 Testing 404 error response format...")
        
        response = self.session.get(f"{BASE_URL}/nonexistent-endpoint")
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify standardized error response format
            assert "success" in data, "Missing 'success' field"
            assert data["success"] == False, "Success should be False for 404"
            assert "error" in data, "Missing 'error' field"
            assert "error_code" in data, "Missing 'error_code' field"
            assert "status_code" in data, "Missing 'status_code' field"
            assert "timestamp" in data, "Missing 'timestamp' field"
            assert data["status_code"] == 404, "Status code should be 404"
            
            print("✅ 404 error response format is correct")
            
        except Exception as e:
            print(f"❌ 404 error response format error: {e}")
    
    def test_validation_error(self):
        """Test validation error response format"""
        print("🔍 Testing validation error response format...")
        
        # Send invalid login data
        response = self.session.post(
            f"{BASE_URL}/auth/login",
            json={"email": "", "password": ""}
        )
        
        print(f"Status Code: {response.status_code}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Verify standardized error response format
            assert "success" in data, "Missing 'success' field"
            assert data["success"] == False, "Success should be False for validation error"
            assert "error" in data, "Missing 'error' field"
            assert "error_code" in data, "Missing 'error_code' field"
            assert "status_code" in data, "Missing 'status_code' field"
            assert "timestamp" in data, "Missing 'timestamp' field"
            assert data["status_code"] == 400, "Status code should be 400 for validation error"
            
            print("✅ Validation error response format is correct")
            
        except Exception as e:
            print(f"❌ Validation error response format error: {e}")
    
    def run_all_tests(self):
        """Run all response format tests"""
        print("🚀 Starting standardized response format tests...\n")
        
        # Test basic endpoints
        self.test_health_check()
        print()
        
        # Test authentication
        self.test_login_endpoint("hr")
        print()
        self.test_login_endpoint("manager")
        print()
        
        # Test dashboard endpoints
        self.test_dashboard_stats("hr")
        print()
        
        # Test applications endpoint
        self.test_applications_endpoint("manager")
        print()
        
        # Test error responses
        self.test_invalid_endpoint()
        print()
        self.test_validation_error()
        print()
        
        print("✅ All standardized response format tests completed!")

def main():
    """Main test function"""
    print("=" * 60)
    print("STANDARDIZED API RESPONSE FORMAT TESTS")
    print("=" * 60)
    print()
    
    tester = ResponseTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("Check the output above for detailed results.")
    print("All responses should follow the standardized format:")
    print("- success: boolean")
    print("- data: object (for successful responses)")
    print("- message: string (optional)")
    print("- error: string (for error responses)")
    print("- error_code: string (for error responses)")
    print("- timestamp: string (ISO format)")

if __name__ == "__main__":
    main()