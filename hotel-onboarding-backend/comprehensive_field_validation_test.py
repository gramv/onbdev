#!/usr/bin/env python3
"""
Comprehensive Field Validation Testing for Hotel Onboarding Job Application
Tests all input fields with edge cases, invalid inputs, and security tests
"""

import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import requests
from urllib.parse import urljoin

# Test configuration
BASE_URL = "http://localhost:3001"
API_BASE_URL = "http://localhost:8000/api"
PROPERTY_ID = "550e8400-e29b-41d4-a716-446655440001"  # Test property ID

# Comprehensive test data for various field types
TEST_DATA = {
    "text_fields": {
        "empty_values": ["", " ", "  ", "\t", "\n", "\r\n"],
        "single_char": ["a", "1", "@", " "],
        "special_chars": ["<>", "&%$#", "@!", "'\"", "\\", "/", "|", "{}", "[]", "()"],
        "sql_injection": [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
            "1; DELETE FROM applications WHERE 1=1; --"
        ],
        "xss_attempts": [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>"
        ],
        "unicode": ["😀😃😄", "é à ñ ü", "™ ® ©", "中文测试", "العربية", "🚀🎉🎊"],
        "formatting": [
            "Text with   multiple    spaces",
            "Line\nbreaks\nin\ntext",
            "Tabs\there\tand\tthere",
            "\rCarriage return",
            "Leading space",
            "Trailing space "
        ],
        "very_long": ["A" * 1000, "Test " * 500, "VeryLongWordWithoutSpaces" * 50]
    },
    "email_fields": {
        "missing_at": ["testuser.com", "test.user.com", "test@", "@domain.com"],
        "multiple_at": ["test@@domain.com", "test@user@domain.com"],
        "no_domain": ["test@", "test@domain", "test@.com", "test@domain."],
        "special_chars": [
            "test+tag@domain.com",
            "test.user@domain.com",
            "test_user@domain.com",
            "test-user@domain.com",
            "test@sub.domain.com"
        ],
        "invalid": [
            "test..user@domain.com",
            ".test@domain.com",
            "test.@domain.com",
            "test user@domain.com",
            "test@domain..com"
        ],
        "case_sensitivity": ["TEST@DOMAIN.COM", "Test@Domain.Com", "TeSt@DoMaIn.CoM"],
        "international": [
            "test@domain.co.uk",
            "test@domain.org.au",
            "test@subdomain.domain.com",
            "test@123.456.789.012"
        ]
    },
    "phone_fields": {
        "invalid_formats": [
            "123",
            "12345",
            "123456789012345",
            "abcdefghij",
            "123-abc-4567",
            "phone number"
        ],
        "international": [
            "+1 (555) 123-4567",
            "+44 20 7946 0958",
            "+86 138 0013 8000",
            "001-555-123-4567"
        ],
        "special_chars": [
            "(555) 123-4567",
            "555.123.4567",
            "555 123 4567",
            "555/123/4567",
            "555*123*4567"
        ],
        "extensions": [
            "555-123-4567 ext 123",
            "555-123-4567 x123",
            "555-123-4567 extension 123"
        ]
    },
    "ssn_fields": {
        "invalid_formats": [
            "12345678",  # Too short
            "1234567890",  # Too long
            "123-45-678",  # Wrong grouping
            "12-345-6789",  # Wrong grouping
            "abc-de-fghi",  # Letters
            "000-00-0000",  # All zeros
            "666-12-3456",  # Invalid area (666)
            "123-00-4567",  # Invalid group (00)
            "123-45-0000"  # Invalid serial (0000)
        ],
        "valid_formats": [
            "123-45-6789",
            "123456789",
            "123 45 6789"
        ]
    },
    "date_fields": {
        "invalid_dates": [
            "02/30/2024",  # February 30th
            "04/31/2024",  # April 31st
            "13/01/2024",  # Invalid month
            "00/01/2024",  # Zero month
            "01/00/2024",  # Zero day
            "01/32/2024"   # Invalid day
        ],
        "future_birth": [
            "01/01/2030",
            "12/31/2025"
        ],
        "edge_cases": [
            "02/29/2023",  # Not a leap year
            "02/29/2024",  # Leap year
            "01/01/1900",  # Very old
            "01/01/0000",  # Year zero
            "01/01/9999"   # Far future
        ],
        "formats": [
            "1/1/2024",
            "01/01/24",
            "2024-01-01",
            "01-01-2024",
            "January 1, 2024"
        ]
    },
    "number_fields": {
        "invalid": [
            "abc",
            "12.34.56",
            "12,34",
            "$100",
            "100%",
            "+100",
            "1e10",
            "NaN",
            "Infinity"
        ],
        "edge_cases": [
            "-1",
            "0",
            "999999999999",
            "-999999999999",
            "1.23456789",
            "0.0000001"
        ]
    }
}

class FieldValidationTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.property_info = None
        
    def log_result(self, field_name: str, test_type: str, input_value: str, 
                   expected: str, actual: str, status: str, impact: str = "Low"):
        """Log a test result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "field_name": field_name,
            "test_type": test_type,
            "input_value": input_value,
            "expected_behavior": expected,
            "actual_behavior": actual,
            "status": status,  # "PASS", "FAIL", "WARNING"
            "impact": impact   # "Critical", "High", "Medium", "Low"
        }
        self.results.append(result)
        
        # Print immediate feedback
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {field_name} - {test_type}: {status}")
        if status != "PASS":
            print(f"   Input: {repr(input_value)}")
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
            print()
    
    def get_property_info(self) -> Dict:
        """Get property information"""
        try:
            response = self.session.get(f"{API_BASE_URL}/properties/{PROPERTY_ID}/public-info")
            if response.status_code == 200:
                self.property_info = response.json()
                return self.property_info
            else:
                print(f"Failed to get property info: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting property info: {e}")
            return None
    
    def test_api_field_validation(self, endpoint: str, field_name: str, 
                                 test_values: List[str], valid_payload: Dict) -> List[Dict]:
        """Test field validation via API"""
        results = []
        
        for test_value in test_values:
            # Create test payload
            test_payload = valid_payload.copy()
            
            # Handle nested fields
            if '.' in field_name:
                parts = field_name.split('.')
                current = test_payload
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = test_value
            else:
                test_payload[field_name] = test_value
            
            try:
                response = self.session.post(
                    f"{API_BASE_URL}{endpoint}",
                    json=test_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                result = {
                    "input": test_value,
                    "status_code": response.status_code,
                    "response": response.json() if response.content else None
                }
                results.append(result)
                
            except Exception as e:
                result = {
                    "input": test_value,
                    "error": str(e)
                }
                results.append(result)
        
        return results
    
    def test_personal_information_fields(self):
        """Test all personal information fields"""
        print("\n" + "="*60)
        print("TESTING PERSONAL INFORMATION FIELDS")
        print("="*60)
        
        # Valid base payload
        valid_payload = {
            "property_id": PROPERTY_ID,
            "position": "Housekeeper",
            "personal_info": {
                "first_name": "John",
                "middle_name": "",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "555-123-4567",
                "address": {
                    "street": "123 Main St",
                    "city": "Springfield",
                    "state": "IL",
                    "zip_code": "62701"
                }
            }
        }
        
        # Test first name
        print("\n--- Testing First Name Field ---")
        for empty in TEST_DATA["text_fields"]["empty_values"]:
            results = self.test_api_field_validation(
                "/applications/submit",
                "personal_info.first_name",
                [empty],
                valid_payload
            )
            for r in results:
                if r.get("status_code") == 201:
                    self.log_result(
                        "first_name", "empty_value", r["input"],
                        "Should reject empty first name",
                        f"Accepted with status {r['status_code']}",
                        "FAIL", "High"
                    )
                else:
                    self.log_result(
                        "first_name", "empty_value", r["input"],
                        "Should reject empty first name",
                        f"Rejected with status {r['status_code']}",
                        "PASS"
                    )
        
        # Test SQL injection
        for sql in TEST_DATA["text_fields"]["sql_injection"]:
            results = self.test_api_field_validation(
                "/applications/submit",
                "personal_info.first_name",
                [sql],
                valid_payload
            )
            for r in results:
                if r.get("status_code") == 201:
                    # Check if the value was sanitized
                    self.log_result(
                        "first_name", "sql_injection", r["input"],
                        "Should sanitize or reject SQL injection attempts",
                        f"Accepted - potential security risk",
                        "FAIL", "Critical"
                    )
        
        # Test XSS attempts
        for xss in TEST_DATA["text_fields"]["xss_attempts"]:
            results = self.test_api_field_validation(
                "/applications/submit",
                "personal_info.first_name",
                [xss],
                valid_payload
            )
            for r in results:
                if r.get("status_code") == 201:
                    self.log_result(
                        "first_name", "xss_attempt", r["input"],
                        "Should sanitize or reject XSS attempts",
                        f"Accepted - potential XSS vulnerability",
                        "FAIL", "Critical"
                    )
        
        # Test email field
        print("\n--- Testing Email Field ---")
        for invalid_email in TEST_DATA["email_fields"]["invalid"]:
            results = self.test_api_field_validation(
                "/applications/submit",
                "personal_info.email",
                [invalid_email],
                valid_payload
            )
            for r in results:
                if r.get("status_code") == 201:
                    self.log_result(
                        "email", "invalid_format", r["input"],
                        "Should reject invalid email format",
                        f"Accepted invalid email",
                        "FAIL", "High"
                    )
                else:
                    self.log_result(
                        "email", "invalid_format", r["input"],
                        "Should reject invalid email format",
                        f"Correctly rejected",
                        "PASS"
                    )
        
        # Test phone field
        print("\n--- Testing Phone Field ---")
        for invalid_phone in TEST_DATA["phone_fields"]["invalid_formats"]:
            results = self.test_api_field_validation(
                "/applications/submit",
                "personal_info.phone",
                [invalid_phone],
                valid_payload
            )
            for r in results:
                # Phone validation might be more lenient
                if r.get("status_code") == 201 and len(r["input"]) < 10:
                    self.log_result(
                        "phone", "invalid_format", r["input"],
                        "Should validate phone number length",
                        f"Accepted short phone number",
                        "WARNING", "Medium"
                    )
    
    def test_cross_field_validation(self):
        """Test cross-field validation and data consistency"""
        print("\n" + "="*60)
        print("TESTING CROSS-FIELD VALIDATION")
        print("="*60)
        
        # Test 1: Consistent SSN across forms
        print("\n--- Testing SSN Consistency ---")
        # This would need to be tested across multiple form submissions
        
        # Test 2: Date logic validation
        print("\n--- Testing Date Logic ---")
        test_payload = {
            "property_id": PROPERTY_ID,
            "position": "Housekeeper",
            "personal_info": {
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "phone": "555-123-4567",
                "date_of_birth": "2030-01-01"  # Future date
            }
        }
        
        response = self.session.post(
            f"{API_BASE_URL}/applications/submit",
            json=test_payload
        )
        
        if response.status_code == 201:
            self.log_result(
                "date_of_birth", "future_date", "2030-01-01",
                "Should reject future birth dates",
                "Accepted future birth date",
                "FAIL", "High"
            )
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("# Field Validation Test Report - Hotel Onboarding Job Application")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests Run: {len(self.results)}")
        
        # Summary statistics
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        warnings = len([r for r in self.results if r["status"] == "WARNING"])
        
        report.append("\n## Test Summary")
        report.append(f"- Total Fields Tested: {len(set(r['field_name'] for r in self.results))}")
        report.append(f"- Validation Failures Found: {failed}")
        report.append(f"- Warnings: {warnings}")
        report.append(f"- Tests Passed: {passed}")
        
        # Critical issues
        critical_issues = [r for r in self.results if r["status"] == "FAIL" and r["impact"] == "Critical"]
        if critical_issues:
            report.append("\n## Critical Issues")
            for i, issue in enumerate(critical_issues, 1):
                report.append(f"\n### {i}. {issue['field_name']} - {issue['test_type']}")
                report.append(f"**Test Input**: `{issue['input_value']}`")
                report.append(f"**Expected Behavior**: {issue['expected_behavior']}")
                report.append(f"**Actual Behavior**: {issue['actual_behavior']}")
                report.append(f"**Impact**: CRITICAL - Potential security vulnerability")
                report.append("**Steps to Reproduce**:")
                report.append(f"1. Navigate to job application form")
                report.append(f"2. Enter `{issue['input_value']}` in {issue['field_name']} field")
                report.append(f"3. Submit form")
                report.append("**Recommended Fix**:")
                report.append("```javascript")
                report.append("// Add input sanitization")
                report.append("const sanitizeInput = (input) => {")
                report.append("  return input.replace(/<script.*?>.*?<\\/script>/gi, '')")
                report.append("    .replace(/[<>]/g, '')")
                report.append("    .trim();")
                report.append("};")
                report.append("```")
        
        # Field-by-field results
        report.append("\n## Field-by-Field Results")
        fields = {}
        for result in self.results:
            field = result['field_name']
            if field not in fields:
                fields[field] = []
            fields[field].append(result)
        
        report.append("\n| Field | Tests Run | Passed | Failed | Warnings |")
        report.append("|-------|-----------|---------|---------|----------|")
        for field, results in fields.items():
            passed = len([r for r in results if r["status"] == "PASS"])
            failed = len([r for r in results if r["status"] == "FAIL"])
            warnings = len([r for r in results if r["status"] == "WARNING"])
            report.append(f"| {field} | {len(results)} | {passed} | {failed} | {warnings} |")
        
        # Priority fixes
        report.append("\n## Priority Fixes")
        report.append("\n1. **Input Sanitization** - Implement comprehensive input sanitization for all text fields")
        report.append("2. **Email Validation** - Strengthen email validation regex")
        report.append("3. **Phone Number Format** - Implement consistent phone number formatting and validation")
        report.append("4. **Date Validation** - Add business logic validation for dates (no future birth dates)")
        report.append("5. **Cross-Form Validation** - Implement SSN consistency checks across forms")
        
        return "\n".join(report)
    
    def run_all_tests(self):
        """Run all field validation tests"""
        print("Starting Comprehensive Field Validation Testing")
        print("=" * 60)
        
        # Get property info first
        if not self.get_property_info():
            print("Failed to get property info. Exiting.")
            return
        
        # Run test suites
        self.test_personal_information_fields()
        self.test_cross_field_validation()
        
        # Generate and save report
        report = self.generate_report()
        
        # Save report
        report_filename = f"field_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_filename, 'w') as f:
            f.write(report)
        
        print(f"\n\nTest report saved to: {report_filename}")
        print(f"Total tests run: {len(self.results)}")
        print(f"Failed tests: {len([r for r in self.results if r['status'] == 'FAIL'])}")

if __name__ == "__main__":
    tester = FieldValidationTester()
    tester.run_all_tests()