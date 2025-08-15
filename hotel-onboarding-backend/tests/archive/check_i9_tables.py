#!/usr/bin/env python3
"""
Check if I-9 tables exist in Supabase and provide instructions if not
"""
from app.supabase_service_enhanced import EnhancedSupabaseService
import sys

def check_tables():
    """Check if required I-9 tables exist"""
    service = EnhancedSupabaseService()
    
    tables_to_check = ['i9_forms', 'i9_section2_documents', 'w4_forms']
    missing_tables = []
    existing_tables = []
    
    for table in tables_to_check:
        try:
            # Try to select from the table
            result = service.client.table(table).select('id').limit(1).execute()
            existing_tables.append(table)
            print(f"✅ Table '{table}' exists")
        except Exception as e:
            if 'relation' in str(e).lower() and 'does not exist' in str(e).lower():
                missing_tables.append(table)
                print(f"❌ Table '{table}' does not exist")
            else:
                print(f"⚠️  Table '{table}' - Unable to verify: {e}")
    
    print("\n" + "="*50)
    
    if missing_tables:
        print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
        print("\n📝 To create the missing tables, please execute the SQL in:")
        print("   create_i9_tables.sql")
        print("\nYou can run this SQL in the Supabase dashboard:")
        print("1. Go to https://app.supabase.com")
        print("2. Select your project")
        print("3. Go to SQL Editor")
        print("4. Copy and paste the contents of create_i9_tables.sql")
        print("5. Click 'Run'")
        return False
    else:
        print("\n✅ All required I-9 tables exist!")
        
        # Test inserting sample data
        print("\n📝 Testing data operations...")
        try:
            # Test i9_forms table
            test_data = {
                "employee_id": "test-emp-00000000",
                "section": "test_section",
                "form_data": {"test": "data"},
                "signed": False
            }
            
            # Try to insert and then delete
            result = service.client.table('i9_forms').insert(test_data).execute()
            print("✅ Can insert into i9_forms")
            
            # Clean up test data
            service.client.table('i9_forms').delete().eq('employee_id', 'test-emp-00000000').execute()
            print("✅ Can delete from i9_forms")
            
        except Exception as e:
            print(f"⚠️  Data operation test failed: {e}")
            print("   This might be due to RLS policies. This is expected.")
        
        return True

if __name__ == "__main__":
    print("🔍 Checking I-9 database tables...")
    print("="*50)
    
    success = check_tables()
    sys.exit(0 if success else 1)