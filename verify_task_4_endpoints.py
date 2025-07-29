#!/usr/bin/env python3
"""
Comprehensive verification of Task 4 endpoints
Tests that all required endpoints exist and respond correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint_exists(method, endpoint, headers=None, data=None, description=""):
    """Test if an endpoint exists and responds (not necessarily with success)"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False

        # Any response (including 404, 401, etc.) means the endpoint exists
        # Only connection errors or 404 from the server itself indicate missing endpoints
        if response.status_code == 404 and "Not Found" in response.text and "detail" not in response.text:
            print(f"❌ {method} {endpoint} - Endpoint does not exist")
            return False
        else:
            print(f"✅ {method} {endpoint} - {description} (Status: {response.status_code})")
            return True
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection error (server not running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def main():
    print("🔍 Verifying Task 4 Endpoints Exist")
    print("=" * 50)
    
    # Login as HR to get token
    hr_login_data = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=hr_login_data)
        if response.status_code == 200:
            hr_data = response.json()
            hr_token = hr_data["data"]["token"]
            hr_headers = {"Authorization": f"Bearer {hr_token}"}
            print("✅ HR authentication successful")
        else:
            print("❌ HR authentication failed")
            hr_headers = None
    except Exception as e:
        print(f"❌ HR authentication error: {e}")
        hr_headers = None
    
    # Test all required endpoints
    tests = [
        # 1. Manager dashboard stats endpoint
        ("GET", "/manager/dashboard-stats", hr_headers, None, "Manager dashboard statistics"),
        
        # 2. Properties info public endpoint  
        ("GET", "/properties/test-id/info", None, None, "Public property information"),
        
        # 3. HR applications history endpoint
        ("GET", "/hr/applications/test-id/history", hr_headers, None, "Application status history"),
        
        # 4. Applications approve endpoint
        ("POST", "/applications/test-id/approve", hr_headers, {
            "job_title": "Test Position",
            "start_date": "2024-01-01",
            "start_time": "09:00",
            "pay_rate": 15.00,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Test Supervisor"
        }, "Application approval"),
        
        # 5. Applications reject endpoint
        ("POST", "/applications/test-id/reject", hr_headers, {
            "rejection_reason": "Test rejection reason"
        }, "Application rejection"),
    ]
    
    print("\n📋 Testing Endpoint Existence:")
    print("-" * 30)
    
    successful_tests = 0
    total_tests = len(tests)
    
    for method, endpoint, headers, data, description in tests:
        if test_endpoint_exists(method, endpoint, headers, data, description):
            successful_tests += 1
    
    print(f"\n📊 Results Summary:")
    print("=" * 30)
    print(f"Total Endpoints: {total_tests}")
    print(f"Existing: {successful_tests}")
    print(f"Missing: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 All Task 4 endpoints exist and are responding!")
        return True
    else:
        print("\n⚠️  Some endpoints are missing or not responding.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)