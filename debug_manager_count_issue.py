#!/usr/bin/env python3
"""
Debug Manager Count Issue
The /hr/managers endpoint returns 7 managers but totalManagers shows 0
"""

import requests
import json

def test_manager_endpoints():
    """Test manager-related endpoints"""
    print("🔍 Testing manager endpoints...")
    
    # Login first
    login_response = requests.post('http://127.0.0.1:8000/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json().get('data', {}).get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test /hr/managers endpoint
    print("\n📊 Testing /hr/managers endpoint:")
    managers_response = requests.get('http://127.0.0.1:8000/hr/managers', headers=headers)
    
    if managers_response.status_code == 200:
        managers_data = managers_response.json()
        # Handle both wrapped and direct responses
        if isinstance(managers_data, dict):
            managers = managers_data.get('data', managers_data)
        else:
            managers = managers_data
        print(f"✅ /hr/managers returned {len(managers)} managers")
        
        if managers:
            print("Sample manager data:")
            for i, manager in enumerate(managers[:3]):  # Show first 3
                print(f"  Manager {i+1}:")
                print(f"    ID: {manager.get('id')}")
                print(f"    Email: {manager.get('email')}")
                print(f"    Role: {manager.get('role')}")
                print(f"    Is Active: {manager.get('is_active')}")
                print(f"    Property ID: {manager.get('property_id')}")
    else:
        print(f"❌ /hr/managers failed: {managers_response.status_code}")
        print(f"Response: {managers_response.text}")
    
    # Test /hr/users endpoint to see all users
    print("\n📊 Testing /hr/users endpoint:")
    users_response = requests.get('http://127.0.0.1:8000/hr/users', headers=headers)
    
    if users_response.status_code == 200:
        users_data = users_response.json()
        # Handle both wrapped and direct responses
        if isinstance(users_data, dict):
            users = users_data.get('data', users_data)
        else:
            users = users_data
        print(f"✅ /hr/users returned {len(users)} users")
        
        # Count by role
        role_counts = {}
        active_counts = {}
        
        for user in users:
            role = user.get('role', 'unknown')
            is_active = user.get('is_active', False)
            
            role_counts[role] = role_counts.get(role, 0) + 1
            
            if is_active:
                active_key = f"{role}_active"
                active_counts[active_key] = active_counts.get(active_key, 0) + 1
        
        print("Role breakdown:")
        for role, count in role_counts.items():
            active_count = active_counts.get(f"{role}_active", 0)
            print(f"  {role}: {count} total, {active_count} active")
    else:
        print(f"❌ /hr/users failed: {users_response.status_code}")
        print(f"Response: {users_response.text}")

def test_direct_database_query():
    """Test what the count method is actually querying"""
    print("\n🔍 Testing what the count method queries...")
    
    # Login first
    login_response = requests.post('http://127.0.0.1:8000/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed")
        return
    
    token = login_response.json().get('data', {}).get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # The count method queries: users table where role='manager' AND is_active=True
    # Let's see what this returns by getting all users and filtering
    users_response = requests.get('http://127.0.0.1:8000/hr/users', headers=headers)
    
    if users_response.status_code == 200:
        users_data = users_response.json()
        # Handle both wrapped and direct responses
        if isinstance(users_data, dict):
            users = users_data.get('data', users_data)
        else:
            users = users_data
        
        # Filter like the count method does
        active_managers = [
            user for user in users 
            if user.get('role') == 'manager' and user.get('is_active') == True
        ]
        
        print(f"📊 Users matching count query (role='manager' AND is_active=True): {len(active_managers)}")
        
        if active_managers:
            print("Active managers found:")
            for manager in active_managers:
                print(f"  - {manager.get('email')} (ID: {manager.get('id')}, Active: {manager.get('is_active')})")
        else:
            print("❌ No active managers found!")
            
            # Check all managers regardless of active status
            all_managers = [user for user in users if user.get('role') == 'manager']
            print(f"\n📊 All managers (regardless of is_active): {len(all_managers)}")
            
            if all_managers:
                print("All managers:")
                for manager in all_managers:
                    print(f"  - {manager.get('email')} (ID: {manager.get('id')}, Active: {manager.get('is_active')})")

def main():
    print("🚀 Debug Manager Count Issue")
    print("=" * 50)
    
    test_manager_endpoints()
    test_direct_database_query()
    
    print("\n" + "=" * 50)
    print("💡 ANALYSIS:")
    print("The issue is likely that:")
    print("1. The /hr/managers endpoint uses a different query than the count method")
    print("2. The count method filters by is_active=True but managers might have is_active=False")
    print("3. There might be a data type mismatch (boolean vs string)")

if __name__ == "__main__":
    main()