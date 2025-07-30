#!/usr/bin/env python3
"""
Comprehensive backend tests for JobApplicationFormV2
Tests the new multi-step job application with enhanced data structure
"""

import asyncio
import json
import time
from datetime import datetime, date
from typing import Dict, Any
import aiohttp
import requests

BASE_URL = "http://127.0.0.1:8000"

# Test data for complete application
COMPLETE_APPLICATION_DATA = {
    # Personal Information
    "first_name": "John",
    "middle_name": "Michael",
    "last_name": "Doe",
    "email": f"john.doe.{int(time.time())}@example.com",  # Unique email
    "phone": "(555) 123-4567",
    "address": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    
    # Position & Availability
    "department": "Front Desk",
    "position": "Guest Service Agent",
    "desired_salary": "35000",
    "employment_type": "full-time",
    "start_date": "2025-02-01",
    "shift_preference": "any",
    "availability_weekends": "yes",
    "availability_holidays": "yes",
    "reliable_transportation": "yes",
    "work_authorized": "yes",
    "sponsorship_required": "no",
    
    # Employment History
    "employment_history": [
        {
            "employer_name": "Previous Hotel Inc",
            "job_title": "Front Desk Clerk",
            "start_date": "2020-01-15",
            "end_date": "2023-12-31",
            "is_current": False,
            "responsibilities": "Checked in guests, handled reservations, resolved customer complaints",
            "reason_for_leaving": "Seeking career advancement",
            "supervisor_name": "Jane Smith",
            "supervisor_phone": "(555) 987-6543",
            "may_contact": True
        },
        {
            "employer_name": "Current Employer LLC",
            "job_title": "Customer Service Representative",
            "start_date": "2024-01-15",
            "end_date": "",
            "is_current": True,
            "responsibilities": "Handle customer inquiries, process orders, maintain records",
            "reason_for_leaving": "Looking for hospitality industry opportunity",
            "supervisor_name": "Bob Johnson",
            "supervisor_phone": "(555) 456-7890",
            "may_contact": False
        }
    ],
    
    # Education & Skills
    "education_level": "bachelors",
    "high_school_info": {
        "name": "Central High School",
        "city": "Springfield",
        "state": "IL",
        "graduated": "yes",
        "graduation_year": "2015"
    },
    "college_info": {
        "name": "State University",
        "city": "Chicago",
        "state": "IL",
        "degree": "Bachelor of Arts",
        "major": "Hospitality Management",
        "graduation_year": "2019"
    },
    "additional_education": "Certified Hotel Administrator (CHA) - 2022",
    "skills": ["Customer Service", "Microsoft Office", "Property Management Systems", "Multilingual"],
    "certifications": ["CPR Certified", "Food Handler's License"],
    "languages": ["English", "Spanish", "French"],
    
    # Additional Information
    "references": [
        {
            "name": "Alice Williams",
            "relationship": "Former Manager",
            "phone": "(555) 111-2222",
            "email": "alice.williams@example.com",
            "years_known": "3"
        },
        {
            "name": "David Brown",
            "relationship": "Professional Colleague",
            "phone": "(555) 333-4444",
            "email": "david.brown@example.com",
            "years_known": "5"
        },
        {
            "name": "Sarah Davis",
            "relationship": "Mentor",
            "phone": "(555) 555-6666",
            "email": "sarah.davis@example.com",
            "years_known": "7"
        }
    ],
    "has_criminal_record": "no",
    "criminal_record_explanation": "",
    "additional_comments": "I am passionate about the hospitality industry and eager to contribute to your team.",
    
    # Voluntary Self-Identification
    "gender": "male",
    "ethnicity": "white",
    "veteran_status": "not_veteran",
    "disability_status": "no_disability",
    
    # Consent
    "physical_requirements_acknowledged": True,
    "background_check_consent": True,
    "information_accuracy_certified": True,
    "at_will_employment_acknowledged": True
}

def create_test_property() -> str:
    """Create a test property and return its ID"""
    property_data = {
        "name": f"Test Hotel {int(time.time())}",
        "address": "456 Test Street",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "phone": "(555) 888-9999"
    }
    
    response = requests.post(f"{BASE_URL}/properties", json=property_data)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        raise Exception(f"Failed to create property: {response.text}")

def test_property_info_endpoint():
    """Test the property info endpoint used by the application form"""
    print("\n=== Testing Property Info Endpoint ===")
    
    # Create a test property
    property_id = create_test_property()
    print(f"Created test property: {property_id}")
    
    # Test getting property info
    response = requests.get(f"{BASE_URL}/properties/{property_id}/info")
    assert response.status_code == 200, f"Failed to get property info: {response.text}"
    
    data = response.json()
    assert "property" in data
    assert "departments_and_positions" in data
    assert "application_url" in data
    assert "is_accepting_applications" in data
    
    print(f"✓ Property info retrieved successfully")
    print(f"  - Property: {data['property']['name']}")
    print(f"  - Departments: {list(data['departments_and_positions'].keys())}")
    print(f"  - Accepting applications: {data['is_accepting_applications']}")
    
    return property_id

