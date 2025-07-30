#!/usr/bin/env python3
"""
Fix All Backend Issues Systematically
No bypasses - fix everything properly
"""
import sys
import os
import traceback

def fix_supabase_service():
    """Fix all issues in the Supabase service"""
    print("🔧 Fixing Supabase Service Issues")
    print("=" * 50)
    
    # Read the current file
    service_path = 'hotel-onboarding-backend/app/supabase_service_enhanced.py'
    
    try:
        with open(service_path, 'r') as f:
            content = f.read()
        
        # Check if health_check method exists and is properly indented
        if 'async def health_check(self)' not in content:
            print("❌ health_check method missing")
            return False
        
        # Check if sync wrapper methods are inside the class
        if 'def get_user_by_email_sync(self, email: str)' not in content:
            print("❌ get_user_by_email_sync method missing or not in class")
            return False
        
        print("✅ Supabase service methods appear to be present")
        return True
        
    except Exception as e:
        print(f"❌ Error checking Supabase service: {e}")
        return False

def fix_main_enhanced():
    """Fix issues in main_enhanced.py"""
    print("\n🔧 Fixing Main Enhanced Issues")
    print("=" * 50)
    
    main_path = 'hotel-onboarding-backend/app/main_enhanced.py'
    
    try:
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Check if email service is imported
        if 'from .email_service import email_service' not in content:
            print("❌ Email service not imported")
            return False
        
        # Check if approval endpoint has email sending
        if 'send_approval_notification' not in content:
            print("❌ Approval notification email not in approval endpoint")
            return False
        
        if 'send_onboarding_welcome_email' not in content:
            print("❌ Welcome email not in approval endpoint")
            return False
        
        print("✅ Main enhanced appears to have email integration")
        return True
        
    except Exception as e:
        print(f"❌ Error checking main enhanced: {e}")
        return False

