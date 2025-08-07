#!/usr/bin/env python3
"""
Simple test for analytics endpoints using existing backend setup
"""

import sys
import os
sys.path.append('hotel-onboarding-backend')

from hotel-onboarding-backend.app.main_enhanced import app, database, initialize_test_data
from fastapi.testclient import TestClient

# Initialize test data
initialize_test_data()

# Create test client
client = TestClient(app)

def test_analytics():
    """Test analytics endpoints"""
    
    # Login as HR user
    login_response = client.post("/auth/login", json={
        "email": "hr@hoteltest.com",
        "password": "password123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ HR login successful")
    
    # Test analytics overview
    print("\n🧪 Testing analytics overview...")
    response = client.get("/hr/analytics/overview", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Overview data keys: {list(data.keys())}")
        print(f"   Total applications: {data['overview']['totalApplications']}")
        print(f"   Total properties: {data['overview']['totalProperties']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test property performance
    print("\n🧪 Testing property performance...")
    response = client.get("/hr/analytics/property-performance", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Property performance data: {len(data['propertyPerformance'])} properties")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test employee trends
    print("\n🧪 Testing employee trends...")
    response = client.get("/hr/analytics/employee-trends", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Employee trends data: {len(data['monthlyTrends'])} months")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test export
    print("\n🧪 Testing data export...")
    response = client.get("/hr/analytics/export?format=json", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Export successful")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    test_analytics()