#!/usr/bin/env python3
"""
Comprehensive Test Suite for Document Preview Endpoints
Hotel Employee Onboarding System

Tests all PDF preview endpoints to ensure they:
1. Return proper base64-encoded PDFs
2. Have correct response format (pdf field, filename field)
3. Generate valid PDF content
4. Handle edge cases appropriately

Test endpoints:
- POST /api/onboarding/{employee_id}/direct-deposit/generate-pdf
- POST /api/onboarding/{employee_id}/health-insurance/generate-pdf  
- POST /api/onboarding/{employee_id}/weapons-policy/generate-pdf
- POST /api/onboarding/{employee_id}/human-trafficking/generate-pdf
- POST /api/onboarding/{employee_id}/company-policies/generate-pdf
"""

import requests
import json
import base64
import io
from datetime import datetime
from PyPDF2 import PdfReader
import sys
import traceback

# Test configuration
BASE_URL = "http://localhost:8000"
EMPLOYEE_ID = "test-employee"

# Test data payloads for different forms
DIRECT_DEPOSIT_DATA = {
    "employee_data": {
        "name": "John Test Smith",
        "ssn": "123-45-6789",
        "account_type": "checking",
        "bank_name": "Test Bank of America",
        "routing_number": "123456789",
        "account_number": "987654321",
        "address": "123 Main St, Test City, CA 90210",
        "signature_date": datetime.now().isoformat()
    }
}

HEALTH_INSURANCE_DATA = {
    "employee_data": {
        "name": "Jane Test Doe",
        "employee_id": "EMP123456",
        "date_of_birth": "1990-01-15",
        "enrollment_choice": "enroll",
        "coverage_level": "employee_spouse",
        "dependents": [
            {
                "name": "John Doe Jr.",
                "relationship": "child",
                "date_of_birth": "2015-06-20"
            }
        ],
        "signature_date": datetime.now().isoformat()
    }
}

WEAPONS_POLICY_DATA = {
    "employee_data": {
        "name": "Mike Test Johnson", 
        "employee_id": "EMP789012",
        "position": "Front Desk Clerk",
        "department": "Guest Services",
        "hire_date": "2025-01-15",
        "signature_date": datetime.now().isoformat()
    }
}

HUMAN_TRAFFICKING_DATA = {
    "employee_data": {
        "name": "Sarah Test Wilson",
        "employee_id": "EMP345678",
        "position": "Housekeeper",
        "department": "Housekeeping",
        "signature_date": datetime.now().isoformat()
    }
}

COMPANY_POLICIES_DATA = {
    "employee_data": {
        "name": "Robert Test Brown",
        "employee_id": "EMP567890", 
        "position": "Maintenance Worker",
        "department": "Engineering",
        "hire_date": "2025-02-01",
        "signature_date": datetime.now().isoformat()
    }
}

