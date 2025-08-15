#!/usr/bin/env python3
"""
Create test accounts with proper bcrypt password hashing in Supabase
"""

import sys
import os
import asyncio
import bcrypt
from datetime import datetime, timezone

# Add the backend path
sys.path.append('hotel-onboarding-backend')

from app.supabase_service_enhanced import EnhancedSupabaseService
from app.models import User, UserRole

async def create_test_accounts():
    """Create test accounts with proper password hashing"""
    print("🔐 Creating test accounts with bcrypt password hashing...")
    
    try:
        # Initialize Supabase service
        service = EnhancedSupabaseService()
        
        # Check if users already exist
        existing_users = await service.get_users()
        print(f"Found {len(existing_users)} existing users")
        
        # Hash passwords
        hr_password = "admin123"
        manager_password = "manager123"
        
        hr_password_hash = service.hash_password(hr_password)
        manager_password_hash = service.hash_password(manager_password)
        
        print(f"✅ Passwords hashed successfully")
        
        # Create or update HR user
        hr_exists = any(user.email == "hr@hoteltest.com" for user in existing_users)
        if not hr_exists:
            hr_user_data = {
                "id": "hr_test_001",
                "email": "hr@hoteltest.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "role": "hr",
                "password_hash": hr_password_hash,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = service.client.table('users').insert(hr_user_data).execute()
            if result.data:
                print("✅ HR user created successfully")
            else:
                print("❌ Failed to create HR user")
        else:
            # Update existing HR user with new password hash
            result = service.client.table('users').update({
                "password_hash": hr_password_hash
            }).eq('email', 'hr@hoteltest.com').execute()
            print("✅ HR user password updated")
        
        # Create or update Manager user
        manager_exists = any(user.email == "manager@hoteltest.com" for user in existing_users)
        if not manager_exists:
            manager_user_data = {
                "id": "mgr_test_001",
                "email": "manager@hoteltest.com",
                "first_name": "Mike",
                "last_name": "Wilson",
                "role": "manager",
                "password_hash": manager_password_hash,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = service.client.table('users').insert(manager_user_data).execute()
            if result.data:
                print("✅ Manager user created successfully")
            else:
                print("❌ Failed to create Manager user")
        else:
            # Update existing Manager user with new password hash
            result = service.client.table('users').update({
                "password_hash": manager_password_hash
            }).eq('email', 'manager@hoteltest.com').execute()
            print("✅ Manager user password updated")
        
        # Verify password hashing works
        print("\n🔍 Verifying password hashing...")
        
        # Test HR password
        hr_verify = service.verify_password(hr_password, hr_password_hash)
        print(f"HR password verification: {'✅ PASS' if hr_verify else '❌ FAIL'}")
        
        # Test Manager password
        manager_verify = service.verify_password(manager_password, manager_password_hash)
        print(f"Manager password verification: {'✅ PASS' if manager_verify else '❌ FAIL'}")
        
        # Test wrong password
        wrong_verify = service.verify_password("wrongpassword", hr_password_hash)
        print(f"Wrong password rejection: {'✅ PASS' if not wrong_verify else '❌ FAIL'}")
        
        print("\n🎉 Test account creation complete!")
        print("\n📋 Test Accounts:")
        print("HR Account:")
        print("  Email: hr@hoteltest.com")
        print("  Password: admin123")
        print(f"  Password Hash: {hr_password_hash[:50]}...")
        
        print("\nManager Account:")
        print("  Email: manager@hoteltest.com")
        print("  Password: manager123")
        print(f"  Password Hash: {manager_password_hash[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test accounts: {e}")
        return False

def main():
    """Main function"""
    print("🏨 Hotel Onboarding System - Test Account Creation")
    print("=" * 60)
    
    # Run the async function
    success = asyncio.run(create_test_accounts())
    
    if success:
        print("\n✅ All test accounts created successfully!")
        print("\n🚀 Next steps:")
        print("1. Start the backend server:")
        print("   cd hotel-onboarding-backend")
        print("   python -m uvicorn app.main_enhanced:app --reload")
        print("2. Run the authentication test:")
        print("   python test_authentication_fix.py")
    else:
        print("\n❌ Test account creation failed!")

if __name__ == "__main__":
    main()