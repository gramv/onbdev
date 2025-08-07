#!/usr/bin/env python3
"""
Debug Frontend KPI Issue
Test the exact API call the frontend is making and check the response format
"""

import requests
import json

def test_frontend_api_call():
    """Test the exact API call the frontend makes"""
    print("🔍 Testing Frontend API Call...")
    
    # Step 1: Login exactly like the frontend does
    print("\n1. Testing login...")
    login_response = requests.post('http://127.0.0.1:8000/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    login_data = login_response.json()
    print(f"Login response structure: {json.dumps(login_data, indent=2)}")
    
    # Extract token like the frontend does
    token = login_data.get('data', {}).get('token') or login_data.get('token')
    
    if not token:
        print(f"❌ No token found in login response")
        return
    
    print(f"✅ Token extracted: {token[:20]}...")
    
    # Step 2: Make the dashboard stats call exactly like the frontend
    print("\n2. Testing dashboard stats call...")
    
    # Frontend uses localStorage.getItem('token') and axios config
    headers = {'Authorization': f'Bearer {token}'}
    
    stats_response = requests.get('http://127.0.0.1:8000/hr/dashboard-stats', headers=headers)
    
    print(f"Stats response status: {stats_response.status_code}")
    print(f"Stats response headers: {dict(stats_response.headers)}")
    
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print(f"Raw stats response: {json.dumps(stats_data, indent=2)}")
        
        # Test frontend data extraction logic
        print("\n3. Testing frontend data extraction...")
        
        # Frontend does: const statsData = response.data.data || response.data
        extracted_data = stats_data.get('data', stats_data)
        print(f"Extracted data: {json.dumps(extracted_data, indent=2)}")
        
        # Check if the expected fields exist
        expected_fields = ['totalProperties', 'totalManagers', 'totalEmployees', 'pendingApplications']
        
        print("\n4. Checking expected fields...")
        for field in expected_fields:
            value = extracted_data.get(field, 'MISSING')
            print(f"  {field}: {value}")
            
            if value == 'MISSING':
                print(f"    ❌ Field {field} is missing!")
            elif value == 0:
                print(f"    ⚠️  Field {field} is 0 (might be correct or might be an issue)")
            else:
                print(f"    ✅ Field {field} has value: {value}")
        
        return extracted_data
    else:
        print(f"❌ Stats call failed: {stats_response.text}")
        return None

def test_individual_count_methods():
    """Test individual count methods to see what they return"""
    print("\n🔍 Testing individual count methods...")
    
    # Login
    login_response = requests.post('http://127.0.0.1:8000/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    token = login_response.json().get('data', {}).get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test individual endpoints that provide the data
    endpoints = [
        ('/hr/properties', 'Properties'),
        ('/hr/managers', 'Managers'),
        ('/hr/applications', 'Applications'),
        ('/api/employees', 'Employees')
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f'http://127.0.0.1:8000{endpoint}', headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle both wrapped and direct responses
                if isinstance(data, dict) and 'data' in data:
                    items = data['data']
                elif isinstance(data, list):
                    items = data
                else:
                    items = data
                
                count = len(items) if isinstance(items, list) else 0
                print(f"  {name}: {count} items from {endpoint}")
                
                # Show sample data structure
                if items and isinstance(items, list) and len(items) > 0:
                    sample = items[0]
                    print(f"    Sample item keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not a dict'}")
            else:
                print(f"  {name}: ERROR {response.status_code}")
                
        except Exception as e:
            print(f"  {name}: EXCEPTION {e}")

def check_backend_logs():
    """Check if there are any backend errors"""
    print("\n🔍 Checking backend health...")
    
    try:
        health_response = requests.get('http://127.0.0.1:8000/healthz')
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Backend is healthy")
            print(f"Database connection: {health_data.get('data', {}).get('connection', {}).get('status', 'unknown')}")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")

def test_cors_and_headers():
    """Test CORS and headers that might affect frontend"""
    print("\n🔍 Testing CORS and headers...")
    
    # Test preflight request
    try:
        preflight_response = requests.options('http://127.0.0.1:8000/hr/dashboard-stats', 
                                            headers={
                                                'Origin': 'http://localhost:3000',
                                                'Access-Control-Request-Method': 'GET',
                                                'Access-Control-Request-Headers': 'authorization'
                                            })
        
        print(f"Preflight status: {preflight_response.status_code}")
        print(f"CORS headers: {dict(preflight_response.headers)}")
        
    except Exception as e:
        print(f"Preflight request failed: {e}")

def main():
    print("🚀 Debug Frontend KPI Issue")
    print("=" * 60)
    
    # Check backend health first
    check_backend_logs()
    
    # Test the exact frontend API call
    stats_data = test_frontend_api_call()
    
    # Test individual endpoints
    test_individual_count_methods()
    
    # Test CORS
    test_cors_and_headers()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DIAGNOSIS:")
    
    if stats_data:
        all_zero = all(stats_data.get(field, 0) == 0 for field in ['totalProperties', 'totalManagers', 'totalEmployees', 'pendingApplications'])
        
        if all_zero:
            print("❌ All KPI values are 0 - Backend count methods are returning 0")
            print("💡 POSSIBLE CAUSES:")
            print("   1. Database tables are empty")
            print("   2. Count methods have incorrect queries")
            print("   3. Database connection issues")
            print("   4. RLS (Row Level Security) blocking queries")
        else:
            print("✅ Backend is returning non-zero values")
            print("💡 ISSUE IS LIKELY:")
            print("   1. Frontend data extraction logic")
            print("   2. State management in React component")
            print("   3. Timing issues with useEffect")
    else:
        print("❌ Backend API call failed completely")
        print("💡 ISSUE IS LIKELY:")
        print("   1. Authentication problems")
        print("   2. Backend endpoint errors")
        print("   3. Network connectivity issues")

if __name__ == "__main__":
    main()