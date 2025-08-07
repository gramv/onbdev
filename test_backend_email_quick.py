#!/usr/bin/env python3
"""
Quick test to check if backend has email integration
"""
import requests
import json

def test_backend_email_integration():
    """Quick test of backend email integration"""
    
    print("🔍 Testing Backend Email Integration")
    print("=" * 50)
    
    try:
        # Check health
        health_response = requests.get("http://localhost:8000/healthz", timeout=5)
        if health_response.status_code != 200:
            print("❌ Backend not responding")
            return False
        
        print("✅ Backend is running")
        
        # Login as manager
        login_response = requests.post("http://localhost:8000/auth/login", json={
            "email": "manager@hoteltest.com",
            "password": "manager123"
        })
        
        if login_response.status_code != 200:
            print("❌ Login failed")
            return False
        
        token = login_response.json()["token"]
        print("✅ Manager login successful")
        
        # Get applications
        headers = {"Authorization": f"Bearer {token}"}
        apps_response = requests.get("http://localhost:8000/manager/applications", headers=headers)
        
        if apps_response.status_code != 200:
            print("❌ Failed to get applications")
            return False
        
        applications = apps_response.json()
        pending_apps = [app for app in applications if app["status"] == "pending"]
        
        if not pending_apps:
            print("⚠️  No pending applications - creating test application")
            
            # Create test application
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
                "additional_comments": "Email integration test"
            }
            
            app_response = requests.post("http://localhost:8000/apply/prop_test_001", json=test_app_data)
            
            if app_response.status_code != 200:
                print(f"❌ Failed to create test application: {app_response.status_code}")
                print(app_response.text)
                return False
            
            print("✅ Test application created")
            
            # Get applications again
            apps_response = requests.get("http://localhost:8000/manager/applications", headers=headers)
            applications = apps_response.json()
            pending_apps = [app for app in applications if app["status"] == "pending"]
        
        if not pending_apps:
            print("❌ Still no pending applications")
            return False
        
        test_app = pending_apps[0]
        print(f"✅ Found application to approve: {test_app['id']}")
        
        # Approve with email
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
            data=approval_data
        )
        
        if approval_response.status_code != 200:
            print(f"❌ Approval failed: {approval_response.status_code}")
            print(approval_response.text)
            return False
        
        result = approval_response.json()
        print("✅ Application approved!")
        
        # Check email results
        email_notifications = result.get("email_notifications", {})
        
        print(f"\n📧 Email Results:")
        print(f"   Approval Email: {'✅' if email_notifications.get('approval_email_sent') else '❌'}")
        print(f"   Welcome Email: {'✅' if email_notifications.get('welcome_email_sent') else '❌'}")
        print(f"   Recipient: {email_notifications.get('recipient', 'Unknown')}")
        
        # Show onboarding details
        onboarding = result.get("onboarding", {})
        print(f"\n🔗 Onboarding:")
        print(f"   URL: {onboarding.get('onboarding_url')}")
        print(f"   Token: {onboarding.get('token')}")
        
        return email_notifications.get('approval_email_sent', False) and email_notifications.get('welcome_email_sent', False)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_backend_email_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 EMAIL INTEGRATION WORKING!")
    else:
        print("❌ EMAIL INTEGRATION NEEDS FIXING")
    
    exit(0 if success else 1)