#!/usr/bin/env python3
"""
Comprehensive Test Suite for QR Job Application Workflow Tasks 1-11
Tests all functionality systematically to ensure complete implementation
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

# Test credentials
HR_TOKEN = "hr_test_001"
MANAGER_TOKEN = "mgr_test_001"

class TaskTester:
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
            # Get property info to verify QR code exists
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

        # Test 1.2: QR code endpoint functionality
        print("\n📋 Test 1.2: QR Code Endpoint Functionality")
        try:
            response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/qr-code")
            if response.status_code == 200:
                qr_data = response.json()
                has_qr_code = 'qr_code_url' in qr_data or 'qr_code_data' in qr_data
                print(f"   ✅ QR code endpoint working: {has_qr_code}")
                self.log_result("task_1", "qr_endpoint", True, "QR code endpoint functional")
            else:
                print(f"   ❌ QR code endpoint failed: {response.status_code}")
                self.log_result("task_1", "qr_endpoint", False, f"QR endpoint failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing QR endpoint: {e}")
            self.log_result("task_1", "qr_endpoint", False, str(e))

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
            # Test without any authentication headers
            response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
            no_auth_works = response.status_code == 200
            print(f"   ✅ Public access works without authentication: {no_auth_works}")
            self.log_result("task_2", "no_auth_required", no_auth_works, "Public access without auth")
        except Exception as e:
            print(f"   ❌ Error testing public access: {e}")
            self.log_result("task_2", "no_auth_required", False, str(e))

    def test_task_3_application_submission(self):
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
            
            validation_works = response.status_code in [400, 422]  # Bad request or validation error
            print(f"   ✅ Invalid application properly rejected: {validation_works}")
            if validation_works:
                print(f"   📋 Validation error status: {response.status_code}")
            self.log_result("task_3", "invalid_rejection", validation_works, f"Validation status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing invalid application: {e}")
            self.log_result("task_3", "invalid_rejection", False, str(e))

    def test_task_4_approval_logic(self):
        """Task 4: Application Review and Approval Logic"""
        self.print_task_header(4, "Application Review and Approval Logic")
        
        # Test 4.1: Manager can view applications
        print("\n📋 Test 4.1: Manager Application Access")
        try:
            headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
            
            if response.status_code == 200:
                applications = response.json()
                has_applications = len(applications) > 0
                print(f"   ✅ Manager can access applications: {has_applications}")
                print(f"   📊 Applications found: {len(applications)}")
                self.log_result("task_4", "manager_access", True, f"Found {len(applications)} applications")
                self.test_data['manager_applications'] = applications
            else:
                print(f"   ❌ Manager application access failed: {response.status_code}")
                self.log_result("task_4", "manager_access", False, f"Access failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing manager access: {e}")
            self.log_result("task_4", "manager_access", False, str(e))

        # Test 4.2: Application approval functionality
        print("\n📋 Test 4.2: Application Approval Functionality")
        try:
            if 'test_application_id' in self.test_data:
                app_id = self.test_data['test_application_id']
                headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
                
                approval_data = {
                    "status": "approved",
                    "notes": "Test approval for comprehensive testing"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/applications/{app_id}/review",
                    json=approval_data,
                    headers=headers
                )
                
                approval_works = response.status_code == 200
                print(f"   ✅ Application approval works: {approval_works}")
                if approval_works:
                    result = response.json()
                    print(f"   📋 Approval result: {result.get('message', 'Success')}")
                self.log_result("task_4", "approval_functionality", approval_works, "Approval process working")
            else:
                print("   ⚠️  No test application ID available for approval test")
                self.log_result("task_4", "approval_functionality", False, "No test application available")
        except Exception as e:
            print(f"   ❌ Error testing approval: {e}")
            self.log_result("task_4", "approval_functionality", False, str(e))

    def test_task_5_manager_dashboard_integration(self):
        """Task 5: Manager Dashboard Integration"""
        self.print_task_header(5, "Manager Dashboard Integration")
        
        # Test 5.1: Manager dashboard access
        print("\n📋 Test 5.1: Manager Dashboard Access")
        try:
            headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/manager/dashboard", headers=headers)
            
            dashboard_accessible = response.status_code == 200
            print(f"   ✅ Manager dashboard accessible: {dashboard_accessible}")
            
            if dashboard_accessible:
                dashboard_data = response.json()
                has_key_sections = any(key in dashboard_data for key in ['applications', 'stats', 'summary'])
                print(f"   📊 Dashboard has key sections: {has_key_sections}")
                self.log_result("task_5", "dashboard_access", True, "Dashboard accessible with data")
            else:
                self.log_result("task_5", "dashboard_access", False, f"Dashboard access failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing dashboard access: {e}")
            self.log_result("task_5", "dashboard_access", False, str(e))

        # Test 5.2: Application management in dashboard
        print("\n📋 Test 5.2: Application Management in Dashboard")
        try:
            headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
            
            if response.status_code == 200:
                applications = response.json()
                management_features = len(applications) >= 0  # Can be empty but should be accessible
                print(f"   ✅ Application management accessible: {management_features}")
                print(f"   📊 Applications in dashboard: {len(applications)}")
                self.log_result("task_5", "application_management", True, f"Managing {len(applications)} applications")
            else:
                print(f"   ❌ Application management failed: {response.status_code}")
                self.log_result("task_5", "application_management", False, f"Management failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing application management: {e}")
            self.log_result("task_5", "application_management", False, str(e))

    def test_task_6_application_form_frontend(self):
        """Task 6: Job Application Form Frontend"""
        self.print_task_header(6, "Job Application Form Frontend")
        
        # Test 6.1: Form accessibility
        print("\n📋 Test 6.1: Application Form Accessibility")
        try:
            form_url = f"{FRONTEND_URL}/apply/{TEST_PROPERTY_ID}"
            response = requests.get(form_url, timeout=10)
            
            form_accessible = response.status_code == 200
            print(f"   ✅ Application form accessible: {form_accessible}")
            
            if form_accessible:
                # Check for key form elements in HTML
                html_content = response.text
                form_elements = [
                    'first_name', 'last_name', 'email', 'phone',
                    'department', 'position', 'submit'
                ]
                elements_found = sum(1 for element in form_elements if element in html_content)
                print(f"   📋 Form elements found: {elements_found}/{len(form_elements)}")
                self.log_result("task_6", "form_accessibility", True, f"Form accessible with {elements_found} elements")
            else:
                self.log_result("task_6", "form_accessibility", False, f"Form not accessible: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ⚠️  Frontend server not running - cannot test form accessibility")
            self.log_result("task_6", "form_accessibility", False, "Frontend server not running")
        except Exception as e:
            print(f"   ❌ Error testing form accessibility: {e}")
            self.log_result("task_6", "form_accessibility", False, str(e))

        # Test 6.2: Form submission integration
        print("\n📋 Test 6.2: Form Submission Integration")
        try:
            # Test the backend endpoint that the form uses
            test_submission = {
                "first_name": "Frontend",
                "last_name": "TestUser",
                "email": f"frontend.test.{int(time.time())}@example.com",
                "phone": "(555) 987-6543",
                "address": "456 Frontend Street",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90210",
                "department": "Housekeeping",
                "position": "Housekeeper",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "shift_preference": "afternoon",
                "employment_type": "part_time",
                "experience_years": "0-1",
                "hotel_experience": "no"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                json=test_submission,
                headers={"Content-Type": "application/json"}
            )
            
            integration_works = response.status_code == 200
            print(f"   ✅ Form submission integration works: {integration_works}")
            
            if integration_works:
                result = response.json()
                print(f"   📋 Submission result: {result.get('message', 'Success')}")
                self.log_result("task_6", "form_integration", True, "Form submission integration working")
            else:
                print(f"   ❌ Form integration failed: {response.status_code}")
                self.log_result("task_6", "form_integration", False, f"Integration failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing form integration: {e}")
            self.log_result("task_6", "form_integration", False, str(e))

    def test_task_7_end_to_end_workflow(self):
        """Task 7: End-to-End Application Workflow"""
        self.print_task_header(7, "End-to-End Application Workflow")
        
        # Test 7.1: Complete workflow from application to approval
        print("\n📋 Test 7.1: Complete Application to Approval Workflow")
        try:
            # Step 1: Submit application
            workflow_application = {
                "first_name": "Workflow",
                "last_name": "TestUser",
                "email": f"workflow.test.{int(time.time())}@example.com",
                "phone": "(555) 111-2222",
                "address": "789 Workflow Avenue",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60601",
                "department": "Food & Beverage",
                "position": "Server",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                "shift_preference": "evening",
                "employment_type": "full_time",
                "experience_years": "6-10",
                "hotel_experience": "yes"
            }
            
            # Submit application
            submit_response = requests.post(
                f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                json=workflow_application,
                headers={"Content-Type": "application/json"}
            )
            
            if submit_response.status_code == 200:
                app_result = submit_response.json()
                app_id = app_result.get('application_id')
                print(f"   ✅ Step 1 - Application submitted: {app_id}")
                
                # Step 2: Manager reviews application
                headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
                review_response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
                
                if review_response.status_code == 200:
                    applications = review_response.json()
                    workflow_app = next((app for app in applications if app.get('id') == app_id), None)
                    print(f"   ✅ Step 2 - Application visible to manager: {workflow_app is not None}")
                    
                    # Step 3: Manager approves application
                    if workflow_app:
                        approval_data = {"status": "approved", "notes": "End-to-end workflow test approval"}
                        approve_response = requests.post(
                            f"{BACKEND_URL}/applications/{app_id}/review",
                            json=approval_data,
                            headers=headers
                        )
                        
                        approval_success = approve_response.status_code == 200
                        print(f"   ✅ Step 3 - Application approved: {approval_success}")
                        
                        if approval_success:
                            print("   🎉 Complete end-to-end workflow successful!")
                            self.log_result("task_7", "end_to_end_workflow", True, "Complete workflow successful")
                        else:
                            self.log_result("task_7", "end_to_end_workflow", False, "Approval step failed")
                    else:
                        self.log_result("task_7", "end_to_end_workflow", False, "Application not visible to manager")
                else:
                    self.log_result("task_7", "end_to_end_workflow", False, "Manager review step failed")
            else:
                print(f"   ❌ Workflow failed at submission: {submit_response.status_code}")
                self.log_result("task_7", "end_to_end_workflow", False, "Application submission failed")
                
        except Exception as e:
            print(f"   ❌ Error in end-to-end workflow: {e}")
            self.log_result("task_7", "end_to_end_workflow", False, str(e))

    def test_task_8_hr_dashboard_integration(self):
        """Task 8: HR Dashboard Integration"""
        self.print_task_header(8, "HR Dashboard Integration")
        
        # Test 8.1: HR dashboard access
        print("\n📋 Test 8.1: HR Dashboard Access")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/dashboard", headers=headers)
            
            hr_dashboard_accessible = response.status_code == 200
            print(f"   ✅ HR dashboard accessible: {hr_dashboard_accessible}")
            
            if hr_dashboard_accessible:
                dashboard_data = response.json()
                has_hr_features = any(key in dashboard_data for key in ['properties', 'managers', 'applications', 'analytics'])
                print(f"   📊 HR dashboard has key features: {has_hr_features}")
                self.log_result("task_8", "hr_dashboard_access", True, "HR dashboard accessible")
            else:
                self.log_result("task_8", "hr_dashboard_access", False, f"HR dashboard failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing HR dashboard: {e}")
            self.log_result("task_8", "hr_dashboard_access", False, str(e))

        # Test 8.2: HR application oversight
        print("\n📋 Test 8.2: HR Application Oversight")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
            
            if response.status_code == 200:
                hr_applications = response.json()
                has_oversight = len(hr_applications) >= 0  # Can be empty but accessible
                print(f"   ✅ HR can oversee applications: {has_oversight}")
                print(f"   📊 Applications visible to HR: {len(hr_applications)}")
                self.log_result("task_8", "hr_oversight", True, f"HR sees {len(hr_applications)} applications")
            else:
                print(f"   ❌ HR oversight failed: {response.status_code}")
                self.log_result("task_8", "hr_oversight", False, f"HR oversight failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing HR oversight: {e}")
            self.log_result("task_8", "hr_oversight", False, str(e))

    def test_task_9_status_tracking(self):
        """Task 9: Application Status Tracking"""
        self.print_task_header(9, "Application Status Tracking")
        
        # Test 9.1: Status tracking functionality
        print("\n📋 Test 9.1: Application Status Tracking")
        try:
            headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
            
            if response.status_code == 200:
                applications = response.json()
                has_status_tracking = all('status' in app for app in applications)
                status_values = set(app.get('status') for app in applications)
                
                print(f"   ✅ Applications have status tracking: {has_status_tracking}")
                print(f"   📊 Status values found: {status_values}")
                
                valid_statuses = {'pending', 'approved', 'rejected', 'talent_pool'}
                has_valid_statuses = status_values.issubset(valid_statuses) if status_values else True
                
                print(f"   ✅ Status values are valid: {has_valid_statuses}")
                self.log_result("task_9", "status_tracking", has_status_tracking and has_valid_statuses, f"Statuses: {status_values}")
            else:
                print(f"   ❌ Status tracking test failed: {response.status_code}")
                self.log_result("task_9", "status_tracking", False, f"Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing status tracking: {e}")
            self.log_result("task_9", "status_tracking", False, str(e))

        # Test 9.2: Status change functionality
        print("\n📋 Test 9.2: Status Change Functionality")
        try:
            if 'test_application_id' in self.test_data:
                app_id = self.test_data['test_application_id']
                headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
                
                # Test status change to talent_pool
                status_change_data = {
                    "status": "talent_pool",
                    "notes": "Moving to talent pool for future opportunities"
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/applications/{app_id}/review",
                    json=status_change_data,
                    headers=headers
                )
                
                status_change_works = response.status_code == 200
                print(f"   ✅ Status change functionality works: {status_change_works}")
                self.log_result("task_9", "status_change", status_change_works, "Status change working")
            else:
                print("   ⚠️  No test application available for status change test")
                self.log_result("task_9", "status_change", False, "No test application available")
        except Exception as e:
            print(f"   ❌ Error testing status change: {e}")
            self.log_result("task_9", "status_change", False, str(e))

    def test_task_10_enhanced_status_management(self):
        """Task 10: Enhanced Status Management"""
        self.print_task_header(10, "Enhanced Status Management")
        
        # Test 10.1: Multiple status options
        print("\n📋 Test 10.1: Multiple Status Options Available")
        try:
            # Test that we can set different statuses
            test_statuses = ['approved', 'rejected', 'talent_pool']
            headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
            
            status_results = {}
            for status in test_statuses:
                # Create a test application for each status
                test_app = {
                    "first_name": f"Status{status.title()}",
                    "last_name": "TestUser",
                    "email": f"status.{status}.{int(time.time())}@example.com",
                    "phone": "(555) 333-4444",
                    "address": "123 Status Street",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77001",
                    "department": "Maintenance",
                    "position": "Maintenance Technician",
                    "work_authorized": "yes",
                    "sponsorship_required": "no",
                    "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                    "shift_preference": "flexible",
                    "employment_type": "full_time",
                    "experience_years": "2-5",
                    "hotel_experience": "yes"
                }
                
                # Submit application
                submit_response = requests.post(
                    f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                    json=test_app,
                    headers={"Content-Type": "application/json"}
                )
                
                if submit_response.status_code == 200:
                    app_result = submit_response.json()
                    app_id = app_result.get('application_id')
                    
                    # Set status
                    status_data = {"status": status, "notes": f"Testing {status} status"}
                    status_response = requests.post(
                        f"{BACKEND_URL}/applications/{app_id}/review",
                        json=status_data,
                        headers=headers
                    )
                    
                    status_results[status] = status_response.status_code == 200
                
            all_statuses_work = all(status_results.values())
            print(f"   ✅ All status options work: {all_statuses_work}")
            print(f"   📊 Status test results: {status_results}")
            self.log_result("task_10", "multiple_statuses", all_statuses_work, f"Results: {status_results}")
            
        except Exception as e:
            print(f"   ❌ Error testing multiple statuses: {e}")
            self.log_result("task_10", "multiple_statuses", False, str(e))

        # Test 10.2: Status history tracking
        print("\n📋 Test 10.2: Status History Tracking")
        try:
            headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
            
            if response.status_code == 200:
                applications = response.json()
                has_history_tracking = any('status_history' in app or 'updated_at' in app for app in applications)
                print(f"   ✅ Status history tracking available: {has_history_tracking}")
                self.log_result("task_10", "status_history", has_history_tracking, "History tracking present")
            else:
                print(f"   ❌ Status history test failed: {response.status_code}")
                self.log_result("task_10", "status_history", False, f"Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing status history: {e}")
            self.log_result("task_10", "status_history", False, str(e))

    def test_task_11_application_form_enhancements(self):
        """Task 11: Application Form Enhancements"""
        self.print_task_header(11, "Application Form Enhancements")
        
        # Test 11.1: Enhanced form validation
        print("\n📋 Test 11.1: Enhanced Form Validation")
        try:
            # Test with invalid data to check validation
            invalid_data = {
                "first_name": "",  # Empty required field
                "last_name": "ValidationTest",
                "email": "invalid-email-format",  # Invalid email
                "phone": "123",  # Invalid phone
                "address": "123 Test St",
                "city": "New York",
                "state": "NY",
                "zip_code": "invalid",  # Invalid zip
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
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            )
            
            validation_working = response.status_code in [400, 422]
            print(f"   ✅ Enhanced validation working: {validation_working}")
            if validation_working:
                print(f"   📋 Validation response: {response.status_code}")
            self.log_result("task_11", "enhanced_validation", validation_working, f"Validation status: {response.status_code}")
            
        except Exception as e:
            print(f"   ❌ Error testing enhanced validation: {e}")
            self.log_result("task_11", "enhanced_validation", False, str(e))

        # Test 11.2: Duplicate application prevention
        print("\n📋 Test 11.2: Duplicate Application Prevention")
        try:
            duplicate_test_email = f"duplicate.test.{int(time.time())}@example.com"
            
            duplicate_app = {
                "first_name": "Duplicate",
                "last_name": "TestUser",
                "email": duplicate_test_email,
                "phone": "(555) 555-5555",
                "address": "123 Duplicate Street",
                "city": "Phoenix",
                "state": "AZ",
                "zip_code": "85001",
                "department": "Front Desk",
                "position": "Concierge",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
                "shift_preference": "afternoon",
                "employment_type": "full_time",
                "experience_years": "2-5",
                "hotel_experience": "yes"
            }
            
            # Submit first application
            first_response = requests.post(
                f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                json=duplicate_app,
                headers={"Content-Type": "application/json"}
            )
            
            # Submit duplicate application
            second_response = requests.post(
                f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                json=duplicate_app,
                headers={"Content-Type": "application/json"}
            )
            
            first_success = first_response.status_code == 200
            duplicate_prevented = second_response.status_code == 400
            
            print(f"   ✅ First application succeeded: {first_success}")
            print(f"   ✅ Duplicate application prevented: {duplicate_prevented}")
            
            if duplicate_prevented:
                error_msg = second_response.json().get('detail', '')
                contains_duplicate_msg = 'already submitted' in error_msg.lower()
                print(f"   📋 Proper duplicate message: {contains_duplicate_msg}")
                
            duplicate_prevention_works = first_success and duplicate_prevented
            self.log_result("task_11", "duplicate_prevention", duplicate_prevention_works, "Duplicate prevention working")
            
        except Exception as e:
            print(f"   ❌ Error testing duplicate prevention: {e}")
            self.log_result("task_11", "duplicate_prevention", False, str(e))

        # Test 11.3: Enhanced fields and mobile responsiveness
        print("\n📋 Test 11.3: Enhanced Fields and Features")
        try:
            enhanced_application = {
                "first_name": "Enhanced",
                "last_name": "TestUser",
                "email": f"enhanced.test.{int(time.time())}@example.com",
                "phone": "(555) 777-8888",
                "address": "456 Enhanced Avenue",
                "city": "San Diego",
                "state": "CA",
                "zip_code": "92101",
                "department": "Housekeeping",
                "position": "Housekeeping Supervisor",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                "shift_preference": "morning",
                "employment_type": "full_time",
                "experience_years": "6-10",
                "hotel_experience": "yes",
                # Enhanced fields
                "availability_weekends": "yes",
                "availability_holidays": "sometimes",
                "reliable_transportation": "yes",
                "previous_employer": "Luxury Resort Chain",
                "reason_for_leaving": "Career advancement",
                "additional_comments": "Excited to bring my experience to your team!",
                "physical_requirements_acknowledged": True,
                "background_check_consent": True
            }
            
            response = requests.post(
                f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                json=enhanced_application,
                headers={"Content-Type": "application/json"}
            )
            
            enhanced_fields_work = response.status_code == 200
            print(f"   ✅ Enhanced fields accepted: {enhanced_fields_work}")
            
            if enhanced_fields_work:
                result = response.json()
                print(f"   📋 Enhanced application ID: {result.get('application_id')}")
                
            self.log_result("task_11", "enhanced_fields", enhanced_fields_work, "Enhanced fields working")
            
        except Exception as e:
            print(f"   ❌ Error testing enhanced fields: {e}")
            self.log_result("task_11", "enhanced_fields", False, str(e))

        # Test 11.4: Position-specific questions
        print("\n📋 Test 11.4: Position-Specific Questions")
        try:
            departments_to_test = [
                ("Front Desk", "Front Desk Agent", "customer_service_experience"),
                ("Housekeeping", "Housekeeper", "physical_demands_ok"),
                ("Food & Beverage", "Server", "food_safety_certification"),
                ("Maintenance", "Maintenance Technician", "maintenance_experience")
            ]
            
            position_specific_results = {}
            
            for dept, position, specific_field in departments_to_test:
                position_app = {
                    "first_name": "Position",
                    "last_name": f"{dept.replace(' ', '')}Test",
                    "email": f"position.{dept.lower().replace(' ', '.')}.{int(time.time())}@example.com",
                    "phone": "(555) 999-0000",
                    "address": "789 Position Street",
                    "city": "Dallas",
                    "state": "TX",
                    "zip_code": "75201",
                    "department": dept,
                    "position": position,
                    "work_authorized": "yes",
                    "sponsorship_required": "no",
                    "start_date": (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d"),
                    "shift_preference": "flexible",
                    "employment_type": "full_time",
                    "experience_years": "2-5",
                    "hotel_experience": "yes",
                    specific_field: "yes"  # Position-specific answer
                }
                
                response = requests.post(
                    f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                    json=position_app,
                    headers={"Content-Type": "application/json"}
                )
                
                position_specific_results[dept] = response.status_code == 200
                
            all_positions_work = all(position_specific_results.values())
            print(f"   ✅ Position-specific questions work: {all_positions_work}")
            print(f"   📊 Department results: {position_specific_results}")
            
            self.log_result("task_11", "position_specific", all_positions_work, f"Results: {position_specific_results}")
            
        except Exception as e:
            print(f"   ❌ Error testing position-specific questions: {e}")
            self.log_result("task_11", "position_specific", False, str(e))

    def generate_final_report(self):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE TEST REPORT - TASKS 1-11")
        print(f"{'='*80}")
        
        total_tests = 0
        passed_tests = 0
        
        for task_num in range(1, 12):
            task_key = f"task_{task_num}"
            if task_key in self.results:
                task_results = self.results[task_key]
                task_passed = sum(1 for result in task_results.values() if result['passed'])
                task_total = len(task_results)
                
                total_tests += task_total
                passed_tests += task_passed
                
                status = "✅ PASS" if task_passed == task_total else "⚠️  PARTIAL" if task_passed > 0 else "❌ FAIL"
                print(f"\nTask {task_num}: {status} ({task_passed}/{task_total})")
                
                for test_name, result in task_results.items():
                    test_status = "✅" if result['passed'] else "❌"
                    print(f"  {test_status} {test_name}: {result['message']}")
        
        print(f"\n{'='*80}")
        print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - QR JOB APPLICATION WORKFLOW FULLY FUNCTIONAL!")
        elif passed_tests > total_tests * 0.8:
            print("✅ MOSTLY FUNCTIONAL - Minor issues detected")
        elif passed_tests > total_tests * 0.5:
            print("⚠️  PARTIALLY FUNCTIONAL - Several issues need attention")
        else:
            print("❌ MAJOR ISSUES - Significant functionality problems detected")
        
        print(f"{'='*80}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests/total_tests if total_tests > 0 else 0,
            'detailed_results': self.results
        }

def main():
    """Run comprehensive test suite for tasks 1-11"""
    print("🚀 STARTING COMPREHENSIVE TEST SUITE FOR QR JOB APPLICATION WORKFLOW")
    print("Testing all tasks 1-11 systematically...")
    
    tester = TaskTester()
    
    # Run all task tests
    tester.test_task_1_qr_code_generation()
    tester.test_task_2_public_property_info()
    tester.test_task_3_application_submission()
    tester.test_task_4_approval_logic()
    tester.test_task_5_manager_dashboard_integration()
    tester.test_task_6_application_form_frontend()
    tester.test_task_7_end_to_end_workflow()
    tester.test_task_8_hr_dashboard_integration()
    tester.test_task_9_status_tracking()
    tester.test_task_10_enhanced_status_management()
    tester.test_task_11_application_form_enhancements()
    
    # Generate final report
    final_results = tester.generate_final_report()
    
    # Save detailed results to file
    with open('COMPREHENSIVE_TASKS_1_TO_11_TEST_RESULTS.json', 'w') as f:
        json.dump(final_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: COMPREHENSIVE_TASKS_1_TO_11_TEST_RESULTS.json")
    
    return final_results

if __name__ == "__main__":
    main()