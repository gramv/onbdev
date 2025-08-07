#!/usr/bin/env python3
"""
Test script for validating I-9 and W-4 PDF field mappings
Tests the corrected field mapping implementation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models import I9Section1Data, W4FormData, I9PDFGenerationRequest, W4PDFGenerationRequest
from app.pdf_forms import pdf_form_service
import json

def test_i9_field_mapping():
    """Test I-9 form field mapping with realistic data"""
    print("=" * 60)
    print("TESTING I-9 FORM FIELD MAPPING")
    print("=" * 60)
    
    # Create test data matching UI field structure
    i9_test_data = I9Section1Data(
        employee_last_name="Smith",
        employee_first_name="John",
        employee_middle_initial="A",
        other_last_names="",
        address_street="123 Main Street",
        address_apt="Apt 4B",
        address_city="Jersey City",
        address_state="NJ",
        address_zip="07302",
        date_of_birth="1990-05-15",
        ssn="123-45-6789",
        email="john.smith@hotel.com",
        phone="(201) 555-0123",
        citizenship_status="us_citizen",
        uscis_number="",
        i94_admission_number="",
        passport_number="",
        passport_country="",
        work_authorization_expiration="",
        section_1_completed_at="2025-01-25T10:30:00Z",
        employee_signature_date="2025-01-25"
    )
    
    print("Test Data Created:")
    print(f"  Name: {i9_test_data.employee_first_name} {i9_test_data.employee_middle_initial} {i9_test_data.employee_last_name}")
    print(f"  Address: {i9_test_data.address_street}, {i9_test_data.address_city}, {i9_test_data.address_state} {i9_test_data.address_zip}")
    print(f"  DOB: {i9_test_data.date_of_birth}")
    print(f"  Citizenship: {i9_test_data.citizenship_status}")
    print()
    
    try:
        # Convert to dict for PDF service
        employee_data = i9_test_data.dict()
        
        # Test PDF generation
        print("Generating I-9 PDF...")
        pdf_bytes = pdf_form_service.fill_i9_form(employee_data, None)
        
        # Save test PDF
        output_path = "/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-backend/test-i9-mapping.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✅ SUCCESS: I-9 PDF generated successfully")
        print(f"   Output saved to: {output_path}")
        print(f"   File size: {len(pdf_bytes)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: I-9 PDF generation failed")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_w4_field_mapping():
    """Test W-4 form field mapping with realistic data"""
    print("\n" + "=" * 60)
    print("TESTING W-4 FORM FIELD MAPPING")
    print("=" * 60)
    
    # Create test data matching UI field structure
    w4_test_data = W4FormData(
        first_name="John",
        middle_initial="A",
        last_name="Smith",
        address="123 Main Street, Apt 4B",
        city="Jersey City",
        state="NJ",
        zip_code="07302",
        ssn="123-45-6789",
        filing_status="Single",
        multiple_jobs_checkbox=False,
        spouse_works_checkbox=False,
        dependents_amount=0.0,
        other_credits=0.0,
        other_income=0.0,
        deductions=0.0,
        extra_withholding=0.0,
        signature="John A. Smith",
        signature_date="2025-01-25"
    )
    
    print("Test Data Created:")
    print(f"  Name: {w4_test_data.first_name} {w4_test_data.middle_initial} {w4_test_data.last_name}")
    print(f"  Address: {w4_test_data.address}, {w4_test_data.city}, {w4_test_data.state} {w4_test_data.zip_code}")
    print(f"  Filing Status: {w4_test_data.filing_status}")
    print(f"  Multiple Jobs: {w4_test_data.multiple_jobs_checkbox}")
    print()
    
    try:
        # Convert to dict for PDF service
        employee_data = w4_test_data.dict()
        
        # Test PDF generation
        print("Generating W-4 PDF...")
        pdf_bytes = pdf_form_service.fill_w4_form(employee_data)
        
        # Save test PDF
        output_path = "/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-backend/test-w4-mapping.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✅ SUCCESS: W-4 PDF generated successfully")
        print(f"   Output saved to: {output_path}")
        print(f"   File size: {len(pdf_bytes)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: W-4 PDF generation failed")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_non_citizen_i9():
    """Test I-9 form with non-citizen data"""
    print("\n" + "=" * 60)
    print("TESTING I-9 FORM WITH NON-CITIZEN DATA")
    print("=" * 60)
    
    # Create test data for authorized alien
    i9_alien_data = I9Section1Data(
        employee_last_name="Garcia",
        employee_first_name="Maria",
        employee_middle_initial="L",
        other_last_names="Lopez",
        address_street="456 Oak Avenue",
        address_apt="",
        address_city="Newark",
        address_state="NJ",
        address_zip="07104",
        date_of_birth="1988-12-03",
        ssn="987-65-4321",
        email="maria.garcia@hotel.com",
        phone="(973) 555-0456",
        citizenship_status="authorized_alien",
        uscis_number="A123456789",
        i94_admission_number="12345678901",
        passport_number="MX1234567",
        passport_country="Mexico",
        work_authorization_expiration="2025-12-31",
        section_1_completed_at="2025-01-25T10:30:00Z",
        employee_signature_date="2025-01-25"
    )
    
    print("Test Data Created:")
    print(f"  Name: {i9_alien_data.employee_first_name} {i9_alien_data.employee_middle_initial} {i9_alien_data.employee_last_name}")
    print(f"  Citizenship: {i9_alien_data.citizenship_status}")
    print(f"  USCIS Number: {i9_alien_data.uscis_number}")
    print(f"  Passport: {i9_alien_data.passport_number} ({i9_alien_data.passport_country})")
    print(f"  Work Auth Exp: {i9_alien_data.work_authorization_expiration}")
    print()
    
    try:
        # Convert to dict for PDF service
        employee_data = i9_alien_data.dict()
        
        # Test PDF generation
        print("Generating I-9 PDF for authorized alien...")
        pdf_bytes = pdf_form_service.fill_i9_form(employee_data, None)
        
        # Save test PDF
        output_path = "/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-backend/test-i9-alien.pdf"
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✅ SUCCESS: I-9 PDF (authorized alien) generated successfully")
        print(f"   Output saved to: {output_path}")
        print(f"   File size: {len(pdf_bytes)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: I-9 PDF (authorized alien) generation failed")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_validation_models():
    """Test Pydantic model validation"""
    print("\n" + "=" * 60)
    print("TESTING PYDANTIC MODEL VALIDATION")
    print("=" * 60)
    
    # Test invalid data
    print("Testing invalid citizenship status...")
    try:
        invalid_i9 = I9Section1Data(
            employee_last_name="Test",
            employee_first_name="User",
            address_street="123 Test St",
            address_city="Test City", 
            address_state="TS",
            address_zip="12345",
            date_of_birth="1990-01-01",
            ssn="123456789",
            email="test@test.com",
            phone="123-456-7890",
            citizenship_status="invalid_status"  # This should fail
        )
        print("❌ ERROR: Should have failed validation")
        return False
    except Exception as e:
        print("✅ SUCCESS: Validation correctly rejected invalid citizenship status")
        print(f"   Error: {str(e)}")
    
    # Test invalid date format
    print("\nTesting invalid date format...")
    try:
        invalid_date_i9 = I9Section1Data(
            employee_last_name="Test",
            employee_first_name="User",
            address_street="123 Test St",
            address_city="Test City",
            address_state="TS", 
            address_zip="12345",
            date_of_birth="01/01/1990",  # Wrong format, should be YYYY-MM-DD
            ssn="123456789",
            email="test@test.com",
            phone="123-456-7890",
            citizenship_status="us_citizen"
        )
        print("❌ ERROR: Should have failed date validation")
        return False
    except Exception as e:
        print("✅ SUCCESS: Validation correctly rejected invalid date format")
        print(f"   Error: {str(e)}")
    
    return True

def main():
    """Run all tests"""
    print("FIELD MAPPING VALIDATION TEST SUITE")
    print("Testing corrected I-9 and W-4 PDF field mappings")
    print("Date: 2025-01-25")
    print()
    
    results = []
    
    # Run tests
    results.append(("I-9 Basic Field Mapping", test_i9_field_mapping()))
    results.append(("W-4 Basic Field Mapping", test_w4_field_mapping()))
    results.append(("I-9 Non-Citizen Data", test_non_citizen_i9()))
    results.append(("Pydantic Model Validation", test_validation_models()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
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
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Field mappings are working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)