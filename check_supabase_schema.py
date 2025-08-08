#!/usr/bin/env python3
"""
Script to check actual Supabase database schema
"""
import os
import sys
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv('hotel-onboarding-backend/.env')

def check_database_schema():
    """Query Supabase to get actual database schema"""
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Missing Supabase credentials in .env")
        return
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_anon_key)
        
        # Try to query each expected table
        tables_to_check = [
            'users',
            'properties', 
            'property_managers',
            'job_applications',
            'employees',
            'onboarding_sessions',
            'audit_log',
            'user_roles',
            'user_role_assignments',
            'application_status_history',
            'managers',  # Check if this exists
            'i9_forms',
            'w4_forms',
            'notifications',
            'analytics_events'
        ]
        
        print("\n📊 Checking Database Tables:")
        print("-" * 50)
        
        existing_tables = []
        missing_tables = []
        
        for table in tables_to_check:
            try:
                # Try to query the table (limit 1 to just check existence)
                response = supabase.table(table).select("*").limit(1).execute()
                print(f"✅ Table '{table}' exists")
                existing_tables.append(table)
                
                # Get count if possible
                count_response = supabase.table(table).select("*", count='exact').execute()
                if hasattr(count_response, 'count'):
                    print(f"   → Records: {count_response.count}")
                    
            except Exception as e:
                error_msg = str(e)
                if "relation" in error_msg and "does not exist" in error_msg:
                    print(f"❌ Table '{table}' does not exist")
                    missing_tables.append(table)
                else:
                    print(f"⚠️  Table '{table}' - Error: {error_msg[:100]}")
        
        print("\n📋 Summary:")
        print("-" * 50)
        print(f"Existing tables ({len(existing_tables)}): {', '.join(existing_tables)}")
        print(f"Missing tables ({len(missing_tables)}): {', '.join(missing_tables) if missing_tables else 'None'}")
        
        # Check actual schema of important tables
        print("\n🔍 Checking Table Schemas:")
        print("-" * 50)
        
        # Check users table schema
        if 'users' in existing_tables:
            print("\n📌 Users Table Sample:")
            try:
                sample = supabase.table('users').select("*").limit(1).execute()
                if sample.data:
                    columns = list(sample.data[0].keys())
                    print(f"   Columns: {', '.join(columns)}")
                else:
                    print("   No data to show columns")
            except Exception as e:
                print(f"   Error getting schema: {e}")
        
        # Check properties table schema  
        if 'properties' in existing_tables:
            print("\n📌 Properties Table Sample:")
            try:
                sample = supabase.table('properties').select("*").limit(1).execute()
                if sample.data:
                    columns = list(sample.data[0].keys())
                    print(f"   Columns: {', '.join(columns)}")
                    print(f"   Sample: {json.dumps(sample.data[0], indent=2, default=str)[:500]}")
                else:
                    print("   No data to show columns")
            except Exception as e:
                print(f"   Error getting schema: {e}")
                
        # Check if managers is a separate table or part of users
        if 'managers' in existing_tables:
            print("\n📌 Managers Table Sample:")
            try:
                sample = supabase.table('managers').select("*").limit(1).execute()
                if sample.data:
                    columns = list(sample.data[0].keys())
                    print(f"   Columns: {', '.join(columns)}")
            except Exception as e:
                print(f"   Error: {e}")
        elif 'property_managers' in existing_tables:
            print("\n📌 Property Managers Table (linking table):")
            try:
                sample = supabase.table('property_managers').select("*").limit(1).execute()
                if sample.data:
                    columns = list(sample.data[0].keys())
                    print(f"   Columns: {', '.join(columns)}")
                    print("   → This appears to be a linking table between users and properties")
            except Exception as e:
                print(f"   Error: {e}")
                
        # Check for any HR users
        print("\n👥 Checking for HR Users:")
        try:
            hr_users = supabase.table('users').select("*").eq('role', 'hr').execute()
            print(f"   Found {len(hr_users.data)} HR users")
            if hr_users.data:
                for user in hr_users.data[:3]:  # Show first 3
                    print(f"   - {user.get('email', 'N/A')} (ID: {user.get('id', 'N/A')})")
        except Exception as e:
            print(f"   Error checking HR users: {e}")
            
        # Check for properties
        print("\n🏢 Checking Properties:")
        try:
            properties = supabase.table('properties').select("*").execute()
            print(f"   Found {len(properties.data)} properties")
            if properties.data:
                for prop in properties.data[:3]:  # Show first 3
                    print(f"   - {prop.get('name', 'N/A')} (ID: {prop.get('id', 'N/A')})")
        except Exception as e:
            print(f"   Error checking properties: {e}")
            
    except Exception as e:
        print(f"\n❌ Connection Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_schema()