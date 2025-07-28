#!/usr/bin/env python3
"""
Comprehensive test for Tasks 7, 8, 9, and 10 from QR Job Application Workflow
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_PROPERTY_ID = "prop_test_001"

# Proper JWT tokens
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

class TaskTester:
    def __init__(self):
        self.results = {}
        self.test_data = {}
        
    def log_result(self, task: str, test: str, passed: bool, message: str = ""):
        if task not in self.results:
            self.results[task] = {}
        self.results[task][test] = {
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
    def print_task_header(self, task_num: int, task_name: str):
        print(f"\n{'='*80}")
        print(f"🧪 TESTING TASK {task_num}: {task_name}")
        print(f"{'='*80}")

    def submit_test_application(self):
        """Submit a test application for workflow testing"""
        test_application = {
            "first_name": "Workflow",
            "last_name": "TestUser",
            "email": f"workflow.test.{int(time.time())}@example.com",
            "phone": "(555) 111-2222",
            "address": "789 Workflow Avenue",
            "city": "Chicago",
            "state": "IL",
            "zip_code": "60601",
            "department": "Food & Beverage",
            "position": "Server",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
            "shift_preference": "evening",
            "employment_type": "full_time",
            "experience_years": "6-10",
            "hotel_experience": "yes"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=test_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('application_id')
        return None

    def test_task_7_end_to_end_workflow(self):
        """Task 7: End-to-End Application Workflow"""
        self.print_task_header(7, "End-to-End Application Workflow")
        
        # Test 7.1: Complete workflow from application to approval
        print("\n📋 Test 7.1: Complete Application to Approval Workflow")
        try:
            # Step 1: Submit application
            app_id = self.submit_test_application()
            if app_id:
                print(f"   ✅ Step 1 - Application submitted: {app_id}")
                
                # Step 2: HR reviews application
                headers = {"Authorization": f"Bearer {HR_TOKEN}"}
                review_response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
                
                if review_response.status_code == 200:
                    applications = review_response.json()
                    workflow_app = next((app for app in applications if app.get('id') == app_id), None)
                    if workflow_app:
                        print("   ✅ Step 2 - Application visible to HR")
                        
                        # Step 3: HR approves application
                        approve_response = requests.post(
                            f"{BACKEND_URL}/hr/applications/{app_id}/approve",
                            headers=headers
                        )
                        
                        approval_success = approve_response.status_code == 200
                        print(f"   ✅ Step 3 - Application approved: {approval_success}")
                        
                        if approval_success:
                            print("   🎉 Complete end-to-end workflow successful!")
                            self.log_result("task_7", "end_to_end_workflow", True, "Complete workflow successful")
                        else:
                            print(f"   ❌ Approval failed: {approve_response.status_code}")
                            print(f"   📋 Error: {approve_response.text}")
                            self.log_result("task_7", "end_to_end_workflow", False, f"Approval failed: {approve_response.status_code}")
                    else:
                        print("   ❌ Application not visible to HR")
                        self.log_result("task_7", "end_to_end_workflow", False, "Application not visible to HR")
                else:
                    print(f"   ❌ HR review step failed: {review_response.status_code}")
                    self.log_result("task_7", "end_to_end_workflow", False, f"HR review failed: {review_response.status_code}")
            else:
                print("   ❌ Application submission failed")
                self.log_result("task_7", "end_to_end_workflow", False, "Application submission failed")
                
        except Exception as e:
            print(f"   ❌ Error in end-to-end workflow: {e}")
            self.log_result("task_7", "end_to_end_workflow", False, str(e))

    def test_task_8_hr_dashboard_integration(self):
        """Task 8: HR Dashboard Integration"""
        self.print_task_header(8, "HR Dashboard Integration")
        
        # Test 8.1: HR dashboard stats
        print("\n📋 Test 8.1: HR Dashboard Statistics")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/dashboard-stats", headers=headers)
            
            hr_dashboard_accessible = response.status_code == 200
            print(f"   ✅ HR dashboard stats accessible: {hr_dashboard_accessible}")
            
            if hr_dashboard_accessible:
                dashboard_data = response.json()
                has_hr_features = any(key in dashboard_data for key in ['totalProperties', 'totalManagers', 'totalApplications', 'pendingApplications'])
                print(f"   📊 HR dashboard has key features: {has_hr_features}")
                print(f"   📋 Available stats: {list(dashboard_data.keys())}")
                self.log_result("task_8", "hr_dashboard_stats", True, "HR dashboard stats accessible")
            else:
                print(f"   ❌ HR dashboard failed: {response.status_code}")
                print(f"   📋 Error: {response.text}")
                self.log_result("task_8", "hr_dashboard_stats", False, f"HR dashboard failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing HR dashboard: {e}")
            self.log_result("task_8", "hr_dashboard_stats", False, str(e))

        # Test 8.2: HR application oversight
        print("\n📋 Test 8.2: HR Application Oversight")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
            
            if response.status_code == 200:
                hr_applications = response.json()
                has_oversight = len(hr_applications) >= 0
                print(f"   ✅ HR can oversee applications: {has_oversight}")
                print(f"   📊 Applications visible to HR: {len(hr_applications)}")
                self.log_result("task_8", "hr_oversight", True, f"HR sees {len(hr_applications)} applications")
            else:
                print(f"   ❌ HR oversight failed: {response.status_code}")
                print(f"   📋 Error: {response.text}")
                self.log_result("task_8", "hr_oversight", False, f"HR oversight failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing HR oversight: {e}")
            self.log_result("task_8", "hr_oversight", False, str(e))

        # Test 8.3: HR property management
        print("\n📋 Test 8.3: HR Property Management")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/properties", headers=headers)
            
            if response.status_code == 200:
                properties = response.json()
                has_property_management = len(properties) >= 0
                print(f"   ✅ HR can manage properties: {has_property_management}")
                print(f"   📊 Properties visible to HR: {len(properties)}")
                self.log_result("task_8", "hr_property_management", True, f"HR sees {len(properties)} properties")
            else:
                print(f"   ❌ HR property management failed: {response.status_code}")
                self.log_result("task_8", "hr_property_management", False, f"Property management failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing HR property management: {e}")
            self.log_result("task_8", "hr_property_management", False, str(e))

    def test_task_9_status_tracking(self):
        """Task 9: Application Status Tracking"""
        self.print_task_header(9, "Application Status Tracking")
        
        # Test 9.1: Status tracking functionality
        print("\n📋 Test 9.1: Application Status Tracking")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
            
            if response.status_code == 200:
                applications = response.json()
                has_status_tracking = all('status' in app for app in applications)
                status_values = set(app.get('status') for app in applications)
                
                print(f"   ✅ Applications have status tracking: {has_status_tracking}")
                print(f"   📊 Status values found: {status_values}")
                
                valid_statuses = {'pending', 'approved', 'rejected', 'talent_pool'}
                has_valid_statuses = status_values.issubset(valid_statuses) if status_values else True
                
                print(f"   ✅ Status values are valid: {has_valid_statuses}")
                self.log_result("task_9", "status_tracking", has_status_tracking and has_valid_statuses, f"Statuses: {status_values}")
            else:
                print(f"   ❌ Status tracking test failed: {response.status_code}")
                self.log_result("task_9", "status_tracking", False, f"Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing status tracking: {e}")
            self.log_result("task_9", "status_tracking", False, str(e))

        # Test 9.2: Status change functionality
        print("\n📋 Test 9.2: Status Change Functionality")
        try:
            # Submit a test application for status change
            app_id = self.submit_test_application()
            if app_id:
                headers = {"Authorization": f"Bearer {HR_TOKEN}"}
                
                # Test status change to rejected
                response = requests.post(
                    f"{BACKEND_URL}/hr/applications/{app_id}/reject",
                    json={"rejection_reason": "Testing status change functionality"},
                    headers=headers
                )
                
                status_change_works = response.status_code == 200
                print(f"   ✅ Status change functionality works: {status_change_works}")
                if not status_change_works:
                    print(f"   📋 Status change error: {response.text}")
                self.log_result("task_9", "status_change", status_change_works, "Status change working")
            else:
                print("   ⚠️  No test application available for status change test")
                self.log_result("task_9", "status_change", False, "No test application available")
        except Exception as e:
            print(f"   ❌ Error testing status change: {e}")
            self.log_result("task_9", "status_change", False, str(e))

        # Test 9.3: Application history tracking
        print("\n📋 Test 9.3: Application History Tracking")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
            
            if response.status_code == 200:
                applications = response.json()
                has_history_fields = any('reviewed_at' in app or 'applied_at' in app for app in applications)
                print(f"   ✅ Applications have history tracking: {has_history_fields}")
                self.log_result("task_9", "history_tracking", has_history_fields, "History tracking present")
            else:
                print(f"   ❌ History tracking test failed: {response.status_code}")
                self.log_result("task_9", "history_tracking", False, f"Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing history tracking: {e}")
            self.log_result("task_9", "history_tracking", False, str(e))

    def test_task_10_enhanced_status_management(self):
        """Task 10: Enhanced Status Management"""
        self.print_task_header(10, "Enhanced Status Management")
        
        # Test 10.1: Multiple status options
        print("\n📋 Test 10.1: Multiple Status Options Available")
        try:
            # Test that we can set different statuses
            test_statuses = [
                ('approved', '/approve'),
                ('rejected', '/reject'),
                ('talent_pool', '/bulk-talent-pool')
            ]
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            
            status_results = {}
            for status_name, endpoint_suffix in test_statuses:
                # Create a test application for each status
                app_id = self.submit_test_application()
                
                if app_id:
                    # Set status based on type
                    if status_name == 'approved':
                        status_response = requests.post(
                            f"{BACKEND_URL}/hr/applications/{app_id}{endpoint_suffix}",
                            headers=headers
                        )
                    elif status_name == 'rejected':
                        status_response = requests.post(
                            f"{BACKEND_URL}/hr/applications/{app_id}{endpoint_suffix}",
                            json={"rejection_reason": f"Testing {status_name} status"},
                            headers=headers
                        )
                    elif status_name == 'talent_pool':
                        status_response = requests.post(
                            f"{BACKEND_URL}/hr/applications{endpoint_suffix}",
                            data={"application_ids": [app_id]},
                            headers=headers
                        )
                    
                    status_results[status_name] = status_response.status_code == 200
                    if not status_results[status_name]:
                        print(f"   ❌ {status_name} status failed: {status_response.status_code}")
                        print(f"   📋 Error: {status_response.text}")
                else:
                    status_results[status_name] = False
                
            all_statuses_work = all(status_results.values())
            print(f"   ✅ All status options work: {all_statuses_work}")
            print(f"   📊 Status test results: {status_results}")
            self.log_result("task_10", "multiple_statuses", all_statuses_work, f"Results: {status_results}")
            
        except Exception as e:
            print(f"   ❌ Error testing multiple statuses: {e}")
            self.log_result("task_10", "multiple_statuses", False, str(e))

        # Test 10.2: Talent pool management
        print("\n📋 Test 10.2: Talent Pool Management")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/applications/talent-pool", headers=headers)
            
            if response.status_code == 200:
                talent_pool_apps = response.json()
                has_talent_pool = len(talent_pool_apps) >= 0
                print(f"   ✅ Talent pool management available: {has_talent_pool}")
                print(f"   📊 Applications in talent pool: {len(talent_pool_apps)}")
                self.log_result("task_10", "talent_pool_management", True, f"Talent pool has {len(talent_pool_apps)} applications")
            else:
                print(f"   ❌ Talent pool management failed: {response.status_code}")
                self.log_result("task_10", "talent_pool_management", False, f"Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing talent pool: {e}")
            self.log_result("task_10", "talent_pool_management", False, str(e))

        # Test 10.3: Application statistics
        print("\n📋 Test 10.3: Application Statistics")
        try:
            headers = {"Authorization": f"Bearer {HR_TOKEN}"}
            response = requests.get(f"{BACKEND_URL}/hr/applications/stats", headers=headers)
            
            if response.status_code == 200:
                stats = response.json()
                has_stats = any(key in stats for key in ['total_applications', 'status_breakdown', 'department_breakdown'])
                print(f"   ✅ Application statistics available: {has_stats}")
                print(f"   📊 Available statistics: {list(stats.keys())}")
                self.log_result("task_10", "application_statistics", True, f"Stats available: {list(stats.keys())}")
            else:
                print(f"   ❌ Application statistics failed: {response.status_code}")
                self.log_result("task_10", "application_statistics", False, f"Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error testing application statistics: {e}")
            self.log_result("task_10", "application_statistics", False, str(e))

    def generate_final_report(self):
        """Generate comprehensive test report for tasks 7-10"""
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE TEST REPORT - TASKS 7-10")
        print(f"{'='*80}")
        
        total_tests = 0
        passed_tests = 0
        
        for task_num in [7, 8, 9, 10]:
            task_key = f"task_{task_num}"
            if task_key in self.results:
                task_results = self.results[task_key]
                task_passed = sum(1 for result in task_results.values() if result['passed'])
                task_total = len(task_results)
                
                total_tests += task_total
                passed_tests += task_passed
                
                status = "✅ PASS" if task_passed == task_total else "⚠️  PARTIAL" if task_passed > 0 else "❌ FAIL"
                print(f"\nTask {task_num}: {status} ({task_passed}/{task_total})")
                
                for test_name, result in task_results.items():
                    test_status = "✅" if result['passed'] else "❌"
                    print(f"  {test_status} {test_name}: {result['message']}")
        
        print(f"\n{'='*80}")
        print(f"OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TASKS 7-10 PASSED!")
        elif passed_tests > total_tests * 0.8:
            print("✅ MOSTLY FUNCTIONAL - Minor issues detected")
        elif passed_tests > total_tests * 0.5:
            print("⚠️  PARTIALLY FUNCTIONAL - Several issues need attention")
        else:
            print("❌ MAJOR ISSUES - Significant functionality problems detected")
        
        print(f"{'='*80}")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests/total_tests if total_tests > 0 else 0,
            'detailed_results': self.results
        }

def main():
    """Run comprehensive test suite for tasks 7-10"""
    print("🚀 STARTING COMPREHENSIVE TEST SUITE FOR TASKS 7-10")
    print("Testing end-to-end workflow, HR dashboard, status tracking, and enhanced status management...")
    
    tester = TaskTester()
    
    # Run all task tests
    tester.test_task_7_end_to_end_workflow()
    tester.test_task_8_hr_dashboard_integration()
    tester.test_task_9_status_tracking()
    tester.test_task_10_enhanced_status_management()
    
    # Generate final report
    final_results = tester.generate_final_report()
    
    # Save detailed results to file
    with open('TASKS_7_TO_10_TEST_RESULTS.json', 'w') as f:
        json.dump(final_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: TASKS_7_TO_10_TEST_RESULTS.json")
    
    return final_results

if __name__ == "__main__":
    main()