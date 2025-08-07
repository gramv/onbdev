#!/usr/bin/env python3
"""
Debug HR Dashboard Stats Issue
Test the HR dashboard stats endpoint and individual count methods
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('hotel-onboarding-backend')
sys.path.append('hotel-onboarding-backend/app')

from supabase_service_enhanced import EnhancedSupabaseService

async def test_individual_count_methods():
    """Test each count method individually"""
    print("🔍 Testing individual count methods...")
    
    try:
        supabase_service = EnhancedSupabaseService()
        
        # Test each count method
        methods_to_test = [
            ('Properties Count', supabase_service.get_properties_count),
            ('Managers Count', supabase_service.get_managers_count),
            ('Employees Count', supabase_service.get_employees_count),
            ('Pending Applications Count', supabase_service.get_pending_applications_count),
            ('Approved Applications Count', supabase_service.get_approved_applications_count),
            ('Total Applications Count', supabase_service.get_total_applications_count),
            ('Active Employees Count', supabase_service.get_active_employees_count),
        ]
        
        results = {}
        for method_name, method in methods_to_test:
            try:
                print(f"  Testing {method_name}...")
                count = await method()
                results[method_name] = count
                print(f"    ✅ {method_name}: {count}")
            except Exception as e:
                results[method_name] = f"ERROR: {str(e)}"
                print(f"    ❌ {method_name}: ERROR - {e}")
        
        return results
        
    except Exception as e:
        print(f"❌ Failed to initialize Supabase service: {e}")
        return {}

def test_hr_dashboard_endpoint():
    """Test the HR dashboard stats endpoint directly"""
    print("\n🔍 Testing HR dashboard stats endpoint...")
    
    try:
        # First, login to get HR token
        login_response = requests.post('http://127.0.0.1:8000/auth/login', json={
            'email': 'hr@hoteltest.com',
            'password': 'admin123'
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return None
        
        login_data = login_response.json()
        token = login_data.get('data', {}).get('token') or login_data.get('token')
        
        if not token:
            print(f"❌ No token in login response: {login_data}")
            return None
        
        print(f"✅ Login successful, token: {token[:20]}...")
        
        # Test the dashboard stats endpoint
        headers = {'Authorization': f'Bearer {token}'}
        stats_response = requests.get('http://127.0.0.1:8000/hr/dashboard-stats', headers=headers)
        
        print(f"📊 Dashboard stats response status: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"✅ Dashboard stats response: {json.dumps(stats_data, indent=2)}")
            return stats_data
        else:
            print(f"❌ Dashboard stats failed: {stats_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing HR dashboard endpoint: {e}")
        return None

def test_database_tables_directly():
    """Test database tables directly to see if data exists"""
    print("\n🔍 Testing database tables directly...")
    
    try:
        supabase_service = EnhancedSupabaseService()
        
        # Test each table directly
        tables_to_test = [
            ('properties', 'is_active', True),
            ('users', 'role', 'manager'),
            ('job_applications', 'status', 'pending'),
            ('employees', 'employment_status', 'active'),
        ]
        
        for table_name, filter_col, filter_val in tables_to_test:
            try:
                print(f"  Testing {table_name} table...")
                
                # Get all records first
                all_response = supabase_service.client.table(table_name).select('*').execute()
                all_count = len(all_response.data) if all_response.data else 0
                print(f"    Total records in {table_name}: {all_count}")
                
                if all_count > 0:
                    print(f"    Sample record: {all_response.data[0] if all_response.data else 'None'}")
                
                # Get filtered records
                if filter_col and filter_val:
                    filtered_response = supabase_service.client.table(table_name).select('*').eq(filter_col, filter_val).execute()
                    filtered_count = len(filtered_response.data) if filtered_response.data else 0
                    print(f"    Filtered records ({filter_col}={filter_val}): {filtered_count}")
                
            except Exception as e:
                print(f"    ❌ Error testing {table_name}: {e}")
        
    except Exception as e:
        print(f"❌ Error testing database tables: {e}")

async def check_supabase_connection():
    """Check if Supabase connection is working"""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        supabase_service = EnhancedSupabaseService()
        health_check = await supabase_service.health_check()
        print(f"📊 Supabase health check: {health_check}")
        return health_check.get('status') == 'healthy'
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False

async def main():
    """Main debug function"""
    print("🚀 Starting HR Dashboard Stats Debug")
    print("=" * 50)
    
    # Check Supabase connection
    connection_ok = await check_supabase_connection()
    if not connection_ok:
        print("❌ Supabase connection failed, stopping debug")
        return
    
    # Test individual count methods
    count_results = await test_individual_count_methods()
    
    # Test database tables directly
    test_database_tables_directly()
    
    # Test HR dashboard endpoint
    endpoint_result = test_hr_dashboard_endpoint()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DEBUG SUMMARY")
    print("=" * 50)
    
    print("\n🔢 Count Method Results:")
    for method, result in count_results.items():
        print(f"  {method}: {result}")
    
    if endpoint_result:
        print(f"\n🌐 Endpoint Result: SUCCESS")
        data = endpoint_result.get('data', {})
        print(f"  Total Properties: {data.get('totalProperties', 'N/A')}")
        print(f"  Total Managers: {data.get('totalManagers', 'N/A')}")
        print(f"  Total Employees: {data.get('totalEmployees', 'N/A')}")
        print(f"  Pending Applications: {data.get('pendingApplications', 'N/A')}")
    else:
        print(f"\n🌐 Endpoint Result: FAILED")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if all(isinstance(result, int) and result == 0 for result in count_results.values() if isinstance(result, int)):
        print("  - All counts are 0, check if test data exists in database")
        print("  - Run: python hotel-onboarding-backend/populate_sample_data.py")
    
    if any("ERROR" in str(result) for result in count_results.values()):
        print("  - Some count methods are failing, check Supabase connection and table structure")
    
    if not endpoint_result:
        print("  - HR dashboard endpoint is failing, check authentication and endpoint implementation")

if __name__ == "__main__":
    asyncio.run(main())