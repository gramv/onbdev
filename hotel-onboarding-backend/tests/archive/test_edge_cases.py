#!/usr/bin/env python3
"""
Edge Cases and Error Handling Test for Document Preview Endpoints
Hotel Employee Onboarding System

Tests edge cases including:
1. Invalid JSON payloads
2. Missing required fields
3. Malformed data structures
4. Non-existent employee IDs
5. Server error conditions
"""

import requests
import json
from datetime import datetime
import sys

# Test configuration
BASE_URL = "http://localhost:8000"

class EdgeCaseTester:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log(self, message):
        """Log test output with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_edge_case(self, endpoint_path, payload, test_description, expected_behavior):
        """Test a single edge case"""
        self.log(f"\nTesting: {test_description}")
        self.log(f"Endpoint: {endpoint_path}")
        self.log(f"Expected: {expected_behavior}")
        
        url = f"{BASE_URL}{endpoint_path}"
        
        try:
            if payload == "INVALID_JSON":
                # Send invalid JSON
                response = requests.post(url, data="invalid json data", 
                                       headers={"Content-Type": "application/json"})
            elif payload == "NO_CONTENT_TYPE":
                # Send without content-type header
                response = requests.post(url, data='{"employee_data": {}}')
            else:
                # Send normal request
                response = requests.post(url, json=payload)
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check if response is what we expect
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "data" in data and "pdf" in data["data"]:
                        self.log("✅ SUCCESS: Generated PDF successfully despite edge case")
                        self.passed_tests += 1
                    else:
                        self.log("❌ FAILED: Invalid response structure")
                        self.failed_tests += 1
                except json.JSONDecodeError:
                    self.log("❌ FAILED: Invalid JSON response")
                    self.failed_tests += 1
            elif response.status_code == 422:
                self.log("✅ SUCCESS: Properly rejected malformed request (422)")
                self.passed_tests += 1
            elif response.status_code == 400:
                self.log("✅ SUCCESS: Properly rejected bad request (400)")
                self.passed_tests += 1
            elif response.status_code == 500:
                self.log("⚠️  SERVER ERROR: 500 response - may indicate server issue")
                try:
                    error_data = response.json()
                    self.log(f"   Error details: {error_data}")
                except:
                    self.log(f"   Raw error: {response.text}")
                self.failed_tests += 1
            else:
                self.log(f"❓ UNEXPECTED: HTTP {response.status_code}")
                self.log(f"   Response: {response.text}")
                self.failed_tests += 1
                
        except requests.exceptions.ConnectionError:
            self.log("❌ CONNECTION ERROR: Could not connect to server")
            self.failed_tests += 1
        except Exception as e:
            self.log(f"❌ UNEXPECTED ERROR: {str(e)}")
            self.failed_tests += 1
            
    def run_edge_case_tests(self):
        """Run comprehensive edge case testing"""
        self.log("🚀 Starting Edge Case and Error Handling Tests")
        self.log(f"Target server: {BASE_URL}")
        
        # Test cases for each endpoint
        endpoints = [
            "direct-deposit", "health-insurance", "weapons-policy", 
            "human-trafficking", "company-policies"
        ]
        
        for endpoint in endpoints:
            endpoint_path = f"/api/onboarding/test-employee/{endpoint}/generate-pdf"
            
            self.log(f"\n{'='*60}")
            self.log(f"EDGE CASE TESTING: {endpoint.upper()}")
            self.log(f"{'='*60}")
            
            # Test 1: Valid empty payload
            self.test_edge_case(
                endpoint_path,
                {"employee_data": {}},
                "Empty employee data",
                "Should generate PDF with blank fields"
            )
            
            # Test 2: Missing employee_data key
            self.test_edge_case(
                endpoint_path,
                {},
                "Missing employee_data key",
                "Should generate PDF or handle gracefully"
            )
            
            # Test 3: Null employee_data
            self.test_edge_case(
                endpoint_path,
                {"employee_data": None},
                "Null employee data",
                "Should handle gracefully"
            )
            
            # Test 4: Invalid data types
            self.test_edge_case(
                endpoint_path,
                {"employee_data": "invalid_string"},
                "Invalid employee_data type (string instead of object)",
                "Should handle gracefully or reject"
            )
            
            # Test 5: Large payload
            large_data = {
                "employee_data": {
                    "name": "x" * 1000,  # Very long name
                    "notes": "Very long text " * 100,  # Very long notes
                    "invalid_field": "should be ignored"
                }
            }
            self.test_edge_case(
                endpoint_path,
                large_data,
                "Large payload with oversized fields",
                "Should handle large data gracefully"
            )
            
            # Test 6: Invalid JSON
            self.test_edge_case(
                endpoint_path,
                "INVALID_JSON",
                "Malformed JSON payload",
                "Should reject with 400 or 422"
            )
            
            # Test 7: Special characters in data
            special_chars_data = {
                "employee_data": {
                    "name": "José María Ñuñez-O'Connor <script>alert('xss')</script>",
                    "address": "123 Main St. & Co., Apt. #5B\n\"Second Line\"",
                    "notes": "Special chars: àáâãäåæçèéêë ñóôõö ùúûüý ¿¡ €£¥ ©®™"
                }
            }
            self.test_edge_case(
                endpoint_path,
                special_chars_data,
                "Special characters and potential XSS",
                "Should sanitize and handle safely"
            )
        
        # Test non-existent endpoint
        self.log(f"\n{'='*60}")
        self.log("TESTING NON-EXISTENT ENDPOINT")
        self.log(f"{'='*60}")
        
        self.test_edge_case(
            "/api/onboarding/test-employee/non-existent-form/generate-pdf",
            {"employee_data": {}},
            "Non-existent form endpoint",
            "Should return 404"
        )
        
        # Print summary
        self.log(f"\n{'='*60}")
        self.log("EDGE CASE TEST SUMMARY")
        self.log(f"{'='*60}")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Total: {self.passed_tests + self.failed_tests}")
        
        if self.failed_tests == 0:
            self.log("🎉 ALL EDGE CASE TESTS PASSED!")
            return True
        else:
            self.log(f"⚠️  {self.failed_tests} edge case tests failed.")
            return False

def main():
    """Main test execution"""
    print("Edge Case and Error Handling Test Suite")
    print("Hotel Employee Onboarding System")
    print("="*60)
    
    tester = EdgeCaseTester()
    success = tester.run_edge_case_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()