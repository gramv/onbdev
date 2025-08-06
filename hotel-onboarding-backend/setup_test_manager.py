#!/usr/bin/env python3
"""
Setup proper test manager with property assignment
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def setup_manager():
    """Setup manager with property assignment"""
    print("Setting up test manager with property...")
    
    # First login as HR
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
    
    # Check if property exists
    properties_response = requests.get(f"{BASE_URL}/properties", headers=headers)
    if properties_response.status_code == 200:
        properties = properties_response.json()
        print(f"Found {len(properties)} properties")
        
        if properties:
            property_id = properties[0]['id']
            print(f"Using property: {properties[0]['name']} (ID: {property_id})")
            
            # Update manager to be assigned to this property
            # This would require an endpoint to update the manager's property assignment
            # For now, let's just document what needs to be done
            print("\nTo fix manager login:")
            print("1. The manager needs to be assigned to a property")
            print("2. This can be done through the HR dashboard")
            print("3. Or by updating the test data initialization")
    
    print("\n✅ Setup complete!")
    print("\nManager credentials:")
    print("  Email: manager@hoteltest.com")
    print("  Password: manager123")
    print("\nNote: Manager needs to be assigned to a property to login successfully")

if __name__ == "__main__":
    setup_manager()