#!/usr/bin/env python3
"""
Fix manager property assignment using service role key
This bypasses RLS policies to directly assign managers to properties
"""

import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
# Try different possible key names
service_key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or 
               os.getenv("SUPABASE_SERVICE_KEY") or 
               os.getenv("SUPABASE_KEY") or 
               os.getenv("SUPABASE_ANON_KEY"))

if not url or not service_key:
    print("Error: Missing SUPABASE_URL or SUPABASE key in .env file")
    print(f"URL found: {bool(url)}")
    print(f"Key found: {bool(service_key)}")
    sys.exit(1)

# Create Supabase client with service role
supabase: Client = create_client(url, service_key)

def assign_manager_to_property(manager_id: str, property_id: str):
    """Assign a manager to a property, bypassing RLS"""
    try:
        # First, check if assignment already exists
        existing = supabase.table('property_managers').select('*').eq(
            'manager_id', manager_id
        ).eq('property_id', property_id).execute()
        
        if existing.data:
            print(f"✓ Assignment already exists for manager {manager_id} to property {property_id}")
            return True
        
        # Remove any existing assignments for this manager
        print(f"Removing existing assignments for manager {manager_id}...")
        supabase.table('property_managers').delete().eq('manager_id', manager_id).execute()
        
        # Create new assignment
        assignment_data = {
            "manager_id": manager_id,
            "property_id": property_id,
            "assigned_at": datetime.now(timezone.utc).isoformat()
        }
        
        print(f"Creating new assignment...")
        result = supabase.table('property_managers').insert(assignment_data).execute()
        
        if result.data:
            print(f"✓ Successfully assigned manager {manager_id} to property {property_id}")
            return True
        else:
            print(f"✗ Failed to create assignment - no data returned")
            return False
            
    except Exception as e:
        print(f"✗ Error assigning manager: {e}")
        return False

def get_manager_properties(manager_id: str):
    """Get all properties assigned to a manager"""
    try:
        # Get assignments
        assignments = supabase.table('property_managers').select('*').eq('manager_id', manager_id).execute()
        
        if not assignments.data:
            print(f"No properties assigned to manager {manager_id}")
            return []
        
        # Get property details for each assignment
        properties = []
        for assignment in assignments.data:
            prop = supabase.table('properties').select('*').eq('id', assignment['property_id']).execute()
            if prop.data:
                properties.append(prop.data[0])
        
        return properties
        
    except Exception as e:
        print(f"Error getting manager properties: {e}")
        return []

def main():
    """Main function to test and fix manager assignments"""
    
    # Test managers and properties
    test_cases = [
        {
            "manager_id": "59356bfe-9c80-4871-81e5-2fa4496b5781",  # Demo Manager
            "property_id": "b1d60a13-ba0d-45bd-b709-87076abc64dc",  # Grand Plaza Hotel
            "manager_name": "Demo Manager"
        },
        {
            "manager_id": "959a01a6-6bb1-4bbb-a779-acaff92518f4",  # Goutham
            "property_id": "550e8400-e29b-41d4-a716-446655440003",  # Test Hotel
            "manager_name": "Goutham"
        }
    ]
    
    print("=" * 60)
    print("Manager Property Assignment Fix Script")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\nProcessing {test['manager_name']}...")
        
        # Assign manager to property
        success = assign_manager_to_property(test['manager_id'], test['property_id'])
        
        if success:
            # Verify assignment
            properties = get_manager_properties(test['manager_id'])
            if properties:
                print(f"✓ Verified: Manager now assigned to {len(properties)} property(ies):")
                for prop in properties:
                    print(f"  - {prop['name']} ({prop['city']}, {prop['state']})")
            else:
                print("⚠ Warning: Assignment created but not showing in properties list")
    
    print("\n" + "=" * 60)
    print("Script completed. Please refresh your dashboard to see changes.")
    print("=" * 60)

if __name__ == "__main__":
    main()