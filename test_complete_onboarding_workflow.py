#!/usr/bin/env python3
"""
Complete onboarding workflow test demonstrating the full employee onboarding process
"""
import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"

def create_test_application():
    """Create a test job application"""
    print("\n1. Creating job application...")
    
    application_data = {
        "position": "Front Desk Agent",
        "department": "Front Office",
        "property_id": "550e8400-e29b-41d4-a716-446655440001",
        "start_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "employment_type": "full_time",
        "first_name": "Test",
        "last_name": "Employee",
        "email": "test.employee@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Test Street",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "can_work_in_us": True,
        "needs_sponsorship": False,
        "has_reliable_transportation": True,
        "can_work_weekends": True,
        "can_work_holidays": True,
        "desired_hours": 40,
        "desired_pay": "$15-20/hour",
        "questions_to_employer": "What are the growth opportunities?"
    }
    
    response = requests.post(f"{BASE_URL}/api/apply", json=application_data)
    if response.status_code == 200:
        app_id = response.json()["application_id"]
        print(f"✓ Application created: {app_id}")
        return app_id
    else:
        print(f"✗ Failed to create application: {response.status_code}")
        print(response.json())
        return None

def approve_application(app_id):
    """Approve the application as manager"""
    print("\n2. Approving application as manager...")
    
    # Login as manager
    auth_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "manager@hotel.com",
        "password": "manager123"
    })
    
    if auth_response.status_code != 200:
        print("✗ Failed to login as manager")
        return False
    
    token = auth_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Approve application
    approval_data = {
        "hourly_rate": 18.50,
        "schedule_notes": "Monday-Friday, 8am-4pm",
        "manager_notes": "Great candidate, approved for immediate hire"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/applications/{app_id}/approve",
        json=approval_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print("✓ Application approved")
        return True
    else:
        print(f"✗ Failed to approve application: {response.status_code}")
        print(response.json())
        return False

def start_onboarding_session(app_id):
    """Start onboarding session as HR"""
    print("\n3. Starting onboarding session as HR...")
    
    # Login as HR
    auth_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "hr@hotel.com",
        "password": "hr123"
    })
    
    if auth_response.status_code != 200:
        print("✗ Failed to login as HR")
        return None, None
    
    token = auth_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Start onboarding
    onboarding_data = {
        "application_id": app_id,
        "property_id": "550e8400-e29b-41d4-a716-446655440001",
        "manager_id": "550e8400-e29b-41d4-a716-446655440011",
        "expires_hours": 72
    }
    
    response = requests.post(
        f"{BASE_URL}/api/onboarding/start",
        json=onboarding_data,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print(f"✓ Onboarding session started: {data['session_id']}")
        print(f"  Token: {data['token']}")
        print(f"  URL: {data['onboarding_url']}")
        return data['session_id'], data['token']
    else:
        print(f"✗ Failed to start onboarding: {response.status_code}")
        print(response.json())
        return None, None

def verify_onboarding_token(token):
    """Verify the onboarding token"""
    print("\n4. Verifying onboarding token...")
    
    response = requests.get(f"{BASE_URL}/onboard/verify", params={"token": token})
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✓ Token verified successfully")
        print(f"  Employee: {data['employee']['first_name']} {data['employee']['last_name']}")
        print(f"  Position: {data['employee']['position']}")
        print(f"  Property: {data['property']['name'] if data['property'] else 'N/A'}")
        return True
    else:
        print(f"✗ Token verification failed: {response.status_code}")
        return False

def get_welcome_data(token):
    """Get welcome page data"""
    print("\n5. Getting welcome page data...")
    
    response = requests.get(f"{BASE_URL}/api/onboarding/welcome/{token}")
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✓ Welcome data retrieved")
        print(f"  Current step: {data['session']['current_step']}")
        print(f"  Phase: {data['session']['phase']}")
        print(f"  Total steps: {data['session']['total_steps']}")
        return True
    else:
        print(f"✗ Failed to get welcome data: {response.status_code}")
        return False

def submit_personal_info(session_id, token):
    """Submit personal information step"""
    print("\n6. Submitting personal information...")
    
    step_data = {
        "form_data": {
            "ssn": "123-45-6789",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "marital_status": "single",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "(555) 987-6543",
            "emergency_contact_relationship": "Spouse"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/onboarding/{session_id}/step/personal_info",
        json=step_data,
        params={"token": token}
    )
    
    if response.status_code == 200:
        print("✓ Personal information submitted")
        return True
    else:
        print(f"✗ Failed to submit personal info: {response.status_code}")
        print(response.json())
        return False

def update_progress_form_data(session_id, token):
    """Update progress using the form endpoint"""
    print("\n7. Updating progress with form data...")
    
    form_data = {
        "session_id": session_id,
        "step_id": "emergency_contacts",
        "form_data": json.dumps({
            "primary_contact": {
                "name": "Jane Doe",
                "relationship": "Spouse",
                "phone": "(555) 111-2222",
                "email": "jane.doe@example.com"
            },
            "secondary_contact": {
                "name": "John Smith",
                "relationship": "Friend",
                "phone": "(555) 333-4444"
            }
        }),
        "token": token
    }
    
    response = requests.post(f"{BASE_URL}/onboard/update-progress", data=form_data)
    
    if response.status_code == 200:
        print("✓ Progress updated with emergency contacts")
        return True
    else:
        print(f"✗ Failed to update progress: {response.status_code}")
        print(response.json())
        return False

def get_current_progress(session_id, token):
    """Get current onboarding progress"""
    print("\n8. Getting current progress...")
    
    response = requests.get(
        f"{BASE_URL}/api/onboarding/{session_id}/progress",
        params={"token": token}
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        print("✓ Progress retrieved")
        print(f"  Status: {data['status']}")
        print(f"  Phase: {data['phase']}")
        print(f"  Current step: {data['current_step']}")
        print(f"  Progress: {data['progress_percentage']}%")
        print(f"  Completed steps: {len(data['completed_steps'])}/{data['total_steps']}")
        return True
    else:
        print(f"✗ Failed to get progress: {response.status_code}")
        return False

def main():
    """Run complete onboarding workflow test"""
    print("=" * 60)
    print("COMPLETE EMPLOYEE ONBOARDING WORKFLOW TEST")
    print("=" * 60)
    
    # Check server health
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Server is not healthy")
            return
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server at", BASE_URL)
        print("Please ensure the server is running: python app/main_enhanced.py")
        return
    
    # Run workflow
    app_id = create_test_application()
    if not app_id:
        return
    
    if not approve_application(app_id):
        return
    
    session_id, token = start_onboarding_session(app_id)
    if not session_id or not token:
        return
    
    # Give email time to send
    print("\nWaiting for email to be sent...")
    time.sleep(2)
    
    if not verify_onboarding_token(token):
        return
    
    if not get_welcome_data(token):
        return
    
    if not submit_personal_info(session_id, token):
        return
    
    if not update_progress_form_data(session_id, token):
        return
    
    if not get_current_progress(session_id, token):
        return
    
    print("\n" + "=" * 60)
    print("✓ WORKFLOW TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nThe employee onboarding endpoints are working correctly.")
    print("The employee would continue through all remaining steps:")
    print("- I-9 Section 1")
    print("- W-4 Form")
    print("- Direct Deposit")
    print("- Health Insurance")
    print("- Company Policies")
    print("- And more...")
    print("\nOnce complete, the manager would review and approve.")

if __name__ == "__main__":
    main()