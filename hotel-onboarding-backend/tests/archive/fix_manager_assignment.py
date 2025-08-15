#!/usr/bin/env python3
"""
Fix manager assignment to property using API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def fix_manager_assignment():
    """Assign the test manager to the test property"""
    print("Fixing manager assignment to property...")
    
    # First login as HR
    print("\n1. Logging in as HR...")
    hr_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "hr@hoteltest.com",
        "password": "admin123"
    })
    
    if hr_response.status_code != 200:
        print("❌ Failed to login as HR")
        return
    
    hr_data = hr_response.json()
    hr_token = hr_data['data']['token']
    headers = {"Authorization": f"Bearer {hr_token}"}
    print("✅ HR login successful")
    
    # Get properties
    print("\n2. Getting properties...")
    properties_response = requests.get(f"{BASE_URL}/hr/properties", headers=headers)
    if properties_response.status_code == 200:
        response_data = properties_response.json()
        # Check if properties are wrapped in data key
        if 'data' in response_data:
            properties = response_data['data']
        else:
            properties = response_data
        
        print(f"✅ Found {len(properties)} properties")
        
        if properties and len(properties) > 0:
            property_id = properties[0]['id']
            property_name = properties[0]['name']
            print(f"   Using property: {property_name} (ID: {property_id})")
            
            # Get managers
            print("\n3. Getting managers...")
            managers_response = requests.get(f"{BASE_URL}/hr/managers", headers=headers)
            if managers_response.status_code == 200:
                managers = managers_response.json()
                print(f"✅ Found {len(managers)} managers")
                
                # Find the test manager
                test_manager = None
                for manager in managers:
                    if manager['email'] == 'manager@hoteltest.com':
                        test_manager = manager
                        break
                
                if test_manager:
                    print(f"   Found test manager: {test_manager['first_name']} {test_manager['last_name']}")
                    manager_id = test_manager['id']
                    
                    # Assign manager to property
                    print(f"\n4. Assigning manager to property...")
                    assign_response = requests.post(
                        f"{BASE_URL}/hr/properties/{property_id}/managers",
                        headers=headers,
                        data={"manager_id": manager_id}
                    )
                    
                    if assign_response.status_code == 200:
                        print(f"✅ Manager successfully assigned to {property_name}!")
                        print("\nYou can now login as manager:")
                        print("  Email: manager@hoteltest.com")
                        print("  Password: manager123")
                    else:
                        print(f"❌ Failed to assign manager: {assign_response.status_code}")
                        print(f"   Response: {assign_response.text}")
                else:
                    print("❌ Test manager not found")
            else:
                print(f"❌ Failed to get managers: {managers_response.status_code}")
        else:
            print("❌ No properties found")
    else:
        print(f"❌ Failed to get properties: {properties_response.status_code}")

if __name__ == "__main__":
    fix_manager_assignment()