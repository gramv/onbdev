#!/usr/bin/env python3
"""
Manual Field Validation Testing Script
Generates test cases and instructions for manual testing
"""

import json
from datetime import datetime
from typing import Dict, List, Any

# Comprehensive test data for various field types
TEST_DATA = {
    "text_fields": {
        "empty_values": {
            "tests": ["", " ", "  ", "\t", "\n", "\r\n"],
            "description": "Empty or whitespace-only values"
        },
        "single_char": {
            "tests": ["a", "1", "@", " ", ".", "-"],
            "description": "Single character inputs"
        },
        "special_chars": {
            "tests": ["<>", "&%$#", "@!", "'\"", "\\", "/", "|", "{}", "[]", "()"],
            "description": "Special characters that might break parsing"
        },
        "sql_injection": {
            "tests": [
                "'; DROP TABLE users; --",
                "1' OR '1'='1",
                "admin'--",
                "' UNION SELECT * FROM users --",
                "1; DELETE FROM applications WHERE 1=1; --"
            ],
            "description": "SQL injection attempts"
        },
        "xss_attempts": {
            "tests": [
                "<script>alert('xss')</script>",
                "<img src=x onerror=alert('xss')>",
                "<iframe src='javascript:alert(1)'></iframe>",
                "javascript:alert('xss')",
                "<svg onload=alert('xss')>",
                "<<SCRIPT>alert('XSS');//<</SCRIPT>",
                "<body onload=alert('xss')>"
            ],
            "description": "Cross-site scripting attempts"
        },
        "unicode": {
            "tests": ["😀😃😄", "é à ñ ü", "™ ® ©", "中文测试", "العربية", "🚀🎉🎊"],
            "description": "Unicode and special language characters"
        },
        "formatting": {
            "tests": [
                "Text with   multiple    spaces",
                "Line\nbreaks\nin\ntext",
                "Tabs\there\tand\tthere",
                "\rCarriage return",
                " Leading space",
                "Trailing space ",
                "   Multiple   spaces   everywhere   "
            ],
            "description": "Text with various formatting issues"
        },
        "very_long": {
            "tests": [
                "A" * 500,
                "Test " * 200,
                "VeryLongWordWithoutSpaces" * 50,
                "This is a very long sentence that goes on and on and on " * 20
            ],
            "description": "Very long inputs to test length limits"
        }
    },
    "name_fields": {
        "invalid_names": {
            "tests": [
                "123",
                "John123",
                "John@Doe",
                "John_Doe",
                "John-Doe-Smith-Johnson-Williams",
                "Mr. John",
                "John Jr.",
                "O'Brien",
                "Mary-Jane",
                "José",
                "François",
                "Müller"
            ],
            "description": "Names with numbers, special chars, or formatting"
        }
    },
    "email_fields": {
        "missing_at": {
            "tests": ["testuser.com", "test.user.com", "test@", "@domain.com"],
            "description": "Missing @ symbol"
        },
        "multiple_at": {
            "tests": ["test@@domain.com", "test@user@domain.com", "@test@domain.com"],
            "description": "Multiple @ symbols"
        },
        "no_domain": {
            "tests": ["test@", "test@domain", "test@.com", "test@domain.", "test@."],
            "description": "Missing or invalid domain"
        },
        "special_chars": {
            "tests": [
                "test+tag@domain.com",
                "test.user@domain.com",
                "test_user@domain.com",
                "test-user@domain.com",
                "test@sub.domain.com",
                "test!user@domain.com",
                "test#user@domain.com"
            ],
            "description": "Special characters in email"
        },
        "invalid": {
            "tests": [
                "test..user@domain.com",
                ".test@domain.com",
                "test.@domain.com",
                "test user@domain.com",
                "test@domain..com",
                "test@domain .com",
                "test@ domain.com"
            ],
            "description": "Invalid email formats"
        },
        "case_sensitivity": {
            "tests": ["TEST@DOMAIN.COM", "Test@Domain.Com", "TeSt@DoMaIn.CoM"],
            "description": "Various case combinations"
        }
    },
    "phone_fields": {
        "invalid_formats": {
            "tests": [
                "123",
                "12345",
                "123456789012345",
                "abcdefghij",
                "123-abc-4567",
                "phone number",
                "555-CALL-NOW",
                "1234567890123456789012345"
            ],
            "description": "Invalid phone formats"
        },
        "international": {
            "tests": [
                "+1 (555) 123-4567",
                "+44 20 7946 0958",
                "+86 138 0013 8000",
                "001-555-123-4567",
                "+1-555-123-4567",
                "011-44-20-7946-0958"
            ],
            "description": "International phone formats"
        },
        "special_chars": {
            "tests": [
                "(555) 123-4567",
                "555.123.4567",
                "555 123 4567",
                "555/123/4567",
                "555*123*4567",
                "555#123#4567"
            ],
            "description": "Various separator characters"
        }
    },
    "ssn_fields": {
        "invalid_formats": {
            "tests": [
                "12345678",      # Too short
                "1234567890",    # Too long
                "123-45-678",    # Wrong grouping
                "12-345-6789",   # Wrong grouping
                "abc-de-fghi",   # Letters
                "000-00-0000",   # All zeros
                "666-12-3456",   # Invalid area (666)
                "123-00-4567",   # Invalid group (00)
                "123-45-0000",   # Invalid serial (0000)
                "999-99-9999",   # Too high
                "078-05-1120"    # Infamous invalid SSN
            ],
            "description": "Invalid SSN formats"
        }
    },
    "date_fields": {
        "invalid_dates": {
            "tests": [
                "02/30/2024",    # February 30th
                "04/31/2024",    # April 31st
                "13/01/2024",    # Invalid month
                "00/01/2024",    # Zero month
                "01/00/2024",    # Zero day
                "01/32/2024",    # Invalid day
                "2024/01/01",    # Wrong format
                "01-01-2024",    # Wrong separator
                "Jan 1, 2024",   # Text format
                "2024",          # Year only
                "01/2024",       # Month/year only
                "99/99/9999"     # All invalid
            ],
            "description": "Invalid date values or formats"
        },
        "edge_cases": {
            "tests": [
                "02/29/2023",    # Not a leap year
                "02/29/2024",    # Leap year
                "01/01/1900",    # Very old
                "01/01/2050",    # Future
                "12/31/1999",    # Y2K edge
                "01/01/2000",    # Y2K edge
                "01/01/0001",    # Minimum date
                "12/31/9999"     # Maximum date
            ],
            "description": "Edge case dates"
        }
    },
    "address_fields": {
        "zip_codes": {
            "tests": [
                "1234",          # Too short
                "123456",        # Too long
                "ABCDE",         # Letters
                "12345-",        # Incomplete ZIP+4
                "12345-123",     # Invalid ZIP+4
                "12345-ABCD",    # Letters in ZIP+4
                "00000",         # All zeros
                "99999",         # All nines
                "12345-0000"     # Zero extension
            ],
            "description": "Invalid ZIP code formats"
        },
        "states": {
            "tests": [
                "XX",            # Invalid state
                "California",    # Full name instead of abbreviation
                "ca",            # Lowercase
                "C",             # Single letter
                "CAL",           # Three letters
                "US",            # Country code
                "123",           # Numbers
                ""               # Empty
            ],
            "description": "Invalid state codes"
        }
    },
    "file_upload": {
        "invalid_files": {
            "tests": [
                "test.exe",
                "test.bat",
                "test.sh",
                "test.js",
                "test.html",
                "very_large_file_100MB.pdf",
                "corrupted_file.pdf",
                "empty_file.pdf",
                "file_without_extension",
                ".hidden_file"
            ],
            "description": "Invalid file types or problematic files"
        }
    }
}

