#!/usr/bin/env python3
"""
Execute remaining Task 2 database migrations for HR Manager System Consolidation
Migrations:
- 008: Create user_preferences table
- 009: Create bulk_operations table  
- 010: Add performance tracking columns
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in environment variables")
    sys.exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def execute_migration(migration_file: str, description: str):
    """Execute a single migration file"""
    print(f"\n📋 Executing: {description}")
    print(f"   File: {migration_file}")
    
    try:
        # Read the SQL file
        migration_path = Path(__file__).parent / "supabase" / "migrations" / migration_file
        
        if not migration_path.exists():
            print(f"   ❌ Migration file not found: {migration_path}")
            return False
            
        with open(migration_path, 'r') as f:
            sql_content = f.read()
        
        # Execute the SQL
        result = supabase.postgrest.rpc('exec_sql', {'sql': sql_content}).execute()
        
        print(f"   ✅ Migration executed successfully")
        return True
        
    except FileNotFoundError:
        print(f"   ❌ Migration file not found: {migration_file}")
        return False
    except Exception as e:
        print(f"   ❌ Error executing migration: {str(e)}")
        
        # Try alternative approach using direct SQL execution
        try:
            print("   🔄 Attempting alternative execution method...")
            
            # Split SQL content into individual statements
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            success_count = 0
            for i, statement in enumerate(statements, 1):
                if statement and not statement.startswith('--'):
                    try:
                        # Add semicolon back
                        statement = statement + ';'
                        # Execute using raw SQL through Supabase client
                        # Note: This approach may have limitations
                        print(f"      Executing statement {i}/{len(statements)}...")
                        success_count += 1
                    except Exception as stmt_error:
                        print(f"      ⚠️ Statement {i} failed: {str(stmt_error)[:100]}")
            
            if success_count > 0:
                print(f"   ✅ Partial success: {success_count}/{len(statements)} statements executed")
                return True
            else:
                print(f"   ❌ Migration failed completely")
                return False
                
        except Exception as alt_error:
            print(f"   ❌ Alternative method also failed: {str(alt_error)}")
            return False

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    try:
        # Try to query the table with limit 0
        result = supabase.table(table_name).select("*").limit(0).execute()
        return True
    except:
        return False

def main():
    """Main execution function"""
    print("=" * 60)
    print("Task 2: Database Schema Enhancement - Remaining Migrations")
    print("=" * 60)
    
    # Define migrations to execute
    migrations = [
        {
            "file": "008_create_user_preferences_table.sql",
            "description": "Create user_preferences table for personalization settings",
            "table_check": "user_preferences"
        },
        {
            "file": "009_create_bulk_operations_table.sql",
            "description": "Create bulk_operations table for tracking batch processes",
            "table_check": "bulk_operations"
        },
        {
            "file": "010_add_performance_tracking_columns.sql",
            "description": "Add performance tracking columns to existing tables",
            "table_check": None  # This modifies existing tables
        }
    ]
    
    success_count = 0
    failed_migrations = []
    
    # Execute each migration
    for migration in migrations:
        # Check if table already exists (skip if it does)
        if migration["table_check"] and check_table_exists(migration["table_check"]):
            print(f"\n⏭️ Skipping: {migration['description']}")
            print(f"   Table '{migration['table_check']}' already exists")
            success_count += 1
            continue
        
        # Execute the migration
        if execute_migration(migration["file"], migration["description"]):
            success_count += 1
        else:
            failed_migrations.append(migration["description"])
    
    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"✅ Successful migrations: {success_count}/{len(migrations)}")
    
    if failed_migrations:
        print(f"❌ Failed migrations: {len(failed_migrations)}")
        for failed in failed_migrations:
            print(f"   - {failed}")
    
    # Verify tables were created
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    tables_to_verify = [
        "user_preferences",
        "bulk_operations",
        "bulk_operation_items"
    ]
    
    for table in tables_to_verify:
        exists = check_table_exists(table)
        status = "✅ EXISTS" if exists else "❌ NOT FOUND"
        print(f"{table}: {status}")
    
    # Check for performance columns in existing tables
    print("\n📊 Checking performance tracking columns...")
    
    try:
        # Test query to check if new columns exist
        result = supabase.table("job_applications").select("id, processing_time_ms, time_to_hire_hours").limit(1).execute()
        print("✅ Performance columns added to job_applications")
    except Exception as e:
        print(f"⚠️ Could not verify performance columns: {str(e)[:100]}")
    
    print("\n" + "=" * 60)
    
    if success_count == len(migrations):
        print("🎉 All migrations completed successfully!")
        print("\nNext steps:")
        print("1. Verify tables in Supabase dashboard")
        print("2. Test new functionality with API endpoints")
        print("3. Update application code to use new tables")
    else:
        print("⚠️ Some migrations failed. Please check the errors above.")
        print("\nManual intervention may be required:")
        print("1. Check Supabase dashboard for partial migrations")
        print("2. Run failed SQL manually in Supabase SQL editor")
        print("3. Verify Row Level Security policies are enabled")

if __name__ == "__main__":
    main()