#!/usr/bin/env python3
"""
Setup test accounts for CHECKPOINT Beta testing
"""

import os
import sys
import uuid
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv(".env")
load_dotenv(".env.local", override=True)

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Missing SUPABASE_URL or SUPABASE_KEY")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def setup_test_data():
    """Setup test accounts and data"""
    print("Setting up test accounts for CHECKPOINT Beta...")
    
    try:
        # Use a fixed UUID for test property
        test_property_id = "903ed05b-5990-4ecf-b1b2-7592cf2923df"  # Fixed UUID for testing
        
        # 1. Check/Create test property
        print("\n1. Checking for test property...")
        properties = supabase.table("properties").select("*").eq("id", test_property_id).execute()
        
        if not properties.data:
            print("   Creating test property...")
            property_data = {
                "id": test_property_id,
                "name": "Demo Hotel",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "TS",
                "zip_code": "12345",
                "phone": "555-0100",
                "created_at": datetime.now().isoformat()
            }
            supabase.table("properties").insert(property_data).execute()
            print(f"   ✅ Test property created (ID: {test_property_id})")
        else:
            print(f"   ✅ Test property already exists (ID: {test_property_id})")
            
        # 2. Check/Create manager account
        print("\n2. Checking for manager account...")
        managers = supabase.table("users").select("*").eq("email", "manager@demo.com").execute()
        
        if not managers.data:
            print("   Creating manager account...")
            manager_data = {
                "email": "manager@demo.com",
                "password_hash": hash_password("password123"),
                "role": "manager",
                "first_name": "John",
                "last_name": "Manager",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
            manager_result = supabase.table("users").insert(manager_data).execute()
            manager_id = manager_result.data[0]["id"]
            print(f"   ✅ Manager account created (ID: {manager_id})")
            
            # Assign manager to property
            print("   Assigning manager to property...")
            assignment_data = {
                "property_id": test_property_id,
                "manager_id": manager_id,
                "created_at": datetime.now().isoformat()
            }
            supabase.table("property_managers").insert(assignment_data).execute()
            print("   ✅ Manager assigned to property")
        else:
            manager_id = managers.data[0]["id"]
            print(f"   ✅ Manager account already exists (ID: {manager_id})")
            
            # Check property assignment
            assignments = supabase.table("property_managers").select("*").eq("manager_id", manager_id).execute()
            if not assignments.data:
                print("   Assigning manager to property...")
                assignment_data = {
                    "property_id": test_property_id,
                    "manager_id": manager_id,
                    "created_at": datetime.now().isoformat()
                }
                supabase.table("property_managers").insert(assignment_data).execute()
                print("   ✅ Manager assigned to property")
                
        # 3. Create a pending application for testing
        print("\n3. Creating test application...")
        app_data = {
            "property_id": test_property_id,
            "first_name": "Jane",
            "last_name": "Doe",
            "applicant_email": "jane.doe@example.com",
            "applicant_phone": "555-0123",
            "position": "Front Desk Agent",
            "department": "Front Office",
            "availability": {
                "start_date": "2025-08-22",
                "shift_preference": "morning",
                "full_time": True
            },
            "experience": {
                "years": 3,
                "previous_role": "Receptionist",
                "skills": ["Customer Service", "MS Office", "PMS Systems"]
            },
            "legal_authorization": True,
            "background_check_consent": True,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        # Check if similar application exists
        existing = supabase.table("job_applications").select("*").eq("applicant_email", "jane.doe@example.com").eq("status", "pending").execute()
        
        if not existing.data:
            app_result = supabase.table("job_applications").insert(app_data).execute()
            print(f"   ✅ Test application created (ID: {app_result.data[0]['id']})")
        else:
            print(f"   ✅ Test application already exists (ID: {existing.data[0]['id']})")
            
        # 4. Display test credentials
        print("\n" + "="*50)
        print(" TEST CREDENTIALS")
        print("="*50)
        print("Manager Login:")
        print("  Email: manager@demo.com")
        print("  Password: password123")
        print(f"\nProperty ID: {test_property_id}")
        print("\n✅ Test data setup complete!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up test data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_test_data()
    sys.exit(0 if success else 1)