#!/usr/bin/env python3
"""
Test Property Lookup
Tests the property lookup method used by the application endpoint
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.supabase_service_enhanced import EnhancedSupabaseService
from setup_test_data_simple import SimpleTestSetup

def test_property_lookup():
    """Test property lookup methods"""
    
    # Get property ID from database
    setup = SimpleTestSetup()
    result = setup.client.table('properties').select('*').eq('name', 'Demo Hotel').execute()
    if not result.data:
        print("❌ No test property found in database")
        return
    
    property_id = result.data[0]['id']
    print(f"Testing property lookup for ID: {property_id}")
    
    # Test with Supabase service
    supabase_service = EnhancedSupabaseService()
    
    # Test sync method (used by application endpoint)
    print("\n1. Testing get_property_by_id_sync (used by /apply endpoint):")
    try:
        property_sync = supabase_service.get_property_by_id_sync(property_id)
        if property_sync:
            print(f"✅ Property found (sync): {property_sync.name}")
            print(f"   ID: {property_sync.id}")
            print(f"   Active: {property_sync.is_active}")
        else:
            print("❌ Property not found (sync)")
            
    except Exception as e:
        print(f"❌ Sync lookup failed: {e}")
    
    # Test async method for comparison
    print("\n2. Testing get_property_by_id (async version):")
    try:
        import asyncio
        property_async = asyncio.run(supabase_service.get_property_by_id(property_id))
        if property_async:
            print(f"✅ Property found (async): {property_async.name}")
            print(f"   ID: {property_async.id}")
            print(f"   Active: {property_async.is_active}")
        else:
            print("❌ Property not found (async)")
            
    except Exception as e:
        print(f"❌ Async lookup failed: {e}")
    
    # Test direct database query
    print("\n3. Testing direct database query:")
    try:
        result = setup.client.table('properties').select('*').eq('id', property_id).execute()
        if result.data:
            prop_data = result.data[0]
            print(f"✅ Property found (direct): {prop_data['name']}")
            print(f"   ID: {prop_data['id']}")
            print(f"   Active: {prop_data['is_active']}")
        else:
            print("❌ Property not found (direct)")
            
    except Exception as e:
        print(f"❌ Direct query failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("PROPERTY LOOKUP TESTING")
    print("=" * 60)
    
    test_property_lookup()