#!/usr/bin/env python3
"""
Fix authentication by creating proper test accounts with password hashes
"""

import sys
import os
import asyncio
import requests
from datetime import datetime, timezone

# Add the backend path
sys.path.append('hotel-onboarding-backend')

from app.supabase_service_enhanced import EnhancedSupabaseService

async def create_proper_test_accounts():
    """Create the test accounts that the system expects"""
    print("🔐 Creating proper test accounts...")
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv('hotel-onboarding-backend/.env')
        
        # Initialize service
        service = EnhancedSupabaseService()
        
        # Hash passwords
        hr_password_hash = service.hash_password("admin123")
        manager_password_hash = service.hash_password("manager123")
        
        print("✅ Passwords hashed successfully")
        
        # Create HR test user
        import uuid
        hr_user_data = {
            "id": str(uuid.uuid4()),
            "email": "hr@hoteltest.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "hr",
            "password_hash": hr_password_hash,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Delete existing user if exists
        service.client.table('users').delete().eq('email', 'hr@hoteltest.com').execute()
        
        # Create new user
        result = service.client.table('users').insert(hr_user_data).execute()
        if result.data:
            print("✅ HR test user created: hr@hoteltest.com")
        else:
            print("❌ Failed to create HR user")
            print(f"Error: {result}")
        
        # Create Manager test user
        manager_user_id = str(uuid.uuid4())
        manager_user_data = {
            "id": manager_user_id,
            "email": "manager@hoteltest.com",
            "first_name": "Mike",
            "last_name": "Wilson",
            "role": "manager",
            "password_hash": manager_password_hash,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Delete existing user if exists
        service.client.table('users').delete().eq('email', 'manager@hoteltest.com').execute()
        
        # Create new user
        result = service.client.table('users').insert(manager_user_data).execute()
        if result.data:
            print("✅ Manager test user created: manager@hoteltest.com")
        else:
            print("❌ Failed to create Manager user")
            print(f"Error: {result}")
        
        # Create test property
        property_id = str(uuid.uuid4())
        property_data = {
            "id": property_id,
            "name": "Grand Plaza Hotel",
            "address": "123 Main Street",
            "city": "Downtown",
            "state": "CA",
            "zip_code": "90210",
            "phone": "(555) 123-4567",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Delete existing property if exists
        service.client.table('properties').delete().eq('id', 'prop_test_001').execute()
        
        # Create new property
        result = service.client.table('properties').insert(property_data).execute()
        if result.data:
            print("✅ Test property created: Grand Plaza Hotel")
        else:
            print("❌ Failed to create test property")
        
        # Assign manager to property
        assignment_data = {
            "manager_id": "mgr_test_001",
            "property_id": "prop_test_001",
            "assigned_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Delete existing assignment if exists
        service.client.table('manager_properties').delete().eq('manager_id', 'mgr_test_001').execute()
        
        # Create new assignment
        result = service.client.table('manager_properties').insert(assignment_data).execute()
        if result.data:
            print("✅ Manager assigned to property")
        else:
            print("❌ Failed to assign manager to property")
        
        # Verify the accounts work
        print("\n🔍 Verifying accounts...")
        
        # Test HR login
        hr_login_data = {
            "email": "hr@hoteltest.com",
            "password": "admin123"
        }
        
        response = requests.post("http://localhost:8000/auth/login", json=hr_login_data)
        if response.status_code == 200:
            print("✅ HR login test successful")
            hr_data = response.json()
            print(f"   User: {hr_data['user']['first_name']} {hr_data['user']['last_name']}")
        else:
            print(f"❌ HR login test failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        # Test Manager login
        manager_login_data = {
            "email": "manager@hoteltest.com",
            "password": "manager123"
        }
        
        response = requests.post("http://localhost:8000/auth/login", json=manager_login_data)
        if response.status_code == 200:
            print("✅ Manager login test successful")
            manager_data = response.json()
            print(f"   User: {manager_data['user']['first_name']} {manager_data['user']['last_name']}")
        else:
            print(f"❌ Manager login test failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        print("\n🎉 Test accounts created and verified!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🏨 Hotel Onboarding System - Authentication Fix")
    print("=" * 60)
    
    success = asyncio.run(create_proper_test_accounts())
    
    if success:
        print("\n✅ Authentication system fixed!")
        print("\n📋 Test Credentials:")
        print("HR Account:")
        print("  Email: hr@hoteltest.com")
        print("  Password: admin123")
        
        print("\nManager Account:")
        print("  Email: manager@hoteltest.com")
        print("  Password: manager123")
        
        print("\n🚀 Run the full test suite:")
        print("  python3 test_authentication_fix.py")
    else:
        print("\n❌ Authentication fix failed!")

if __name__ == "__main__":
    main()