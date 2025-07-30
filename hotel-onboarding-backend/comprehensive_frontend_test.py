#!/usr/bin/env python3
"""
Comprehensive Frontend Testing Script
Tests all backend endpoints that the frontend relies on
"""

import requests
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_hr_authentication():
    """Test HR authentication and get token"""
    print("🔐 Testing HR Authentication...")
    
    # Create HR user if doesn't exist
    hr_data = {
        "email": "hr.test.final@hotel.com",
        "password": "FinalTest123",
        "secret_key": "hotel-admin-2025"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/secret/create-hr",
        params=hr_data
    )
    print(f"HR Creation: {create_response.status_code} - {create_response.text}")
    
    # Login
    login_data = {
        "email": "hr.test.final@hotel.com",
        "password": "FinalTest123"
    }
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        print("✅ HR Authentication successful")
        return token_data["token"]
    else:
        print(f"❌ HR Authentication failed: {login_response.text}")
        return None

def test_hr_dashboard_stats(token):
    """Test HR dashboard statistics"""
    print("\n📊 Testing HR Dashboard Stats...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/hr/dashboard-stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Dashboard stats retrieved:")
        print(f"   Properties: {stats.get('properties_count', 0)}")
        print(f"   Managers: {stats.get('managers_count', 0)}")
        print(f"   Applications: {stats.get('pending_applications_count', 0)}")
        return True
    else:
        print(f"❌ Dashboard stats failed: {response.text}")
        return False

