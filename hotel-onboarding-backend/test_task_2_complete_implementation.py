#!/usr/bin/env python3
"""
Test Script for Task 2: Database Schema Enhancements
Verifies complete implementation of all Task 2 components
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import importlib.util

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{text:^60}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 60}{RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{YELLOW}ℹ️  {text}{RESET}")

def print_section(text: str):
    """Print section header"""
    print(f"\n{BOLD}{text}{RESET}")
    print("-" * 40)

class Task2Tester:
    def __init__(self):
        self.results = {
            "models": {"passed": 0, "failed": 0, "tests": []},
            "service_methods": {"passed": 0, "failed": 0, "tests": []},
            "api_endpoints": {"passed": 0, "failed": 0, "tests": []},
            "database_tables": {"passed": 0, "failed": 0, "tests": []},
            "integration": {"passed": 0, "failed": 0, "tests": []}
        }
        self.supabase_service = None
        
    async def setup(self):
        """Setup test environment"""
        try:
            # Import the enhanced supabase service
            from app.supabase_service_enhanced import get_enhanced_supabase_service
            self.supabase_service = get_enhanced_supabase_service()
            print_success("Supabase service initialized")
            return True
        except Exception as e:
            print_error(f"Failed to initialize Supabase service: {e}")
            return False
    
    def test_models(self):
        """Test that all required models are defined"""
        print_section("Testing Pydantic Models")
        
        required_models = [
            ("AuditLog", "Audit log model"),
            ("AuditLogAction", "Audit log action enum"),
            ("Notification", "Notification model"),
            ("NotificationChannel", "Notification channel enum"),
            ("NotificationPriority", "Notification priority enum"),
            ("NotificationStatus", "Notification status enum"),
            ("NotificationType", "Notification type enum"),
            ("AnalyticsEvent", "Analytics event model"),
            ("AnalyticsEventType", "Analytics event type enum"),
            ("ReportTemplate", "Report template model"),
            ("ReportType", "Report type enum"),
            ("ReportFormat", "Report format enum"),
            ("ReportSchedule", "Report schedule enum"),
            ("SavedFilter", "Saved filter model")
        ]
        
        try:
            from app import models
            
            for model_name, description in required_models:
                if hasattr(models, model_name):
                    print_success(f"{description} ({model_name})")
                    self.results["models"]["passed"] += 1
                    self.results["models"]["tests"].append((model_name, True))
                else:
                    print_error(f"{description} ({model_name}) not found")
                    self.results["models"]["failed"] += 1
                    self.results["models"]["tests"].append((model_name, False))
                    
        except ImportError as e:
            print_error(f"Failed to import models: {e}")
            self.results["models"]["failed"] = len(required_models)
    
    async def test_service_methods(self):
        """Test that all required service methods exist"""
        print_section("Testing Database Service Methods")
        
        required_methods = [
            # Audit log methods
            ("create_audit_log", "Create audit log"),
            ("get_audit_logs", "Get audit logs"),
            
            # Notification methods
            ("create_notification", "Create notification"),
            ("get_notifications", "Get notifications"),
            ("mark_notification_read", "Mark notification as read"),
            ("mark_notifications_read_bulk", "Mark notifications as read (bulk)"),
            
            # Analytics methods
            ("create_analytics_event", "Create analytics event"),
            ("get_analytics_events", "Get analytics events"),
            
            # Report template methods
            ("create_report_template", "Create report template"),
            ("get_report_templates", "Get report templates"),
            ("update_report_template", "Update report template"),
            ("delete_report_template", "Delete report template"),
            
            # Saved filter methods
            ("create_saved_filter", "Create saved filter"),
            ("get_saved_filters", "Get saved filters")
        ]
        
        if not self.supabase_service:
            print_error("Supabase service not initialized")
            self.results["service_methods"]["failed"] = len(required_methods)
            return
        
        for method_name, description in required_methods:
            if hasattr(self.supabase_service, method_name):
                print_success(f"{description} ({method_name})")
                self.results["service_methods"]["passed"] += 1
                self.results["service_methods"]["tests"].append((method_name, True))
            else:
                print_error(f"{description} ({method_name}) not found")
                self.results["service_methods"]["failed"] += 1
                self.results["service_methods"]["tests"].append((method_name, False))
    
    def test_api_endpoints(self):
        """Test that all required API endpoints are defined"""
        print_section("Testing API Endpoints")
        
        required_endpoints = [
            # Audit log endpoints
            ("GET", "/api/audit-logs", "Get audit logs"),
            
            # Notification endpoints
            ("GET", "/api/notifications", "Get notifications"),
            ("POST", "/api/notifications/{notification_id}/read", "Mark notification as read"),
            ("POST", "/api/notifications/mark-read", "Mark notifications as read (bulk)"),
            
            # Analytics endpoints
            ("POST", "/api/analytics/track", "Track analytics event"),
            ("GET", "/api/analytics/events", "Get analytics events"),
            
            # Report template endpoints
            ("GET", "/api/reports/templates", "Get report templates"),
            ("POST", "/api/reports/templates", "Create report template"),
            ("PUT", "/api/reports/templates/{template_id}", "Update report template"),
            ("DELETE", "/api/reports/templates/{template_id}", "Delete report template"),
            
            # Saved filter endpoints
            ("GET", "/api/filters", "Get saved filters"),
            ("POST", "/api/filters", "Create saved filter")
        ]
        
        try:
            # Import the main app
            spec = importlib.util.spec_from_file_location(
                "main_enhanced",
                "app/main_enhanced.py"
            )
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            
            app = main_module.app
            
            # Get all routes
            routes = []
            for route in app.routes:
                if hasattr(route, "methods") and hasattr(route, "path"):
                    for method in route.methods:
                        routes.append((method, route.path))
            
            # Check each required endpoint
            for method, path, description in required_endpoints:
                # Convert path pattern to check (remove {param} parts for matching)
                check_path = path.replace("{notification_id}", "{notification_id}").replace("{template_id}", "{template_id}")
                
                found = False
                for route_method, route_path in routes:
                    if route_method == method and route_path == check_path:
                        found = True
                        break
                
                if found:
                    print_success(f"{method} {path} - {description}")
                    self.results["api_endpoints"]["passed"] += 1
                    self.results["api_endpoints"]["tests"].append((f"{method} {path}", True))
                else:
                    print_error(f"{method} {path} - {description} not found")
                    self.results["api_endpoints"]["failed"] += 1
                    self.results["api_endpoints"]["tests"].append((f"{method} {path}", False))
                    
        except Exception as e:
            print_error(f"Failed to check API endpoints: {e}")
            self.results["api_endpoints"]["failed"] = len(required_endpoints)
    
    async def test_database_tables(self):
        """Test that database tables can be accessed"""
        print_section("Testing Database Tables")
        
        tables_to_test = [
            ("audit_logs", "Audit logs table"),
            ("notifications", "Notifications table"),
            ("analytics_events", "Analytics events table"),
            ("report_templates", "Report templates table"),
            ("saved_filters", "Saved filters table")
        ]
        
        if not self.supabase_service:
            print_error("Supabase service not initialized")
            self.results["database_tables"]["failed"] = len(tables_to_test)
            return
        
        for table_name, description in tables_to_test:
            try:
                # Try to query the table (will fail if table doesn't exist)
                result = self.supabase_service.client.table(table_name).select("id").limit(1).execute()
                print_success(f"{description} ({table_name}) exists and is accessible")
                self.results["database_tables"]["passed"] += 1
                self.results["database_tables"]["tests"].append((table_name, True))
            except Exception as e:
                print_error(f"{description} ({table_name}) - {str(e)[:50]}")
                self.results["database_tables"]["failed"] += 1
                self.results["database_tables"]["tests"].append((table_name, False))
    
    async def test_integration(self):
        """Test basic integration scenarios"""
        print_section("Testing Integration")
        
        # Test 1: Create and retrieve audit log
        try:
            audit_log_data = {
                "user_id": "test-user-id",
                "user_email": "test@example.com",
                "user_role": "hr",
                "action": "create",
                "resource_type": "test",
                "resource_id": "test-resource-id",
                "description": "Test audit log entry"
            }
            
            result = await self.supabase_service.create_audit_log(audit_log_data)
            if result:
                print_success("Created audit log entry")
                
                # Try to retrieve it
                logs = await self.supabase_service.get_audit_logs({"user_id": "test-user-id"})
                if logs:
                    print_success("Retrieved audit logs")
                    self.results["integration"]["passed"] += 2
                else:
                    print_error("Failed to retrieve audit logs")
                    self.results["integration"]["failed"] += 1
                    self.results["integration"]["passed"] += 1
            else:
                print_error("Failed to create audit log")
                self.results["integration"]["failed"] += 2
                
        except Exception as e:
            print_error(f"Audit log integration test failed: {e}")
            self.results["integration"]["failed"] += 2
        
        # Test 2: Create and retrieve notification
        try:
            notification_data = {
                "type": "system_alert",
                "channel": "in_app",
                "recipient_id": "test-user-id",
                "subject": "Test Notification",
                "message": "This is a test notification"
            }
            
            result = await self.supabase_service.create_notification(notification_data)
            if result:
                print_success("Created notification")
                
                # Try to retrieve it
                notifications = await self.supabase_service.get_notifications(user_id="test-user-id")
                if notifications is not None:
                    print_success("Retrieved notifications")
                    self.results["integration"]["passed"] += 2
                else:
                    print_error("Failed to retrieve notifications")
                    self.results["integration"]["failed"] += 1
                    self.results["integration"]["passed"] += 1
            else:
                print_error("Failed to create notification")
                self.results["integration"]["failed"] += 2
                
        except Exception as e:
            print_error(f"Notification integration test failed: {e}")
            self.results["integration"]["failed"] += 2
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            
            if total > 0:
                percentage = (passed / total) * 100
                status = "✅" if percentage == 100 else "⚠️" if percentage >= 50 else "❌"
                
                print(f"{status} {category.replace('_', ' ').title()}: {passed}/{total} passed ({percentage:.1f}%)")
                
                total_passed += passed
                total_failed += failed
        
        print("\n" + "=" * 60)
        overall_total = total_passed + total_failed
        if overall_total > 0:
            overall_percentage = (total_passed / overall_total) * 100
            
            if overall_percentage == 100:
                print(f"{GREEN}{BOLD}🎉 ALL TESTS PASSED! {total_passed}/{overall_total} ({overall_percentage:.1f}%){RESET}")
            elif overall_percentage >= 80:
                print(f"{GREEN}✅ Task 2 is mostly complete: {total_passed}/{overall_total} ({overall_percentage:.1f}%){RESET}")
            elif overall_percentage >= 50:
                print(f"{YELLOW}⚠️ Task 2 is partially complete: {total_passed}/{overall_total} ({overall_percentage:.1f}%){RESET}")
            else:
                print(f"{RED}❌ Task 2 needs significant work: {total_passed}/{overall_total} ({overall_percentage:.1f}%){RESET}")
        
        # Calculate implementation percentage
        print("\n" + "=" * 60)
        print(f"{BOLD}Task 2 Implementation Status:{RESET}")
        
        components = [
            ("Pydantic Models", self.results["models"]["passed"], 14),
            ("Service Methods", self.results["service_methods"]["passed"], 14),
            ("API Endpoints", self.results["api_endpoints"]["passed"], 12),
            ("Database Tables", self.results["database_tables"]["passed"], 5),
            ("Integration", self.results["integration"]["passed"], 4)
        ]
        
        total_expected = sum(c[2] for c in components)
        total_implemented = sum(c[1] for c in components)
        
        for name, implemented, expected in components:
            pct = (implemented / expected * 100) if expected > 0 else 0
            status = "✅" if pct == 100 else "⚠️" if pct >= 50 else "❌"
            print(f"  {status} {name}: {implemented}/{expected} ({pct:.1f}%)")
        
        final_percentage = (total_implemented / total_expected * 100) if total_expected > 0 else 0
        print(f"\n{BOLD}Overall Task 2 Completion: {final_percentage:.1f}%{RESET}")
        
        if final_percentage >= 90:
            print(f"{GREEN}{BOLD}✅ Task 2 is COMPLETE and ready for production!{RESET}")
        elif final_percentage >= 70:
            print(f"{YELLOW}{BOLD}⚠️ Task 2 is mostly complete but needs finishing touches{RESET}")
        else:
            print(f"{RED}{BOLD}❌ Task 2 requires significant additional work{RESET}")

async def main():
    """Main test function"""
    print_header("Task 2: Database Schema Enhancements Test")
    print("Testing complete implementation of all Task 2 components\n")
    
    tester = Task2Tester()
    
    # Setup
    if not await tester.setup():
        print_error("Failed to setup test environment")
        return
    
    # Run tests
    tester.test_models()
    await tester.test_service_methods()
    tester.test_api_endpoints()
    await tester.test_database_tables()
    await tester.test_integration()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())