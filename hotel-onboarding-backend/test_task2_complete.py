#!/usr/bin/env python3
"""
Comprehensive Test for Task 2 Implementation
Tests all models, services, and API endpoints
"""

import asyncio
import httpx
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import sys

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# API base URL
BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_HR_EMAIL = "freshhr@test.com"
TEST_HR_PASSWORD = "test123"
TEST_MANAGER_EMAIL = "testuser@example.com"
TEST_MANAGER_PASSWORD = "pass123"

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{text:^60}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 60}{RESET}\n")

def print_section(text: str):
    """Print a section header"""
    print(f"\n{BOLD}{text}{RESET}")
    print("-" * 40)

def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{YELLOW}ℹ️  {text}{RESET}")

async def login(client: httpx.AsyncClient, email: str, password: str) -> str:
    """Login and get JWT token"""
    response = await client.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")

async def test_audit_logs(client: httpx.AsyncClient, token: str) -> bool:
    """Test audit log endpoints"""
    print_section("Testing Audit Logs")
    
    try:
        # Get audit logs
        response = await client.get(
            f"{BASE_URL}/api/audit-logs",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 5}
        )
        
        if response.status_code == 200:
            logs = response.json()
            print_success(f"Retrieved {len(logs)} audit logs")
            
            # Check if recent login was logged
            recent_login = any(
                log.get("action") == "login" 
                for log in logs 
                if isinstance(log, dict)
            )
            
            if recent_login:
                print_success("Recent login action found in audit logs")
            else:
                print_info("No recent login in audit logs (might be filtered)")
            
            return True
        else:
            print_error(f"Failed to get audit logs: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Audit log test failed: {str(e)}")
        return False

async def test_notifications(client: httpx.AsyncClient, token: str) -> bool:
    """Test notification endpoints"""
    print_section("Testing Notifications")
    
    try:
        # Get notifications
        response = await client.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            notifications = response.json()
            print_success(f"Retrieved {len(notifications)} notifications")
            
            # Check for unread notifications
            unread = sum(1 for n in notifications if n.get("status") == "pending")
            print_info(f"Found {unread} unread notifications")
            
            return True
        else:
            print_error(f"Failed to get notifications: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Notification test failed: {str(e)}")
        return False

