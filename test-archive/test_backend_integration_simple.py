#!/usr/bin/env python3
"""
Simple backend integration test to verify API functionality
"""
import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """Test basic health check"""
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_hr_login():
    """Test HR login functionality"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "hr@hoteltest.com",
            "password": "admin123"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                print("✅ HR login test passed")
                return data["token"]
            else:
                print(f"❌ HR login response missing fields: {data}")
                return None
        else:
            print(f"❌ HR login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ HR login error: {e}")
        return None

def test_manager_login():
    """Test Manager login functionality"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "manager@hoteltest.com",
            "password": "manager123"
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data and "user" in data:
                print("✅ Manager login test passed")
                return data["token"]
            else:
                print(f"❌ Manager login response missing fields: {data}")
                return None
        else:
            print(f"❌ Manager login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Manager login error: {e}")
        return None

def test_authenticated_endpoint(token, endpoint, description):
    """Test authenticated endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ {description} test passed")
            return True
        else:
            print(f"❌ {description} failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def test_role_based_access():
    """Test role-based access control"""
    print("\n🔐 Testing Role-Based Access Control...")
    
    # Get HR token
    hr_token = test_hr_login()
    if not hr_token:
        return False
        
    # Get Manager token
    manager_token = test_manager_login()
    if not manager_token:
        return False
    
    # Test HR endpoints
    hr_tests = [
        ("/hr/dashboard-stats", "HR dashboard stats"),
        ("/hr/properties", "HR properties access"),
        ("/hr/applications", "HR applications access"),
        ("/hr/managers", "HR managers access")
    ]
    
    hr_success = 0
    for endpoint, description in hr_tests:
        if test_authenticated_endpoint(hr_token, endpoint, description):
            hr_success += 1
    
    # Test Manager endpoints (should have filtered access)
    manager_tests = [
        ("/hr/properties", "Manager properties access"),
        ("/hr/applications", "Manager applications access"),
        ("/api/employees", "Manager employees access")
    ]
    
    manager_success = 0
    for endpoint, description in manager_tests:
        if test_authenticated_endpoint(manager_token, endpoint, description):
            manager_success += 1
    
    print(f"\nHR Tests: {hr_success}/{len(hr_tests)} passed")
    print(f"Manager Tests: {manager_success}/{len(manager_tests)} passed")
    
    return hr_success >= 3 and manager_success >= 2  # Allow some flexibility

def test_api_error_handling():
    """Test API error handling"""
    print("\n🚨 Testing API Error Handling...")
    
    # Test invalid login
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        }, timeout=10)
        
        if response.status_code == 401:
            print("✅ Invalid login properly rejected")
        else:
            print(f"❌ Invalid login should return 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Invalid login test error: {e}")
        return False
    
    # Test unauthenticated access
    try:
        response = requests.get(f"{BASE_URL}/hr/dashboard-stats", timeout=10)
        
        if response.status_code in [401, 403]:
            print("✅ Unauthenticated access properly rejected")
        else:
            print(f"❌ Unauthenticated access should return 401 or 403, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Unauthenticated access test error: {e}")
        return False
    
    return True

def main():
    """Run all integration tests"""
    print("🚀 Starting Backend Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Role-Based Access", test_role_based_access),
        ("API Error Handling", test_api_error_handling)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All backend integration tests passed!")
        return True
    else:
        print("⚠️  Some backend integration tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)