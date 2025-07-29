#!/usr/bin/env python3
"""
Debug Onboarding URL Generation
Tests the actual URL generation during the approval process
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
import time

def debug_onboarding_url():
    """Debug the actual onboarding URL generation"""
    print("🔍 DEBUGGING ONBOARDING URL GENERATION")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # Step 1: Set environment variable explicitly
        os.environ['FRONTEND_URL'] = 'http://localhost:3000'
        print(f"1. 🌐 Environment variable set: {os.environ.get('FRONTEND_URL')}")
        
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
        
        # Step 3: Create debug application
        print("\n3. 📝 Creating DEBUG application...")
        
        timestamp = int(time.time())
        debug_id = f"DEBUG{timestamp}"
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        application_data = {
            "first_name": "Debug",
            "last_name": f"URLTest{debug_id}",
            "email": "goutamramv@gmail.com",
            "phone": f"(555) {timestamp % 1000:03d}-0000",
            "address": f"777 Debug Street #{timestamp % 100}",
            "city": "Debug City",
            "state": "FL", 
            "zip_code": "33101",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": future_date,
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "1-2",
            "hotel_experience": "no",
            "previous_employer": f"Debug Corp {timestamp}",
            "reason_for_leaving": "URL debugging test",
            "additional_comments": f"DEBUG URL TEST {debug_id} - Testing onboarding URL generation"
        }
        
        app_response = requests.post(f"{base_url}/apply/prop_test_001", json=application_data)
        
        if app_response.status_code != 200:
            print(f"❌ Failed to create application: {app_response.text}")
            return False
        
        app_data = app_response.json()
        application_id = app_data["application_id"]
        print(f"✅ DEBUG application created: {application_id}")
        
        # Step 4: Approve and capture the full response
        print(f"\n4. ✅ APPROVING with URL debugging...")
        
        approve_response = requests.post(
            f"{base_url}/applications/{application_id}/approve",
            headers={"Authorization": f"Bearer {manager_token}"},
            data={
                "job_title": "Front Desk Agent",
                "start_date": future_date,
                "start_time": "09:00",
                "pay_rate": "19.00",
                "pay_frequency": "biweekly",
                "benefits_eligible": "true",
                "supervisor": "Front Desk Manager",
                "special_instructions": f"DEBUG URL TEST {debug_id} - Check the onboarding URL port!"
            }
        )
        
        if approve_response.status_code != 200:
            print(f"❌ Failed to approve application: {approve_response.text}")
            return False
        
        approve_data = approve_response.json()
        print(f"✅ DEBUG APPLICATION APPROVED!")
        
        # Step 5: Examine the response for URL information
        print(f"\n5. 🔍 Examining approval response...")
        print(f"Full response keys: {list(approve_data.keys())}")
        
        if "job_offer" in approve_data:
            job_offer = approve_data["job_offer"]
            print(f"Job offer keys: {list(job_offer.keys())}")
            
            if "onboarding_url" in job_offer:
                onboarding_url = job_offer["onboarding_url"]
                print(f"🔗 ONBOARDING URL FOUND: {onboarding_url}")
                
                if "localhost:3000" in onboarding_url:
                    print(f"✅ CORRECT PORT (3000) detected!")
                elif "localhost:5173" in onboarding_url:
                    print(f"❌ WRONG PORT (5173) detected!")
                    print(f"🔧 This indicates the backend is still using the wrong port")
                else:
                    print(f"⚠️  Unexpected URL format")
            else:
                print(f"⚠️  No onboarding_url in job_offer")
        else:
            print(f"⚠️  No job_offer in response")
        
        # Step 6: Check if there's an onboarding token we can use to test the welcome endpoint
        employee_id = approve_data.get("employee_id")
        if employee_id:
            print(f"\n6. 🎯 Testing onboarding initiation...")
            
            # Try to initiate onboarding to see what URL gets generated
            onboarding_response = requests.post(
                f"{base_url}/api/onboarding/initiate/{application_id}",
                headers={"Authorization": f"Bearer {manager_token}"}
            )
            
            if onboarding_response.status_code == 200:
                onboarding_data = onboarding_response.json()
                onboarding_url = onboarding_data.get("onboarding_url", "")
                
                print(f"🔗 ONBOARDING INITIATION URL: {onboarding_url}")
                
                if "localhost:3000" in onboarding_url:
                    print(f"✅ CORRECT PORT (3000) in onboarding initiation!")
                elif "localhost:5173" in onboarding_url:
                    print(f"❌ WRONG PORT (5173) in onboarding initiation!")
                else:
                    print(f"⚠️  Unexpected onboarding URL format")
            else:
                print(f"⚠️  Onboarding initiation failed: {onboarding_response.status_code}")
        
        print(f"\n🎊 DEBUG COMPLETED!")
        print("=" * 60)
        print("📧 DEBUG EMAIL SENT:")
        print(f"   ✅ TO: goutamramv@gmail.com")
        print(f"   🆔 LOOK FOR: {debug_id} in the email content")
        print(f"   💼 POSITION: Front Desk Agent")
        print()
        print("🔍 DEBUG RESULTS:")
        print("   - Check the console output above for URL analysis")
        print("   - Check your email for the debug message")
        print("   - The URL in the email should match the console output")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug execution"""
    print("🚀 Starting Onboarding URL Debug Test")
    print("🎯 This will analyze the actual URL generation process")
    print()
    
    success = debug_onboarding_url()
    
    if success:
        print("\n🎉 DEBUG COMPLETED!")
        print("📧 Check your email and compare with console output!")
        exit(0)
    else:
        print("\n💥 DEBUG FAILED!")
        exit(1)

if __name__ == "__main__":
    main()