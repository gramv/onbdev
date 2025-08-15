#!/usr/bin/env python3
"""
Test what happens when rejecting a non-existent application
"""

import requests

BACKEND_URL = "http://localhost:8000"

def test_nonexistent_app():
    # Login as manager
    manager_login = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=manager_login)
    manager_auth = response.json()
    manager_token = manager_auth["token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    
    # Try to reject a non-existent application
    fake_app_id = "9aa3fcd8-3c53-43e4-88b8-556a97536071"
    
    print(f"🧪 Testing rejection of non-existent application: {fake_app_id}")
    
    rejection_data = {
        "rejection_reason": "Test rejection"
    }
    
    response = requests.post(f"{BACKEND_URL}/applications/{fake_app_id}/reject", 
                           data=rejection_data, headers=manager_headers)
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")

if __name__ == "__main__":
    test_nonexistent_app()