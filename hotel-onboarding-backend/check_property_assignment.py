import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# Check property_managers table
print("Checking property_managers table...")
response = supabase.table('property_managers').select('*').eq('manager_id', '59356bfe-9c80-4871-81e5-2fa4496b5781').execute()

if response.data:
    print(f"Found {len(response.data)} assignments:")
    for assignment in response.data:
        print(f"  - Property: {assignment['property_id']}, Assigned: {assignment.get('assigned_at', 'N/A')}")
else:
    print("No property assignments found for this manager")

# Also check if assignment was made for the property
print("\nChecking assignments for property b1d60a13-ba0d-45bd-b709-87076abc64dc...")
response2 = supabase.table('property_managers').select('*').eq('property_id', 'b1d60a13-ba0d-45bd-b709-87076abc64dc').execute()
if response2.data:
    print(f"Found {len(response2.data)} managers assigned to this property:")
    for assignment in response2.data:
        print(f"  - Manager: {assignment['manager_id']}")
else:
    print("No managers assigned to this property")