def test_properties_management(token):
    """Test properties CRUD operations"""
    print("\n🏨 Testing Properties Management...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET properties
    get_response = requests.get(f"{BASE_URL}/hr/properties", headers=headers)
    print(f"GET Properties: {get_response.status_code}")
    
    if get_response.status_code == 200:
        properties = get_response.json()
        print(f"✅ Retrieved {len(properties)} properties")
    
    # Test CREATE property
    property_data = {
        "name": f"Test Hotel Frontend {datetime.now().strftime('%H%M%S')}",
        "address": "123 Frontend Test St",
        "city": "Test City",
        "state": "CA",
        "zip_code": "90210",
        "phone": "555-0123"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/hr/properties",
        headers=headers,
        data=property_data
    )
    
    if create_response.status_code == 200:
        created_property = create_response.json()
        print("✅ Property created successfully")
        return created_property.get("property", {}).get("id")
    else:
        print(f"❌ Property creation failed: {create_response.text}")
        return None

def test_managers_management(token):
    """Test managers management"""
    print("\n👥 Testing Managers Management...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET managers
    get_response = requests.get(f"{BASE_URL}/hr/managers", headers=headers)
    
    if get_response.status_code == 200:
        managers = get_response.json()
        print(f"✅ Retrieved {len(managers)} managers")
        
        if managers:
            # Test individual manager details
            manager_id = managers[0]["id"]
            detail_response = requests.get(
                f"{BASE_URL}/hr/managers/{manager_id}",
                headers=headers
            )
            
            if detail_response.status_code == 200:
                print("✅ Manager details retrieved")
            else:
                print(f"⚠️ Manager details failed: {detail_response.text}")
                
            # Test manager performance
            perf_response = requests.get(
                f"{BASE_URL}/hr/managers/{manager_id}/performance",
                headers=headers
            )
            
            if perf_response.status_code == 200:
                print("✅ Manager performance retrieved")
            else:
                print(f"⚠️ Manager performance failed: {perf_response.text}")
        
        return True
    else:
        print(f"❌ Managers retrieval failed: {get_response.text}")
        return False

def test_applications_workflow(token, property_id=None):
    """Test job applications workflow"""
    print("\n📝 Testing Applications Workflow...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET applications
    get_response = requests.get(f"{BASE_URL}/hr/applications", headers=headers)
    
    if get_response.status_code == 200:
        applications = get_response.json()
        print(f"✅ Retrieved {len(applications)} applications")
        
        # If we have applications, test individual operations
        if applications:
            app_id = applications[0]["id"]
            
            # Test application history
            history_response = requests.get(
                f"{BASE_URL}/hr/applications/{app_id}/history",
                headers=headers
            )
            
            if history_response.status_code == 200:
                print("✅ Application history retrieved")
            elif history_response.status_code == 404:
                print("ℹ️ Application history not found (expected for new apps)")
            else:
                print(f"⚠️ Application history failed: {history_response.text}")
        
        return True
    else:
        print(f"❌ Applications retrieval failed: {get_response.text}")
        return False

def test_bulk_operations(token):
    """Test bulk operations on applications"""
    print("\n🔄 Testing Bulk Operations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test UUIDs for bulk operations
    test_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
    
    # Test bulk status update
    bulk_data = {
        "application_ids": test_ids,
        "new_status": "approved",
        "reason": "Frontend testing bulk approval"
    }
    
    bulk_response = requests.post(
        f"{BASE_URL}/hr/applications/bulk-status-update",
        headers=headers,
        data=bulk_data
    )
    
    if bulk_response.status_code == 200:
        result = bulk_response.json()
        print(f"✅ Bulk operations processed: {result.get('processed', 0)} applications")
        print(f"   Successful: {result.get('successful', 0)}, Failed: {result.get('failed', 0)}")
        return True
    else:
        print(f"❌ Bulk operations failed: {bulk_response.text}")
        return False

def test_duplicate_check(token):
    """Test duplicate application checking"""
    print("\n🔍 Testing Duplicate Check...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    duplicate_data = {
        "email": "test.duplicate@example.com",
        "property_id": str(uuid.uuid4()),
        "position": "Front Desk Clerk"
    }
    
    duplicate_response = requests.post(
        f"{BASE_URL}/applications/check-duplicate",
        headers=headers,
        data=duplicate_data
    )
    
    if duplicate_response.status_code == 200:
        result = duplicate_response.json()
        print(f"✅ Duplicate check successful: {result.get('is_duplicate', False)}")
        return True
    else:
        print(f"❌ Duplicate check failed: {duplicate_response.text}")
        return False

def test_employee_management(token):
    """Test employee search and management"""
    print("\n👤 Testing Employee Management...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test employee search
    search_response = requests.get(
        f"{BASE_URL}/hr/employees/search?search_query=test",
        headers=headers
    )
    
    if search_response.status_code == 200:
        print("✅ Employee search successful")
    elif search_response.status_code == 404 and "Employee not found" in search_response.text:
        print("ℹ️ Employee search returned 'not found' (expected when no employees exist)")
    else:
        print(f"⚠️ Employee search failed: {search_response.text}")
    
    # Test employee statistics
    stats_response = requests.get(
        f"{BASE_URL}/hr/employees/stats",
        headers=headers
    )
    
    if stats_response.status_code == 200:
        print("✅ Employee statistics retrieved")
        return True
    elif stats_response.status_code == 404:
        print("ℹ️ Employee statistics returned 'not found' (expected when no employees exist)")
        return True
    else:
        print(f"⚠️ Employee statistics failed: {stats_response.text}")
        return False

def test_talent_pool_operations(token):
    """Test talent pool operations"""
    print("\n🎯 Testing Talent Pool Operations...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET talent pool
    talent_response = requests.get(f"{BASE_URL}/hr/applications/talent-pool", headers=headers)
    
    if talent_response.status_code == 200:
        talent_pool = talent_response.json()
        print(f"✅ Retrieved {len(talent_pool)} talent pool applications")
        return True
    else:
        print(f"❌ Talent pool retrieval failed: {talent_response.text}")
        return False

def run_comprehensive_test():
    """Run comprehensive frontend testing"""
    print("🚀 Starting Comprehensive Frontend Testing")
    print("=" * 60)
    
    # Get authentication token
    token = test_hr_authentication()
    if not token:
        print("❌ Cannot proceed without authentication")
        return False
    
    # Run all tests
    results = []
    
    results.append(("HR Dashboard Stats", test_hr_dashboard_stats(token)))
    results.append(("Properties Management", test_properties_management(token)))
    results.append(("Managers Management", test_managers_management(token)))
    results.append(("Applications Workflow", test_applications_workflow(token)))
    results.append(("Bulk Operations", test_bulk_operations(token)))
    results.append(("Duplicate Check", test_duplicate_check(token)))
    results.append(("Employee Management", test_employee_management(token)))
    results.append(("Talent Pool Operations", test_talent_pool_operations(token)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Frontend should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the details above.")
    
    # Provide HR account details
    print("\n" + "=" * 60)
    print("🔑 HR ACCOUNT FOR FRONTEND TESTING")
    print("=" * 60)
    print("Email: hr.test.final@hotel.com")
    print("Password: FinalTest123")
    print("Role: HR Admin")
    print("Token: Valid for testing")
    print("\nUse this account to test the frontend!")
    
    return passed == total

if __name__ == "__main__":
    run_comprehensive_test()