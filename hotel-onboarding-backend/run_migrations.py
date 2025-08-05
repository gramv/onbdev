#!/usr/bin/env python3
"""
Run Supabase migrations to create necessary tables
"""
import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migrations():
    """Run all SQL migrations in the migrations folder"""
    # Get Supabase credentials
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        sys.exit(1)
    
    # Create Supabase client
    supabase: Client = create_client(url, key)
    
    # Get migrations directory
    migrations_dir = Path(__file__).parent / "supabase" / "migrations"
    
    if not migrations_dir.exists():
        print(f"Error: Migrations directory not found: {migrations_dir}")
        sys.exit(1)
    
    # Get all SQL files
    sql_files = sorted(migrations_dir.glob("*.sql"))
    
    if not sql_files:
        print("No migration files found")
        return
    
    print(f"Found {len(sql_files)} migration files")
    
    # Run each migration
    for sql_file in sql_files:
        print(f"\nRunning migration: {sql_file.name}")
        
        try:
            # Read SQL content
            with open(sql_file, 'r') as f:
                sql_content = f.read()
            
            # Execute SQL using raw RPC call
            # Note: Supabase Python client doesn't have a direct SQL execute method
            # You would need to run this SQL directly in Supabase dashboard or use psql
            print(f"Migration content for {sql_file.name}:")
            print("-" * 50)
            print(sql_content[:500] + "..." if len(sql_content) > 500 else sql_content)
            print("-" * 50)
            print(f"✓ Please run this migration in Supabase SQL Editor")
            
        except Exception as e:
            print(f"Error reading migration {sql_file.name}: {e}")
            continue
    
    print("\n" + "="*50)
    print("IMPORTANT: The migrations need to be run manually in Supabase:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste each migration SQL")
    print("4. Run the migrations in order")
    print("="*50)

if __name__ == "__main__":
    run_migrations()