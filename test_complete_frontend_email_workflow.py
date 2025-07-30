#!/usr/bin/env python3
"""
Complete Frontend Email Workflow Test
Test the complete workflow through frontend APIs:
1. Create job application with goutamramv@gmail.com
2. Login as manager (vgoutamram@gmail.com / Gouthi321@)
3. Approve application through frontend
4. Verify onboarding emails are sent
"""
import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# Test credentials
APPLICANT_EMAIL = "goutamramv@gmail.com"
MANAGER_EMAIL = "vgoutamram@gmail.com"
MANAGER_PASSWORD = "Gouthi321@"

def setup_test_data():
    """Set up test data including manager account and property"""
    print("🔧 Setting up test data...")
    
    try:
        # First, let's create the manager account and property in the backend
        # This simulates what would be done during system setup
        
        # Check if backend is running
        health_response = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
        if health_response.status_code != 200:
            print("❌ Backend not running")
            return False
        
        print("✅ Backend is running")
        
        # The backend should have test data initialization
        # Let's verify the property exists
        prop_response = requests.get(f"{BACKEND_URL}/properties/prop_test_001/info", timeout=10)
        
        if prop_response.status_code == 200:
            print("✅ Test property exists")
            prop_data = prop_response.json()
            print(f"   Property: {prop_data.get('property', {}).get('name', 'Unknown')}")
        else:
            print("⚠️  Test property not found - will create application anyway")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def create_job_application():
    """Create a job application with goutamramv@gmail.com"""
    print("\n📝 Creating job application...")
    
    try:
        # Application data with correct types
        app_data = {
            "first_name": "Goutam",
            "last_name": "Vemula", 
            "email": APPLICANT_EMAIL,
            "phone": "(555) 123-4567",
            "address": "123 Tech Street",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94105",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",  # String instead of boolean
            "sponsorship_required": "no",  # String instead of boolean
            "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),  # Future date
            "shift_preference": "day",
            "employment_type": "full_time",
            "experience_years": "3",  # String instead of number
            "hotel_experience": "yes",  # String instead of boolean
            "previous_employer": "Tech Hotel Group",
            "reason_for_leaving": "Career advancement opportunity",
            "additional_comments": "Excited to join the team and contribute to excellent guest service!"
        }
        
        # Submit application
        app_response = requests.post(
            f"{BACKEND_URL}/apply/prop_test_001", 
            json=app_data, 
            timeout=15
        )
        
        if app_response.status_code == 200:
            result = app_response.json()
            print("✅ Job application created successfully!")
            print(f"   Application ID: {result.get('application_id')}")
            print(f"   Applicant: {app_data['first_name']} {app_data['last_name']}")
            print(f"   Email: {app_data['email']}")
            print(f"   Position: {app_data['position']} - {app_data['department']}")
            return result.get('application_id')
        else:
            print(f"❌ Application creation failed: {app_response.status_code}")
            print(f"   Error: {app_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Application creation error: {e}")
        return None

