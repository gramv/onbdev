#!/usr/bin/env python3
"""
Unit tests for Property Access Control System
Tests the property access control logic without requiring database connection
"""

import sys
import os
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.property_access_control import PropertyAccessController
from app.models import User, UserRole, Property, JobApplication, Employee, OnboardingSession, OnboardingStatus

class TestPropertyAccessControlUnit:
    """Unit test suite for PropertyAccessController"""
    
    def __init__(self):
        # Mock Supabase service
        self.mock_supabase = Mock()
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
            qr_code_url="http://localhost:3000/apply/prop_001",
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
            qr_code_url="http://localhost:3000/apply/prop_002",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        # Test application
        self.application = JobApplication(
            id="app_001",
            property_id="prop_001",
            department="Front Desk",
            position="Receptionist",
            applicant_data={"first_name": "John", "last_name": "Doe", "email": "john@test.com", "phone": "(555) 123-4567"},
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
        
        # Test onboarding session
        self.onboarding_session = OnboardingSession(
            id="session_001",
            employee_id="emp_001",
            application_id="app_001",
            property_id="prop_001",
            manager_id="mgr_001",
            token="test_token",
            status=OnboardingStatus.IN_PROGRESS,
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
    
    def test_get_manager_properties_success(self):
        """Test successful retrieval of manager properties"""
        print("🧪 Testing get_manager_properties_success...")
        
        # Mock the supabase service to return properties
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1, self.property2]
        
        # Get manager properties
        property_ids = self.access_controller.get_manager_properties("mgr_001")
        
        # Verify results
        assert property_ids == ["prop_001", "prop_002"], f"Expected ['prop_001', 'prop_002'], got {property_ids}"
        self.mock_supabase.get_manager_properties_sync.assert_called_once_with("mgr_001")
        
        print("✅ get_manager_properties_success test passed")
    
    def test_get_manager_properties_empty(self):
        """Test manager with no properties"""
        print("🧪 Testing get_manager_properties_empty...")
        
        # Mock the supabase service to return empty list
        self.mock_supabase.get_manager_properties_sync.return_value = []
        
        # Get manager properties
        property_ids = self.access_controller.get_manager_properties("mgr_002")
        
        # Verify results
        assert property_ids == [], f"Expected [], got {property_ids}"
        self.mock_supabase.get_manager_properties_sync.assert_called_once_with("mgr_002")
        
        print("✅ get_manager_properties_empty test passed")
    
    def test_get_manager_properties_error_handling(self):
        """Test error handling in get_manager_properties"""
        print("🧪 Testing get_manager_properties_error_handling...")
        
        # Mock the supabase service to raise an exception
        self.mock_supabase.get_manager_properties_sync.side_effect = Exception("Database error")
        
        # Get manager properties
        property_ids = self.access_controller.get_manager_properties("mgr_001")
        
        # Verify error handling returns empty list
        assert property_ids == [], f"Expected [], got {property_ids}"
        
        print("✅ get_manager_properties_error_handling test passed")
    
    def test_validate_manager_property_access_success(self):
        """Test successful property access validation"""
        print("🧪 Testing validate_manager_property_access_success...")
        
        # Mock the supabase service
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Validate access
        has_access = self.access_controller.validate_manager_property_access(self.manager_user, "prop_001")
        
        # Verify access granted
        assert has_access is True, f"Expected True, got {has_access}"
        
        print("✅ validate_manager_property_access_success test passed")
    
    def test_validate_manager_property_access_denied(self):
        """Test property access validation denial"""
        print("🧪 Testing validate_manager_property_access_denied...")
        
        # Mock the supabase service to return different property
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property2]
        
        # Validate access
        has_access = self.access_controller.validate_manager_property_access(self.manager_user, "prop_001")
        
        # Verify access denied
        assert has_access is False, f"Expected False, got {has_access}"
        
        print("✅ validate_manager_property_access_denied test passed")
    
    def test_validate_manager_property_access_hr_user(self):
        """Test that HR users are not validated through this method"""
        print("🧪 Testing validate_manager_property_access_hr_user...")
        
        # Validate access for HR user
        has_access = self.access_controller.validate_manager_property_access(self.hr_user, "prop_001")
        
        # Verify HR user access is denied (they should use different validation)
        assert has_access is False, f"Expected False, got {has_access}"
        
        print("✅ validate_manager_property_access_hr_user test passed")
    
    def test_validate_manager_property_access_none_user(self):
        """Test validation with None user"""
        print("🧪 Testing validate_manager_property_access_none_user...")
        
        # Validate access for None user
        has_access = self.access_controller.validate_manager_property_access(None, "prop_001")
        
        # Verify None user access is denied
        assert has_access is False, f"Expected False, got {has_access}"
        
        print("✅ validate_manager_property_access_none_user test passed")
    
    def test_validate_manager_property_access_empty_property_id(self):
        """Test validation with empty property ID"""
        print("🧪 Testing validate_manager_property_access_empty_property_id...")
        
        # Validate access with empty property ID
        has_access = self.access_controller.validate_manager_property_access(self.manager_user, "")
        
        # Verify empty property ID is denied
        assert has_access is False, f"Expected False, got {has_access}"
        
        print("✅ validate_manager_property_access_empty_property_id test passed")
    
    def test_validate_manager_application_access_success(self):
        """Test successful application access validation"""
        print("🧪 Testing validate_manager_application_access_success...")
        
        # Mock the supabase service
        self.mock_supabase.get_application_by_id_sync.return_value = self.application
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Validate access
        has_access = self.access_controller.validate_manager_application_access(self.manager_user, "app_001")
        
        # Verify access granted
        assert has_access is True, f"Expected True, got {has_access}"
        
        print("✅ validate_manager_application_access_success test passed")
    
    def test_validate_manager_application_access_denied(self):
        """Test application access validation denial"""
        print("🧪 Testing validate_manager_application_access_denied...")
        
        # Mock the supabase service - manager has different property
        self.mock_supabase.get_application_by_id_sync.return_value = self.application
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property2]
        
        # Validate access
        has_access = self.access_controller.validate_manager_application_access(self.manager_user, "app_001")
        
        # Verify access denied
        assert has_access is False, f"Expected False, got {has_access}"
        
        print("✅ validate_manager_application_access_denied test passed")
    
    def test_validate_manager_application_access_not_found(self):
        """Test application access validation when application not found"""
        print("🧪 Testing validate_manager_application_access_not_found...")
        
        # Mock the supabase service to return None
        self.mock_supabase.get_application_by_id_sync.return_value = None
        
        # Validate access
        has_access = self.access_controller.validate_manager_application_access(self.manager_user, "app_999")
        
        # Verify access denied
        assert has_access is False, f"Expected False, got {has_access}"
        
        print("✅ validate_manager_application_access_not_found test passed")
    
    def test_validate_manager_employee_access_success(self):
        """Test successful employee access validation"""
        print("🧪 Testing validate_manager_employee_access_success...")
        
        # Mock the supabase service
        self.mock_supabase.get_employee_by_id_sync.return_value = self.employee
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Validate access
        has_access = self.access_controller.validate_manager_employee_access(self.manager_user, "emp_001")
        
        # Verify access granted
        assert has_access is True, f"Expected True, got {has_access}"
        
        print("✅ validate_manager_employee_access_success test passed")
    
    def test_validate_manager_employee_access_denied(self):
        """Test employee access validation denial"""
        print("🧪 Testing validate_manager_employee_access_denied...")
        
        # Mock the supabase service - manager has different property
        self.mock_supabase.get_employee_by_id_sync.return_value = self.employee
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property2]
        
        # Validate access
        has_access = self.access_controller.validate_manager_employee_access(self.manager_user, "emp_001")
        
        # Verify access denied
        assert has_access is False, f"Expected False, got {has_access}"
        
        print("✅ validate_manager_employee_access_denied test passed")
    
    def test_validate_manager_onboarding_access_success(self):
        """Test successful onboarding access validation"""
        print("🧪 Testing validate_manager_onboarding_access_success...")
        
        # Mock the supabase service
        self.mock_supabase.get_onboarding_session_by_id_sync.return_value = self.onboarding_session
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Validate access
        has_access = self.access_controller.validate_manager_onboarding_access(self.manager_user, "session_001")
        
        # Verify access granted
        assert has_access is True, f"Expected True, got {has_access}"
        
        print("✅ validate_manager_onboarding_access_success test passed")
    
    def test_validate_manager_onboarding_access_denied(self):
        """Test onboarding access validation denial"""
        print("🧪 Testing validate_manager_onboarding_access_denied...")
        
        # Mock the supabase service - manager has different property
        self.mock_supabase.get_onboarding_session_by_id_sync.return_value = self.onboarding_session
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property2]
        
        # Validate access
        has_access = self.access_controller.validate_manager_onboarding_access(self.manager_user, "session_001")
        
        # Verify access denied
        assert has_access is False, f"Expected False, got {has_access}"
        
        print("✅ validate_manager_onboarding_access_denied test passed")
    
    def test_cache_functionality(self):
        """Test that caching works correctly"""
        print("🧪 Testing cache_functionality...")
        
        # Mock the supabase service
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Clear cache first
        self.access_controller.clear_manager_cache("mgr_001")
        
        # First call should hit the database
        property_ids1 = self.access_controller.get_manager_properties("mgr_001")
        
        # Second call should use cache
        property_ids2 = self.access_controller.get_manager_properties("mgr_001")
        
        # Verify results are the same
        assert property_ids1 == property_ids2 == ["prop_001"], f"Expected ['prop_001'], got {property_ids1}, {property_ids2}"
        
        # Verify database was only called once
        assert self.mock_supabase.get_manager_properties_sync.call_count == 1, f"Expected 1 call, got {self.mock_supabase.get_manager_properties_sync.call_count}"
        
        print("✅ cache_functionality test passed")
    
    def test_clear_manager_cache(self):
        """Test cache clearing functionality"""
        print("🧪 Testing clear_manager_cache...")
        
        # Mock the supabase service
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # First call should hit the database
        self.access_controller.get_manager_properties("mgr_001")
        
        # Clear cache
        self.access_controller.clear_manager_cache("mgr_001")
        
        # Second call should hit the database again
        self.access_controller.get_manager_properties("mgr_001")
        
        # Verify database was called twice
        assert self.mock_supabase.get_manager_properties_sync.call_count == 2, f"Expected 2 calls, got {self.mock_supabase.get_manager_properties_sync.call_count}"
        
        print("✅ clear_manager_cache test passed")
    
    def test_clear_all_cache(self):
        """Test clear all cache functionality"""
        print("🧪 Testing clear_all_cache...")
        
        # Mock the supabase service
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # Populate cache
        self.access_controller.get_manager_properties("mgr_001")
        
        # Clear all cache
        self.access_controller.clear_all_cache()
        
        # Next call should hit database again
        self.access_controller.get_manager_properties("mgr_001")
        
        # Verify database was called twice
        assert self.mock_supabase.get_manager_properties_sync.call_count == 2, f"Expected 2 calls, got {self.mock_supabase.get_manager_properties_sync.call_count}"
        
        print("✅ clear_all_cache test passed")
    
    def run_all_tests(self):
        """Run all unit tests"""
        print("🚀 Starting Property Access Control Unit Tests")
        print("=" * 60)
        
        tests = [
            self.test_get_manager_properties_success,
            self.test_get_manager_properties_empty,
            self.test_get_manager_properties_error_handling,
            self.test_validate_manager_property_access_success,
            self.test_validate_manager_property_access_denied,
            self.test_validate_manager_property_access_hr_user,
            self.test_validate_manager_property_access_none_user,
            self.test_validate_manager_property_access_empty_property_id,
            self.test_validate_manager_application_access_success,
            self.test_validate_manager_application_access_denied,
            self.test_validate_manager_application_access_not_found,
            self.test_validate_manager_employee_access_success,
            self.test_validate_manager_employee_access_denied,
            self.test_validate_manager_onboarding_access_success,
            self.test_validate_manager_onboarding_access_denied,
            self.test_cache_functionality,
            self.test_clear_manager_cache,
            self.test_clear_all_cache
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                # Reset mocks for each test
                self.mock_supabase.reset_mock()
                self.access_controller.clear_all_cache()
                
                # Run test
                test()
                passed += 1
                
            except Exception as e:
                print(f"❌ {test.__name__}: {str(e)}")
                failed += 1
        
        print(f"\n📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All property access control unit tests passed!")
            return True
        else:
            print("⚠️ Some tests failed. Please review the implementation.")
            return False

def run_unit_tests():
    """Run the unit tests"""
    test_runner = TestPropertyAccessControlUnit()
    return test_runner.run_all_tests()

if __name__ == "__main__":
    success = run_unit_tests()
    sys.exit(0 if success else 1)