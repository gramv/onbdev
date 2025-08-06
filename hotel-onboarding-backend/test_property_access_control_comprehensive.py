#!/usr/bin/env python3
"""
Comprehensive Property Access Control Test
Tests all aspects of the enhanced property access control system
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
from app.models import User, UserRole

class ComprehensivePropertyAccessTest:
    """Comprehensive test suite for property access control"""
    
    def __init__(self):
        self.supabase_service = EnhancedSupabaseService()
        self.access_controller = PropertyAccessController(self.supabase_service)
        
        # Test data IDs
        self.test_property_id = "test_prop_comprehensive_001"
        self.test_property_id_2 = "test_prop_comprehensive_002"
        self.test_manager_id = "test_mgr_comprehensive_001"
        self.test_unauthorized_manager_id = "test_mgr_comprehensive_002"
        self.test_hr_id = "test_hr_comprehensive_001"
        self.test_application_id = "test_app_comprehensive_001"
        self.test_employee_id = "test_emp_comprehensive_001"
        self.test_session_id = "test_session_comprehensive_001"
        
        # JWT secret for token generation
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "test-secret-key")
    
    async def setup_test_data(self):
        """Set up comprehensive test data"""
        print("🔧 Setting up comprehensive test data...")
        
        try:
            # Create test properties
            property_data_1 = {
                "id": self.test_property_id,
                "name": "Test Property 1 - Comprehensive",
                "address": "123 Test Comprehensive St",
                "city": "Test City",
                "state": "CA",
                "zip_code": "12345",
                "phone": "(555) 123-4567",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.supabase_service.create_property(property_data_1)
            
            property_data_2 = {
                "id": self.test_property_id_2,
                "name": "Test Property 2 - Comprehensive",
                "address": "456 Test Comprehensive Ave",
                "city": "Test City",
                "state": "CA",
                "zip_code": "67890",
                "phone": "(555) 987-6543",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.supabase_service.create_property(property_data_2)
            
            # Create HR user
            hr_password_hash = self.supabase_service.hash_password("hr123")
            hr_user_data = {
                "id": self.test_hr_id,
                "email": "hr.comprehensive@test.com",
                "first_name": "HR",
                "last_name": "Comprehensive",
                "role": "hr",
                "password_hash": hr_password_hash,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.supabase_service.create_user(hr_user_data)
            
            # Create authorized manager
            manager_password_hash = self.supabase_service.hash_password("manager123")
            authorized_manager_data = {
                "id": self.test_manager_id,
                "email": "authorized.comprehensive@test.com",
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
                "email": "unauthorized.comprehensive@test.com",
                "first_name": "Unauthorized",
                "last_name": "Manager",
                "role": "manager",
                "password_hash": manager_password_hash,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await self.supabase_service.create_user(unauthorized_manager_data)
            
            # Assign authorized manager to property 1 only
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
            
            # Create test onboarding session
            session_data = {
                "id": self.test_session_id,
                "employee_id": self.test_employee_id,
                "application_id": self.test_application_id,
                "property_id": self.test_property_id,
                "manager_id": self.test_manager_id,
                "token": "test_token_123",
                "status": "in_progress",
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=72)).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Insert session directly into Supabase
            result = self.supabase_service.client.table('onboarding_sessions').insert(session_data).execute()
            
            print("✅ Comprehensive test data setup completed")
            
        except Exception as e:
            print(f"❌ Failed to setup comprehensive test data: {e}")
            raise
    
    async def cleanup_test_data(self):
        """Clean up comprehensive test data"""
        print("🧹 Cleaning up comprehensive test data...")
        
        try:
            # Delete test records in reverse order of creation
            self.supabase_service.client.table('onboarding_sessions').delete().eq('id', self.test_session_id).execute()
            self.supabase_service.client.table('employees').delete().eq('id', self.test_employee_id).execute()
            self.supabase_service.client.table('job_applications').delete().eq('id', self.test_application_id).execute()
            self.supabase_service.client.table('property_managers').delete().eq('manager_id', self.test_manager_id).execute()
            self.supabase_service.client.table('users').delete().eq('id', self.test_manager_id).execute()
            self.supabase_service.client.table('users').delete().eq('id', self.test_unauthorized_manager_id).execute()
            self.supabase_service.client.table('users').delete().eq('id', self.test_hr_id).execute()
            self.supabase_service.client.table('properties').delete().eq('id', self.test_property_id).execute()
            self.supabase_service.client.table('properties').delete().eq('id', self.test_property_id_2).execute()
            
            print("✅ Comprehensive test data cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    async def test_property_access_validation(self):
        """Test comprehensive property access validation"""
        print("🧪 Testing comprehensive property access validation...")
        
        # Get test users
        authorized_manager = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        unauthorized_manager = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        hr_user = self.supabase_service.get_user_by_id_sync(self.test_hr_id)
        
        # Test authorized manager access to assigned property
        has_access = self.access_controller.validate_manager_property_access(
            authorized_manager, self.test_property_id
        )
        assert has_access, "Authorized manager should have access to assigned property"
        
        # Test authorized manager denied access to unassigned property
        has_access = self.access_controller.validate_manager_property_access(
            authorized_manager, self.test_property_id_2
        )
        assert not has_access, "Authorized manager should not have access to unassigned property"
        
        # Test unauthorized manager denied access
        has_access = self.access_controller.validate_manager_property_access(
            unauthorized_manager, self.test_property_id
        )
        assert not has_access, "Unauthorized manager should not have property access"
        
        # Test HR user (should return False as they use different validation)
        has_access = self.access_controller.validate_manager_property_access(
            hr_user, self.test_property_id
        )
        assert not has_access, "HR user should not use manager property validation"
        
        # Test with None user
        has_access = self.access_controller.validate_manager_property_access(
            None, self.test_property_id
        )
        assert not has_access, "None user should not have property access"
        
        # Test with empty property ID
        has_access = self.access_controller.validate_manager_property_access(
            authorized_manager, ""
        )
        assert not has_access, "Empty property ID should be denied"
        
        print("✅ Comprehensive property access validation test passed")
    
    async def test_application_access_validation(self):
        """Test comprehensive application access validation"""
        print("🧪 Testing comprehensive application access validation...")
        
        # Get test users
        authorized_manager = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        unauthorized_manager = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        hr_user = self.supabase_service.get_user_by_id_sync(self.test_hr_id)
        
        # Test authorized manager access to application
        has_access = self.access_controller.validate_manager_application_access(
            authorized_manager, self.test_application_id
        )
        assert has_access, "Authorized manager should have access to application"
        
        # Test unauthorized manager denied access
        has_access = self.access_controller.validate_manager_application_access(
            unauthorized_manager, self.test_application_id
        )
        assert not has_access, "Unauthorized manager should not have application access"
        
        # Test with non-existent application
        has_access = self.access_controller.validate_manager_application_access(
            authorized_manager, "non_existent_app"
        )
        assert not has_access, "Non-existent application should be denied"
        
        # Test with None user
        has_access = self.access_controller.validate_manager_application_access(
            None, self.test_application_id
        )
        assert not has_access, "None user should not have application access"
        
        # Test with empty application ID
        has_access = self.access_controller.validate_manager_application_access(
            authorized_manager, ""
        )
        assert not has_access, "Empty application ID should be denied"
        
        print("✅ Comprehensive application access validation test passed")
    
    async def test_employee_access_validation(self):
        """Test comprehensive employee access validation"""
        print("🧪 Testing comprehensive employee access validation...")
        
        # Get test users
        authorized_manager = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        unauthorized_manager = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        
        # Test authorized manager access to employee
        has_access = self.access_controller.validate_manager_employee_access(
            authorized_manager, self.test_employee_id
        )
        assert has_access, "Authorized manager should have access to employee"
        
        # Test unauthorized manager denied access
        has_access = self.access_controller.validate_manager_employee_access(
            unauthorized_manager, self.test_employee_id
        )
        assert not has_access, "Unauthorized manager should not have employee access"
        
        # Test with non-existent employee
        has_access = self.access_controller.validate_manager_employee_access(
            authorized_manager, "non_existent_emp"
        )
        assert not has_access, "Non-existent employee should be denied"
        
        print("✅ Comprehensive employee access validation test passed")
    
    async def test_onboarding_access_validation(self):
        """Test comprehensive onboarding session access validation"""
        print("🧪 Testing comprehensive onboarding access validation...")
        
        # Get test users
        authorized_manager = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        unauthorized_manager = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        
        # Test authorized manager access to onboarding session
        has_access = self.access_controller.validate_manager_onboarding_access(
            authorized_manager, self.test_session_id
        )
        assert has_access, "Authorized manager should have access to onboarding session"
        
        # Test unauthorized manager denied access
        has_access = self.access_controller.validate_manager_onboarding_access(
            unauthorized_manager, self.test_session_id
        )
        assert not has_access, "Unauthorized manager should not have onboarding access"
        
        # Test with non-existent session
        has_access = self.access_controller.validate_manager_onboarding_access(
            authorized_manager, "non_existent_session"
        )
        assert not has_access, "Non-existent session should be denied"
        
        print("✅ Comprehensive onboarding access validation test passed")
    
    async def test_cache_functionality(self):
        """Test comprehensive cache functionality"""
        print("🧪 Testing comprehensive cache functionality...")
        
        # Clear cache
        self.access_controller.clear_manager_cache(self.test_manager_id)
        
        # First call should populate cache
        property_ids_1 = self.access_controller.get_manager_properties(self.test_manager_id)
        
        # Second call should use cache
        property_ids_2 = self.access_controller.get_manager_properties(self.test_manager_id)
        
        assert property_ids_1 == property_ids_2, "Cached results should be consistent"
        assert self.test_property_id in property_ids_1, "Manager should have access to assigned property"
        assert self.test_property_id_2 not in property_ids_1, "Manager should not have access to unassigned property"
        
        # Test cache clearing
        self.access_controller.clear_manager_cache(self.test_manager_id)
        
        # After clearing, should still get same results
        property_ids_3 = self.access_controller.get_manager_properties(self.test_manager_id)
        assert property_ids_1 == property_ids_3, "Results should be consistent after cache clear"
        
        # Test clear all cache
        self.access_controller.clear_all_cache()
        property_ids_4 = self.access_controller.get_manager_properties(self.test_manager_id)
        assert property_ids_1 == property_ids_4, "Results should be consistent after clear all cache"
        
        print("✅ Comprehensive cache functionality test passed")
    
    async def test_data_filtering(self):
        """Test comprehensive data filtering"""
        print("🧪 Testing comprehensive data filtering...")
        
        # Get test data
        application = self.supabase_service.get_application_by_id_sync(self.test_application_id)
        employee = self.supabase_service.get_employee_by_id_sync(self.test_employee_id)
        
        # Create additional test data for filtering
        app_property_2 = type(application)(
            id="app_prop_2",
            property_id=self.test_property_id_2,
            department="Housekeeping",
            position="Housekeeper",
            applicant_data={},
            status="pending",
            applied_at=datetime.now(timezone.utc)
        )
        
        emp_property_2 = type(employee)(
            id="emp_prop_2",
            property_id=self.test_property_id_2,
            department="Housekeeping",
            position="Housekeeper",
            employment_status="active",
            created_at=datetime.now(timezone.utc)
        )
        
        # Test authorized manager filtering
        authorized_manager = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        
        filtered_apps = self.access_controller.filter_applications_by_manager_access(
            authorized_manager, [application, app_property_2]
        )
        assert len(filtered_apps) == 1, "Should only see applications from assigned property"
        assert filtered_apps[0].id == self.test_application_id, "Should see the correct application"
        
        filtered_emps = self.access_controller.filter_employees_by_manager_access(
            authorized_manager, [employee, emp_property_2]
        )
        assert len(filtered_emps) == 1, "Should only see employees from assigned property"
        assert filtered_emps[0].id == self.test_employee_id, "Should see the correct employee"
        
        # Test unauthorized manager filtering
        unauthorized_manager = self.supabase_service.get_user_by_id_sync(self.test_unauthorized_manager_id)
        
        filtered_apps = self.access_controller.filter_applications_by_manager_access(
            unauthorized_manager, [application, app_property_2]
        )
        assert len(filtered_apps) == 0, "Unauthorized manager should see no applications"
        
        filtered_emps = self.access_controller.filter_employees_by_manager_access(
            unauthorized_manager, [employee, emp_property_2]
        )
        assert len(filtered_emps) == 0, "Unauthorized manager should see no employees"
        
        # Test HR user filtering (should return empty as they use different patterns)
        hr_user = self.supabase_service.get_user_by_id_sync(self.test_hr_id)
        
        filtered_apps = self.access_controller.filter_applications_by_manager_access(
            hr_user, [application, app_property_2]
        )
        assert len(filtered_apps) == 0, "HR user should not use manager filtering"
        
        print("✅ Comprehensive data filtering test passed")
    
    async def test_error_handling(self):
        """Test comprehensive error handling"""
        print("🧪 Testing comprehensive error handling...")
        
        # Test with invalid manager ID
        property_ids = self.access_controller.get_manager_properties("invalid_manager_id")
        assert property_ids == [], "Invalid manager ID should return empty list"
        
        # Test validation with invalid data
        authorized_manager = self.supabase_service.get_user_by_id_sync(self.test_manager_id)
        
        # Test with invalid property ID
        has_access = self.access_controller.validate_manager_property_access(
            authorized_manager, "invalid_property_id"
        )
        assert not has_access, "Invalid property ID should be denied"
        
        # Test with invalid application ID
        has_access = self.access_controller.validate_manager_application_access(
            authorized_manager, "invalid_application_id"
        )
        assert not has_access, "Invalid application ID should be denied"
        
        # Test with invalid employee ID
        has_access = self.access_controller.validate_manager_employee_access(
            authorized_manager, "invalid_employee_id"
        )
        assert not has_access, "Invalid employee ID should be denied"
        
        # Test with invalid session ID
        has_access = self.access_controller.validate_manager_onboarding_access(
            authorized_manager, "invalid_session_id"
        )
        assert not has_access, "Invalid session ID should be denied"
        
        print("✅ Comprehensive error handling test passed")
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Property Access Control Tests")
        print("=" * 70)
        
        try:
            # Setup test data
            await self.setup_test_data()
            
            # Run all tests
            await self.test_property_access_validation()
            await self.test_application_access_validation()
            await self.test_employee_access_validation()
            await self.test_onboarding_access_validation()
            await self.test_cache_functionality()
            await self.test_data_filtering()
            await self.test_error_handling()
            
            print("\n🎉 All comprehensive tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Comprehensive test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Cleanup test data
            await self.cleanup_test_data()

async def run_comprehensive_tests():
    """Run the comprehensive tests"""
    test_runner = ComprehensivePropertyAccessTest()
    return await test_runner.run_all_tests()

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)