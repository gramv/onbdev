#!/usr/bin/env python3
"""
Task 1: Test Manager Property Access Control Issues
Comprehensive test to identify and validate fixes for manager property access control
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime, timezone

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend', 'app'))

def test_manager_authentication_issues():
    """Test manager authentication and property access validation"""
    print("🧪 Testing Manager Authentication Issues...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Manager login and token validation
    print("\n1. Testing Manager Login...")
    login_data = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            if login_result.get("success"):
                token = login_result["data"]["token"]
                print(f"   ✅ Manager login successful")
                
                # Test 2: Manager applications endpoint with property access
                print("\n2. Testing Manager Applications Endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                
                apps_response = requests.get(f"{base_url}/manager/applications", headers=headers)
                print(f"   Applications Status: {apps_response.status_code}")
                
                if apps_response.status_code == 200:
                    apps_result = apps_response.json()
                    print(f"   ✅ Applications retrieved: {len(apps_result.get('data', []))}")
                else:
                    print(f"   ❌ Applications failed: {apps_response.text}")
                
                # Test 3: Manager property endpoint
                print("\n3. Testing Manager Property Endpoint...")
                prop_response = requests.get(f"{base_url}/manager/property", headers=headers)
                print(f"   Property Status: {prop_response.status_code}")
                
                if prop_response.status_code == 200:
                    prop_result = prop_response.json()
                    print(f"   ✅ Property retrieved: {prop_result.get('data', {}).get('name', 'Unknown')}")
                else:
                    print(f"   ❌ Property failed: {prop_response.text}")
                
                # Test 4: Manager dashboard stats
                print("\n4. Testing Manager Dashboard Stats...")
                stats_response = requests.get(f"{base_url}/manager/dashboard-stats", headers=headers)
                print(f"   Stats Status: {stats_response.status_code}")
                
                if stats_response.status_code == 200:
                    stats_result = stats_response.json()
                    print(f"   ✅ Stats retrieved successfully")
                else:
                    print(f"   ❌ Stats failed: {stats_response.text}")
                
                return True
            else:
                print(f"   ❌ Login failed: {login_result}")
                return False
        else:
            print(f"   ❌ Login request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Authentication test failed: {e}")
        return False

def test_property_access_validation():
    """Test property access validation for unauthorized access attempts"""
    print("\n🧪 Testing Property Access Validation...")
    
    base_url = "http://localhost:8000"
    
    # First login as manager
    login_data = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code != 200:
            print("   ❌ Could not login manager for access validation test")
            return False
        
        login_result = response.json()
        if not login_result.get("success"):
            print("   ❌ Manager login failed for access validation test")
            return False
        
        token = login_result["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test unauthorized property access (try to access a property the manager doesn't own)
        print("\n1. Testing Unauthorized Property Access...")
        
        # Try to access HR endpoints (should fail)
        hr_response = requests.get(f"{base_url}/hr/properties", headers=headers)
        print(f"   HR Properties Status: {hr_response.status_code}")
        
        if hr_response.status_code == 403:
            print("   ✅ HR access properly blocked for manager")
        else:
            print(f"   ❌ HR access not properly blocked: {hr_response.status_code}")
        
        # Test property filtering in applications
        print("\n2. Testing Property Filtering in Applications...")
        apps_response = requests.get(f"{base_url}/manager/applications", headers=headers)
        
        if apps_response.status_code == 200:
            apps_result = apps_response.json()
            applications = apps_result.get('data', [])
            
            # Check if all applications belong to manager's property
            manager_property_ids = set()
            for app in applications:
                manager_property_ids.add(app.get('property_id'))
            
            print(f"   Manager has access to properties: {manager_property_ids}")
            
            if len(manager_property_ids) <= 1:  # Manager should only see their own property
                print("   ✅ Property filtering working correctly")
            else:
                print(f"   ❌ Property filtering issue: Manager sees {len(manager_property_ids)} properties")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Property access validation test failed: {e}")
        return False

def test_error_handling():
    """Test error handling for property access control"""
    print("\n🧪 Testing Error Handling...")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Invalid token
    print("\n1. Testing Invalid Token Handling...")
    headers = {"Authorization": "Bearer invalid_token"}
    
    try:
        response = requests.get(f"{base_url}/manager/applications", headers=headers)
        print(f"   Invalid Token Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Invalid token properly rejected")
        else:
            print(f"   ❌ Invalid token not properly handled: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Invalid token test failed: {e}")
    
    # Test 2: Missing token
    print("\n2. Testing Missing Token Handling...")
    try:
        response = requests.get(f"{base_url}/manager/applications")
        print(f"   Missing Token Status: {response.status_code}")
        
        if response.status_code == 403:  # FastAPI HTTPBearer returns 403 for missing token
            print("   ✅ Missing token properly rejected")
        else:
            print(f"   ❌ Missing token not properly handled: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Missing token test failed: {e}")

def run_comprehensive_test():
    """Run all manager property access control tests"""
    print("🚀 Starting Task 1: Manager Property Access Control Tests")
    print("=" * 60)
    
    # Test authentication issues
    auth_success = test_manager_authentication_issues()
    
    # Test property access validation
    access_success = test_property_access_validation()
    
    # Test error handling
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Authentication Tests: {'✅ PASS' if auth_success else '❌ FAIL'}")
    print(f"   Access Validation Tests: {'✅ PASS' if access_success else '❌ FAIL'}")
    
    if auth_success and access_success:
        print("\n🎉 All critical tests passed! Manager property access control is working.")
        return True
    else:
        print("\n⚠️ Some tests failed. Manager property access control needs fixes.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)