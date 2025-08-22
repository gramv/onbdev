#!/usr/bin/env python3
"""
Comprehensive Testing Script for Professional Job Application Form
Tests all components, features, and user flows
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Test configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class JobApplicationTester:
    def __init__(self):
        self.results = {
            "component_tests": [],
            "api_tests": [],
            "performance_metrics": [],
            "accessibility_checks": [],
            "mobile_tests": [],
            "edge_cases": [],
            "errors": [],
            "warnings": []
        }
        self.test_property_id = "test-property"
        
    def log(self, category: str, test: str, status: str, details: str = ""):
        """Log test results"""
        timestamp = datetime.now().isoformat()
        result = {
            "test": test,
            "status": status,
            "details": details,
            "timestamp": timestamp
        }
        
        if category in self.results:
            self.results[category].append(result)
            
        # Print to console with color coding
        color = "\033[92m" if status == "PASS" else "\033[91m" if status == "FAIL" else "\033[93m"
        reset = "\033[0m"
        print(f"{color}[{status}]{reset} {test}: {details}")
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("\n" + "="*50)
        print("TESTING API ENDPOINTS")
        print("="*50)
        
        # Test property info endpoint
        try:
            resp = requests.get(f"{BASE_URL}/api/properties/{self.test_property_id}/info")
            if resp.status_code == 404:
                # Create test property
                self.create_test_property()
                resp = requests.get(f"{BASE_URL}/api/properties/{self.test_property_id}/info")
            
            if resp.status_code == 200:
                self.log("api_tests", "Property Info Endpoint", "PASS", 
                        f"Retrieved property info successfully")
            else:
                self.log("api_tests", "Property Info Endpoint", "FAIL", 
                        f"Status code: {resp.status_code}")
        except Exception as e:
            self.log("api_tests", "Property Info Endpoint", "FAIL", str(e))
            
        # Test application submission endpoint
        try:
            test_data = self.get_test_application_data()
            resp = requests.post(
                f"{BASE_URL}/api/job-applications/submit",
                json=test_data
            )
            if resp.status_code in [200, 201]:
                self.log("api_tests", "Application Submit Endpoint", "PASS",
                        "Application submitted successfully")
            else:
                self.log("api_tests", "Application Submit Endpoint", "FAIL",
                        f"Status code: {resp.status_code}, Response: {resp.text[:200]}")
        except Exception as e:
            self.log("api_tests", "Application Submit Endpoint", "FAIL", str(e))
            
    def create_test_property(self):
        """Create a test property for testing"""
        property_data = {
            "id": self.test_property_id,
            "name": "Test Hotel Property",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "phone": "(555) 123-4567",
            "is_accepting_applications": True,
            "departments_and_positions": {
                "Front Desk": ["Receptionist", "Concierge", "Night Auditor"],
                "Housekeeping": ["Room Attendant", "Housekeeping Supervisor", "Laundry Attendant"],
                "Food & Beverage": ["Server", "Bartender", "Host/Hostess", "Line Cook"],
                "Maintenance": ["Maintenance Technician", "Grounds Keeper"],
                "Management": ["Assistant Manager", "Department Supervisor"]
            }
        }
        
        try:
            # Try to create property via admin endpoint if available
            resp = requests.post(f"{BASE_URL}/api/admin/properties", json=property_data)
            if resp.status_code in [200, 201]:
                self.log("api_tests", "Create Test Property", "PASS", "Test property created")
            else:
                self.log("api_tests", "Create Test Property", "WARN", 
                        f"Could not create property: {resp.status_code}")
        except:
            self.log("api_tests", "Create Test Property", "WARN", 
                    "Admin endpoint not available")
    
    def get_test_application_data(self) -> Dict:
        """Generate test application data"""
        return {
            "property_id": self.test_property_id,
            "personal_info": {
                "first_name": "Test",
                "middle_name": "Middle",
                "last_name": "User",
                "email": "test@example.com",
                "phone": "(555) 987-6543",
                "ssn": "123-45-6789",
                "date_of_birth": "1990-01-15",
                "address": "456 Test Ave",
                "city": "Test City",
                "state": "CA",
                "zip_code": "90210",
                "emergency_contact": {
                    "name": "Emergency Contact",
                    "relationship": "Spouse",
                    "phone": "(555) 111-2222"
                }
            },
            "position_availability": {
                "desired_position": "Receptionist",
                "department": "Front Desk",
                "desired_pay": "20.00",
                "employment_type": "full-time",
                "shift_preference": "day",
                "start_date": "2025-02-01",
                "availability": {
                    "monday": {"available": True, "start": "08:00", "end": "17:00"},
                    "tuesday": {"available": True, "start": "08:00", "end": "17:00"},
                    "wednesday": {"available": True, "start": "08:00", "end": "17:00"},
                    "thursday": {"available": True, "start": "08:00", "end": "17:00"},
                    "friday": {"available": True, "start": "08:00", "end": "17:00"},
                    "saturday": {"available": False},
                    "sunday": {"available": False}
                }
            },
            "employment_history": [
                {
                    "employer": "Previous Hotel",
                    "position": "Front Desk Agent",
                    "start_date": "2020-01-15",
                    "end_date": "2024-12-31",
                    "reason_for_leaving": "Career advancement",
                    "supervisor": "Jane Smith",
                    "phone": "(555) 333-4444",
                    "may_contact": True
                }
            ],
            "education_skills": {
                "highest_education": "associate",
                "school_name": "Community College",
                "graduation_year": "2019",
                "certifications": ["CPR Certified", "First Aid"],
                "skills": ["Customer Service", "Microsoft Office", "Bilingual (English/Spanish)"],
                "languages": ["English", "Spanish"]
            },
            "additional_info": {
                "has_criminal_record": False,
                "can_provide_documentation": True,
                "agrees_to_background_check": True,
                "references": [
                    {
                        "name": "Reference One",
                        "relationship": "Former Manager",
                        "phone": "(555) 444-5555",
                        "email": "ref1@example.com"
                    },
                    {
                        "name": "Reference Two",
                        "relationship": "Colleague",
                        "phone": "(555) 666-7777",
                        "email": "ref2@example.com"
                    }
                ]
            },
            "voluntary_self_id": {
                "veteran_status": "not_veteran",
                "disability_status": "no",
                "gender": "prefer_not_to_say",
                "ethnicity": "prefer_not_to_say"
            },
            "consent": {
                "signature": "Test User",
                "date": datetime.now().isoformat(),
                "agrees_to_terms": True,
                "agrees_to_background_check": True,
                "certifies_information_true": True
            }
        }
    
    def test_frontend_components(self):
        """Test frontend component loading and functionality"""
        print("\n" + "="*50)
        print("TESTING FRONTEND COMPONENTS")
        print("="*50)
        
        # Test main application form route
        try:
            resp = requests.get(f"{FRONTEND_URL}/apply/{self.test_property_id}")
            if resp.status_code == 200:
                self.log("component_tests", "Main Application Form", "PASS",
                        "Form loads successfully")
            else:
                self.log("component_tests", "Main Application Form", "FAIL",
                        f"Status code: {resp.status_code}")
        except Exception as e:
            self.log("component_tests", "Main Application Form", "FAIL", str(e))
            
        # Component checklist
        components = [
            "PersonalInformationStep",
            "PositionAvailabilityStep", 
            "EmploymentHistoryStep",
            "EducationSkillsStep",
            "AdditionalInformationStep",
            "ReviewConsentStep",
            "VoluntarySelfIdentificationStep"
        ]
        
        for component in components:
            # Since we can't directly test React components from Python,
            # we'll mark them for manual verification
            self.log("component_tests", f"{component} Component", "INFO",
                    "Requires browser testing for full validation")
    
    def test_performance(self):
        """Test performance metrics"""
        print("\n" + "="*50)
        print("TESTING PERFORMANCE")
        print("="*50)
        
        # Test API response times
        endpoints = [
            f"/api/properties/{self.test_property_id}/info",
            "/api/health"
        ]
        
        for endpoint in endpoints:
            try:
                start = time.time()
                resp = requests.get(f"{BASE_URL}{endpoint}")
                elapsed = (time.time() - start) * 1000  # Convert to ms
                
                if elapsed < 200:
                    self.log("performance_metrics", f"{endpoint} Response Time", "PASS",
                            f"{elapsed:.2f}ms (target: <200ms)")
                else:
                    self.log("performance_metrics", f"{endpoint} Response Time", "WARN",
                            f"{elapsed:.2f}ms (target: <200ms)")
                            
            except Exception as e:
                self.log("performance_metrics", f"{endpoint} Response Time", "FAIL", str(e))
    
    def test_mobile_responsiveness(self):
        """Test mobile responsiveness features"""
        print("\n" + "="*50)
        print("TESTING MOBILE RESPONSIVENESS")
        print("="*50)
        
        # These tests require browser automation, so we'll document what needs testing
        breakpoints = ["320px", "375px", "768px", "1024px", "1440px"]
        
        for breakpoint in breakpoints:
            self.log("mobile_tests", f"Breakpoint {breakpoint}", "INFO",
                    "Requires browser testing with viewport resize")
        
        # Mobile features to test
        mobile_features = [
            "Touch target size (44px minimum)",
            "Swipe navigation between steps",
            "Bottom navigation bar visibility",
            "Mobile-optimized select dropdowns",
            "Virtual keyboard handling"
        ]
        
        for feature in mobile_features:
            self.log("mobile_tests", feature, "INFO",
                    "Requires manual mobile device or emulator testing")
    
    def test_accessibility(self):
        """Test accessibility compliance"""
        print("\n" + "="*50)
        print("TESTING ACCESSIBILITY")
        print("="*50)
        
        # Accessibility checks
        checks = [
            "WCAG 2.1 AA Compliance",
            "Keyboard Navigation (Tab order)",
            "Screen Reader Compatibility",
            "Focus Management",
            "Color Contrast (4.5:1 minimum)",
            "Form Labels and ARIA attributes",
            "Error Message Clarity",
            "Skip Links"
        ]
        
        for check in checks:
            self.log("accessibility_checks", check, "INFO",
                    "Requires automated accessibility testing tools (axe, WAVE)")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n" + "="*50)
        print("TESTING EDGE CASES")
        print("="*50)
        
        # Test invalid data submission
        try:
            invalid_data = {"invalid": "data"}
            resp = requests.post(
                f"{BASE_URL}/api/job-applications/submit",
                json=invalid_data
            )
            if resp.status_code >= 400:
                self.log("edge_cases", "Invalid Data Rejection", "PASS",
                        f"Server properly rejects invalid data: {resp.status_code}")
            else:
                self.log("edge_cases", "Invalid Data Rejection", "FAIL",
                        "Server accepted invalid data")
        except Exception as e:
            self.log("edge_cases", "Invalid Data Rejection", "FAIL", str(e))
        
        # Test empty submission
        try:
            resp = requests.post(
                f"{BASE_URL}/api/job-applications/submit",
                json={}
            )
            if resp.status_code >= 400:
                self.log("edge_cases", "Empty Data Rejection", "PASS",
                        f"Server properly rejects empty data: {resp.status_code}")
            else:
                self.log("edge_cases", "Empty Data Rejection", "FAIL",
                        "Server accepted empty data")
        except Exception as e:
            self.log("edge_cases", "Empty Data Rejection", "FAIL", str(e))
        
        # Additional edge cases to test manually
        manual_edge_cases = [
            "Network interruption during submission",
            "Browser refresh mid-form",
            "Multiple browser tabs with same form",
            "Session expiration handling",
            "Draft recovery after browser crash",
            "Concurrent form edits"
        ]
        
        for case in manual_edge_cases:
            self.log("edge_cases", case, "INFO",
                    "Requires manual testing or browser automation")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*50)
        print("TEST REPORT SUMMARY")
        print("="*50)
        
        # Calculate statistics
        total_tests = 0
        passed = 0
        failed = 0
        warnings = 0
        info = 0
        
        for category, tests in self.results.items():
            if isinstance(tests, list):
                for test in tests:
                    total_tests += 1
                    if test["status"] == "PASS":
                        passed += 1
                    elif test["status"] == "FAIL":
                        failed += 1
                    elif test["status"] == "WARN":
                        warnings += 1
                    elif test["status"] == "INFO":
                        info += 1
        
        # Print summary
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"ℹ️  Info/Manual: {info}")
        
        if total_tests > 0:
            success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
            print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        # Write detailed report to file
        report_file = "job_application_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed report saved to: {report_file}")
        
        return self.results
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*50)
        print("PROFESSIONAL JOB APPLICATION FORM")
        print("COMPREHENSIVE TESTING SUITE")
        print("="*50)
        print(f"Started at: {datetime.now().isoformat()}")
        
        # Run test suites
        self.test_api_endpoints()
        self.test_frontend_components()
        self.test_performance()
        self.test_mobile_responsiveness()
        self.test_accessibility()
        self.test_edge_cases()
        
        # Generate report
        return self.generate_report()

def main():
    """Main test execution"""
    tester = JobApplicationTester()
    
    try:
        # Check if servers are running
        try:
            requests.get(BASE_URL, timeout=2)
            print("✅ Backend server is running")
        except:
            print("❌ Backend server is not running on port 8000")
            print("Please start it with: python3 -m uvicorn app.main_enhanced:app --port 8000")
            
        try:
            requests.get(FRONTEND_URL, timeout=2)
            print("✅ Frontend server is running")
        except:
            print("❌ Frontend server is not running on port 3000")
            print("Please start it with: npm run dev")
        
        # Run tests
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if any(test["status"] == "FAIL" for tests in results.values() 
               if isinstance(tests, list) for test in tests):
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()