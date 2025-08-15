import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase = create_client(url, key)

# Test direct insert into property_managers
manager_id = "959a01a6-6bb1-4bbb-a779-acaff92518f4"  # Goutham
property_id = "628113c8-ed04-4119-9118-e358c14ad13f"  # The property from logs

print("Testing direct insert into property_managers table...")

# First, delete any existing assignments
print("Removing existing assignments...")
delete_result = supabase.table('property_managers').delete().eq('manager_id', manager_id).execute()
print(f"Deleted {len(delete_result.data) if delete_result.data else 0} existing assignments")

# Try to insert
assignment_data = {
    "manager_id": manager_id,
    "property_id": property_id,
    "assigned_at": datetime.now(timezone.utc).isoformat()
}

print(f"Inserting assignment: manager={manager_id[:8]}... to property={property_id[:8]}...")
try:
    result = supabase.table('property_managers').insert(assignment_data).execute()
    if result.data:
        print(f"✅ Success\! Assignment created: {result.data}")
    else:
        print(f"❌ No data returned from insert")
except Exception as e:
    print(f"❌ Error: {e}")

# Check if it exists
print("\nChecking if assignment exists...")
check = supabase.table('property_managers').select('*').eq('manager_id', manager_id).execute()
if check.data:
    print(f"✅ Found {len(check.data)} assignments for this manager:")
    for a in check.data:
        print(f"  - Property: {a['property_id']}, Assigned: {a.get('assigned_at', 'N/A')}")
else:
    print("❌ No assignments found")
