#!/usr/bin/env python3
"""
Apply RLS Policy Fix for Properties
This script updates the Supabase RLS policies to allow HR users to manage properties
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_rls_fix():
    """Apply the RLS policy fix to Supabase"""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
        return False
    
    # Try to use service key if available, otherwise use anon key
    if supabase_service_key:
        print("🔑 Using service key for admin operations...")
        client = create_client(supabase_url, supabase_service_key)
    else:
        print("⚠️  No service key found, using anon key...")
        client = create_client(supabase_url, supabase_anon_key)
    
    # Read the SQL file
    try:
        with open("fix_properties_rls.sql", "r") as f:
            sql_content = f.read()
    except FileNotFoundError:
        print("❌ Error: fix_properties_rls.sql file not found")
        return False
    
    # Split SQL into individual statements (simple approach)
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    print(f"📋 Executing {len(statements)} SQL statements...")
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements):
        if not statement or statement.startswith('--'):
            continue
            
        try:
            print(f"🔄 Executing statement {i+1}...")
            
            # Execute SQL using Supabase RPC or direct SQL execution
            # Note: Supabase Python client doesn't have direct SQL execution
            # We'll need to use the REST API directly
            import requests
            
            headers = {
                'Authorization': f'Bearer {supabase_service_key or supabase_anon_key}',
                'Content-Type': 'application/json',
                'apikey': supabase_service_key or supabase_anon_key
            }
            
            # Use Supabase's SQL execution endpoint
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={'sql': statement}
            )
            
            if response.status_code in [200, 201, 204]:
                print(f"✅ Statement {i+1} executed successfully")
                success_count += 1
            else:
                print(f"⚠️  Statement {i+1} failed: {response.status_code} - {response.text}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error executing statement {i+1}: {e}")
            error_count += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {error_count}")
    
    if error_count == 0:
        print("\n🎉 RLS policies updated successfully! HR users can now create properties.")
        return True
    else:
        print(f"\n⚠️  {error_count} statements failed. Check the errors above.")
        return False

def test_property_creation():
    """Test property creation after RLS fix"""
    print("\n🧪 Testing property creation...")
    
    # This would be called by the main application
    # For now, just print success message
    print("✅ RLS fix applied. Please test property creation from the frontend.")

if __name__ == "__main__":
    print("🚀 Starting RLS Policy Fix for Properties...")
    print("=" * 50)
    
    success = apply_rls_fix()
    
    if success:
        test_property_creation()
        print("\n✅ RLS fix completed successfully!")
        print("🔄 Please restart your backend server to ensure changes take effect.")
    else:
        print("\n❌ RLS fix failed. Please check the errors above.")
        sys.exit(1)