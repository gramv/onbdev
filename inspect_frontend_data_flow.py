#!/usr/bin/env python3
"""
Script to inspect and simulate the exact frontend data flow
"""
import json
import sys
import os

def simulate_frontend_data_flow():
    """Simulate the exact data flow from frontend to backend"""

    print("🔍 FRONTEND DATA FLOW SIMULATION")
    print("=" * 50)

    # Step 1: Simulate what would be in session storage
    print("\n1️⃣ SIMULATING SESSION STORAGE DATA:")

    # Personal Info Step data (what user enters first)
    personal_info_data = {
        "personalInfo": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789"
        }
    }

    # Direct Deposit form data (what user fills in DirectDepositStep)
    direct_deposit_form_data = {
        "paymentMethod": "direct_deposit",
        "depositType": "full",
        "primaryAccount": {
            "bankName": "Chase Bank",
            "routingNumber": "021000021",
            "accountNumber": "1234567890",
            "accountType": "checking",
            "depositAmount": "",
            "percentage": 100
        },
        "additionalAccounts": [],
        "voidedCheckUploaded": False,
        "bankLetterUploaded": False,
        "totalPercentage": 100,
        "authorizeDeposit": True,
        "employeeSignature": "",
        "dateOfAuth": "2025-01-27"
    }

    # Session storage structure (what gets saved)
    session_data = {
        "onboarding_personal-info_data": json.dumps(personal_info_data),
        "onboarding_direct-deposit_data": json.dumps({
            "formData": direct_deposit_form_data,
            "isValid": True,
            "isSigned": False,
            "showReview": True
        })
    }

    print("Personal Info Data:")
    print(json.dumps(personal_info_data, indent=2))

    print("\nDirect Deposit Form Data:")
    print(json.dumps(direct_deposit_form_data, indent=2))

    # Step 2: Simulate DirectDepositStep.tsx SSN retrieval
    print("\n2️⃣ SSN RETRIEVAL SIMULATION:")

    ssn_sources = [
        ("Personal Info", personal_info_data.get("personalInfo", {}).get("ssn")),
        ("Direct Form SSN", direct_deposit_form_data.get("ssn")),
    ]

    found_ssn = None
    ssn_source = "NOT FOUND"

    for source_name, ssn_value in ssn_sources:
        if ssn_value:
            found_ssn = ssn_value
            ssn_source = source_name
            break

    print(f"SSN Found: {found_ssn or 'NOT FOUND'}")
    print(f"SSN Source: {ssn_source}")

    # Step 3: Simulate extraPdfData creation
    print("\n3️⃣ EXTRA PDF DATA CREATION:")

    # Simulate employee object (would come from API)
    employee = {
        "id": "test-employee-123",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com"
    }

    extra_pdf_data = {
        "firstName": employee.get("firstName", ""),
        "lastName": employee.get("lastName", ""),
        "email": employee.get("email", ""),
        "ssn": found_ssn or ""
    }

    print("Extra PDF Data:")
    print(json.dumps(extra_pdf_data, indent=2))

    # Step 4: Simulate PDF payload creation
    print("\n4️⃣ PDF PAYLOAD CREATION:")

    pdf_payload = {
        **direct_deposit_form_data,
        **extra_pdf_data,
        "signatureData": "",  # Would be added during signing
        "ssn": found_ssn or extra_pdf_data.get("ssn", "")
    }

    print("PDF Payload (what gets sent to backend):")
    print(json.dumps(pdf_payload, indent=2))

    # Step 5: Simulate backend processing
    print("\n5️⃣ BACKEND PROCESSING SIMULATION:")

    # This is what the backend receives
    backend_request = {
        "employee_data": pdf_payload
    }

    print("Backend Request:")
    print(json.dumps(backend_request, indent=2))

    # Simulate backend data extraction
    employee_data_from_request = backend_request["employee_data"]

    print(f"\nRaw employee_data keys: {list(employee_data_from_request.keys())}")

    # Find primaryAccount data (backend logic)
    primary_account = None

    if "primaryAccount" in employee_data_from_request:
        primary_account = employee_data_from_request["primaryAccount"]
        print("✅ Found primaryAccount at root level")
    elif "formData" in employee_data_from_request and "primaryAccount" in employee_data_from_request["formData"]:
        primary_account = employee_data_from_request["formData"]["primaryAccount"]
        print("✅ Found primaryAccount nested in formData")
    else:
        primary_account = {}
        print("❌ Could not find primaryAccount data")

    print("Primary Account Data:")
    print(json.dumps(primary_account, indent=2))

    # Build final PDF data structure
    pdf_data = {
        "first_name": employee_data_from_request.get("firstName", ""),
        "last_name": employee_data_from_request.get("lastName", ""),
        "employee_id": "test-employee-123",
        "email": employee_data_from_request.get("email", ""),
        "ssn": employee_data_from_request.get("ssn", ""),
        "direct_deposit": {
            "bank_name": primary_account.get("bankName", ""),
            "account_type": primary_account.get("accountType", "checking"),
            "routing_number": primary_account.get("routingNumber", ""),
            "account_number": primary_account.get("accountNumber", ""),
            "deposit_type": employee_data_from_request.get("depositType", "full"),
            "deposit_amount": primary_account.get("depositAmount", ""),
        },
        "signatureData": employee_data_from_request.get("signatureData", ""),
        "property": {"name": "Test Property"},
    }

    print("\nFinal PDF Data Structure:")
    print(json.dumps(pdf_data, indent=2))

    # Step 6: Test actual PDF generation
    print("\n6️⃣ PDF GENERATION TEST:")

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend', 'app'))

        from app.pdf_forms import PDFFormFiller

        pdf_filler = PDFFormFiller()
        pdf_bytes = pdf_filler.fill_direct_deposit_form(pdf_data)

        if pdf_bytes:
            print(f"✅ PDF Generation SUCCESSFUL! Size: {len(pdf_bytes)} bytes")

            # Save test PDF
            with open("frontend_simulation_test.pdf", "wb") as f:
                f.write(pdf_bytes)
            print("📄 Saved as: frontend_simulation_test.pdf")
        else:
            print("❌ PDF Generation returned empty bytes")

    except Exception as e:
        print(f"❌ PDF Generation ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("📋 ANALYSIS SUMMARY:")
    print("✅ SSN Retrieval:", "WORKING" if found_ssn else "BROKEN")
    print("✅ Primary Account Data:", "WORKING" if primary_account else "BROKEN")
    print("✅ PDF Data Structure:", "WORKING" if pdf_data["direct_deposit"]["bank_name"] else "BROKEN")
    print("✅ PDF Generation:", "WORKING" if pdf_bytes else "BROKEN")

    if not found_ssn:
        print("\n🚨 ISSUE IDENTIFIED: SSN not found in any data source")
        print("   This would result in empty SSN field in PDF")

    if not primary_account:
        print("\n🚨 ISSUE IDENTIFIED: Primary account data not found")
        print("   This would result in empty bank fields in PDF")

    if not pdf_data["direct_deposit"]["bank_name"]:
        print("\n🚨 ISSUE IDENTIFIED: Bank name not extracted from primaryAccount")
        print("   This would result in empty bank name field in PDF")

def check_real_session_data():
    """Instructions for checking real browser session data"""
    print("\n🔍 HOW TO CHECK REAL BROWSER DATA:")
    print("1. Open browser developer console (F12)")
    print("2. Go to Application/Storage > Session Storage")
    print("3. Look for keys starting with 'onboarding_'")
    print("4. Run: debugDirectDepositData()")
    print("5. Run: testPdfGeneration()")
    print("\nThis will show you the exact data being sent to the backend.")

if __name__ == "__main__":
    simulate_frontend_data_flow()
    check_real_session_data()
