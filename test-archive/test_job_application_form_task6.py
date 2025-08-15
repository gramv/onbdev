#!/usr/bin/env python3
"""
Test script for Task 6: Update Job Application Form Route
Tests the updated JobApplicationForm to ensure it works with new endpoints
"""

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"
TEST_PROPERTY_ID = "prop_test_001"

def test_backend_endpoints():
    """Test that the backend endpoints are working correctly"""
    print("🧪 Testing Backend Endpoints...")
    
    # Test 1: Property info endpoint
    print("1. Testing /properties/{property_id}/info endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "property" in data, "Response missing 'property' field"
        assert "departments_and_positions" in data, "Response missing 'departments_and_positions' field"
        assert "application_url" in data, "Response missing 'application_url' field"
        assert "is_accepting_applications" in data, "Response missing 'is_accepting_applications' field"
        
        property_info = data["property"]
        assert property_info["id"] == TEST_PROPERTY_ID, "Property ID mismatch"
        assert "name" in property_info, "Property missing 'name' field"
        assert "address" in property_info, "Property missing 'address' field"
        
        print("   ✅ Property info endpoint working correctly")
        print(f"   📍 Property: {property_info['name']}")
        print(f"   🏢 Address: {property_info['address']}")
        print(f"   🏷️ Departments: {list(data['departments_and_positions'].keys())}")
        
    except Exception as e:
        print(f"   ❌ Property info endpoint failed: {e}")
        return False
    
    # Test 2: Application submission endpoint
    print("2. Testing /apply/{property_id} endpoint...")
    try:
        test_application = {
            "first_name": "Test",
            "last_name": "Applicant",
            "email": "test.task6@example.com",
            "phone": "5551234567",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "zip_code": "12345",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-01",
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
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "success" in data, "Response missing 'success' field"
        assert data["success"] == True, "Application submission not successful"
        assert "application_id" in data, "Response missing 'application_id' field"
        assert "message" in data, "Response missing 'message' field"
        
        print("   ✅ Application submission endpoint working correctly")
        print(f"   📝 Application ID: {data['application_id']}")
        print(f"   💬 Message: {data['message']}")
        
    except Exception as e:
        print(f"   ❌ Application submission endpoint failed: {e}")
        return False
    
    return True

def test_frontend_form():
    """Test the frontend form using Selenium"""
    print("\n🌐 Testing Frontend Form...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        # Navigate to the job application form
        form_url = f"{FRONTEND_URL}/apply/{TEST_PROPERTY_ID}"
        print(f"1. Navigating to: {form_url}")
        driver.get(form_url)
        
        # Wait for the form to load
        wait = WebDriverWait(driver, 10)
        
        # Check if property information loaded
        print("2. Checking if property information loaded...")
        try:
            property_name = wait.until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Apply for a position at')]"))
            )
            print(f"   ✅ Property information loaded: {property_name.text}")
        except TimeoutException:
            print("   ❌ Property information did not load")
            return False
        
        # Fill out the form
        print("3. Filling out the form...")
        
        # Personal Information
        driver.find_element(By.ID, "first_name").send_keys("John")
        driver.find_element(By.ID, "last_name").send_keys("Doe")
        driver.find_element(By.ID, "email").send_keys("john.doe.task6@example.com")
        driver.find_element(By.ID, "phone").send_keys("5551234567")
        driver.find_element(By.ID, "address").send_keys("456 Test Avenue")
        
        # City dropdown
        city_dropdown = Select(driver.find_element(By.XPATH, "//select[contains(@class, 'city') or @id='city']"))
        city_dropdown.select_by_visible_text("New York")
        
        # State dropdown
        state_dropdown = Select(driver.find_element(By.XPATH, "//select[contains(@class, 'state') or @id='state']"))
        state_dropdown.select_by_visible_text("NY")
        
        driver.find_element(By.ID, "zip_code").send_keys("10001")
        
        # Department and Position
        print("4. Selecting department and position...")
        
        # Wait for departments to load and select one
        department_trigger = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'SelectTrigger') and contains(., 'Select department')]"))
        )
        department_trigger.click()
        
        # Select Front Desk department
        front_desk_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and text()='Front Desk']"))
        )
        front_desk_option.click()
        
        # Wait a moment for positions to load
        time.sleep(1)
        
        # Select position
        position_trigger = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'SelectTrigger') and contains(., 'Select position')]"))
        )
        position_trigger.click()
        
        position_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and text()='Front Desk Agent']"))
        )
        position_option.click()
        
        # Work Authorization
        print("5. Filling work authorization...")
        
        work_auth_trigger = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'SelectTrigger') and contains(., 'Select') and ancestor::*[contains(., 'Authorized to work')]]"))
        )
        work_auth_trigger.click()
        
        yes_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and text()='Yes']"))
        )
        yes_option.click()
        
        # Sponsorship
        sponsorship_trigger = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'SelectTrigger') and contains(., 'Select') and ancestor::*[contains(., 'Require sponsorship')]]"))
        )
        sponsorship_trigger.click()
        
        no_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and text()='No']"))
        )
        no_option.click()
        
        # Availability
        print("6. Filling availability information...")
        
        driver.find_element(By.ID, "start_date").send_keys("2025-08-01")
        
        # Shift preference
        shift_trigger = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'SelectTrigger') and contains(., 'Select shift')]"))
        )
        shift_trigger.click()
        
        morning_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and text()='Morning']"))
        )
        morning_option.click()
        
        # Employment type
        employment_trigger = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'SelectTrigger') and contains(., 'Select type')]"))
        )
        employment_trigger.click()
        
        fulltime_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and text()='Full-time']"))
        )
        fulltime_option.click()
        
        # Experience
        print("7. Filling experience information...")
        
        # Years of experience
        exp_trigger = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'SelectTrigger') and contains(., 'Select experience')]"))
        )
        exp_trigger.click()
        
        exp_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and text()='2-5 years']"))
        )
        exp_option.click()
        
        # Hotel experience
        hotel_exp_trigger = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'SelectTrigger') and ancestor::*[contains(., 'Previous Hotel Experience')]]"))
        )
        hotel_exp_trigger.click()
        
        hotel_yes_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and text()='Yes']"))
        )
        hotel_yes_option.click()
        
        # Submit the form
        print("8. Submitting the form...")
        
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        # Wait for success message
        try:
            success_message = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Application Submitted')]"))
            )
            print("   ✅ Form submitted successfully!")
            print(f"   💬 Success message found: {success_message.text}")
            return True
            
        except TimeoutException:
            print("   ❌ Success message not found after form submission")
            # Check for any error messages
            try:
                error_message = driver.find_element(By.XPATH, "//*[contains(@class, 'alert') or contains(@class, 'error')]")
                print(f"   ⚠️ Error message: {error_message.text}")
            except:
                print("   ⚠️ No success or error message found")
            return False
            
    except Exception as e:
        print(f"   ❌ Frontend form test failed: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()

def main():
    """Run all tests for Task 6"""
    print("🚀 Testing Task 6: Update Job Application Form Route")
    print("=" * 60)
    
    # Test backend endpoints
    backend_success = test_backend_endpoints()
    
    if not backend_success:
        print("\n❌ Backend tests failed. Cannot proceed with frontend tests.")
        return False
    
    # Test frontend form
    frontend_success = test_frontend_form()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Backend Endpoints: {'✅ PASS' if backend_success else '❌ FAIL'}")
    print(f"Frontend Form: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    overall_success = backend_success and frontend_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Task 6 implementation is working correctly!")
        print("✅ JobApplicationForm successfully updated to use new endpoints")
        print("✅ Form works without authentication")
        print("✅ Property info fetched from /properties/{property_id}/info")
        print("✅ Applications submitted to /apply/{property_id}")
    else:
        print("\n⚠️ Task 6 implementation needs attention.")
    
    return overall_success

if __name__ == "__main__":
    main()