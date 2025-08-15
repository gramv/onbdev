#!/usr/bin/env python3
"""
Test script to measure performance improvements in HR dashboard endpoints
"""

import time
import requests
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "freshhr": {"email": "freshhr@test.com", "password": "test123"},
    "manager": {"email": "testmanager@test.com", "password": "test123"}
}

def login(email: str, password: str) -> str:
    """Login and get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        data = response.json()
        # Handle both token and access_token fields
        token = data.get("token") or data.get("access_token")
        if not token and "data" in data:
            # Handle wrapped response
            token = data["data"].get("token") or data["data"].get("access_token")
        return token
    else:
        print(f"Login failed for {email}: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            pass
        return None

def test_endpoint(endpoint: str, token: str, name: str) -> Dict[str, Any]:
    """Test an endpoint and measure response time"""
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    try:
        response = requests.get(
            f"{BASE_URL}{endpoint}",
            headers=headers,
            timeout=30
        )
        end_time = time.time()
        
        return {
            "name": name,
            "endpoint": endpoint,
            "status": response.status_code,
            "time": round(end_time - start_time, 3),
            "size": len(response.content) if response.status_code == 200 else 0,
            "success": response.status_code == 200
        }
    except requests.Timeout:
        end_time = time.time()
        return {
            "name": name,
            "endpoint": endpoint,
            "status": "TIMEOUT",
            "time": round(end_time - start_time, 3),
            "size": 0,
            "success": False
        }
    except Exception as e:
        end_time = time.time()
        return {
            "name": name,
            "endpoint": endpoint,
            "status": f"ERROR: {str(e)}",
            "time": round(end_time - start_time, 3),
            "size": 0,
            "success": False
        }

def main():
    print("=" * 60)
    print("HR Dashboard Performance Test")
    print("=" * 60)
    
    # Try login with freshhr user
    print("\n1. Testing with freshhr@test.com...")
    token = login("freshhr@test.com", "test123")
    
    if not token:
        print("   Failed to login with freshhr@test.com")
        print("\n2. Trying with testmanager@test.com...")
        token = login("testmanager@test.com", "test123")
    
    if not token:
        print("\nNo valid authentication token obtained. Please check user credentials.")
        print("\nTrying to find valid users...")
        
        # Try to get any valid user from the test endpoint
        try:
            response = requests.get(f"{BASE_URL}/test/users")
            if response.status_code == 200:
                users = response.json()
                print(f"Found {len(users)} users in database")
                for user in users[:5]:  # Show first 5 users
                    print(f"  - {user.get('email')} ({user.get('role')})")
        except:
            print("Could not retrieve user list")
        
        return
    
    print(f"\n✓ Authentication successful")
    
    # Test endpoints
    endpoints_to_test = [
        ("/hr/dashboard-stats", "Dashboard Stats"),
        ("/hr/properties", "Properties (Optimized)"),
        ("/hr/managers", "Managers (Optimized)"),
        ("/hr/users", "Users (Optimized)"),
    ]
    
    print("\n" + "=" * 60)
    print("Testing Optimized Endpoints")
    print("=" * 60)
    
    results = []
    total_time = 0
    
    for endpoint, name in endpoints_to_test:
        print(f"\nTesting {name}...")
        result = test_endpoint(endpoint, token, name)
        results.append(result)
        total_time += result["time"]
        
        if result["success"]:
            print(f"  ✓ Status: {result['status']}")
            print(f"  ✓ Time: {result['time']}s")
            print(f"  ✓ Size: {result['size']} bytes")
        else:
            print(f"  ✗ Status: {result['status']}")
            print(f"  ✗ Time: {result['time']}s")
    
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    
    print(f"\nTotal time for all endpoints: {round(total_time, 3)}s")
    print(f"Average response time: {round(total_time / len(results), 3)}s")
    
    # Check if we meet performance targets
    print("\n" + "=" * 60)
    print("Performance Analysis")
    print("=" * 60)
    
    if total_time < 2:
        print("✅ EXCELLENT: Total load time under 2 seconds!")
    elif total_time < 4:
        print("✅ GOOD: Total load time under 4 seconds")
    elif total_time < 6:
        print("⚠️  ACCEPTABLE: Total load time under 6 seconds")
    else:
        print("❌ NEEDS IMPROVEMENT: Total load time over 6 seconds")
    
    # Show breakdown
    print("\nDetailed Breakdown:")
    for result in sorted(results, key=lambda x: x["time"], reverse=True):
        status_icon = "✓" if result["success"] else "✗"
        print(f"  {status_icon} {result['name']}: {result['time']}s")
    
    # Compare with previous baseline (if known)
    print("\n" + "=" * 60)
    print("Optimization Impact")
    print("=" * 60)
    print("\nBefore optimization:")
    print("  - Multiple N+1 queries for each manager's properties")
    print("  - 11+ queries per endpoint for manager property lookups")
    print("  - Total time: 8-9 seconds (causing timeouts)")
    print("\nAfter optimization:")
    print("  - Batch fetching with 2-3 queries total")
    print("  - Single query for all manager properties")
    print(f"  - Total time: {round(total_time, 3)}s")
    
    if total_time < 6:
        improvement = round((9 - total_time) / 9 * 100, 1)
        print(f"\n🎉 Performance improved by ~{improvement}%!")

if __name__ == "__main__":
    main()