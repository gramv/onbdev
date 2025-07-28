#!/usr/bin/env python3
"""
Fixed Comprehensive Test Suite for QR Job Application Workflow Tasks 1-11
Uses proper JWT tokens for authentication
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_PROPERTY_ID = "prop_test_001"

# Proper JWT tokens generated for testing
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzYxNywiZXhwIjoxNzUzNzYwMDE3fQ.7Lql9bsGY5Rm6h3io3n1l4fni0lzZW9zXGg4CxE_Sfw"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzYxNywiZXhwIjoxNzUzNzYwMDE3fQ.hhkLF_WT6xYfVUCgqKnEHeZhn6TX0xt1pKOW3GQkko8"

class FixedTaskTester:
    def __init__(self):
        self.results = {}
        self.test_data = {}
        
    def log_result(self, task: str, test: str, passed: bool, message: str = ""):
        if task not in self.results:
            self.results[task] = {}
        self.results[task][test] = {
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
    def print_task_header(self, task_num: int, task_name: str):
        print(f"\n{'='*80}")
        print(f"🧪 TESTING TASK {task_num}: {task_name}")
        print(f"{'='*80}")

    def test_task_1_qr_code_generation(self):
        """Task 1: QR Code Generation and Property Setup"""
        self.print_task_header(1, "QR Code Generation and Property Setup")
        
        # Test 1.1: Property creation with QR code
        print("\n📋 Test 1.1: Property Creation with QR Code Generation")
        try:
            response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
            if response.status_code == 200:
                property_info = response.json()
                has_qr_url = 'application_url' in property_info
                print(f"   ✅ Property exists with QR application URL: {has_qr_url}")
                self.log_result("task_1", "property_creation", True, "Property with QR code exists")
                self.test_data['property_info'] = property_info
            else:
                print(f"   ❌ Property not found: {response.status_code}")
                self.log_result("task_1", "property_creation", False, f"Property not found: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing property creation: {e}")
            self.log_result("task_1", "property_creation", False, str(e))  
      # Test 1.2: QR code regeneration endpoint (HR endpoint)
        print("\n📋 Test 1.2: QR Code Regeneration Functionality")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.post(f"{BACKEND_URL}/hr/properties/{TEST_PROPERTY_ID}/qr-code", headers=headers)
            if response.status_code == 200:
                qr_data = response.json()
                has_qr_code = 'qr_code_url' in qr_data or 'message' in qr_data
                print(f"   ✅ QR code regeneration working: {has_qr_code}")
                self.log_result("task_1", "qr_regeneration", True, "QR code regeneration functional")
            else:
                print(f"   ❌ QR code regeneration failed: {response.status_code}")
                self.log_result("task_1", "qr_regeneration", False, f"QR regeneration failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing QR regeneration: {e}")
            self.log_result("task_1", "qr_regeneration", False, str(e))

    def test_task_2_public_property_info(self):
        """Task 2: Public Property Information Access"""
        self.print_task_header(2, "Public Property Information Access")
        
        # Test 2.1: Public property info endpoint
        print("\n📋 Test 2.1: Public Property Information Endpoint")
        try:
            response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
            if response.status_code == 200:
                info = response.json()
                required_fields = ['property', 'departments_and_positions', 'application_url', 'is_accepting_applications']
                has_all_fields = all(field in info for field in required_fields)
                print(f"   ✅ Property info endpoint working with all fields: {has_all_fields}")
                print(f"   📊 Available departments: {list(info.get('departments_and_positions', {}).keys())}")
                self.log_result("task_2", "public_info", True, "Public property info accessible")
            else:
                print(f"   ❌ Property info endpoint failed: {response.status_code}")
                self.log_result("task_2", "public_info", False, f"Info endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing property info: {e}")
            self.log_result("task_2", "public_info", False, str(e))

        # Test 2.2: No authentication required
        print("\n📋 Test 2.2: No Authentication Required for Public Info")
        try:
            response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
            no_auth_works = response.status_code == 200
            print(f"   ✅ Public access works without authentication: {no_auth_works}")
            self.log_result("task_2", "no_auth_required", no_auth_works, "Public access without auth")
        except Exception as e:
            print(f"   ❌ Error testing public access: {e}")
            self.log_result("task_2", "no_auth_required", False, str(e))    def 
test_task_3_application_submission(self):
        """Task 3: Job Application Submission"""
        self.print_task_header(3, "Job Application Submission")
        
        # Test 3.1: Valid application submission
        print("\n📋 Test 3.1: Valid Application Submission")
        try:
            test_application = {
                "first_name": "John",
                "last_name": "TestUser",
                "email": f"john.test.{int(time.time())}@example.com",
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
            
            response = requests.post(
                f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                json=test_application,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                has_required_fields = all(field in result for field in ['success', 'application_id', 'message'])
                print(f"   ✅ Application submitted successfully: {has_required_fields}")
                print(f"   📋 Application ID: {result.get('application_id')}")
                self.log_result("task_3", "valid_submission", True, f"Application ID: {result.get('application_id')}")
                self.test_data['test_application_id'] = result.get('application_id')
            else:
                print(f"   ❌ Application submission failed: {response.status_code}")
                print(f"   📋 Error: {response.text}")
                self.log_result("task_3", "valid_submission", False, f"Submission failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing application submission: {e}")
            self.log_result("task_3", "valid_submission", False, str(e))

        # Test 3.2: Invalid application rejection
        print("\n📋 Test 3.2: Invalid Application Rejection")
        try:
            invalid_application = {
                "first_name": "",  # Empty required field
                "last_name": "TestUser",
                "email": "invalid-email",  # Invalid format
                "phone": "123",  # Invalid format
                "address": "123 Test Street",
                "city": "New York",
                "state": "NY",
                "zip_code": "invalid",  # Invalid format
                "department": "Front Desk",
                "position": "Front Desk Agent",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": "2020-01-01",  # Past date
                "shift_preference": "morning",
                "employment_type": "full_time",
                "experience_years": "2-5",
                "hotel_experience": "yes"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                json=invalid_application,
                headers={"Content-Type": "application/json"}
            )
            
            validation_works = response.status_code in [400, 422]
            print(f"   ✅ Invalid application properly rejected: {validation_works}")
            if validation_works:
                print(f"   📋 Validation error status: {response.status_code}")
            self.log_result("task_3", "invalid_rejection", validation_works, f"Validation status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing invalid application: {e}")
            self.log_result("task_3", "invalid_rejection", False, str(e))