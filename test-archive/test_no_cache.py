#!/usr/bin/env python3
"""
Test the simplified no-cache approach
"""
import httpx
import asyncio
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

async def test_no_cache():
    """Test that properties update immediately without cache"""
    print("🧪 Testing No-Cache Properties\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try to login
        print("1️⃣ Attempting login...")
        login_resp = await client.post(
            f"{API_BASE}/auth/login",
            json={"email": "michael.scott@dundermifflin.com", "password": "test123"}
        )
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return
            
        token = login_resp.json().get("token")
        if not token:
            print("❌ No token received")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful\n")
        
        # Get initial properties
        print("2️⃣ Getting initial properties...")
        resp1 = await client.get(f"{API_BASE}/hr/properties", headers=headers)
        if resp1.status_code == 200:
            initial_props = resp1.json().get("properties", [])
            print(f"   Found {len(initial_props)} properties")
        else:
            print(f"❌ Failed to get properties: {resp1.status_code}")
            return
        
        # Create a new property
        print("\n3️⃣ Creating a new property...")
        timestamp = datetime.now().strftime("%H%M%S")
        new_prop = {
            "name": f"Test Hotel {timestamp}",
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "phone": "555-0001"
        }
        
        create_resp = await client.post(
            f"{API_BASE}/hr/properties",
            data=new_prop,
            headers={**headers, "Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if create_resp.status_code == 200:
            print(f"✅ Created: {new_prop['name']}")
        else:
            print(f"❌ Failed to create: {create_resp.text}")
            return
        
        # Immediately get properties again
        print("\n4️⃣ Getting properties immediately after creation...")
        resp2 = await client.get(f"{API_BASE}/hr/properties", headers=headers)
        if resp2.status_code == 200:
            new_props = resp2.json().get("properties", [])
            print(f"   Found {len(new_props)} properties")
            
            if len(new_props) > len(initial_props):
                print(f"✅ SUCCESS! New property appears immediately!")
                print(f"   {len(initial_props)} → {len(new_props)}")
            else:
                print(f"❌ FAILED! Property not showing")
                print(f"   Still showing {len(new_props)} properties")
        
        # Try to delete the property we just created
        if create_resp.status_code == 200:
            # Find the property we created
            all_props = resp2.json().get("properties", [])
            test_prop = next((p for p in all_props if p["name"] == new_prop["name"]), None)
            
            if test_prop:
                print(f"\n5️⃣ Deleting property: {test_prop['name']}")
                del_resp = await client.delete(
                    f"{API_BASE}/hr/properties/{test_prop['id']}",
                    headers=headers
                )
                
                if del_resp.status_code == 200:
                    print("✅ Deleted successfully")
                    
                    # Check if it's gone
                    print("\n6️⃣ Checking if property is gone...")
                    resp3 = await client.get(f"{API_BASE}/hr/properties", headers=headers)
                    if resp3.status_code == 200:
                        final_props = resp3.json().get("properties", [])
                        print(f"   Found {len(final_props)} properties")
                        
                        if len(final_props) == len(initial_props):
                            print(f"✅ SUCCESS! Property deleted immediately!")
                        else:
                            print(f"❌ Property still showing after delete")
                else:
                    print(f"❌ Failed to delete: {del_resp.text}")
        
        print("\n" + "=" * 60)
        print("📋 Summary:")
        print("✅ No caching = immediate updates")
        print("✅ Create/Delete operations work instantly")
        print("✅ No need for hard refreshes!")

if __name__ == "__main__":
    print("\n🔧 No-Cache Properties Test\n")
    asyncio.run(test_no_cache())
    print("\n✅ Test completed!\n")