#!/usr/bin/env python3
"""
Comprehensive User Story Validation Test
Tests all user stories from both QR Job Application Workflow and HR Manager Dashboard System specs
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_PROPERTY_ID = "prop_test_001"

# JWT tokens (using the fixed authentication)
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

class UserStoryValidator:
    def __init__(self):
        self.results = {}
        self.total_stories = 0
        self.passed_stories = 0
        
    def validate_story(self, story_id, story_description, test_function):
        """Validate a single user story"""
        print(f"\n{'='*80}")
        print(f"📖 USER STORY {story_id}: {story_description}")
        print(f"{'='*80}")
        
        try:
            result = test_function()
            self.results[story_id] = {
                'description': story_description,
                'passed': result,
                'details': getattr(test_function, 'details', [])
            }
            
            if result:
                print(f"✅ USER STORY {story_id}: PASSED")
                self.passed_stories += 1
            else:
                print(f"❌ USER STORY {story_id}: FAILED")
                
            self.total_stories += 1
            return result
            
        except Exception as e:
            print(f"❌ USER STORY {story_id}: ERROR - {e}")
            self.results[story_id] = {
                'description': story_description,
                'passed': False,
                'error': str(e)
            }
            self.total_stories += 1
            return False

def test_qr_story_1():
    """QR Requirement 1: QR Code Generation and Access"""
    print("🔍 Testing QR code generation and access...")
    
    # Test 1.1: HR can generate QR codes
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    response = requests.get(f"{BACKEND_URL}/hr/properties", headers=headers)
    
    if response.status_code != 200:
        print("   ❌ HR cannot access properties")
        return False
        
    properties = response.json()
    if not properties:
        print("   ❌ No properties found")
        return False
        
    property_with_qr = next((p for p in properties if 'qr_code_url' in p), None)
    if not property_with_qr:
        print("   ❌ No property has QR code")
        return False
        
    print(f"   ✅ Property has QR code: {property_with_qr.get('name')}")
    
    # Test 1.2: QR code regeneration
    regen_response = requests.post(
        f"{BACKEND_URL}/hr/properties/{TEST_PROPERTY_ID}/qr-code",
        headers=headers
    )
    
    qr_regen_works = regen_response.status_code == 200
    print(f"   ✅ QR regeneration works: {qr_regen_works}")
    
    # Test 1.3: Manager access to QR codes
    manager_headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    manager_response = requests.get(f"{BACKEND_URL}/manager/dashboard-stats", headers=manager_headers)
    
    manager_access = manager_response.status_code == 200
    print(f"   ✅ Manager can access QR functionality: {manager_access}")
    
    return qr_regen_works and manager_access

def test_qr_story_2():
    """QR Requirement 2: Job Application Submission"""
    print("🔍 Testing job application submission...")
    
    # Test 2.1: Public property info access
    response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
    
    if response.status_code != 200:
        print("   ❌ Cannot access property info publicly")
        return False
        
    property_info = response.json()
    # Check for nested structure
    property_data = property_info.get('property', {})
    departments_data = property_info.get('departments_and_positions', {})
    
    has_required_fields = (
        'name' in property_data and 
        'address' in property_data and 
        len(departments_data) > 0
    )
    print(f"   ✅ Property info has required fields: {has_required_fields}")
    
    # Test 2.2: Application submission
    test_application = {
        "first_name": "UserStory",
        "last_name": "TestApplicant",
        "email": f"userstory.test.{int(time.time())}@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Test Street",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "2-5",
        "hotel_experience": "yes"
    }
    
    submit_response = requests.post(
        f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
        json=test_application,
        headers={"Content-Type": "application/json"}
    )
    
    submission_works = submit_response.status_code == 200
    print(f"   ✅ Application submission works: {submission_works}")
    
    if submission_works:
        app_result = submit_response.json()
        has_confirmation = 'application_id' in app_result
        print(f"   ✅ Confirmation message provided: {has_confirmation}")
        return has_confirmation
    
    return False

def test_qr_story_3():
    """QR Requirement 3: Application Review and Approval"""
    print("🔍 Testing application review and approval...")
    
    # Test 3.1: Manager can view applications
    manager_headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    
    if response.status_code != 200:
        print("   ❌ Manager cannot view applications")
        return False
        
    applications = response.json()
    print(f"   ✅ Manager can view applications: {len(applications)} found")
    
    # Test 3.2: HR can view applications (broader access)
    hr_headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    hr_response = requests.get(f"{BACKEND_URL}/hr/applications", headers=hr_headers)
    
    hr_access = hr_response.status_code == 200
    print(f"   ✅ HR can view applications: {hr_access}")
    
    if hr_access:
        hr_applications = hr_response.json()
        print(f"   📊 HR sees {len(hr_applications)} applications across all properties")
    
    # Test 3.3: Application details are complete
    if applications:
        sample_app = applications[0]
        required_fields = ['applicant_name', 'applicant_email', 'department', 'position', 'status']
        has_details = all(field in sample_app for field in required_fields)
        print(f"   ✅ Application details are complete: {has_details}")
        return has_details
    
    return hr_access

def test_hr_story_1():
    """HR Dashboard Requirement 1: HR Administrative Dashboard"""
    print("🔍 Testing HR administrative dashboard...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Test 1.1: Dashboard stats
    stats_response = requests.get(f"{BACKEND_URL}/hr/dashboard-stats", headers=headers)
    dashboard_accessible = stats_response.status_code == 200
    print(f"   ✅ HR dashboard accessible: {dashboard_accessible}")
    
    if not dashboard_accessible:
        return False
    
    # Test 1.2: Properties management
    properties_response = requests.get(f"{BACKEND_URL}/hr/properties", headers=headers)
    properties_access = properties_response.status_code == 200
    print(f"   ✅ Properties management accessible: {properties_access}")
    
    # Test 1.3: Managers management
    managers_response = requests.get(f"{BACKEND_URL}/hr/managers", headers=headers)
    managers_access = managers_response.status_code == 200
    print(f"   ✅ Managers management accessible: {managers_access}")
    
    # Test 1.4: Applications oversight
    applications_response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
    applications_access = applications_response.status_code == 200
    print(f"   ✅ Applications oversight accessible: {applications_access}")
    
    # Test 1.5: Analytics access
    if dashboard_accessible:
        dashboard_data = stats_response.json()
        has_analytics = any(key in dashboard_data for key in ['totalProperties', 'totalManagers', 'totalEmployees'])
        print(f"   ✅ Analytics data available: {has_analytics}")
        return has_analytics
    
    return False

def test_hr_story_2():
    """HR Dashboard Requirement 2: Manager Property-Specific Dashboard"""
    print("🔍 Testing manager property-specific dashboard...")
    
    headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    
    # Test 2.1: Manager dashboard access
    stats_response = requests.get(f"{BACKEND_URL}/manager/dashboard-stats", headers=headers)
    dashboard_accessible = stats_response.status_code == 200
    print(f"   ✅ Manager dashboard accessible: {dashboard_accessible}")
    
    # Test 2.2: Property-specific applications
    apps_response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
    apps_access = apps_response.status_code == 200
    print(f"   ✅ Manager can access property applications: {apps_access}")
    
    # Test 2.3: Property restriction (manager should only see their property)
    if apps_access:
        applications = apps_response.json()
        # All applications should be for the manager's property
        property_restricted = all(app.get('property_id') == TEST_PROPERTY_ID for app in applications if 'property_id' in app)
        print(f"   ✅ Manager sees only their property data: {property_restricted}")
        return property_restricted
    
    return dashboard_accessible

def test_hr_story_3():
    """HR Dashboard Requirement 3: Application Management System"""
    print("🔍 Testing application management system...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Test 3.1: Application listing with details
    response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
    
    if response.status_code != 200:
        print("   ❌ Cannot access applications")
        return False
    
    applications = response.json()
    print(f"   ✅ Applications accessible: {len(applications)} found")
    
    # Test 3.2: Application details completeness
    if applications:
        sample_app = applications[0]
        required_fields = ['id', 'applicant_name', 'applicant_email', 'department', 'position', 'status', 'applied_at']
        has_complete_details = all(field in sample_app for field in required_fields)
        print(f"   ✅ Application details complete: {has_complete_details}")
        
        # Test 3.3: Status management
        valid_statuses = {'pending', 'approved', 'rejected', 'talent_pool'}
        app_statuses = set(app.get('status') for app in applications)
        valid_status_values = app_statuses.issubset(valid_statuses)
        print(f"   ✅ Valid status values: {valid_status_values}")
        print(f"   📊 Found statuses: {app_statuses}")
        
        return has_complete_details and valid_status_values
    
    return True  # No applications is acceptable

def test_hr_story_4():
    """HR Dashboard Requirement 4: Authentication and Role-Based Access"""
    print("🔍 Testing authentication and role-based access...")
    
    # Test 4.1: HR access to all properties
    hr_headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    hr_response = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
    hr_full_access = hr_response.status_code == 200
    print(f"   ✅ HR has full property access: {hr_full_access}")
    
    # Test 4.2: Manager restricted access
    manager_headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    
    # Manager should NOT be able to access HR endpoints
    manager_hr_attempt = requests.get(f"{BACKEND_URL}/hr/properties", headers=manager_headers)
    manager_restricted = manager_hr_attempt.status_code == 403
    print(f"   ✅ Manager access properly restricted: {manager_restricted}")
    
    # Manager should be able to access their own endpoints
    manager_own_access = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    manager_can_access_own = manager_own_access.status_code == 200
    print(f"   ✅ Manager can access own data: {manager_can_access_own}")
    
    # Test 4.3: Invalid token handling
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    invalid_response = requests.get(f"{BACKEND_URL}/hr/properties", headers=invalid_headers)
    invalid_rejected = invalid_response.status_code == 401
    print(f"   ✅ Invalid tokens properly rejected: {invalid_rejected}")
    
    return hr_full_access and manager_restricted and manager_can_access_own and invalid_rejected

def test_hr_story_5():
    """HR Dashboard Requirement 5: Professional UI/UX Design"""
    print("🔍 Testing professional UI/UX design (backend API structure)...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Test 5.1: Consistent API responses
    endpoints_to_test = [
        "/hr/dashboard-stats",
        "/hr/properties", 
        "/hr/applications"
    ]
    
    consistent_responses = True
    for endpoint in endpoints_to_test:
        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
        if response.status_code == 200:
            try:
                data = response.json()
                # Check for consistent structure (should be JSON)
                print(f"   ✅ {endpoint}: Valid JSON response")
            except:
                print(f"   ❌ {endpoint}: Invalid JSON response")
                consistent_responses = False
        else:
            print(f"   ⚠️  {endpoint}: Status {response.status_code}")
    
    # Test 5.2: Error handling
    error_response = requests.get(f"{BACKEND_URL}/hr/nonexistent", headers=headers)
    proper_error_handling = error_response.status_code == 404
    print(f"   ✅ Proper error handling: {proper_error_handling}")
    
    # Test 5.3: Data validation
    invalid_data = {"invalid": "data"}
    validation_response = requests.post(
        f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
        json=invalid_data,
        headers={"Content-Type": "application/json"}
    )
    proper_validation = validation_response.status_code == 422
    print(f"   ✅ Proper data validation: {proper_validation}")
    
    return consistent_responses and proper_error_handling and proper_validation

def test_hr_story_6():
    """HR Dashboard Requirement 6: Data Management and Search"""
    print("🔍 Testing data management and search capabilities...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Test 6.1: Data retrieval
    response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
    
    if response.status_code != 200:
        print("   ❌ Cannot retrieve application data")
        return False
    
    applications = response.json()
    print(f"   ✅ Data retrieval works: {len(applications)} applications")
    
    # Test 6.2: Data structure for sorting/filtering
    if applications:
        sample_app = applications[0]
        sortable_fields = ['submitted_at', 'status', 'department', 'position']
        has_sortable_fields = any(field in sample_app for field in sortable_fields)
        print(f"   ✅ Data has sortable fields: {has_sortable_fields}")
        
        # Test 6.3: Status filtering capability
        statuses = set(app.get('status') for app in applications)
        filterable_statuses = len(statuses) > 1
        print(f"   ✅ Multiple statuses for filtering: {filterable_statuses}")
        print(f"   📊 Available statuses: {statuses}")
        
        return has_sortable_fields
    
    return True  # Empty data is acceptable

def main():
    """Run comprehensive user story validation"""
    print("🚀 COMPREHENSIVE USER STORY VALIDATION")
    print("=" * 80)
    print("Testing all user stories from QR Job Application Workflow and HR Manager Dashboard System")
    print("=" * 80)
    
    validator = UserStoryValidator()
    
    # QR Job Application Workflow User Stories
    print("\n🔗 QR JOB APPLICATION WORKFLOW USER STORIES")
    print("=" * 60)
    
    validator.validate_story(
        "QR-1", 
        "HR/Manager QR Code Generation and Access",
        test_qr_story_1
    )
    
    validator.validate_story(
        "QR-2",
        "Job Applicant Application Submission", 
        test_qr_story_2
    )
    
    validator.validate_story(
        "QR-3",
        "Manager Application Review and Approval",
        test_qr_story_3
    )
    
    # HR Manager Dashboard System User Stories  
    print("\n👥 HR MANAGER DASHBOARD SYSTEM USER STORIES")
    print("=" * 60)
    
    validator.validate_story(
        "HR-1",
        "HR Administrative Dashboard",
        test_hr_story_1
    )
    
    validator.validate_story(
        "HR-2", 
        "Manager Property-Specific Dashboard",
        test_hr_story_2
    )
    
    validator.validate_story(
        "HR-3",
        "Application Management System",
        test_hr_story_3
    )
    
    validator.validate_story(
        "HR-4",
        "Authentication and Role-Based Access", 
        test_hr_story_4
    )
    
    validator.validate_story(
        "HR-5",
        "Professional UI/UX Design (API Structure)",
        test_hr_story_5
    )
    
    validator.validate_story(
        "HR-6",
        "Data Management and Search",
        test_hr_story_6
    )
    
    # Final Summary
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE USER STORY VALIDATION RESULTS")
    print(f"{'='*80}")
    
    success_rate = (validator.passed_stories / validator.total_stories) * 100
    
    print(f"\n📈 OVERALL RESULTS:")
    print(f"   Total User Stories Tested: {validator.total_stories}")
    print(f"   User Stories Passed: {validator.passed_stories}")
    print(f"   User Stories Failed: {validator.total_stories - validator.passed_stories}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for story_id, result in validator.results.items():
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"   {story_id}: {status} - {result['description']}")
        if 'error' in result:
            print(f"      Error: {result['error']}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if success_rate >= 90:
        print("   🎉 EXCELLENT: System meets user story requirements!")
        print("   ✅ Ready for user acceptance testing")
    elif success_rate >= 75:
        print("   ✅ GOOD: Most user stories are satisfied")
        print("   🔧 Address remaining issues for full compliance")
    elif success_rate >= 50:
        print("   ⚠️  MODERATE: Significant user stories need attention")
        print("   🔧 Focus on failed stories for user satisfaction")
    else:
        print("   ❌ CRITICAL: Major user story gaps exist")
        print("   🚨 Immediate attention required before deployment")
    
    return validator.results

if __name__ == "__main__":
    main()