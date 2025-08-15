#!/usr/bin/env python3
"""
Minimal Test Setup - Direct SQL approach
"""
import os
import sys
import uuid
import hashlib
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

# Verify we're on test database
if 'kzommszdhapvqpekpvnt' not in url:
    print("ERROR: This script is for TEST database only!")
    sys.exit(1)

print(f"Setting up TEST database: {url}")
print("=" * 60)

# Create Supabase client
client = create_client(url, key)

# Fixed IDs for consistency
PROPERTY_ID = 'a99239dd-ebde-4c69-b862-ecba9e878798'
MANAGER_ID = str(uuid.uuid4())

def main():
    """Setup test data"""
    
    # Step 1: Check if property exists
    print("\n1. Checking for existing Demo Hotel...")
    try:
        existing = client.table('properties').select('*').eq('name', 'Demo Hotel').execute()
        if existing.data:
            property_id = existing.data[0]['id']
            print(f"   ✅ Found existing Demo Hotel (ID: {property_id})")
        else:
            print("   ℹ️  Demo Hotel not found, will try to create")
            
            # Try creating with explicit ID
            property_data = {
                "id": PROPERTY_ID,
                "name": "Demo Hotel",
                "address": "123 Demo Street",
                "city": "Demo City",
                "state": "CA",
                "zip_code": "90210",
                "phone": "(555) 123-4567",
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            try:
                result = client.table('properties').insert(property_data).execute()
                if result.data:
                    property_id = PROPERTY_ID
                    print(f"   ✅ Created Demo Hotel (ID: {property_id})")
                else:
                    print("   ❌ Failed to create property")
                    property_id = None
            except Exception as e:
                print(f"   ❌ Error creating property: {e}")
                property_id = None
    except Exception as e:
        print(f"   ❌ Error checking properties: {e}")
        property_id = None
    
    # Step 2: Create or update manager
    print("\n2. Setting up manager account...")
    try:
        # Check if manager exists
        existing = client.table('users').select('*').eq('email', 'manager@demo.com').execute()
        
        if existing.data:
            manager_id = existing.data[0]['id']
            print(f"   ℹ️  Found existing manager (ID: {manager_id})")
            
            # Update property assignment if we have a property
            if property_id:
                try:
                    client.table('users').update({
                        'property_id': property_id,
                        'is_active': True
                    }).eq('id', manager_id).execute()
                    print(f"   ✅ Updated manager's property assignment")
                except Exception as e:
                    print(f"   ⚠️  Could not update manager: {e}")
        else:
            # Create new manager
            manager_data = {
                "id": MANAGER_ID,
                "email": "manager@demo.com",
                "first_name": "Demo",
                "last_name": "Manager",
                "role": "manager",
                "property_id": property_id if property_id else None,
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            try:
                result = client.table('users').insert(manager_data).execute()
                if result.data:
                    manager_id = MANAGER_ID
                    print(f"   ✅ Created manager account (ID: {manager_id})")
                else:
                    print("   ❌ Failed to create manager")
                    manager_id = None
            except Exception as e:
                print(f"   ❌ Error creating manager: {e}")
                manager_id = None
                
    except Exception as e:
        print(f"   ❌ Error with manager setup: {e}")
        manager_id = None
    
    # Step 3: Create property_managers link if both exist
    if property_id and manager_id:
        print("\n3. Linking manager to property...")
        try:
            # Check if link exists
            existing = client.table('property_managers').select('*').eq('manager_id', manager_id).eq('property_id', property_id).execute()
            
            if existing.data:
                print(f"   ℹ️  Link already exists")
            else:
                link_data = {
                    "manager_id": manager_id,
                    "property_id": property_id,
                    "assigned_at": datetime.now().isoformat()
                }
                
                result = client.table('property_managers').insert(link_data).execute()
                if result.data:
                    print(f"   ✅ Manager linked to property")
                else:
                    print(f"   ⚠️  Could not create link")
        except Exception as e:
            print(f"   ⚠️  Error creating link: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if property_id and manager_id:
        print("✅ TEST DATA SETUP COMPLETE!")
        print("=" * 60)
        print(f"\nProperty: Demo Hotel")
        print(f"Property ID: {property_id}")
        print(f"\nManager: manager@demo.com")
        print(f"Manager ID: {manager_id}")
        print(f"\n⚠️  NOTE: Password authentication not configured")
        print("The manager account exists but password login won't work")
        print("until the password column issue is resolved.")
    else:
        print("⚠️  PARTIAL SETUP")
        print("=" * 60)
        if property_id:
            print(f"Property created: {property_id}")
        if manager_id:
            print(f"Manager created: {manager_id}")
        print("\nSome components could not be created.")
        print("Check the errors above for details.")

if __name__ == "__main__":
    main()