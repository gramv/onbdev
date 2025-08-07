#!/usr/bin/env python3
"""
Test backend startup and email integration
"""
import sys
import os
import asyncio
import uvicorn
from threading import Thread
import time
import requests

# Add the backend to Python path
sys.path.insert(0, 'hotel-onboarding-backend')

def start_backend():
    """Start the backend server"""
    try:
        os.chdir('hotel-onboarding-backend')
        uvicorn.run("app.main_enhanced:app", host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"Backend startup error: {e}")

def test_email_integration():
    """Test the email integration after backend starts"""
    
    print("🧪 Testing Email Integration After Backend Startup")
    print("=" * 60)
    
    # Wait for backend to start
    print("⏳ Waiting for backend to start...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/healthz", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                break
        except:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Still waiting... ({i+1}/30)")
    else:
        print("❌ Backend failed to start within 30 seconds")
        return False
    
    try:
        # Login as manager
        print("\n1️⃣ Logging in as manager...")
        login_response = requests.post("http://localhost:8000/auth/login", json={
            "email": "manager@hoteltest.com",
            "password": "manager123"
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return False
        
        token = login_response.json()["token"]
        print("✅ Manager login successful")
        
        # Create test application
        print("\n2️⃣ Creating test application...")
        test_app_data = {
            "first_name": "Email",
            "last_name": "Integration",
            "email": "goutamramv@gmail.com",
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
            "additional_comments": "Email integration test"
        }
        
        app_response = requests.post("http://localhost:8000/apply/prop_test_001", json=test_app_data)
        
        if app_response.status_code != 200:
            print(f"❌ Failed to create application: {app_response.status_code}")
            print(app_response.text)
            return False
        
        app_result = app_response.json()
        print(f"✅ Test application created: {app_result['application_id']}")
        
        # Get the application
        headers = {"Authorization": f"Bearer {token}"}
        apps_response = requests.get("http://localhost:8000/manager/applications", headers=headers)
        
        if apps_response.status_code != 200:
            print(f"❌ Failed to get applications: {apps_response.status_code}")
            return False
        
        applications = apps_response.json()
        test_app = None
        for app in applications:
            if app["applicant_data"]["email"] == "goutamramv@gmail.com" and app["status"] == "pending":
                test_app = app
                break
        
        if not test_app:
            print("❌ Test application not found")
            return False
        
        print(f"✅ Found test application: {test_app['id']}")
        
        # Approve with email integration
        print("\n3️⃣ Approving application (should send emails)...")
        
        approval_data = {
            "job_title": "Front Desk Agent",
            "start_date": "2024-02-15",
            "start_time": "9:00 AM",
            "pay_rate": 18.50,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Mike Wilson",
            "special_instructions": "Email integration test - should send both approval and welcome emails"
        }
        
        approval_response = requests.post(
            f"http://localhost:8000/applications/{test_app['id']}/approve",
            headers=headers,
            data=approval_data
        )
        
        if approval_response.status_code != 200:
            print(f"❌ Approval failed: {approval_response.status_code}")
            print(approval_response.text)
            return False
        
        result = approval_response.json()
        print("✅ Application approved successfully!")
        
        # Check email results
        print("\n4️⃣ Checking email integration results...")
        
        email_notifications = result.get("email_notifications", {})
        onboarding = result.get("onboarding", {})
        
        print(f"📧 Email Results:")
        print(f"   Approval Email Sent: {'✅' if email_notifications.get('approval_email_sent') else '❌'}")
        print(f"   Welcome Email Sent: {'✅' if email_notifications.get('welcome_email_sent') else '❌'}")
        print(f"   Recipient: {email_notifications.get('recipient', 'Unknown')}")
        
        print(f"\n🔗 Onboarding Details:")
        print(f"   URL: {onboarding.get('onboarding_url')}")
        print(f"   Token: {onboarding.get('token')}")
        print(f"   Expires: {onboarding.get('expires_at')}")
        
        # Final results
        approval_sent = email_notifications.get('approval_email_sent', False)
        welcome_sent = email_notifications.get('welcome_email_sent', False)
        
        print(f"\n" + "=" * 60)
        print("📊 FINAL EMAIL INTEGRATION RESULTS")
        print("=" * 60)
        
        if approval_sent and welcome_sent:
            print("🎉 SUCCESS: Both emails sent successfully!")
            print("📧 Check goutamramv@gmail.com for:")
            print("   1. Job approval notification with offer details")
            print("   2. Onboarding welcome email with secure link")
            return True
        elif approval_sent or welcome_sent:
            print("⚠️  PARTIAL SUCCESS: Some emails sent")
            return False
        else:
            print("❌ FAILURE: No emails were sent")
            print("🔧 Check email service configuration")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Backend and Testing Email Integration")
    print("=" * 60)
    
    # Start backend in background thread
    backend_thread = Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Test email integration
    success = test_email_integration()
    
    print(f"\n🎯 FINAL RESULT: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    
    if success:
        print("✅ Onboarding emails are working perfectly!")
        print("📧 Employees will receive job details and secure onboarding links")
    else:
        print("❌ Email integration needs debugging")
    
    # Keep the server running for a bit to see results
    print("\n⏳ Keeping server running for 10 seconds...")
    time.sleep(10)
    
    exit(0 if success else 1)