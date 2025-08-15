#!/usr/bin/env python3
"""
Simple test to diagnose job application submission issues
"""
import requests
import json
from datetime import datetime, date, timedelta
import uuid

BASE_URL = "http://localhost:8000"
property_id = "a99239dd-ebde-4c69-b862-ecba9e878798"

def test_simple_application():
    """Test with the simple application structure that works"""
    
    print("🧪 Testing Simple Job Application")
    print("=" * 50)
    
    unique_id = uuid.uuid4().hex[:8]
    
    simple_application = {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"john.doe.{unique_id}@testhotel.com",
        "phone": "555-123-4567",
        "address": "123 Test Street",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes",
        "previous_employer": "Test Hotel",
        "reason_for_leaving": "Career advancement",
        "additional_comments": "Excited to join your team!"
    }
    
    print(f"Property ID: {property_id}")
    print(f"Applicant: {simple_application['first_name']} {simple_application['last_name']}")
    print(f"Email: {simple_application['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/apply/{property_id}",
            json=simple_application,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"Application ID: {result.get('application_id')}")
            return result.get('application_id')
        else:
            print(f"❌ FAILED!")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

if __name__ == "__main__":
    test_simple_application()