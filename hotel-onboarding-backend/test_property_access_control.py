#!/usr/bin/env python3
"""
Comprehensive tests for Manager Property Access Control
Tests the property access control system for manager operations
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.property_access_control import PropertyAccessController, PropertyAccessError
from app.models import User, UserRole, Property, JobApplication, Employee
from app.supabase_service_enhanced import EnhancedSupabaseService

class TestPropertyAccessController:
    """Test suite for PropertyAccessController"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Mock Supabase service
        self.mock_supabase = Mock(spec=EnhancedSupabaseService)
        self.access_controller = PropertyAccessController(self.mock_supabase)
        
        # Test users
        self.hr_user = User(
            id="hr_001",
            email="hr@test.com",
            first_name="HR",
            last_name="Admin",
            role=UserRole.HR,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        self.manager_user = User(
            id="mgr_001",
            email="manager@test.com",
            first_name="Manager",
            last_name="User",
            role=UserRole.MANAGER,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        self.unauthorized_manager = User(
            id="mgr_002",
            email="unauthorized@test.com",
            first_name="Unauthorized",
            last_name="Manager",
            role=UserRole.MANAGER,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        # Test properties
        self.property1 = Property(
            id="prop_001",
            name="Hotel A",
            address="123 Main St",
            city="City A",
            state="CA",
            zip_code="12345",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        self.property2 = Property(
            id="prop_002",
            name="Hotel B",
            address="456 Oak St",
            city="City B",
            state="CA",
            zip_code="67890",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        # Test application
        self.application = JobApplication(
            id="app_001",
            property_id="prop_001",
            department="Front Desk",
            position="Receptionist",
            applicant_data={"first_name": "John", "last_name": "Doe", "email": "john@test.com"},
            status="pending",
            applied_at=datetime.now(timezone.utc)
        )
        
        # Test employee
        self.employee = Employee(
            id="emp_001",
            property_id="prop_001",
            department="Front Desk",
            position="Receptionist",
            employment_status="active",
            created_at=datetime.now(timezone.utc)
        )
    
    def test_get_manager_properties_success(self):
        """Test successful retrieval of manager properties"""
        # Mock the supabase service to return properties
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1, self.property2]
        
        # Get manager properties
        property_ids = self.access_controller.get_manager_properties("mgr_001")
        
        # Verify results
        assert property_ids == ["prop_001", "prop_002"]
        self.mock_supabase.get_manager_properties_sync.assert_called_once_with("mgr_001")
    
    def test_get_manager_properties_empty(self):
        """Test manager with no properties"""
        # Mock the supabase service to return empty list
        self.mock_supabase.get_manager_properties_sync.return_value = []
        
        # Get manager properties
        property_ids = self.access_controller.get_manager_properties("mgr_002")
        
        # Verify results
        assert property_ids == []
        self.mock_supabase.get_manager_properties_sync.assert_called_once_with("mgr_002")
    
    def test_get_manager_properties_error_handling(self):
        """Test error handling in get_manager_properties"""
        # Mock the supabase service to raise an exception
        self.mock_supabase.get_manager_properties_sync.side_effect = Exception("Database error")
        
        # Get manager properties
        property_ids = self.access_controller.get_manager_properties("mgr_001")
        
        # Verify error handling returns empty list
        assert property_ids == []
    
    def test_validate_manager_property_access_success(self):
        """Test successful property access validation"""
        # Mock the supabase service
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Validate access
        has_access = self.access_controller.validate_manager_property_access(self.manager_user, "prop_001")
        
        # Verify access granted
        assert has_access is True
    
    def test_validate_manager_property_access_denied(self):
        """Test property access validation denial"""
        # Mock the supabase service to return different property
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property2]
        
        # Validate access
        has_access = self.access_controller.validate_manager_property_access(self.manager_user, "prop_001")
        
        # Verify access denied
        assert has_access is False
    
    def test_validate_manager_property_access_hr_user(self):
        """Test that HR users are not validated through this method"""
        # Validate access for HR user
        has_access = self.access_controller.validate_manager_property_access(self.hr_user, "prop_001")
        
        # Verify HR user access is denied (they should use different validation)
        assert has_access is False
    
    def test_validate_manager_application_access_success(self):
        """Test successful application access validation"""
        # Mock the supabase service
        self.mock_supabase.get_application_by_id_sync.return_value = self.application
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Validate access
        has_access = self.access_controller.validate_manager_application_access(self.manager_user, "app_001")
        
        # Verify access granted
        assert has_access is True
    
    def test_validate_manager_application_access_denied(self):
        """Test application access validation denial"""
        # Mock the supabase service - manager has different property
        self.mock_supabase.get_application_by_id_sync.return_value = self.application
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property2]
        
        # Validate access
        has_access = self.access_controller.validate_manager_application_access(self.manager_user, "app_001")
        
        # Verify access denied
        assert has_access is False
    
    def test_validate_manager_application_access_not_found(self):
        """Test application access validation when application not found"""
        # Mock the supabase service to return None
        self.mock_supabase.get_application_by_id_sync.return_value = None
        
        # Validate access
        has_access = self.access_controller.validate_manager_application_access(self.manager_user, "app_999")
        
        # Verify access denied
        assert has_access is False
    
    def test_validate_manager_employee_access_success(self):
        """Test successful employee access validation"""
        # Mock the supabase service
        self.mock_supabase.get_employee_by_id_sync.return_value = self.employee
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Validate access
        has_access = self.access_controller.validate_manager_employee_access(self.manager_user, "emp_001")
        
        # Verify access granted
        assert has_access is True
    
    def test_validate_manager_employee_access_denied(self):
        """Test employee access validation denial"""
        # Mock the supabase service - manager has different property
        self.mock_supabase.get_employee_by_id_sync.return_value = self.employee
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property2]
        
        # Validate access
        has_access = self.access_controller.validate_manager_employee_access(self.manager_user, "emp_001")
        
        # Verify access denied
        assert has_access is False
    
    def test_get_manager_accessible_properties(self):
        """Test getting all accessible properties for a manager"""
        # Mock the supabase service
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1, self.property2]
        
        # Get accessible properties
        property_ids = self.access_controller.get_manager_accessible_properties(self.manager_user)
        
        # Verify results
        assert property_ids == ["prop_001", "prop_002"]
    
    def test_get_manager_accessible_properties_hr_user(self):
        """Test that HR users get empty list (they have different access patterns)"""
        # Get accessible properties for HR user
        property_ids = self.access_controller.get_manager_accessible_properties(self.hr_user)
        
        # Verify HR user gets empty list
        assert property_ids == []
    
    def test_filter_applications_by_manager_access(self):
        """Test filtering applications by manager access"""
        # Create test applications
        app1 = JobApplication(
            id="app_001", property_id="prop_001", department="Front Desk", 
            position="Receptionist", applicant_data={}, status="pending",
            applied_at=datetime.now(timezone.utc)
        )
        app2 = JobApplication(
            id="app_002", property_id="prop_002", department="Housekeeping", 
            position="Housekeeper", applicant_data={}, status="pending",
            applied_at=datetime.now(timezone.utc)
        )
        app3 = JobApplication(
            id="app_003", property_id="prop_003", department="Kitchen", 
            position="Cook", applicant_data={}, status="pending",
            applied_at=datetime.now(timezone.utc)
        )
        
        applications = [app1, app2, app3]
        
        # Mock manager has access to prop_001 and prop_002
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1, self.property2]
        
        # Filter applications
        filtered_apps = self.access_controller.filter_applications_by_manager_access(self.manager_user, applications)
        
        # Verify only accessible applications are returned
        assert len(filtered_apps) == 2
        assert filtered_apps[0].id == "app_001"
        assert filtered_apps[1].id == "app_002"
    
    def test_filter_employees_by_manager_access(self):
        """Test filtering employees by manager access"""
        # Create test employees
        emp1 = Employee(
            id="emp_001", property_id="prop_001", department="Front Desk", 
            position="Receptionist", employment_status="active",
            created_at=datetime.now(timezone.utc)
        )
        emp2 = Employee(
            id="emp_002", property_id="prop_002", department="Housekeeping", 
            position="Housekeeper", employment_status="active",
            created_at=datetime.now(timezone.utc)
        )
        emp3 = Employee(
            id="emp_003", property_id="prop_003", department="Kitchen", 
            position="Cook", employment_status="active",
            created_at=datetime.now(timezone.utc)
        )
        
        employees = [emp1, emp2, emp3]
        
        # Mock manager has access to prop_001 and prop_002
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1, self.property2]
        
        # Filter employees
        filtered_emps = self.access_controller.filter_employees_by_manager_access(self.manager_user, employees)
        
        # Verify only accessible employees are returned
        assert len(filtered_emps) == 2
        assert filtered_emps[0].id == "emp_001"
        assert filtered_emps[1].id == "emp_002"
    
    def test_cache_functionality(self):
        """Test that caching works correctly"""
        # Mock the supabase service
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # First call should hit the database
        property_ids1 = self.access_controller.get_manager_properties("mgr_001")
        
        # Second call should use cache
        property_ids2 = self.access_controller.get_manager_properties("mgr_001")
        
        # Verify results are the same
        assert property_ids1 == property_ids2 == ["prop_001"]
        
        # Verify database was only called once
        assert self.mock_supabase.get_manager_properties_sync.call_count == 1
    
    def test_clear_manager_cache(self):
        """Test cache clearing functionality"""
        # Mock the supabase service
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # First call should hit the database
        self.access_controller.get_manager_properties("mgr_001")
        
        # Clear cache
        self.access_controller.clear_manager_cache("mgr_001")
        
        # Second call should hit the database again
        self.access_controller.get_manager_properties("mgr_001")
        
        # Verify database was called twice
        assert self.mock_supabase.get_manager_properties_sync.call_count == 2

