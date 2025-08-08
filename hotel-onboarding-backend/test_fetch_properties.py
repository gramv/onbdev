import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(url, key)

manager_id = "959a01a6-6bb1-4bbb-a779-acaff92518f4"  # Goutham

print("Testing different ways to fetch manager properties...")

# Method 1: Direct query to property_managers
print("\n1. Direct query to property_managers:")
result1 = supabase.table('property_managers').select('*').eq('manager_id', manager_id).execute()
print(f"Found {len(result1.data)} assignments: {result1.data}")

# Method 2: With joined properties data (as backend does)
print("\n2. Query with joined properties:")
try:
    result2 = supabase.table('property_managers').select('*, properties(*)').eq('manager_id', manager_id).execute()
    print(f"Found {len(result2.data)} assignments with properties:")
    for item in result2.data:
        print(f"  - Assignment: {item}")
except Exception as e:
    print(f"Error with join query: {e}")

# Method 3: Check if foreign key relationship exists
print("\n3. Checking properties table directly:")
prop_result = supabase.table('properties').select('*').eq('id', '628113c8-ed04-4119-9118-e358c14ad13f').execute()
if prop_result.data:
    print(f"Property exists: {prop_result.data[0]['name']}")
else:
    print("Property not found\!")