def generate_test_report():
    """Generate a comprehensive test report with all test cases"""
    report = []
    report.append("# Comprehensive Field Validation Test Cases")
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n## Test Instructions")
    report.append("\n1. Open the job application form at http://localhost:3001")
    report.append("2. For each field, test with the provided test cases")
    report.append("3. Record the behavior in the checklist")
    report.append("4. Note any unexpected behaviors or security concerns")
    
    report.append("\n## Personal Information Step")
    
    # First Name Field
    report.append("\n### First Name Field")
    report.append("\n#### Empty Values")
    for test in TEST_DATA["text_fields"]["empty_values"]["tests"]:
        report.append(f"- [ ] Input: `{repr(test)}` - Expected: Show 'First name is required' error")
    
    report.append("\n#### Special Characters")
    for test in TEST_DATA["text_fields"]["special_chars"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Either sanitize or show 'Invalid characters' error")
    
    report.append("\n#### SQL Injection")
    for test in TEST_DATA["text_fields"]["sql_injection"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Sanitize/escape or reject with error")
    
    report.append("\n#### XSS Attempts")
    for test in TEST_DATA["text_fields"]["xss_attempts"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Sanitize HTML tags or reject")
    
    report.append("\n#### Very Long Input")
    report.append(f"- [ ] Input: `{'A' * 100}` - Expected: Accept or show max length error")
    report.append(f"- [ ] Input: `{'A' * 500}` - Expected: Enforce max length limit")
    
    # Email Field
    report.append("\n### Email Field")
    report.append("\n#### Invalid Formats")
    for test in TEST_DATA["email_fields"]["invalid"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Show 'Invalid email format' error")
    
    report.append("\n#### Missing @ Symbol")
    for test in TEST_DATA["email_fields"]["missing_at"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Show 'Invalid email format' error")
    
    report.append("\n#### Multiple @ Symbols")
    for test in TEST_DATA["email_fields"]["multiple_at"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Show 'Invalid email format' error")
    
    # Phone Field
    report.append("\n### Phone Field")
    report.append("\n#### Invalid Formats")
    for test in TEST_DATA["phone_fields"]["invalid_formats"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Show 'Invalid phone number' error or format correctly")
    
    report.append("\n#### International Formats")
    for test in TEST_DATA["phone_fields"]["international"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Accept or format to standard format")
    
    # Address Fields
    report.append("\n### Address Fields")
    report.append("\n#### ZIP Code")
    for test in TEST_DATA["address_fields"]["zip_codes"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Show 'Invalid ZIP code' error")
    
    report.append("\n#### State")
    for test in TEST_DATA["address_fields"]["states"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Show 'Invalid state' error or convert to valid state code")
    
    # SSN Field (if present)
    report.append("\n### SSN Field")
    for test in TEST_DATA["ssn_fields"]["invalid_formats"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Show 'Invalid SSN format' error")
    
    # Date Fields
    report.append("\n### Date of Birth Field")
    report.append("\n#### Invalid Dates")
    for test in TEST_DATA["date_fields"]["invalid_dates"]["tests"]:
        report.append(f"- [ ] Input: `{test}` - Expected: Show 'Invalid date' error or prevent selection")
    
    report.append("\n#### Future Dates")
    report.append("- [ ] Input: `01/01/2030` - Expected: Show 'Birth date cannot be in the future' error")
    report.append("- [ ] Input: Today's date - Expected: Show error or warning for unlikely birth date")
    
    # Cross-Field Validation
    report.append("\n## Cross-Field Validation Tests")
    report.append("\n### Email Confirmation")
    report.append("- [ ] Different emails in 'Email' and 'Confirm Email' - Expected: Show 'Emails do not match' error")
    report.append("- [ ] Copy-paste same email - Expected: Accept")
    
    report.append("\n### Phone Number Consistency")
    report.append("- [ ] Enter phone in different formats across forms - Expected: Store in consistent format")
    
    report.append("\n### SSN Consistency")
    report.append("- [ ] Enter different SSN in I-9 vs W-4 forms - Expected: Flag inconsistency or use single source")
    
    # Security Tests
    report.append("\n## Security Tests")
    report.append("\n### Form Submission")
    report.append("- [ ] Submit form with browser dev tools network throttling - Expected: Handle timeout gracefully")
    report.append("- [ ] Submit form multiple times rapidly - Expected: Prevent duplicate submissions")
    report.append("- [ ] Modify hidden fields via browser dev tools - Expected: Validate on server side")
    report.append("- [ ] Submit form with very large payload - Expected: Reject oversized requests")
    
    # File Upload Tests
    report.append("\n## File Upload Tests")
    report.append("\n### Invalid File Types")
    for test in TEST_DATA["file_upload"]["invalid_files"]["tests"]:
        report.append(f"- [ ] Upload: `{test}` - Expected: Show 'Invalid file type' error")
    
    report.append("\n### File Size")
    report.append("- [ ] Upload 50MB file - Expected: Show 'File too large' error")
    report.append("- [ ] Upload 0 byte file - Expected: Show 'File is empty' error")
    
    # Save test results template
    report.append("\n## Test Results Summary")
    report.append("\n### Issues Found")
    report.append("\n#### Critical (Security)")
    report.append("1. [Field Name] - [Issue description]")
    report.append("   - Input: `[test input]`")
    report.append("   - Expected: [expected behavior]")
    report.append("   - Actual: [actual behavior]")
    report.append("   - Impact: [security/data integrity impact]")
    report.append("   - Fix: [recommended fix]")
    
    report.append("\n#### High (Data Integrity)")
    report.append("1. [Field Name] - [Issue description]")
    
    report.append("\n#### Medium (User Experience)")
    report.append("1. [Field Name] - [Issue description]")
    
    report.append("\n#### Low (Enhancement)")
    report.append("1. [Field Name] - [Issue description]")
    
    return "\n".join(report)

def generate_automated_test_script():
    """Generate a Cypress/Playwright test script"""
    script = []
    script.append("// Automated Field Validation Tests for Job Application Form")
    script.append("// This script can be adapted for Cypress, Playwright, or Selenium")
    script.append("")
    script.append("describe('Job Application Form - Field Validation', () => {")
    script.append("  beforeEach(() => {")
    script.append("    cy.visit('http://localhost:3001/apply/{property_id}');")
    script.append("  });")
    script.append("")
    script.append("  describe('Personal Information Fields', () => {")
    script.append("    it('should validate first name field', () => {")
    script.append("      // Test empty value")
    script.append("      cy.get('[name=\"firstName\"]').clear().blur();")
    script.append("      cy.contains('First name is required').should('be.visible');")
    script.append("      ")
    script.append("      // Test special characters")
    script.append("      cy.get('[name=\"firstName\"]').type('<script>alert(\"xss\")</script>');")
    script.append("      cy.get('[name=\"firstName\"]').should('not.contain', '<script>');")
    script.append("    });")
    script.append("    ")
    script.append("    it('should validate email field', () => {")
    script.append("      // Test invalid email")
    script.append("      cy.get('[name=\"email\"]').type('invalid.email');")
    script.append("      cy.contains('Invalid email format').should('be.visible');")
    script.append("    });")
    script.append("  });")
    script.append("});")
    
    return "\n".join(script)

if __name__ == "__main__":
    # Generate test report
    report = generate_test_report()
    report_filename = f"field_validation_test_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Test cases report generated: {report_filename}")
    
    # Generate automated test script
    script = generate_automated_test_script()
    script_filename = f"field_validation_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"
    
    with open(script_filename, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"Automated test script template generated: {script_filename}")
    
    # Print summary
    total_tests = sum(len(category["tests"]) for field_type in TEST_DATA.values() 
                     for category in field_type.values())
    print(f"\nTotal test cases generated: {total_tests}")
    print("\nNext steps:")
    print("1. Open the test cases report and use it as a checklist")
    print("2. Manually test each case and record results")
    print("3. Or adapt the automated test script for your testing framework")