def run_property_access_tests():
    """Run all property access control tests"""
    print("🧪 Running Property Access Control Tests...")
    
    # Create test instance
    test_instance = TestPropertyAccessController()
    
    # List of test methods
    test_methods = [
        'test_get_manager_properties_success',
        'test_get_manager_properties_empty',
        'test_get_manager_properties_error_handling',
        'test_validate_manager_property_access_success',
        'test_validate_manager_property_access_denied',
        'test_validate_manager_property_access_hr_user',
        'test_validate_manager_application_access_success',
        'test_validate_manager_application_access_denied',
        'test_validate_manager_application_access_not_found',
        'test_validate_manager_employee_access_success',
        'test_validate_manager_employee_access_denied',
        'test_get_manager_accessible_properties',
        'test_get_manager_accessible_properties_hr_user',
        'test_filter_applications_by_manager_access',
        'test_filter_employees_by_manager_access',
        'test_cache_functionality',
        'test_clear_manager_cache'
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            # Set up test
            test_instance.setup_method()
            
            # Run test
            getattr(test_instance, test_method)()
            
            print(f"✅ {test_method}")
            passed += 1
            
        except Exception as e:
            print(f"❌ {test_method}: {str(e)}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All property access control tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = run_property_access_tests()
    sys.exit(0 if success else 1)