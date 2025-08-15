#!/usr/bin/env python3
"""
Test Login Logic Directly
Mimics exactly what the main app does for login
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.supabase_service_enhanced import EnhancedSupabaseService

def test_login_logic():
    """Test the exact same login logic as main app"""
    email = "manager@demo.com"
    password = "demo123"
    
    print(f"Testing login logic for: {email}")
    
    # Initialize service (same as main app)
    supabase_service = EnhancedSupabaseService()
    
    # Step 1: Find user in Supabase (same as main app)
    existing_user = supabase_service.get_user_by_email_sync(email)
    if not existing_user:
        print("❌ User not found")
        return False
    
    print(f"✅ User found: {existing_user.email}")
    print(f"   Role: {existing_user.role}")
    print(f"   Has password hash: {bool(existing_user.password_hash)}")
    
    # Step 2: Check password hash exists (same as main app)
    if not existing_user.password_hash:
        print("❌ No password hash found")
        return False
    
    print("✅ Password hash exists")
    
    # Step 3: Verify password (same as main app)
    if not supabase_service.verify_password(password, existing_user.password_hash):
        print("❌ Password verification failed")
        return False
    
    print("✅ Password verification successful")
    
    # Step 4: Check manager properties (same as main app)
    if existing_user.role == "manager":
        manager_properties = supabase_service.get_manager_properties_sync(existing_user.id)
        if not manager_properties:
            print("❌ Manager has no properties")
            return False
        
        print(f"✅ Manager has {len(manager_properties)} properties:")
        for prop in manager_properties:
            print(f"   - {prop.name} ({prop.id})")
    
    print("✅ Login logic would succeed")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING LOGIN LOGIC DIRECTLY")
    print("=" * 60)
    
    success = test_login_logic()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 LOGIN LOGIC WORKS - The issue is elsewhere!")
    else:
        print("❌ LOGIN LOGIC FAILED")