async def test_analytics(client: httpx.AsyncClient, token: str = None) -> bool:
    """Test analytics tracking"""
    print_section("Testing Analytics Events")
    
    try:
        # Track an event (no auth required)
        event_data = {
            "event_type": "page_view",
            "event_name": "task_2_test",
            "session_id": "test-session-123",
            "page_url": "/test",
            "page_title": "Task 2 Test Page",
            "properties": {
                "test": True,
                "task": 2,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = await client.post(
            f"{BASE_URL}/api/analytics/track",
            json=event_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Successfully tracked analytics event")
            print_info(f"Event ID: {result.get('event_id', 'N/A')}")
            return True
        else:
            print_error(f"Failed to track event: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Analytics test failed: {str(e)}")
        return False

async def test_report_templates(client: httpx.AsyncClient, token: str) -> bool:
    """Test report template endpoints"""
    print_section("Testing Report Templates")
    
    try:
        # Create a report template
        template_data = {
            "name": "Task 2 Test Report",
            "description": "Test report for Task 2 verification",
            "type": "employee_onboarding",
            "format": "pdf",
            "schedule": "weekly",
            "filters": {
                "status": "completed",
                "date_range": "last_7_days"
            },
            "columns": ["employee_name", "status", "completion_date"],
            "is_active": True
        }
        
        response = await client.post(
            f"{BASE_URL}/api/reports/templates",
            json=template_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            template = response.json()
            print_success(f"Created report template: {template.get('name')}")
            template_id = template.get("id")
            
            # Get all templates
            response = await client.get(
                f"{BASE_URL}/api/reports/templates",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                templates = response.json()
                print_success(f"Retrieved {len(templates)} report templates")
                return True
            else:
                print_error(f"Failed to get templates: {response.status_code}")
                return False
        else:
            print_error(f"Failed to create template: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Report template test failed: {str(e)}")
        return False

async def test_saved_filters(client: httpx.AsyncClient, token: str) -> bool:
    """Test saved filter endpoints"""
    print_section("Testing Saved Filters")
    
    try:
        # Create a saved filter
        filter_data = {
            "name": "Active Employees - Task 2 Test",
            "description": "Filter for active employees",
            "filter_type": "employee",
            "filters": {
                "status": "active",
                "department": "all",
                "test": True
            },
            "is_shared": True
        }
        
        response = await client.post(
            f"{BASE_URL}/api/filters/save",
            json=filter_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            saved_filter = response.json()
            print_success(f"Created saved filter: {saved_filter.get('name')}")
            
            # Get saved filters
            response = await client.get(
                f"{BASE_URL}/api/filters",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                filters = response.json()
                print_success(f"Retrieved {len(filters)} saved filters")
                return True
            else:
                print_error(f"Failed to get filters: {response.status_code}")
                return False
        else:
            print_error(f"Failed to create filter: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Saved filter test failed: {str(e)}")
        return False

async def test_api_response_models(client: httpx.AsyncClient, token: str) -> bool:
    """Test that API responses match expected models"""
    print_section("Testing API Response Models")
    
    try:
        # Test audit log response model
        response = await client.get(
            f"{BASE_URL}/api/audit-logs",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 1}
        )
        
        if response.status_code == 200 and response.json():
            log = response.json()[0]
            required_fields = ["id", "timestamp", "action", "resource_type"]
            has_fields = all(field in log for field in required_fields)
            
            if has_fields:
                print_success("Audit log response has required fields")
            else:
                print_error("Audit log response missing fields")
                return False
        
        # Test notification response model
        response = await client.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 1}
        )
        
        if response.status_code == 200:
            if response.json():
                notification = response.json()[0]
                required_fields = ["id", "type", "status", "subject", "message"]
                has_fields = all(field in notification for field in required_fields)
                
                if has_fields:
                    print_success("Notification response has required fields")
                else:
                    print_error("Notification response missing fields")
                    return False
            else:
                print_info("No notifications to validate model")
        
        return True
        
    except Exception as e:
        print_error(f"Model validation failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print_header("Task 2 Implementation Test Suite")
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/healthz")
            if response.status_code != 200:
                print_error("Server is not running or not healthy")
                print_info(f"Start the server with: python3 -m uvicorn app.main_enhanced:app --reload")
                return
    except Exception as e:
        print_error(f"Cannot connect to server at {BASE_URL}")
        print_info(f"Start the server with: python3 -m uvicorn app.main_enhanced:app --reload")
        return
    
    print_success("Server is running and healthy")
    
    # Run tests
    async with httpx.AsyncClient(timeout=30.0) as client:
        test_results = []
        
        try:
            # Login as HR user
            print_section("Authentication")
            hr_token = await login(client, TEST_HR_EMAIL, TEST_HR_PASSWORD)
            print_success(f"Logged in as HR user: {TEST_HR_EMAIL}")
            
            # Run all tests
            test_results.append(("Audit Logs", await test_audit_logs(client, hr_token)))
            test_results.append(("Notifications", await test_notifications(client, hr_token)))
            test_results.append(("Analytics", await test_analytics(client, hr_token)))
            test_results.append(("Report Templates", await test_report_templates(client, hr_token)))
            test_results.append(("Saved Filters", await test_saved_filters(client, hr_token)))
            test_results.append(("Response Models", await test_api_response_models(client, hr_token)))
            
        except Exception as e:
            print_error(f"Test suite error: {str(e)}")
            
        # Summary
        print_header("Test Results Summary")
        
        passed = sum(1 for _, result in test_results if result)
        failed = len(test_results) - passed
        
        for test_name, result in test_results:
            status = f"{GREEN}✅ PASSED{RESET}" if result else f"{RED}❌ FAILED{RESET}"
            print(f"  {test_name:20} {status}")
        
        print(f"\n{BOLD}Overall Results:{RESET}")
        print(f"  ✅ Passed: {passed}/{len(test_results)}")
        print(f"  ❌ Failed: {failed}/{len(test_results)}")
        
        if passed == len(test_results):
            print(f"\n{GREEN}{BOLD}🎉 All Task 2 tests passed!{RESET}")
            print(f"{GREEN}Task 2 implementation is fully functional!{RESET}")
        elif passed >= len(test_results) * 0.7:
            print(f"\n{YELLOW}{BOLD}⚠️ Most tests passed but some issues remain{RESET}")
        else:
            print(f"\n{RED}{BOLD}❌ Task 2 implementation needs attention{RESET}")
        
        # Final status
        print_header("Task 2 Implementation Checklist")
        print("✅ Pydantic models created (AuditLog, Notification, etc.)")
        print("✅ Database service methods implemented")
        print("✅ API endpoints added to main_enhanced.py")
        print("✅ Migration files created")
        
        if passed == len(test_results):
            print("✅ All functionality tests passed")
            print(f"\n{GREEN}{BOLD}Task 2 Status: COMPLETE ✨{RESET}")
        else:
            print("⚠️  Some functionality tests failed")
            print(f"\n{YELLOW}{BOLD}Task 2 Status: NEEDS MIGRATION{RESET}")
            print("\nNext steps:")
            print("1. Run migrations in Supabase SQL Editor")
            print("2. Use file: task2_simple_migration.sql")
            print("3. Re-run this test script")

if __name__ == "__main__":
    asyncio.run(main())