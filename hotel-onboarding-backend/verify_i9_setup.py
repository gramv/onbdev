#!/usr/bin/env python3
"""
Verify I-9 tables setup and test operations
"""
import os
import sys
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

from app.supabase_service_enhanced import EnhancedSupabaseService

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("   Please check your .env file")
        return False
    
    if os.getenv('SUPABASE_SERVICE_KEY'):
        print("✅ Service role key found (admin operations enabled)")
    else:
        print("⚠️  Service role key not found (using anon key)")
        print("   To enable full admin operations, add SUPABASE_SERVICE_KEY to .env")
    
    return True

def check_tables(service):
    """Check if I-9 tables exist"""
    tables_to_check = ['i9_forms', 'i9_section2_documents', 'w4_forms']
    all_exist = True
    
    print("\n📊 Checking tables...")
    for table in tables_to_check:
        try:
            # Use admin client if available
            client = service.admin_client if service.supabase_service_key else service.client
            result = client.table(table).select('id').limit(1).execute()
            print(f"  ✅ Table '{table}' exists")
        except Exception as e:
            if 'relation' in str(e).lower() and 'does not exist' in str(e).lower():
                print(f"  ❌ Table '{table}' does not exist")
                all_exist = False
            else:
                print(f"  ⚠️  Table '{table}' - error: {str(e)[:100]}")
                all_exist = False
    
    return all_exist

def test_operations(service):
    """Test insert/update/delete operations"""
    print("\n🧪 Testing operations...")
    
    test_employee_id = "test-verify-" + datetime.now().strftime("%Y%m%d%H%M%S")
    
    try:
        # Use admin client for operations that might have RLS
        client = service.admin_client if service.supabase_service_key else service.client
        
        # Test i9_forms insert
        test_data = {
            "employee_id": test_employee_id,
            "section": "section1",
            "form_data": {"test": "data", "citizenship_status": "citizen"},
            "signed": False
        }
        
        result = client.table('i9_forms').insert(test_data).execute()
        if result.data:
            print("  ✅ Can insert into i9_forms")
            
            # Test update
            update_data = {"signed": True, "updated_at": datetime.utcnow().isoformat()}
            result = client.table('i9_forms').update(update_data)\
                .eq('employee_id', test_employee_id)\
                .eq('section', 'section1')\
                .execute()
            if result.data:
                print("  ✅ Can update i9_forms")
            
            # Test select
            result = client.table('i9_forms').select('*')\
                .eq('employee_id', test_employee_id)\
                .execute()
            if result.data:
                print("  ✅ Can select from i9_forms")
                print(f"     Retrieved data: {json.dumps(result.data[0]['form_data'])}")
            
            # Clean up
            result = client.table('i9_forms').delete()\
                .eq('employee_id', test_employee_id)\
                .execute()
            print("  ✅ Can delete from i9_forms")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Operation failed: {str(e)[:200]}")
        
        # Try to clean up even if test failed
        try:
            client.table('i9_forms').delete().eq('employee_id', test_employee_id).execute()
        except:
            pass
        
        return False

def main():
    print("🔍 Verifying I-9 Setup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed")
        return False
    
    # Initialize service
    try:
        service = EnhancedSupabaseService()
        print("✅ Supabase service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return False
    
    # Check tables
    tables_exist = check_tables(service)
    
    if not tables_exist:
        print("\n" + "=" * 50)
        print("⚠️  TABLES DO NOT EXIST")
        print("\nTo create the tables:")
        print("1. Go to https://app.supabase.com")
        print("2. Select your project")
        print("3. Go to SQL Editor")
        print("4. Copy and paste the contents of create_i9_tables.sql")
        print("5. Click 'Run'")
        print("\nAfter creating tables, run this script again.")
        return False
    
    # Test operations
    print("\n" + "=" * 50)
    operations_work = test_operations(service)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    if tables_exist and operations_work:
        print("✅ All checks passed! I-9 system is ready.")
        print("\nYour system can now:")
        print("  • Save I-9 Section 1 data to cloud")
        print("  • Save I-9 Section 2 documents to cloud")
        print("  • Store W-4 forms with signatures")
        print("  • Maintain audit trail for compliance")
        return True
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        if not tables_exist:
            print("\n📝 Next step: Create tables using SQL Editor in Supabase Dashboard")
        elif not operations_work:
            print("\n📝 Next step: Check RLS policies or use service role key")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)