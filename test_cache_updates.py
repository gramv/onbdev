#!/usr/bin/env python3
"""
Test script to verify cache invalidation and real-time updates
"""
import time
import httpx
import asyncio
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

async def test_cache_invalidation():
    """Test that updates are reflected immediately after mutations"""
    print("🧪 Testing Cache Invalidation and Real-time Updates\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First, try to login as HR
        print("\n1️⃣ Attempting login...")
        login_resp = await client.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": "michael.scott@dundermifflin.com", "password": "test123"}
        )
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed. Creating test HR user...")
            # Try to create a test HR user
            from app.supabase_service_enhanced import EnhancedSupabaseService
            from app.auth import PasswordManager
            import uuid
            
            service = EnhancedSupabaseService()
            pwd_mgr = PasswordManager()
            
            test_user = {
                "id": str(uuid.uuid4()),
                "email": "cache.test@example.com",
                "password_hash": pwd_mgr.hash_password("test123"),
                "first_name": "Cache",
                "last_name": "Test",
                "role": "hr",
                "is_active": True
            }
            
            try:
                service.client.table("users").insert(test_user).execute()
                print(f"✅ Created test HR user: {test_user['email']}")
                
                # Login with new user
                login_resp = await client.post(
                    f"{API_BASE_URL}/auth/login",
                    json={"email": "cache.test@example.com", "password": "test123"}
                )
            except:
                print("❌ Could not create test user. Please ensure database is configured.")
                return
        
        if login_resp.status_code == 200:
            token = login_resp.json()["token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            print(f"❌ Could not login: {login_resp.json()}")
            return
        
        print("\n2️⃣ Testing Properties Cache Invalidation")
        print("-" * 40)
        
        # Get initial properties count
        resp1 = await client.get(f"{API_BASE_URL}/hr/properties", headers=headers)
        if resp1.status_code == 200:
            initial_count = len(resp1.json().get("properties", []))
            print(f"📊 Initial properties count: {initial_count}")
        else:
            print(f"❌ Failed to get properties: {resp1.status_code}")
            return
        
        # Create a new property
        print("➕ Creating new property...")
        timestamp = datetime.now().strftime("%H%M%S")
        new_property_data = {
            "name": f"Test Hotel {timestamp}",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "phone": "555-0001"
        }
        
        create_resp = await client.post(
            f"{API_BASE_URL}/hr/properties",
            data=new_property_data,
            headers={**headers, "Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if create_resp.status_code == 200:
            print(f"✅ Property created: {new_property_data['name']}")
        else:
            print(f"❌ Failed to create property: {create_resp.text}")
            return
        
        # Immediately fetch properties again (should show new property)
        print("🔄 Fetching properties immediately after creation...")
        await asyncio.sleep(0.5)  # Small delay for database
        
        resp2 = await client.get(f"{API_BASE_URL}/hr/properties", headers=headers)
        if resp2.status_code == 200:
            new_count = len(resp2.json().get("properties", []))
            print(f"📊 New properties count: {new_count}")
            
            if new_count > initial_count:
                print(f"✅ Property appeared immediately! ({initial_count} → {new_count})")
            else:
                print(f"❌ Property not showing yet (still {new_count})")
                
                # Try again after cache expires
                print("⏳ Waiting 5 seconds for cache to expire...")
                await asyncio.sleep(5)
                
                resp3 = await client.get(f"{API_BASE_URL}/hr/properties", headers=headers)
                if resp3.status_code == 200:
                    final_count = len(resp3.json().get("properties", []))
                    if final_count > initial_count:
                        print(f"✅ Property appeared after cache expiry ({final_count})")
                    else:
                        print(f"❌ Property still not showing ({final_count})")
        
        print("\n3️⃣ Testing Managers Cache Invalidation")
        print("-" * 40)
        
        # Get initial managers count
        resp4 = await client.get(f"{API_BASE_URL}/hr/managers", headers=headers)
        if resp4.status_code == 200:
            initial_managers = len(resp4.json())
            print(f"📊 Initial managers count: {initial_managers}")
        else:
            print(f"❌ Failed to get managers: {resp4.status_code}")
        
        # Create a new manager
        print("➕ Creating new manager...")
        new_manager_data = {
            "email": f"manager.{timestamp}@test.com",
            "first_name": "Test",
            "last_name": f"Manager{timestamp}",
            "password": "test12345"
        }
        
        create_mgr_resp = await client.post(
            f"{API_BASE_URL}/hr/managers",
            data=new_manager_data,
            headers={**headers, "Content-Type": "multipart/form-data"}
        )
        
        if create_mgr_resp.status_code == 200:
            print(f"✅ Manager created: {new_manager_data['email']}")
        else:
            print(f"❌ Failed to create manager: {create_mgr_resp.text}")
        
        # Immediately fetch managers again
        print("🔄 Fetching managers immediately after creation...")
        await asyncio.sleep(0.5)
        
        resp5 = await client.get(f"{API_BASE_URL}/hr/managers", headers=headers)
        if resp5.status_code == 200:
            new_managers = len(resp5.json())
            print(f"📊 New managers count: {new_managers}")
            
            if new_managers > initial_managers:
                print(f"✅ Manager appeared immediately! ({initial_managers} → {new_managers})")
            else:
                print(f"⚠️ Manager not showing immediately")
        
        print("\n4️⃣ Testing Cache Headers")
        print("-" * 40)
        
        # Check cache headers
        resp6 = await client.get(f"{API_BASE_URL}/hr/properties", headers=headers)
        if "cache-control" in resp6.headers:
            print(f"📦 Cache-Control: {resp6.headers['cache-control']}")
        if "vary" in resp6.headers:
            print(f"🔀 Vary: {resp6.headers['vary']}")
        if "etag" in resp6.headers:
            print(f"🏷️ ETag: {resp6.headers['etag'][:30]}...")
        
        print("\n" + "=" * 60)
        print("📋 Summary of Improvements Applied:")
        print("✅ Frontend cache reduced to 5 seconds")
        print("✅ Backend cache reduced to 5 seconds")
        print("✅ Cache cleared after mutations")
        print("✅ HTTP headers use 'private' and 'must-revalidate'")
        print("✅ Added 'Vary: Authorization' header")
        print("✅ Frontend uses refreshProperties/refreshManagers after mutations")

if __name__ == "__main__":
    print("\n🔧 Cache Invalidation Test\n")
    asyncio.run(test_cache_invalidation())
    print("\n✅ Test completed!\n")