#!/usr/bin/env python3
"""
Complete Email Workflow Test - Final Version
Test the complete workflow: Create accounts → Login → Create application → Approve → Check emails
"""
import requests
import json
import time
from datetime import datetime, timedelta

BACKEND_URL = "http://localhost:8000"

def create_test_accounts():
    """Create test accounts using the secret endpoints"""
    print("🔧 Creating test accounts...")
    
    accounts_created = []
    
    # Create HR account
    try:
        response = requests.post(
            f"{BACKEND_URL}/secret/create-hr",
            params={
                "email": "hr@test.com",
                "password": "hr123",
                "secret_key": "hotel-admin-2025"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ HR account created")
            accounts_created.append(("hr@test.com", "hr123", "hr"))
        else:
            print(f"⚠️  HR account: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ HR account creation failed: {e}")
    
    # Create Manager account
    try:
        response = requests.post(
            f"{BACKEND_URL}/secret/create-manager",
            params={
                "email": "manager@test.com",
                "password": "manager123",
                "property_name": "Test Hotel",
                "secret_key": "hotel-admin-2025"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Manager account created")
            print(f"   Property ID: {result.get('property_id')}")
            accounts_created.append(("manager@test.com", "manager123", "manager"))
            return accounts_created, result.get('property_id')
        else:
            print(f"⚠️  Manager account: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Manager account creation failed: {e}")
    
    return accounts_created, None

def test_login_and_get_token(email, password):
    """Test login and return auth token"""
    print(f"🔐 Testing login: {email}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful!")
            return result.get('token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def create_application_for_property(property_id):
    """Create a test application for the property"""
    print(f"📝 Creating application for property: {property_id}")
    
    app_data = {
        "first_name": "Goutam",
        "last_name": "Vemula",
        "email": "goutamramv@gmail.com",
        "phone": "(555) 123-4567",
        "address": "123 Tech Street",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "shift_preference": "day",
        "employment_type": "full_time",
        "experience_years": "3",
        "hotel_experience": "yes",
        "previous_employer": "Tech Hotel Group",
        "reason_for_leaving": "Career advancement",
        "additional_comments": "Email integration test application"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/apply/{property_id}",
            json=app_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Application created successfully!")
            print(f"   Application ID: {result.get('application_id')}")
            return result.get('application_id')
        else:
            print(f"❌ Application creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Application creation error: {e}")
        return None

def get_pending_applications(auth_token):
    """Get pending applications for manager"""
    print("📋 Getting pending applications...")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BACKEND_URL}/manager/applications",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            applications = response.json()
            pending_apps = [app for app in applications if app.get('status') == 'pending']
            
            print(f"✅ Found {len(applications)} total applications")
            print(f"   Pending: {len(pending_apps)}")
            
            # Find our test application
            test_app = None
            for app in pending_apps:
                if app.get('applicant_data', {}).get('email') == 'goutamramv@gmail.com':
                    test_app = app
                    break
            
            if test_app:
                print(f"✅ Found test application: {test_app['id']}")
                return test_app
            else:
                print("❌ Test application not found")
                return None
                
        else:
            print(f"❌ Failed to get applications: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting applications: {e}")
        return None

def approve_application_and_check_emails(auth_token, application):
    """Approve application and check if emails are sent"""
    print(f"✅ Approving application: {application['id']}")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        approval_data = {
            "job_title": "Front Desk Agent",
            "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "start_time": "9:00 AM",
            "pay_rate": 19.50,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Test Manager",
            "special_instructions": "Email integration test - should send both approval and welcome emails"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/applications/{application['id']}/approve",
            headers=headers,
            data=approval_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 Application approved successfully!")
            
            # Check email results
            email_notifications = result.get('email_notifications', {})
            onboarding = result.get('onboarding', {})
            
            print(f"\n📧 Email Results:")
            print(f"   Approval Email: {'✅ SENT' if email_notifications.get('approval_email_sent') else '❌ FAILED'}")
            print(f"   Welcome Email: {'✅ SENT' if email_notifications.get('welcome_email_sent') else '❌ FAILED'}")
            print(f"   Recipient: {email_notifications.get('recipient', 'Unknown')}")
            
            print(f"\n🔗 Onboarding Details:")
            print(f"   URL: {onboarding.get('onboarding_url', 'Not provided')}")
            print(f"   Token: {onboarding.get('token', 'Not provided')}")
            
            return {
                'approval_sent': email_notifications.get('approval_email_sent', False),
                'welcome_sent': email_notifications.get('welcome_email_sent', False),
                'recipient': email_notifications.get('recipient'),
                'onboarding_url': onboarding.get('onboarding_url')
            }
            
        else:
            print(f"❌ Approval failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Approval error: {e}")
        return None

def main():
    """Run complete email workflow test"""
    print("🚀 COMPLETE EMAIL WORKFLOW TEST - FINAL VERSION")
    print("=" * 70)
    
    # Step 1: Create accounts
    accounts, property_id = create_test_accounts()
    
    if not accounts or not property_id:
        print("❌ Account creation failed")
        return False
    
    # Step 2: Find manager account
    manager_account = None
    for email, password, role in accounts:
        if role == "manager":
            manager_account = (email, password)
            break
    
    if not manager_account:
        print("❌ No manager account found")
        return False
    
    # Step 3: Login as manager
    auth_token = test_login_and_get_token(manager_account[0], manager_account[1])
    
    if not auth_token:
        print("❌ Manager login failed")
        return False
    
    # Step 4: Create application
    app_id = create_application_for_property(property_id)
    
    if not app_id:
        print("❌ Application creation failed")
        return False
    
    # Step 5: Get pending applications
    application = get_pending_applications(auth_token)
    
    if not application:
        print("❌ Could not find pending application")
        return False
    
    # Step 6: Approve application (should trigger emails)
    email_result = approve_application_and_check_emails(auth_token, application)
    
    if not email_result:
        print("❌ Application approval failed")
        return False
    
    # Final results
    print("\n" + "=" * 70)
    print("🎯 FINAL EMAIL WORKFLOW RESULTS")
    print("=" * 70)
    
    approval_sent = email_result.get('approval_sent', False)
    welcome_sent = email_result.get('welcome_sent', False)
    recipient = email_result.get('recipient')
    
    if approval_sent and welcome_sent:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ Manager account created and login working")
        print("✅ Application created and approved")
        print("✅ Both onboarding emails sent successfully")
        print(f"📧 Check {recipient} for:")
        print("   1. Job approval notification with offer details")
        print("   2. Onboarding welcome email with secure link")
        print(f"🔗 Onboarding URL: {email_result.get('onboarding_url')}")
        return True
    elif approval_sent or welcome_sent:
        print("⚠️  PARTIAL SUCCESS - Some emails sent")
        return False
    else:
        print("❌ EMAIL FAILURE - No emails sent")
        print("🔧 Check email service configuration")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)