#!/usr/bin/env python3
"""
Simple Frontend Integration Test
Tests the key frontend-backend integration points without complex mocking
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_PROPERTY_ID = "prop_test_001"

# JWT tokens
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

def test_complete_user_journey():
    """Test complete user journey from application to dashboard"""
    print("🚀 TESTING COMPLETE USER JOURNEY")
    print("=" * 60)
    
    results = {}
    
    # Step 1: Job Applicant Journey
    print("\n👤 STEP 1: Job Applicant Journey")
    print("-" * 40)
    
    # Get property info (what frontend form would do)
    try:
        response = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
        if response.status_code == 200:
            property_info = response.json()
            print("   ✅ Property info retrieved for application form")
            print(f"   📍 Property: {property_info['property']['name']}")
            print(f"   🏢 Departments: {len(property_info['departments_and_positions'])} available")
            results['property_info'] = True
        else:
            print(f"   ❌ Property info failed: {response.status_code}")
            results['property_info'] = False
    except Exception as e:
        print(f"   ❌ Property info error: {e}")
        results['property_info'] = False
    
    # Submit application (what frontend form would do)
    test_application = {
        "first_name": "Journey",
        "last_name": "TestUser",
        "email": f"journey.test.{int(time.time())}@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Journey Street",
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
            app_result = response.json()
            print("   ✅ Application submitted successfully")
            print(f"   🆔 Application ID: {app_result.get('application_id')}")
            print(f"   💬 Message: {app_result.get('message')}")
            results['application_submit'] = True
            new_app_id = app_result.get('application_id')
        else:
            print(f"   ❌ Application submission failed: {response.status_code}")
            results['application_submit'] = False
            new_app_id = None
    except Exception as e:
        print(f"   ❌ Application submission error: {e}")
        results['application_submit'] = False
        new_app_id = None
    
    # Step 2: Manager Dashboard Journey
    print("\n👨‍💼 STEP 2: Manager Dashboard Journey")
    print("-" * 40)
    
    manager_headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    
    # Get manager dashboard stats (what frontend dashboard would do)
    try:
        response = requests.get(f"{BACKEND_URL}/manager/dashboard-stats", headers=manager_headers)
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Manager dashboard stats loaded")
            print(f"   🏨 Property: {stats.get('propertyName')}")
            print(f"   📊 Total Applications: {stats.get('totalApplications')}")
            print(f"   ⏳ Pending Applications: {stats.get('pendingApplications')}")
            results['manager_stats'] = True
        else:
            print(f"   ❌ Manager stats failed: {response.status_code}")
            results['manager_stats'] = False
    except Exception as e:
        print(f"   ❌ Manager stats error: {e}")
        results['manager_stats'] = False
    
    # Get manager applications (what frontend applications tab would do)
    try:
        response = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
        if response.status_code == 200:
            applications = response.json()
            print("   ✅ Manager applications loaded")
            print(f"   📋 Applications visible: {len(applications)}")
            
            # Check if new application is visible
            if new_app_id:
                new_app_visible = any(app.get('id') == new_app_id for app in applications)
                print(f"   👀 New application visible: {new_app_visible}")
                results['new_app_visible'] = new_app_visible
            else:
                results['new_app_visible'] = False
                
            results['manager_applications'] = True
        else:
            print(f"   ❌ Manager applications failed: {response.status_code}")
            results['manager_applications'] = False
            results['new_app_visible'] = False
    except Exception as e:
        print(f"   ❌ Manager applications error: {e}")
        results['manager_applications'] = False
        results['new_app_visible'] = False
    
    # Step 3: HR Dashboard Journey
    print("\n👩‍💼 STEP 3: HR Dashboard Journey")
    print("-" * 40)
    
    hr_headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Get HR dashboard stats (what frontend HR dashboard would do)
    try:
        response = requests.get(f"{BACKEND_URL}/hr/dashboard-stats", headers=hr_headers)
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ HR dashboard stats loaded")
            print(f"   🏢 Total Properties: {stats.get('totalProperties')}")
            print(f"   👥 Total Managers: {stats.get('totalManagers')}")
            print(f"   📊 Pending Applications: {stats.get('pendingApplications')}")
            results['hr_stats'] = True
        else:
            print(f"   ❌ HR stats failed: {response.status_code}")
            results['hr_stats'] = False
    except Exception as e:
        print(f"   ❌ HR stats error: {e}")
        results['hr_stats'] = False
    
    # Get HR applications (what frontend HR applications tab would do)
    try:
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=hr_headers)
        if response.status_code == 200:
            applications = response.json()
            print("   ✅ HR applications loaded")
            print(f"   📋 Total applications visible: {len(applications)}")
            
            # Check if new application is visible to HR
            if new_app_id:
                new_app_visible_hr = any(app.get('id') == new_app_id for app in applications)
                print(f"   👀 New application visible to HR: {new_app_visible_hr}")
                results['new_app_visible_hr'] = new_app_visible_hr
            else:
                results['new_app_visible_hr'] = False
                
            results['hr_applications'] = True
        else:
            print(f"   ❌ HR applications failed: {response.status_code}")
            results['hr_applications'] = False
            results['new_app_visible_hr'] = False
    except Exception as e:
        print(f"   ❌ HR applications error: {e}")
        results['hr_applications'] = False
        results['new_app_visible_hr'] = False
    
    # Step 4: QR Code Generation (what frontend would do)
    print("\n📱 STEP 4: QR Code Generation")
    print("-" * 40)
    
    try:
        response = requests.post(f"{BACKEND_URL}/hr/properties/{TEST_PROPERTY_ID}/qr-code", headers=hr_headers)
        if response.status_code == 200:
            qr_result = response.json()
            print("   ✅ QR code generated successfully")
            print(f"   🔗 QR URL available: {'qr_code_url' in qr_result}")
            results['qr_generation'] = True
        else:
            print(f"   ❌ QR generation failed: {response.status_code}")
            results['qr_generation'] = False
    except Exception as e:
        print(f"   ❌ QR generation error: {e}")
        results['qr_generation'] = False
    
    # Final Summary
    print(f"\n{'='*60}")
    print("📊 COMPLETE USER JOURNEY RESULTS")
    print(f"{'='*60}")
    
    passed_steps = sum(results.values())
    total_steps = len(results)
    success_rate = (passed_steps / total_steps) * 100
    
    print(f"\n📈 JOURNEY RESULTS:")
    print(f"   Total Steps: {total_steps}")
    print(f"   Passed Steps: {passed_steps}")
    print(f"   Failed Steps: {total_steps - passed_steps}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 STEP-BY-STEP RESULTS:")
    step_names = {
        'property_info': '1. Property Info Retrieval',
        'application_submit': '2. Application Submission',
        'manager_stats': '3. Manager Dashboard Stats',
        'manager_applications': '4. Manager Applications View',
        'new_app_visible': '5. New App Visible to Manager',
        'hr_stats': '6. HR Dashboard Stats',
        'hr_applications': '7. HR Applications View',
        'new_app_visible_hr': '8. New App Visible to HR',
        'qr_generation': '9. QR Code Generation'
    }
    
    for key, passed in results.items():
        step_name = step_names.get(key, key)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {step_name}: {status}")
    
    print(f"\n🎯 FRONTEND INTEGRATION STATUS:")
    if success_rate >= 90:
        print("   🎉 EXCELLENT: Complete user journey working perfectly!")
        print("   ✅ Frontend can integrate seamlessly with backend")
        print("   🚀 Ready for frontend development and UI testing")
    elif success_rate >= 75:
        print("   ✅ GOOD: Most user journey steps working")
        print("   🔧 Minor issues to address for full functionality")
    elif success_rate >= 50:
        print("   ⚠️  MODERATE: Significant journey issues")
        print("   🔧 Focus on failed steps")
    else:
        print("   ❌ CRITICAL: Major journey failures")
        print("   🚨 Backend integration needs attention")
    
    return results

if __name__ == "__main__":
    test_complete_user_journey()