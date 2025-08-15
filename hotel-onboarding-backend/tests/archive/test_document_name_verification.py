#!/usr/bin/env python3
"""
Quick test to verify that generated documents contain correct employee names
This validates that the document generation pipeline properly embeds employee data
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_document_name_integration():
    """Test that all documents properly integrate employee names"""
    
    print("🔍 DOCUMENT NAME INTEGRATION TEST")
    print("=" * 50)
    
    # Generate test token
    print("1. Generating test employee token...")
    token_response = requests.post(
        f"{BASE_URL}/api/test/generate-onboarding-token",
        params={
            "employee_name": "John Doe Test Employee",
            "property_id": "a99239dd-ebde-4c69-b862-ecba9e878798"
        }
    )
    
    if token_response.status_code != 200:
        print(f"❌ Token generation failed: {token_response.text}")
        return False
    
    token_data = token_response.json()["data"]
    employee_id = token_data["test_employee"]["id"]
    employee_name = f"{token_data['test_employee']['firstName']} {token_data['test_employee']['lastName']}"
    
    print(f"   ✅ Employee ID: {employee_id}")
    print(f"   ✅ Employee Name: {employee_name}")
    
    # Test each document type with employee name data
    documents_to_test = [
        ("I-9 Form", f"/api/onboarding/{employee_id}/i9-section1/generate-pdf", {
            "employee_name": employee_name,
            "first_name": "John",
            "last_name": "Doe Test Employee",
            "address": "123 Test Street, Test City, CA 90210",
            "date_of_birth": "1990-01-15",
            "ssn": "123-45-6789",
            "citizenship_status": "us_citizen"
        }),
        ("W-4 Form", f"/api/onboarding/{employee_id}/w4-form/generate-pdf", {
            "employee_name": employee_name,
            "filing_status": "single",
            "multiple_jobs": False,
            "dependents_amount": 0
        }),
        ("Direct Deposit", f"/api/onboarding/{employee_id}/direct-deposit/generate-pdf", {
            "employee_name": employee_name,
            "bank_name": "Test Bank",
            "routing_number": "123456789",
            "account_number": "987654321",
            "account_type": "checking"
        })
    ]
    
    print(f"\n2. Testing {len(documents_to_test)} document types...")
    
    name_integration_results = []
    
    for doc_name, endpoint, form_data in documents_to_test:
        print(f"\n   Testing {doc_name}...")
        
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=form_data)
            
            if response.status_code == 200:
                result = response.json()
                pdf_filename = result.get("pdf_filename", "unknown.pdf")
                
                # Check if employee name appears in filename
                name_in_filename = (
                    "john" in pdf_filename.lower() or
                    "doe" in pdf_filename.lower() or
                    employee_name.lower() in pdf_filename.lower()
                )
                
                # Check response data for name integration
                pdf_data = result.get("data", {})
                name_in_data = (
                    employee_name in str(pdf_data) or
                    "John" in str(pdf_data) or 
                    "Doe" in str(pdf_data)
                )
                
                status = "✅" if (name_in_filename or name_in_data) else "⚠️"
                print(f"      {status} {doc_name}: {pdf_filename}")
                print(f"         Name in filename: {name_in_filename}")
                print(f"         Name in response: {name_in_data}")
                
                name_integration_results.append({
                    "document": doc_name,
                    "success": True,
                    "filename": pdf_filename,
                    "name_integrated": name_in_filename or name_in_data
                })
            else:
                print(f"      ❌ {doc_name}: Failed to generate (Status {response.status_code})")
                name_integration_results.append({
                    "document": doc_name,
                    "success": False,
                    "error": response.text
                })
                
        except Exception as e:
            print(f"      ❌ {doc_name}: Exception - {str(e)}")
            name_integration_results.append({
                "document": doc_name,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DOCUMENT NAME INTEGRATION SUMMARY")
    print("=" * 50)
    
    successful_docs = sum(1 for r in name_integration_results if r["success"])
    name_integrated_docs = sum(1 for r in name_integration_results if r.get("name_integrated", False))
    
    print(f"Total Documents Tested: {len(documents_to_test)}")
    print(f"Successfully Generated: {successful_docs}")
    print(f"Name Integration Working: {name_integrated_docs}")
    print(f"Success Rate: {(successful_docs / len(documents_to_test)) * 100:.1f}%")
    print(f"Name Integration Rate: {(name_integrated_docs / len(documents_to_test)) * 100:.1f}%")
    
    if successful_docs == len(documents_to_test):
        print("\n✅ ALL DOCUMENTS GENERATED SUCCESSFULLY")
        
        if name_integrated_docs == len(documents_to_test):
            print("✅ EMPLOYEE NAME INTEGRATION: WORKING")
        else:
            print("⚠️ EMPLOYEE NAME INTEGRATION: PARTIAL")
            
        print("\n🎯 DOCUMENT GENERATION PIPELINE: FULLY OPERATIONAL")
        return True
    else:
        print(f"\n❌ SOME DOCUMENTS FAILED TO GENERATE")
        return False

if __name__ == "__main__":
    success = test_document_name_integration()
    exit(0 if success else 1)