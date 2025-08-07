#!/usr/bin/env python3
"""
Simple HR Dashboard Stats Test
Test the HR dashboard endpoint directly
"""

import requests
import json
import sys

def test_hr_login():
    """Test HR login"""
    print("🔍 Testing HR login...")
    
    try:
        response = requests.post('http://127.0.0.1:8000/auth/login', json={
            'email': 'hr@hoteltest.com',
            'password': 'admin123'
        })
        
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful")
            token = data.get('data', {}).get('token') or data.get('token')
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_hr_dashboard_stats(token):
    """Test HR dashboard stats endpoint"""
    print("\n🔍 Testing HR dashboard stats...")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://127.0.0.1:8000/hr/dashboard-stats', headers=headers)
        
        print(f"Dashboard stats status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard stats successful")
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            # Check if data contains the expected fields
            stats_data = data.get('data', {})
            expected_fields = [
                'totalProperties', 'totalManagers', 'totalEmployees', 
                'pendingApplications', 'approvedApplications', 'totalApplications',
                'activeEmployees', 'onboardingInProgress'
            ]
            
            print(f"\n📊 KPI Values:")
            for field in expected_fields:
                value = stats_data.get(field, 'MISSING')
                print(f"  {field}: {value}")
            
            return data
        else:
            print(f"❌ Dashboard stats failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Dashboard stats error: {e}")
        return None

def test_individual_endpoints(token):
    """Test individual endpoints that might provide data"""
    print("\n🔍 Testing individual endpoints...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    endpoints_to_test = [
        ('/hr/properties', 'Properties'),
        ('/hr/applications', 'Applications'),
        ('/hr/managers', 'Managers'),
        ('/api/employees', 'Employees'),
    ]
    
    for endpoint, name in endpoints_to_test:
        try:
            print(f"  Testing {name} ({endpoint})...")
            response = requests.get(f'http://127.0.0.1:8000{endpoint}', headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Handle both wrapped and direct responses
                items = data.get('data', data) if isinstance(data, dict) else data
                count = len(items) if isinstance(items, list) else 0
                print(f"    ✅ {name}: {count} items")
            else:
                print(f"    ❌ {name}: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"    ❌ {name}: Error - {e}")

def test_backend_health():
    """Test if backend is running"""
    print("🔍 Testing backend health...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/healthz')
        print(f"Health check status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 HR Dashboard Stats Debug Test")
    print("=" * 50)
    
    # Test backend health
    if not test_backend_health():
        print("❌ Backend is not healthy, stopping tests")
        sys.exit(1)
    
    # Test HR login
    token = test_hr_login()
    if not token:
        print("❌ HR login failed, stopping tests")
        sys.exit(1)
    
    # Test dashboard stats
    stats_result = test_hr_dashboard_stats(token)
    
    # Test individual endpoints
    test_individual_endpoints(token)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if stats_result:
        stats_data = stats_result.get('data', {})
        all_zero = all(stats_data.get(field, 0) == 0 for field in [
            'totalProperties', 'totalManagers', 'totalEmployees', 'pendingApplications'
        ])
        
        if all_zero:
            print("⚠️  All KPI values are 0 - this indicates:")
            print("   1. No test data in the database")
            print("   2. Database tables might be empty")
            print("   3. Count methods might be failing silently")
            print("\n💡 SOLUTIONS:")
            print("   - Check if backend initialization created test data")
            print("   - Verify database tables have data")
            print("   - Check Supabase connection and permissions")
        else:
            print("✅ KPI values are populated correctly")
    else:
        print("❌ Dashboard stats endpoint failed completely")

if __name__ == "__main__":
    main()