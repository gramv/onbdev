#!/usr/bin/env python3
"""
Test script to generate updated PDFs for review
Run this script to generate Company Policies, Direct Deposit, Weapons Policy, and Health Insurance PDFs
"""

import sys
import os
import base64
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.pdf_forms import PDFFormFiller

def save_pdf_to_file(pdf_bytes, filename):
    """Save PDF bytes to a file"""
    output_dir = "generated_pdfs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)
    print(f"✅ Generated: {filepath}")
    return filepath

def generate_sample_signature():
    """Generate a sample signature image as base64"""
    # This is a simple 1x1 transparent PNG - in production, this would be actual signature data
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_company_policies_pdf():
    """Test Company Policies PDF generation - matches pages 3-9"""
    print("\n📋 Testing Company Policies PDF (Pages 3-9)...")
    
    pdf_filler = PDFFormFiller()
    
    sample_data = {
        "employee_name": "John Smith",
        "employee_id": "EMP001",
        "property_name": "Grand Hotel & Resort",
        "hire_date": "2025-01-15",
        "position": "Front Desk Agent",
        "acknowledgments": {
            "at_will": True,
            "eeo": True,
            "sexual_harassment": True,
            "workplace_violence": True,
            "ethics": True,
            "confidentiality": True,
            "customer_relations": True,
            "teamwork": True
        },
        "signatureData": {
            "signature": generate_sample_signature(),
            "signedAt": datetime.now().isoformat()
        }
    }
    
    try:
        pdf_bytes = pdf_filler.create_company_policies_pdf(sample_data)
        save_pdf_to_file(pdf_bytes, "1_company_policies.pdf")
        print("   ✓ Should contain all policies from pages 3-9 of packet")
        print("   ✓ Includes: AT WILL, EEO, Sexual Harassment, Violence-Free, Ethics, etc.")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_direct_deposit_pdf():
    """Test Direct Deposit PDF generation - matches page 18"""
    print("\n💰 Testing Direct Deposit PDF (Page 18 - ADP Form)...")
    
    pdf_filler = PDFFormFiller()
    
    sample_data = {
        "employee_name": "John Smith",
        "employee_id": "EMP001",
        "ssn": "123-45-6789",
        "property_name": "Grand Hotel & Resort",
        "hire_date": "2025-01-15",
        "position": "Front Desk Agent",
        "paymentMethod": "direct_deposit",
        "primaryAccount": {
            "accountType": "checking",
            "bankName": "Wells Fargo Bank",
            "routingNumber": "121000248",
            "accountNumber": "1234567890"
        },
        "signatureData": {
            "signature": generate_sample_signature(),
            "signedAt": datetime.now().isoformat()
        }
    }
    
    try:
        pdf_bytes = pdf_filler.create_direct_deposit_pdf(sample_data)
        save_pdf_to_file(pdf_bytes, "2_direct_deposit.pdf")
        print("   ✓ Should match ADP Direct Deposit form layout")
        print("   ✓ Includes MICR line visualization and legal notices")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_weapons_policy_pdf():
    """Test Weapons Policy PDF generation - matches page 22"""
    print("\n🚫 Testing Weapons Policy PDF (Page 22)...")
    
    pdf_filler = PDFFormFiller()
    
    sample_data = {
        "employee_name": "John Smith",
        "employee_id": "EMP001",
        "property_name": "Grand Hotel & Resort",
        "hire_date": "2025-01-15",
        "position": "Front Desk Agent",
        "acknowledgments": {
            "understands_policy": True,
            "agrees_to_comply": True,
            "understands_consequences": True,
            "will_report_violations": True
        },
        "signatureData": {
            "signature": generate_sample_signature(),
            "signedAt": datetime.now().isoformat()
        }
    }
    
    try:
        pdf_bytes = pdf_filler.create_weapons_policy_pdf(sample_data)
        save_pdf_to_file(pdf_bytes, "3_weapons_policy.pdf")
        print("   ✓ Should match exact text from page 22 of packet")
        print("   ✓ Includes concealed carry prohibition and enforcement")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_health_insurance_pdf():
    """Test Health Insurance PDF generation - matches pages 23-28"""
    print("\n🏥 Testing Health Insurance PDFs (Pages 23-28 - Lakecrest forms)...")
    
    pdf_filler = PDFFormFiller()
    
    # Test with enrollment (HMO/PPO selection)
    sample_data_enrolled = {
        "employee_name": "John Smith",
        "employee_id": "EMP001",
        "ssn": "123-45-6789",
        "property_name": "Grand Hotel & Resort",
        "hire_date": "2025-01-15",
        "position": "Front Desk Agent",
        "phone": "(555) 123-4567",
        "address": "123 Main St, Suite 100, Anytown, TX 75001",
        "birth_date": "1985-06-15",
        "enrollmentChoice": "enroll",
        "planChoice": "ppo",
        "coverageLevel": "employee_spouse",
        "dependents": [
            {
                "name": "Jane Smith",
                "relationship": "Spouse",
                "birthDate": "1987-03-22",
                "ssn": "987-65-4321"
            }
        ],
        "signatureData": {
            "signature": generate_sample_signature(),
            "signedAt": datetime.now().isoformat()
        }
    }
    
    try:
        pdf_bytes = pdf_filler.create_health_insurance_pdf(sample_data_enrolled)
        save_pdf_to_file(pdf_bytes, "4a_health_insurance_enrolled.pdf")
        print("   ✓ Enrollment form should match Lakecrest format")
        print("   ✓ Includes HMO/PPO selection and dependent info")
    except Exception as e:
        print(f"   ❌ Error (enrollment): {e}")
    
    # Test with waiver
    sample_data_waived = {
        "employee_name": "Jane Doe",
        "employee_id": "EMP002",
        "ssn": "987-65-4321",
        "property_name": "Grand Hotel & Resort",
        "hire_date": "2025-01-15",
        "position": "Housekeeping Supervisor",
        "phone": "(555) 987-6543",
        "address": "456 Oak Ave, Anytown, TX 75002",
        "birth_date": "1990-08-20",
        "enrollmentChoice": "waive",
        "waiveReason": "covered_spouse",
        "otherInsuranceCarrier": "Blue Cross Blue Shield",
        "signatureData": {
            "signature": generate_sample_signature(),
            "signedAt": datetime.now().isoformat()
        }
    }
    
    try:
        pdf_bytes = pdf_filler.create_health_insurance_pdf(sample_data_waived)
        save_pdf_to_file(pdf_bytes, "4b_health_insurance_waived.pdf")
        print("   ✓ Waiver form should match page 28 format")
        print("   ✓ Includes reason for waiver and other insurance info")
    except Exception as e:
        print(f"   ❌ Error (waiver): {e}")

def main():
    """Run all PDF generation tests"""
    print("=" * 70)
    print("🧪 UPDATED PDF GENERATION TEST SUITE")
    print("=" * 70)
    print("\nThis will generate PDFs that should match the official hire packet")
    print("Compare these with '2025+-+New+Employee+Hire+Packet_compressed (1).pdf'")
    
    try:
        # Create output directory
        os.makedirs("generated_pdfs", exist_ok=True)
        
        # Run all tests
        test_company_policies_pdf()
        test_direct_deposit_pdf()
        test_weapons_policy_pdf()
        test_health_insurance_pdf()
        
        print("\n" + "=" * 70)
        print("✅ PDF generation complete!")
        print("\n📁 Check the 'generated_pdfs' folder to review:")
        print("   1. Company Policies (should match pages 3-9)")
        print("   2. Direct Deposit (should match page 18 - ADP form)")
        print("   3. Weapons Policy (should match page 22)")
        print("   4. Health Insurance (should match pages 23-28 - Lakecrest)")
        print("\n⚠️  Still TODO:")
        print("   - Human Trafficking Awareness (pages 19-21)")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error generating PDFs: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())