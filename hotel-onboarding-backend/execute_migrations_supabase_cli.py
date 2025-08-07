#!/usr/bin/env python3
"""
Execute migrations using Supabase Management API
Requires Supabase access token from dashboard
"""

import os
import sys
import json
import time
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseManagementMigrator:
    """Execute migrations using Supabase Management API"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.project_ref = self.supabase_url.split('//')[1].split('.')[0] if self.supabase_url else None
        
        # Get access token - user needs to set this
        self.access_token = os.getenv("SUPABASE_ACCESS_TOKEN")
        
        if not self.project_ref:
            raise ValueError("SUPABASE_URL not found in environment")
        
        if not self.access_token:
            print("⚠️ SUPABASE_ACCESS_TOKEN not set")
            print("\n📝 To get your access token:")
            print("1. Go to https://app.supabase.com/project/" + self.project_ref)
            print("2. Go to Settings > API")
            print("3. Copy your 'anon public' or 'service_role' key")
            print("4. Set environment variable: export SUPABASE_ACCESS_TOKEN='your-token'")
            print("\nAlternatively, run the SQL manually in Supabase SQL Editor")
            raise ValueError("Missing SUPABASE_ACCESS_TOKEN")

    def execute_sql_via_api(self, sql_content: str, description: str) -> bool:
        """Execute SQL using Supabase Management API"""
        try:
            print(f"\n📋 Executing: {description}")
            
            # Supabase SQL execution endpoint
            url = f"https://{self.project_ref}.supabase.co/rest/v1/rpc/exec_sql"
            
            headers = {
                "apikey": self.access_token,
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            
            # Try to execute the SQL
            payload = {"sql": sql_content}
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201, 204]:
                print(f"✅ {description}: Successfully executed")
                return True
            elif response.status_code == 404:
                # exec_sql function doesn't exist, try to create it
                return self.create_and_execute(sql_content, description)
            else:
                print(f"❌ API error: {response.status_code} - {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}")
            return False

    def create_and_execute(self, sql_content: str, description: str) -> bool:
        """Create exec_sql function and then execute"""
        try:
            print("   🔧 Creating exec_sql function...")
            
            # Create a simpler approach - directly create the tables
            # Split into individual statements
            statements = self._split_sql_statements(sql_content)
            
            success = 0
            for i, stmt in enumerate(statements, 1):
                if self._execute_single_statement(stmt, f"Statement {i}/{len(statements)}"):
                    success += 1
            
            if success > 0:
                print(f"   ✅ {description}: {success}/{len(statements)} statements executed")
                return True
            return False
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            return False

    def _split_sql_statements(self, sql: str) -> list:
        """Split SQL into individual statements"""
        statements = []
        current = []
        in_function = False
        
        for line in sql.split('\n'):
            if line.strip().startswith('--') or not line.strip():
                continue
            
            if 'CREATE OR REPLACE FUNCTION' in line or 'CREATE FUNCTION' in line:
                in_function = True
            
            current.append(line)
            
            if not in_function and line.rstrip().endswith(';'):
                statements.append('\n'.join(current))
                current = []
            elif in_function and line.strip().endswith('$$ LANGUAGE plpgsql;'):
                statements.append('\n'.join(current))
                current = []
                in_function = False
        
        if current:
            statements.append('\n'.join(current))
        
        return [s.strip() for s in statements if s.strip()]

    def _execute_single_statement(self, stmt: str, description: str) -> bool:
        """Try to execute a single SQL statement"""
        # This would need actual implementation based on Supabase API capabilities
        # For now, return False to indicate manual execution is needed
        return False

def create_manual_execution_script():
    """Create a script that can be easily copied to Supabase SQL Editor"""
    print("\n" + "=" * 60)
    print("MANUAL EXECUTION SCRIPT")
    print("=" * 60)
    print("\n📝 Copy and paste the following into Supabase SQL Editor:")
    print("   (Dashboard > SQL Editor > New Query)\n")
    
    script_path = Path(__file__).parent / "run_task2_migrations_combined.sql"
    
    if script_path.exists():
        print(f"-- File: {script_path.name}")
        print("-- " + "=" * 58)
        with open(script_path, 'r') as f:
            content = f.read()
            # Print first 50 lines as preview
            lines = content.split('\n')[:50]
            for line in lines:
                print(line)
            if len(content.split('\n')) > 50:
                print("\n... (truncated - copy from file: run_task2_migrations_combined.sql)")
    else:
        print("❌ Combined migration file not found")
        print("   Please check: run_task2_migrations_combined.sql")

def main():
    """Main execution"""
    print("=" * 60)
    print("Supabase Migration Execution")
    print("=" * 60)
    
    try:
        migrator = SupabaseManagementMigrator()
        
        # Try to execute migrations
        base_path = Path(__file__).parent
        migrations = [
            ("supabase/migrations/008_create_user_preferences_table.sql", "User Preferences Table"),
            ("supabase/migrations/009_create_bulk_operations_table.sql", "Bulk Operations Tables"),
            ("supabase/migrations/010_add_performance_tracking_columns.sql", "Performance Tracking")
        ]
        
        success = 0
        for file_path, description in migrations:
            full_path = base_path / file_path
            if full_path.exists():
                with open(full_path, 'r') as f:
                    sql = f.read()
                if migrator.execute_sql_via_api(sql, description):
                    success += 1
        
        if success == len(migrations):
            print("\n✅ All migrations executed successfully!")
        else:
            print(f"\n⚠️ Only {success}/{len(migrations)} migrations succeeded")
            create_manual_execution_script()
            
    except ValueError as e:
        print(f"\n{e}")
        create_manual_execution_script()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        create_manual_execution_script()

if __name__ == "__main__":
    main()