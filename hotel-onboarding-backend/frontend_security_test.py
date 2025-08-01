"""
Frontend Security Testing for Job Application Form using Selenium
Tests XSS, client-side validation bypass, and UI vulnerabilities
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from security_test_payloads import get_all_payloads

class FrontendSecurityTester:
    def __init__(self, base_url: str = "http://localhost:3000", property_id: str = "property123"):
        self.base_url = base_url
        self.property_id = property_id
        self.payloads = get_all_payloads()
        self.test_results = []
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with security testing options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Enable console log collection
        caps = webdriver.DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'browser': 'ALL', 'performance': 'ALL'}
        
        self.driver = webdriver.Chrome(options=options, desired_capabilities=caps)
        self.driver.set_window_size(1280, 1024)
        
    def teardown_driver(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            
    def check_for_xss_alert(self) -> bool:
        """Check if an XSS alert was triggered"""
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            return True, alert_text
        except NoAlertPresentException:
            return False, None
            
    def get_console_errors(self) -> list:
        """Get browser console errors"""
        logs = self.driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        return errors
        
    def test_field_with_payload(self, field_selector: str, field_name: str, 
                               payload: str, payload_type: str) -> dict:
        """Test a single field with a payload"""
        result = {
            'field': field_name,
            'selector': field_selector,
            'payload': payload,
            'payload_type': payload_type,
            'client_validation_bypassed': False,
            'xss_triggered': False,
            'console_errors': [],
            'stored_in_dom': False,
            'persisted_after_navigation': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Find and clear the field
            element = self.driver.find_element(By.CSS_SELECTOR, field_selector)
            element.clear()
            
            # Enter the payload
            element.send_keys(payload)
            
            # Trigger validation by tabbing out
            element.send_keys(Keys.TAB)
            time.sleep(0.5)
            
            # Check if payload is still in the field (validation didn't clear it)
            current_value = element.get_attribute('value')
            if current_value == payload:
                result['client_validation_bypassed'] = True
                
            # Check for XSS alert
            xss_triggered, alert_text = self.check_for_xss_alert()
            if xss_triggered:
                result['xss_triggered'] = True
                result['alert_text'] = alert_text
                
            # Check console errors
            result['console_errors'] = self.get_console_errors()
            
            # Check if payload appears in DOM unescaped
            page_source = self.driver.page_source
            if payload in page_source and '<script>' in payload:
                result['stored_in_dom'] = True
                
            # Try to move to next step to see if validation allows it
            try:
                next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
                if next_button.is_enabled():
                    result['next_button_enabled'] = True
            except:
                pass
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
        
    def test_step_1_personal_info(self):
        """Test Step 1: Personal Information fields"""
        print("\n[Step 1] Testing Personal Information...")
        
        # Wait for form to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "first_name"))
        )
        
        # Test XSS in text fields
        text_fields = [
            ("#first_name", "first_name"),
            ("#last_name", "last_name"),
            ("#email", "email"),
            ("#address", "address"),
            ("#city", "city")
        ]
        
        for selector, field_name in text_fields:
            # Test with XSS payload
            for payload in self.payloads['xss'][:3]:
                result = self.test_field_with_payload(selector, field_name, payload, "XSS")
                self.test_results.append(result)
                if result['xss_triggered'] or result['client_validation_bypassed']:
                    print(f"  ⚠️  {field_name}: XSS payload accepted/triggered")
                    
            # Test with SQL injection
            for payload in self.payloads['sql_injection'][:2]:
                result = self.test_field_with_payload(selector, field_name, payload, "SQL Injection")
                self.test_results.append(result)
                if result['client_validation_bypassed']:
                    print(f"  ⚠️  {field_name}: SQL injection payload accepted")
                    
        # Test phone field with format bypass
        for payload in self.payloads['format_bypass']['phone'][:3]:
            result = self.test_field_with_payload("#phone", "phone", payload, "Format Bypass")
            self.test_results.append(result)
            if result['client_validation_bypassed']:
                print(f"  ⚠️  phone: Invalid format accepted: {payload}")
                
        # Test email with invalid formats
        for payload in self.payloads['format_bypass']['email'][:3]:
            result = self.test_field_with_payload("#email", "email", payload, "Format Bypass")
            self.test_results.append(result)
            if result['client_validation_bypassed']:
                print(f"  ⚠️  email: Invalid format accepted: {payload}")
                
        # Test ZIP with invalid formats
        for payload in self.payloads['format_bypass']['zip'][:3]:
            result = self.test_field_with_payload("#zip_code", "zip_code", payload, "Format Bypass")
            self.test_results.append(result)
            if result['client_validation_bypassed']:
                print(f"  ⚠️  zip_code: Invalid format accepted: {payload}")
                
    def test_date_validation(self):
        """Test date field validation"""
        print("\n[Date Validation] Testing date fields...")
        
        # Navigate to Position & Availability step
        # First fill required fields in step 1
        self.fill_valid_step_1()
        
        # Click next
        next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
        next_button.click()
        time.sleep(1)
        
        # Test start_date with invalid dates
        for payload in self.payloads['format_bypass']['date'][:5]:
            try:
                date_field = self.driver.find_element(By.ID, "start_date")
                date_field.clear()
                date_field.send_keys(payload)
                date_field.send_keys(Keys.TAB)
                
                current_value = date_field.get_attribute('value')
                if current_value == payload:
                    print(f"  ⚠️  start_date: Invalid date accepted: {payload}")
                    self.test_results.append({
                        'field': 'start_date',
                        'payload': payload,
                        'payload_type': 'Invalid Date',
                        'client_validation_bypassed': True,
                        'timestamp': datetime.now().isoformat()
                    })
            except:
                pass
                
    def fill_valid_step_1(self):
        """Fill step 1 with valid data to proceed"""
        fields = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "(555) 123-4567",
            "address": "123 Test St",
            "city": "Test City",
            "zip_code": "12345"
        }
        
        for field_id, value in fields.items():
            element = self.driver.find_element(By.ID, field_id)
            element.clear()
            element.send_keys(value)
            
        # Select state
        state_select = Select(self.driver.find_element(By.ID, "state"))
        state_select.select_by_value("CA")
        
        # Check age verification
        age_checkbox = self.driver.find_element(By.ID, "age_verification")
        if not age_checkbox.is_selected():
            age_checkbox.click()
            
        # Select work authorization
        work_auth_yes = self.driver.find_element(By.ID, "work_auth_yes")
        work_auth_yes.click()
        
        # Select sponsorship
        sponsor_no = self.driver.find_element(By.ID, "sponsor_no")
        sponsor_no.click()
        
        # Select transportation
        transport_yes = self.driver.find_element(By.ID, "transport_yes")
        transport_yes.click()
        
        time.sleep(0.5)
        
        # Select transportation method
        transport_method = self.driver.find_element(By.ID, "method_own")
        transport_method.click()
        
    def test_file_upload_security(self):
        """Test file upload security in Document Upload step"""
        print("\n[File Upload] Testing file upload security...")
        
        # This would require navigating to the document upload step
        # and testing with malicious file names and content
        # Placeholder for now as it requires more complex file handling
        
    def test_stored_xss(self):
        """Test for stored XSS by submitting and reviewing data"""
        print("\n[Stored XSS] Testing stored XSS vulnerabilities...")
        
        # Fill form with XSS payloads and try to submit
        # Then check if payloads are rendered unescaped in review step
        
    def run_all_tests(self):
        """Run all security tests"""
        print(f"Starting frontend security testing...")
        print(f"Testing URL: {self.base_url}/apply/{self.property_id}")
        print("-" * 80)
        
        try:
            # Navigate to the application form
            self.driver.get(f"{self.base_url}/apply/{self.property_id}")
            time.sleep(3)  # Wait for initial load
            
            # Test each step
            self.test_step_1_personal_info()
            self.test_date_validation()
            # Additional tests can be added here
            
        except Exception as e:
            print(f"Error during testing: {e}")
            
    def generate_report(self) -> str:
        """Generate frontend security test report"""
        report = []
        report.append("# Frontend Security Test Report - Job Application Form")
        report.append(f"\n**Test Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Application URL**: {self.base_url}/apply/{self.property_id}")
        report.append(f"**Total Tests**: {len(self.test_results)}")
        
        # Count vulnerabilities
        xss_triggered = [r for r in self.test_results if r.get('xss_triggered', False)]
        validation_bypassed = [r for r in self.test_results if r.get('client_validation_bypassed', False)]
        console_errors = [r for r in self.test_results if r.get('console_errors', [])]
        
        report.append(f"\n## Summary")
        report.append(f"- XSS Alerts Triggered: {len(xss_triggered)}")
        report.append(f"- Client Validation Bypassed: {len(validation_bypassed)}")
        report.append(f"- Console Errors Found: {len(console_errors)}")
        
        if xss_triggered:
            report.append(f"\n## Critical: XSS Vulnerabilities")
            for result in xss_triggered:
                report.append(f"\n**Field**: {result['field']}")
                report.append(f"**Payload**: `{result['payload']}`")
                report.append(f"**Alert Text**: {result.get('alert_text', 'N/A')}")
                
        if validation_bypassed:
            report.append(f"\n## Client-Side Validation Issues")
            for result in validation_bypassed[:10]:  # First 10
                report.append(f"- **{result['field']}** accepted: `{result['payload'][:50]}...`")
                
        report.append(f"\n## Recommendations")
        report.append("1. Implement Content Security Policy (CSP) headers")
        report.append("2. Use DOMPurify or similar library for input sanitization")
        report.append("3. Escape all user input when rendering")
        report.append("4. Implement server-side validation for all inputs")
        report.append("5. Use React's built-in XSS protection properly")
        
        return "\n".join(report)


def main():
    tester = FrontendSecurityTester()
    tester.setup_driver()
    
    try:
        tester.run_all_tests()
        report = tester.generate_report()
        
        with open('/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-backend/frontend_security_test_report.md', 'w') as f:
            f.write(report)
            
        print(f"\n✅ Frontend security test report saved")
        print(f"Total tests: {len(tester.test_results)}")
        
    finally:
        tester.teardown_driver()


if __name__ == "__main__":
    main()