def test_application_submission():
    """Test submitting a complete job application"""
    print("\n=== Testing Application Submission ===")
    
    # Create property
    property_id = test_property_info_endpoint()
    
    # Submit application
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=COMPLETE_APPLICATION_DATA
    )
    
    assert response.status_code == 200, f"Failed to submit application: {response.text}"
    
    result = response.json()
    assert "application_id" in result
    assert result["status"] == "Application submitted successfully"
    
    print(f"✓ Application submitted successfully")
    print(f"  - Application ID: {result['application_id']}")
    
    return result["application_id"], property_id

def test_duplicate_application_prevention():
    """Test that duplicate applications are prevented"""
    print("\n=== Testing Duplicate Application Prevention ===")
    
    # Create property
    property_id = create_test_property()
    
    # Submit first application
    response1 = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=COMPLETE_APPLICATION_DATA
    )
    assert response1.status_code == 200
    
    # Try to submit duplicate application
    response2 = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=COMPLETE_APPLICATION_DATA
    )
    
    assert response2.status_code == 400, "Duplicate application should be rejected"
    assert "already submitted" in response2.json()["detail"].lower()
    
    print("✓ Duplicate application correctly prevented")

def test_incomplete_application_validation():
    """Test validation of incomplete applications"""
    print("\n=== Testing Incomplete Application Validation ===")
    
    property_id = create_test_property()
    
    # Test missing required fields
    incomplete_data = {
        "first_name": "John",
        "last_name": "Doe",
        # Missing email, phone, and other required fields
    }
    
    response = requests.post(
        f"{BASE_URL}/apply/{property_id}",
        json=incomplete_data
    )
    
    # The API might accept partial data for draft saving
    # or it might require all fields - check actual behavior
    print(f"  - Response status: {response.status_code}")
    if response.status_code == 422:
        print("✓ Validation correctly rejected incomplete data")
    else:
        print("! API accepted partial data (may be for draft functionality)")

def test_field_validation():
    """Test individual field validations"""
    print("\n=== Testing Field Validations ===")
    
    property_id = create_test_property()
    
    # Test invalid email
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = "invalid-email"
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    if response.status_code == 422:
        print("✓ Invalid email correctly rejected")
    else:
        print("! API accepted invalid email format")
    
    # Test invalid phone
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["phone"] = "123"
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    if response.status_code == 422:
        print("✓ Invalid phone correctly rejected")
    else:
        print("! API accepted invalid phone format")

def test_employment_history_structure():
    """Test employment history array structure"""
    print("\n=== Testing Employment History Structure ===")
    
    property_id = create_test_property()
    
    # Test with empty employment history
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["employment_history"] = []
    test_data["email"] = f"test.empty.history.{int(time.time())}@example.com"
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    print(f"  - Empty history: {response.status_code}")
    
    # Test with multiple entries
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = f"test.multiple.history.{int(time.time())}@example.com"
    test_data["employment_history"] = [
        {
            "employer_name": f"Employer {i}",
            "job_title": f"Position {i}",
            "start_date": "2020-01-01",
            "end_date": "2021-01-01",
            "is_current": False,
            "responsibilities": "Various duties",
            "reason_for_leaving": "Career growth",
            "supervisor_name": f"Supervisor {i}",
            "supervisor_phone": "(555) 111-2222",
            "may_contact": True
        }
        for i in range(5)
    ]
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    assert response.status_code == 200, f"Failed with multiple history entries: {response.text}"
    print("✓ Multiple employment history entries accepted")

def test_references_structure():
    """Test references array structure"""
    print("\n=== Testing References Structure ===")
    
    property_id = create_test_property()
    
    # Test with different numbers of references
    for num_refs in [0, 1, 3, 5]:
        test_data = COMPLETE_APPLICATION_DATA.copy()
        test_data["email"] = f"test.refs.{num_refs}.{int(time.time())}@example.com"
        test_data["references"] = [
            {
                "name": f"Reference {i}",
                "relationship": "Professional",
                "phone": "(555) 111-2222",
                "email": f"ref{i}@example.com",
                "years_known": str(i + 1)
            }
            for i in range(num_refs)
        ]
        
        response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
        print(f"  - {num_refs} references: {response.status_code}")

def test_skills_and_languages():
    """Test skills, certifications, and languages arrays"""
    print("\n=== Testing Skills and Languages Arrays ===")
    
    property_id = create_test_property()
    
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = f"test.skills.{int(time.time())}@example.com"
    
    # Test with many skills
    test_data["skills"] = [f"Skill {i}" for i in range(20)]
    test_data["certifications"] = [f"Cert {i}" for i in range(10)]
    test_data["languages"] = ["English", "Spanish", "French", "German", "Italian"]
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    assert response.status_code == 200, f"Failed with multiple skills: {response.text}"
    print("✓ Multiple skills, certifications, and languages accepted")

