#!/usr/bin/env python3
"""
Fix Manager Property Assignment Issues
Ensures managers are properly assigned to properties for access control
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add the app directory to the path
app_path = os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend', 'app')
sys.path.insert(0, app_path)

from supabase_service_enhanced import EnhancedSupabaseService
from models import User, Property, UserRole

async def fix_manager_property_assignment():
    """Fix manager property assignment in the database"""
    print("🔧 Fixing Manager Property Assignment...")
    
    try:
        # Initialize Supabase service
        supabase_service = EnhancedSupabaseService()
        
        # Check current users
        print("\n1. Checking current users...")
        users = await supabase_service.get_users()
        
        manager_user = None
        for user in users:
            print(f"   User: {user.email} - Role: {user.role}")
            if user.role == "manager":
                manager_user = user
        
        if not manager_user:
            print("   ❌ No manager user found!")
            return False
        
        print(f"   ✅ Found manager: {manager_user.email}")
        
        # Check current properties
        print("\n2. Checking current properties...")
        properties = await supabase_service.get_all_properties()
        
        if not properties:
            print("   ❌ No properties found!")
            return False
        
        test_property = None
        for prop in properties:
            print(f"   Property: {prop.name} - ID: {prop.id}")
            if "test" in prop.name.lower() or "grand plaza" in prop.name.lower():
                test_property = prop
        
        if not test_property:
            test_property = properties[0]  # Use first property
        
        print(f"   ✅ Using property: {test_property.name}")
        
        # Check current manager-property assignments
        print("\n3. Checking current manager-property assignments...")
        manager_properties = await supabase_service.get_manager_properties(manager_user.id)
        
        print(f"   Manager currently assigned to {len(manager_properties)} properties")
        for prop in manager_properties:
            print(f"   - {prop.name}")
        
        # Assign manager to property if not already assigned
        if not manager_properties or test_property.id not in [p.id for p in manager_properties]:
            print(f"\n4. Assigning manager {manager_user.email} to property {test_property.name}...")
            
            success = await supabase_service.assign_manager_to_property(manager_user.id, test_property.id)
            
            if success:
                print("   ✅ Manager successfully assigned to property")
                
                # Verify assignment
                updated_properties = await supabase_service.get_manager_properties(manager_user.id)
                print(f"   ✅ Verification: Manager now assigned to {len(updated_properties)} properties")
                
                return True
            else:
                print("   ❌ Failed to assign manager to property")
                return False
        else:
            print("   ✅ Manager already properly assigned to property")
            return True
            
    except Exception as e:
        print(f"   ❌ Error fixing manager property assignment: {e}")
        return False

async def verify_property_access_control():
    """Verify that property access control is working correctly"""
    print("\n🧪 Verifying Property Access Control...")
    
    try:
        supabase_service = EnhancedSupabaseService()
        
        # Get manager user
        users = await supabase_service.get_users()
        manager_user = None
        for user in users:
            if user.role == "manager":
                manager_user = user
                break
        
        if not manager_user:
            print("   ❌ No manager user found for verification")
            return False
        
        # Test property access
        manager_properties = await supabase_service.get_manager_properties(manager_user.id)
        print(f"   Manager {manager_user.email} has access to {len(manager_properties)} properties:")
        
        for prop in manager_properties:
            print(f"   - {prop.name} (ID: {prop.id})")
        
        if manager_properties:
            print("   ✅ Property access control verification successful")
            return True
        else:
            print("   ❌ Manager has no property access")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verifying property access control: {e}")
        return False

async def main():
    """Main function to fix manager property assignment issues"""
    print("🚀 Starting Manager Property Assignment Fix")
    print("=" * 50)
    
    # Fix manager property assignment
    assignment_success = await fix_manager_property_assignment()
    
    # Verify property access control
    verification_success = await verify_property_access_control()
    
    print("\n" + "=" * 50)
    print("📊 Fix Summary:")
    print(f"   Assignment Fix: {'✅ SUCCESS' if assignment_success else '❌ FAILED'}")
    print(f"   Verification: {'✅ SUCCESS' if verification_success else '❌ FAILED'}")
    
    if assignment_success and verification_success:
        print("\n🎉 Manager property assignment successfully fixed!")
        return True
    else:
        print("\n⚠️ Manager property assignment fix failed.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)