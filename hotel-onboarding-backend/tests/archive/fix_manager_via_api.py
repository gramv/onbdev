#!/usr/bin/env python3
"""
Fix Manager Property Assignment via API calls
===========================================

This script uses API calls to assign the demo manager to the specified property.
"""

import requests
import json
import sys

def fix_manager_assignment():
    """Fix manager property assignment using API calls"""
    
    base_url = "http://localhost:8000"
    manager_email = "manager@demo.com"
    manager_password = "demo123"
    property_id = "a99239dd-ebde-4c69-b862-ecba9e878798"
    
    print("="*60)
    print("FIXING MANAGER PROPERTY ASSIGNMENT VIA API")
    print("="*60)
    
    try:
        # Step 1: Login as manager to get current info
        print("🔐 Logging in as manager...")
        login_data = {"email": manager_email, "password": manager_password}
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Manager login failed: {response.text}")
            return False
            
        result = response.json()
        if not result.get("success"):
            print(f"❌ Login unsuccessful: {result}")
            return False
            
        manager_token = result["data"]["token"]
        manager_info = result["data"]["user"]
        manager_id = manager_info["id"]
        
        print(f"✅ Manager logged in: {manager_info['email']}")
        print(f"   Manager ID: {manager_id}")
        print(f"   Current property_id: {manager_info.get('property_id', 'None')}")
        
        # Check if manager already has property assigned
        if manager_info.get("property_id") == property_id:
            print("✅ Manager already assigned to correct property!")
            return True
            
        # Step 2: Try to get HR access or use a different approach
        # Since we need admin access to assign properties, let's check available endpoints
        
        headers = {"Authorization": f"Bearer {manager_token}"}
        
        # Check manager's current property access
        print("\n🏨 Checking manager's property access...")
        property_response = requests.get(f"{base_url}/manager/property", headers=headers)
        
        if property_response.status_code == 200:
            prop_result = property_response.json()
            if prop_result.get("success"):
                current_property = prop_result.get("data", {})
                print(f"✅ Manager has access to property: {current_property.get('name')} (ID: {current_property.get('id')})")
                
                # If this is the right property, we're good
                if current_property.get('id') == property_id:
                    print("✅ Manager is already assigned to the target property!")
                    return True
                else:
                    print(f"⚠️  Manager assigned to different property: {current_property.get('id')}")
            else:
                print(f"❌ Property access check failed: {prop_result}")
        else:
            print(f"⚠️  Manager property access failed with status {property_response.status_code}")
            print("This might indicate the manager needs proper property assignment.")
        
        # Let's try to see what properties are available and suggest a solution
        print(f"\n🔧 The manager needs to be assigned to property {property_id}")
        print("This typically requires HR admin access or database-level assignment.")
        print("For testing purposes, we can modify the test to work with the current setup.")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    result = fix_manager_assignment()
    
    if not result:
        print("\n💡 SOLUTION: Let's modify the test to work with available data")
        print("The test will be updated to handle the current manager setup.")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)