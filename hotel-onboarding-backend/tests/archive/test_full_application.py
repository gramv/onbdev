#!/usr/bin/env python3
"""
Test Full Application Data
Creates a complete application with all required fields
"""

import requests
import json
from datetime import datetime, date
from setup_test_data_simple import SimpleTestSetup

BASE_URL = "http://localhost:8000"

def get_property_id():
    """Get the test property ID"""
    setup = SimpleTestSetup()
    result = setup.client.table('properties').select('*').eq('name', 'Demo Hotel').execute()
    if result.data:
        return result.data[0]['id']
    return None

def create_complete_application_data():
    """Create complete application data with all required fields"""
    
    return {
        # Personal Information
        "first_name": "Jane",
        "middle_initial": "M",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "(555) 123-4567",
        "phone_is_cell": True,
        "phone_is_home": False,
        "secondary_phone": "(555) 987-6543",
        "secondary_phone_is_cell": False,
        "secondary_phone_is_home": True,
        "address": "123 Main Street",
        "apartment_unit": "Apt 2B",
        "city": "Demo City",
        "state": "CA",
        "zip_code": "90210",
        
        # Position Information
        "department": "Front Desk",
        "position": "Front Desk Associate",
        "salary_desired": "$18/hour",
        
        # Work Authorization & Legal
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "age_verification": True,
        "conviction_record": {
            "has_conviction": False,
            "explanation": None
        },
        
        # Availability
        "start_date": "2025-08-15",
        "shift_preference": "flexible",
        "employment_type": "full_time",
        "seasonal_start_date": None,
        "seasonal_end_date": None,
        
        # Previous Hotel Employment
        "previous_hotel_employment": True,
        "previous_hotel_details": "Marriott Downtown, 2022-2024",
        
        # How did you hear about us?
        "how_heard": "online",
        "how_heard_detailed": "Company website",
        
        # References
        "personal_reference": {
            "name": "John Smith",
            "years_known": "5",
            "phone": "(555) 111-2222",
            "relationship": "Former colleague"
        },
        
        # Military Service
        "military_service": {
            "branch": None,
            "from_date": None,
            "to_date": None,
            "rank_at_discharge": None,
            "type_of_discharge": None,
            "disabilities_related": None
        },
        
        # Education History
        "education_history": [
            {
                "school_name": "Demo High School",
                "location": "Demo City, CA",
                "years_attended": "2016-2020",
                "graduated": True,
                "degree_received": "High School Diploma"
            },
            {
                "school_name": "Community College",
                "location": "Demo City, CA",
                "years_attended": "2020-2022",
                "graduated": True,
                "degree_received": "Associate Degree in Hospitality"
            }
        ],
        
        # Employment History
        "employment_history": [
            {
                "company_name": "Previous Hotel Inc",
                "phone": "(555) 333-4444",
                "address": "456 Business Ave, Demo City, CA",
                "supervisor": "Mike Manager",
                "job_title": "Front Desk Clerk",
                "starting_salary": "$15/hour",
                "ending_salary": "$17/hour",
                "from_date": "01/2022",
                "to_date": "12/2023",
                "reason_for_leaving": "Career advancement",
                "may_contact": True
            },
            {
                "company_name": "Restaurant ABC",
                "phone": "(555) 555-6666",
                "address": "789 Food St, Demo City, CA",
                "supervisor": "Sarah Supervisor",
                "job_title": "Server",
                "starting_salary": "$12/hour",
                "ending_salary": "$14/hour",
                "from_date": "06/2020",
                "to_date": "12/2021",
                "reason_for_leaving": "Changed career path",
                "may_contact": True
            },
            {
                "company_name": "Retail Store XYZ",
                "phone": "(555) 777-8888",
                "address": "321 Shop Blvd, Demo City, CA",
                "supervisor": "Tom Boss",
                "job_title": "Sales Associate",
                "starting_salary": "$11/hour",
                "ending_salary": "$12/hour",
                "from_date": "05/2019",
                "to_date": "05/2020",
                "reason_for_leaving": "Went to college",
                "may_contact": False
            }
        ],
        
        # Skills, Languages, and Certifications
        "skills_languages_certifications": "Fluent in English and Spanish, Microsoft Office, Customer service",
        
        # Voluntary Self-Identification (optional)
        "voluntary_self_identification": None,
        
        # Experience
        "experience_years": "2-5",
        "hotel_experience": "yes",
        
        # Additional Information
        "additional_comments": "I am excited to join your team and bring my hospitality experience to this role."
    }

def test_complete_application():
    """Test application with complete data"""
    
    property_id = get_property_id()
    if not property_id:
        print("❌ No test property found")
        return None
    
    print(f"Testing complete application for property: {property_id}")
    
    application_data = create_complete_application_data()
    
    session = requests.Session()
    
    try:
        response = session.post(f"{BASE_URL}/apply/{property_id}", json=application_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ SUCCESS - Application created!")
            print(f"Application ID: {result.get('id', 'N/A')}")
            print(f"Status: {result.get('status', 'N/A')}")
            return result
        else:
            print(f"❌ FAILED - Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("COMPLETE APPLICATION TESTING")
    print("=" * 60)
    
    result = test_complete_application()
    
    if result:
        print(f"\n🎉 Complete application endpoint is working!")
        print(f"Application created with ID: {result.get('id')}")
    else:
        print(f"\n⚠️  Application submission failed")