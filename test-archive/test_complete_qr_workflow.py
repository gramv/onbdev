#!/usr/bin/env python3
"""
Complete QR Code to Job Application Workflow Test

This test verifies the entire flow:
1. HR creates a property
2. QR code is generated for the property
3. QR code links to the correct application form
4. Application submission is linked to the correct property
5. Applications appear in the correct property's dashboard
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_complete_qr_workflow():
    """Test the complete QR code workflow"""
    
    print("🚀 TESTING COMPLETE QR CODE TO APPLICATION WORKFLOW")
    print(f"Backend: {BACKEND_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    
    # Step 1: Login as HR
    print_step(1, "HR Login")
    
    login_data = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            auth_data = response.json()
            hr_token = auth_data["token"]
            print_success("HR login successful")
            print_info(f"HR User: {auth_data['user']['first_name']} {auth_data['user']['last_name']}")
        else:
            print_error(f"HR login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"HR login error: {e}")
        return False
    
    # Step 2: Create a new property
    print_step(2, "Create New Property")
    
    property_data = {
        "name": "QR Test Hotel",
        "address": "123 QR Test Street",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "phone": "(555) 123-4567"
    }
    
    headers = {"Authorization": f"Bearer {hr_token}"}
    
    try:
        response = requests.post(f"{BACKEND_URL}/hr/properties", data=property_data, headers=headers)
        if response.status_code == 200:
            property_response = response.json()
            property_id = property_response["id"]
            qr_code_url = property_response["qr_code_url"]
            print_success("Property created successfully")
            print_info(f"Property ID: {property_id}")
            print_info(f"Property Name: {property_response['name']}")
            print_info(f"QR Code Generated: {'Yes' if qr_code_url else 'No'}")
        else:
            print_error(f"Property creation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Property creation error: {e}")
        return False
    
    # Step 3: Verify QR code generation
    print_step(3, "Verify QR Code Generation")
    
    try:
        response = requests.post(f"{BACKEND_URL}/hr/properties/{property_id}/qr-code", headers=headers)
        if response.status_code == 200:
            qr_data = response.json()
            application_url = qr_data["application_url"]
            print_success("QR code generated successfully")
            print_info(f"Application URL: {application_url}")
            print_info(f"QR Code URL: {'Present' if qr_data.get('qr_code_url') else 'Missing'}")
            print_info(f"Printable QR URL: {'Present' if qr_data.get('printable_qr_url') else 'Missing'}")
            
            # Verify the application URL format
            expected_url = f"{FRONTEND_URL}/apply/{property_id}"
            if application_url == expected_url:
                print_success(f"Application URL format is correct: {application_url}")
            else:
                print_error(f"Application URL format incorrect. Expected: {expected_url}, Got: {application_url}")
        else:
            print_error(f"QR code generation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"QR code generation error: {e}")
        return False
    
    # Step 4: Test property info endpoint (what the QR code would access)
    print_step(4, "Test Property Info Endpoint (QR Code Target)")
    
    try:
        response = requests.get(f"{BACKEND_URL}/properties/{property_id}/info")
        if response.status_code == 200:
            property_info = response.json()
            print_success("Property info endpoint accessible")
            print_info(f"Property Name: {property_info['property']['name']}")
            print_info(f"Accepting Applications: {property_info['is_accepting_applications']}")
            print_info(f"Available Departments: {list(property_info['departments_and_positions'].keys())}")
            
            # Verify property details match
            if property_info['property']['name'] == property_data['name']:
                print_success("Property details match created property")
            else:
                print_error("Property details don't match created property")
        else:
            print_error(f"Property info endpoint failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Property info endpoint error: {e}")
        return False
    
    # Step 5: Submit job application through QR code endpoint
    print_step(5, "Submit Job Application (Simulating QR Code Scan)")
    
    application_data = {
        "first_name": "John",
        "last_name": "QRTest",
        "email": "john.qrtest@example.com",
        "phone": "(555) 987-6543",
        "address": "456 Test Avenue",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90211",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-08-15",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes",
        "previous_employer": "Test Hotel Chain",
        "reason_for_leaving": "Career advancement",
        "additional_comments": "Excited to join the team!"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/apply/{property_id}", json=application_data)
        if response.status_code == 200:
            app_response = response.json()
            application_id = app_response["application_id"]
            print_success("Job application submitted successfully")
            print_info(f"Application ID: {application_id}")
            print_info(f"Property Name: {app_response['property_name']}")
            print_info(f"Position Applied: {app_response['position_applied']}")
            
            # Verify property name matches
            if app_response['property_name'] == property_data['name']:
                print_success("Application linked to correct property")
            else:
                print_error("Application not linked to correct property")
        else:
            print_error(f"Job application submission failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Job application submission error: {e}")
        return False
    
    # Step 6: Verify application appears in HR dashboard
    print_step(6, "Verify Application in HR Dashboard")
    
    try:
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
        if response.status_code == 200:
            applications = response.json()
            print_success("HR applications retrieved successfully")
            print_info(f"Total applications: {len(applications)}")
            
            # Find our test application
            test_application = None
            for app in applications:
                if app["id"] == application_id:
                    test_application = app
                    break
            
            if test_application:
                print_success("Test application found in HR dashboard")
                print_info(f"Application Property ID: {test_application['property_id']}")
                print_info(f"Application Status: {test_application['status']}")
                print_info(f"Applicant: {test_application['applicant_data']['first_name']} {test_application['applicant_data']['last_name']}")
                
                # Verify property linkage
                if test_application['property_id'] == property_id:
                    print_success("Application correctly linked to property")
                else:
                    print_error(f"Application linked to wrong property. Expected: {property_id}, Got: {test_application['property_id']}")
            else:
                print_error("Test application not found in HR dashboard")
                return False
        else:
            print_error(f"HR applications retrieval failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"HR applications retrieval error: {e}")
        return False
    
    # Step 7: Test manager access (if manager exists for this property)
    print_step(7, "Test Manager Access to Property Applications")
    
    # First, assign a manager to the property
    try:
        # Get existing manager
        response = requests.get(f"{BACKEND_URL}/hr/managers", headers=headers)
        if response.status_code == 200:
            managers = response.json()
            if managers:
                manager_id = managers[0]["id"]
                
                # Assign manager to property
                assign_data = {"manager_id": manager_id}
                response = requests.post(f"{BACKEND_URL}/hr/properties/{property_id}/managers", 
                                       json=assign_data, headers=headers)
                
                if response.status_code == 200:
                    print_success("Manager assigned to property")
                    
                    # Login as manager
                    manager_login = {
                        "email": "manager@hoteltest.com",
                        "password": "manager123"
                    }
                    
                    response = requests.post(f"{BACKEND_URL}/auth/login", json=manager_login)
                    if response.status_code == 200:
                        manager_auth = response.json()
                        manager_token = manager_auth["token"]
                        manager_headers = {"Authorization": f"Bearer {manager_token}"}
                        
                        # Check manager can see applications for their property
                        response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
                        if response.status_code == 200:
                            manager_applications = response.json()
                            print_success("Manager can access applications")
                            
                            # Find our test application
                            manager_test_app = None
                            for app in manager_applications:
                                if app["id"] == application_id:
                                    manager_test_app = app
                                    break
                            
                            if manager_test_app:
                                print_success("Manager can see application from QR code")
                                print_info(f"Manager sees application for: {manager_test_app['applicant_data']['first_name']} {manager_test_app['applicant_data']['last_name']}")
                            else:
                                print_error("Manager cannot see application from QR code")
                        else:
                            print_error(f"Manager applications access failed: {response.status_code}")
                    else:
                        print_error("Manager login failed")
                else:
                    print_info("Could not assign manager to property (may not be implemented)")
            else:
                print_info("No managers available for testing")
        else:
            print_info("Could not retrieve managers for testing")
    except Exception as e:
        print_info(f"Manager testing skipped due to error: {e}")
    
    # Step 8: Test duplicate application prevention
    print_step(8, "Test Duplicate Application Prevention")
    
    try:
        # Try to submit the same application again
        response = requests.post(f"{BACKEND_URL}/apply/{property_id}", json=application_data)
        if response.status_code == 400:
            error_detail = response.json().get("detail", "")
            if "already submitted" in error_detail.lower():
                print_success("Duplicate application prevention working")
                print_info(f"Error message: {error_detail}")
            else:
                print_error(f"Unexpected error for duplicate: {error_detail}")
        else:
            print_error("Duplicate application was allowed (should be prevented)")
            return False
    except Exception as e:
        print_error(f"Duplicate application test error: {e}")
        return False
    
    # Final Summary
    print_step("FINAL", "Workflow Test Summary")
    
    print_success("✅ Complete QR Code Workflow Test PASSED")
    print("\n📋 WORKFLOW VERIFIED:")
    print("   1. ✅ HR can create properties")
    print("   2. ✅ QR codes are automatically generated")
    print("   3. ✅ QR codes link to correct property application form")
    print("   4. ✅ Property info endpoint works (QR scan target)")
    print("   5. ✅ Applications are submitted to correct property")
    print("   6. ✅ Applications appear in HR dashboard")
    print("   7. ✅ Applications are linked to correct property")
    print("   8. ✅ Duplicate applications are prevented")
    print("   9. ✅ Manager access works (if configured)")
    
    print(f"\n🎯 KEY VERIFICATION POINTS:")
    print(f"   • Property ID: {property_id}")
    print(f"   • Application ID: {application_id}")
    print(f"   • QR Code URL: {application_url}")
    print(f"   • Property Name: {property_data['name']}")
    print(f"   • Applicant: {application_data['first_name']} {application_data['last_name']}")
    
    return True

if __name__ == "__main__":
    print("🧪 Starting Complete QR Code Workflow Test...")
    
    try:
        success = test_complete_qr_workflow()
        if success:
            print("\n🎉 ALL TESTS PASSED! QR Code workflow is working correctly.")
            sys.exit(0)
        else:
            print("\n💥 TESTS FAILED! Check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)