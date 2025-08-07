#!/usr/bin/env python3
"""
Execute Task 2 Migrations via Supabase REST API
"""

import os
import httpx
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{text:^60}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 60}{RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{YELLOW}ℹ️  {text}{RESET}")

async def execute_sql_via_api(sql: str, supabase_url: str, service_key: str):
    """Execute SQL via Supabase REST API"""
    
    # Parse project ref from URL
    # URL format: https://[project-ref].supabase.co
    import re
    match = re.match(r'https://([^.]+)\.supabase\.co', supabase_url)
    if not match:
        raise ValueError(f"Invalid Supabase URL: {supabase_url}")
    
    project_ref = match.group(1)
    
    # Use the Database REST API endpoint
    api_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
    
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Try different approaches
        
        # Approach 1: Try via RPC (if we have a function)
        try:
            response = await client.post(
                api_url,
                headers=headers,
                json={"query": sql}
            )
            
            if response.status_code == 200:
                return True, "Success via RPC"
            else:
                print_info(f"RPC approach failed: {response.status_code}")
        except:
            pass
        
        # Approach 2: Try direct table creation by inserting schema
        # This won't work for DDL, but we'll verify tables exist
        return False, "Direct SQL execution not available via REST API"

async def main():
    """Main function"""
    print_header("Task 2 Migration Execution")
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url:
        print_error("SUPABASE_URL not found in .env")
        return
    
    # Try service key first, then anon key
    api_key = service_key or anon_key
    
    if not api_key:
        print_error("No Supabase API key found in .env")
        print_info("Add SUPABASE_SERVICE_KEY to your .env file for admin access")
        return
    
    print_info("Unfortunately, Supabase REST API doesn't support DDL statements (CREATE TABLE)")
    print_info("Tables must be created via the Supabase Dashboard SQL Editor")
    
    print("\n" + "=" * 60)
    print(f"{BOLD}To complete Task 2 migration:{RESET}")
    print("\n1. Open Supabase SQL Editor:")
    print(f"   {BLUE}{supabase_url}/project/default/sql/new{RESET}")
    
    print("\n2. Copy this entire SQL block and paste it in the editor:")
    print(f"   {YELLOW}File: task2_simple_migration.sql{RESET}")
    
    # Display the SQL for easy copying
    migration_file = Path("task2_simple_migration.sql")
    if migration_file.exists():
        print("\n3. Or copy from here (first 50 lines):")
        print("   " + "-" * 50)
        with open(migration_file, 'r') as f:
            lines = f.readlines()[:50]
            for line in lines:
                print(f"   {line.rstrip()}")
        print("   ... (see task2_simple_migration.sql for complete SQL)")
        print("   " + "-" * 50)
    
    print("\n4. Click 'Run' in the SQL Editor")
    
    print("\n5. After running, verify with:")
    print(f"   {GREEN}python3 run_task2_migrations.py{RESET}")
    
    print("\n" + "=" * 60)
    print(f"{YELLOW}{BOLD}Alternative: Use Supabase CLI{RESET}")
    print("\nIf you have Supabase CLI installed:")
    print(f"  {GREEN}supabase db push --db-url '{os.getenv('DATABASE_URL')}'{RESET}")
    
    print("\n" + "=" * 60)
    print(f"{BOLD}Direct Link to SQL Editor:{RESET}")
    print(f"\n{BLUE}{supabase_url}/project/default/sql/new{RESET}")
    
    print(f"\n{YELLOW}Copy the contents of 'task2_simple_migration.sql' and run it there.{RESET}")

if __name__ == "__main__":
    asyncio.run(main())