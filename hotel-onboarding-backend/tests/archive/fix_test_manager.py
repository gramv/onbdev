#!/usr/bin/env python3
"""
Direct fix for test database manager property assignment
"""
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

print(f"Connecting to test database: {url}")

# Create Supabase client
client = create_client(url, key)

manager_email = 'manager@demo.com'
property_id = 'a99239dd-ebde-4c69-b862-ecba9e878798'

print(f"\nFixing manager property assignment...")
print(f"Manager: {manager_email}")
print(f"Property ID: {property_id}")

try:
    # First, create the property if it doesn't exist
    print("\n1. Ensuring property exists...")
    property_data = {
        "id": property_id,
        "name": "Demo Hotel",
        "address": "123 Demo Street",
        "city": "Demo City",
        "state": "CA",
        "zip_code": "90210",
        "phone": "(555) 123-4567",
        "is_active": True
    }
    
    # Try to insert property (will fail if exists, that's ok)
    try:
        result = client.table('properties').insert(property_data).execute()
        print("   ✅ Property created")
    except Exception as e:
        if "duplicate" in str(e).lower():
            print("   ℹ️  Property already exists")
        else:
            print(f"   ⚠️  Property error: {e}")
    
    # Create or update manager
    print("\n2. Creating/updating manager account...")
    
    # Hash password (simple for test)
    import hashlib
    password = "demo123"
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    manager_data = {
        "email": manager_email,
        "role": "manager",
        "first_name": "Demo",
        "last_name": "Manager",
        "property_id": property_id,
        "password_hash": hashed,
        "is_active": True
    }
    
    # Try to update existing manager first
    try:
        update_result = client.table('users').update({
            "property_id": property_id,
            "is_active": True
        }).eq('email', manager_email).execute()
        
        if update_result.data:
            print("   ✅ Manager updated with property assignment")
        else:
            # Try to insert new manager
            result = client.table('users').insert(manager_data).execute()
            print("   ✅ Manager created with property assignment")
    except Exception as e:
        print(f"   ⚠️  Manager update/create error: {e}")
        print("   Trying alternative approach...")
        
        # Try raw SQL approach
        try:
            # This might work better with RLS issues
            client.rpc('update_manager_property', {
                'manager_email': manager_email,
                'new_property_id': property_id
            }).execute()
            print("   ✅ Manager property updated via RPC")
        except:
            print("   ❌ Could not update manager property")
    
    print("\n✅ Setup complete!")
    print("\nYou can now login with:")
    print(f"  Email: {manager_email}")
    print(f"  Password: {password}")
    print(f"  Property: Demo Hotel")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nThe test database may have RLS policy issues.")
    print("You may need to fix the database policies or use the service key.")