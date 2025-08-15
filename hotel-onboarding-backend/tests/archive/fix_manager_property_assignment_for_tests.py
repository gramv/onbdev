#!/usr/bin/env python3
"""
Fix Manager Property Assignment for Document Access Tests
========================================================

This script assigns the demo manager to the specified property to enable
comprehensive testing of manager document access functionality.
"""

import asyncio
import sys
import os
from uuid import uuid4

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from supabase_service_enhanced import SupabaseServiceEnhanced

async def fix_manager_property_assignment():
    """Fix manager property assignment for testing"""
    
    # Initialize Supabase service
    supabase_service = SupabaseServiceEnhanced()
    
    manager_email = "manager@demo.com"
    property_id = "a99239dd-ebde-4c69-b862-ecba9e878798"
    
    try:
        print("🔍 Checking manager and property...")
        
        # Get manager by email
        manager = supabase_service.get_user_by_email_sync(manager_email)
        if not manager:
            print(f"❌ Manager not found: {manager_email}")
            return False
            
        print(f"✅ Found manager: {manager.email} (ID: {manager.id})")
        
        # Check if property exists
        properties_data = await supabase_service.get_all_properties()
        target_property = next((p for p in properties_data if p.get("id") == property_id), None)
        
        if not target_property:
            print(f"❌ Property not found: {property_id}")
            print("Available properties:")
            for prop in properties_data[:3]:  # Show first 3
                print(f"  - {prop.get('name', 'Unknown')} (ID: {prop.get('id')})")
            return False
            
        print(f"✅ Found property: {target_property.get('name')} (ID: {property_id})")
        
        # Check if manager is already assigned to this property
        try:
            existing_assignment = supabase_service.supabase.table("property_managers") \
                .select("*") \
                .eq("manager_id", manager.id) \
                .eq("property_id", property_id) \
                .execute()
                
            if existing_assignment.data:
                print(f"✅ Manager already assigned to property")
                
                # Update user record to include property_id
                update_result = supabase_service.supabase.table("users") \
                    .update({"property_id": property_id}) \
                    .eq("id", manager.id) \
                    .execute()
                    
                if update_result.data:
                    print(f"✅ Updated manager user record with property_id")
                else:
                    print(f"❌ Failed to update manager user record")
                    
                return True
                
        except Exception as e:
            print(f"ℹ️  No existing assignment found: {e}")
        
        # Create property_managers assignment
        try:
            assignment_data = {
                "id": str(uuid4()),
                "manager_id": manager.id,
                "property_id": property_id,
                "assigned_at": "now()",
                "is_active": True
            }
            
            assignment_result = supabase_service.supabase.table("property_managers") \
                .insert(assignment_data) \
                .execute()
                
            if assignment_result.data:
                print(f"✅ Created property_managers assignment")
            else:
                print(f"❌ Failed to create property_managers assignment")
                return False
                
        except Exception as e:
            print(f"⚠️  Property assignment may already exist: {e}")
        
        # Update user record to include property_id
        try:
            update_result = supabase_service.supabase.table("users") \
                .update({"property_id": property_id}) \
                .eq("id", manager.id) \
                .execute()
                
            if update_result.data:
                print(f"✅ Updated manager user record with property_id")
            else:
                print(f"❌ Failed to update manager user record")
                return False
                
        except Exception as e:
            print(f"❌ Error updating manager user record: {e}")
            return False
        
        print("\n🎉 Manager property assignment completed successfully!")
        print(f"Manager: {manager_email}")
        print(f"Property: {target_property.get('name')} ({property_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing manager assignment: {e}")
        return False

def main():
    """Main execution function"""
    print("="*60)
    print("FIXING MANAGER PROPERTY ASSIGNMENT FOR TESTS")
    print("="*60)
    
    result = asyncio.run(fix_manager_property_assignment())
    
    if result:
        print("\n✅ Setup complete! Manager document access tests should now work.")
        sys.exit(0)
    else:
        print("\n❌ Failed to fix manager assignment.")
        sys.exit(1)

if __name__ == "__main__":
    main()