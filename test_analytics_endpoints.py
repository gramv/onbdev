#!/usr/bin/env python3
"""
Test script for analytics endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def get_hr_token():
    """Get HR authentication token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "hr@hoteltest.com",
        "password": "password123"
    })
    
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"❌ HR login failed: {response.text}")
        return None

def test_analytics_endpoints():
    """Test all analytics endpoints"""
    token = get_hr_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test analytics overview
    print("\n🧪 Testing analytics overview...")
    response = requests.get(f"{BASE_URL}/hr/analytics/overview", headers=headers)
    print(f"GET /hr/analytics/overview: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Overview data: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test property performance
    print("\n🧪 Testing property performance...")
    response = requests.get(f"{BASE_URL}/hr/analytics/property-performance", headers=headers)
    print(f"GET /hr/analytics/property-performance: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Property performance data: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test employee trends
    print("\n🧪 Testing employee trends...")
    response = requests.get(f"{BASE_URL}/hr/analytics/employee-trends", headers=headers)
    print(f"GET /hr/analytics/employee-trends: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Employee trends data: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test export
    print("\n🧪 Testing data export...")
    response = requests.get(f"{BASE_URL}/hr/analytics/export?format=json", headers=headers)
    print(f"GET /hr/analytics/export: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Export successful (data length: {len(response.text)} chars)")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    test_analytics_endpoints()