class DocumentPreviewTester:
    def __init__(self):
        self.results = {}
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log(self, message):
        """Log test output with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def validate_pdf_response(self, response, endpoint_name):
        """Validate that response contains proper PDF data"""
        try:
            # Check status code
            if response.status_code != 200:
                return False, f"HTTP {response.status_code}: {response.text}"
                
            # Parse JSON response
            response_data = response.json()
            
            # Check response structure - expect nested data object
            if "data" not in response_data:
                return False, "Missing 'data' field in response"
                
            data = response_data["data"]
            
            # Check required fields in data object
            if "pdf" not in data:
                return False, "Missing 'pdf' field in data object"
                
            if "filename" not in data:
                return False, "Missing 'filename' field in data object"
                
            # Validate base64 PDF data
            pdf_base64 = data["pdf"]
            if not pdf_base64:
                return False, "Empty PDF data"
                
            # Attempt to decode base64
            try:
                pdf_bytes = base64.b64decode(pdf_base64)
            except Exception as e:
                return False, f"Invalid base64 encoding: {str(e)}"
                
            # Validate PDF format
            try:
                pdf_buffer = io.BytesIO(pdf_bytes)
                pdf_reader = PdfReader(pdf_buffer)
                
                # Check if PDF has pages
                num_pages = len(pdf_reader.pages)
                if num_pages == 0:
                    return False, "PDF has no pages"
                    
                # Try to extract text from first page to ensure it's not corrupted
                first_page = pdf_reader.pages[0]
                page_text = first_page.extract_text()
                
                return True, {
                    "filename": data["filename"],
                    "pdf_size": len(pdf_bytes),
                    "pages": num_pages,
                    "has_content": len(page_text.strip()) > 0,
                    "sample_text": page_text[:100] + "..." if len(page_text) > 100 else page_text
                }
                
            except Exception as e:
                return False, f"Invalid PDF format: {str(e)}"
                
        except Exception as e:
            return False, f"Response validation error: {str(e)}"
            
    def test_endpoint(self, endpoint_path, test_data, endpoint_name):
        """Test a single document preview endpoint"""
        self.log(f"\n{'='*60}")
        self.log(f"TESTING: {endpoint_name}")
        self.log(f"Endpoint: {endpoint_path}")
        self.log(f"{'='*60}")
        
        url = f"{BASE_URL}{endpoint_path}"
        
        try:
            # Test with complete data
            self.log("Test 1: Complete form data")
            response = requests.post(url, json=test_data)
            
            success, result = self.validate_pdf_response(response, endpoint_name)
            
            if success:
                self.log(f"✅ SUCCESS: {endpoint_name} with complete data")
                self.log(f"   Filename: {result['filename']}")
                self.log(f"   PDF Size: {result['pdf_size']} bytes")
                self.log(f"   Pages: {result['pages']}")
                self.log(f"   Has Content: {result['has_content']}")
                if result['sample_text']:
                    self.log(f"   Sample Text: {result['sample_text']}")
                self.passed_tests += 1
            else:
                self.log(f"❌ FAILED: {endpoint_name} with complete data")
                self.log(f"   Error: {result}")
                self.failed_tests += 1
                
            # Test with minimal data
            self.log("Test 2: Minimal form data")
            minimal_data = {"employee_data": {"name": "Test User"}}
            response = requests.post(url, json=minimal_data)
            
            success, result = self.validate_pdf_response(response, endpoint_name)
            
            if success:
                self.log(f"✅ SUCCESS: {endpoint_name} with minimal data")
                self.passed_tests += 1
            else:
                self.log(f"❌ FAILED: {endpoint_name} with minimal data")
                self.log(f"   Error: {result}")
                self.failed_tests += 1
                
            # Test with empty data (should still generate PDF)
            self.log("Test 3: Empty form data")
            empty_data = {"employee_data": {}}
            response = requests.post(url, json=empty_data)
            
            success, result = self.validate_pdf_response(response, endpoint_name)
            
            if success:
                self.log(f"✅ SUCCESS: {endpoint_name} with empty data")
                self.passed_tests += 1
            else:
                self.log(f"❌ FAILED: {endpoint_name} with empty data")
                self.log(f"   Error: {result}")
                self.failed_tests += 1
                
        except requests.exceptions.ConnectionError:
            self.log(f"❌ CONNECTION ERROR: Could not connect to {BASE_URL}")
            self.log("   Make sure the backend server is running on port 8000")
            self.failed_tests += 3
            
        except Exception as e:
            self.log(f"❌ UNEXPECTED ERROR testing {endpoint_name}: {str(e)}")
            self.log(f"   Traceback: {traceback.format_exc()}")
            self.failed_tests += 3
            
    def run_all_tests(self):
        """Run comprehensive tests for all document preview endpoints"""
        self.log("🚀 Starting comprehensive document preview endpoint tests")
        self.log(f"Target server: {BASE_URL}")
        self.log(f"Test employee ID: {EMPLOYEE_ID}")
        
        # Test each endpoint
        endpoints_to_test = [
            (f"/api/onboarding/{EMPLOYEE_ID}/direct-deposit/generate-pdf", 
             DIRECT_DEPOSIT_DATA, "Direct Deposit PDF"),
             
            (f"/api/onboarding/{EMPLOYEE_ID}/health-insurance/generate-pdf", 
             HEALTH_INSURANCE_DATA, "Health Insurance PDF"),
             
            (f"/api/onboarding/{EMPLOYEE_ID}/weapons-policy/generate-pdf", 
             WEAPONS_POLICY_DATA, "Weapons Policy PDF"),
             
            (f"/api/onboarding/{EMPLOYEE_ID}/human-trafficking/generate-pdf", 
             HUMAN_TRAFFICKING_DATA, "Human Trafficking PDF"),
             
            (f"/api/onboarding/{EMPLOYEE_ID}/company-policies/generate-pdf", 
             COMPANY_POLICIES_DATA, "Company Policies PDF")
        ]
        
        for endpoint_path, test_data, endpoint_name in endpoints_to_test:
            self.test_endpoint(endpoint_path, test_data, endpoint_name)
            
        # Print summary
        self.log(f"\n{'='*60}")
        self.log("TEST SUMMARY")
        self.log(f"{'='*60}")
        self.log(f"✅ Passed: {self.passed_tests}")
        self.log(f"❌ Failed: {self.failed_tests}")
        self.log(f"📊 Total: {self.passed_tests + self.failed_tests}")
        
        if self.failed_tests == 0:
            self.log("🎉 ALL TESTS PASSED! All document preview endpoints working correctly.")
            return True
        else:
            self.log(f"⚠️  {self.failed_tests} tests failed. Please check the endpoints.")
            return False

def main():
    """Main test execution"""
    print("Document Preview Endpoints Test Suite")
    print("Hotel Employee Onboarding System")
    print("="*60)
    
    tester = DocumentPreviewTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()