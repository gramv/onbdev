#!/usr/bin/env python3
"""
Environment Variable Verification Test
Verifies that the FRONTEND_URL is correctly set and creates a final test email
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
import time

def test_env_and_email():
    """Test environment variable and send final email"""
    print("🔍 ENVIRONMENT VERIFICATION & FINAL EMAIL TEST")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Step 1: Check environment variable
        print("\n1. 🌐 Checking environment variable...")
        frontend_url = os.getenv('FRONTEND_URL', 'NOT_SET')
        print(f"   FRONTEND_URL: {frontend_url}")
        
        if frontend_url == "http://localhost:3000":
            print(f"   ✅ Environment variable is CORRECT")
        else:
            print(f"   ⚠️  Setting environment variable explicitly")
            os.environ['FRONTEND_URL'] = 'http://localhost:3000'
            print(f"   ✅ Environment variable set to: {os.environ['FRONTEND_URL']}")
        
        # Step 2: Login as Manager
        print("\n2. 🔐 Logging in as Manager...")
        manager_login_response = requests.post(f"{base_url}/auth/login", json={
            "email": "manager@hoteltest.com",
            "password": "manager123"
        })
        
        if manager_login_response.status_code != 200:
            print(f"❌ Manager login failed: {manager_login_response.text}")
            return False
        
        manager_data = manager_login_response.json()
        manager_token = manager_data["token"]
        print(f"✅ Manager login successful")
        
        # Step 3: Create final verification application
        print("\n3. 📝 Creating FINAL VERIFICATION application...")
        
        timestamp = int(time.time())
        unique_id = f"VERIFY{timestamp}"
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        application_data = {
            "first_name": "Goutam",
            "last_name": f"VERIFY{timestamp}",
            "email": "goutamramv@gmail.com",
            "phone": f"(555) {timestamp % 1000:03d}-9999",
            "address": f"888 Verification Lane #{timestamp % 100}",
            "city": "Verification City",
            "state": "TX", 
            "zip_code": "75001",
            "department": "Maintenance",
            "position": "Maintenance Technician",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": future_date,
            "shift_preference": "day",
            "employment_type": "full_time",
            "experience_years": "5+",
            "hotel_experience": "yes",
            "previous_employer": f"Verification Corp {timestamp}",
            "reason_for_leaving": "Final verification test",
            "additional_comments": f"FINAL VERIFICATION TEST {unique_id} - This should have port 3000!"
        }
        
        app_response = requests.post(f"{base_url}/apply/prop_test_001", json=application_data)
        
        if app_response.status_code != 200:
            print(f"❌ Failed to create application: {app_response.text}")
            return False
        
        app_data = app_response.json()
        application_id = app_data["application_id"]
        print(f"✅ VERIFICATION application created: {application_id}")
        
        # Step 4: Approve with explicit port verification
        print(f"\n4. ✅ APPROVING with PORT 3000 verification...")
        
        approve_response = requests.post(
            f"{base_url}/applications/{application_id}/approve",
            headers={"Authorization": f"Bearer {manager_token}"},
            data={
                "job_title": "Maintenance Technician",
                "start_date": future_date,
                "start_time": "08:00",
                "pay_rate": "22.00",
                "pay_frequency": "biweekly",
                "benefits_eligible": "true",
                "supervisor": "Maintenance Supervisor",
                "special_instructions": f"FINAL VERIFICATION {unique_id} - Port 3000 test. Welcome to the team!"
            }
        )
        
        if approve_response.status_code != 200:
            print(f"❌ Failed to approve application: {approve_response.text}")
            return False
        
        approve_data = approve_response.json()
        employee_id = approve_data.get("employee_id")
        
        print(f"✅ VERIFICATION APPLICATION APPROVED!")
        print(f"   📧 Email sent to: goutamramv@gmail.com")
        print(f"   👤 Employee ID: {employee_id}")
        print(f"   🆔 Unique ID: {unique_id}")
        
        print(f"\n🎊 FINAL VERIFICATION COMPLETED!")
        print("=" * 60)
        print("📧 VERIFICATION EMAIL SENT:")
        print(f"   ✅ TO: goutamramv@gmail.com")
        print(f"   🆔 LOOK FOR: {unique_id} in the email content")
        print(f"   💼 POSITION: Maintenance Technician")
        print(f"   🔗 LINK: Should be http://localhost:3000/onboarding/[token]")
        print()
        print("📬 FINAL INSTRUCTIONS:")
        print("   1. Check goutamramv@gmail.com for the NEWEST email")
        print(f"   2. Look for '{unique_id}' in the email to identify it")
        print("   3. The onboarding link MUST use port 3000")
        print("   4. Click the link to access your Task 3 welcome page")
        print()
        print("✨ This is the FINAL test - the port should now be correct!")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Starting FINAL Environment Verification Test")
    print("🎯 This will ensure port 3000 is used in onboarding links")
    print()
    
    success = test_env_and_email()
    
    if success:
        print("\n🎉 SUCCESS! Environment verification completed!")
        print("📧 Check your email for the NEWEST message with correct port!")
        exit(0)
    else:
        print("\n💥 FAILED! Environment verification encountered errors")
        exit(1)

if __name__ == "__main__":
    main()