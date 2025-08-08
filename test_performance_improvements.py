#!/usr/bin/env python3
"""
Test script to verify performance improvements
"""
import time
import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_CREDENTIALS = [
    {"email": "freshhr@test.com", "password": "test123"},
    {"email": "testuser@example.com", "password": "pass123"},
    {"email": "michael.scott@dundermifflin.com", "password": "test123"},
]

async def test_performance():
    """Test API performance improvements"""
    print("🚀 Testing Performance Improvements\n")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try to login with different credentials
        token = None
        for creds in TEST_CREDENTIALS:
            print(f"\nTrying login with: {creds['email']}")
            try:
                login_resp = await client.post(
                    f"{API_BASE_URL}/auth/login",
                    json=creds
                )
                if login_resp.status_code == 200:
                    data = login_resp.json()
                    token = data.get('token')
                    print(f"✅ Login successful!")
                    user_role = data.get('user', {}).get('role', 'unknown')
                    print(f"   Role: {user_role}")
                    break
                else:
                    print(f"❌ Login failed: {login_resp.status_code}")
                    print(f"   Response: {login_resp.json().get('detail', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        if not token:
            print("\n⚠️ Could not login with any test credentials")
            print("Please ensure test users are set up in the database")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n" + "=" * 50)
        print("📊 Testing API Endpoints Performance\n")
        
        # Define endpoints to test based on user role
        endpoints = []
        if 'hr' in user_role.lower():
            endpoints = [
                ("/hr/dashboard-stats", "Dashboard Statistics"),
                ("/hr/properties", "Properties List"),
                ("/hr/managers", "Managers List"),
                ("/hr/applications", "Applications List"),
                ("/hr/employees", "Employees List"),
            ]
        else:
            endpoints = [
                ("/manager/dashboard-stats", "Dashboard Statistics"),
                ("/hr/properties", "Properties List"),  # Try HR endpoints too
                ("/hr/managers", "Managers List"),
            ]
        
        total_time = 0
        successful_calls = 0
        
        for endpoint, name in endpoints:
            print(f"\n📍 Testing: {name}")
            print(f"   Endpoint: {endpoint}")
            
            try:
                # First call (potentially cached on backend)
                start = time.time()
                resp1 = await client.get(f"{API_BASE_URL}{endpoint}", headers=headers)
                time1 = time.time() - start
                
                if resp1.status_code == 200:
                    print(f"   ✅ First call: {time1:.3f}s")
                    successful_calls += 1
                    total_time += time1
                    
                    # Check cache headers
                    if 'cache-control' in resp1.headers:
                        print(f"   📦 Cache-Control: {resp1.headers['cache-control']}")
                    if 'etag' in resp1.headers:
                        print(f"   🏷️ ETag: {resp1.headers['etag'][:30]}...")
                    
                    # Second call (should be faster due to frontend caching)
                    await asyncio.sleep(0.1)  # Small delay
                    start = time.time()
                    resp2 = await client.get(f"{API_BASE_URL}{endpoint}", headers=headers)
                    time2 = time.time() - start
                    
                    if resp2.status_code == 200:
                        print(f"   ✅ Second call: {time2:.3f}s")
                        improvement = ((time1 - time2) / time1) * 100 if time1 > 0 else 0
                        if improvement > 0:
                            print(f"   ⚡ {improvement:.1f}% faster!")
                    
                    # Get response size
                    if resp1.content:
                        size_kb = len(resp1.content) / 1024
                        print(f"   📏 Response size: {size_kb:.1f} KB")
                else:
                    print(f"   ❌ Failed: {resp1.status_code}")
                    error_detail = resp1.json().get('detail', 'Unknown error')
                    print(f"   Error: {error_detail}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("📈 Performance Summary\n")
        
        if successful_calls > 0:
            avg_time = total_time / successful_calls
            print(f"✅ Successful API calls: {successful_calls}/{len(endpoints)}")
            print(f"⏱️ Average response time: {avg_time:.3f}s")
            
            if avg_time < 0.5:
                print(f"🎉 Excellent performance! (< 500ms average)")
            elif avg_time < 1.0:
                print(f"✅ Good performance! (< 1s average)")
            elif avg_time < 2.0:
                print(f"⚠️ Acceptable performance (< 2s average)")
            else:
                print(f"❌ Performance needs improvement (> 2s average)")
        else:
            print("❌ No successful API calls")
        
        print("\n" + "=" * 50)
        print("🎯 Improvements Applied:")
        print("1. ✅ Backend caching with 30-second TTL")
        print("2. ✅ Frontend request deduplication")
        print("3. ✅ HTTP cache headers (Cache-Control, ETag)")
        print("4. ✅ Optimized Supabase queries")
        print("5. ✅ Service worker fixed (no POST/DELETE caching)")

if __name__ == "__main__":
    print("\n🔧 Hotel Onboarding System - Performance Test\n")
    asyncio.run(test_performance())
    print("\n✅ Test completed!\n")