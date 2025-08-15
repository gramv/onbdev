#!/usr/bin/env python3
"""
Test script for session management API endpoints
Tests the comprehensive onboarding session management functionality
"""

import requests
import json
import time
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_session_management():
    """Test the complete session management workflow"""
    print("🧪 Testing Session Management API Endpoints")
    print("=" * 50)
    
    # Test data
    test_employee_id = "test-employee-123"
    test_user_token = "test-user-token"
    
    # Headers for authentication
    headers = {
        "Authorization": f"Bearer {test_user_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test 1: Get onboarding session (should create new session)
        print("\n1. Testing GET /api/onboarding/session/{employee_id}")
        response = requests.get(f"{BASE_URL}/api/onboarding/session/{test_employee_id}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            session_data = response.json()
            print(f"✅ Session created/retrieved: {session_data['session']['id']}")
            print(f"   Current step: {session_data['session']['current_step']}")
            print(f"   Progress: {session_data['session']['progress_percentage']}%")
        else:
            print(f"❌ Error: {response.text}")
            return False
        
        # Test 2: Save step data (auto-save functionality)
        print("\n2. Testing POST /api/onboarding/session/{employee_id}/save")
        save_data = {
            "step": "personal-info",
            "form_data": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "555-123-4567"
            },
            "auto_save": True
        }
        response = requests.post(f"{BASE_URL}/api/onboarding/session/{test_employee_id}/save", 
                               headers=headers, json=save_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Data saved successfully")
        else:
            print(f"❌ Save failed: {response.text}")
        
        # Test 3: Get specific step data
        print("\n3. Testing GET /api/onboarding/session/{employee_id}/step/{step_name}")
        response = requests.get(f"{BASE_URL}/api/onboarding/session/{test_employee_id}/step/personal-info", 
                              headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            step_data = response.json()
            print(f"✅ Step data retrieved: {len(step_data['form_data'])} fields")
            print(f"   Can edit: {step_data['can_edit']}")
            print(f"   Is completed: {step_data['is_completed']}")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 4: Complete a step with federal compliance validation
        print("\n4. Testing POST /api/onboarding/session/{employee_id}/progress")
        progress_data = {
            "step": "personal-info",
            "form_data": {
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-15",
                "ssn": "123-45-6789",
                "email": "john.doe@example.com",
                "phone": "555-123-4567",
                "address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345"
            },
            "completed": True
        }
        response = requests.post(f"{BASE_URL}/api/onboarding/session/{test_employee_id}/progress", 
                               headers=headers, json=progress_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            progress_result = response.json()
            print("✅ Step completed successfully")
            print(f"   New progress: {progress_result['session']['progress_percentage']}%")
            print(f"   Next step: {progress_result['session']['current_step']}")
        else:
            print(f"❌ Progress update failed: {response.text}")
        
        # Test 5: Test federal compliance validation
        print("\n5. Testing POST /api/compliance/validate/personal-info")
        compliance_data = {
            "date_of_birth": "1990-01-15",
            "ssn": "123-45-6789"
        }
        response = requests.post(f"{BASE_URL}/api/compliance/validate/personal-info", 
                               headers=headers, json=compliance_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            compliance_result = response.json()
            print(f"✅ Compliance validation completed")
            print(f"   Overall compliant: {compliance_result['overall_compliant']}")
            if compliance_result.get('age_validation'):
                print(f"   Age validation: {'✅ Valid' if compliance_result['age_validation']['is_valid'] else '❌ Invalid'}")
            if compliance_result.get('ssn_validation'):
                print(f"   SSN validation: {'✅ Valid' if compliance_result['ssn_validation']['is_valid'] else '❌ Invalid'}")
        else:
            print(f"❌ Compliance validation failed: {response.text}")
        
        # Test 6: Get session analytics
        print("\n6. Testing GET /api/onboarding/analytics/sessions")
        response = requests.get(f"{BASE_URL}/api/onboarding/analytics/sessions", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            analytics = response.json()
            print("✅ Analytics retrieved successfully")
            print(f"   Total sessions: {analytics['total_sessions']}")
            print(f"   Average progress: {analytics['average_progress']}%")
            print(f"   Status distribution: {analytics['status_distribution']}")
        else:
            print(f"❌ Analytics failed: {response.text}")
        
        print("\n" + "=" * 50)
        print("🎉 Session Management API Test Completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on http://localhost:8000")
        print("   Run: poetry run python app/main.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_i9_compliance():
    """Test I-9 federal compliance validation"""
    print("\n🧪 Testing I-9 Federal Compliance Validation")
    print("=" * 50)
    
    headers = {
        "Authorization": "Bearer test-user-token",
        "Content-Type": "application/json"
    }
    
    # Test valid I-9 data
    i9_data = {
        "employee_last_name": "Doe",
        "employee_first_name": "John",
        "employee_middle_initial": "M",
        "address_street": "123 Main St",
        "address_city": "Anytown",
        "address_state": "CA",
        "address_zip": "12345",
        "date_of_birth": "1990-01-15",
        "ssn": "123-45-6789",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "citizenship_status": "us_citizen",
        "employee_signature_date": "2025-01-01"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/compliance/validate/i9-section1", 
                               headers=headers, json=i9_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ I-9 validation completed")
            print(f"   Federal compliance status: {result['federal_compliance_status']}")
            print(f"   Validation errors: {len(result['validation_result']['errors'])}")
            print(f"   Validation warnings: {len(result['validation_result']['warnings'])}")
            
            if result['validation_result']['errors']:
                print("   Errors:")
                for error in result['validation_result']['errors']:
                    print(f"     - {error['message']}")
        else:
            print(f"❌ I-9 validation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ I-9 test error: {str(e)}")

if __name__ == "__main__":
    # Run tests
    success = test_session_management()
    test_i9_compliance()
    
    if success:
        print("\n✅ All tests completed! Session management API is ready for frontend integration.")
    else:
        print("\n❌ Some tests failed. Check server status and logs.")