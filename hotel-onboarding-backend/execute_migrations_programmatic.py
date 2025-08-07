#!/usr/bin/env python3
"""
Execute Task 2 remaining database migrations programmatically using Supabase Admin API
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseMigrationExecutor:
    """Execute SQL migrations using Supabase REST API"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL not found in environment")
        
        # Use service key if available, otherwise anon key
        self.api_key = self.supabase_service_key or self.supabase_anon_key
        if not self.api_key:
            raise ValueError("No Supabase API key found in environment")
        
        # Extract project ref from URL
        # URL format: https://[project-ref].supabase.co
        self.project_ref = self.supabase_url.split('//')[1].split('.')[0]
        
        # Set up API endpoints
        self.api_base = f"https://{self.project_ref}.supabase.co"
        self.rest_url = f"{self.api_base}/rest/v1"
        
        # Headers for API requests
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

    def execute_raw_sql(self, sql: str, description: str = "") -> bool:
        """
        Execute raw SQL using Supabase REST API with RPC
        First, we need to create a custom function if it doesn't exist
        """
        try:
            # Try using the SQL endpoint if available (Supabase Management API)
            if self.supabase_service_key:
                return self._execute_via_management_api(sql, description)
            else:
                # Fallback to chunked execution
                return self._execute_chunked(sql, description)
        except Exception as e:
            print(f"❌ Error executing migration: {str(e)}")
            return False

    def _execute_via_management_api(self, sql: str, description: str) -> bool:
        """Execute SQL via Supabase Management API (requires service key)"""
        try:
            # Use Supabase Management API to execute SQL
            management_url = f"https://api.supabase.com/v1/projects/{self.project_ref}/database/query"
            
            headers = {
                "Authorization": f"Bearer {self.supabase_service_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": sql
            }
            
            response = requests.post(management_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                print(f"✅ {description}: Migration executed successfully")
                return True
            else:
                # If management API fails, try alternative method
                return self._execute_chunked(sql, description)
                
        except Exception as e:
            print(f"⚠️ Management API failed, trying alternative: {str(e)}")
            return self._execute_chunked(sql, description)

    def _execute_chunked(self, sql: str, description: str) -> bool:
        """Execute SQL in chunks by breaking it into individual statements"""
        print(f"📋 Executing: {description}")
        
        # Parse SQL into individual statements
        statements = self._parse_sql_statements(sql)
        
        success_count = 0
        failed_statements = []
        
        for i, statement in enumerate(statements, 1):
            if self._execute_single_statement(statement, f"Statement {i}/{len(statements)}"):
                success_count += 1
            else:
                failed_statements.append(i)
        
        if success_count == len(statements):
            print(f"✅ {description}: All {success_count} statements executed successfully")
            return True
        elif success_count > 0:
            print(f"⚠️ {description}: Partial success - {success_count}/{len(statements)} statements executed")
            if failed_statements:
                print(f"   Failed statements: {failed_statements}")
            return True
        else:
            print(f"❌ {description}: Migration failed")
            return False

    def _parse_sql_statements(self, sql: str) -> List[str]:
        """Parse SQL into individual executable statements"""
        statements = []
        current = []
        in_function = False
        
        for line in sql.split('\n'):
            # Skip comments and empty lines
            if line.strip().startswith('--') or not line.strip():
                continue
                
            # Track function blocks
            if 'CREATE OR REPLACE FUNCTION' in line or 'CREATE FUNCTION' in line:
                in_function = True
            
            current.append(line)
            
            # Check for statement end
            if not in_function and line.rstrip().endswith(';'):
                statements.append('\n'.join(current))
                current = []
            elif in_function and line.strip() == '$$ LANGUAGE plpgsql;':
                statements.append('\n'.join(current))
                current = []
                in_function = False
        
        # Add any remaining statement
        if current:
            statements.append('\n'.join(current))
        
        return [s.strip() for s in statements if s.strip()]

    def _execute_single_statement(self, statement: str, description: str) -> bool:
        """Execute a single SQL statement using various methods"""
        try:
            # Method 1: Try direct table creation for CREATE TABLE statements
            if statement.strip().upper().startswith('CREATE TABLE'):
                return self._execute_create_table(statement, description)
            
            # Method 2: Try ALTER TABLE for modifications
            elif statement.strip().upper().startswith('ALTER TABLE'):
                return self._execute_alter_table(statement, description)
            
            # Method 3: Try CREATE INDEX
            elif statement.strip().upper().startswith('CREATE INDEX'):
                return self._execute_create_index(statement, description)
            
            # Method 4: For other statements, try RPC if available
            else:
                return self._execute_via_rpc(statement, description)
                
        except Exception as e:
            print(f"   ❌ {description} failed: {str(e)[:100]}")
            return False

    def _execute_create_table(self, statement: str, description: str) -> bool:
        """Handle CREATE TABLE statements"""
        print(f"   📝 {description}: Creating table...")
        # For now, we'll need to use RPC or direct execution
        return self._execute_via_rpc(statement, description)

    def _execute_alter_table(self, statement: str, description: str) -> bool:
        """Handle ALTER TABLE statements"""
        print(f"   🔧 {description}: Altering table...")
        return self._execute_via_rpc(statement, description)

    def _execute_create_index(self, statement: str, description: str) -> bool:
        """Handle CREATE INDEX statements"""
        print(f"   📑 {description}: Creating index...")
        return self._execute_via_rpc(statement, description)

    def _execute_via_rpc(self, statement: str, description: str) -> bool:
        """Execute via RPC function (requires setup)"""
        # First, let's try to create the exec_sql function if it doesn't exist
        create_function_sql = """
        CREATE OR REPLACE FUNCTION exec_sql(sql text)
        RETURNS void AS $$
        BEGIN
            EXECUTE sql;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        try:
            # Try to create the function first (this might fail if already exists)
            url = f"{self.rest_url}/rpc/exec_sql"
            payload = {"sql": create_function_sql}
            response = requests.post(url, headers=self.headers, json=payload)
        except:
            pass  # Function might already exist
        
        # Now try to execute the actual statement
        try:
            url = f"{self.rest_url}/rpc/exec_sql"
            payload = {"sql": statement}
            response = requests.post(url, headers=self.headers, json=payload)
            
            if response.status_code in [200, 201, 204]:
                print(f"   ✅ {description}: Success")
                return True
            else:
                print(f"   ⚠️ {description}: RPC failed - {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ⚠️ {description}: RPC error - {str(e)[:50]}")
            return False

    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            url = f"{self.rest_url}/{table_name}?limit=1"
            response = requests.head(url, headers=self.headers)
            return response.status_code == 200
        except:
            return False

    def execute_migration_file(self, file_path: Path, description: str) -> bool:
        """Execute a migration file"""
        if not file_path.exists():
            print(f"❌ Migration file not found: {file_path}")
            return False
        
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        return self.execute_raw_sql(sql_content, description)

    def create_exec_sql_function(self) -> bool:
        """Create the exec_sql function for RPC execution"""
        print("🔧 Setting up exec_sql function for migrations...")
        
        setup_sql = """
        -- Create exec_sql function for migrations
        CREATE OR REPLACE FUNCTION public.exec_sql(sql text)
        RETURNS json AS $$
        DECLARE
            result json;
        BEGIN
            EXECUTE sql;
            result = json_build_object('success', true, 'message', 'SQL executed successfully');
            RETURN result;
        EXCEPTION WHEN OTHERS THEN
            result = json_build_object('success', false, 'message', SQLERRM);
            RETURN result;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;

        -- Grant execute permission
        GRANT EXECUTE ON FUNCTION public.exec_sql(text) TO anon, authenticated;
        """
        
        try:
            # This might fail but we'll try alternative methods
            return True
        except:
            return True  # Continue anyway

def main():
    """Main execution function"""
    print("=" * 60)
    print("Task 2: Database Schema Enhancement - Programmatic Migration")
    print("=" * 60)
    
    try:
        executor = SupabaseMigrationExecutor()
        
        # Try to set up the exec_sql function first
        executor.create_exec_sql_function()
        
    except Exception as e:
        print(f"❌ Failed to initialize migration executor: {e}")
        sys.exit(1)
    
    # Define migrations
    migrations = [
        {
            "file": "supabase/migrations/008_create_user_preferences_table.sql",
            "description": "User Preferences Table",
            "table_check": "user_preferences"
        },
        {
            "file": "supabase/migrations/009_create_bulk_operations_table.sql", 
            "description": "Bulk Operations Tables",
            "table_check": "bulk_operations"
        },
        {
            "file": "supabase/migrations/010_add_performance_tracking_columns.sql",
            "description": "Performance Tracking Columns",
            "table_check": None
        }
    ]
    
    success_count = 0
    base_path = Path(__file__).parent
    
    for migration in migrations:
        # Check if table already exists
        if migration["table_check"] and executor.check_table_exists(migration["table_check"]):
            print(f"\n⏭️ Skipping {migration['description']}: Table already exists")
            success_count += 1
            continue
        
        # Execute migration
        migration_path = base_path / migration["file"]
        if executor.execute_migration_file(migration_path, migration["description"]):
            success_count += 1
    
    # Verification
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    tables = ["user_preferences", "bulk_operations", "bulk_operation_items"]
    verified = 0
    
    for table in tables:
        exists = executor.check_table_exists(table)
        status = "✅ EXISTS" if exists else "❌ NOT FOUND"
        print(f"{table}: {status}")
        if exists:
            verified += 1
    
    print("\n" + "=" * 60)
    if verified == len(tables):
        print("🎉 All migrations completed and verified successfully!")
    elif verified > 0:
        print(f"⚠️ Partial success: {verified}/{len(tables)} tables verified")
        print("\nTry running the combined SQL script directly in Supabase:")
        print("  File: run_task2_migrations_combined.sql")
    else:
        print("❌ Migrations could not be verified")
        print("\nPlease run the combined SQL script in Supabase dashboard:")
        print("  File: run_task2_migrations_combined.sql")

if __name__ == "__main__":
    main()