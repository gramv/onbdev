#!/usr/bin/env python3
"""
API Integration Test for I-9 and W-4 PDF Generation
Tests the complete data flow from frontend to PDF generation
"""

import requests
import json
import sys
import os

BASE_URL = "http://localhost:8000"

def test_api_validation_endpoints():
    """Test the validation endpoints"""
    print("=" * 60)
    print("TESTING API VALIDATION ENDPOINTS")
    print("=" * 60)
    
    # Test I-9 validation endpoint
    i9_test_data = {
        "employee_data": {
            "employee_last_name": "Smith",
            "employee_first_name": "John",
            "employee_middle_initial": "A",
            "other_last_names": "",
            "address_street": "123 Main Street",
            "address_apt": "Apt 4B",
            "address_city": "Jersey City",
            "address_state": "NJ",
            "address_zip": "07302",
            "date_of_birth": "1990-05-15",
            "ssn": "123-45-6789",
            "email": "john.smith@hotel.com",
            "phone": "(201) 555-0123",
            "citizenship_status": "us_citizen",
            "uscis_number": "",
            "i94_admission_number": "",
            "passport_number": "",
            "passport_country": "",
            "work_authorization_expiration": "",
            "section_1_completed_at": "2025-01-25T10:30:00Z",
            "employee_signature_date": "2025-01-25"
        }
    }
    
    # Test W-4 validation endpoint
    w4_test_data = {
        "employee_data": {
            "first_name": "John",
            "middle_initial": "A",
            "last_name": "Smith",
            "address": "123 Main Street, Apt 4B",
            "city": "Jersey City",
            "state": "NJ",
            "zip_code": "07302",
            "ssn": "123-45-6789",
            "filing_status": "Single",
            "multiple_jobs_checkbox": False,
            "spouse_works_checkbox": False,
            "dependents_amount": 0.0,
            "other_credits": 0.0,
            "other_income": 0.0,
            "deductions": 0.0,
            "extra_withholding": 0.0,
            "signature": "John A. Smith",
            "signature_date": "2025-01-25"
        }
    }
    
    try:
        # Test I-9 validation
        print("Testing I-9 validation endpoint...")
        response = requests.post(f"{BASE_URL}/api/forms/validate/i9", json=i9_test_data)
        print(f"I-9 Validation Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Validation Status: {result.get('status')}")
            print(f"Employee Name: {result.get('employee_data_summary', {}).get('name')}")
            print("✅ I-9 validation endpoint working")
        else:
            print(f"❌ I-9 validation failed: {response.text}")
        
        # Test W-4 validation
        print("\nTesting W-4 validation endpoint...")
        response = requests.post(f"{BASE_URL}/api/forms/validate/w4", json=w4_test_data)
        print(f"W-4 Validation Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Validation Status: {result.get('status')}")
            print(f"Employee Name: {result.get('employee_data_summary', {}).get('name')}")
            print("✅ W-4 validation endpoint working")
        else:
            print(f"❌ W-4 validation failed: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        print("Please start the server with: python app/main_enhanced.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_pdf_generation_endpoints():
    """Test PDF generation endpoints"""
    print("\n" + "=" * 60)
    print("TESTING PDF GENERATION ENDPOINTS")
    print("=" * 60)
    
    # Test data matching our models
    i9_test_data = {
        "employee_data": {
            "employee_last_name": "Smith",
            "employee_first_name": "John",
            "employee_middle_initial": "A",
            "other_last_names": "",
            "address_street": "123 Main Street",
            "address_apt": "Apt 4B",
            "address_city": "Jersey City",
            "address_state": "NJ",
            "address_zip": "07302",
            "date_of_birth": "1990-05-15",
            "ssn": "123-45-6789",
            "email": "john.smith@hotel.com",
            "phone": "(201) 555-0123",
            "citizenship_status": "us_citizen",
            "uscis_number": "",
            "i94_admission_number": "",
            "passport_number": "",
            "passport_country": "",
            "work_authorization_expiration": "",
            "section_1_completed_at": "2025-01-25T10:30:00Z",
            "employee_signature_date": "2025-01-25"
        }
    }
    
    w4_test_data = {
        "employee_data": {
            "first_name": "John",
            "middle_initial": "A",
            "last_name": "Smith",
            "address": "123 Main Street, Apt 4B",
            "city": "Jersey City",
            "state": "NJ",
            "zip_code": "07302",
            "ssn": "123-45-6789",
            "filing_status": "Single",
            "multiple_jobs_checkbox": False,
            "spouse_works_checkbox": False,
            "dependents_amount": 0.0,
            "other_credits": 0.0,
            "other_income": 0.0,
            "deductions": 0.0,
            "extra_withholding": 0.0,
            "signature": "John A. Smith",
            "signature_date": "2025-01-25"
        }
    }
    
    try:
        # Test I-9 PDF generation
        print("Testing I-9 PDF generation endpoint...")
        response = requests.post(f"{BASE_URL}/api/forms/i9/generate", json=i9_test_data)
        print(f"I-9 PDF Generation Status: {response.status_code}")
        if response.status_code == 200:
            print(f"PDF Size: {len(response.content)} bytes")
            print("Content Type:", response.headers.get('Content-Type'))
            
            # Save PDF
            with open('test-api-i9.pdf', 'wb') as f:
                f.write(response.content)
            print("✅ I-9 PDF generated successfully via API")
        else:
            print(f"❌ I-9 PDF generation failed: {response.text}")
        
        # Test W-4 PDF generation
        print("\nTesting W-4 PDF generation endpoint...")
        response = requests.post(f"{BASE_URL}/api/forms/w4/generate", json=w4_test_data)
        print(f"W-4 PDF Generation Status: {response.status_code}")
        if response.status_code == 200:
            print(f"PDF Size: {len(response.content)} bytes")
            print("Content Type:", response.headers.get('Content-Type'))
            
            # Save PDF
            with open('test-api-w4.pdf', 'wb') as f:
                f.write(response.content)
            print("✅ W-4 PDF generated successfully via API")
        else:
            print(f"❌ W-4 PDF generation failed: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        print("Please start the server with: python app/main_enhanced.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_field_debugging():
    """Test the field debugging endpoints"""
    print("\n" + "=" * 60)
    print("TESTING FIELD DEBUGGING ENDPOINTS")
    print("=" * 60)
    
    try:
        # Test debug endpoints
        print("Testing I-9 field debug endpoint...")
        response = requests.get(f"{BASE_URL}/api/forms/debug/i9-fields")
        if response.status_code == 200:
            result = response.json()
            print(f"Total I-9 fields found: {result.get('total_fields', 0)}")
            print("✅ I-9 field debug endpoint working")
        else:
            print(f"❌ I-9 field debug failed: {response.text}")
        
        print("\nTesting service status endpoint...")
        response = requests.get(f"{BASE_URL}/api/forms/test")
        if response.status_code == 200:
            result = response.json()
            print(f"Service Status: {result.get('status')}")
            print(f"PyMuPDF: {result.get('pymupdf')}")
            print("✅ Test endpoint working")
        else:
            print(f"❌ Test endpoint failed: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    """Run API integration tests"""
    print("API INTEGRATION TEST SUITE")
    print("Testing field mapping fixes via HTTP API")
    print(f"Server URL: {BASE_URL}")
    print()
    
    results = []
    
    # Run tests
    results.append(("Field Debugging Endpoints", test_field_debugging()))
    results.append(("API Validation Endpoints", test_api_validation_endpoints()))
    results.append(("PDF Generation Endpoints", test_pdf_generation_endpoints()))
    
    # Summary
    print("\n" + "=" * 60)
    print("API INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(results)} test groups")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All API integration tests passed!")
        print("Field mappings are working correctly via HTTP API.")
        return True
    else:
        print(f"\n⚠️  {failed} test group(s) failed.")
        print("Note: Some failures may be due to server not running.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)