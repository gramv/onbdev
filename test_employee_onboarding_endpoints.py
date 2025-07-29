#!/usr/bin/env python3
"""
Test script for employee onboarding API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_verify_token():
    """Test token verification endpoint"""
    print("\n=== Testing Token Verification ===")
    
    # Test with invalid token
    response = requests.get(f"{BASE_URL}/onboard/verify", params={"token": "invalid-token"})
    print(f"Invalid token response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Note: To test with valid token, we need an actual onboarding session
    print("\nNote: Valid token test requires an active onboarding session")

def test_update_progress():
    """Test progress update endpoint"""
    print("\n=== Testing Progress Update ===")
    
    # Test with form data
    form_data = {
        "session_id": "test-session-id",
        "step_id": "personal_info",
        "form_data": json.dumps({
            "ssn": "123-45-6789",
            "date_of_birth": "1990-01-01",
            "address": "123 Main St"
        }),
        "token": "test-token"
    }
    
    response = requests.post(f"{BASE_URL}/onboard/update-progress", data=form_data)
    print(f"Update progress response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_start_onboarding():
    """Test start onboarding endpoint"""
    print("\n=== Testing Start Onboarding ===")
    
    # First, we need to authenticate as HR
    auth_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "hr@hotel.com",
        "password": "hr123"
    })
    
    if auth_response.status_code == 200:
        token = auth_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Start onboarding for a test application
        onboarding_data = {
            "application_id": "test-app-id",
            "property_id": "test-property-id",
            "manager_id": "test-manager-id",
            "expires_hours": 72
        }
        
        response = requests.post(
            f"{BASE_URL}/api/onboarding/start",
            json=onboarding_data,
            headers=headers
        )
        print(f"Start onboarding response: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Failed to authenticate as HR")

def test_welcome_data():
    """Test get welcome data endpoint"""
    print("\n=== Testing Get Welcome Data ===")
    
    # Test with invalid token
    response = requests.get(f"{BASE_URL}/api/onboarding/welcome/invalid-token")
    print(f"Welcome data response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_submit_step():
    """Test submit step endpoint"""
    print("\n=== Testing Submit Step ===")
    
    step_data = {
        "form_data": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        },
        "signature_data": {
            "signature": "base64-signature-data",
            "signed_at": "2025-01-29T10:00:00Z"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/onboarding/test-session/step/personal_info",
        json=step_data,
        params={"token": "test-token"}
    )
    print(f"Submit step response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_get_progress():
    """Test get progress endpoint"""
    print("\n=== Testing Get Progress ===")
    
    response = requests.get(
        f"{BASE_URL}/api/onboarding/test-session/progress",
        params={"token": "test-token"}
    )
    print(f"Get progress response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_complete_onboarding():
    """Test complete onboarding endpoint"""
    print("\n=== Testing Complete Onboarding ===")
    
    response = requests.post(
        f"{BASE_URL}/api/onboarding/test-session/complete",
        params={"token": "test-token"}
    )
    print(f"Complete onboarding response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def main():
    """Run all tests"""
    print("Testing Employee Onboarding API Endpoints")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("Server is not running or not healthy")
            return
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server at", BASE_URL)
        print("Please ensure the server is running: python app/main_enhanced.py")
        return
    
    # Run tests
    test_verify_token()
    test_update_progress()
    test_start_onboarding()
    test_welcome_data()
    test_submit_step()
    test_get_progress()
    test_complete_onboarding()
    
    print("\n" + "=" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    main()