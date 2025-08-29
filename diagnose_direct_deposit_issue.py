#!/usr/bin/env python3
"""
Comprehensive diagnostic script for Direct Deposit PDF generation issues
"""
import json
import sys
import os
import requests
import base64
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend', 'app'))

def test_template_fields():
    """Test if template fields are being read correctly"""
    print("=== TEMPLATE FIELD ANALYSIS ===")

    try:
        import fitz
        template_path = os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend', 'static', 'direct-deposit-template.pdf')
        doc = fitz.open(template_path)
        page = doc[0]

        print(f"Template loaded: {len(doc)} pages")

        # Get all widgets
        widgets = list(page.widgets())
        print(f"Total widgets found: {len(widgets)}")

        # Categorize fields
        text_fields = []
        checkbox_fields = []
        other_fields = []

        for widget in widgets:
            field_info = {
                'name': widget.field_name or 'unnamed',
                'type': widget.field_type,
                'rect': widget.rect,
                'value': widget.field_value
            }

            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                text_fields.append(field_info)
            elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                checkbox_fields.append(field_info)
            else:
                other_fields.append(field_info)

        print(f"\nText Fields ({len(text_fields)}):")
        for field in text_fields[:15]:  # Show first 15
            print(f"  - {field['name']} (rect: {field['rect']})")

        print(f"\nCheckbox Fields ({len(checkbox_fields)}):")
        for field in checkbox_fields[:10]:  # Show first 10
            print(f"  - {field['name']} (current: {field['value']})")

        doc.close()
        return text_fields, checkbox_fields

    except Exception as e:
        print(f"Error analyzing template: {e}")
        return [], []

def test_pdf_generation_with_real_data():
    """Test PDF generation with realistic data structures"""
    print("\n=== PDF GENERATION TEST ===")

    try:
        from app.pdf_forms import PDFFormFiller

        # Test different data structures that might be coming from frontend
        test_cases = [
            {
                "name": "Standard Frontend Data",
                "data": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "ssn": "123-45-6789",
                    "direct_deposit": {
                        "bank_name": "Chase Bank",
                        "routing_number": "021000021",
                        "account_number": "1234567890",
                        "account_type": "checking",
                        "deposit_type": "full",
                        "deposit_amount": ""
                    }
                }
            },
            {
                "name": "Frontend with primaryAccount structure",
                "data": {
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "email": "jane.smith@example.com",
                    "ssn": "987-65-4321",
                    "primaryAccount": {
                        "bankName": "Bank of America",
                        "routingNumber": "121000358",
                        "accountNumber": "9876543210",
                        "accountType": "checking",
                        "depositAmount": "",
                        "percentage": 100
                    },
                    "depositType": "full"
                }
            }
        ]

        pdf_filler = PDFFormFiller()

        for test_case in test_cases:
            print(f"\n--- Testing: {test_case['name']} ---")
            try:
                pdf_bytes = pdf_filler.fill_direct_deposit_form(test_case['data'])
                if pdf_bytes:
                    size = len(pdf_bytes)
                    print(f"✅ SUCCESS: Generated PDF ({size} bytes)")

                    # Save for inspection
                    filename = f"test_{test_case['name'].lower().replace(' ', '_')}.pdf"
                    with open(filename, 'wb') as f:
                        f.write(pdf_bytes)
                    print(f"📄 Saved as: {filename}")
                else:
                    print("❌ FAILED: No PDF data returned")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"Error in PDF generation test: {e}")

def test_backend_endpoint():
    """Test the actual backend endpoint"""
    print("\n=== BACKEND ENDPOINT TEST ===")

    base_url = "http://localhost:8000"

    # Test data that mimics what frontend sends
    test_payload = {
        "employee_data": {
            "paymentMethod": "direct_deposit",
            "depositType": "full",
            "primaryAccount": {
                "bankName": "Test Bank",
                "routingNumber": "123456789",
                "accountNumber": "9876543210",
                "accountType": "checking",
                "depositAmount": "",
                "percentage": 100
            },
            "firstName": "Test",
            "lastName": "User",
            "email": "test@example.com",
            "ssn": "123-45-6789"
        }
    }

    print("Test payload:")
    print(json.dumps(test_payload, indent=2))

    try:
        endpoint = f"{base_url}/api/onboarding/test-employee/direct-deposit/generate-pdf"
        print(f"\nCalling: {endpoint}")

        response = requests.post(endpoint, json=test_payload, timeout=30)

        print(f"Status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            try:
                response_data = response.json()
                print("Response data keys:", list(response_data.keys()) if response_data else "None")

                if 'data' in response_data and 'pdf' in response_data['data']:
                    pdf_b64 = response_data['data']['pdf']
                    pdf_bytes = base64.b64decode(pdf_b64)
                    print(f"✅ PDF received ({len(pdf_bytes)} bytes)")

                    with open("test_endpoint_response.pdf", "wb") as f:
                        f.write(pdf_bytes)
                    print("📄 Saved as: test_endpoint_response.pdf")
                else:
                    print("❌ No PDF data in response")
                    print("Full response:", json.dumps(response_data, indent=2))
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
                print("Raw response:", response.text[:500])
        else:
            print(f"❌ HTTP {response.status_code}")
            try:
                error_data = response.json()
                print("Error response:", json.dumps(error_data, indent=2))
            except:
                print("Raw error:", response.text[:500])

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("Start backend: cd hotel-onboarding-backend && python3 -m uvicorn app.main_enhanced:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Request error: {e}")

def analyze_backend_logs():
    """Check for any backend log files"""
    print("\n=== BACKEND LOG ANALYSIS ===")

    log_files = [
        "hotel-onboarding-backend/server.log",
        "hotel-onboarding-backend/debug.log",
        "/tmp/fastapi.log"
    ]

    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"Found log file: {log_file}")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Show last 20 lines
                    print("Last 20 lines:")
                    for line in lines[-20:]:
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"Error reading log: {e}")
        else:
            print(f"Log file not found: {log_file}")

def main():
    print("🔍 COMPREHENSIVE DIRECT DEPOSIT PDF DIAGNOSTIC")
    print("=" * 50)

    # Run all diagnostic tests
    text_fields, checkbox_fields = test_template_fields()
    test_pdf_generation_with_real_data()
    test_backend_endpoint()
    analyze_backend_logs()

    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print(f"Template has {len(text_fields)} text fields and {len(checkbox_fields)} checkboxes")

    if text_fields:
        key_fields = ['employee_name', 'social_security_number', 'employee_email', 'bank1_name']
        found_key_fields = [f for f in text_fields if f['name'] in key_fields]
        print(f"Key fields found: {[f['name'] for f in found_key_fields]}")

    print("\n🔧 RECOMMENDED NEXT STEPS:")
    print("1. Check browser console for frontend logging")
    print("2. Run debugDirectDepositData() in browser console")
    print("3. Verify SSN is present in session storage")
    print("4. Check primaryAccount data structure")
    print("5. Ensure backend server is running on port 8000")

if __name__ == "__main__":
    main()
