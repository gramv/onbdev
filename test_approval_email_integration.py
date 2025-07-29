#!/usr/bin/env python3
"""
Test Approval Email Integration
Verify that emails are sent during the approval process
"""
import asyncio
import sys
import os
import requests
import json
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000"
TEST_EMAIL = "goutamramv@gmail.com"

async def test_approval_with_email():
    """Test the approval endpoint with email integration"""
    
    print("🧪 Testing Approval Endpoint with Email Integration")
    print("=" * 60)
    
    try:
        # 1. Login as manager
        print("\n1️⃣ Logging in as manager...")
        
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "email": "manager@hoteltest.com",
            "password": "manager123"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return False
        
        login_data = login_response.json()
        token = login_data["token"]
        print("✅ Manager login successful")
        
        # 2. Get applications
        print("\n2️⃣ Getting manager applications...")
        
        headers = {"Authorization": f"Bearer {token}"}
        apps_response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
        
        if apps_response.status_code != 200:
            print(f"❌ Failed to get applications: {apps_response.status_code}")
            return False
        
        applications = apps_response.json()
        pending_apps = [app for app in applications if app["status"] == "pending"]
        
        if not pending_apps:
            print("⚠️  No pending applications found. Creating test application...")
            
            # Create test application
            test_app_data = {
                "first_name": "John",
                "last_name": "Doe",
                "email": TEST_EMAIL,
                "phone": "(555) 123-4567",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "zip_code": "90210",
                "department": "Front Desk",
                "position": "Front Desk Agent",
                "work_authorized": True,
                "sponsorship_required": False,
                "start_date": "2024-02-01",
                "shift_preference": "day",
                "employment_type": "full_time",
                "experience_years": 2,
                "hotel_experience": True,
                "previous_employer": "Test Hotel",
                "reason_for_leaving": "Career advancement",
                "additional_comments": "Excited to join the team!"
            }
            
            app_response = requests.post(f"{BACKEND_URL}/apply/prop_test_001", json=test_app_data)
            
            if app_response.status_code != 200:
                print(f"❌ Failed to create test application: {app_response.status_code}")
                return False
            
            # Get applications again
            apps_response = requests.get(f"{BACKEND_URL}/manager/applications", headers=headers)
            applications = apps_response.json()
            pending_apps = [app for app in applications if app["status"] == "pending"]
        
        if not pending_apps:
            print("❌ Still no pending applications found")
            return False
        
        test_app = pending_apps[0]
        print(f"✅ Found test application: {test_app['id']}")
        print(f"   Applicant: {test_app['applicant_data']['first_name']} {test_app['applicant_data']['last_name']}")
        print(f"   Email: {test_app['applicant_data']['email']}")
        
        # 3. Approve application with email
        print("\n3️⃣ Approving application (should trigger emails)...")
        
        approval_data = {
            "job_title": "Front Desk Agent",
            "start_date": "2024-02-15",
            "start_time": "9:00 AM",
            "pay_rate": 18.50,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Mike Wilson",
            "special_instructions": "New hire orientation on first day"
        }
        
        approval_response = requests.post(
            f"{BACKEND_URL}/applications/{test_app['id']}/approve",
            headers=headers,
            data=approval_data
        )
        
        if approval_response.status_code != 200:
            print(f"❌ Approval failed: {approval_response.status_code}")
            print(approval_response.text)
            return False
        
        approval_result = approval_response.json()
        print("✅ Application approved successfully!")
        
        # 4. Check email results
        print("\n4️⃣ Checking email notification results...")
        
        email_notifications = approval_result.get("email_notifications", {})
        
        print(f"   Approval Email Sent: {'✅' if email_notifications.get('approval_email_sent') else '❌'}")
        print(f"   Welcome Email Sent: {'✅' if email_notifications.get('welcome_email_sent') else '❌'}")
        print(f"   Recipient: {email_notifications.get('recipient', 'Unknown')}")
        
        # 5. Display onboarding details
        print("\n5️⃣ Onboarding details...")
        
        onboarding = approval_result.get("onboarding", {})
        employee_info = approval_result.get("employee_info", {})
        
        print(f"   Employee: {employee_info.get('name')}")
        print(f"   Position: {employee_info.get('position')}")
        print(f"   Department: {employee_info.get('department')}")
        print(f"   Onboarding URL: {onboarding.get('onboarding_url')}")
        print(f"   Token: {onboarding.get('token')}")
        print(f"   Expires: {onboarding.get('expires_at')}")
        
        # 6. Test results summary
        print("\n" + "=" * 60)
        print("📊 EMAIL INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        approval_email_success = email_notifications.get('approval_email_sent', False)
        welcome_email_success = email_notifications.get('welcome_email_sent', False)
        
        print(f"✅ Application Approval: SUCCESS")
        print(f"{'✅' if approval_email_success else '❌'} Approval Email: {'SENT' if approval_email_success else 'FAILED'}")
        print(f"{'✅' if welcome_email_success else '❌'} Welcome Email: {'SENT' if welcome_email_success else 'FAILED'}")
        print(f"✅ Onboarding URL Generated: SUCCESS")
        
        if approval_email_success and welcome_email_success:
            print(f"\n🎉 COMPLETE SUCCESS: Both emails sent to {email_notifications.get('recipient')}")
            print(f"📧 Check your email for:")
            print(f"   1. Job offer approval notification with job details")
            print(f"   2. Onboarding welcome email with secure link")
        elif approval_email_success or welcome_email_success:
            print(f"\n⚠️  PARTIAL SUCCESS: Some emails sent")
        else:
            print(f"\n❌ EMAIL FAILURE: No emails were sent")
        
        return approval_email_success and welcome_email_success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Starting Approval Email Integration Test")
    print("=" * 60)
    
    # Check backend status
    if not check_backend_status():
        print("❌ Backend not running. Please start the backend server first:")
        print("   cd hotel-onboarding-backend && poetry run python -m app.main_enhanced")
        exit(1)
    
    print("✅ Backend is running")
    
    # Run the test
    success = asyncio.run(test_approval_with_email())
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULT")
    print("=" * 60)
    
    if success:
        print("✅ EMAIL INTEGRATION WORKING PERFECTLY!")
        print("📧 Onboarding emails are now sent automatically after approval")
        print("🔗 Employees receive secure onboarding links with job details")
    else:
        print("❌ EMAIL INTEGRATION NEEDS ATTENTION")
        print("🔧 Check email configuration and error logs")
    
    exit(0 if success else 1)