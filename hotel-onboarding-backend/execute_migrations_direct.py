#!/usr/bin/env python3
"""
Execute migrations directly using Supabase Python client with PostgreSQL connection
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
import urllib.parse

# Load environment variables
load_dotenv()

class DirectMigrationExecutor:
    """Execute migrations using direct PostgreSQL connection"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials")
        
        # Initialize Supabase client for checking
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Get database connection string
        self.db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
        
        if not self.db_url:
            # Construct database URL from Supabase URL
            # Format: postgresql://postgres.[project-ref]:[password]@[host]:5432/postgres
            project_ref = self.supabase_url.split('//')[1].split('.')[0]
            db_password = os.getenv("SUPABASE_DB_PASSWORD") or "your-db-password"
            
            # Common Supabase database host patterns
            db_host = f"db.{project_ref}.supabase.co"
            self.db_url = f"postgresql://postgres.{project_ref}:{db_password}@{db_host}:5432/postgres"
            
            print(f"ℹ️ Using constructed database URL")
            print(f"   Host: {db_host}")
            print(f"   Note: You may need to set SUPABASE_DB_PASSWORD environment variable")

    def execute_with_psycopg2(self, sql_content: str, description: str) -> bool:
        """Execute SQL using psycopg2 direct connection"""
        try:
            print(f"\n📋 Executing: {description}")
            
            # Parse connection string
            result = urllib.parse.urlparse(self.db_url)
            
            # Connect to PostgreSQL
            connection = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port or 5432,
                sslmode='require'
            )
            
            connection.autocommit = True
            cursor = connection.cursor()
            
            # Execute the SQL
            try:
                cursor.execute(sql_content)
                print(f"✅ {description}: Successfully executed")
                return True
            except psycopg2.Error as e:
                print(f"❌ SQL execution error: {e.pgerror}")
                return False
            finally:
                cursor.close()
                connection.close()
                
        except psycopg2.OperationalError as e:
            print(f"❌ Connection error: {str(e)[:200]}")
            print("\n💡 To fix this:")
            print("1. Get your database password from Supabase dashboard > Settings > Database")
            print("2. Set environment variable: export SUPABASE_DB_PASSWORD='your-password'")
            print("3. Or set DATABASE_URL with full connection string")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)[:200]}")
            return False

    def execute_migration_file(self, file_path: Path, description: str) -> bool:
        """Execute a migration file"""
        if not file_path.exists():
            print(f"❌ Migration file not found: {file_path}")
            return False
        
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        return self.execute_with_psycopg2(sql_content, description)

    def check_table_exists(self, table_name: str) -> bool:
        """Check if table exists using Supabase client"""
        try:
            # Try to query the table
            result = self.supabase.table(table_name).select("*").limit(0).execute()
            return True
        except:
            return False

def main():
    """Main execution"""
    print("=" * 60)
    print("Direct PostgreSQL Migration Execution")
    print("=" * 60)
    
    try:
        executor = DirectMigrationExecutor()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\n📝 Alternative: Please run these SQL files manually in Supabase:")
        print("   1. supabase/migrations/008_create_user_preferences_table.sql")
        print("   2. supabase/migrations/009_create_bulk_operations_table.sql")
        print("   3. supabase/migrations/010_add_performance_tracking_columns.sql")
        print("\n   Or use the combined file: run_task2_migrations_combined.sql")
        sys.exit(1)
    
    # Check if tables already exist
    tables_to_check = ["user_preferences", "bulk_operations"]
    existing = []
    
    for table in tables_to_check:
        if executor.check_table_exists(table):
            existing.append(table)
            print(f"ℹ️ Table '{table}' already exists")
    
    if len(existing) == len(tables_to_check):
        print("\n✅ All tables already exist! Migration may have been completed.")
        return
    
    # Try to execute migrations
    base_path = Path(__file__).parent
    migrations = [
        ("supabase/migrations/008_create_user_preferences_table.sql", "User Preferences Table"),
        ("supabase/migrations/009_create_bulk_operations_table.sql", "Bulk Operations Tables"),
        ("supabase/migrations/010_add_performance_tracking_columns.sql", "Performance Tracking")
    ]
    
    success_count = 0
    for file_path, description in migrations:
        full_path = base_path / file_path
        if executor.execute_migration_file(full_path, description):
            success_count += 1
    
    # Verification
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    all_tables = ["user_preferences", "bulk_operations", "bulk_operation_items"]
    verified = 0
    
    for table in all_tables:
        exists = executor.check_table_exists(table)
        status = "✅ EXISTS" if exists else "❌ NOT FOUND"
        print(f"{table}: {status}")
        if exists:
            verified += 1
    
    print("\n" + "=" * 60)
    if verified == len(all_tables):
        print("🎉 All migrations completed successfully!")
    elif verified > 0:
        print(f"⚠️ Partial success: {verified}/{len(all_tables)} tables created")
    else:
        print("❌ Migration verification failed")
        print("\nPlease run manually in Supabase SQL Editor:")
        print("  File: run_task2_migrations_combined.sql")

if __name__ == "__main__":
    main()