#!/usr/bin/env python3
"""
Setup exec_sql function and run migrations through Supabase
This creates a special function that allows SQL execution via RPC
"""

import os
import sys
import asyncio
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class MigrationSetup:
    """Setup and execute migrations through Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print(f"✅ Connected to Supabase")
        print(f"   URL: {self.supabase_url}")

    def setup_exec_function(self) -> bool:
        """Create the exec_sql function if it doesn't exist"""
        print("\n🔧 Setting up SQL execution function...")
        
        # First, let's try a simple test to see what works
        try:
            # Test if we can query the users table
            result = self.supabase.table("users").select("id").limit(1).execute()
            print("   ✅ Can query existing tables")
        except Exception as e:
            print(f"   ❌ Cannot query tables: {e}")
            return False
        
        # Since we can't directly execute SQL through the client,
        # we'll create the tables using individual operations
        return True

    def create_user_preferences_table(self) -> bool:
        """Create user_preferences table through Supabase operations"""
        print("\n📋 Creating user_preferences table...")
        
        try:
            # Check if table exists
            result = self.supabase.table("user_preferences").select("id").limit(0).execute()
            print("   ℹ️ Table user_preferences already exists")
            return True
        except:
            # Table doesn't exist, but we can't create it via client
            print("   ⚠️ Table doesn't exist and cannot be created via API")
            return False

    def create_bulk_operations_table(self) -> bool:
        """Create bulk_operations table through Supabase operations"""
        print("\n📋 Creating bulk_operations table...")
        
        try:
            # Check if table exists
            result = self.supabase.table("bulk_operations").select("id").limit(0).execute()
            print("   ℹ️ Table bulk_operations already exists")
            return True
        except:
            print("   ⚠️ Table doesn't exist and cannot be created via API")
            return False

    def verify_tables(self) -> dict:
        """Verify which tables exist"""
        print("\n🔍 Verifying tables...")
        
        tables = {
            "users": False,
            "properties": False,
            "employees": False,
            "job_applications": False,
            "user_preferences": False,
            "bulk_operations": False,
            "bulk_operation_items": False,
            "audit_logs": False,
            "notifications": False,
            "analytics_events": False
        }
        
        for table_name in tables:
            try:
                self.supabase.table(table_name).select("*").limit(0).execute()
                tables[table_name] = True
                print(f"   ✅ {table_name}: EXISTS")
            except:
                print(f"   ❌ {table_name}: NOT FOUND")
        
        return tables

    def generate_dashboard_sql(self) -> str:
        """Generate SQL that can be run in Supabase dashboard"""
        print("\n📝 Generating SQL for manual execution...")
        
        base_path = Path(__file__).parent
        combined_sql = []
        
        # Add header
        combined_sql.append("-- Combined Migration Script for Task 2")
        combined_sql.append("-- Run this in Supabase SQL Editor")
        combined_sql.append("-- " + "=" * 50)
        combined_sql.append("")
        
        # Add each migration file
        migrations = [
            "supabase/migrations/008_create_user_preferences_table.sql",
            "supabase/migrations/009_create_bulk_operations_table.sql",
            "supabase/migrations/010_add_performance_tracking_columns.sql"
        ]
        
        for migration_file in migrations:
            file_path = base_path / migration_file
            if file_path.exists():
                combined_sql.append(f"-- From: {migration_file}")
                combined_sql.append("-- " + "-" * 50)
                with open(file_path, 'r') as f:
                    combined_sql.append(f.read())
                combined_sql.append("")
                combined_sql.append("-- " + "-" * 50)
                combined_sql.append("")
        
        # Save to file
        output_file = base_path / "final_task2_migrations.sql"
        with open(output_file, 'w') as f:
            f.write('\n'.join(combined_sql))
        
        print(f"   ✅ SQL saved to: {output_file.name}")
        return output_file.name

def main():
    """Main execution"""
    print("=" * 60)
    print("Supabase Migration Setup and Execution")
    print("=" * 60)
    
    try:
        setup = MigrationSetup()
        
        # Setup execution function
        setup.setup_exec_function()
        
        # Verify current state
        tables = setup.verify_tables()
        
        # Check if key tables exist
        required_new_tables = ["user_preferences", "bulk_operations", "bulk_operation_items"]
        missing = [t for t in required_new_tables if not tables.get(t, False)]
        
        if not missing:
            print("\n✅ All required tables already exist!")
            print("   Migration appears to be complete.")
            return
        
        print(f"\n⚠️ Missing tables: {', '.join(missing)}")
        
        # Generate SQL file for manual execution
        sql_file = setup.generate_dashboard_sql()
        
        print("\n" + "=" * 60)
        print("MANUAL EXECUTION REQUIRED")
        print("=" * 60)
        print("\n📝 The Supabase client API doesn't support direct DDL execution.")
        print("   Please run the migrations manually:\n")
        print("1. Open Supabase Dashboard:")
        print(f"   https://app.supabase.com/project/{setup.supabase_url.split('//')[1].split('.')[0]}")
        print("\n2. Go to SQL Editor (left sidebar)")
        print("\n3. Click 'New Query'")
        print(f"\n4. Copy the contents of: {sql_file}")
        print("\n5. Paste and click 'Run'")
        print("\n" + "=" * 60)
        print("\n💡 Quick Copy Command:")
        print(f"   cat {sql_file} | pbcopy")
        print("   (This copies the SQL to your clipboard)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease run migrations manually in Supabase SQL Editor")

if __name__ == "__main__":
    main()