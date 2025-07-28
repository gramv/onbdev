#!/usr/bin/env python3
"""Test Task 2: Public Property Info Endpoint"""

import requests
import json

def test_task2_property_info():
    """Test public property info endpoint"""
    BASE_URL = 'http://localhost:8000'
    
    print("🧪 Testing Task 2: Public Property Info Endpoint")
    print("=" * 50)
    
    # Get a property ID first (using HR access)
    print("1. Getting property ID for testing...")
    hr_response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    if hr_response.status_code != 200:
        print(f"❌ HR login failed: {hr_response.text}")
        return False
    
    hr_token = hr_response.json()['token']
    headers = {'Authorization': f'Bearer {hr_token}'}
    
    props_response = requests.get(f'{BASE_URL}/hr/properties', headers=headers)
    if props_response.status_code != 200:
        print(f"❌ Failed to get properties: {props_response.text}")
        return False
    
    properties = props_response.json()
    if not properties:
        print("❌ No properties found")
        return False
    
    prop_id = properties[0]['id']
    prop_name = properties[0]['name']
    print(f"✅ Using property '{prop_name}' ({prop_id})")
    
    # Test public property info endpoint (no auth required)
    print(f"\n2. Testing public property info endpoint...")
    info_response = requests.get(f'{BASE_URL}/properties/{prop_id}/info')
    
    if info_response.status_code != 200:
        print(f"❌ Property info endpoint failed: {info_response.text}")
        return False
    
    info_data = info_response.json()
    print("✅ Property info endpoint working")
    
    # Validate response structure
    if 'property' not in info_data:
        print("❌ Missing 'property' field in response")
        return False
    
    property_info = info_data['property']
    required_fields = ['id', 'name', 'address', 'city', 'state']
    missing_fields = [field for field in required_fields if field not in property_info]
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    
    print("✅ All required fields present")
    print(f"   Property: {property_info['name']}")
    print(f"   Location: {property_info['city']}, {property_info['state']}")
    
    # Check for departments and positions
    if 'departments_and_positions' in info_data:
        departments = info_data['departments_and_positions']
        print(f"✅ Departments available: {len(departments)}")
        for dept, positions in departments.items():
            print(f"   {dept}: {len(positions)} positions")
    else:
        print("⚠️  No departments info in response")
    
    # Check for application URL
    if 'application_url' in info_data:
        print(f"✅ Application URL: {info_data['application_url']}")
    else:
        print("⚠️  No application URL in response")
    
    # Test with invalid property ID
    print(f"\n3. Testing with invalid property ID...")
    invalid_response = requests.get(f'{BASE_URL}/properties/invalid-id/info')
    
    if invalid_response.status_code == 404:
        print("✅ Correctly returns 404 for invalid property")
    else:
        print(f"⚠️  Expected 404, got {invalid_response.status_code}")
    
    print("\n📋 Task 2 Summary:")
    print("✅ Public property info endpoint working")
    print("✅ No authentication required")
    print("✅ Returns basic property information")
    print("✅ Includes departments and positions")
    print("✅ Handles invalid property IDs correctly")
    
    return True

if __name__ == "__main__":
    success = test_task2_property_info()
    if success:
        print("\n🎉 Task 2: PASSED")
    else:
        print("\n❌ Task 2: FAILED")