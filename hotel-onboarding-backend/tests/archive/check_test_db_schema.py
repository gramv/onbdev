#!/usr/bin/env python3
"""
Check Test Database Schema
Compares test database schema with what we expect
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

# Verify we're on test database
if 'kzommszdhapvqpekpvnt' not in url:
    print("ERROR: This script is for TEST database only!")
    exit(1)

print(f"Checking TEST database schema: {url}")
print("=" * 60)

# Create Supabase client
client = create_client(url, key)

# Tables to check
tables_to_check = [
    'users',
    'properties', 
    'property_managers',
    'employees',
    'job_applications'
]

for table_name in tables_to_check:
    print(f"\n📊 Table: {table_name}")
    print("-" * 40)
    try:
        # Try to select one row to see structure
        result = client.table(table_name).select('*').limit(1).execute()
        
        if result.data and len(result.data) > 0:
            # Show columns from first row
            columns = list(result.data[0].keys())
            print(f"   Columns found: {', '.join(columns)}")
        else:
            # Table exists but is empty - try to insert dummy data to see error
            print(f"   Table exists but is empty")
            # Try a minimal insert to see what columns are required
            try:
                if table_name == 'properties':
                    test_insert = client.table(table_name).insert({'name': 'TEST'}).execute()
                elif table_name == 'users':
                    test_insert = client.table(table_name).insert({'email': 'test@test.com'}).execute()
            except Exception as e:
                error_msg = str(e)
                if 'null value' in error_msg:
                    # Extract required columns from error
                    print(f"   Required columns from error: {error_msg}")
                    
    except Exception as e:
        print(f"   ❌ Error accessing table: {e}")

print("\n" + "=" * 60)
print("Schema check complete!")
print("\nIf the schema is different from production, you may need to:")
print("1. Export production schema (without data)")
print("2. Import it into test database")
print("3. Then run the data setup scripts")