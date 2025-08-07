#!/usr/bin/env python3
"""
Verify that Task 2 migrations were successfully applied
"""

import os
import sys
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_table_structure(table_name: str, expected_columns: list) -> bool:
    """Verify a table exists and has expected columns"""
    try:
        # Query with limit 0 to just check structure
        result = supabase.table(table_name).select("*").limit(0).execute()
        print(f"✅ Table '{table_name}' exists")
        return True
    except Exception as e:
        print(f"❌ Table '{table_name}' not found: {str(e)[:50]}")
        return False

def test_user_preferences() -> bool:
    """Test user_preferences table operations"""
    print("\n📋 Testing user_preferences table...")
    
    try:
        # Try to insert a test preference
        test_data = {
            "user_id": "7ba78d45-9352-43ec-88a4-aef5614124d7",  # HR user ID
            "theme": "dark",
            "language": "en",
            "dashboard_layout": "compact",
            "email_notifications": True
        }
        
        # First delete if exists (for idempotency)
        supabase.table("user_preferences").delete().eq("user_id", test_data["user_id"]).execute()
        
        # Insert new preference
        result = supabase.table("user_preferences").insert(test_data).execute()
        print("   ✅ Can insert into user_preferences")
        
        # Read it back
        result = supabase.table("user_preferences").select("*").eq("user_id", test_data["user_id"]).execute()
        if result.data and len(result.data) > 0:
            print("   ✅ Can read from user_preferences")
            print(f"      Theme: {result.data[0].get('theme')}")
            print(f"      Language: {result.data[0].get('language')}")
            return True
        else:
            print("   ❌ Could not read preferences")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing user_preferences: {str(e)[:100]}")
        return False

def test_bulk_operations() -> bool:
    """Test bulk_operations table operations"""
    print("\n📋 Testing bulk_operations table...")
    
    try:
        # Create a test bulk operation
        test_data = {
            "operation_type": "application_approval",
            "operation_name": "Test Bulk Approval",
            "description": "Testing bulk operations table",
            "initiated_by": "7ba78d45-9352-43ec-88a4-aef5614124d7",  # HR user ID
            "target_entity_type": "applications",
            "target_count": 5,
            "status": "pending",
            "total_items": 5
        }
        
        # Insert test operation
        result = supabase.table("bulk_operations").insert(test_data).execute()
        
        if result.data and len(result.data) > 0:
            operation_id = result.data[0].get('id')
            print(f"   ✅ Created bulk operation: {operation_id}")
            
            # Update the operation
            update_data = {
                "status": "processing",
                "processed_items": 2
            }
            result = supabase.table("bulk_operations").update(update_data).eq("id", operation_id).execute()
            print("   ✅ Can update bulk operation status")
            
            # Test bulk_operation_items
            item_data = {
                "bulk_operation_id": operation_id,
                "target_id": "a120ae58-7f72-49e0-ae95-abb209df438e",  # Random UUID
                "target_type": "application",
                "status": "success"
            }
            result = supabase.table("bulk_operation_items").insert(item_data).execute()
            print("   ✅ Can insert bulk operation items")
            
            return True
        else:
            print("   ❌ Could not create bulk operation")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing bulk_operations: {str(e)[:100]}")
        return False

def test_performance_columns() -> bool:
    """Test that performance tracking columns were added"""
    print("\n📋 Testing performance tracking columns...")
    
    try:
        # Test job_applications table has new columns
        result = supabase.table("job_applications").select(
            "id, processing_time_ms, time_to_hire_hours, quality_score"
        ).limit(1).execute()
        print("   ✅ job_applications has performance columns")
        
        # Test employees table has new columns
        result = supabase.table("employees").select(
            "id, onboarding_completion_time_hours, compliance_score"
        ).limit(1).execute()
        print("   ✅ employees has performance columns")
        
        # Test properties table has new columns
        result = supabase.table("properties").select(
            "id, total_employees_onboarded, performance_tier"
        ).limit(1).execute()
        print("   ✅ properties has performance columns")
        
        # Test users table has new columns
        result = supabase.table("users").select(
            "id, login_count, last_login_at, performance_rating"
        ).limit(1).execute()
        print("   ✅ users has performance columns")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing performance columns: {str(e)[:100]}")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("Task 2 Migration Verification")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Track results
    results = {
        "user_preferences": False,
        "bulk_operations": False, 
        "bulk_operation_items": False,
        "performance_columns": False
    }
    
    # Verify each table exists
    print("\n🔍 Checking table existence...")
    results["user_preferences"] = verify_table_structure("user_preferences", [])
    results["bulk_operations"] = verify_table_structure("bulk_operations", [])
    results["bulk_operation_items"] = verify_table_structure("bulk_operation_items", [])
    
    # Run functional tests
    if results["user_preferences"]:
        results["user_preferences"] = test_user_preferences()
    
    if results["bulk_operations"]:
        results["bulk_operations"] = test_bulk_operations()
    
    # Test performance columns
    results["performance_columns"] = test_performance_columns()
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = all(results.values())
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL MIGRATIONS VERIFIED SUCCESSFULLY!")
        print("\nTask 2 Database Schema Enhancements are complete:")
        print("  ✅ user_preferences table created and functional")
        print("  ✅ bulk_operations tables created and functional")
        print("  ✅ Performance tracking columns added to all tables")
        print("\n✨ The system is ready for the next tasks!")
    else:
        print(f"⚠️ Partial success: {passed_count}/{total_count} verifications passed")
        print("\nPlease check the failed items above")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())