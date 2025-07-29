#!/usr/bin/env python3
"""Test script for the three-phase workflow APIs"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Test credentials
HR_EMAIL = "hr@hotelonboarding.com"
HR_PASSWORD = "hr123456"
MANAGER_EMAIL = "manager@grandhotel.com"
MANAGER_PASSWORD = "manager123"

def get_auth_token(email, password):
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/login", data={
        "username": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["user"]["id"]
    else:
        print(f"Login failed for {email}: {response.text}")
        return None

def test_manager_review_apis():
    """Test manager review APIs"""
    print("\n=== Testing Manager Review APIs ===")
    
    # Get manager token
    manager_token = get_auth_token(MANAGER_EMAIL, MANAGER_PASSWORD)
    if not manager_token:
        print("Failed to authenticate as manager")
        return
    
    headers = {"Authorization": f"Bearer {manager_token}"}
    
    # Test session ID (you'll need to replace with actual session ID)
    session_id = "test-session-123"
    
    # 1. Get onboarding for review
    print("\n1. Testing GET /api/manager/onboarding/{session_id}/review")
    response = requests.get(
        f"{BASE_URL}/api/manager/onboarding/{session_id}/review",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # 2. Complete I-9 Section 2
    print("\n2. Testing POST /api/manager/onboarding/{session_id}/i9-section2")
    i9_data = {
        "form_data": {
            "document_title_list_a": "US Passport",
            "issuing_authority_list_a": "U.S. Department of State",
            "document_number_list_a": "123456789",
            "expiration_date_list_a": "2030-01-01"
        },
        "signature_data": {
            "signature": "base64_signature_data",
            "signed_at": datetime.utcnow().isoformat(),
            "ip_address": "127.0.0.1"
        }
    }
    response = requests.post(
        f"{BASE_URL}/api/manager/onboarding/{session_id}/i9-section2",
        headers=headers,
        json=i9_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 3. Approve onboarding
    print("\n3. Testing POST /api/manager/onboarding/{session_id}/approve")
    approval_data = {
        "signature_data": {
            "signature": "base64_manager_signature",
            "signed_at": datetime.utcnow().isoformat(),
            "ip_address": "127.0.0.1"
        },
        "notes": "All documents verified. Employee cleared for work."
    }
    response = requests.post(
        f"{BASE_URL}/api/manager/onboarding/{session_id}/approve",
        headers=headers,
        json=approval_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 4. Request changes
    print("\n4. Testing POST /api/manager/onboarding/{session_id}/request-changes")
    changes_data = {
        "requested_changes": [
            {"form": "personal_info", "reason": "Missing middle name"},
            {"form": "emergency_contacts", "reason": "Need secondary emergency contact"}
        ]
    }
    response = requests.post(
        f"{BASE_URL}/api/manager/onboarding/{session_id}/request-changes",
        headers=headers,
        json=changes_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

def test_hr_approval_apis():
    """Test HR approval APIs"""
    print("\n\n=== Testing HR Approval APIs ===")
    
    # Get HR token
    hr_token = get_auth_token(HR_EMAIL, HR_PASSWORD)
    if not hr_token:
        print("Failed to authenticate as HR")
        return
    
    headers = {"Authorization": f"Bearer {hr_token}"}
    
    # 1. Get pending HR approvals
    print("\n1. Testing GET /api/hr/onboarding/pending")
    response = requests.get(
        f"{BASE_URL}/api/hr/onboarding/pending",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    # Test session ID
    session_id = "test-session-123"
    
    # 2. Approve onboarding
    print("\n2. Testing POST /api/hr/onboarding/{session_id}/approve")
    approval_data = {
        "signature_data": {
            "signature": "base64_hr_signature",
            "signed_at": datetime.utcnow().isoformat(),
            "ip_address": "127.0.0.1"
        },
        "notes": "Final approval granted. Welcome to the team!"
    }
    response = requests.post(
        f"{BASE_URL}/api/hr/onboarding/{session_id}/approve",
        headers=headers,
        json=approval_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 3. Reject onboarding
    print("\n3. Testing POST /api/hr/onboarding/{session_id}/reject")
    rejection_data = {
        "rejection_reason": "Failed background check"
    }
    response = requests.post(
        f"{BASE_URL}/api/hr/onboarding/{session_id}/reject",
        headers=headers,
        json=rejection_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 4. Request changes
    print("\n4. Testing POST /api/hr/onboarding/{session_id}/request-changes")
    changes_data = {
        "requested_changes": [
            {"form": "w4_form", "reason": "Need to update withholding allowances"},
            {"form": "direct_deposit", "reason": "Bank account verification failed"}
        ],
        "request_from": "employee"
    }
    response = requests.post(
        f"{BASE_URL}/api/hr/onboarding/{session_id}/request-changes",
        headers=headers,
        json=changes_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 5. Request changes from manager
    print("\n5. Testing POST /api/hr/onboarding/{session_id}/request-changes (from manager)")
    changes_data = {
        "requested_changes": [
            {"form": "i9_section2", "reason": "Document expiration date is incorrect"}
        ],
        "request_from": "manager"
    }
    response = requests.post(
        f"{BASE_URL}/api/hr/onboarding/{session_id}/request-changes",
        headers=headers,
        json=changes_data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

def test_email_notification_helper():
    """Test email notification helper"""
    print("\n\n=== Testing Email Notification Helper ===")
    
    data = {
        "session_id": "test-session-123",
        "phase_completed": "employee"
    }
    response = requests.post(
        f"{BASE_URL}/api/internal/send-phase-completion-email",
        json=data
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    print("Testing Three-Phase Workflow APIs")
    print("=================================")
    
    print("\nNote: Make sure the backend is running on http://localhost:8000")
    print("Note: You'll need to replace 'test-session-123' with an actual session ID")
    
    try:
        # Test manager APIs
        test_manager_review_apis()
        
        # Test HR APIs
        test_hr_approval_apis()
        
        # Test email helper
        test_email_notification_helper()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the backend. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")