#!/usr/bin/env python3
"""
Check what property the manager is assigned to
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('.env')

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

supabase: Client = create_client(url, key)

# Get manager user
manager_result = supabase.table('users').select('*').eq('email', 'manager@demo.com').execute()
if manager_result.data:
    manager = manager_result.data[0]
    print(f"Manager ID: {manager['id']}")
    print(f"Manager Name: {manager['first_name']} {manager['last_name']}")
    
    # Check property assignment
    pm_result = supabase.table('property_managers').select('*, properties(*)').eq('manager_id', manager['id']).execute()
    if pm_result.data:
        for assignment in pm_result.data:
            print(f"\nAssigned Property:")
            print(f"  Property ID: {assignment['property_id']}")
            if assignment.get('properties'):
                print(f"  Property Name: {assignment['properties']['name']}")
                print(f"  Property Address: {assignment['properties']['address']}")
    else:
        print("\n❌ No property assignment found")
        
        # List available properties
        props_result = supabase.table('properties').select('*').limit(5).execute()
        if props_result.data:
            print("\nAvailable properties:")
            for prop in props_result.data:
                print(f"  {prop['id']}: {prop['name']}")
else:
    print("❌ Manager not found")