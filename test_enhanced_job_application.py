#!/usr/bin/env python3
"""
Test script for enhanced job application with comprehensive data
"""
import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def test_get_application_info():
    """Test getting application info for a property"""
    print("\n1. Testing GET /properties/{property_id}/info")
    
    # Use the test property created by the server
    property_id = "prop_test_001"
    
    response = requests.get(f"{BASE_URL}/properties/{property_id}/info")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Property: {data['property']['name']}")
        print(f"Departments and Positions:")
        for dept, positions in data['departments_and_positions'].items():
            print(f"  {dept}: {', '.join(positions)}")
    else:
        print(f"Error: {response.json()}")

def test_submit_comprehensive_application():
    """Test submitting a comprehensive job application"""
    print("\n2. Testing POST /apply/{property_id} with comprehensive data")
    
    property_id = "prop_test_001"
    
    # Create comprehensive application data matching the PDF form
    application_data = {
        # Personal Information
        "first_name": "John",
        "middle_initial": "M",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "phone_type": "cell",
        "secondary_phone": "(555) 987-6543",
        "secondary_phone_type": "home",
        "address": "123 Main Street",
        "apartment_unit": "Apt 4B",
        "city": "Anytown",
        "state": "CA",
        "zip_code": "12345",
        
        # Position Information
        "department": "Front Desk",
        "position": "Night Auditor",
        "salary_desired": "$18-20/hour",
        
        # Work Authorization & Legal
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "age_verification": True,
        "conviction_record": {
            "has_conviction": False,
            "explanation": None
        },
        
        # Availability
        "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "shift_preference": "night",
        "employment_type": "full_time",
        "seasonal_start_date": None,
        "seasonal_end_date": None,
        
        # Previous Hotel Employment
        "previous_hotel_employment": True,
        "previous_hotel_details": "Worked at Holiday Inn Downtown from 2020-2022",
        
        # How did you hear about us
        "how_heard": "employee_referral",
        "how_heard_detailed": "Jane Smith - current employee",
        
        # References
        "personal_reference": {
            "name": "Robert Johnson",
            "years_known": "5",
            "phone": "(555) 111-2222",
            "relationship": "Former supervisor"
        },
        
        # Military Service
        "military_service": {
            "branch": "Army",
            "from_date": "01/2015",
            "to_date": "01/2019",
            "rank_at_discharge": "Sergeant",
            "type_of_discharge": "Honorable",
            "disabilities_related": "None"
        },
        
        # Education History
        "education_history": [
            {
                "school_name": "State University",
                "location": "Springfield, IL",
                "years_attended": "2019-2023",
                "graduated": True,
                "degree_received": "Bachelor of Science in Hospitality Management"
            },
            {
                "school_name": "Central High School",
                "location": "Hometown, CA",
                "years_attended": "2011-2015",
                "graduated": True,
                "degree_received": "High School Diploma"
            }
        ],
        
        # Employment History (Last 3 employers)
        "employment_history": [
            {
                "company_name": "Holiday Inn Downtown",
                "phone": "(555) 333-4444",
                "address": "456 Hotel Blvd, Downtown, CA 54321",
                "supervisor": "Mary Williams",
                "job_title": "Front Desk Agent",
                "starting_salary": "$15/hour",
                "ending_salary": "$17/hour",
                "from_date": "06/2020",
                "to_date": "08/2022",
                "reason_for_leaving": "Relocated to new city",
                "may_contact": True
            },
            {
                "company_name": "Coffee Shop Co.",
                "phone": "(555) 555-6666",
                "address": "789 Main St, College Town, IL 67890",
                "supervisor": "Tom Brown",
                "job_title": "Barista/Shift Lead",
                "starting_salary": "$12/hour",
                "ending_salary": "$14/hour",
                "from_date": "09/2019",
                "to_date": "05/2020",
                "reason_for_leaving": "Better opportunity in hospitality",
                "may_contact": True
            }
        ],
        
        # Skills & Additional Info
        "skills_languages_certifications": "Fluent in English and Spanish. Certified in CPR/First Aid. Proficient in Opera PMS and Microsoft Office.",
        "voluntary_self_identification": {
            "gender": "male",
            "ethnicity": "hispanic_latino",
            "veteran_status": "protected_veteran",
            "disability_status": "no_disability"
        },
        
        # Experience (legacy fields)
        "experience_years": "2-5",
        "hotel_experience": "yes",
        
        # Additional Comments
        "additional_comments": "I am excited about the opportunity to join your team and bring my hospitality experience to contribute to excellent guest service."
    }
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=application_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Application ID: {data['application_id']}")
        print(f"Position Applied: {data['position_applied']}")
    else:
        print(f"Error: {response.json()}")

def test_minimal_application():
    """Test submitting application with minimal required fields"""
    print("\n3. Testing POST /apply/{property_id} with minimal data")
    
    property_id = "prop_test_001"
    
    # Create minimal application data
    application_data = {
        # Required Personal Information
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "(555) 999-8888",
        "phone_type": "cell",
        "address": "789 Oak Street",
        "city": "Sometown",
        "state": "NY",
        "zip_code": "54321",
        
        # Required Position Information
        "department": "Housekeeping",
        "position": "Housekeeper",
        
        # Required Work Authorization & Legal
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "age_verification": True,
        "conviction_record": {
            "has_conviction": False
        },
        
        # Required Availability
        "start_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "shift_preference": "morning",
        "employment_type": "part_time",
        
        # Required Previous Hotel Employment
        "previous_hotel_employment": False,
        
        # Required How did you hear about us
        "how_heard": "online",
        
        # Required References
        "personal_reference": {
            "name": "Alice Johnson",
            "years_known": "3",
            "phone": "(555) 777-8888",
            "relationship": "Friend"
        },
        
        # Required Military Service (empty)
        "military_service": {},
        
        # Required Education History (at least one entry)
        "education_history": [
            {
                "school_name": "Local High School",
                "location": "Hometown, NY",
                "years_attended": "2015-2019",
                "graduated": True,
                "degree_received": "High School Diploma"
            }
        ],
        
        # Required Employment History (can be empty list)
        "employment_history": [],
        
        # Required Experience fields
        "experience_years": "0-1",
        "hotel_experience": "no"
    }
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=application_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Application ID: {data['application_id']}")
    else:
        print(f"Error: {response.json()}")

def main():
    """Run all tests"""
    print("Testing Enhanced Job Application System")
    print("=" * 50)
    print("Using test property created by server: prop_test_001")
    
    # Run tests
    test_get_application_info()
    test_submit_comprehensive_application()
    test_minimal_application()

if __name__ == "__main__":
    main()