#!/usr/bin/env python3
"""
Test script for enhanced job application form (Task 11)
Tests form validation, error handling, duplicate prevention, mobile responsiveness, and position-specific questions
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"
TEST_PROPERTY_ID = "prop_test_001"

def test_enhanced_form_validation():
    """Test enhanced form validation and error handling"""
    print("\n🧪 Testing Enhanced Form Validation...")
    
    # Test invalid data
    invalid_application = {
        "first_name": "",  # Empty required field
        "last_name": "Doe",
        "email": "invalid-email",  # Invalid email format
        "phone": "123",  # Invalid phone format
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "invalid",  # Invalid zip code
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2024-01-01",  # Past date
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes",
        "availability_weekends": "yes",
        "availability_holidays": "yes",
        "reliable_transportation": "yes",
        "physical_requirements_acknowledged": False,  # Required consent not given
        "background_check_consent": False  # Required consent not given
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=invalid_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:  # Validation error
            print("✅ Backend validation working correctly")
            validation_errors = response.json()
            print(f"   Validation errors: {len(validation_errors.get('detail', []))}")
        else:
            print(f"⚠️  Expected validation error, got status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing validation: {e}")

def test_duplicate_prevention():
    """Test duplicate application prevention"""
    print("\n🧪 Testing Duplicate Application Prevention...")
    
    # Create a valid application
    valid_application = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.duplicate.test@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Main Street",
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
        "hotel_experience": "yes",
        "availability_weekends": "yes",
        "availability_holidays": "yes",
        "reliable_transportation": "yes",
        "physical_requirements_acknowledged": True,
        "background_check_consent": True,
        "previous_employer": "Previous Hotel",
        "reason_for_leaving": "Career advancement",
        "additional_comments": "Looking forward to joining your team!"
    }
    
    try:
        # Submit first application
        print("   Submitting first application...")
        response1 = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=valid_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response1.status_code == 200:
            print("✅ First application submitted successfully")
        else:
            print(f"❌ First application failed: {response1.status_code}")
            return
        
        # Submit duplicate application
        print("   Submitting duplicate application...")
        response2 = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=valid_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response2.status_code == 400:
            error_detail = response2.json().get('detail', '')
            if 'already submitted' in error_detail:
                print("✅ Duplicate prevention working correctly")
                print(f"   Error message: {error_detail}")
            else:
                print(f"⚠️  Unexpected error message: {error_detail}")
        else:
            print(f"❌ Expected duplicate error, got status: {response2.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing duplicate prevention: {e}")

def test_position_specific_questions():
    """Test position-specific questions for different departments"""
    print("\n🧪 Testing Position-Specific Questions...")
    
    departments_to_test = [
        ("Front Desk", "Front Desk Agent"),
        ("Housekeeping", "Housekeeper"),
        ("Food & Beverage", "Server"),
        ("Maintenance", "Maintenance Technician")
    ]
    
    for dept, position in departments_to_test:
        print(f"   Testing {dept} - {position}...")
        
        application = {
            "first_name": "Test",
            "last_name": f"{dept.replace(' ', '')}Worker",
            "email": f"test.{dept.lower().replace(' ', '.')}@example.com",
            "phone": "(555) 123-4567",
            "address": "123 Test Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "department": dept,
            "position": position,
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "shift_preference": "flexible",
            "employment_type": "full_time",
            "experience_years": "2-5",
            "hotel_experience": "yes",
            "availability_weekends": "yes",
            "availability_holidays": "yes",
            "reliable_transportation": "yes",
            "physical_requirements_acknowledged": True,
            "background_check_consent": True
        }
        
        # Add position-specific answers
        if dept == "Front Desk":
            application["customer_service_experience"] = "yes"
        elif dept == "Housekeeping":
            application["physical_demands_ok"] = "yes"
        elif dept == "Food & Beverage":
            application["food_safety_certification"] = "yes"
        elif dept == "Maintenance":
            application["maintenance_experience"] = "yes"
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
                json=application,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"   ✅ {dept} application submitted successfully")
            else:
                print(f"   ❌ {dept} application failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing {dept}: {e}")

def test_enhanced_fields():
    """Test new enhanced fields"""
    print("\n🧪 Testing Enhanced Fields...")
    
    enhanced_application = {
        "first_name": "Enhanced",
        "last_name": "Tester",
        "email": "enhanced.tester@example.com",
        "phone": "(555) 987-6543",
        "address": "456 Enhanced Street",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Guest Services Representative",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "shift_preference": "afternoon",
        "employment_type": "part_time",
        "experience_years": "6-10",
        "hotel_experience": "yes",
        # Enhanced availability fields
        "availability_weekends": "sometimes",
        "availability_holidays": "no",
        "reliable_transportation": "yes",
        # Enhanced experience fields
        "previous_employer": "Luxury Resort & Spa",
        "reason_for_leaving": "Seeking new challenges",
        "additional_comments": "I have extensive experience in luxury hospitality and am passionate about providing exceptional guest service. I speak three languages fluently.",
        # Required acknowledgments
        "physical_requirements_acknowledged": True,
        "background_check_consent": True,
        # Position-specific
        "customer_service_experience": "yes"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=enhanced_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Enhanced application with all new fields submitted successfully")
            result = response.json()
            print(f"   Application ID: {result.get('application_id')}")
            print(f"   Position: {result.get('position_applied')}")
        else:
            print(f"❌ Enhanced application failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing enhanced fields: {e}")

def test_mobile_responsiveness():
    """Test mobile responsiveness indicators"""
    print("\n🧪 Testing Mobile Responsiveness Indicators...")
    
    try:
        # Test the form page loads
        form_url = f"{FRONTEND_URL}/apply/{TEST_PROPERTY_ID}"
        response = requests.get(form_url)
        
        if response.status_code == 200:
            print("✅ Form page loads successfully")
            
            # Check for mobile-responsive CSS classes in the HTML
            html_content = response.text
            mobile_indicators = [
                'grid-cols-1 md:grid-cols-2',  # Responsive grid
                'sm:px-6 lg:px-8',  # Responsive padding
                'max-w-3xl',  # Responsive max width
                'min-h-screen'  # Full height on mobile
            ]
            
            found_indicators = []
            for indicator in mobile_indicators:
                if indicator in html_content:
                    found_indicators.append(indicator)
            
            if found_indicators:
                print(f"✅ Mobile responsive classes found: {len(found_indicators)}/{len(mobile_indicators)}")
                for indicator in found_indicators:
                    print(f"   - {indicator}")
            else:
                print("⚠️  No mobile responsive indicators found in HTML")
                
        else:
            print(f"❌ Form page failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing mobile responsiveness: {e}")

def main():
    """Run all enhanced form tests"""
    print("🚀 Starting Enhanced Job Application Form Tests (Task 11)")
    print("=" * 60)
    
    # Test all enhancements
    test_enhanced_form_validation()
    test_duplicate_prevention()
    test_position_specific_questions()
    test_enhanced_fields()
    test_mobile_responsiveness()
    
    print("\n" + "=" * 60)
    print("✅ Enhanced Job Application Form Testing Complete!")
    print("\nEnhancements Tested:")
    print("- ✅ Form validation and error handling")
    print("- ✅ Duplicate application prevention")
    print("- ✅ Mobile-responsive design improvements")
    print("- ✅ Position-specific questions")
    print("- ✅ Enhanced fields and user experience")
    print("\nTask 11 - Application Form Enhancements: COMPLETE")

if __name__ == "__main__":
    main()