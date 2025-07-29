#!/usr/bin/env python3
"""
Setup Manager Account for Testing
Create the manager account: vgoutamram@gmail.com / Gouthi321@
"""
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, 'hotel-onboarding-backend')

from app.supabase_service_enhanced import EnhancedSupabaseService
from app.auth import PasswordManager
from app.models import User, Property

async def setup_manager_account():
    """Set up the manager account and test data"""
    print("🔧 Setting up manager account for testing...")
    
    try:
        # Initialize services
        supabase_service = EnhancedSupabaseService()
        password_manager = PasswordManager()
        
        # Manager details
        manager_email = "vgoutamram@gmail.com"
        manager_password = "Gouthi321@"
        manager_id = "mgr_rci_001"
        property_id = "prop_test_001"
        
        print(f"Creating manager: {manager_email}")
        
        # Create manager user
        manager_data = {
            "id": manager_id,
            "email": manager_email,
            "first_name": "Goutam",
            "last_name": "Vemula",
            "role": "manager",
            "is_active": True
        }
        
        # Check if manager already exists
        existing_manager = await supabase_service.get_user_by_email(manager_email)
        
        if existing_manager:
            print("✅ Manager already exists")
        else:
            # Create User object
            from app.models import User, UserRole
            from datetime import datetime, timezone
            manager_user = User(
                id=manager_id,
                email=manager_email,
                first_name="Goutam",
                last_name="Vemula",
                role=UserRole.MANAGER,
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            await supabase_service.create_user_with_role(manager_user)
            print("✅ Manager user created")
        
        # Store password
        password_manager.store_password(manager_email, manager_password)
        print("✅ Manager password stored")
        
        # Create/verify test property
        property_data = {
            "id": property_id,
            "name": "RCI Hotel",
            "address": "123 Business Street",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94105",
            "phone": "(555) 987-6543",
            "is_active": True
        }
        
        # Check if property exists
        existing_property = await supabase_service.get_property_by_id(property_id)
        
        if existing_property:
            print("✅ Test property already exists")
        else:
            # Create Property object
            property_obj = Property(
                id=property_id,
                name="RCI Hotel",
                address="123 Business Street",
                city="San Francisco",
                state="CA",
                zip_code="94105",
                phone="(555) 987-6543",
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            await supabase_service.create_property_with_managers(property_obj, [manager_id])
            print("✅ Test property created")
        
        # Assign manager to property
        await supabase_service.assign_manager_to_property(manager_id, property_id)
        print("✅ Manager assigned to property")
        
        # Create HR user for completeness
        hr_email = "hr@rcihotel.com"
        hr_password = "hr123"
        hr_id = "hr_rci_001"
        
        hr_data = {
            "id": hr_id,
            "email": hr_email,
            "first_name": "HR",
            "last_name": "Admin",
            "role": "hr",
            "is_active": True
        }
        
        existing_hr = await supabase_service.get_user_by_email(hr_email)
        
        if existing_hr:
            print("✅ HR user already exists")
        else:
            hr_user = User(
                id=hr_id,
                email=hr_email,
                first_name="HR",
                last_name="Admin",
                role=UserRole.HR,
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            await supabase_service.create_user_with_role(hr_user)
            password_manager.store_password(hr_email, hr_password)
            print("✅ HR user created")
        
        print("\n🎉 Setup complete!")
        print("=" * 50)
        print("Manager Account:")
        print(f"  Email: {manager_email}")
        print(f"  Password: {manager_password}")
        print(f"  Property: {property_data['name']}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(setup_manager_account())
    exit(0 if success else 1)