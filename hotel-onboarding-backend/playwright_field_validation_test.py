#!/usr/bin/env python3
"""
Playwright-based Field Validation Testing
Automated browser testing for comprehensive field validation
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
try:
    from playwright.async_api import async_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Install with: pip install playwright && playwright install")

# Test configuration
FRONTEND_URL = "http://localhost:3001"
PROPERTY_ID = "550e8400-e29b-41d4-a716-446655440001"

class PlaywrightFieldTester:
    def __init__(self):
        self.results = []
        self.page = None
        self.browser = None
        
    def log_result(self, field: str, test_type: str, input_value: str, 
                   expected: str, actual: str, status: str, impact: str = "Low"):
        """Log a test result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "field": field,
            "test_type": test_type,
            "input_value": str(input_value)[:100],
            "expected": expected,
            "actual": actual,
            "status": status,
            "impact": impact
        }
        self.results.append(result)
        
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {field} - {test_type}: {status}")
        if status != "PASS":
            print(f"   Input: {repr(input_value)[:50]}...")
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}\n")
    
    async def test_field(self, selector: str, test_values: List[str], 
                        field_name: str, test_type: str):
        """Test a specific field with various inputs"""
        for value in test_values:
            try:
                # Clear and fill field
                await self.page.fill(selector, "")
                await self.page.fill(selector, value)
                await self.page.press(selector, "Tab")  # Trigger blur
                
                # Wait a bit for validation
                await self.page.wait_for_timeout(100)
                
                # Look for error messages
                error_selectors = [
                    f"{selector} ~ .text-red-500",
                    f"{selector} ~ .error-message",
                    f".field-error[data-field='{field_name}']",
                    f"{selector} + .text-destructive"
                ]
                
                error_text = None
                for error_selector in error_selectors:
                    try:
                        error_element = await self.page.query_selector(error_selector)
                        if error_element:
                            error_text = await error_element.text_content()
                            break
                    except:
                        continue
                
                # Determine test result
                if test_type == "empty" and not error_text:
                    self.log_result(field_name, test_type, value,
                                  "Should show required field error",
                                  "No error shown", "FAIL", "High")
                elif test_type in ["sql", "xss"] and not error_text:
                    self.log_result(field_name, test_type, value,
                                  "Should sanitize or reject dangerous input",
                                  "Input accepted without validation", "WARNING", "Critical")
                elif test_type == "invalid" and not error_text:
                    self.log_result(field_name, test_type, value,
                                  "Should show validation error",
                                  "Invalid input accepted", "FAIL", "Medium")
                else:
                    self.log_result(field_name, test_type, value,
                                  "Appropriate validation",
                                  error_text or "Accepted", "PASS")
                
            except Exception as e:
                self.log_result(field_name, test_type, value,
                              "Field should be testable",
                              f"Error: {str(e)}", "FAIL", "Low")
    
    async def test_personal_information_step(self):
        """Test the personal information step"""
        print("\n" + "="*60)
        print("TESTING PERSONAL INFORMATION STEP")
        print("="*60)
        
        # Navigate to application form
        await self.page.goto(f"{FRONTEND_URL}/apply/{PROPERTY_ID}")
        await self.page.wait_for_load_state("networkidle")
        
        # Test first name
        print("\n--- Testing First Name ---")
        await self.test_field(
            "input[name='first_name']",
            ["", " ", "<script>alert('xss')</script>", "'; DROP TABLE users; --", "A"*500],
            "first_name",
            "various"
        )
        
        # Test email
        print("\n--- Testing Email ---")
        await self.test_field(
            "input[name='email']",
            ["notanemail", "test@", "@test.com", "test@@test.com", "test..user@test.com"],
            "email",
            "invalid"
        )
        
        # Test phone
        print("\n--- Testing Phone ---")
        await self.test_field(
            "input[name='phone']",
            ["123", "abcdef", "123-abc-4567"],
            "phone",
            "invalid"
        )
        
        # Test ZIP code
        print("\n--- Testing ZIP Code ---")
        await self.test_field(
            "input[name='zip_code']",
            ["1234", "123456", "ABCDE", "12345-"],
            "zip_code",
            "invalid"
        )
    
    async def test_cross_field_validation(self):
        """Test cross-field validation scenarios"""
        print("\n" + "="*60)
        print("TESTING CROSS-FIELD VALIDATION")
        print("="*60)
        
        # Fill valid data first
        await self.page.fill("input[name='first_name']", "John")
        await self.page.fill("input[name='last_name']", "Doe")
        await self.page.fill("input[name='email']", "john.doe@example.com")
        await self.page.fill("input[name='phone']", "(555) 123-4567")
        
        # Test email confirmation if exists
        email_confirm = await self.page.query_selector("input[name='email_confirm']")
        if email_confirm:
            await self.page.fill("input[name='email_confirm']", "different@example.com")
            await self.page.press("input[name='email_confirm']", "Tab")
            await self.page.wait_for_timeout(100)
            
            # Check for mismatch error
            error = await self.page.query_selector("input[name='email_confirm'] ~ .text-red-500")
            if error:
                error_text = await error.text_content()
                self.log_result("email_confirm", "mismatch", "different@example.com",
                              "Should show mismatch error", error_text, "PASS")
            else:
                self.log_result("email_confirm", "mismatch", "different@example.com",
                              "Should show mismatch error", "No error shown", "FAIL", "Medium")
    
    async def test_navigation_with_invalid_data(self):
        """Test if user can navigate to next step with invalid data"""
        print("\n" + "="*60)
        print("TESTING NAVIGATION VALIDATION")
        print("="*60)
        
        # Leave required fields empty
        await self.page.fill("input[name='first_name']", "")
        await self.page.fill("input[name='last_name']", "")
        
        # Try to proceed to next step
        next_button = await self.page.query_selector("button:has-text('Next')")
        if next_button:
            await next_button.click()
            await self.page.wait_for_timeout(500)
            
            # Check if we're still on the same step
            current_url = self.page.url
            if "personal" in current_url.lower():
                self.log_result("navigation", "invalid_data", "empty required fields",
                              "Should prevent navigation with invalid data",
                              "Navigation correctly prevented", "PASS")
            else:
                self.log_result("navigation", "invalid_data", "empty required fields",
                              "Should prevent navigation with invalid data",
                              "Allowed navigation with invalid data", "FAIL", "High")
    
    async def run_all_tests(self):
        """Run all field validation tests"""
        if not PLAYWRIGHT_AVAILABLE:
            print("Playwright is not installed. Please install it first.")
            return
        
        print("🚀 Starting Playwright Field Validation Testing")
        print("=" * 60)
        
        async with async_playwright() as p:
            # Launch browser
            self.browser = await p.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            
            try:
                # Run test suites
                await self.test_personal_information_step()
                await self.test_cross_field_validation()
                await self.test_navigation_with_invalid_data()
                
            except Exception as e:
                print(f"Error during testing: {e}")
            finally:
                await self.browser.close()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        report_lines = []
        report_lines.append("# Frontend Field Validation Test Report")
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Tests: {len(self.results)}")
        
        # Summary
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        warnings = len([r for r in self.results if r["status"] == "WARNING"])
        
        report_lines.append(f"\n## Summary")
        report_lines.append(f"- ✅ Passed: {passed}")
        report_lines.append(f"- ❌ Failed: {failed}")
        report_lines.append(f"- ⚠️ Warnings: {warnings}")
        
        # Critical issues
        critical = [r for r in self.results if r["impact"] == "Critical"]
        if critical:
            report_lines.append(f"\n## 🚨 Critical Issues ({len(critical)})")
            for issue in critical:
                report_lines.append(f"\n### {issue['field']} - {issue['test_type']}")
                report_lines.append(f"- Input: `{issue['input_value']}`")
                report_lines.append(f"- Expected: {issue['expected']}")
                report_lines.append(f"- Actual: {issue['actual']}")
        
        # Save report
        report = "\n".join(report_lines)
        filename = f"playwright_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {filename}")

