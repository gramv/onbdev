#!/usr/bin/env python3
"""
API Field Validation Testing
Tests the backend API endpoints directly for field validation
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3001"

class APIFieldValidationTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.test_property_id = None
        
    def log_result(self, endpoint: str, field: str, test_type: str, 
                   input_value: Any, expected: str, actual: str, 
                   status: str, impact: str = "Low"):
        """Log a test result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "field": field,
            "test_type": test_type,
            "input_value": str(input_value)[:100],  # Truncate long inputs
            "expected": expected,
            "actual": actual,
            "status": status,  # "PASS", "FAIL", "WARNING"
            "impact": impact   # "Critical", "High", "Medium", "Low"
        }
        self.results.append(result)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {endpoint} - {field} - {test_type}: {status}")
        if status != "PASS":
            print(f"   Input: {repr(input_value)[:50]}...")
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}\n")
    
    def get_test_property(self):
        """Get or create a test property"""
        # First, try to get properties
        try:
            # Try the QR generation endpoint to get a property
            response = self.session.post(
                f"{BASE_URL}/api/qr/generate",
                json={
                    "propertyName": "Test Hotel",
                    "propertyId": "test-property-001",
                    "departmentsAndPositions": {
                        "Housekeeping": ["Housekeeper", "Housekeeping Supervisor"],
                        "Front Desk": ["Front Desk Agent", "Night Auditor"]
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_property_id = data.get("propertyId", "test-property-001")
                return self.test_property_id
            else:
                print(f"Could not create test property: {response.status_code}")
                # Use a default test property ID
                self.test_property_id = "test-property-001"
                return self.test_property_id
                
        except Exception as e:
            print(f"Error getting test property: {e}")
            self.test_property_id = "test-property-001"
            return self.test_property_id
    
    def test_job_application_fields(self):
        """Test job application submission fields"""
        print("\n" + "="*60)
        print("TESTING JOB APPLICATION FIELDS")
        print("="*60)
        
        # Base valid payload
        valid_payload = {
            "property_id": self.test_property_id,
            "position": "Housekeeper",
            "department": "Housekeeping",
            "first_name": "John",
            "middle_name": "",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "address": "123 Main St",
            "apartment_unit": "",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "age_verification": True,
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "reliable_transportation": "yes",
            "transportation_method": "personal_vehicle",
            "positions_applying": ["Housekeeper"],
            "availability": {
                "monday": {"available": True, "start": "09:00", "end": "17:00"},
                "tuesday": {"available": True, "start": "09:00", "end": "17:00"},
                "wednesday": {"available": True, "start": "09:00", "end": "17:00"},
                "thursday": {"available": True, "start": "09:00", "end": "17:00"},
                "friday": {"available": True, "start": "09:00", "end": "17:00"},
                "saturday": {"available": False},
                "sunday": {"available": False}
            },
            "start_date": "2025-08-15",
            "desired_pay": "15.00",
            "employment_history": [],
            "education": {
                "highest_level": "high_school",
                "school_name": "Springfield High",
                "graduation_year": "2020"
            },
            "references": [],
            "criminal_history": "no",
            "criminal_explanation": "",
            "voluntary_self_identification": {
                "gender": "prefer_not_to_say",
                "ethnicity": "prefer_not_to_say",
                "veteran_status": "prefer_not_to_say",
                "disability_status": "prefer_not_to_say"
            },
            "consent_background_check": True,
            "consent_terms": True,
            "signature": "John Doe",
            "signature_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Test empty first name
        print("\n--- Testing First Name Field ---")
        test_payload = valid_payload.copy()
        test_payload["first_name"] = ""
        response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
        
        if response.status_code == 201:
            self.log_result("/api/applications/submit", "first_name", "empty_value", "",
                          "Should reject empty first name",
                          f"Accepted with status {response.status_code}",
                          "FAIL", "High")
        else:
            self.log_result("/api/applications/submit", "first_name", "empty_value", "",
                          "Should reject empty first name",
                          f"Correctly rejected: {response.json().get('detail', 'Unknown error')}",
                          "PASS")
        
        # Test SQL injection in first name
        sql_injections = [
            "'; DROP TABLE applications; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ]
        
        for sql in sql_injections:
            test_payload = valid_payload.copy()
            test_payload["first_name"] = sql
            response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
            
            if response.status_code == 201:
                # Check if the value was stored as-is (dangerous) or sanitized
                self.log_result("/api/applications/submit", "first_name", "sql_injection", sql,
                              "Should sanitize or reject SQL injection",
                              "Accepted - potential SQL injection vulnerability",
                              "FAIL", "Critical")
            else:
                self.log_result("/api/applications/submit", "first_name", "sql_injection", sql,
                              "Should sanitize or reject SQL injection",
                              "Rejected appropriately",
                              "PASS")
        
        # Test XSS attempts in first name
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>"
        ]
        
        for xss in xss_attempts:
            test_payload = valid_payload.copy()
            test_payload["first_name"] = xss
            response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
            
            if response.status_code == 201:
                self.log_result("/api/applications/submit", "first_name", "xss_attempt", xss,
                              "Should sanitize or reject XSS attempts",
                              "Accepted - potential XSS vulnerability",
                              "FAIL", "Critical")
        
        # Test email validation
        print("\n--- Testing Email Field ---")
        invalid_emails = [
            "notanemail",
            "test@",
            "@example.com",
            "test@@example.com",
            "test..user@example.com",
            "test user@example.com",
            "test@.com",
            ".test@example.com"
        ]
        
        for email in invalid_emails:
            test_payload = valid_payload.copy()
            test_payload["email"] = email
            response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
            
            if response.status_code == 201:
                self.log_result("/api/applications/submit", "email", "invalid_format", email,
                              "Should reject invalid email format",
                              "Accepted invalid email",
                              "FAIL", "High")
            else:
                self.log_result("/api/applications/submit", "email", "invalid_format", email,
                              "Should reject invalid email format",
                              "Correctly rejected",
                              "PASS")
        
        # Test phone validation
        print("\n--- Testing Phone Field ---")
        invalid_phones = [
            "123",
            "abcdefghij",
            "123-abc-4567",
            "12345678901234567890"
        ]
        
        for phone in invalid_phones:
            test_payload = valid_payload.copy()
            test_payload["phone"] = phone
            response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
            
            if response.status_code == 201 and (len(phone) < 10 or not any(c.isdigit() for c in phone)):
                self.log_result("/api/applications/submit", "phone", "invalid_format", phone,
                              "Should validate phone number format",
                              "Accepted invalid phone",
                              "WARNING", "Medium")
        
        # Test ZIP code validation
        print("\n--- Testing ZIP Code Field ---")
        invalid_zips = ["1234", "123456", "ABCDE", "12345-", "12345-123"]
        
        for zip_code in invalid_zips:
            test_payload = valid_payload.copy()
            test_payload["zip_code"] = zip_code
            response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
            
            if response.status_code == 201:
                self.log_result("/api/applications/submit", "zip_code", "invalid_format", zip_code,
                              "Should validate ZIP code format",
                              "Accepted invalid ZIP",
                              "WARNING", "Medium")
        
        # Test date validation
        print("\n--- Testing Date Fields ---")
        # Future birth date (assuming date_of_birth field exists)
        test_payload = valid_payload.copy()
        test_payload["start_date"] = "2099-12-31"
        response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
        
        if response.status_code == 201:
            self.log_result("/api/applications/submit", "start_date", "far_future_date", "2099-12-31",
                          "Should validate reasonable date ranges",
                          "Accepted unreasonable future date",
                          "WARNING", "Low")
        
        # Test very long input
        print("\n--- Testing Input Length Limits ---")
        test_payload = valid_payload.copy()
        test_payload["first_name"] = "A" * 1000
        response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
        
        if response.status_code == 201:
            self.log_result("/api/applications/submit", "first_name", "very_long_input", "A" * 1000,
                          "Should enforce maximum length",
                          "Accepted very long input",
                          "WARNING", "Medium")
        
        # Test Unicode and special characters
        print("\n--- Testing Unicode and Special Characters ---")
        unicode_tests = ["😀😃😄", "é à ñ ü", "中文测试", "الع��بية"]
        
        for unicode_str in unicode_tests:
            test_payload = valid_payload.copy()
            test_payload["first_name"] = unicode_str
            response = self.session.post(f"{BASE_URL}/api/applications/submit", json=test_payload)
            
            if response.status_code != 201:
                self.log_result("/api/applications/submit", "first_name", "unicode", unicode_str,
                              "Should accept valid unicode characters",
                              "Rejected valid unicode",
                              "WARNING", "Low")
    
    def test_cross_endpoint_validation(self):
        """Test data consistency across different endpoints"""
        print("\n" + "="*60)
        print("TESTING CROSS-ENDPOINT VALIDATION")
        print("="*60)
        
        # This would test scenarios like:
        # 1. SSN consistency between I-9 and W-4 endpoints
        # 2. Name consistency across forms
        # 3. Address standardization
        
        print("Cross-endpoint validation tests would require multiple form submissions")
        print("Skipping for now as it requires more complex setup")
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("# API Field Validation Test Report - Hotel Onboarding System")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"API Base URL: {BASE_URL}")
        report.append(f"Total Tests Run: {len(self.results)}")
        
        # Summary statistics
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        warnings = len([r for r in self.results if r["status"] == "WARNING"])
        
        report.append("\n## Test Summary")
        report.append(f"- Total Tests: {len(self.results)}")
        report.append(f"- Passed: {passed}")
        report.append(f"- Failed: {failed}")
        report.append(f"- Warnings: {warnings}")
        
        # Critical issues
        critical_issues = [r for r in self.results if r["status"] == "FAIL" and r["impact"] == "Critical"]
        if critical_issues:
            report.append("\n## 🚨 CRITICAL SECURITY ISSUES")
            for i, issue in enumerate(critical_issues, 1):
                report.append(f"\n### {i}. {issue['field']} - {issue['test_type']}")
                report.append(f"**Endpoint**: `{issue['endpoint']}`")
                report.append(f"**Test Input**: `{issue['input_value']}`")
                report.append(f"**Expected**: {issue['expected']}")
                report.append(f"**Actual**: {issue['actual']}")
                report.append(f"**Impact**: CRITICAL - Immediate security risk")
                report.append("\n**Recommended Fix**:")
                
                if "sql" in issue['test_type'].lower():
                    report.append("```python")
                    report.append("# Use parameterized queries")
                    report.append("# Never concatenate user input into SQL")
                    report.append("# Example with SQLAlchemy:")
                    report.append("query = db.query(Application).filter(")
                    report.append("    Application.first_name == :first_name")
                    report.append(").params(first_name=sanitized_input)")
                    report.append("```")
                elif "xss" in issue['test_type'].lower():
                    report.append("```python")
                    report.append("# Sanitize HTML in all text inputs")
                    report.append("import html")
                    report.append("sanitized = html.escape(user_input)")
                    report.append("# Or use a library like bleach")
                    report.append("import bleach")
                    report.append("sanitized = bleach.clean(user_input)")
                    report.append("```")
        
        # High priority issues
        high_issues = [r for r in self.results if r["status"] == "FAIL" and r["impact"] == "High"]
        if high_issues:
            report.append("\n## High Priority Issues")
            for issue in high_issues:
                report.append(f"\n- **{issue['field']}**: {issue['expected']}")
                report.append(f"  - Test: {issue['test_type']}")
                report.append(f"  - Input: `{issue['input_value']}`")
        
        # Field-by-field results
        report.append("\n## Detailed Results by Field")
        
        # Group by field
        fields = {}
        for result in self.results:
            field = result['field']
            if field not in fields:
                fields[field] = {"pass": 0, "fail": 0, "warning": 0}
            fields[field][result['status'].lower()] += 1
        
        report.append("\n| Field | Tests | Passed | Failed | Warnings |")
        report.append("|-------|-------|--------|--------|----------|")
        for field, counts in fields.items():
            total = counts['pass'] + counts['fail'] + counts['warning']
            report.append(f"| {field} | {total} | {counts['pass']} | {counts['fail']} | {counts['warning']} |")
        
        # Recommendations
        report.append("\n## Priority Recommendations")
        report.append("\n### 1. Input Sanitization (CRITICAL)")
        report.append("- Implement comprehensive input sanitization for ALL text fields")
        report.append("- Use parameterized queries for all database operations")
        report.append("- HTML-escape all user input before display")
        report.append("- Consider using a validation library like Pydantic with strict mode")
        
        report.append("\n### 2. Field Validation (HIGH)")
        report.append("- Enforce strict email validation (RFC 5322)")
        report.append("- Implement proper phone number formatting and validation")
        report.append("- Add ZIP code format validation (XXXXX or XXXXX-XXXX)")
        report.append("- Enforce maximum length limits on all text fields")
        
        report.append("\n### 3. Business Logic Validation (MEDIUM)")
        report.append("- Validate date ranges (no future birth dates, reasonable start dates)")
        report.append("- Implement SSN format validation (XXX-XX-XXXX)")
        report.append("- Add state code validation (2-letter codes only)")
        
        report.append("\n### 4. Cross-Form Consistency (MEDIUM)")
        report.append("- Implement data consistency checks across forms")
        report.append("- Store canonical data once and reference it")
        report.append("- Add warnings for data mismatches")
        
        report.append("\n## Security Best Practices")
        report.append("\n1. **Never trust client-side validation** - Always validate on the server")
        report.append("2. **Use allowlists, not denylists** - Define what's allowed, reject everything else")
        report.append("3. **Sanitize on input, escape on output** - Clean data when received, escape when displayed")
        report.append("4. **Log security events** - Track validation failures for security monitoring")
        report.append("5. **Rate limit API endpoints** - Prevent abuse and brute force attacks")
        
        return "\n".join(report)
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting API Field Validation Testing")
        print("=" * 60)
        
        # Get test property
        self.get_test_property()
        print(f"Using test property ID: {self.test_property_id}")
        
        # Run test suites
        self.test_job_application_fields()
        self.test_cross_endpoint_validation()
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        report_filename = f"api_field_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"\n\n📄 Test report saved to: {report_filename}")
        print(f"Total tests run: {len(self.results)}")
        print(f"Failed tests: {len([r for r in self.results if r['status'] == 'FAIL'])}")
        print(f"Critical issues: {len([r for r in self.results if r['impact'] == 'Critical'])}")

if __name__ == "__main__":
    tester = APIFieldValidationTester()
    tester.run_all_tests()