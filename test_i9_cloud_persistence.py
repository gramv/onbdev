#!/usr/bin/env python3
"""
Test I-9 cloud persistence across sessions
This script simulates the complete workflow to verify data persists
"""
import requests
import json
import time
import sys
from datetime import datetime

API_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

def generate_test_token():
    """Generate a test JWT token"""
    print("🔐 Generating test token...")
    
    # Create test employee ID
    test_employee_id = f"test-emp-{int(time.time())}"
    
    # Generate token via API
    token_data = {
        "email": f"{test_employee_id}@test.com",
        "password": "test123"  # Not used for test employees
    }
    
    # For test employees, we'll simulate a token
    import jwt
    import os
    from datetime import datetime, timedelta
    
    secret_key = os.getenv("JWT_SECRET_KEY", "test-secret-key")
    
    payload = {
        "sub": test_employee_id,
        "employee_id": test_employee_id,
        "property_id": "test-property-123",
        "position": "Test Position",
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    
    print(f"✅ Generated token for employee: {test_employee_id}")
    print(f"📝 Token: {token[:50]}...")
    
    return test_employee_id, token

def save_i9_section1_data(employee_id, include_signature=False):
    """Save I-9 Section 1 data to cloud"""
    print(f"\n📤 Saving I-9 Section 1 data for {employee_id}...")
    
    test_data = {
        "formData": {
            "last_name": "CloudTest",
            "first_name": "John",
            "middle_initial": "C",
            "date_of_birth": "1990-01-01",
            "ssn": "123-45-6789",
            "email": "cloudtest@test.com",
            "phone": "555-1234",
            "address": "123 Cloud St",
            "city": "CloudCity",
            "state": "CC",
            "zip_code": "12345",
            "citizenship_status": "citizen",
            "alien_registration": None,
            "alien_expiration": None,
            "form_admission": None,
            "foreign_passport": None,
            "country_of_issuance": None
        },
        "signed": include_signature,
        "formValid": True
    }
    
    if include_signature:
        test_data["signatureData"] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        test_data["completedAt"] = datetime.now().isoformat()
    
    try:
        response = requests.post(
            f"{API_URL}/api/onboarding/{employee_id}/i9-section1",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ I-9 Section 1 saved successfully (signed: {include_signature})")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to save: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return False

def save_i9_section2_data(employee_id):
    """Save I-9 Section 2 document data to cloud"""
    print(f"\n📤 Saving I-9 Section 2 documents for {employee_id}...")
    
    test_data = {
        "documentSelection": "list_a",
        "uploadedDocuments": [
            {
                "id": f"doc_{int(time.time())}",
                "type": "list_a",
                "documentType": "US Passport",
                "fileName": "passport.pdf",
                "fileSize": 1048576,
                "uploadedAt": datetime.now().isoformat(),
                "ocrData": {
                    "document_number": "P123456789",
                    "expiry_date": "2030-01-01",
                    "name": "John CloudTest"
                }
            }
        ],
        "verificationComplete": True,
        "completedAt": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/onboarding/{employee_id}/i9-section2",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ I-9 Section 2 documents saved successfully")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to save: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error saving documents: {e}")
        return False

def retrieve_i9_data(employee_id):
    """Retrieve I-9 data from cloud"""
    print(f"\n📥 Retrieving I-9 data for {employee_id}...")
    
    all_data = {}
    
    # Get I-9 Section 1
    try:
        response = requests.get(f"{API_URL}/api/onboarding/{employee_id}/i9-section1")
        if response.status_code == 200:
            result = response.json()
            # Handle the success response wrapper
            if result.get('success') and result.get('data'):
                data = result['data']
            else:
                data = result
            
            all_data["section1"] = data
            print("✅ I-9 Section 1 retrieved:")
            print(f"   Raw response: {data}")
            print(f"   - Citizenship Status: {data.get('form_data', {}).get('citizenship_status', 'Not set')}")
            print(f"   - Signed: {data.get('signed', False)}")
        else:
            print(f"⚠️  No I-9 Section 1 data found (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error retrieving Section 1: {e}")
    
    # Get I-9 Section 2
    try:
        response = requests.get(f"{API_URL}/api/onboarding/{employee_id}/i9-section2")
        if response.status_code == 200:
            result = response.json()
            # Handle the success response wrapper
            if result.get('success') and result.get('data'):
                data = result['data']
            else:
                data = result
                
            all_data["section2"] = data
            print("✅ I-9 Section 2 retrieved:")
            print(f"   Raw response: {data}")
            if data and (data.get("documents") or data.get("uploadedDocuments")):
                docs = data.get("uploadedDocuments") or data.get("documents") or []
                print(f"   - Documents: {len(docs)} document(s) found")
                for doc in docs:
                    print(f"     • {doc.get('documentType', doc.get('document_type', 'Unknown'))} - {doc.get('fileName', doc.get('file_name', 'No name'))}")
            else:
                print("   - No documents found")
        else:
            print(f"⚠️  No I-9 Section 2 data found (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error retrieving Section 2: {e}")
    
    return all_data

def test_cross_session_persistence():
    """Test that data persists across different sessions"""
    print("\n" + "="*60)
    print("🧪 TESTING I-9 CLOUD PERSISTENCE ACROSS SESSIONS")
    print("="*60)
    
    # Generate test employee
    employee_id, token = generate_test_token()
    
    # Session 1: Save data
    print("\n📝 SESSION 1: Saving I-9 data...")
    print("-"*40)
    
    # Save Section 1 (unsigned)
    if not save_i9_section1_data(employee_id, include_signature=False):
        print("❌ Failed to save Section 1 data")
        return False
    
    # Save Section 2 documents
    if not save_i9_section2_data(employee_id):
        print("❌ Failed to save Section 2 documents")
        return False
    
    # Save Section 1 (signed)
    if not save_i9_section1_data(employee_id, include_signature=True):
        print("❌ Failed to sign Section 1")
        return False
    
    # Simulate clearing local storage
    print("\n🧹 Simulating browser session clear...")
    print("   (In real scenario, this would clear sessionStorage)")
    time.sleep(2)
    
    # Session 2: Retrieve data
    print("\n📝 SESSION 2: Retrieving I-9 data (simulating new browser)...")
    print("-"*40)
    
    retrieved_data = retrieve_i9_data(employee_id)
    
    # Verify data persistence
    print("\n🔍 VERIFICATION RESULTS:")
    print("-"*40)
    
    success = True
    
    # Check Section 1
    if "section1" in retrieved_data:
        section1 = retrieved_data["section1"]
        citizenship = section1.get("form_data", {}).get("citizenship_status")
        is_signed = section1.get("signed", False)
        
        if citizenship == "citizen":
            print("✅ Citizenship status persisted correctly")
        else:
            print(f"❌ Citizenship status not persisted (expected: citizen, got: {citizenship})")
            success = False
        
        if is_signed:
            print("✅ Signature persisted correctly")
        else:
            print("❌ Signature not persisted")
            success = False
    else:
        print("❌ Section 1 data not found")
        success = False
    
    # Check Section 2
    if "section2" in retrieved_data:
        section2 = retrieved_data["section2"]
        documents = section2.get("documents", [])
        
        if len(documents) > 0:
            print(f"✅ {len(documents)} document(s) persisted correctly")
            for doc in documents:
                doc_type = doc.get("documentType") or doc.get("document_type") or doc.get("document_name")
                if doc_type == "US Passport":
                    print("✅ US Passport document details persisted")
                else:
                    print(f"✅ Document persisted: {doc_type}")
        else:
            print("❌ Documents not persisted")
            success = False
    else:
        print("❌ Section 2 data not found")
        success = False
    
    # Final result
    print("\n" + "="*60)
    if success:
        print("🎉 SUCCESS: I-9 data persists across sessions!")
        print("✅ The cloud sync is working correctly")
        print(f"✅ Employee ID: {employee_id}")
        print(f"✅ Token: {token[:50]}...")
        print("\n📱 To test in browser:")
        print(f"   1. Open: {FRONTEND_URL}/onboard?token={token}")
        print("   2. Navigate to I-9 Section 1 - data should be pre-filled")
        print("   3. Navigate to Document Upload - documents should be shown")
    else:
        print("❌ FAILURE: Some data did not persist correctly")
        print("⚠️  Please check the backend logs for errors")
    print("="*60)
    
    return success

def main():
    """Main test runner"""
    print("🚀 I-9 Cloud Persistence Test Suite")
    print(f"   API URL: {API_URL}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_URL}/healthz")
        if response.status_code != 200:
            print("❌ Backend is not running! Please start it first.")
            print("   Run: cd hotel-onboarding-backend && python3 -m uvicorn app.main_enhanced:app --port 8000")
            return False
    except:
        print("❌ Cannot connect to backend at", API_URL)
        print("   Please ensure the backend is running")
        return False
    
    # Run the test
    return test_cross_session_persistence()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)