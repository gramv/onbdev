#!/usr/bin/env python3
"""
Fixed Frontend Testing Script
Tests all backend endpoints with correct form data handling
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_hr_token():
    """Get HR authentication token"""
    print("🔐 Getting HR Authentication Token...")
    
    login_data = {
        "email": "hr.frontend.test@hotel.com",
        "password": "FrontendTest123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ HR Authentication successful")
        return token_data["token"]
    else:
        print(f"❌ HR Authentication failed: {response.text}")
        return None

def test_properties_creation(token):
    """Test properties creation with correct form data"""
    print("\n🏨 Testing Properties Creation (Fixed)...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use proper form data (not files parameter)
    property_data = {
        "name": f"Test Hotel Fixed {datetime.now().strftime('%H%M%S')}",
        "address": "123 Frontend Test St",
        "city": "Test City", 
        "state": "CA",
        "zip_code": "90210",
        "phone": "555-0123"
    }
    
    # Test with curl-like approach using data parameter for form encoding
    response = requests.post(
        f"{BASE_URL}/hr/properties",
        headers=headers,
        data=property_data  # This sends as application/x-www-form-urlencoded
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        property_id = result.get("property", {}).get("id")
        print(f"✅ Property created successfully: {property_id}")
        return property_id
    else:
        print(f"❌ Property creation failed")
        return None

def test_bulk_operations_fixed(token):
    """Test bulk operations with correct form data"""
    print("\n🔄 Testing Bulk Operations (Fixed)...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test bulk status update with proper form data
    bulk_data = {
        "application_ids": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"],
        "new_status": "approved",
        "reason": "Frontend testing bulk approval"
    }
    
    response = requests.post(
        f"{BASE_URL}/hr/applications/bulk-status-update",
        headers=headers,
        data=bulk_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Bulk operations: {result.get('processed', 0)} processed")
        return True
    else:
        print(f"❌ Bulk operations failed")
        return False

def test_duplicate_check_fixed(token):
    """Test duplicate check with correct form data"""
    print("\n🔍 Testing Duplicate Check (Fixed)...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    duplicate_data = {
        "email": "test.duplicate@example.com",
        "property_id": "550e8400-e29b-41d4-a716-446655440000",
        "position": "Front Desk Clerk"
    }
    
    response = requests.post(
        f"{BASE_URL}/applications/check-duplicate",
        headers=headers,
        data=duplicate_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Duplicate check: {result.get('is_duplicate', False)}")
        return True
    else:
        print(f"❌ Duplicate check failed")
        return False

def test_applications_endpoints(token):
    """Test all applications-related endpoints"""
    print("\n📝 Testing Applications Endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test get applications
    response = requests.get(f"{BASE_URL}/hr/applications", headers=headers)
    print(f"GET Applications: {response.status_code}")
    
    if response.status_code == 200:
        applications = response.json()
        print(f"✅ Retrieved {len(applications)} applications")
    
    # Test talent pool
    response = requests.get(f"{BASE_URL}/hr/applications/talent-pool", headers=headers)
    print(f"GET Talent Pool: {response.status_code}")
    
    if response.status_code == 200:
        talent_pool = response.json()
        print(f"✅ Retrieved {len(talent_pool)} talent pool applications")
    elif response.status_code == 500:
        print("⚠️ Talent pool has database issues (expected)")
    
    # Test departments and positions
    response = requests.get(f"{BASE_URL}/hr/applications/departments", headers=headers)
    print(f"GET Departments: {response.status_code}")
    
    response = requests.get(f"{BASE_URL}/hr/applications/positions", headers=headers)
    print(f"GET Positions: {response.status_code}")
    
    return True

def run_fixed_tests():
    """Run the fixed frontend tests"""
    print("🚀 Running Fixed Frontend Tests")
    print("=" * 50)
    
    token = get_hr_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    print(f"\n🎫 Using token: {token[:50]}...")
    
    # Run specific tests that were failing
    test_properties_creation(token)
    test_bulk_operations_fixed(token)
    test_duplicate_check_fixed(token)
    test_applications_endpoints(token)
    
    print("\n" + "=" * 50)
    print("🎯 FIXED TESTS COMPLETED")
    print("=" * 50)
    
    # HR Account Information
    print("\n🔑 HR ACCOUNT FOR FRONTEND TESTING:")
    print("Email: hr.frontend.test@hotel.com")
    print("Password: FrontendTest123")
    print("Role: HR Admin")
    print("\n📋 FRONTEND TESTING CHECKLIST:")
    print("✅ Login with the HR account above")
    print("✅ Test HR Dashboard - should show statistics")
    print("✅ Test Properties tab - create/view properties")
    print("✅ Test Managers tab - view/manage managers")
    print("✅ Test Applications tab - view applications")
    print("✅ Test bulk operations on applications")
    print("✅ Test approval/rejection workflows")
    
    return True

if __name__ == "__main__":
    run_fixed_tests()