# Alternative manual testing approach
def generate_manual_test_instructions():
    """Generate manual testing instructions"""
    instructions = """
# Manual Field Validation Testing Instructions

## Setup
1. Open browser to http://localhost:3001
2. Navigate to job application form
3. Open browser developer console (F12)

## Test Each Field

### Personal Information Fields

#### First Name
1. Leave empty and tab out → Should show "First name is required"
2. Enter `<script>alert('xss')</script>` → Should sanitize or reject
3. Enter `'; DROP TABLE users; --` → Should sanitize or reject
4. Enter 500 A's → Should enforce max length
5. Enter `😀😃😄` → Should accept or show clear error
6. Enter `José` → Should accept accented characters

#### Email
1. Enter `notanemail` → Should show "Invalid email format"
2. Enter `test@` → Should show error
3. Enter `test@@test.com` → Should show error
4. Enter `test..user@test.com` → Should show error
5. Enter `test user@test.com` → Should show error

#### Phone
1. Enter `123` → Should show "Invalid phone number"
2. Enter `abcdefghij` → Should show error
3. Enter `123-abc-4567` → Should show error
4. Enter `(555) 123-4567` → Should accept and format

#### ZIP Code
1. Enter `1234` → Should show "Invalid ZIP code"
2. Enter `ABCDE` → Should show error
3. Enter `12345-` → Should show error or autocomplete
4. Enter `12345` → Should accept
5. Enter `12345-6789` → Should accept

### Cross-Field Validation

1. If email confirmation exists:
   - Enter different emails → Should show mismatch error
   
2. Navigation validation:
   - Leave required fields empty
   - Click Next → Should prevent navigation

### Security Testing

1. Open Network tab in dev tools
2. Submit form with XSS payload
3. Check if payload is sanitized in request
4. Check response for any reflected input

## What to Look For

✅ Good:
- Clear, immediate error messages
- Prevents navigation with invalid data
- Sanitizes dangerous input
- Consistent validation across fields

❌ Bad:
- No validation on required fields
- Accepts SQL/XSS without sanitization
- Allows navigation with invalid data
- Stores dangerous input as-is
"""
    
    filename = f"manual_test_instructions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, 'w') as f:
        f.write(instructions)
    
    print(f"📋 Manual test instructions saved to: {filename}")

if __name__ == "__main__":
    if PLAYWRIGHT_AVAILABLE:
        # Run automated tests
        tester = PlaywrightFieldTester()
        asyncio.run(tester.run_all_tests())
    else:
        # Generate manual test instructions
        print("Generating manual test instructions instead...")
        generate_manual_test_instructions()