def login_as_manager():
    """Login as manager using frontend API"""
    print(f"\n🔐 Logging in as manager ({MANAGER_EMAIL})...")
    
    try:
        login_data = {
            "email": MANAGER_EMAIL,
            "password": MANAGER_PASSWORD
        }
        
        login_response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code == 200:
            result = login_response.json()
            print("✅ Manager login successful!")
            print(f"   Manager: {result.get('user', {}).get('first_name', 'Unknown')} {result.get('user', {}).get('last_name', '')}")
            print(f"   Role: {result.get('user', {}).get('role', 'Unknown')}")
            return result.get('token')
        else:
            print(f"❌ Manager login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            
            # If login fails, let's try to create the manager account
            print("\n🔧 Attempting to create manager account...")
            return create_manager_account()
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def create_manager_account():
    """Create manager account if it doesn't exist"""
    print("🔧 Creating manager account...")
    
    # This would typically be done through an admin interface
    # For testing, we'll try to create the account directly
    
    # Note: This is a simplified approach for testing
    # In production, accounts would be created through proper admin workflows
    
    print("⚠️  Manager account creation not implemented in this test")
    print("   Please ensure manager account exists in Supabase:")
    print(f"   Email: {MANAGER_EMAIL}")
    print(f"   Password: {MANAGER_PASSWORD}")
    print("   Role: manager")
    
    return None

def get_pending_applications(auth_token):
    """Get pending applications for manager review"""
    print("\n📋 Getting pending applications...")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        apps_response = requests.get(
            f"{BACKEND_URL}/manager/applications",
            headers=headers,
            timeout=10
        )
        
        if apps_response.status_code == 200:
            applications = apps_response.json()
            pending_apps = [app for app in applications if app.get('status') == 'pending']
            
            print(f"✅ Found {len(applications)} total applications")
            print(f"   Pending applications: {len(pending_apps)}")
            
            # Find our test application
            test_app = None
            for app in pending_apps:
                if app.get('applicant_data', {}).get('email') == APPLICANT_EMAIL:
                    test_app = app
                    break
            
            if test_app:
                print(f"✅ Found test application: {test_app['id']}")
                print(f"   Applicant: {test_app['applicant_data']['first_name']} {test_app['applicant_data']['last_name']}")
                print(f"   Position: {test_app['position']}")
                return test_app
            else:
                print("❌ Test application not found in pending applications")
                return None
                
        else:
            print(f"❌ Failed to get applications: {apps_response.status_code}")
            print(f"   Error: {apps_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting applications: {e}")
        return None

def approve_application(auth_token, application):
    """Approve application through frontend API (this should trigger emails)"""
    print(f"\n✅ Approving application {application['id']}...")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Approval data (simulating frontend form submission)
        approval_data = {
            "job_title": "Front Desk Agent",
            "start_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "start_time": "9:00 AM",
            "pay_rate": 19.50,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Mike Wilson",
            "special_instructions": "Welcome to the team! Please arrive 30 minutes early on your first day for orientation."
        }
        
        print("   Submitting approval with job details:")
        print(f"   • Position: {approval_data['job_title']}")
        print(f"   • Start Date: {approval_data['start_date']}")
        print(f"   • Pay Rate: ${approval_data['pay_rate']}/hour")
        print(f"   • Supervisor: {approval_data['supervisor']}")
        
        # Submit approval (this should trigger email sending)
        approval_response = requests.post(
            f"{BACKEND_URL}/applications/{application['id']}/approve",
            headers=headers,
            data=approval_data,  # Using form data as expected by backend
            timeout=30  # Longer timeout for email sending
        )
        
        if approval_response.status_code == 200:
            result = approval_response.json()
            print("🎉 Application approved successfully!")
            
            # Check email results
            email_notifications = result.get('email_notifications', {})
            onboarding = result.get('onboarding', {})
            employee_info = result.get('employee_info', {})
            
            print(f"\n📧 Email Notification Results:")
            print(f"   Approval Email: {'✅ SENT' if email_notifications.get('approval_email_sent') else '❌ FAILED'}")
            print(f"   Welcome Email: {'✅ SENT' if email_notifications.get('welcome_email_sent') else '❌ FAILED'}")
            print(f"   Recipient: {email_notifications.get('recipient', 'Unknown')}")
            
            print(f"\n👤 Employee Information:")
            print(f"   Name: {employee_info.get('name', 'Unknown')}")
            print(f"   Email: {employee_info.get('email', 'Unknown')}")
            print(f"   Position: {employee_info.get('position', 'Unknown')}")
            
            print(f"\n🔗 Onboarding Details:")
            print(f"   URL: {onboarding.get('onboarding_url', 'Not provided')}")
            print(f"   Token: {onboarding.get('token', 'Not provided')}")
            print(f"   Expires: {onboarding.get('expires_at', 'Not provided')}")
            
            return {
                'approval_email_sent': email_notifications.get('approval_email_sent', False),
                'welcome_email_sent': email_notifications.get('welcome_email_sent', False),
                'recipient': email_notifications.get('recipient'),
                'onboarding_url': onboarding.get('onboarding_url'),
                'employee_info': employee_info
            }
            
        else:
            print(f"❌ Approval failed: {approval_response.status_code}")
            print(f"   Error: {approval_response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Approval error: {e}")
        return None

def verify_email_integration(approval_result):
    """Verify that email integration worked correctly"""
    print(f"\n📧 Verifying Email Integration...")
    
    if not approval_result:
        print("❌ No approval result to verify")
        return False
    
    approval_sent = approval_result.get('approval_email_sent', False)
    welcome_sent = approval_result.get('welcome_email_sent', False)
    recipient = approval_result.get('recipient')
    onboarding_url = approval_result.get('onboarding_url')
    
    print(f"📊 Email Integration Results:")
    print(f"   Approval Email: {'✅' if approval_sent else '❌'}")
    print(f"   Welcome Email: {'✅' if welcome_sent else '❌'}")
    print(f"   Recipient: {recipient}")
    print(f"   Onboarding URL Generated: {'✅' if onboarding_url else '❌'}")
    
    if approval_sent and welcome_sent:
        print(f"\n🎉 SUCCESS: Both emails sent successfully!")
        print(f"📧 Check {recipient} for:")
        print(f"   1. Job approval notification with offer details")
        print(f"   2. Onboarding welcome email with secure link")
        print(f"   3. Onboarding URL: {onboarding_url}")
        return True
    elif approval_sent or welcome_sent:
        print(f"\n⚠️  PARTIAL SUCCESS: Some emails sent")
        return False
    else:
        print(f"\n❌ FAILURE: No emails were sent")
        print(f"🔧 Check email service configuration and backend logs")
        return False

def main():
    """Run complete frontend email workflow test"""
    print("🚀 COMPLETE FRONTEND EMAIL WORKFLOW TEST")
    print("=" * 70)
    print(f"Applicant Email: {APPLICANT_EMAIL}")
    print(f"Manager Email: {MANAGER_EMAIL}")
    print("=" * 70)
    
    # Step 1: Setup
    if not setup_test_data():
        print("❌ Setup failed")
        return False
    
    # Step 2: Create job application
    application_id = create_job_application()
    if not application_id:
        print("❌ Application creation failed")
        return False
    
    # Step 3: Login as manager
    auth_token = login_as_manager()
    if not auth_token:
        print("❌ Manager login failed")
        return False
    
    # Step 4: Get pending applications
    application = get_pending_applications(auth_token)
    if not application:
        print("❌ Could not find pending application")
        return False
    
    # Step 5: Approve application (should trigger emails)
    approval_result = approve_application(auth_token, application)
    if not approval_result:
        print("❌ Application approval failed")
        return False
    
    # Step 6: Verify email integration
    email_success = verify_email_integration(approval_result)
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎯 FINAL WORKFLOW RESULTS")
    print("=" * 70)
    
    if email_success:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ Job application created")
        print("✅ Manager login successful")
        print("✅ Application approved through frontend")
        print("✅ Onboarding emails sent successfully")
        print(f"📧 Check {APPLICANT_EMAIL} for onboarding emails")
    else:
        print("❌ WORKFLOW INCOMPLETE")
        print("🔧 Email integration needs attention")
    
    return email_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)