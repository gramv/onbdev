#!/usr/bin/env python3
"""
Direct test of email functionality without backend restart
"""
import requests
import json

def test_email_functionality():
    """Test email functionality directly"""
    
    print("📧 Testing Email Functionality")
    print("=" * 50)
    
    try:
        # Test health endpoint first
        print("1️⃣ Testing backend health...")
        health_response = requests.get("http://localhost:8000/healthz", timeout=5)
        print(f"   Health status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
        
        # Try to login
        print("\n2️⃣ Testing login...")
        login_response = requests.post("http://localhost:8000/auth/login", json={
            "email": "manager@hoteltest.com",
            "password": "manager123"
        }, timeout=10)
        
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   Login error: {login_response.text}")
            return False
        
        token = login_response.json()["token"]
        print("   ✅ Login successful")
        
        # Create a test application
        print("\n3️⃣ Creating test application...")
        test_app_data = {
            "first_name": "Email",
            "last_name": "Test",
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
            "additional_comments": "Email test application"
        }
        
        app_response = requests.post("http://localhost:8000/apply/prop_test_001", json=test_app_data, timeout=10)
        
        if app_response.status_code != 200:
            print(f"   Application creation failed: {app_response.status_code}")
            print(f"   Error: {app_response.text}")
            return False
        
        print("   ✅ Test application created")
        
        # Get applications
        print("\n4️⃣ Getting applications...")
        headers = {"Authorization": f"Bearer {token}"}
        apps_response = requests.get("http://localhost:8000/manager/applications", headers=headers, timeout=10)
        
        if apps_response.status_code != 200:
            print(f"   Failed to get applications: {apps_response.status_code}")
            return False
        
        applications = apps_response.json()
        test_app = None
        
        for app in applications:
            if (app.get("applicant_data", {}).get("email") == "goutamramv@gmail.com" and 
                app.get("status") == "pending"):
                test_app = app
                break
        
        if not test_app:
            print("   ❌ Test application not found")
            return False
        
        print(f"   ✅ Found test application: {test_app['id']}")
        
        # Approve application (this should trigger emails)
        print("\n5️⃣ Approving application (should send emails)...")
        
        approval_data = {
            "job_title": "Front Desk Agent",
            "start_date": "2024-02-15",
            "start_time": "9:00 AM",
            "pay_rate": 18.50,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Mike Wilson",
            "special_instructions": "Email integration test"
        }
        
        approval_response = requests.post(
            f"http://localhost:8000/applications/{test_app['id']}/approve",
            headers=headers,
            data=approval_data,
            timeout=30  # Longer timeout for email sending
        )
        
        print(f"   Approval status: {approval_response.status_code}")
        
        if approval_response.status_code != 200:
            print(f"   Approval failed: {approval_response.text}")
            return False
        
        result = approval_response.json()
        print("   ✅ Application approved!")
        
        # Check email results
        print("\n6️⃣ Checking email results...")
        
        email_notifications = result.get("email_notifications", {})
        
        print(f"   Email notifications object: {email_notifications}")
        
        approval_sent = email_notifications.get('approval_email_sent', False)
        welcome_sent = email_notifications.get('welcome_email_sent', False)
        recipient = email_notifications.get('recipient', 'Unknown')
        
        print(f"   Approval Email: {'✅ SENT' if approval_sent else '❌ FAILED'}")
        print(f"   Welcome Email: {'✅ SENT' if welcome_sent else '❌ FAILED'}")
        print(f"   Recipient: {recipient}")
        
        # Show onboarding details
        onboarding = result.get("onboarding", {})
        print(f"\n🔗 Onboarding Details:")
        print(f"   URL: {onboarding.get('onboarding_url')}")
        print(f"   Token: {onboarding.get('token')}")
        print(f"   Expires: {onboarding.get('expires_at')}")
        
        # Final result
        print(f"\n" + "=" * 50)
        print("📊 EMAIL TEST RESULTS")
        print("=" * 50)
        
        if approval_sent and welcome_sent:
            print("🎉 SUCCESS: Both emails sent!")
            print(f"📧 Check {recipient} for:")
            print("   1. Job approval notification")
            print("   2. Onboarding welcome email")
            return True
        elif approval_sent or welcome_sent:
            print("⚠️  PARTIAL: Some emails sent")
            return False
        else:
            print("❌ FAILED: No emails sent")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_functionality()
    
    print(f"\n🎯 RESULT: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    
    if success:
        print("✅ Email integration is working!")
        print("📧 Onboarding emails are sent after approval")
    else:
        print("❌ Email integration needs debugging")
        print("🔧 Check backend logs and email configuration")
    
    exit(0 if success else 1)