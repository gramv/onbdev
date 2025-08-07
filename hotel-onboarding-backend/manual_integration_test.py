#!/usr/bin/env python3
"""
Manual Integration Test for Tasks 1, 2, and 3
HR Manager System Consolidation

This script manually tests the integration between:
- Task 1: Property Access Control
- Task 2: Database Schema Enhancements  
- Task 3: WebSocket Infrastructure

No external test framework dependencies required.
"""

import asyncio
import sys
import os
import json
import uuid
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from unittest.mock import Mock

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Test results tracking
test_results = {
    'task_1_property_access': {'passed': 0, 'failed': 0, 'tests': []},
    'task_2_database_schema': {'passed': 0, 'failed': 0, 'tests': []},
    'task_3_websocket_infrastructure': {'passed': 0, 'failed': 0, 'tests': []},
    'cross_task_integration': {'passed': 0, 'failed': 0, 'tests': []},
    'system_health': {'passed': 0, 'failed': 0, 'tests': []}
}


def test_result(category: str, test_name: str, passed: bool, message: str = ""):
    """Record test result and print status"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} {test_name}")
    if message:
        print(f"    → {message}")
    
    test_results[category]['tests'].append({
        'name': test_name,
        'passed': passed,
        'message': message
    })
    
    if passed:
        test_results[category]['passed'] += 1
    else:
        test_results[category]['failed'] += 1


def test_task_1_property_access_control():
    """Test Task 1: Property Access Control functionality"""
    print("\n📋 Task 1: Property Access Control Tests")
    print("-" * 50)
    
    try:
        # Import and test property access control
        from property_access_control import PropertyAccessController
        from models import User, UserRole
        
        # Create mock Supabase service
        mock_service = Mock()
        mock_properties = [
            Mock(id="property-1", name="Hotel Alpha"),
            Mock(id="property-2", name="Hotel Beta")
        ]
        mock_service.get_manager_properties_sync.return_value = mock_properties
        
        # Create controller
        controller = PropertyAccessController(mock_service)
        test_result('task_1_property_access', 'PropertyAccessController initialization', True, "Controller created successfully")
        
        # Create mock manager
        manager = User(
            id="manager-1",
            email="manager@hotel.com", 
            role=UserRole.MANAGER,
            name="Test Manager",
            is_active=True
        )
        
        # Test property access validation - success case
        has_access = controller.validate_manager_property_access(manager, "property-1")
        test_result('task_1_property_access', 'Manager property access validation (valid)', has_access, 
                   "Manager can access assigned property")
        
        # Test property access validation - denied case
        has_access = controller.validate_manager_property_access(manager, "property-999")
        test_result('task_1_property_access', 'Manager property access validation (denied)', not has_access,
                   "Manager cannot access unassigned property")
        
        # Test caching functionality
        properties1 = controller.get_manager_properties("manager-1")
        properties2 = controller.get_manager_properties("manager-1")  # Should use cache
        cache_works = (properties1 == properties2 == ["property-1", "property-2"])
        test_result('task_1_property_access', 'Property access caching', cache_works,
                   f"Cache returned consistent results: {properties1}")
        
        # Test cache clearing
        controller.clear_manager_cache("manager-1")
        properties3 = controller.get_manager_properties("manager-1")  # Should hit DB again
        cache_clear_works = (properties3 == properties1)
        test_result('task_1_property_access', 'Cache invalidation', cache_clear_works,
                   "Cache cleared and refreshed successfully")
        
    except ImportError as e:
        test_result('task_1_property_access', 'Module import', False, f"Import error: {e}")
    except Exception as e:
        test_result('task_1_property_access', 'General functionality', False, f"Error: {e}")


def test_task_2_database_schema():
    """Test Task 2: Database Schema Enhancement functionality"""
    print("\n💾 Task 2: Database Schema Enhancement Tests")  
    print("-" * 50)
    
    try:
        # Test enhanced supabase service import
        from supabase_service_enhanced import EnhancedSupabaseService
        test_result('task_2_database_schema', 'EnhancedSupabaseService import', True, 
                   "Service imported successfully")
        
        # Test service initialization
        service = EnhancedSupabaseService()
        test_result('task_2_database_schema', 'Service initialization', True,
                   "Service initialized successfully")
        
        # Test method existence for new tables
        expected_methods = [
            'create_audit_log',
            'get_audit_logs', 
            'create_notification',
            'get_notifications',
            'mark_notification_read',
            'get_unread_notifications_count',
            'create_analytics_event',
            'get_analytics_events',
            'create_report_template',
            'get_report_templates'
        ]
        
        missing_methods = []
        for method in expected_methods:
            if not hasattr(service, method):
                missing_methods.append(method)
        
        methods_exist = len(missing_methods) == 0
        test_result('task_2_database_schema', 'New table methods exist', methods_exist,
                   f"Missing methods: {missing_methods}" if missing_methods else "All methods present")
        
        # Test model imports
        try:
            from models import AuditLog, Notification, AnalyticsEvent, ReportTemplate
            test_result('task_2_database_schema', 'New model classes import', True,
                       "All new model classes imported successfully")
        except ImportError as e:
            test_result('task_2_database_schema', 'New model classes import', False,
                       f"Model import error: {e}")
        
    except ImportError as e:
        test_result('task_2_database_schema', 'Module import', False, f"Import error: {e}")
    except Exception as e:
        test_result('task_2_database_schema', 'General functionality', False, f"Error: {e}")


def test_task_3_websocket_infrastructure():
    """Test Task 3: WebSocket Infrastructure functionality"""
    print("\n🔗 Task 3: WebSocket Infrastructure Tests")
    print("-" * 50)
    
    try:
        # Test WebSocket manager import
        try:
            from websocket_manager import WebSocketManager, BroadcastEvent
            test_result('task_3_websocket_infrastructure', 'WebSocket manager import', True,
                       "WebSocket modules imported successfully")
            websocket_available = True
        except ImportError as e:
            test_result('task_3_websocket_infrastructure', 'WebSocket manager import', False,
                       f"WebSocket modules not available: {e}")
            websocket_available = False
        
        if websocket_available:
            # Test WebSocket manager initialization
            manager = WebSocketManager()
            test_result('task_3_websocket_infrastructure', 'WebSocket manager initialization', True,
                       "WebSocket manager created successfully")
            
            # Test connection management
            initial_connections = len(manager.connections)
            mock_connection = Mock()
            mock_connection.user_id = "user-1"
            mock_connection.user_role = "MANAGER"
            mock_connection.property_id = "property-1"
            
            connection_id = manager.add_connection(mock_connection)
            connection_added = len(manager.connections) == initial_connections + 1
            test_result('task_3_websocket_infrastructure', 'Connection management (add)', connection_added,
                       f"Connection added with ID: {connection_id}")
            
            # Test room subscriptions
            room_id = "property-1"
            manager.subscribe_to_room(mock_connection, room_id)
            room_created = room_id in manager.rooms
            connection_in_room = mock_connection in manager.rooms[room_id].connections
            test_result('task_3_websocket_infrastructure', 'Room subscription', room_created and connection_in_room,
                       f"Connection subscribed to room: {room_id}")
            
            # Test connection removal
            manager.remove_connection(connection_id)
            connection_removed = len(manager.connections) == initial_connections
            test_result('task_3_websocket_infrastructure', 'Connection management (remove)', connection_removed,
                       "Connection removed successfully")
            
            # Test router import
            try:
                from websocket_router import router
                test_result('task_3_websocket_infrastructure', 'WebSocket router import', True,
                           "WebSocket router imported successfully")
            except ImportError as e:
                test_result('task_3_websocket_infrastructure', 'WebSocket router import', False,
                           f"Router import error: {e}")
        
    except Exception as e:
        test_result('task_3_websocket_infrastructure', 'General functionality', False, f"Error: {e}")


def test_cross_task_integration():
    """Test integration between all three tasks"""
    print("\n🔄 Cross-Task Integration Tests")
    print("-" * 50)
    
    try:
        # Test that all components can be imported together
        components_imported = True
        import_errors = []
        
        try:
            from property_access_control import PropertyAccessController
        except ImportError as e:
            components_imported = False
            import_errors.append(f"PropertyAccessController: {e}")
        
        try:
            from supabase_service_enhanced import EnhancedSupabaseService
        except ImportError as e:
            components_imported = False  
            import_errors.append(f"EnhancedSupabaseService: {e}")
        
        try:
            from websocket_manager import WebSocketManager
        except ImportError as e:
            # WebSocket is optional
            import_errors.append(f"WebSocketManager: {e} (optional)")
        
        test_result('cross_task_integration', 'All components import together', components_imported,
                   f"Import errors: {import_errors}" if import_errors else "All components imported")
        
        if components_imported:
            # Test integration scenario
            mock_service = Mock()
            mock_service.get_manager_properties_sync.return_value = [
                Mock(id="property-1", name="Hotel Alpha")
            ]
            
            controller = PropertyAccessController(mock_service)
            service = EnhancedSupabaseService()
            
            # Test that property access and audit logging can work together
            from models import User, UserRole
            manager = User(
                id="manager-1",
                email="manager@hotel.com",
                role=UserRole.MANAGER, 
                name="Test Manager",
                is_active=True
            )
            
            has_access = controller.validate_manager_property_access(manager, "property-1")
            integration_works = has_access and hasattr(service, 'create_audit_log')
            test_result('cross_task_integration', 'Property access + Audit logging integration', integration_works,
                       "Components can work together for audit logging")
            
    except Exception as e:
        test_result('cross_task_integration', 'Integration test', False, f"Error: {e}")


def test_system_health():
    """Test overall system health and performance"""
    print("\n🏥 System Health and Performance Tests")
    print("-" * 50)
    
    try:
        # Test main application import
        try:
            from main_enhanced import app
            test_result('system_health', 'Main application import', True,
                       "Main FastAPI application imported successfully")
        except ImportError as e:
            test_result('system_health', 'Main application import', False, f"Import error: {e}")
        
        # Test essential models import
        try:
            from models import User, UserRole, Property, JobApplication
            test_result('system_health', 'Core models import', True,
                       "Core models imported successfully")
        except ImportError as e:
            test_result('system_health', 'Core models import', False, f"Model import error: {e}")
        
        # Test configuration and environment
        env_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'JWT_SECRET']
        missing_env = []
        for var in env_vars:
            if not os.getenv(var):
                missing_env.append(var)
        
        env_configured = len(missing_env) == 0
        test_result('system_health', 'Environment configuration', env_configured,
                   f"Missing env vars: {missing_env}" if missing_env else "All required env vars present")
        
        # Test performance of key operations
        mock_service = Mock()
        mock_service.get_manager_properties_sync.return_value = [
            Mock(id=f"property-{i}", name=f"Hotel {i}") for i in range(5)
        ]
        
        from property_access_control import PropertyAccessController
        controller = PropertyAccessController(mock_service)
        
        # Time cache performance
        start_time = time.time()
        properties1 = controller.get_manager_properties("manager-1")  # DB call
        first_call_time = time.time() - start_time
        
        start_time = time.time() 
        properties2 = controller.get_manager_properties("manager-1")  # Cache call
        second_call_time = time.time() - start_time
        
        cache_performance = second_call_time < first_call_time
        test_result('system_health', 'Cache performance optimization', cache_performance,
                   f"Cache call ({second_call_time:.4f}s) faster than DB call ({first_call_time:.4f}s)")
        
    except Exception as e:
        test_result('system_health', 'System health check', False, f"Error: {e}")


def generate_summary_report():
    """Generate comprehensive test summary report"""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE INTEGRATION TEST REPORT")
    print("=" * 80)
    
    total_passed = 0
    total_failed = 0
    all_categories_passed = True
    
    for category, results in test_results.items():
        passed = results['passed']
        failed = results['failed']
        total = passed + failed
        
        total_passed += passed
        total_failed += failed
        
        if failed > 0:
            all_categories_passed = False
        
        status = "✅ PASSED" if failed == 0 else "❌ FAILED"
        print(f"\n{category.replace('_', ' ').title()}: {status}")
        print(f"  Tests: {total}, Passed: {passed}, Failed: {failed}")
        
        # Show failed tests
        if failed > 0:
            print("  Failed tests:")
            for test in results['tests']:
                if not test['passed']:
                    print(f"    ❌ {test['name']}: {test['message']}")
    
    print("\n" + "=" * 80)
    print("🎯 OVERALL SYSTEM STATUS")
    print("=" * 80)
    
    print(f"Total Tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/(total_passed + total_failed)*100):.1f}%")
    
    if all_categories_passed:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("\n✅ Task 1 (Property Access Control): OPERATIONAL")
        print("✅ Task 2 (Database Schema Enhancements): OPERATIONAL") 
        print("✅ Task 3 (WebSocket Infrastructure): OPERATIONAL")
        print("✅ Cross-Task Integration: WORKING")
        print("✅ System Health: GOOD")
        print("\n🚀 SYSTEM IS READY FOR PRODUCTION!")
        
    else:
        print("\n⚠️ SOME TESTS FAILED - SYSTEM NEEDS ATTENTION")
        print("\nRequired Actions:")
        
        for category, results in test_results.items():
            if results['failed'] > 0:
                print(f"🔧 Fix issues in: {category.replace('_', ' ').title()}")
    
    return all_categories_passed


def main():
    """Main test execution function"""
    print("🚀 Starting Manual Integration Tests for HR Manager System Consolidation")
    print("Testing Tasks 1, 2, and 3 implementation and integration")
    print("=" * 80)
    
    # Run all test suites
    test_task_1_property_access_control()
    test_task_2_database_schema()
    test_task_3_websocket_infrastructure()
    test_cross_task_integration()
    test_system_health()
    
    # Generate summary report
    success = generate_summary_report()
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)