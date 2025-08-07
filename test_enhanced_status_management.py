#!/usr/bin/env python3
"""
Test script for enhanced application status management functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_enhanced_status_management():
    """Test the enhanced status management endpoints"""
    
    print("Testing Enhanced Application Status Management")
    print("=" * 50)
    
    # Test data
    test_application_ids = ["app_test_001"]  # Using the test application from initialization
    
    # Test 1: Bulk status update
    print("\n1. Testing bulk status update...")
    try:
        response = requests.post(
            f"{BASE_URL}/hr/applications/bulk-status-update",
            data={
                "application_ids": test_application_ids,
                "new_status": "talent_pool",
                "reason": "Test bulk status update",
                "notes": "Moving to talent pool for testing"
            },
            headers={"Authorization": "Bearer test_hr_token"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Results: {result['results']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Application history
    print("\n2. Testing application history...")
    try:
        response = requests.get(
            f"{BASE_URL}/hr/applications/{test_application_ids[0]}/history",
            headers={"Authorization": "Bearer test_hr_token"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Application ID: {result['application_id']}")
            print(f"Current Status: {result['current_status']}")
            print(f"History entries: {len(result['history'])}")
            for entry in result['history']:
                print(f"  - {entry['old_status']} → {entry['new_status']} by {entry['changed_by']} ({entry['reason']})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Bulk reactivate
    print("\n3. Testing bulk reactivate...")
    try:
        response = requests.post(
            f"{BASE_URL}/hr/applications/bulk-reactivate",
            data={
                "application_ids": test_application_ids
            },
            headers={"Authorization": "Bearer test_hr_token"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Results: {result['results']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Bulk talent pool notify
    print("\n4. Testing bulk talent pool notify...")
    try:
        # First move back to talent pool
        requests.post(
            f"{BASE_URL}/hr/applications/bulk-status-update",
            data={
                "application_ids": test_application_ids,
                "new_status": "talent_pool",
                "reason": "Test notification"
            },
            headers={"Authorization": "Bearer test_hr_token"}
        )
        
        response = requests.post(
            f"{BASE_URL}/hr/applications/bulk-talent-pool-notify",
            data={
                "application_ids": test_application_ids
            },
            headers={"Authorization": "Bearer test_hr_token"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Results: {result['results']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Enhanced Status Management Test Complete")

if __name__ == "__main__":
    test_enhanced_status_management()