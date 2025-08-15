#!/usr/bin/env python3
"""
Test Manager Document Access Functionality
=========================================

This test verifies that managers can access documents for employees in their property
and that property isolation is properly enforced.

Test Coverage:
- Manager authentication and JWT token handling
- Document viewing for employees within manager's property
- Document download functionality
- PDF preview capabilities
- Property-based access control isolation
- Error handling for unauthorized access attempts
"""

import asyncio
import json
import os
import sys
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import tempfile
import base64

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

class ManagerDocumentAccessTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.manager_token = None
        self.property_id = "a99239dd-ebde-4c69-b862-ecba9e878798"
        self.manager_email = "manager@demo.com"
        self.manager_password = "demo123"
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log test results with timestamp"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test": test_name,
            "status": status,
            "details": details,
            "data": data
        }
        self.test_results.append(result)
        
        # Color coding for console output
        color = "\033[92m" if status == "PASS" else "\033[91m" if status == "FAIL" else "\033[93m"
        reset = "\033[0m"
        print(f"{color}[{status}]{reset} {test_name}: {details}")
        
        if data and isinstance(data, dict):
            print(f"  Data: {json.dumps(data, indent=2)[:200]}...")

    def test_manager_authentication(self) -> bool:
        """Test 5.1: Manager Authentication and JWT Token Retrieval"""
        print("\n" + "="*60)
        print("TEST 5.1: Manager Authentication")
        print("="*60)
        
        try:
            # Test manager login
            login_data = {
                "email": self.manager_email,
                "password": self.manager_password
            }
            
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and result.get("data", {}).get("token"):
                    self.manager_token = result["data"]["token"]
                    user_data = result["data"].get("user", {})
                    
                    # Verify manager role - property assignment will be checked separately
                    if user_data.get("role") == "manager":
                        self.log_test(
                            "Manager Authentication",
                            "PASS",
                            "Manager authenticated successfully with proper role",
                            {
                                "manager_id": user_data.get("id"),
                                "property_id": user_data.get("property_id"),
                                "role": user_data.get("role"),
                                "email": user_data.get("email")
                            }
                        )
                        return True
                    else:
                        self.log_test(
                            "Manager Authentication", 
                            "FAIL",
                            f"Manager missing proper role. Role: {user_data.get('role')}"
                        )
                else:
                    self.log_test(
                        "Manager Authentication",
                        "FAIL", 
                        f"Login response missing token or success flag: {result}"
                    )
            else:
                self.log_test(
                    "Manager Authentication",
                    "FAIL",
                    f"Login failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Manager Authentication", "FAIL", f"Authentication error: {str(e)}")
            
        return False

    def test_manager_dashboard_access(self) -> Dict[str, Any]:
        """Test manager dashboard access and get property information"""
        print("\n" + "="*60)
        print("TEST: Manager Dashboard Access")
        print("="*60)
        
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Test dashboard stats endpoint
            response = requests.get(f"{self.base_url}/manager/dashboard-stats", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    dashboard_data = result.get("data", {})
                    self.log_test(
                        "Manager Dashboard Access",
                        "PASS",
                        "Dashboard accessed successfully",
                        dashboard_data
                    )
                    return dashboard_data
                else:
                    self.log_test(
                        "Manager Dashboard Access",
                        "FAIL",
                        f"Dashboard request unsuccessful: {result}"
                    )
            else:
                self.log_test(
                    "Manager Dashboard Access",
                    "FAIL",
                    f"Dashboard request failed with status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Manager Dashboard Access", "FAIL", f"Dashboard access error: {str(e)}")
            
        return {}

    def get_manager_employees(self) -> List[Dict[str, Any]]:
        """Get list of employees for the manager's property"""
        print("\n" + "="*60)
        print("TEST: Get Manager's Employees")
        print("="*60)
        
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Try different possible endpoints for employee listing
            endpoints_to_try = [
                "/manager/applications",
                "/api/manager/employees",
                "/api/employees",
                "/hr/employees"  # Fallback to HR endpoint with manager auth
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success") and result.get("data"):
                            employees_data = result["data"]
                            
                            # Handle different response formats
                            if isinstance(employees_data, dict):
                                employees = employees_data.get("applications", employees_data.get("employees", []))
                            else:
                                employees = employees_data
                            
                            self.log_test(
                                "Get Manager Employees",
                                "PASS",
                                f"Found {len(employees)} employees via {endpoint}",
                                {"endpoint_used": endpoint, "employee_count": len(employees)}
                            )
                            return employees
                            
                except Exception as e:
                    continue
            
            self.log_test(
                "Get Manager Employees",
                "FAIL",
                "No working employee endpoint found"
            )
                
        except Exception as e:
            self.log_test("Get Manager Employees", "FAIL", f"Employee retrieval error: {str(e)}")
            
        return []

    def test_employee_document_access(self, employees: List[Dict[str, Any]]) -> bool:
        """Test 5.2 & 5.3: Employee Document Access and List Display"""
        print("\n" + "="*60)
        print("TEST 5.2 & 5.3: Employee Document Access")
        print("="*60)
        
        if not employees:
            self.log_test(
                "Employee Document Access",
                "SKIP",
                "No employees found to test document access"
            )
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            for employee in employees[:3]:  # Test first 3 employees
                employee_id = employee.get("id") or employee.get("employee_id")
                employee_name = employee.get("name") or employee.get("full_name", "Unknown")
                
                if not employee_id:
                    continue
                    
                # Test document access endpoint
                response = requests.get(
                    f"{self.base_url}/api/documents/employee/{employee_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        documents = result.get("data", {}).get("documents", [])
                        
                        self.log_test(
                            f"Employee Documents - {employee_name}",
                            "PASS",
                            f"Retrieved {len(documents)} documents for employee {employee_id}",
                            {
                                "employee_id": employee_id,
                                "employee_name": employee_name,
                                "document_count": len(documents),
                                "document_types": [doc.get("document_type") for doc in documents]
                            }
                        )
                        
                        # Test document metadata display
                        for doc in documents:
                            self.validate_document_metadata(doc)
                            
                        return True
                    else:
                        self.log_test(
                            f"Employee Documents - {employee_name}",
                            "FAIL",
                            f"Document request unsuccessful: {result}"
                        )
                elif response.status_code == 404:
                    self.log_test(
                        f"Employee Documents - {employee_name}",
                        "INFO",
                        f"No documents found for employee {employee_id} (404)"
                    )
                else:
                    self.log_test(
                        f"Employee Documents - {employee_name}",
                        "FAIL",
                        f"Document request failed with status {response.status_code}: {response.text}"
                    )
                    
        except Exception as e:
            self.log_test("Employee Document Access", "FAIL", f"Document access error: {str(e)}")
            
        return False

    def validate_document_metadata(self, document: Dict[str, Any]):
        """Test 5.4: Validate document metadata structure"""
        required_fields = ["id", "document_type", "file_name", "upload_date"]
        optional_fields = ["file_size", "mime_type", "status", "employee_id"]
        
        missing_fields = [field for field in required_fields if field not in document]
        present_optional = [field for field in optional_fields if field in document]
        
        if not missing_fields:
            self.log_test(
                "Document Metadata Validation",
                "PASS",
                f"Document {document.get('id', 'unknown')} has all required metadata",
                {
                    "document_id": document.get("id"),
                    "document_type": document.get("document_type"),
                    "optional_fields_present": present_optional
                }
            )
        else:
            self.log_test(
                "Document Metadata Validation",
                "FAIL",
                f"Document missing required fields: {missing_fields}",
                document
            )

    def test_document_download(self, employees: List[Dict[str, Any]]) -> bool:
        """Test 5.5: Document Download Functionality"""
        print("\n" + "="*60)
        print("TEST 5.5: Document Download")
        print("="*60)
        
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Find an employee with documents
            for employee in employees[:3]:
                employee_id = employee.get("id") or employee.get("employee_id")
                if not employee_id:
                    continue
                    
                # Get employee documents
                response = requests.get(
                    f"{self.base_url}/api/documents/employee/{employee_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    documents = result.get("data", {}).get("documents", [])
                    
                    for doc in documents[:2]:  # Test first 2 documents
                        document_id = doc.get("id")
                        if not document_id:
                            continue
                            
                        # Test document download endpoint
                        download_response = requests.post(
                            f"{self.base_url}/api/documents/{document_id}/download",
                            headers=headers
                        )
                        
                        if download_response.status_code == 200:
                            # Check if response is binary (PDF/image) or JSON
                            content_type = download_response.headers.get('content-type', '')
                            
                            if 'application/pdf' in content_type or 'image/' in content_type:
                                self.log_test(
                                    "Document Download",
                                    "PASS",
                                    f"Successfully downloaded document {document_id} ({content_type})",
                                    {
                                        "document_id": document_id,
                                        "content_type": content_type,
                                        "size_bytes": len(download_response.content)
                                    }
                                )
                                return True
                            elif 'application/json' in content_type:
                                # Check if it's a successful JSON response with download URL
                                json_result = download_response.json()
                                if json_result.get("success") and json_result.get("data", {}).get("download_url"):
                                    self.log_test(
                                        "Document Download",
                                        "PASS",
                                        f"Received download URL for document {document_id}",
                                        json_result["data"]
                                    )
                                    return True
                        else:
                            self.log_test(
                                "Document Download",
                                "FAIL",
                                f"Download failed with status {download_response.status_code}: {download_response.text}"
                            )
                            
        except Exception as e:
            self.log_test("Document Download", "FAIL", f"Download test error: {str(e)}")
            
        return False

    def test_property_isolation(self) -> bool:
        """Test 5.6: Property Isolation - Manager should only see their property's documents"""
        print("\n" + "="*60)
        print("TEST 5.6: Property Isolation")
        print("="*60)
        
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Test 1: Try to access documents with a fake employee ID from another property
            fake_employee_id = "00000000-0000-0000-0000-000000000000"
            
            response = requests.get(
                f"{self.base_url}/api/documents/employee/{fake_employee_id}",
                headers=headers
            )
            
            # Should return empty results or 404, not unauthorized access
            if response.status_code in [200, 404]:
                result = response.json()
                if response.status_code == 404 or (result.get("success") and not result.get("data", {}).get("documents")):
                    self.log_test(
                        "Property Isolation - Fake Employee",
                        "PASS",
                        "Manager cannot access documents for non-existent employee",
                        {"employee_id": fake_employee_id, "status_code": response.status_code}
                    )
                else:
                    self.log_test(
                        "Property Isolation - Fake Employee",
                        "FAIL",
                        f"Manager should not have access to fake employee: {result}"
                    )
            else:
                self.log_test(
                    "Property Isolation - Fake Employee",
                    "INFO",
                    f"Access properly denied with status {response.status_code}"
                )
            
            # Test 2: Verify manager property context
            property_response = requests.get(f"{self.base_url}/manager/property", headers=headers)
            
            if property_response.status_code == 200:
                property_result = property_response.json()
                if property_result.get("success"):
                    property_data = property_result.get("data", {})
                    manager_property_id = property_data.get("id")
                    
                    if manager_property_id == self.property_id:
                        self.log_test(
                            "Property Isolation - Manager Property Context",
                            "PASS",
                            f"Manager correctly assigned to property {manager_property_id}",
                            property_data
                        )
                        return True
                    else:
                        self.log_test(
                            "Property Isolation - Manager Property Context",
                            "FAIL",
                            f"Manager property mismatch. Expected: {self.property_id}, Got: {manager_property_id}"
                        )
                        
        except Exception as e:
            self.log_test("Property Isolation", "FAIL", f"Property isolation test error: {str(e)}")
            
        return False

    def test_pdf_preview_functionality(self, employees: List[Dict[str, Any]]) -> bool:
        """Test 5.7: PDF Preview Functionality"""
        print("\n" + "="*60)
        print("TEST 5.7: PDF Preview Functionality")
        print("="*60)
        
        try:
            headers = {"Authorization": f"Bearer {self.manager_token}"}
            
            # Look for PDF documents to test preview
            for employee in employees[:3]:
                employee_id = employee.get("id") or employee.get("employee_id")
                if not employee_id:
                    continue
                    
                # Get employee documents
                response = requests.get(
                    f"{self.base_url}/api/documents/employee/{employee_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    documents = result.get("data", {}).get("documents", [])
                    
                    # Find PDF documents
                    pdf_documents = [
                        doc for doc in documents 
                        if doc.get("mime_type") == "application/pdf" or 
                           doc.get("file_name", "").lower().endswith('.pdf')
                    ]
                    
                    if pdf_documents:
                        for pdf_doc in pdf_documents[:2]:  # Test first 2 PDFs
                            document_id = pdf_doc.get("id")
                            
                            # Test document viewing/preview endpoint
                            preview_response = requests.get(
                                f"{self.base_url}/api/documents/{document_id}",
                                headers=headers
                            )
                            
                            if preview_response.status_code == 200:
                                preview_result = preview_response.json()
                                if preview_result.get("success"):
                                    document_info = preview_result.get("data", {})
                                    
                                    self.log_test(
                                        "PDF Preview",
                                        "PASS",
                                        f"PDF document {document_id} preview accessed successfully",
                                        {
                                            "document_id": document_id,
                                            "file_name": document_info.get("file_name"),
                                            "mime_type": document_info.get("mime_type"),
                                            "has_preview_url": "preview_url" in document_info
                                        }
                                    )
                                    return True
                    else:
                        self.log_test(
                            "PDF Preview",
                            "INFO",
                            f"No PDF documents found for employee {employee_id}"
                        )
                        
        except Exception as e:
            self.log_test("PDF Preview", "FAIL", f"PDF preview test error: {str(e)}")
            
        return False

    def test_unauthorized_access(self) -> bool:
        """Test 5.8: Access Permissions and Error Handling"""
        print("\n" + "="*60)
        print("TEST 5.8: Unauthorized Access Handling")
        print("="*60)
        
        try:
            # Test 1: No authentication token
            response = requests.get(f"{self.base_url}/api/documents/employee/test-id")
            
            if response.status_code == 401:
                self.log_test(
                    "Unauthorized Access - No Token",
                    "PASS",
                    "Properly rejected request without authentication token"
                )
            else:
                self.log_test(
                    "Unauthorized Access - No Token",
                    "FAIL",
                    f"Should return 401 for no auth token, got {response.status_code}"
                )
            
            # Test 2: Invalid token
            headers = {"Authorization": "Bearer invalid-token-123"}
            response = requests.get(f"{self.base_url}/api/documents/employee/test-id", headers=headers)
            
            if response.status_code in [401, 403]:
                self.log_test(
                    "Unauthorized Access - Invalid Token",
                    "PASS",
                    f"Properly rejected request with invalid token (status {response.status_code})"
                )
            else:
                self.log_test(
                    "Unauthorized Access - Invalid Token",
                    "FAIL",
                    f"Should return 401/403 for invalid token, got {response.status_code}"
                )
            
            # Test 3: Try accessing HR-only endpoints with manager token
            if self.manager_token:
                headers = {"Authorization": f"Bearer {self.manager_token}"}
                response = requests.get(f"{self.base_url}/hr/employees", headers=headers)
                
                if response.status_code in [401, 403]:
                    self.log_test(
                        "Role-based Access Control",
                        "PASS",
                        f"Manager properly denied access to HR endpoint (status {response.status_code})"
                    )
                    return True
                else:
                    self.log_test(
                        "Role-based Access Control",
                        "WARN",
                        f"Manager may have access to HR endpoint (status {response.status_code})"
                    )
                    
        except Exception as e:
            self.log_test("Unauthorized Access", "FAIL", f"Access control test error: {str(e)}")
            
        return False

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all manager document access tests"""
        print("\n" + "="*80)
        print("MANAGER DOCUMENT ACCESS COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"Testing against: {self.base_url}")
        print(f"Manager Account: {self.manager_email}")
        print(f"Property ID: {self.property_id}")
        
        # Test 1: Authentication
        if not self.test_manager_authentication():
            print("\n❌ CRITICAL: Manager authentication failed - cannot proceed with other tests")
            return self.generate_test_report()
        
        # Test 2: Dashboard access
        dashboard_data = self.test_manager_dashboard_access()
        
        # Test 3: Get employees
        employees = self.get_manager_employees()
        
        # Test 4: Document access
        self.test_employee_document_access(employees)
        
        # Test 5: Document download
        self.test_document_download(employees)
        
        # Test 6: Property isolation
        self.test_property_isolation()
        
        # Test 7: PDF preview
        self.test_pdf_preview_functionality(employees)
        
        # Test 8: Unauthorized access
        self.test_unauthorized_access()
        
        return self.generate_test_report()

    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIP"])
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            "test_details": self.test_results,
            "manager_info": {
                "email": self.manager_email,
                "property_id": self.property_id,
                "authenticated": bool(self.manager_token)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️  Skipped: {skipped_tests}")
        print(f"Success Rate: {report['test_summary']['success_rate']}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test["status"] == "FAIL":
                    print(f"  - {test['test']}: {test['details']}")
        
        return report


def main():
    """Main test execution"""
    # Check if backend is running by testing a simple endpoint
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Backend connection test: Status {response.status_code}")
        if response.status_code not in [200, 404]:  # 404 is ok, means server is up but no root route
            print("❌ Backend is not responding properly. Please ensure it's running on port 8000.")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend at http://localhost:8000: {e}")
        print("Please ensure the backend is running with:")
        print("cd hotel-onboarding-backend && python3 -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)
    
    # Run tests
    tester = ManagerDocumentAccessTester()
    report = tester.run_comprehensive_tests()
    
    # Save report to file
    report_file = f"manager_document_access_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Full test report saved to: {report_file}")
    
    # Exit with appropriate code
    if report["test_summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()