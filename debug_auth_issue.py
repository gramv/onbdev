#!/usr/bin/env python3
"""
Debug authentication issues
"""

import sys
import os
import asyncio
import requests

# Add the backend path
sys.path.append('hotel-onboarding-backend')

from app.supabase_service_enhanced import EnhancedSupabaseService

async def debug_auth():
    """Debug authentication issues"""
    print("🔍 Debugging Authentication Issues...")
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv('hotel-onboarding-backend/.env')
        
        # Initialize service
        service = EnhancedSupabaseService()
        
        # Check users in database
        print("\n📋 Users in database:")
        users = await service.get_users()
        for user in users:
            print(f"  - {user.email} ({user.role})")
            print(f"    ID: {user.id}")
            print(f"    Has password_hash: {bool(user.password_hash)}")
            if user.password_hash:
                print(f"    Password hash: {user.password_hash[:50]}...")
            print()
        
        # Test password hashing
        print("🔐 Testing password hashing:")
        test_password = "admin123"
        hashed = service.hash_password(test_password)
        print(f"Test password: {test_password}")
        print(f"Hashed: {hashed}")
        
        # Test verification
        is_valid = service.verify_password(test_password, hashed)
        print(f"Verification works: {is_valid}")
        
        # If we have users, test their passwords
        if users:
            hr_user = next((u for u in users if u.email == "hr@hoteltest.com"), None)
            if hr_user and hr_user.password_hash:
                print(f"\n🔍 Testing HR user password:")
                hr_verify = service.verify_password("admin123", hr_user.password_hash)
                print(f"HR password 'admin123' verification: {hr_verify}")
                
                # Try the old password from memory manager
                hr_verify2 = service.verify_password("password123", hr_user.password_hash)
                print(f"HR password 'password123' verification: {hr_verify2}")
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_auth())