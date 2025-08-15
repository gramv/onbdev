#!/usr/bin/env python3
"""
Quick fix for manager property assignment
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

from app.supabase_service_enhanced import EnhancedSupabaseService
import asyncio

async def main():
    service = EnhancedSupabaseService()
    manager_email = 'manager@demo.com'
    property_id = 'a99239dd-ebde-4c69-b862-ecba9e878798'
    
    print('Fixing manager property assignment...')
    
    # Get manager
    manager = service.get_user_by_email_sync(manager_email)
    if not manager:
        print('Manager not found')
        return False
    
    print(f'Found manager: {manager.id}')
    
    # Update user record with property_id
    try:
        result = service.supabase.table('users') \
            .update({'property_id': property_id}) \
            .eq('id', manager.id) \
            .execute()
        
        if result.data:
            print('SUCCESS: Manager property assignment updated!')
            print(f'Manager {manager_email} is now assigned to property {property_id}')
            return True
    except Exception as e:
        print(f'Error: {e}')
    
    return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)