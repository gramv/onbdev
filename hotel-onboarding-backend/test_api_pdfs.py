#\!/usr/bin/env python3
"""
Test PDF generation via API endpoints
"""
import requests
import json
import base64
from datetime import datetime
import os

# Backend URL
BASE_URL = "http://localhost:8000"

def save_pdf_from_base64(base64_data, filename):
    """Save base64 PDF to file"""
    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Remove data URL prefix if present
    if base64_data.startswith('data:'):
        base64_data = base64_data.split(',')[1]
    
    pdf_bytes = base64.b64decode(base64_data)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)
    print(f"✅ Saved: {filepath}")
    return filepath

def generate_sample_signature():
    """Generate a sample signature"""
    # Simple black dot as signature placeholder
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_company_policies():
    """Test Company Policies PDF via API"""
    print("\n📋 Testing Company Policies PDF via API...")
    
    data = {
        "employee_data": {
            "employee_name": "John Smith",
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
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/onboarding/test-employee/company-policies/generate-pdf",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("data", {}).get("pdf"):
                save_pdf_from_base64(result["data"]["pdf"], "api_company_policies.pdf")
                print("   ✓ Company Policies PDF generated successfully")
            else:
                print(f"   ❌ Error in response: {result}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def test_direct_deposit():
    """Test Direct Deposit PDF via API"""
    print("\n💰 Testing Direct Deposit PDF via API...")
    
    data = {
        "employee_data": {
            "employee_name": "John Smith",
            "ssn": "123-45-6789",
            "property_name": "Grand Hotel & Resort",
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
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/onboarding/test-employee/direct-deposit/generate-pdf",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("data", {}).get("pdf"):
                save_pdf_from_base64(result["data"]["pdf"], "api_direct_deposit.pdf")
                print("   ✓ Direct Deposit PDF generated successfully")
            else:
                print(f"   ❌ Error in response: {result}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def test_weapons_policy():
    """Test Weapons Policy PDF via API"""
    print("\n🚫 Testing Weapons Policy PDF via API...")
    
    data = {
        "employee_data": {
            "employee_name": "John Smith",
            "property_name": "Grand Hotel & Resort",
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
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/onboarding/test-employee/weapons-policy/generate-pdf",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("data", {}).get("pdf"):
                save_pdf_from_base64(result["data"]["pdf"], "api_weapons_policy.pdf")
                print("   ✓ Weapons Policy PDF generated successfully")
            else:
                print(f"   ❌ Error in response: {result}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 API PDF GENERATION TEST")
    print("=" * 70)
    
    test_company_policies()
    test_direct_deposit()
    test_weapons_policy()
    
    print("\n" + "=" * 70)
    print("✅ Test complete\!")
    print("\n📁 Check the 'generated_pdfs' folder for:")
    print("   - api_company_policies.pdf")
    print("   - api_direct_deposit.pdf")
    print("   - api_weapons_policy.pdf")
    print("=" * 70)
