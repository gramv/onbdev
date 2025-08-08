#!/usr/bin/env python3
"""
Fix manager assignment for notification workflow test
"""

import requests
import json

def assign_manager_to_property():
    """Assign the test manager to a property"""
    
    # Login as HR
    hr_response = requests.post('http://127.0.0.1:8000/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    if hr_response.status_code != 200:
        print(f"❌ HR login failed: {hr_response.text}")
        return False
    
    hr_token = hr_response.json()['data']['token']
    print("✅ HR logged in successfully")
    
    # Get all properties
    props_response = requests.get('http://127.0.0.1:8000/hr/properties', 
                                 headers={'Authorization': f'Bearer {hr_token}'})
    
    if props_response.status_code != 200:
        print(f"❌ Failed to get properties: {props_response.text}")
        return False
    
    properties = props_response.json()['data']
    if not properties:
        print("❌ No properties found")
        return False
    
    prop_id = properties[0]['id']
    print(f"✅ Using property: {properties[0]['name']} ({prop_id})")
    
    # Get manager users
    users_response = requests.get('http://127.0.0.1:8000/hr/users?role=manager', 
                                headers={'Authorization': f'Bearer {hr_token}'})
    
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.text}")
        return False
    
    users_data = users_response.json()
    if isinstance(users_data, dict) and 'data' in users_data:
        users = users_data['data']
    else:
        users = users_data
    manager_users = [u for u in users if u['email'] == 'manager@hoteltest.com']
    
    if not manager_users:
        print("❌ Manager user not found")
        return False
    
    manager_id = manager_users[0]['id']
    print(f"✅ Found manager: {manager_id}")
    
    # Assign manager to property
    assign_response = requests.post(
        f'http://127.0.0.1:8000/hr/properties/{prop_id}/managers',
        data={'manager_id': manager_id},
        headers={'Authorization': f'Bearer {hr_token}'}
    )
    
    if assign_response.status_code == 200:
        print("✅ Manager successfully assigned to property")
        return True
    else:
        print(f"❌ Assignment failed: {assign_response.text}")
        return False

if __name__ == "__main__":
    success = assign_manager_to_property()
    if success:
        print("\n🎉 Manager assignment completed! Ready to run notification test.")
    else:
        print("\n❌ Manager assignment failed.")