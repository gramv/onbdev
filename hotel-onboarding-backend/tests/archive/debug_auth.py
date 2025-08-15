#!/usr/bin/env python3
"""
Debug Authentication Issues
Tests database queries and password verification directly
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.supabase_service_enhanced import EnhancedSupabaseService
from app.auth import PasswordManager

class AuthDebugger:
    def __init__(self):
        self.supabase_service = EnhancedSupabaseService()
        self.password_manager = PasswordManager()
    
    async def debug_user_lookup(self, email: str):
        """Debug user lookup in database"""
        print(f"Looking up user: {email}")
        
        try:
            # Test async method
            user = await self.supabase_service.get_user_by_email(email)
            if user:
                print(f"✅ User found (async): {user.email}")
                print(f"   Role: {user.role}")
                print(f"   ID: {user.id}")
                print(f"   Has password hash: {bool(user.password_hash)}")
                print(f"   Is active: {user.is_active}")
                return user
            else:
                print("❌ User not found (async)")
                return None
                
        except Exception as e:
            print(f"❌ Async lookup failed: {e}")
            return None
    
    def debug_user_lookup_sync(self, email: str):
        """Debug synchronous user lookup"""
        print(f"Looking up user synchronously: {email}")
        
        try:
            user = self.supabase_service.get_user_by_email_sync(email)
            if user:
                print(f"✅ User found (sync): {user.email}")
                print(f"   Role: {user.role}")
                print(f"   ID: {user.id}")
                print(f"   Has password hash: {bool(user.password_hash)}")
                print(f"   Is active: {user.is_active}")
                return user
            else:
                print("❌ User not found (sync)")
                return None
                
        except Exception as e:
            print(f"❌ Sync lookup failed: {e}")
            return None
    
    def debug_password_verification(self, password: str, password_hash: str):
        """Debug password verification"""
        print(f"Testing password verification...")
        
        try:
            # Test with supabase service method
            is_valid_service = self.supabase_service.verify_password(password, password_hash)
            print(f"Supabase service verification: {is_valid_service}")
            
            # Test with PasswordManager static method
            is_valid_manager = PasswordManager.verify_password(password, password_hash)
            print(f"PasswordManager verification: {is_valid_manager}")
            
            return is_valid_service or is_valid_manager
            
        except Exception as e:
            print(f"❌ Password verification failed: {e}")
            return False
    
    async def debug_manager_properties(self, manager_id: str):
        """Debug manager property lookup"""
        print(f"Looking up properties for manager: {manager_id}")
        
        try:
            # Test sync method
            properties = self.supabase_service.get_manager_properties_sync(manager_id)
            if properties:
                print(f"✅ Found {len(properties)} properties")
                for prop in properties:
                    print(f"   Property: {prop.name} ({prop.id})")
                return properties
            else:
                print("❌ No properties found")
                return []
                
        except Exception as e:
            print(f"❌ Property lookup failed: {e}")
            return []
    
    def debug_direct_database_query(self, email: str):
        """Debug direct database query"""
        print(f"Direct database query for: {email}")
        
        try:
            result = self.supabase_service.client.table("users").select("*").eq("email", email.lower()).execute()
            print(f"Query result: {len(result.data) if result.data else 0} rows")
            
            if result.data:
                user_data = result.data[0]
                print(f"Raw user data keys: {list(user_data.keys())}")
                print(f"Email: {user_data.get('email')}")
                print(f"Role: {user_data.get('role')}")
                print(f"Password hash exists: {bool(user_data.get('password_hash'))}")
                return user_data
            else:
                print("❌ No data returned")
                return None
                
        except Exception as e:
            print(f"❌ Direct query failed: {e}")
            return None

async def main():
    print("=" * 60)
    print("AUTHENTICATION DEBUG")
    print("=" * 60)
    
    debugger = AuthDebugger()
    email = "manager@demo.com"
    password = "demo123"
    
    # Test 1: Direct database query
    print("\n1. Testing direct database query...")
    raw_user = debugger.debug_direct_database_query(email)
    
    # Test 2: Async user lookup
    print("\n2. Testing async user lookup...")
    user_async = await debugger.debug_user_lookup(email)
    
    # Test 3: Sync user lookup
    print("\n3. Testing sync user lookup...")
    user_sync = debugger.debug_user_lookup_sync(email)
    
    # Test 4: Password verification
    if user_async and user_async.password_hash:
        print("\n4. Testing password verification...")
        password_valid = debugger.debug_password_verification(password, user_async.password_hash)
        print(f"Password verification result: {password_valid}")
    elif user_sync and user_sync.password_hash:
        print("\n4. Testing password verification...")
        password_valid = debugger.debug_password_verification(password, user_sync.password_hash)
        print(f"Password verification result: {password_valid}")
    else:
        print("\n4. Cannot test password - no user or password hash found")
        password_valid = False
    
    # Test 5: Manager properties
    if user_async:
        print("\n5. Testing manager properties...")
        properties = await debugger.debug_manager_properties(user_async.id)
    elif user_sync:
        print("\n5. Testing manager properties...")
        properties = await debugger.debug_manager_properties(user_sync.id)
    else:
        print("\n5. Cannot test properties - no user found")
        properties = []
    
    # Summary
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    print(f"Raw database query: {'✅ SUCCESS' if raw_user else '❌ FAILED'}")
    print(f"Async user lookup: {'✅ SUCCESS' if user_async else '❌ FAILED'}")
    print(f"Sync user lookup: {'✅ SUCCESS' if user_sync else '❌ FAILED'}")
    print(f"Password verification: {'✅ SUCCESS' if password_valid else '❌ FAILED'}")
    print(f"Manager properties: {'✅ SUCCESS' if properties else '❌ FAILED'}")
    
    if all([raw_user, user_async, password_valid]):
        print("\n🎉 Authentication system appears to be working!")
    else:
        print("\n⚠️  Some components are not working properly.")

if __name__ == "__main__":
    asyncio.run(main())