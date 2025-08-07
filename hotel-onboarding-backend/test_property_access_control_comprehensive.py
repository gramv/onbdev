#!/usr/bin/env python3
"""
Comprehensive test suite for property access control
Tests all scenarios for manager property-based access restrictions
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
import uuid
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.property_access_control import (
    PropertyAccessController, 
    PropertyAccessError,
    get_property_access_controller,
    require_property_access,
    require_application_access,
    require_employee_access,
    require_manager_with_property_access,
    require_onboarding_access
)
from app.models import User, UserRole
from app.supabase_service_enhanced import EnhancedSupabaseService
from fastapi import HTTPException


class TestPropertyAccessController:
    """Test PropertyAccessController class methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_supabase = Mock(spec=EnhancedSupabaseService)
        self.controller = PropertyAccessController(self.mock_supabase)
        
        # Create test users
        self.hr_user = Mock(spec=User, id="hr-123", role=UserRole.HR)
        self.manager1 = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
        self.manager2 = Mock(spec=User, id="mgr-2", role=UserRole.MANAGER)
        
        # Create test properties
        self.property1 = Mock(id="prop-1", name="Hotel A")
        self.property2 = Mock(id="prop-2", name="Hotel B")
        self.property3 = Mock(id="prop-3", name="Hotel C")
        
        # Create test entities
        self.application1 = Mock(id="app-1", property_id="prop-1")
        self.application2 = Mock(id="app-2", property_id="prop-2")
        self.employee1 = Mock(id="emp-1", property_id="prop-1")
        self.employee2 = Mock(id="emp-2", property_id="prop-2")
        self.session1 = Mock(id="sess-1", property_id="prop-1")
        self.session2 = Mock(id="sess-2", property_id="prop-2")
    
    def test_get_manager_properties_success(self):
        """Test successful retrieval of manager properties"""
        # Setup mock
        self.mock_supabase.get_manager_properties_sync.return_value = [
            self.property1, 
            self.property2
        ]
        
        # Test
        properties = self.controller.get_manager_properties("mgr-1")
        
        # Verify
        assert properties == ["prop-1", "prop-2"]
        self.mock_supabase.get_manager_properties_sync.assert_called_once_with("mgr-1")
    
    def test_get_manager_properties_with_cache(self):
        """Test property caching functionality"""
        # Setup mock
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # First call - should hit database
        properties1 = self.controller.get_manager_properties("mgr-1")
        assert properties1 == ["prop-1"]
        assert self.mock_supabase.get_manager_properties_sync.call_count == 1
        
        # Second call - should use cache
        properties2 = self.controller.get_manager_properties("mgr-1")
        assert properties2 == ["prop-1"]
        assert self.mock_supabase.get_manager_properties_sync.call_count == 1  # No additional call
    
    def test_get_manager_properties_cache_expiry(self):
        """Test that cache expires after TTL"""
        # Setup mock
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        # First call
        properties1 = self.controller.get_manager_properties("mgr-1")
        
        # Manually expire cache
        self.controller._cache_timestamps["mgr-1"] = datetime.now().timestamp() - 400  # Beyond TTL
        
        # Second call should hit database again
        properties2 = self.controller.get_manager_properties("mgr-1")
        assert self.mock_supabase.get_manager_properties_sync.call_count == 2
    
    def test_get_manager_properties_empty(self):
        """Test manager with no properties"""
        self.mock_supabase.get_manager_properties_sync.return_value = []
        
        properties = self.controller.get_manager_properties("mgr-1")
        assert properties == []
    
    def test_get_manager_properties_error_handling(self):
        """Test error handling in property retrieval"""
        self.mock_supabase.get_manager_properties_sync.side_effect = Exception("DB Error")
        
        properties = self.controller.get_manager_properties("mgr-1")
        assert properties == []  # Returns empty list on error
    
    def test_clear_manager_cache(self):
        """Test clearing cache for specific manager"""
        # Setup cache
        self.controller._manager_property_cache["mgr-1"] = ["prop-1"]
        self.controller._cache_timestamps["mgr-1"] = datetime.now().timestamp()
        
        # Clear cache
        self.controller.clear_manager_cache("mgr-1")
        
        # Verify
        assert "mgr-1" not in self.controller._manager_property_cache
        assert "mgr-1" not in self.controller._cache_timestamps
    
    def test_clear_all_cache(self):
        """Test clearing all cached data"""
        # Setup cache
        self.controller._manager_property_cache = {"mgr-1": ["prop-1"], "mgr-2": ["prop-2"]}
        self.controller._cache_timestamps = {"mgr-1": 123, "mgr-2": 456}
        
        # Clear all
        self.controller.clear_all_cache()
        
        # Verify
        assert len(self.controller._manager_property_cache) == 0
        assert len(self.controller._cache_timestamps) == 0
    
    def test_validate_manager_property_access_success(self):
        """Test successful property access validation"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        result = self.controller.validate_manager_property_access(self.manager1, "prop-1")
        assert result is True
    
    def test_validate_manager_property_access_denied(self):
        """Test property access denial for unauthorized property"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        result = self.controller.validate_manager_property_access(self.manager1, "prop-2")
        assert result is False
    
    def test_validate_manager_property_access_invalid_role(self):
        """Test property access validation with non-manager user"""
        result = self.controller.validate_manager_property_access(self.hr_user, "prop-1")
        assert result is False
    
    def test_validate_manager_property_access_no_property_id(self):
        """Test property access validation with missing property ID"""
        result = self.controller.validate_manager_property_access(self.manager1, "")
        assert result is False
    
    def test_validate_manager_property_access_no_user(self):
        """Test property access validation with no user"""
        result = self.controller.validate_manager_property_access(None, "prop-1")
        assert result is False
    
    def test_validate_manager_application_access_success(self):
        """Test successful application access validation"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        self.mock_supabase.get_application_by_id_sync.return_value = self.application1
        
        result = self.controller.validate_manager_application_access(self.manager1, "app-1")
        assert result is True
    
    def test_validate_manager_application_access_wrong_property(self):
        """Test application access denied for wrong property"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        self.mock_supabase.get_application_by_id_sync.return_value = self.application2
        
        result = self.controller.validate_manager_application_access(self.manager1, "app-2")
        assert result is False
    
    def test_validate_manager_application_access_not_found(self):
        """Test application access when application doesn't exist"""
        self.mock_supabase.get_application_by_id_sync.return_value = None
        
        result = self.controller.validate_manager_application_access(self.manager1, "app-999")
        assert result is False
    
    def test_validate_manager_employee_access_success(self):
        """Test successful employee access validation"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        self.mock_supabase.get_employee_by_id_sync.return_value = self.employee1
        
        result = self.controller.validate_manager_employee_access(self.manager1, "emp-1")
        assert result is True
    
    def test_validate_manager_employee_access_wrong_property(self):
        """Test employee access denied for wrong property"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        self.mock_supabase.get_employee_by_id_sync.return_value = self.employee2
        
        result = self.controller.validate_manager_employee_access(self.manager1, "emp-2")
        assert result is False
    
    def test_validate_manager_employee_access_not_found(self):
        """Test employee access when employee doesn't exist"""
        self.mock_supabase.get_employee_by_id_sync.return_value = None
        
        result = self.controller.validate_manager_employee_access(self.manager1, "emp-999")
        assert result is False
    
    def test_validate_manager_onboarding_access_success(self):
        """Test successful onboarding session access validation"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        self.mock_supabase.get_onboarding_session_by_id_sync.return_value = self.session1
        
        result = self.controller.validate_manager_onboarding_access(self.manager1, "sess-1")
        assert result is True
    
    def test_validate_manager_onboarding_access_wrong_property(self):
        """Test onboarding access denied for wrong property"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        self.mock_supabase.get_onboarding_session_by_id_sync.return_value = self.session2
        
        result = self.controller.validate_manager_onboarding_access(self.manager1, "sess-2")
        assert result is False
    
    def test_get_manager_accessible_properties(self):
        """Test getting all accessible properties for a manager"""
        self.mock_supabase.get_manager_properties_sync.return_value = [
            self.property1, 
            self.property2
        ]
        
        properties = self.controller.get_manager_accessible_properties(self.manager1)
        assert properties == ["prop-1", "prop-2"]
    
    def test_get_manager_accessible_properties_non_manager(self):
        """Test getting accessible properties for non-manager returns empty"""
        properties = self.controller.get_manager_accessible_properties(self.hr_user)
        assert properties == []
    
    def test_filter_applications_by_manager_access(self):
        """Test filtering applications by manager access"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        applications = [self.application1, self.application2]
        filtered = self.controller.filter_applications_by_manager_access(self.manager1, applications)
        
        assert len(filtered) == 1
        assert filtered[0] == self.application1
    
    def test_filter_employees_by_manager_access(self):
        """Test filtering employees by manager access"""
        self.mock_supabase.get_manager_properties_sync.return_value = [self.property1]
        
        employees = [self.employee1, self.employee2]
        filtered = self.controller.filter_employees_by_manager_access(self.manager1, employees)
        
        assert len(filtered) == 1
        assert filtered[0] == self.employee1
    
    def test_multiple_properties_access(self):
        """Test manager with access to multiple properties"""
        self.mock_supabase.get_manager_properties_sync.return_value = [
            self.property1, 
            self.property2
        ]
        
        # Should have access to both properties
        assert self.controller.validate_manager_property_access(self.manager1, "prop-1") is True
        assert self.controller.validate_manager_property_access(self.manager1, "prop-2") is True
        assert self.controller.validate_manager_property_access(self.manager1, "prop-3") is False


class TestPropertyAccessDecorators:
    """Test property access decorators"""
    
    @pytest.mark.asyncio
    async def test_require_property_access_decorator_hr_bypass(self):
        """Test that HR users bypass property access checks"""
        mock_controller = Mock(spec=PropertyAccessController)
        
        with patch('app.property_access_control.get_property_access_controller', return_value=mock_controller):
            @require_property_access("property_id")
            async def test_endpoint(property_id: str, current_user: User):
                return {"success": True}
            
            hr_user = Mock(spec=User, id="hr-123", role=UserRole.HR)
            result = await test_endpoint(property_id="prop-1", current_user=hr_user)
            
            assert result == {"success": True}
            mock_controller.validate_manager_property_access.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_require_property_access_decorator_manager_success(self):
        """Test manager with proper property access"""
        mock_controller = Mock(spec=PropertyAccessController)
        mock_controller.validate_manager_property_access.return_value = True
        
        with patch('app.property_access_control.get_property_access_controller', return_value=mock_controller):
            @require_property_access("property_id")
            async def test_endpoint(property_id: str, current_user: User):
                return {"success": True}
            
            manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
            result = await test_endpoint(property_id="prop-1", current_user=manager)
            
            assert result == {"success": True}
            mock_controller.validate_manager_property_access.assert_called_once_with(manager, "prop-1")
    
    @pytest.mark.asyncio
    async def test_require_property_access_decorator_manager_denied(self):
        """Test manager without property access is denied"""
        mock_controller = Mock(spec=PropertyAccessController)
        mock_controller.validate_manager_property_access.return_value = False
        
        with patch('app.property_access_control.get_property_access_controller', return_value=mock_controller):
            @require_property_access("property_id")
            async def test_endpoint(property_id: str, current_user: User):
                return {"success": True}
            
            manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
            
            with pytest.raises(HTTPException) as exc_info:
                await test_endpoint(property_id="prop-2", current_user=manager)
            
            assert exc_info.value.status_code == 403
            assert "not authorized for this property" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_property_access_decorator_no_user(self):
        """Test decorator with no current user"""
        @require_property_access("property_id")
        async def test_endpoint(property_id: str):
            return {"success": True}
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(property_id="prop-1")
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_application_access_decorator_success(self):
        """Test application access decorator with valid access"""
        mock_controller = Mock(spec=PropertyAccessController)
        mock_controller.validate_manager_application_access.return_value = True
        
        with patch('app.property_access_control.get_property_access_controller', return_value=mock_controller):
            @require_application_access("app_id")
            async def test_endpoint(app_id: str, current_user: User):
                return {"success": True}
            
            manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
            result = await test_endpoint(app_id="app-1", current_user=manager)
            
            assert result == {"success": True}
            mock_controller.validate_manager_application_access.assert_called_once_with(manager, "app-1")
    
    @pytest.mark.asyncio
    async def test_require_employee_access_decorator_success(self):
        """Test employee access decorator with valid access"""
        mock_controller = Mock(spec=PropertyAccessController)
        mock_controller.validate_manager_employee_access.return_value = True
        
        with patch('app.property_access_control.get_property_access_controller', return_value=mock_controller):
            @require_employee_access("emp_id")
            async def test_endpoint(emp_id: str, current_user: User):
                return {"success": True}
            
            manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
            result = await test_endpoint(emp_id="emp-1", current_user=manager)
            
            assert result == {"success": True}
            mock_controller.validate_manager_employee_access.assert_called_once_with(manager, "emp-1")
    
    @pytest.mark.asyncio
    async def test_require_onboarding_access_decorator_success(self):
        """Test onboarding access decorator with valid access"""
        mock_controller = Mock(spec=PropertyAccessController)
        mock_controller.validate_manager_onboarding_access.return_value = True
        
        with patch('app.property_access_control.get_property_access_controller', return_value=mock_controller):
            @require_onboarding_access("session_id")
            async def test_endpoint(session_id: str, current_user: User):
                return {"success": True}
            
            manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
            result = await test_endpoint(session_id="sess-1", current_user=manager)
            
            assert result == {"success": True}
            mock_controller.validate_manager_onboarding_access.assert_called_once_with(manager, "sess-1")


class TestManagerPropertyDependency:
    """Test the require_manager_with_property_access dependency"""
    
    def test_require_manager_with_property_access_success(self):
        """Test successful manager with property access"""
        mock_controller = Mock(spec=PropertyAccessController)
        mock_controller.get_manager_properties.return_value = ["prop-1", "prop-2"]
        
        with patch('app.property_access_control.get_property_access_controller', return_value=mock_controller):
            manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
            result = require_manager_with_property_access(current_user=manager)
            
            assert result == manager
            mock_controller.get_manager_properties.assert_called_once_with("mgr-1")
    
    def test_require_manager_with_property_access_no_properties(self):
        """Test manager with no properties assigned"""
        mock_controller = Mock(spec=PropertyAccessController)
        mock_controller.get_manager_properties.return_value = []
        
        with patch('app.property_access_control.get_property_access_controller', return_value=mock_controller):
            manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
            
            with pytest.raises(HTTPException) as exc_info:
                require_manager_with_property_access(current_user=manager)
            
            assert exc_info.value.status_code == 403
            assert "not assigned to any property" in exc_info.value.detail
    
    def test_require_manager_with_property_access_not_manager(self):
        """Test non-manager user is rejected"""
        hr_user = Mock(spec=User, id="hr-123", role=UserRole.HR)
        
        with pytest.raises(HTTPException) as exc_info:
            require_manager_with_property_access(current_user=hr_user)
        
        assert exc_info.value.status_code == 403
        assert "Manager access required" in exc_info.value.detail
    
    def test_require_manager_with_property_access_no_user(self):
        """Test no user provided"""
        with pytest.raises(HTTPException) as exc_info:
            require_manager_with_property_access(current_user=None)
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_concurrent_access_different_managers(self):
        """Test that different managers can access their own properties concurrently"""
        mock_supabase = Mock(spec=EnhancedSupabaseService)
        controller = PropertyAccessController(mock_supabase)
        
        # Setup different properties for different managers
        def get_properties(manager_id):
            if manager_id == "mgr-1":
                return [Mock(id="prop-1")]
            elif manager_id == "mgr-2":
                return [Mock(id="prop-2")]
            return []
        
        mock_supabase.get_manager_properties_sync.side_effect = get_properties
        
        # Manager 1 access
        manager1 = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
        assert controller.validate_manager_property_access(manager1, "prop-1") is True
        assert controller.validate_manager_property_access(manager1, "prop-2") is False
        
        # Manager 2 access
        manager2 = Mock(spec=User, id="mgr-2", role=UserRole.MANAGER)
        assert controller.validate_manager_property_access(manager2, "prop-1") is False
        assert controller.validate_manager_property_access(manager2, "prop-2") is True
    
    def test_property_reassignment(self):
        """Test behavior when manager property assignment changes"""
        mock_supabase = Mock(spec=EnhancedSupabaseService)
        controller = PropertyAccessController(mock_supabase)
        
        # Initial assignment
        mock_supabase.get_manager_properties_sync.return_value = [Mock(id="prop-1")]
        manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
        
        assert controller.validate_manager_property_access(manager, "prop-1") is True
        assert controller.validate_manager_property_access(manager, "prop-2") is False
        
        # Clear cache and change assignment
        controller.clear_manager_cache("mgr-1")
        mock_supabase.get_manager_properties_sync.return_value = [Mock(id="prop-2")]
        
        # New access pattern
        assert controller.validate_manager_property_access(manager, "prop-1") is False
        assert controller.validate_manager_property_access(manager, "prop-2") is True
    
    def test_invalid_uuid_handling(self):
        """Test handling of invalid UUIDs"""
        mock_supabase = Mock(spec=EnhancedSupabaseService)
        controller = PropertyAccessController(mock_supabase)
        
        mock_supabase.get_manager_properties_sync.return_value = []
        manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
        
        # Should handle invalid IDs gracefully
        assert controller.validate_manager_property_access(manager, "invalid-uuid") is False
        assert controller.validate_manager_application_access(manager, "not-a-uuid") is False
        assert controller.validate_manager_employee_access(manager, "") is False
    
    def test_database_connection_failure(self):
        """Test behavior when database connection fails"""
        mock_supabase = Mock(spec=EnhancedSupabaseService)
        controller = PropertyAccessController(mock_supabase)
        
        # Simulate database connection failure
        mock_supabase.get_manager_properties_sync.side_effect = ConnectionError("Database unavailable")
        
        manager = Mock(spec=User, id="mgr-1", role=UserRole.MANAGER)
        
        # Should return False on connection error
        assert controller.get_manager_properties("mgr-1") == []
        assert controller.validate_manager_property_access(manager, "prop-1") is False


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])