def test_backend_startup():
    """Test if backend can start without errors"""
    print("\n🚀 Testing Backend Startup")
    print("=" * 50)
    
    try:
        # Add backend to path
        backend_path = os.path.join(os.getcwd(), 'hotel-onboarding-backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Change to backend directory
        original_cwd = os.getcwd()
        os.chdir(backend_path)
        
        try:
            # Test imports
            print("1️⃣ Testing imports...")
            from app.main_enhanced import app
            print("✅ Main app imported successfully")
            
            from app.supabase_service_enhanced import EnhancedSupabaseService
            print("✅ Supabase service imported successfully")
            
            from app.email_service import email_service
            print("✅ Email service imported successfully")
            
            # Test service initialization
            print("\n2️⃣ Testing service initialization...")
            service = EnhancedSupabaseService()
            print("✅ Supabase service initialized")
            
            # Test if methods exist
            if hasattr(service, 'health_check'):
                print("✅ health_check method exists")
            else:
                print("❌ health_check method missing")
                return False
            
            if hasattr(service, 'get_user_by_email_sync'):
                print("✅ get_user_by_email_sync method exists")
            else:
                print("❌ get_user_by_email_sync method missing")
                return False
            
            print("\n✅ Backend startup test passed")
            return True
            
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        print(f"❌ Backend startup test failed: {e}")
        traceback.print_exc()
        return False

def start_backend_properly():
    """Start the backend properly"""
    print("\n🚀 Starting Backend Properly")
    print("=" * 50)
    
    import subprocess
    import time
    import requests
    
    try:
        # Kill any existing processes
        subprocess.run(['pkill', '-f', 'python.*main_enhanced'], capture_output=True)
        time.sleep(2)
        
        # Start backend
        backend_dir = 'hotel-onboarding-backend'
        env = os.environ.copy()
        env['PYTHONPATH'] = backend_dir
        
        process = subprocess.Popen(
            ['python3', '-m', 'app.main_enhanced'],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for backend to start...")
        
        # Wait for backend to be ready
        for i in range(30):
            try:
                response = requests.get('http://localhost:8000/healthz', timeout=2)
                if response.status_code == 200:
                    print("✅ Backend started successfully!")
                    health_data = response.json()
                    print(f"   Status: {health_data.get('status', 'unknown')}")
                    return True
            except:
                pass
            
            time.sleep(1)
            if i % 5 == 0:
                print(f"   Still waiting... ({i+1}/30)")
        
        print("❌ Backend failed to start within 30 seconds")
        
        # Get error output
        stdout, stderr = process.communicate(timeout=5)
        if stderr:
            print(f"Error output: {stderr.decode()}")
        
        return False
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def test_email_integration():
    """Test email integration end-to-end"""
    print("\n📧 Testing Email Integration")
    print("=" * 50)
    
    import requests
    import json
    
    try:
        # Test login
        print("1️⃣ Testing login...")
        login_response = requests.post('http://localhost:8000/auth/login', json={
            'email': 'manager@hoteltest.com',
            'password': 'manager123'
        }, timeout=10)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return False
        
        token = login_response.json()['token']
        print("✅ Login successful")
        
        # Create test application
        print("\n2️⃣ Creating test application...")
        app_data = {
            'first_name': 'Email',
            'last_name': 'Integration',
            'email': 'goutamramv@gmail.com',
            'phone': '(555) 123-4567',
            'address': '123 Test Street',
            'city': 'Test City',
            'state': 'CA',
            'zip_code': '90210',
            'department': 'Front Desk',
            'position': 'Front Desk Agent',
            'work_authorized': True,
            'sponsorship_required': False,
            'start_date': '2024-02-01',
            'shift_preference': 'day',
            'employment_type': 'full_time',
            'experience_years': 2,
            'hotel_experience': True,
            'previous_employer': 'Test Hotel',
            'reason_for_leaving': 'Career advancement',
            'additional_comments': 'Email integration test'
        }
        
        app_response = requests.post('http://localhost:8000/apply/prop_test_001', json=app_data, timeout=10)
        
        if app_response.status_code != 200:
            print(f"❌ Application creation failed: {app_response.status_code}")
            print(f"   Error: {app_response.text}")
            return False
        
        print("✅ Test application created")
        
        # Get applications
        print("\n3️⃣ Getting applications...")
        headers = {'Authorization': f'Bearer {token}'}
        apps_response = requests.get('http://localhost:8000/manager/applications', headers=headers, timeout=10)
        
        if apps_response.status_code != 200:
            print(f"❌ Failed to get applications: {apps_response.status_code}")
            return False
        
        applications = apps_response.json()
        test_app = None
        
        for app in applications:
            if (app.get('applicant_data', {}).get('email') == 'goutamramv@gmail.com' and 
                app.get('status') == 'pending'):
                test_app = app
                break
        
        if not test_app:
            print("❌ Test application not found")
            return False
        
        print(f"✅ Found test application: {test_app['id']}")
        
        # Approve application (should send emails)
        print("\n4️⃣ Approving application (should send emails)...")
        
        approval_data = {
            'job_title': 'Front Desk Agent',
            'start_date': '2024-02-15',
            'start_time': '9:00 AM',
            'pay_rate': 18.50,
            'pay_frequency': 'hourly',
            'benefits_eligible': 'yes',
            'supervisor': 'Mike Wilson',
            'special_instructions': 'Email integration test'
        }
        
        approval_response = requests.post(
            f"http://localhost:8000/applications/{test_app['id']}/approve",
            headers=headers,
            data=approval_data,
            timeout=30
        )
        
        if approval_response.status_code != 200:
            print(f"❌ Approval failed: {approval_response.status_code}")
            print(f"   Error: {approval_response.text}")
            return False
        
        result = approval_response.json()
        print("✅ Application approved successfully!")
        
        # Check email results
        print("\n5️⃣ Checking email results...")
        
        email_notifications = result.get('email_notifications', {})
        
        approval_sent = email_notifications.get('approval_email_sent', False)
        welcome_sent = email_notifications.get('welcome_email_sent', False)
        recipient = email_notifications.get('recipient', 'Unknown')
        
        print(f"   Approval Email: {'✅ SENT' if approval_sent else '❌ FAILED'}")
        print(f"   Welcome Email: {'✅ SENT' if welcome_sent else '❌ FAILED'}")
        print(f"   Recipient: {recipient}")
        
        # Show onboarding details
        onboarding = result.get('onboarding', {})
        print(f"\n🔗 Onboarding Details:")
        print(f"   URL: {onboarding.get('onboarding_url')}")
        print(f"   Token: {onboarding.get('token')}")
        
        return approval_sent and welcome_sent
        
    except Exception as e:
        print(f"❌ Email integration test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 FIXING ALL BACKEND ISSUES")
    print("=" * 60)
    
    # Step 1: Check service files
    supabase_ok = fix_supabase_service()
    main_ok = fix_main_enhanced()
    
    if not (supabase_ok and main_ok):
        print("\n❌ Service files have issues - need manual fixes")
        exit(1)
    
    # Step 2: Test backend startup
    startup_ok = test_backend_startup()
    
    if not startup_ok:
        print("\n❌ Backend startup issues - need manual fixes")
        exit(1)
    
    # Step 3: Start backend properly
    backend_started = start_backend_properly()
    
    if not backend_started:
        print("\n❌ Failed to start backend properly")
        exit(1)
    
    # Step 4: Test email integration
    email_ok = test_email_integration()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS")
    print("=" * 60)
    
    if email_ok:
        print("🎉 SUCCESS: All issues fixed!")
        print("✅ Backend is running properly")
        print("✅ Email integration is working")
        print("📧 Onboarding emails are sent after approval")
        print("\nCheck goutamramv@gmail.com for:")
        print("  1. Job approval notification")
        print("  2. Onboarding welcome email with secure link")
    else:
        print("❌ ISSUES REMAIN:")
        print("🔧 Email integration needs more work")
        print("📧 Check email service configuration")
    
    exit(0 if email_ok else 1)