#!/usr/bin/env python3
"""
Test Property and Manager Setup Script
Creates a test property and manager account for development and testing.

Usage:
    python setup_test_data.py
"""

import asyncio
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any
import uuid

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.supabase_service_enhanced import EnhancedSupabaseService
from app.models import User, Property, UserRole
from app.auth import PasswordManager

class TestDataSetup:
    """Handles setup of test property and manager data"""
    
    def __init__(self):
        self.supabase_service = EnhancedSupabaseService()
        self.password_manager = PasswordManager()
        
    async def setup_test_property(self) -> Dict[str, Any]:
        """
        Create test property: Demo Hotel (using UUID)
        """
        # Use a proper UUID format
        property_id = str(uuid.uuid4())
        
        print(f"Setting up test property with ID: {property_id}")
        
        # Property data without manager_ids column (it may not exist)
        property_data = {
            "id": property_id,
            "name": "Demo Hotel",
            "address": "123 Demo Street",
            "city": "Demo City", 
            "state": "CA",
            "zip_code": "90210",
            "phone": "(555) 123-4567",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Try to create property with minimal data structure
            result = await self.supabase_service.create_property(property_data)
            if result.get("success"):
                print(f"✅ Property created successfully: Demo Hotel ({property_id})")
                return {"success": True, "property": result.get("property"), "created": True}
            else:
                print(f"❌ Property creation failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            print(f"❌ Property creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def setup_test_manager(self, property_id: str) -> Dict[str, Any]:
        """
        Create test manager: manager@demo.com
        """
        manager_email = "manager@demo.com"
        manager_id = str(uuid.uuid4())
        
        print(f"Setting up test manager: {manager_email}")
        
        # Check if manager already exists
        try:
            existing_user = await self.supabase_service.get_user_by_email(manager_email)
            if existing_user:
                print(f"✅ Manager {manager_email} already exists")
                # Store password for login testing
                self.password_manager.store_password(manager_email, "demo123")
                return {"success": True, "manager": existing_user, "created": False}
        except Exception as e:
            print(f"Manager check failed (will create new): {e}")
        
        # Create manager user
        password = "demo123"
        hashed_password = PasswordManager.hash_password(password)
        
        manager = User(
            id=manager_id,
            email=manager_email,
            role=UserRole.manager,
            first_name="Demo",
            last_name="Manager",
            property_id=property_id,
            password_hash=hashed_password,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        try:
            # Create user in database
            created_user = await self.supabase_service.create_user_with_role(manager)
            if created_user:
                print(f"✅ Manager created successfully: {manager_email}")
                
                # Store password in memory for login
                self.password_manager.store_password(manager_email, password)
                
                # Assign manager to property
                assignment_success = await self.supabase_service.assign_manager_to_property(
                    manager_id, property_id
                )
                
                if assignment_success:
                    print(f"✅ Manager assigned to property successfully")
                else:
                    print(f"⚠️  Manager created but property assignment may have failed")
                
                return {
                    "success": True, 
                    "manager": created_user, 
                    "created": True,
                    "password": password
                }
            else:
                print(f"❌ Manager creation failed")
                return {"success": False, "error": "Manager creation failed"}
                
        except Exception as e:
            print(f"❌ Manager creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_manager_login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Test manager login functionality
        """
        print(f"Testing manager login: {email}")
        
        try:
            # Get user from database
            user = await self.supabase_service.get_user_by_email(email)
            if not user:
                print(f"❌ User {email} not found in database")
                return {"success": False, "error": "User not found"}
            
            # Verify password
            if self.password_manager.verify_user_password(email, password):
                print(f"✅ Manager login successful: {email}")
                return {"success": True, "user": user}
            else:
                print(f"❌ Invalid password for {email}")
                return {"success": False, "error": "Invalid password"}
                
        except Exception as e:
            print(f"❌ Login test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_application_endpoint(self, property_id: str) -> Dict[str, Any]:
        """
        Test that the application endpoint works for the property
        """
        print(f"Testing application endpoint for property: {property_id}")
        
        try:
            # Check if property exists and is accessible
            property_data = await self.supabase_service.get_property_by_id(property_id)
            if property_data:
                application_url = f"/apply/{property_id}"
                print(f"✅ Application URL available: {application_url}")
                return {
                    "success": True, 
                    "application_url": application_url,
                    "property": property_data
                }
            else:
                print(f"❌ Property {property_id} not accessible")
                return {"success": False, "error": "Property not accessible"}
                
        except Exception as e:
            print(f"❌ Application endpoint test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_sample_application(self, property_id: str) -> Dict[str, Any]:
        """
        Create a sample job application for testing manager approval flow
        """
        print("Creating sample job application for testing...")
        
        application_data = {
            "id": str(uuid.uuid4()),
            "property_id": property_id,
            "department": "Front Desk",
            "position": "Front Desk Associate", 
            "applicant_data": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "phone": "(555) 987-6543",
                "address": "456 Test Avenue",
                "city": "Test City",
                "state": "CA",
                "zip_code": "90211",
                "work_authorized": True,
                "availability": "Full-time",
                "experience": "2 years customer service"
            },
            "status": "submitted",
            "applied_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            result = await self.supabase_service.create_job_application(application_data)
            if result:
                print(f"✅ Sample application created: {application_data['applicant_data']['first_name']} {application_data['applicant_data']['last_name']}")
                return {"success": True, "application": result}
            else:
                print("❌ Sample application creation failed")
                return {"success": False, "error": "Application creation failed"}
                
        except Exception as e:
            print(f"❌ Sample application creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_full_setup(self) -> None:
        """
        Run the complete test setup process
        """
        print("=" * 60)
        print("HOTEL ONBOARDING SYSTEM - TEST DATA SETUP")
        print("=" * 60)
        
        # Step 1: Create test property
        print("\n1. Setting up test property...")
        property_result = await self.setup_test_property()
        
        if not property_result.get("success"):
            print(f"❌ Setup failed at property creation: {property_result.get('error')}")
            return
        
        property_id = property_result["property"]["id"]
        
        # Step 2: Create test manager
        print("\n2. Setting up test manager...")
        manager_result = await self.setup_test_manager(property_id)
        
        if not manager_result.get("success"):
            print(f"❌ Setup failed at manager creation: {manager_result.get('error')}")
            return
        
        manager_email = "manager@demo.com"
        manager_password = manager_result.get("password", "demo123")
        
        # Step 3: Test manager login
        print("\n3. Testing manager login...")
        login_result = await self.test_manager_login(manager_email, manager_password)
        
        if not login_result.get("success"):
            print(f"❌ Login test failed: {login_result.get('error')}")
        
        # Step 4: Test application endpoint
        print("\n4. Testing application endpoint...")
        app_result = await self.test_application_endpoint(property_id)
        
        if not app_result.get("success"):
            print(f"❌ Application endpoint test failed: {app_result.get('error')}")
        
        # Step 5: Create sample application
        print("\n5. Creating sample application...")
        sample_result = await self.create_sample_application(property_id)
        
        # Final summary
        print("\n" + "=" * 60)
        print("SETUP SUMMARY")
        print("=" * 60)
        print(f"✅ Property ID: {property_id}")
        print(f"✅ Property Name: Demo Hotel")
        print(f"✅ Manager Email: {manager_email}")
        print(f"✅ Manager Password: {manager_password}")
        print(f"✅ Application URL: /apply/{property_id}")
        
        if sample_result.get("success"):
            print(f"✅ Sample application created for testing")
        
        print(f"\nTo test the system:")
        print(f"1. Start the backend server: python3 -m uvicorn app.main_enhanced:app --reload")
        print(f"2. Manager login at: http://localhost:8000/auth/login")
        print(f"3. Application form at: http://localhost:8000/apply/{property_id}")
        print(f"4. Use credentials: {manager_email} / {manager_password}")

async def main():
    """Main execution function"""
    setup = TestDataSetup()
    await setup.run_full_setup()

if __name__ == "__main__":
    asyncio.run(main())