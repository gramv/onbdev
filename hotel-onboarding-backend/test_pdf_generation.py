#!/usr/bin/env python3
"""
Test PDF generation endpoints
"""
import requests
import json
import base64
from datetime import datetime

# Backend URL
BASE_URL = "http://localhost:8000"

def test_i9_pdf_generation():
    """Test I-9 PDF generation"""
    print("Testing I-9 PDF generation...")
    
    # Sample I-9 data
    i9_data = {
        "employee_data": {
            "employee_first_name": "John",
            "employee_last_name": "Doe",
            "employee_middle_initial": "M",
            "other_last_names": "",
            "address_street": "123 Main Street",
            "apt_number": "Apt 4B",
            "address_city": "New York",
            "address_state": "NY",
            "address_zip": "10001",
            "date_of_birth": "1990-01-15",
            "ssn": "123-45-6789",
            "email": "john.doe@example.com",
            "phone": "(555) 123-4567",
            "citizenship_status": "citizen",
            "employee_signature": "John Doe",
            "employee_signature_date": datetime.now().strftime("%Y-%m-%d")
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/forms/i9/generate",
            json=i9_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ I-9 PDF generated successfully!")
            
            # Save PDF to file
            with open("test_i9_form.pdf", "wb") as f:
                f.write(response.content)
            print("📄 Saved to test_i9_form.pdf")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_w4_pdf_generation():
    """Test W-4 PDF generation"""
    print("\nTesting W-4 PDF generation...")
    
    # Sample W-4 data
    w4_data = {
        "employee_data": {
            "first_name": "John",
            "last_name": "Doe",
            "middle_initial": "M",
            "ssn": "123-45-6789",
            "address": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "filing_status": "single",
            "multiple_jobs": False,
            "qualifying_children": 0,
            "other_dependents": 0,
            "other_income": 0,
            "deductions": 0,
            "extra_withholding": 0,
            "exempt": False
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/forms/w4/generate",
            json=w4_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ W-4 PDF generated successfully!")
            
            # Save PDF to file
            with open("test_w4_form.pdf", "wb") as f:
                f.write(response.content)
            print("📄 Saved to test_w4_form.pdf")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_pdf_service_status():
    """Test PDF service status"""
    print("Testing PDF service status...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/forms/test")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PDF Service Status:")
            print(f"   - PyMuPDF: {data.get('pymupdf', 'Unknown')}")
            print(f"   - I-9 Form Available: {data.get('i9_form_exists', False)}")
            print(f"   - W-4 Form Available: {data.get('w4_form_exists', False)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("PDF Generation Test Script")
    print("=" * 50)
    
    # Test service status first
    test_pdf_service_status()
    
    print("\n" + "=" * 50)
    
    # Test I-9 generation
    test_i9_pdf_generation()
    
    # Test W-4 generation
    test_w4_pdf_generation()
    
    print("\n✅ All tests completed!")