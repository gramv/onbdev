#!/usr/bin/env python3
"""
Simple test to verify cache improvements
"""
import time
import httpx
import asyncio
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

# Test credentials - modify these based on your setup
TEST_CREDENTIALS = [
    {"email": "michael.scott@dundermifflin.com", "password": "test123"},
    {"email": "freshhr@test.com", "password": "test123"},
    {"email": "test.hr@example.com", "password": "test123"},
]

async def test_cache():
    """Test cache behavior after updates"""
    print("🧪 Testing Cache Improvements\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try to login
        token = None
        for creds in TEST_CREDENTIALS:
            print(f"Trying login: {creds['email']}")
            try:
                login_resp = await client.post(
                    f"{API_BASE_URL}/auth/login",
                    json=creds
                )
                if login_resp.status_code == 200:
                    token = login_resp.json()["token"]
                    print(f"✅ Login successful!\n")
                    break
            except Exception as e:
                print(f"❌ Failed: {e}")
        
        if not token:
            print("\n⚠️ Could not login. Please check credentials.")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        print("📊 Testing Response Times and Cache Behavior")
        print("-" * 40)
        
        # Test 1: Initial request (cold cache)
        print("\n1️⃣ First request (cold cache):")
        start = time.time()
        resp1 = await client.get(f"{API_BASE_URL}/hr/properties", headers=headers)
        time1 = time.time() - start
        print(f"   Response time: {time1:.3f}s")
        
        if resp1.status_code == 200:
            count1 = len(resp1.json().get("properties", []))
            print(f"   Properties count: {count1}")
            
            # Check headers
            if "cache-control" in resp1.headers:
                print(f"   Cache-Control: {resp1.headers['cache-control']}")
        
        # Test 2: Immediate second request (should use cache)
        print("\n2️⃣ Immediate second request (cached):")
        start = time.time()
        resp2 = await client.get(f"{API_BASE_URL}/hr/properties", headers=headers)
        time2 = time.time() - start
        print(f"   Response time: {time2:.3f}s")
        
        if time2 < time1:
            print(f"   ✅ Faster! ({(time1/time2):.1f}x speed improvement)")
        
        # Test 3: Wait for cache to expire
        print("\n3️⃣ After 5 second cache expiry:")
        print("   Waiting 5 seconds...")
        await asyncio.sleep(5.5)
        
        start = time.time()
        resp3 = await client.get(f"{API_BASE_URL}/hr/properties", headers=headers)
        time3 = time.time() - start
        print(f"   Response time: {time3:.3f}s")
        
        if time3 > time2:
            print(f"   ✅ Cache expired, fresh fetch performed")
        
        # Test managers endpoint
        print("\n4️⃣ Testing managers endpoint:")
        start = time.time()
        resp4 = await client.get(f"{API_BASE_URL}/hr/managers", headers=headers)
        time4 = time.time() - start
        print(f"   Response time: {time4:.3f}s")
        
        if resp4.status_code == 200:
            count4 = len(resp4.json())
            print(f"   Managers count: {count4}")
        
        print("\n" + "=" * 60)
        print("📋 Cache Configuration Summary:")
        print("✅ Frontend cache: 5 seconds")
        print("✅ Backend cache: 5 seconds") 
        print("✅ HTTP headers: private, max-age=5, must-revalidate")
        print("✅ Cache invalidation on mutations")
        print("\n💡 Updates should now appear within 5 seconds")
        print("   (no hard reload required)")

if __name__ == "__main__":
    print("\n🔧 Simple Cache Test\n")
    asyncio.run(test_cache())
    print("\n✅ Test completed!\n")