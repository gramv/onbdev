#!/usr/bin/env python3
"""
Simple Test Data Setup for Test Database
Creates minimal test data using actual column names from test DB
"""
import os
import sys
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

def main():
    """Setup test data with simple approach"""
    
    # Step 1: Create property
    print("\n1. Creating test property...")
    property_data = {
        "name": "Demo Hotel",
        "address": "123 Demo Street",
        "city": "Demo City",
        "state": "CA",
        "zip_code": "90210",
        "phone": "(555) 123-4567",
        "is_active": True
    }
    
    try:
        result = client.table('properties').insert(property_data).execute()
        if result.data:
            property_id = result.data[0]['id']
            print(f"   ✅ Property created: Demo Hotel (ID: {property_id})")
        else:
            print("   ❌ Failed to create property")
            return
    except Exception as e:
        print(f"   ❌ Error creating property: {e}")
        # Try to get existing Demo Hotel
        try:
            existing = client.table('properties').select('*').eq('name', 'Demo Hotel').execute()
            if existing.data:
                property_id = existing.data[0]['id']
                print(f"   ℹ️  Using existing Demo Hotel (ID: {property_id})")
            else:
                print("   ❌ Could not find or create Demo Hotel")
                return
        except Exception as e2:
            print(f"   ❌ Failed to check for existing property: {e2}")
            return
    
    # Step 2: Create manager user
    print("\n2. Creating manager account...")
    
    # Simple password hash (SHA256 for test environment)
    password = "demo123"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    manager_data = {
        "email": "manager@demo.com",
        "role": "manager",
        "first_name": "Demo",
        "last_name": "Manager",
        "property_id": property_id,
        "is_active": True
    }
    
    # Try different password column names
    password_columns = ['password_hash', 'password', 'encrypted_password']
    
    for col in password_columns:
        try:
            manager_data[col] = password_hash
            result = client.table('users').insert(manager_data).execute()
            if result.data:
                manager_id = result.data[0]['id']
                print(f"   ✅ Manager created: manager@demo.com (ID: {manager_id})")
                print(f"   ℹ️  Password column used: {col}")
                break
            del manager_data[col]
        except Exception as e:
            if col in str(e):
                del manager_data[col]
                continue
            # Check if user exists
            try:
                existing = client.table('users').select('*').eq('email', 'manager@demo.com').execute()
                if existing.data:
                    manager_id = existing.data[0]['id']
                    print(f"   ℹ️  Manager already exists (ID: {manager_id})")
                    
                    # Update property_id
                    try:
                        client.table('users').update({'property_id': property_id}).eq('id', manager_id).execute()
                        print(f"   ✅ Updated manager's property assignment")
                    except:
                        pass
                    break
            except:
                pass
    
    # Step 3: Create property_managers assignment
    print("\n3. Creating property_managers assignment...")
    if 'manager_id' in locals():
        try:
            assignment_data = {
                "manager_id": manager_id,
                "property_id": property_id,
                "is_active": True
            }
            result = client.table('property_managers').insert(assignment_data).execute()
            print(f"   ✅ Manager assigned to property")
        except Exception as e:
            if "duplicate" in str(e).lower():
                print(f"   ℹ️  Assignment already exists")
            else:
                print(f"   ⚠️  Could not create assignment: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ TEST DATA SETUP COMPLETE!")
    print("=" * 60)
    print(f"\nProperty: Demo Hotel")
    if 'property_id' in locals():
        print(f"Property ID: {property_id}")
    print(f"\nManager Login:")
    print(f"  Email: manager@demo.com")
    print(f"  Password: demo123")
    print(f"\nFrontend URL: http://localhost:3000/manager")
    print("\nNote: Password authentication may need to be configured")
    print("in your backend auth.py to match the test DB schema.")

if __name__ == "__main__":
    main()