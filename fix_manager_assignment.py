#!/usr/bin/env python3
"""
Fix manager assignment to property for testing
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    # Login as HR
    hr_login_data = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=hr_login_data)
    if response.status_code != 200:
        print(f"❌ HR login failed: {response.text}")
        return
    
    hr_data = response.json()
    hr_token = hr_data["data"]["token"]
    headers = {"Authorization": f"Bearer {hr_token}"}
    
    # Get properties
    response = requests.get(f"{BASE_URL}/hr/properties", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get properties: {response.text}")
        return
    
    properties_data = response.json()
    properties = properties_data.get("data", [])
    
    if not properties:
        print("❌ No properties found, creating one...")
        # Create a test property
        property_data = {
            "name": "Grand Plaza Hotel",
            "address": "123 Main Street",
            "city": "Downtown",
            "state": "CA",
            "zip_code": "90210",
            "phone": "(555) 123-4567"
        }
        
        response = requests.post(f"{BASE_URL}/hr/properties", headers=headers, data=property_data)
        print(f"Property creation response: {response.status_code} - {response.text}")
        if response.status_code != 200:
            print(f"❌ Failed to create property: {response.text}")
            return
        
        print("✅ Property created successfully")
        
        # Get properties again
        response = requests.get(f"{BASE_URL}/hr/properties", headers=headers)
        print(f"Get properties response: {response.status_code} - {response.text}")
        if response.status_code != 200:
            print(f"❌ Failed to get properties after creation: {response.text}")
            return
        
        properties_data = response.json()
        properties = properties_data.get("data", [])
        print(f"Properties found: {len(properties)}")
    
    if not properties:
        print("❌ Still no properties found")
        return
    
    property_id = properties[0]["id"]
    print(f"✅ Found property: {property_id}")
    
    # Assign manager to property
    assign_data = {"manager_id": "mgr_test_001"}
    response = requests.post(f"{BASE_URL}/hr/properties/{property_id}/managers", 
                           headers=headers, data=assign_data)
    
    if response.status_code == 200:
        print("✅ Manager assigned to property successfully")
    else:
        print(f"❌ Failed to assign manager: {response.text}")

if __name__ == "__main__":
    main()