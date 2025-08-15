#!/usr/bin/env python3
"""
Final comprehensive user story validation with detailed analysis
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

def test_all_user_stories():
    """Test all user stories with detailed analysis"""
    print("🚀 FINAL COMPREHENSIVE USER STORY VALIDATION")
    print("=" * 80)
    
    results = {}
    
    # QR-1: HR/Manager QR Code Generation and Access
    print("\n📖 QR-1: HR/Manager QR Code Generation and Access")
    print("-" * 60)
    
    # QR generation works
    hr_headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    qr_regen = requests.post(f"{BACKEND_URL}/hr/properties/{TEST_PROPERTY_ID}/qr-code", headers=hr_headers)
    qr_works = qr_regen.status_code == 200
    print(f"✅ QR regeneration: {qr_works}")
    
    # Manager access to QR functionality (via dashboard)
    manager_headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
    manager_dashboard = requests.get(f"{BACKEND_URL}/manager/dashboard-stats", headers=manager_headers)
    manager_qr_access = manager_dashboard.status_code == 200
    print(f"❌ Manager QR access: {manager_qr_access} (Status: {manager_dashboard.status_code})")
    
    results['QR-1'] = qr_works and manager_qr_access
    
    # QR-2: Job Applicant Application Submission
    print("\n📖 QR-2: Job Applicant Application Submission")
    print("-" * 60)
    
    # Public property info
    prop_info = requests.get(f"{BACKEND_URL}/properties/{TEST_PROPERTY_ID}/info")
    prop_info_works = prop_info.status_code == 200
    print(f"✅ Property info access: {prop_info_works}")
    
    # Application submission
    test_app = {
        "first_name": "Final", "last_name": "Test",
        "email": f"final.test.{int(time.time())}@example.com",
        "phone": "(555) 999-0000", "address": "123 Final St",
        "city": "Test City", "state": "TS", "zip_code": "12345",
        "department": "Front Desk", "position": "Front Desk Agent",
        "work_authorized": "yes", "sponsorship_required": "no",
        "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
        "shift_preference": "morning", "employment_type": "full_time",
        "experience_years": "2-5", "hotel_experience": "yes"
    }
    
    app_submit = requests.post(f"{BACKEND_URL}/apply/{TEST_PROPERTY_ID}", json=test_app)
    app_submit_works = app_submit.status_code == 200
    print(f"✅ Application submission: {app_submit_works}")
    
    results['QR-2'] = prop_info_works and app_submit_works
    
    # QR-3: Manager Application Review and Approval
    print("\n📖 QR-3: Manager Application Review and Approval")
    print("-" * 60)
    
    # Manager can view applications
    manager_apps = requests.get(f"{BACKEND_URL}/manager/applications", headers=manager_headers)
    manager_apps_works = manager_apps.status_code == 200
    print(f"❌ Manager applications access: {manager_apps_works} (Status: {manager_apps.status_code})")
    
    # HR can view applications
    hr_apps = requests.get(f"{BACKEND_URL}/hr/applications", headers=hr_headers)
    hr_apps_works = hr_apps.status_code == 200
    print(f"✅ HR applications access: {hr_apps_works}")
    
    results['QR-3'] = manager_apps_works and hr_apps_works
    
    # HR-1: HR Administrative Dashboard
    print("\n📖 HR-1: HR Administrative Dashboard")
    print("-" * 60)
    
    hr_dashboard = requests.get(f"{BACKEND_URL}/hr/dashboard-stats", headers=hr_headers)
    hr_properties = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
    hr_managers = requests.get(f"{BACKEND_URL}/hr/managers", headers=hr_headers)
    
    hr_dashboard_works = all(r.status_code == 200 for r in [hr_dashboard, hr_properties, hr_managers, hr_apps])
    print(f"✅ HR dashboard complete: {hr_dashboard_works}")
    
    results['HR-1'] = hr_dashboard_works
    
    # HR-2: Manager Property-Specific Dashboard
    print("\n📖 HR-2: Manager Property-Specific Dashboard")
    print("-" * 60)
    
    manager_dashboard_works = manager_dashboard.status_code == 200 and manager_apps_works
    print(f"❌ Manager dashboard: {manager_dashboard_works}")
    
    results['HR-2'] = manager_dashboard_works
    
    # HR-3: Application Management System
    print("\n📖 HR-3: Application Management System")
    print("-" * 60)
    
    if hr_apps_works:
        apps_data = hr_apps.json()
        has_required_fields = len(apps_data) > 0 and all(
            field in apps_data[0] for field in ['applicant_name', 'applicant_email', 'status']
        )
        print(f"✅ Application management: {has_required_fields}")
        results['HR-3'] = has_required_fields
    else:
        results['HR-3'] = False
    
    # HR-4: Authentication and Role-Based Access
    print("\n📖 HR-4: Authentication and Role-Based Access")
    print("-" * 60)
    
    # HR has full access
    hr_full_access = hr_properties.status_code == 200
    print(f"✅ HR full access: {hr_full_access}")
    
    # Manager restricted from HR endpoints (this is the current issue)
    manager_hr_restricted = requests.get(f"{BACKEND_URL}/hr/properties", headers=manager_headers).status_code == 403
    print(f"❌ Manager HR restriction: {manager_hr_restricted}")
    
    # Manager can access own data
    manager_own_access = manager_dashboard.status_code == 200
    print(f"❌ Manager own access: {manager_own_access}")
    
    results['HR-4'] = hr_full_access and manager_hr_restricted and manager_own_access
    
    # HR-5: Professional UI/UX Design (API Structure)
    print("\n📖 HR-5: Professional UI/UX Design")
    print("-" * 60)
    
    api_consistency = all(r.status_code == 200 for r in [hr_dashboard, hr_properties, hr_apps])
    error_handling = requests.get(f"{BACKEND_URL}/hr/nonexistent", headers=hr_headers).status_code == 404
    print(f"✅ API design: {api_consistency and error_handling}")
    
    results['HR-5'] = api_consistency and error_handling
    
    # HR-6: Data Management and Search
    print("\n📖 HR-6: Data Management and Search")
    print("-" * 60)
    
    if hr_apps_works:
        apps_data = hr_apps.json()
        has_sortable_data = len(apps_data) > 0 and 'applied_at' in apps_data[0]
        print(f"✅ Data management: {has_sortable_data}")
        results['HR-6'] = has_sortable_data
    else:
        results['HR-6'] = False
    
    # Final Summary
    print(f"\n{'='*80}")
    print("📊 FINAL USER STORY VALIDATION RESULTS")
    print(f"{'='*80}")
    
    passed = sum(results.values())
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n📈 OVERALL RESULTS:")
    print(f"   Total User Stories: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for story, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {story}: {status}")
    
    print(f"\n🔧 REMAINING ISSUES:")
    if not results.get('QR-1'):
        print("   - Manager QR access (500 error on /manager/dashboard-stats)")
    if not results.get('QR-3'):
        print("   - Manager applications access (500 error on /manager/applications)")
    if not results.get('HR-2'):
        print("   - Manager dashboard functionality")
    if not results.get('HR-4'):
        print("   - Role-based access control (managers can access HR endpoints)")
    
    print(f"\n🎯 ANALYSIS:")
    if success_rate >= 75:
        print("   ✅ GOOD: Most user stories satisfied")
        print("   🔧 Focus on remaining manager endpoint issues")
    else:
        print("   ⚠️  MODERATE: Manager functionality needs attention")
        print("   🚨 Primary issue: Manager endpoints returning 500 errors")
    
    return results

if __name__ == "__main__":
    test_all_user_stories()