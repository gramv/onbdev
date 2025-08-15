#!/usr/bin/env python3
"""
Setup Test Database with Initial Data
After running disable_test_rls.sql, use this to create test data
"""
import os
import sys
import hashlib
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

if 'kzommszdhapvqpekpvnt' not in url:
    print("ERROR: This script is for TEST database only!")
    print(f"Current URL: {url}")
    sys.exit(1)

print(f"Setting up TEST database: {url}")
print("=" * 60)

# Create Supabase client
client = create_client(url, key)

# Test data configuration
PROPERTY_ID = 'a99239dd-ebde-4c69-b862-ecba9e878798'
MANAGER_EMAIL = 'manager@demo.com'
MANAGER_PASSWORD = 'demo123'

def hash_password(password: str) -> str:
    """Simple password hashing for test environment"""
    # For test environment, using simple SHA256
    # Production should use bcrypt or similar
    return hashlib.sha256(password.encode()).hexdigest()

def setup_test_data():
    """Setup all test data"""
    
    print("\n1. Creating test property...")
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
        # Try to insert property
        result = client.table('properties').insert(property_data).execute()
        print(f"   ✅ Property created: Demo Hotel")
    except Exception as e:
        if "duplicate" in str(e).lower():
            print(f"   ℹ️  Property already exists")
            # Update existing property
            try:
                client.table('properties').update({
                    "is_active": True,
                    "updated_at": datetime.now().isoformat()
                }).eq('id', PROPERTY_ID).execute()
                print(f"   ✅ Property updated")
            except:
                pass
        else:
            print(f"   ❌ Error: {e}")
    
    print("\n2. Creating manager account...")
    manager_id = str(uuid.uuid4())
    manager_data = {
        "id": manager_id,
        "email": MANAGER_EMAIL,
        "role": "manager",
        "first_name": "Demo",
        "last_name": "Manager",
        "property_id": PROPERTY_ID,
        "password_hash": hash_password(MANAGER_PASSWORD),
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        # Check if manager exists
        existing = client.table('users').select('id').eq('email', MANAGER_EMAIL).execute()
        
        if existing.data:
            # Update existing manager
            manager_id = existing.data[0]['id']
            client.table('users').update({
                "property_id": PROPERTY_ID,
                "password_hash": hash_password(MANAGER_PASSWORD),
                "is_active": True,
                "updated_at": datetime.now().isoformat()
            }).eq('id', manager_id).execute()
            print(f"   ✅ Manager updated: {MANAGER_EMAIL}")
        else:
            # Create new manager
            result = client.table('users').insert(manager_data).execute()
            print(f"   ✅ Manager created: {MANAGER_EMAIL}")
    except Exception as e:
        print(f"   ❌ Manager error: {e}")
        return False
    
    print("\n3. Creating property_managers assignment...")
    try:
        # Check if assignment exists
        existing_assignment = client.table('property_managers').select('id').eq('manager_id', manager_id).eq('property_id', PROPERTY_ID).execute()
        
        if not existing_assignment.data:
            assignment_data = {
                "id": str(uuid.uuid4()),
                "manager_id": manager_id,
                "property_id": PROPERTY_ID,
                "assigned_at": datetime.now().isoformat(),
                "is_active": True
            }
            client.table('property_managers').insert(assignment_data).execute()
            print(f"   ✅ Manager assigned to property")
        else:
            print(f"   ℹ️  Manager already assigned to property")
    except Exception as e:
        print(f"   ⚠️  Assignment error (may already exist): {e}")
    
    print("\n4. Creating additional test users...")
    
    # Create HR user
    hr_data = {
        "id": str(uuid.uuid4()),
        "email": "hr@demo.com",
        "role": "hr",
        "first_name": "HR",
        "last_name": "Admin",
        "password_hash": hash_password("hr123"),
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    try:
        existing_hr = client.table('users').select('id').eq('email', 'hr@demo.com').execute()
        if not existing_hr.data:
            client.table('users').insert(hr_data).execute()
            print(f"   ✅ HR user created: hr@demo.com / hr123")
        else:
            print(f"   ℹ️  HR user already exists")
    except Exception as e:
        print(f"   ⚠️  HR user error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ TEST DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print("\nYou can now login with:")
    print(f"  Manager: {MANAGER_EMAIL} / {MANAGER_PASSWORD}")
    print(f"  HR: hr@demo.com / hr123")
    print(f"\nProperty: Demo Hotel (ID: {PROPERTY_ID})")
    print("\nFrontend URL: http://localhost:3000/manager")
    
    return True

if __name__ == "__main__":
    try:
        success = setup_test_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nMake sure you've run disable_test_rls.sql first!")
        sys.exit(1)