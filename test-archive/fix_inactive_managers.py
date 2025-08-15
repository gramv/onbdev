#!/usr/bin/env python3
"""
Fix Inactive Managers in Database
Update all managers to have is_active=True
"""

import sys
import os
sys.path.append('hotel-onboarding-backend/app')

import asyncio
from supabase import create_client

async def fix_inactive_managers():
    """Update all managers to be active"""
    print("🔧 Fixing inactive managers in database...")
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Get all inactive managers
        response = supabase.table('users').select('*').eq('role', 'manager').eq('is_active', False).execute()
        
        inactive_managers = response.data
        print(f"Found {len(inactive_managers)} inactive managers")
        
        if not inactive_managers:
            print("✅ No inactive managers found")
            return True
        
        # Update all managers to be active
        update_response = supabase.table('users').update({
            'is_active': True
        }).eq('role', 'manager').execute()
        
        print(f"✅ Updated {len(update_response.data)} managers to active status")
        
        # Verify the fix
        verify_response = supabase.table('users').select('id, email, is_active').eq('role', 'manager').execute()
        
        active_count = sum(1 for user in verify_response.data if user['is_active'])
        total_count = len(verify_response.data)
        
        print(f"📊 Verification: {active_count}/{total_count} managers are now active")
        
        return active_count > 0
        
    except Exception as e:
        print(f"❌ Error fixing managers: {e}")
        return False

def main():
    print("🚀 Fix Inactive Managers")
    print("=" * 40)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('hotel-onboarding-backend/.env')
    
    success = asyncio.run(fix_inactive_managers())
    
    if success:
        print("\n✅ Managers fixed successfully!")
        print("💡 Next steps:")
        print("1. Restart the backend server")
        print("2. Test the HR dashboard KPIs")
        print("3. The totalManagers count should now show the correct value")
    else:
        print("\n❌ Failed to fix managers")
        print("💡 Manual fix needed:")
        print("Run this SQL in your Supabase dashboard:")
        print("UPDATE users SET is_active = true WHERE role = 'manager';")

if __name__ == "__main__":
    main()