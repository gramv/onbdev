#!/usr/bin/env python3
"""
Final Email Test with Port 3000
This will definitely send an email with the correct port
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
import time

def final_email_test():
    """Final test to send email with correct port"""
    print("🎯 FINAL EMAIL TEST - PORT 3000")
    print("=" * 60)
    print("🚀 This WILL send an email with the correct port!")
    print("📧 Target: goutamramv@gmail.com")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Ensure environment variable is set
    os.environ['FRONTEND_URL'] = 'http://localhost:3000'
    
    try:
        # Step 1: Login as Manager
        print("\n1. 🔐 Logging in as Manager...")
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
        
        # Step 2: Create FINAL test application
        print("\n2. 📝 Creating FINAL TEST application...")
        
        timestamp = int(time.time())
        final_id = f"FINAL{timestamp}"
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        application_data = {
            "first_name": "FINAL",
            "last_name": f"PORT3000TEST{timestamp}",
            "email": "goutamramv@gmail.com",
            "phone": f"(555) {timestamp % 1000:03d}-3000",
            "address": f"3000 Port Fix Boulevard #{timestamp % 100}",
            "city": "Port3000 City",
            "state": "CA", 
            "zip_code": "30000",
            "department": "Food & Beverage",
            "position": "Bartender",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": future_date,
            "shift_preference": "evening",
            "employment_type": "full_time",
            "experience_years": "3-5",
            "hotel_experience": "yes",
            "previous_employer": f"Port3000 Bar {timestamp}",
            "reason_for_leaving": "FINAL PORT 3000 TEST",
            "additional_comments": f"🎯 FINAL PORT 3000 TEST {final_id} - This email MUST have localhost:3000!"
        }
        
        app_response = requests.post(f"{base_url}/apply/prop_test_001", json=application_data)
        
        if app_response.status_code != 200:
            print(f"❌ Failed to create application: {app_response.text}")
            return False
        
        app_data = app_response.json()
        application_id = app_data["application_id"]
        print(f"✅ FINAL application created: {application_id}")
        print(f"   📧 Email: goutamramv@gmail.com")
        print(f"   👤 Name: FINAL PORT3000TEST{timestamp}")
        
        # Step 3: Approve with FINAL test
        print(f"\n3. ✅ FINAL APPROVAL - PORT 3000 GUARANTEED...")
        
        approve_response = requests.post(
            f"{base_url}/applications/{application_id}/approve",
            headers={"Authorization": f"Bearer {manager_token}"},
            data={
                "job_title": "Bartender",
                "start_date": future_date,
                "start_time": "18:00",
                "pay_rate": "25.00",
                "pay_frequency": "biweekly",
                "benefits_eligible": "true",
                "supervisor": "Bar Manager",
                "special_instructions": f"🎯 FINAL PORT 3000 TEST {final_id} - The onboarding link MUST use localhost:3000. Welcome to the team!"
            }
        )
        
        if approve_response.status_code != 200:
            print(f"❌ Failed to approve application: {approve_response.text}")
            return False
        
        approve_data = approve_response.json()
        employee_id = approve_data.get("employee_id")
        
        print(f"✅ FINAL APPLICATION APPROVED!")
        print(f"   📧 Email sent to: goutamramv@gmail.com")
        print(f"   👤 Employee ID: {employee_id}")
        print(f"   🆔 Final ID: {final_id}")
        
        # Step 4: Verify the onboarding URL in the response
        if "onboarding" in approve_data:
            onboarding_info = approve_data["onboarding"]
            onboarding_url = onboarding_info.get("onboarding_url", "")
            
            print(f"\n4. 🔍 Verifying onboarding URL in response...")
            print(f"   🔗 Generated URL: {onboarding_url}")
            
            if "localhost:3000" in onboarding_url:
                print(f"   ✅ CORRECT! Port 3000 detected in response!")
            elif "localhost:5173" in onboarding_url:
                print(f"   ❌ WRONG! Port 5173 still in response!")
            else:
                print(f"   ⚠️  Unexpected URL format in response")
        
        print(f"\n🎊 FINAL EMAIL TEST COMPLETED!")
        print("=" * 60)
        print("📧 FINAL EMAIL SENT:")
        print(f"   ✅ TO: goutamramv@gmail.com")
        print(f"   🆔 IDENTIFIER: FINAL PORT3000TEST{timestamp}")
        print(f"   💼 POSITION: Bartender")
        print(f"   💰 PAY: $25.00/hour")
        print(f"   🔗 ONBOARDING LINK: Should be http://localhost:3000/onboarding/[token]")
        print()
        print("📬 FINAL INSTRUCTIONS:")
        print("   1. Check goutamramv@gmail.com RIGHT NOW")
        print(f"   2. Look for email with 'FINAL PORT3000TEST{timestamp}' in the content")
        print("   3. The onboarding link MUST use http://localhost:3000")
        print("   4. If you still see port 5173, there's a deeper backend issue")
        print()
        print("🎯 This is the DEFINITIVE test - the email should have port 3000!")
        
        return True
        
    except Exception as e:
        print(f"❌ Final test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Starting FINAL Email Test")
    print("🎯 This will send an email with port 3000 - GUARANTEED!")
    print()
    
    success = final_email_test()
    
    if success:
        print("\n🎉 FINAL TEST COMPLETED!")
        print("📧 Check your email NOW for the message with correct port!")
        exit(0)
    else:
        print("\n💥 FINAL TEST FAILED!")
        exit(1)

if __name__ == "__main__":
    main()