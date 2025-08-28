#!/usr/bin/env python3
"""
Comprehensive Frontend Validation Test
Tests frontend components and their integration with backend APIs
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"  # Assuming React dev server
TEST_PROPERTY_ID = "prop_test_001"

# JWT tokens
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

class FrontendValidator:
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def test_component(self, component_name, test_function):
        """Test a frontend component"""
        print(f"\n{'='*80}")
        print(f"🧪 TESTING FRONTEND COMPONENT: {component_name}")
        print(f"{'='*80}")
        
        try:
            result = test_function()
            self.results[component_name] = {
                'passed': result,
                'details': getattr(test_function, 'details', [])
            }
            
            if result:
                print(f"✅ COMPONENT {component_name}: PASSED")
                self.passed_tests += 1
            else:
                print(f"❌ COMPONENT {component_name}: FAILED")
                
            self.total_tests += 1
            return result
            
        except Exception as e:
            print(f"❌ COMPONENT {component_name}: ERROR - {e}")
            self.results[component_name] = {
                'passed': False,
                'error': str(e)
            }
            self.total_tests += 1
            return False

def test_frontend_server_running():
    """Test if frontend development server is running"""
    print("🔍 Testing frontend server availability...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        server_running = response.status_code == 200
        print(f"   ✅ Frontend server running: {server_running}")
        return server_running
    except requests.exceptions.RequestException:
        print("   ❌ Frontend server not running")
        print("   💡 To start frontend: cd hotel-onboarding-frontend && npm run dev")
        return False

def test_job_application_form_integration():
    """Test Job Application Form integration with backend"""
    print("🔍 Testing Job Application Form integration...")
    
    # Test 1: Property info endpoint for form
    try:
        response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
        if response.status_code == 200:
            property_info = response.json()
            has_departments = 'departments_and_positions' in property_info
            has_property_data = 'property' in property_info
            print(f"   ✅ Property info for form: {has_departments and has_property_data}")
        else:
            print(f"   ❌ Property info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Property info error: {e}")
        return False
    
    # Test 2: Application submission endpoint
    test_application = {
        "first_name": "Frontend",
        "last_name": "TestUser",
        "email": f"frontend.test.{int(time.time())}@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Frontend Street",
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
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=test_application,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            has_confirmation = 'application_id' in result and 'message' in result
            print(f"   ✅ Application submission: {has_confirmation}")
            return has_confirmation
        else:
            print(f"   ❌ Application submission failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Application submission error: {e}")
        return False

def test_hr_dashboard_integration():
    """Test HR Dashboard integration with backend APIs"""
    print("🔍 Testing HR Dashboard integration...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Test dashboard stats endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/hr/dashboard-stats", headers=headers)
        dashboard_stats = response.status_code == 200
        print(f"   ✅ Dashboard stats API: {dashboard_stats}")
    except Exception as e:
        print(f"   ❌ Dashboard stats error: {e}")
        dashboard_stats = False
    
    # Test properties endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/hr/properties", headers=headers)
        properties_api = response.status_code == 200
        print(f"   ✅ Properties API: {properties_api}")
    except Exception as e:
        print(f"   ❌ Properties error: {e}")
        properties_api = False
    
    # Test managers endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/hr/managers", headers=headers)
        managers_api = response.status_code == 200
        print(f"   ✅ Managers API: {managers_api}")
    except Exception as e:
        print(f"   ❌ Managers error: {e}")
        managers_api = False
    
    # Test applications endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
        applications_api = response.status_code == 200
        if applications_api:
            apps = response.json()
            has_required_fields = len(apps) > 0 and all(
                field in apps[0] for field in ['applicant_name', 'applicant_email', 'status']
            )
            print(f"   ✅ Applications API with data: {has_required_fields}")
        else:
            print(f"   ❌ Applications API failed: {response.status_code}")
            has_required_fields = False
    except Exception as e:
        print(f"   ❌ Applications error: {e}")
        has_required_fields = False
    
    return dashboard_stats and properties_api and managers_api and has_required_fields

def test_manager_dashboard_integration():
    """Test Manager Dashboard integration with backend APIs"""
    print("🔍 Testing Manager Dashboard integration...")
    
    headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    
    # Test manager dashboard stats
    try:
        response = requests.get(f"{BACKEND_URL}/manager/dashboard-stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            has_manager_stats = all(
                field in stats for field in ['propertyId', 'propertyName', 'totalApplications']
            )
            print(f"   ✅ Manager dashboard stats: {has_manager_stats}")
        else:
            print(f"   ❌ Manager dashboard stats failed: {response.status_code}")
            has_manager_stats = False
    except Exception as e:
        print(f"   ❌ Manager dashboard stats error: {e}")
        has_manager_stats = False
    
    # Test manager applications
    try:
        response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
        if response.status_code == 200:
            apps = response.json()
            has_manager_apps = isinstance(apps, list)
            if has_manager_apps and len(apps) > 0:
                has_required_fields = all(
                    field in apps[0] for field in ['applicant_name', 'status', 'property_id']
                )
                print(f"   ✅ Manager applications with data: {has_required_fields}")
                return has_manager_stats and has_required_fields
            else:
                print(f"   ✅ Manager applications (empty): {has_manager_apps}")
                return has_manager_stats and has_manager_apps
        else:
            print(f"   ❌ Manager applications failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Manager applications error: {e}")
        return False

def test_authentication_integration():
    """Test authentication integration"""
    print("🔍 Testing authentication integration...")
    
    # Test HR authentication
    hr_headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    try:
        response = requests.get(f"{BACKEND_URL}/auth/me", headers=hr_headers)
        if response.status_code == 200:
            user_info = response.json()
            hr_auth_valid = user_info.get('role') == 'hr'
            print(f"   ✅ HR authentication: {hr_auth_valid}")
        else:
            print(f"   ❌ HR authentication failed: {response.status_code}")
            hr_auth_valid = False
    except Exception as e:
        print(f"   ❌ HR authentication error: {e}")
        hr_auth_valid = False
    
    # Test Manager authentication
    manager_headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    try:
        response = requests.get(f"{BACKEND_URL}/auth/me", headers=manager_headers)
        if response.status_code == 200:
            user_info = response.json()
            manager_auth_valid = user_info.get('role') == 'manager'
            print(f"   ✅ Manager authentication: {manager_auth_valid}")
        else:
            print(f"   ❌ Manager authentication failed: {response.status_code}")
            manager_auth_valid = False
    except Exception as e:
        print(f"   ❌ Manager authentication error: {e}")
        manager_auth_valid = False
    
    # Test invalid token handling
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    try:
        response = requests.get(f"{BACKEND_URL}/auth/me", headers=invalid_headers)
        invalid_rejected = response.status_code == 401
        print(f"   ✅ Invalid token rejection: {invalid_rejected}")
    except Exception as e:
        print(f"   ❌ Invalid token test error: {e}")
        invalid_rejected = False
    
    return hr_auth_valid and manager_auth_valid and invalid_rejected

def test_qr_code_functionality():
    """Test QR code functionality for frontend"""
    print("🔍 Testing QR code functionality...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Test QR code generation
    try:
        response = requests.post(f"{BACKEND_URL}/hr/properties/{TEST_PROPERTY_ID}/qr-code", headers=headers)
        qr_generation = response.status_code == 200
        print(f"   ✅ QR code generation: {qr_generation}")
        
        if qr_generation:
            qr_data = response.json()
            has_qr_url = 'qr_code_url' in qr_data
            print(f"   ✅ QR code URL provided: {has_qr_url}")
            return has_qr_url
        else:
            print(f"   ❌ QR generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ QR code error: {e}")
        return False

def test_form_validation_endpoints():
    """Test form validation endpoints"""
    print("🔍 Testing form validation endpoints...")
    
    # Test invalid application data
    invalid_application = {
        "first_name": "",  # Invalid: empty
        "email": "invalid-email",  # Invalid: bad format
        "phone": "123",  # Invalid: too short
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}",
            json=invalid_application,
            headers={"Content-Type": "application/json"}
        )
        
        validation_working = response.status_code == 422  # Unprocessable Entity
        print(f"   ✅ Form validation working: {validation_working}")
        
        if validation_working:
            error_data = response.json()
            has_error_details = 'detail' in error_data
            print(f"   ✅ Validation error details: {has_error_details}")
            return has_error_details
        else:
            print(f"   ❌ Validation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Validation test error: {e}")
        return False

def main():
    """Run comprehensive frontend validation"""
    print("🚀 COMPREHENSIVE FRONTEND VALIDATION")
    print("=" * 80)
    print("Testing frontend components and their backend integration")
    print("=" * 80)
    
    validator = FrontendValidator()
    
    # Test frontend server availability
    frontend_server_running = test_frontend_server_running()
    
    # Test backend integration components
    print("\n🔗 FRONTEND-BACKEND INTEGRATION TESTS")
    print("=" * 60)
    
    validator.test_component(
        "Job Application Form Integration",
        test_job_application_form_integration
    )
    
    validator.test_component(
        "HR Dashboard Integration", 
        test_hr_dashboard_integration
    )
    
    validator.test_component(
        "Manager Dashboard Integration",
        test_manager_dashboard_integration
    )
    
    validator.test_component(
        "Authentication Integration",
        test_authentication_integration
    )
    
    validator.test_component(
        "QR Code Functionality",
        test_qr_code_functionality
    )
    
    validator.test_component(
        "Form Validation Endpoints",
        test_form_validation_endpoints
    )
    
    # Final Summary
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE FRONTEND VALIDATION RESULTS")
    print(f"{'='*80}")
    
    success_rate = (validator.passed_tests / validator.total_tests) * 100 if validator.total_tests > 0 else 0
    
    print(f"\n📈 OVERALL RESULTS:")
    print(f"   Frontend Server Running: {'✅' if frontend_server_running else '❌'}")
    print(f"   Total Components Tested: {validator.total_tests}")
    print(f"   Components Passed: {validator.passed_tests}")
    print(f"   Components Failed: {validator.total_tests - validator.passed_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for component, result in validator.results.items():
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"   {component}: {status}")
        if 'error' in result:
            print(f"      Error: {result['error']}")
    
    # Recommendations
    print(f"\n🎯 FRONTEND RECOMMENDATIONS:")
    if not frontend_server_running:
        print("   🚨 CRITICAL: Start frontend development server")
        print("   💡 Run: cd hotel-onboarding-frontend && npm run dev")
    
    if success_rate >= 90:
        print("   🎉 EXCELLENT: Frontend integration is working perfectly!")
        print("   ✅ Ready for end-to-end user testing")
    elif success_rate >= 75:
        print("   ✅ GOOD: Most frontend integrations working")
        print("   🔧 Address remaining issues for full functionality")
    elif success_rate >= 50:
        print("   ⚠️  MODERATE: Significant frontend issues need attention")
        print("   🔧 Focus on failed components")
    else:
        print("   ❌ CRITICAL: Major frontend integration issues")
        print("   🚨 Immediate attention required")
    
    print(f"\n🔗 NEXT STEPS:")
    if frontend_server_running and success_rate >= 90:
        print("   1. ✅ Backend APIs working perfectly")
        print("   2. 🌐 Test frontend UI components manually")
        print("   3. 🧪 Run frontend unit tests: npm test")
        print("   4. 🚀 Ready for user acceptance testing")
    else:
        print("   1. 🔧 Fix failing backend integrations")
        print("   2. 🌐 Start frontend development server")
        print("   3. 🧪 Test individual components")
    
    return validator.results

if __name__ == "__main__":
    main()