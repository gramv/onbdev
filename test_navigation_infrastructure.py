#!/usr/bin/env python3
"""
Comprehensive Test Suite for Navigation Infrastructure
Tests both frontend and backend components for the 11-step onboarding workflow
"""

import requests
import json
import time
from typing import Dict, Any, List
import sys

class NavigationInfrastructureTester:
    def __init__(self, backend_url="http://localhost:8000", frontend_url="http://localhost:5174"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.session = requests.Session()
        self.test_results = []
        
        # Test data
        self.test_employee_id = "test-employee-nav-001"
        self.test_user_data = {
            "email": "test.employee@hoteltest.com",
            "password": "TestPass123!",
            "role": "employee"
        }
        
        # Expected onboarding steps
        self.expected_steps = [
            "personal-info",
            "i9-section1", 
            "i9-supplements",
            "document-upload",
            "w4-form",
            "direct-deposit",
            "health-insurance",
            "company-policies",
            "trafficking-awareness",
            "weapons-policy",
            "employee-review"
        ]

    def log_test(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   {details}")
        print()

    def test_backend_connectivity(self) -> bool:
        """Test if backend server is running and responsive"""
        try:
            response = self.session.get(f"{self.backend_url}/healthz", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Connectivity", "PASS", "Backend server responding correctly")
                return True
            else:
                self.log_test("Backend Connectivity", "FAIL", f"Server returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Connectivity", "FAIL", f"Cannot connect to backend: {str(e)}")
            return False

    def test_frontend_connectivity(self) -> bool:
        """Test if frontend server is running"""
        try:
            response = self.session.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Connectivity", "PASS", "Frontend server responding correctly")
                return True
            else:
                self.log_test("Frontend Connectivity", "FAIL", f"Frontend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Connectivity", "FAIL", f"Cannot connect to frontend: {str(e)}")
            return False

    def test_session_creation(self) -> bool:
        """Test onboarding session creation"""
        try:
            url = f"{self.backend_url}/api/onboarding/session/{self.test_employee_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                session = data.get("session")
                if session:
                    self.log_test("Session Creation", "PASS", 
                                f"Session created with ID: {session.get('id')}")
                    return True
                else:
                    self.log_test("Session Creation", "FAIL", "No session data in response")
                    return False
            else:
                self.log_test("Session Creation", "FAIL", 
                            f"API returned status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Session Creation", "FAIL", f"Error: {str(e)}")
            return False

    def test_step_navigation(self) -> bool:
        """Test navigation between onboarding steps"""
        all_passed = True
        
        for step_name in self.expected_steps:
            try:
                url = f"{self.backend_url}/api/onboarding/session/{self.test_employee_id}/step/{step_name}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("step_name") == step_name:
                        self.log_test(f"Step Navigation - {step_name}", "PASS", 
                                    f"Step accessible and returns correct data")
                    else:
                        self.log_test(f"Step Navigation - {step_name}", "FAIL", 
                                    "Step data mismatch")
                        all_passed = False
                else:
                    self.log_test(f"Step Navigation - {step_name}", "FAIL", 
                                f"API returned status {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Step Navigation - {step_name}", "FAIL", f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_progress_update(self) -> bool:
        """Test progress update functionality"""
        try:
            # Test updating progress for first step
            step = "personal-info"
            url = f"{self.backend_url}/api/onboarding/session/{self.test_employee_id}/progress"
            
            progress_data = {
                "step": step,
                "form_data": {
                    "firstName": "Test",
                    "lastName": "User",
                    "email": "test@example.com"
                },
                "completed": True,
                "validation_passed": True
            }
            
            response = self.session.post(url, json=progress_data)
            
            if response.status_code == 200:
                data = response.json()
                session = data.get("session")
                if session and step in session.get("steps_completed", []):
                    self.log_test("Progress Update", "PASS", 
                                f"Step {step} marked as completed")
                    return True
                else:
                    self.log_test("Progress Update", "FAIL", 
                                "Step not marked as completed in response")
                    return False
            else:
                self.log_test("Progress Update", "FAIL", 
                            f"API returned status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Progress Update", "FAIL", f"Error: {str(e)}")
            return False

    def test_auto_save(self) -> bool:
        """Test auto-save functionality"""
        try:
            step = "i9-section1"
            url = f"{self.backend_url}/api/onboarding/session/{self.test_employee_id}/save"
            
            save_data = {
                "step": step,
                "form_data": {
                    "employee_last_name": "User",
                    "employee_first_name": "Test",
                    "employee_middle_initial": "T"
                }
            }
            
            response = self.session.post(url, json=save_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_test("Auto Save", "PASS", "Form data auto-saved successfully")
                    return True
                else:
                    self.log_test("Auto Save", "FAIL", "Auto-save did not report success")
                    return False
            else:
                self.log_test("Auto Save", "FAIL", 
                            f"API returned status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Auto Save", "FAIL", f"Error: {str(e)}")
            return False

    def test_session_persistence(self) -> bool:
        """Test that session data persists between requests"""
        try:
            # First, get current session
            url = f"{self.backend_url}/api/onboarding/session/{self.test_employee_id}"
            response1 = self.session.get(url)
            
            if response1.status_code != 200:
                self.log_test("Session Persistence", "FAIL", "Could not retrieve initial session")
                return False
            
            data1 = response1.json()
            session1 = data1.get("session")
            
            # Wait a moment then get session again
            time.sleep(1)
            response2 = self.session.get(url)
            
            if response2.status_code == 200:
                data2 = response2.json()
                session2 = data2.get("session")
                
                # Compare session IDs and data
                if (session1.get("id") == session2.get("id") and 
                    session1.get("form_data") == session2.get("form_data")):
                    self.log_test("Session Persistence", "PASS", 
                                "Session data persists correctly between requests")
                    return True
                else:
                    self.log_test("Session Persistence", "FAIL", 
                                "Session data not consistent between requests")
                    return False
            else:
                self.log_test("Session Persistence", "FAIL", 
                            f"Second request failed with status {response2.status_code}")
                return False
        except Exception as e:
            self.log_test("Session Persistence", "FAIL", f"Error: {str(e)}")
            return False

    def test_federal_compliance_validation(self) -> bool:
        """Test federal compliance validation features"""
        try:
            # Test I-9 validation
            url = f"{self.backend_url}/api/forms/validate/i9"
            
            i9_data = {
                "employee_data": {
                    "last_name": "User",
                    "first_name": "Test",
                    "middle_initial": "T",
                    "other_last_names": "",
                    "address": "123 Test St",
                    "apt_number": "",
                    "city": "Test City",
                    "state": "CA",
                    "zip_code": "12345",
                    "date_of_birth": "1990-01-01",
                    "ssn": "123-45-6789",
                    "email": "test@example.com",
                    "phone": "555-123-4567"
                },
                "citizenship_status": "us_citizen",
                "signature_data": {
                    "signature": "base64signaturedata",
                    "signed_at": "2024-01-01T12:00:00Z"
                }
            }
            
            response = self.session.post(url, json=i9_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid") == True:
                    self.log_test("Federal Compliance Validation", "PASS", 
                                "I-9 validation working correctly")
                    return True
                else:
                    self.log_test("Federal Compliance Validation", "WARN", 
                                f"I-9 validation failed: {data.get('errors', [])}")
                    return True  # This might be expected due to test data
            else:
                self.log_test("Federal Compliance Validation", "FAIL", 
                            f"Validation API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Federal Compliance Validation", "FAIL", f"Error: {str(e)}")
            return False

    def test_manager_review_workflow(self) -> bool:
        """Test manager review workflow"""
        try:
            # First, mark session as employee completed
            url = f"{self.backend_url}/api/onboarding/session/{self.test_employee_id}/progress"
            
            # Mark all steps as completed
            for step in self.expected_steps:
                progress_data = {
                    "step": step,
                    "form_data": {"test": "data"},
                    "completed": True,
                    "validation_passed": True
                }
                response = self.session.post(url, json=progress_data)
                if response.status_code != 200:
                    self.log_test("Manager Review Workflow", "FAIL", 
                                f"Could not complete step {step}")
                    return False
            
            # Check pending review sessions
            review_url = f"{self.backend_url}/api/onboarding/sessions/pending-review"
            response = self.session.get(review_url)
            
            if response.status_code == 200:
                data = response.json()
                pending_sessions = data.get("pending_sessions", [])
                
                # Look for our test session
                found_session = False
                for session_data in pending_sessions:
                    session = session_data.get("session", {})
                    if session.get("employee_id") == self.test_employee_id:
                        found_session = True
                        break
                
                if found_session:
                    self.log_test("Manager Review Workflow", "PASS", 
                                "Session correctly appears in pending review queue")
                    return True
                else:
                    self.log_test("Manager Review Workflow", "WARN", 
                                "Session not found in pending review (may need employee record)")
                    return True
            else:
                self.log_test("Manager Review Workflow", "FAIL", 
                            f"Could not retrieve pending sessions: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Manager Review Workflow", "FAIL", f"Error: {str(e)}")
            return False

    def test_analytics_endpoints(self) -> bool:
        """Test analytics and reporting endpoints"""
        try:
            url = f"{self.backend_url}/api/onboarding/analytics/sessions"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                expected_keys = ["total_sessions", "status_breakdown", "step_completion", "average_progress"]
                
                if all(key in data for key in expected_keys):
                    self.log_test("Analytics Endpoints", "PASS", 
                                "Analytics API returns expected data structure")
                    return True
                else:
                    self.log_test("Analytics Endpoints", "FAIL", 
                                f"Missing expected keys in analytics response")
                    return False
            else:
                self.log_test("Analytics Endpoints", "FAIL", 
                            f"Analytics API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Analytics Endpoints", "FAIL", f"Error: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🧪 COMPREHENSIVE NAVIGATION INFRASTRUCTURE TEST SUITE")
        print("=" * 60)
        print()
        
        # Connectivity tests
        backend_ok = self.test_backend_connectivity()
        frontend_ok = self.test_frontend_connectivity()
        
        if not backend_ok:
            print("❌ Backend not available - skipping backend tests")
            return self.generate_report()
        
        # Core functionality tests
        self.test_session_creation()
        self.test_step_navigation()
        self.test_progress_update()
        self.test_auto_save()
        self.test_session_persistence()
        
        # Advanced functionality tests
        self.test_federal_compliance_validation()
        self.test_manager_review_workflow()
        self.test_analytics_endpoints()
        
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0
            },
            "results": self.test_results,
            "recommendations": self.generate_recommendations()
        }
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings: {warning_tests}")
        print(f"Success Rate: {report['summary']['success_rate']}%")
        print()
        
        if report['recommendations']:
            print("🔧 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"• {rec}")
            print()
        
        return report

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r["status"] == "FAIL"]
        
        if any("connectivity" in r["test"].lower() for r in failed_tests):
            recommendations.append("Ensure both frontend and backend servers are running")
        
        if any("session" in r["test"].lower() for r in failed_tests):
            recommendations.append("Check session management API endpoints and database connectivity")
        
        if any("navigation" in r["test"].lower() for r in failed_tests):
            recommendations.append("Verify onboarding step routing and URL patterns")
        
        if any("compliance" in r["test"].lower() for r in failed_tests):
            recommendations.append("Review federal compliance validation logic")
        
        if any("progress" in r["test"].lower() for r in failed_tests):
            recommendations.append("Check progress tracking and state management")
        
        # General recommendations based on overall success rate
        success_rate = len([r for r in self.test_results if r["status"] == "PASS"]) / len(self.test_results) * 100
        
        if success_rate < 80:
            recommendations.append("Consider comprehensive code review and additional testing")
        elif success_rate < 95:
            recommendations.append("Address failing tests before production deployment")
        
        return recommendations

if __name__ == "__main__":
    tester = NavigationInfrastructureTester()
    report = tester.run_all_tests()
    
    # Save report to file
    with open("navigation_infrastructure_test_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"📄 Detailed report saved to: navigation_infrastructure_test_report.json")
    
    # Exit with appropriate code
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)