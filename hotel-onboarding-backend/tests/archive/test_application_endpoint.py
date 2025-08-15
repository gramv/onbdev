#!/usr/bin/env python3
"""
Test Application Endpoint
Tests the job application submission endpoint with various data formats
"""

import requests
import json
from setup_test_data_simple import SimpleTestSetup

BASE_URL = "http://localhost:8000"

def get_property_id():
    """Get the test property ID"""
    setup = SimpleTestSetup()
    result = setup.client.table('properties').select('*').eq('name', 'Demo Hotel').execute()
    if result.data:
        return result.data[0]['id']
    return None

def test_application_variations():
    """Test different application data formats"""
    
    property_id = get_property_id()
    if not property_id:
        print("❌ No test property found")
        return
    
    print(f"Testing application endpoint for property: {property_id}")
    
    # Variation 1: Minimal required fields
    minimal_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Receptionist"
    }
    
    # Variation 2: Extended fields based on the model
    extended_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "(555) 987-6543",
        "phone_is_cell": True,
        "address": "456 Oak Ave",
        "city": "Testville",
        "state": "CA",
        "zip_code": "90211",
        "department": "Front Desk",
        "position": "Front Desk Associate",
        "work_authorization": "Yes",
        "criminal_conviction": "No",
        "position_preferences": ["Full-time"],
        "availability_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "start_date_preference": "Immediately",
        "previous_employment": [
            {
                "company": "Previous Hotel",
                "position": "Receptionist",
                "duration": "2 years"
            }
        ],
        "terms_agreement": True
    }
    
    # Variation 3: All possible fields
    complete_data = {
        "first_name": "Alice",
        "middle_initial": "M",
        "last_name": "Johnson",
        "email": "alice.johnson@example.com",
        "phone": "(555) 456-7890",
        "phone_is_cell": True,
        "phone_is_home": False,
        "secondary_phone": "(555) 098-7654",
        "secondary_phone_is_cell": False,
        "secondary_phone_is_home": True,
        "address": "789 Pine St",
        "apartment_unit": "Apt 2B",
        "city": "Demo City",
        "state": "CA",
        "zip_code": "90212",
        "department": "Front Desk",
        "position": "Front Desk Supervisor",
        "work_authorization": "Yes",
        "criminal_conviction": "No",
        "conviction_details": "",
        "position_preferences": ["Full-time", "Part-time"],
        "availability_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "availability_hours": "Flexible",
        "start_date_preference": "Within 2 weeks",
        "salary_expectations": "$18-20/hour",
        "previous_employment": [
            {
                "company": "Marriott Hotel",
                "position": "Front Desk Agent",
                "duration": "3 years",
                "reason_for_leaving": "Career advancement"
            }
        ],
        "education": {
            "high_school": "Completed",
            "college": "Some college",
            "certifications": ["Hospitality Management Certificate"]
        },
        "references": [
            {
                "name": "John Manager",
                "relationship": "Former Supervisor",
                "phone": "(555) 111-2222"
            }
        ],
        "emergency_contact": {
            "name": "Bob Johnson",
            "relationship": "Spouse",
            "phone": "(555) 333-4444"
        },
        "terms_agreement": True,
        "background_check_consent": True,
        "drug_test_consent": True
    }
    
    variations = [
        ("Minimal Data", minimal_data),
        ("Extended Data", extended_data),
        ("Complete Data", complete_data)
    ]
    
    session = requests.Session()
    
    for name, data in variations:
        print(f"\nTesting {name}:")
        
        try:
            response = session.post(f"{BASE_URL}/apply/{property_id}", json=data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ SUCCESS - Application ID: {result.get('id', 'N/A')}")
                return result  # Return first successful application
            else:
                print(f"❌ FAILED - Response: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("APPLICATION ENDPOINT TESTING")
    print("=" * 60)
    
    application_result = test_application_variations()
    
    if application_result:
        print(f"\n🎉 Application endpoint is working!")
        print(f"Successfully created application: {application_result.get('id')}")
    else:
        print(f"\n⚠️  All application attempts failed")