def test_consent_fields():
    """Test consent boolean fields"""
    print("\n=== Testing Consent Fields ===")
    
    property_id = create_test_property()
    
    # Test with all consent fields false
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = f"test.no.consent.{int(time.time())}@example.com"
    test_data["physical_requirements_acknowledged"] = False
    test_data["background_check_consent"] = False
    test_data["information_accuracy_certified"] = False
    test_data["at_will_employment_acknowledged"] = False
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    # Application might be accepted but marked as incomplete
    print(f"  - No consent given: {response.status_code}")
    
    # Test with all consent fields true
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = f"test.full.consent.{int(time.time())}@example.com"
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    assert response.status_code == 200
    print("✓ Full consent application accepted")

def test_voluntary_identification():
    """Test voluntary self-identification fields"""
    print("\n=== Testing Voluntary Self-Identification ===")
    
    property_id = create_test_property()
    
    # Test with no voluntary info
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = f"test.no.voluntary.{int(time.time())}@example.com"
    test_data["gender"] = ""
    test_data["ethnicity"] = ""
    test_data["veteran_status"] = ""
    test_data["disability_status"] = ""
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    assert response.status_code == 200, "Should accept application without voluntary info"
    print("✓ Application accepted without voluntary identification")

def test_edge_cases():
    """Test various edge cases"""
    print("\n=== Testing Edge Cases ===")
    
    property_id = create_test_property()
    
    # Test very long text fields
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = f"test.long.text.{int(time.time())}@example.com"
    test_data["additional_comments"] = "A" * 5000  # Very long comment
    test_data["employment_history"][0]["responsibilities"] = "B" * 2000
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    print(f"  - Very long text fields: {response.status_code}")
    
    # Test special characters
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = f"test.special.chars.{int(time.time())}@example.com"
    test_data["first_name"] = "José"
    test_data["last_name"] = "O'Brien-Smith"
    test_data["address"] = "123 Main St. #456 & Suite 789"
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    print(f"  - Special characters in names/address: {response.status_code}")
    
    # Test international phone format
    test_data = COMPLETE_APPLICATION_DATA.copy()
    test_data["email"] = f"test.intl.phone.{int(time.time())}@example.com"
    test_data["phone"] = "+1 (555) 123-4567"
    
    response = requests.post(f"{BASE_URL}/apply/{property_id}", json=test_data)
    print(f"  - International phone format: {response.status_code}")

async def test_concurrent_submissions():
    """Test concurrent application submissions"""
    print("\n=== Testing Concurrent Submissions ===")
    
    property_id = create_test_property()
    
    async def submit_application(session, index):
        test_data = COMPLETE_APPLICATION_DATA.copy()
        test_data["email"] = f"test.concurrent.{index}.{int(time.time())}@example.com"
        
        async with session.post(
            f"{BASE_URL}/apply/{property_id}",
            json=test_data
        ) as response:
            return response.status, await response.text()
    
    async with aiohttp.ClientSession() as session:
        tasks = [submit_application(session, i) for i in range(5)]
        results = await asyncio.gather(*tasks)
    
    successful = sum(1 for status, _ in results if status == 200)
    print(f"✓ Concurrent submissions: {successful}/5 successful")

def test_application_retrieval():
    """Test retrieving submitted applications"""
    print("\n=== Testing Application Retrieval ===")
    
    # Submit an application
    app_id, property_id = test_application_submission()
    
    # Try to retrieve it (if endpoint exists)
    response = requests.get(f"{BASE_URL}/applications/{app_id}")
    if response.status_code == 200:
        data = response.json()
        print("✓ Application retrieved successfully")
        print(f"  - Status: {data.get('status', 'N/A')}")
    else:
        print(f"! Application retrieval endpoint not available or restricted")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("BACKEND TESTS FOR JOB APPLICATION FORM V2")
    print("=" * 60)
    
    try:
        # Basic connectivity test
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("ERROR: Backend is not running or not accessible")
            return
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to backend at", BASE_URL)
        print("Make sure the backend is running with: poetry run python app/main_enhanced.py")
        return
    
    # Run tests
    test_property_info_endpoint()
    test_application_submission()
    test_duplicate_application_prevention()
    test_incomplete_application_validation()
    test_field_validation()
    test_employment_history_structure()
    test_references_structure()
    test_skills_and_languages()
    test_consent_fields()
    test_voluntary_identification()
    test_edge_cases()
    
    # Run async tests
    asyncio.run(test_concurrent_submissions())
    
    test_application_retrieval()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()