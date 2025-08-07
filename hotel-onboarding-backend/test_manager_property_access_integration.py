#!/usr/bin/env python3
"""
Integration tests for Manager Property Access Control
Tests the complete property access control system with actual API endpoints
"""

import asyncio
import sys
import os
import json
import jwt
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.supabase_service_enhanced import EnhancedSupabaseService
from app.property_access_control import PropertyAccessController

class ManagerPropertyAccessIntegrationTest:
    """Integration test suite for manager property access control"""
    
    def __init__(self):
        self.supabase_service = EnhancedSupabaseService()
        self.access_controller = PropertyAccessController(self.supabase_service)
        
        # Test data IDs
        self.test_property_id = "test_prop_access_001"
        self.test_manager_id = "test_mgr_access_001"
        self.test_unauthorized_manager_id = "test_mgr_access_002"
        self.test_application_id = "test_app_access_001"
        self.test_employee_id = "test_emp_access_001"
        
        # JWT secret for token generation
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "test-secret-key")
    
    async def setup_test_data(self):
        """Set up test data for integration tests"""
        print("🔧 Setting up test data...")
        
        try:
            # Create test property
            property_data = {
                "id": self.test_property_id,
                "name": "Test Property Access Hotel",
                "address": "123 Test Access St",
                "city": "Test City",
                "state": "CA",
                "zip_code": "12345",
                "phone": "(555) 123-4567",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.supabase_service.create_property(property_data)
            
            # Create authorized manager
            manager_password_hash = self.supabase_service.hash_password("manager123")
            authorized_manager_data = {
                "id": self.test_manager_id,
                "email": "authorized.manager@test.com",
                "first_name": "Authorized",
                "last_name": "Manager",
                "role": "manager",
                "password_hash": manager_password_hash,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.supabase_service.create_user(authorized_manager_data)
            
            # Create unauthorized manager
            unauthorized_manager_data = {
                "id": self.test_unauthorized_manager_id,
                "email": "unauthorized.manager@test.com",
                "first_name": "Unauthorized",
                "last_name": "Manager",
                "role": "manager",
                "password_hash": manager_password_hash,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.supabase_service.create_user(unauthorized_manager_data)
            
            # Assign authorized manager to property
            await self.supabase_service.assign_manager_to_property(
                self.test_manager_id, 
                self.test_property_id
            )
            
            # Create test application
            application_data = {
                "id": self.test_application_id,
                "property_id": self.test_property_id,
                "department": "Front Desk",
                "position": "Receptionist",
                "applicant_data": {
                    "first_name": "Test",
                    "last_name": "Applicant",
                    "email": "test.applicant@test.com",
                    "phone": "(555) 987-6543"
                },
                "status": "pending",
                "applied_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Insert application directly into Supabase
            result = self.supabase_service.client.table('job_applications').insert(application_data).execute()
            
            # Create test employee
            employee_data = {
                "id": self.test_employee_id,
                "property_id": self.test_property_id,
                "department": "Front Desk",
                "position": "Receptionist",
                "employment_status": "active",
                "onboarding_status": "completed",
                "hire_date": datetime.now(timezone.utc).date().isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Insert employee directly into Supabase
            result = self.supabase_service.client.table('employees').insert(employee_data).execute()
            
            print("✅ Test data setup completed")
            
        except Exception as e:
            print(f"❌ Failed to setup test data: {e}")
            raise
    
    async def cleanup_test_data(self):
        """Clean up test data after tests"""
        print("🧹 Cleaning up test data...")
        
        try:
            # Delete test records
            self.supabase_service.client.table('employees').delete().eq('id', self.test_employee_id).execute()
            self.supabase_service.client.table('job_applications').delete().eq('id', self.test_application_id).execute()
            self.supabase_service.client.table('property_managers').delete().eq('manager_id', self.test_manager_id).execute()
            self.supabase_service.client.table('users').delete().eq('id', self.test_manager_id).execute()
            self.supabase_service.client.table('users').delete().eq('id', self.test_unauthorized_manager_id).execute()
            self.supabase_service.client.table('properties').delete().eq('id', self.test_property_id).execute()
            
            print("✅ Test data cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def generate_manager_token(self, manager_id: str) -> str:
        """Generate JWT token for manager authentication"""
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "manager_id": manager_id,
            "role": "manager",
            "token_type": "manager_auth",
            "exp": expire
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    async def test_property_access_validation(self):
        """Test property access validation"""
        print("🧪 Testing property access validation...")
        
        # Test authorized manager
        authorized_user = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        has_access = self.access_controller.validate_manager_property_access(
            authorized_user, 
            self.test_property_id
        )
        assert has_access, "Authorized manager should have property access"
        
        # Test unauthorized manager
        unauthorized_user = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        has_access = self.access_controller.validate_manager_property_access(
            unauthorized_user, 
            self.test_property_id
        )
        assert not has_access, "Unauthorized manager should not have property access"
        
        print("✅ Property access validation test passed")
    
    async def test_application_access_validation(self):
        """Test application access validation"""
        print("🧪 Testing application access validation...")
        
        # Test authorized manager
        authorized_user = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        has_access = self.access_controller.validate_manager_application_access(
            authorized_user, 
            self.test_application_id
        )
        assert has_access, "Authorized manager should have application access"
        
        # Test unauthorized manager
        unauthorized_user = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        has_access = self.access_controller.validate_manager_application_access(
            unauthorized_user, 
            self.test_application_id
        )
        assert not has_access, "Unauthorized manager should not have application access"
        
        print("✅ Application access validation test passed")
    
    async def test_employee_access_validation(self):
        """Test employee access validation"""
        print("🧪 Testing employee access validation...")
        
        # Test authorized manager
        authorized_user = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        has_access = self.access_controller.validate_manager_employee_access(
            authorized_user, 
            self.test_employee_id
        )
        assert has_access, "Authorized manager should have employee access"
        
        # Test unauthorized manager
        unauthorized_user = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        has_access = self.access_controller.validate_manager_employee_access(
            unauthorized_user, 
            self.test_employee_id
        )
        assert not has_access, "Unauthorized manager should not have employee access"
        
        print("✅ Employee access validation test passed")
    
    async def test_manager_accessible_properties(self):
        """Test getting manager accessible properties"""
        print("🧪 Testing manager accessible properties...")
        
        # Test authorized manager
        authorized_user = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        property_ids = self.access_controller.get_manager_accessible_properties(authorized_user)
        assert self.test_property_id in property_ids, "Authorized manager should have access to test property"
        
        # Test unauthorized manager
        unauthorized_user = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        property_ids = self.access_controller.get_manager_accessible_properties(unauthorized_user)
        assert self.test_property_id not in property_ids, "Unauthorized manager should not have access to test property"
        
        print("✅ Manager accessible properties test passed")
    
    async def test_data_filtering(self):
        """Test data filtering by manager access"""
        print("🧪 Testing data filtering by manager access...")
        
        # Get test data
        application = self.supabase_service.get_application_by_id_sync(self.test_application_id)
        employee = self.supabase_service.get_employee_by_id_sync(self.test_employee_id)
        
        # Test authorized manager filtering
        authorized_user = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        
        filtered_apps = self.access_controller.filter_applications_by_manager_access(
            authorized_user, [application]
        )
        assert len(filtered_apps) == 1, "Authorized manager should see the application"
        
        filtered_emps = self.access_controller.filter_employees_by_manager_access(
            authorized_user, [employee]
        )
        assert len(filtered_emps) == 1, "Authorized manager should see the employee"
        
        # Test unauthorized manager filtering
        unauthorized_user = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        
        filtered_apps = self.access_controller.filter_applications_by_manager_access(
            unauthorized_user, [application]
        )
        assert len(filtered_apps) == 0, "Unauthorized manager should not see the application"
        
        filtered_emps = self.access_controller.filter_employees_by_manager_access(
            unauthorized_user, [employee]
        )
        assert len(filtered_emps) == 0, "Unauthorized manager should not see the employee"
        
        print("✅ Data filtering test passed")
    
    async def test_cache_functionality(self):
        """Test caching functionality"""
        print("🧪 Testing cache functionality...")
        
        # Clear any existing cache
        self.access_controller.clear_manager_cache(self.test_manager_id)
        
        # First call should populate cache
        property_ids_1 = self.access_controller.get_manager_properties(self.test_manager_id)
        
        # Second call should use cache (we can't easily verify this without mocking, 
        # but we can verify the results are consistent)
        property_ids_2 = self.access_controller.get_manager_properties(self.test_manager_id)
        
        assert property_ids_1 == property_ids_2, "Cached results should be consistent"
        assert self.test_property_id in property_ids_1, "Manager should have access to test property"
        
        # Test cache clearing
        self.access_controller.clear_manager_cache(self.test_manager_id)
        
        # After clearing, should still get same results
        property_ids_3 = self.access_controller.get_manager_properties(self.test_manager_id)
        assert property_ids_1 == property_ids_3, "Results should be consistent after cache clear"
        
        print("✅ Cache functionality test passed")
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Manager Property Access Control Integration Tests")
        print("=" * 60)
        
        try:
            # Setup test data
            await self.setup_test_data()
            
            # Run tests
            await self.test_property_access_validation()
            await self.test_application_access_validation()
            await self.test_employee_access_validation()
            await self.test_manager_accessible_properties()
            await self.test_data_filtering()
            await self.test_cache_functionality()
            
            print("\n🎉 All integration tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Integration test failed: {e}")
            return False
            
        finally:
            # Cleanup test data
            await self.cleanup_test_data()

async def run_integration_tests():
    """Run the integration tests"""
    test_runner = ManagerPropertyAccessIntegrationTest()
    return await test_runner.run_all_tests()

if __name__ == "__main__":
    success = asyncio.run(run_integration_tests())
    sys.exit(0 if success else 1)