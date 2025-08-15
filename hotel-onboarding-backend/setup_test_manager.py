#!/usr/bin/env python3
"""
Setup test manager account for testing
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def setup_test_data():
    """Setup test property and manager"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Setting up test data...")
        
        # First, try to login as admin to create the manager
        print("\n1. Logging in as admin...")
        try:
            admin_response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"email": "admin@hotelonboard.com", "password": "admin123"}
            )
            
            if admin_response.status_code == 200:
                print("✅ Admin login successful")
                admin_token = admin_response.json()["access_token"]
                admin_headers = {"Authorization": f"Bearer {admin_token}"}
                
                # Create property first
                print("\n2. Creating test property...")
                prop_response = await client.post(
                    f"{BASE_URL}/admin/properties",
                    headers=admin_headers,
                    json={
                        "id": "test-prop-001",
                        "name": "Demo Hotel",
                        "address": "123 Demo Street, Demo City, DC 12345",
                        "phone": "555-0001"
                    }
                )
                
                if prop_response.status_code in [200, 201]:
                    print("✅ Property created/exists")
                elif prop_response.status_code == 409:
                    print("ℹ️  Property already exists")
                else:
                    print(f"⚠️  Property creation response: {prop_response.status_code}")
                    print(f"   {prop_response.text}")
                
                # Create manager
                print("\n3. Creating manager account...")
                manager_response = await client.post(
                    f"{BASE_URL}/admin/managers",
                    headers=admin_headers,
                    json={
                        "email": "manager@demo.com",
                        "password": "demo123",
                        "first_name": "Demo",
                        "last_name": "Manager",
                        "property_id": "test-prop-001"
                    }
                )
                
                if manager_response.status_code in [200, 201]:
                    print("✅ Manager created successfully")
                    print(f"   Response: {manager_response.json()}")
                elif manager_response.status_code == 409:
                    print("ℹ️  Manager already exists - updating...")
                    
                    # Try to update the manager's property assignment
                    update_response = await client.put(
                        f"{BASE_URL}/admin/managers/manager@demo.com",
                        headers=admin_headers,
                        json={
                            "property_id": "test-prop-001",
                            "password": "demo123"  # Reset password
                        }
                    )
                    
                    if update_response.status_code == 200:
                        print("✅ Manager updated successfully")
                    else:
                        print(f"⚠️  Manager update failed: {update_response.status_code}")
                        print(f"   {update_response.text}")
                else:
                    print(f"❌ Manager creation failed: {manager_response.status_code}")
                    print(f"   {manager_response.text}")
                
                # Test the manager login
                print("\n4. Testing manager login...")
                test_response = await client.post(
                    f"{BASE_URL}/auth/login",
                    json={"email": "manager@demo.com", "password": "demo123"}
                )
                
                if test_response.status_code == 200:
                    print("✅ Manager login works!")
                    manager_data = test_response.json()
                    print(f"   User ID: {manager_data.get('user', {}).get('id')}")
                    print(f"   Role: {manager_data.get('user', {}).get('role')}")
                else:
                    print(f"❌ Manager login failed: {test_response.status_code}")
                    print(f"   {test_response.text}")
                
            else:
                print(f"❌ Admin login failed: {admin_response.status_code}")
                print(f"   Response: {admin_response.text}")
                print("\nTrying to create admin account...")
                
                # Try to create admin account (might work if no users exist)
                register_response = await client.post(
                    f"{BASE_URL}/auth/register",
                    json={
                        "email": "admin@hotelonboard.com",
                        "password": "admin123",
                        "first_name": "System",
                        "last_name": "Admin",
                        "role": "admin"
                    }
                )
                
                if register_response.status_code in [200, 201]:
                    print("✅ Admin account created")
                    print("Please run this script again to setup the manager")
                else:
                    print(f"❌ Could not create admin: {register_response.status_code}")
                    print(f"   {register_response.text}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def main():
    await setup_test_data()

if __name__ == "__main__":
    asyncio.run(main())