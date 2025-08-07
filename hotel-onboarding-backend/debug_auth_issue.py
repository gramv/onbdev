#!/usr/bin/env python3
"""
Debug authentication issue with Supabase password storage
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.supabase_service_enhanced import EnhancedSupabaseService
supabase_service = EnhancedSupabaseService()
import bcrypt

def debug_user_auth():
    """Debug the authentication for hr.test.final@hotel.com"""
    email = "hr.test.final@hotel.com"
    password = "FinalTest123"
    
    print(f"🔍 Debugging authentication for: {email}")
    print("=" * 50)
    
    # 1. Check if user exists in Supabase
    print("1. Checking if user exists in Supabase...")
    user = supabase_service.get_user_by_email_sync(email)
    if not user:
        print("❌ User not found in Supabase")
        return False
    
    print(f"✅ User found: {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role}")
    print(f"   Has password_hash: {bool(user.password_hash)}")
    
    # 2. Check password hash
    if not user.password_hash:
        print("❌ No password_hash found for user")
        return False
    
    print(f"   Password hash (first 20 chars): {user.password_hash[:20]}...")
    
    # 3. Try to verify password
    print("2. Verifying password...")
    try:
        result = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
        if result:
            print("✅ Password verification successful")
            return True
        else:
            print("❌ Password verification failed")
            return False
    except Exception as e:
        print(f"❌ Password verification error: {e}")
        return False

if __name__ == "__main__":
    success = debug_user_auth()
    if success:
        print("\n🎉 Authentication should work!")
    else:
        print("\n❌ Authentication will fail")