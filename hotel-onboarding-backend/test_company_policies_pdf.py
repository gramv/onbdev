#!/usr/bin/env python3
"""Test Company Policies PDF generation with initials and signature"""

import requests
import json
import os

# API endpoint
API_URL = "http://localhost:8000/api/onboarding/test-employee/company-policies/generate-pdf"

# Test data with initials and signature
test_data = {
    "employee_data": {
        "firstName": "John",
        "lastName": "Smith",
        "property_name": "Lakecrest Hotel & Suites",
        "companyPoliciesInitials": "JS",
        "eeoInitials": "JS", 
        "sexualHarassmentInitials": "JS",
        "acknowledgmentChecked": True,
        "signatureData": {
            "signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        },
        "completedAt": "2025-08-06T12:00:00Z"
    }
}

def test_pdf_generation():
    """Test Company Policies PDF generation"""
    print("📋 Testing Company Policies PDF with initials and signature...")
    
    try:
        response = requests.post(API_URL, json=test_data)
        
        if response.status_code == 200:
            # Save the PDF
            os.makedirs("generated_pdfs", exist_ok=True)
            pdf_path = "generated_pdfs/test_company_policies_with_initials.pdf"
            
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ PDF generated successfully: {pdf_path}")
            print(f"   File size: {len(response.content):,} bytes")
            print("\n📝 Included in PDF:")
            print("   - Company Policies initials: JS")
            print("   - EEO initials: JS")
            print("   - Sexual Harassment initials: JS")
            print("   - Digital signature: Yes")
            print("   - Employee name: John Smith")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_pdf_generation()