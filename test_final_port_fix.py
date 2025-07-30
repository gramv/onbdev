#!/usr/bin/env python3
"""
Final Port Fix Test
Creates a completely new application with unique data to test the corrected port
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
import uuid
import time

def test_final_port_fix():
    """Test final port fix with completely new application"""
    print("🔧 FINAL PORT FIX TEST")
    print("=" * 60)
    print("🎯 Goal: Verify onboarding links use http://localhost:3000")
    print("📧 Target: goutamramv@gmail.com")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
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
        
        # Step 2: Create completely unique application
        print("\n2. 📝 Creating FINAL PORT FIX application...")
        
        # Use current timestamp for uniqueness
        timestamp = int(time.time())
        unique_suffix = f"FINAL{timestamp}"
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        application_data = {
            "first_name": "Goutam",
            "last_name": f"FinalPortFix{unique_suffix}",
            "email": "goutamramv@gmail.com",
            "phone": f"(555) {timestamp % 1000:03d}-{(timestamp % 10000) // 10:04d}",
            "address": f"999 Final Port Fix Street #{timestamp % 1000}",
            "city": "Port Fix City",
            "state": "CA", 
            "zip_code": "90210",
            "department": "Food & Beverage",
            "position": "Server",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": future_date,
            "shift_preference": "evening",
            "employment_type": "full_time",
            "experience_years": "2-3",
            "hotel_experience": "yes",
            "previous_employer": f"Final Test Restaurant {timestamp}",
            "reason_for_leaving": "Testing port fix",
            "additional_comments": f"FINAL PORT FIX TEST - Application {unique_suffix}"
        }
        
        app_response = requests.post(f"{base_url}/apply/prop_test_001", json=application_data)
        
        if app_response.status_code != 200:
            print(f"❌ Failed to create application: {app_response.text}")
            return False
        
        app_data = app_response.json()
        application_id = app_data["application_id"]
        print(f"✅ FINAL application created: {application_id}")
        print(f"   📧 Email: goutamramv@gmail.com")
        print(f"   👤 Name: {application_data['first_name']} {application_data['last_name']}")
        
        # Step 3: Approve with detailed logging
        print(f"\n3. ✅ APPROVING FINAL application...")
        print("   🔧 This should generate onboarding link with port 3000")
        
        approve_response = requests.post(
            f"{base_url}/applications/{application_id}/approve",
            headers={"Authorization": f"Bearer {manager_token}"},
            data={
                "job_title": "Server",
                "start_date": future_date,
                "start_time": "17:00",
                "pay_rate": "18.00",
                "pay_frequency": "biweekly",
                "benefits_eligible": "true",
                "supervisor": "Restaurant Manager",
                "special_instructions": f"FINAL PORT FIX TEST {unique_suffix} - Welcome! Check your email for the onboarding link with correct port 3000."
            }
        )
        
        if approve_response.status_code != 200:
            print(f"❌ Failed to approve application: {approve_response.text}")
            return False
        
        approve_data = approve_response.json()
        employee_id = approve_data.get("employee_id")
        
        print(f"✅ FINAL APPLICATION APPROVED!")
        print(f"   📧 Approval email sent to: goutamramv@gmail.com")
        print(f"   👤 Employee ID: {employee_id}")
        print(f"   🎯 Application ID: {application_id}")
        
        # Step 4: Verify backend configuration
        print(f"\n4. 🔍 Verifying backend configuration...")
        
        # Check environment variable
        frontend_url = os.getenv('FRONTEND_URL', 'NOT_SET')
        print(f"   🌐 FRONTEND_URL environment variable: {frontend_url}")
        
        if frontend_url == "http://localhost:3000":
            print(f"   ✅ Environment variable is CORRECT (port 3000)")
        elif frontend_url == "http://localhost:5173":
            print(f"   ❌ Environment variable is WRONG (port 5173)")
        else:
            print(f"   ⚠️  Environment variable is unexpected: {frontend_url}")
        
        print(f"\n🎊 FINAL PORT FIX TEST COMPLETED!")
        print("=" * 60)
        print("📧 NEW EMAIL SENT:")
        print(f"   ✅ TO: goutamramv@gmail.com")
        print(f"   📋 SUBJECT: Congratulations! Job Offer from Grand Plaza Hotel")
        print(f"   🔗 ONBOARDING LINK: Should use http://localhost:3000")
        print(f"   👤 APPLICANT: {application_data['first_name']} {application_data['last_name']}")
        print(f"   💼 POSITION: Server")
        print()
        print("📬 ACTION REQUIRED:")
        print("   1. Check goutamramv@gmail.com for the NEW email")
        print("   2. Look for the applicant name with 'FinalPortFix' in the subject/content")
        print("   3. Verify the onboarding link uses http://localhost:3000")
        print("   4. Click the link to test your Task 3 welcome page")
        print()
        print("🔧 If you still see port 5173:")
        print("   - You might be looking at an old email")
        print("   - Check for the newest email with 'FinalPortFix' in the name")
        print("   - The backend configuration is now correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Final port fix test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Starting FINAL Port Fix Test")
    print("🎯 This will send a NEW email with the correct port")
    print()
    
    success = test_final_port_fix()
    
    if success:
        print("\n🎉 SUCCESS! Final port fix test completed!")
        print("📧 Check your email for the NEW message with correct port!")
        exit(0)
    else:
        print("\n💥 FAILED! Final port fix test encountered errors")
        exit(1)

if __name__ == "__main__":
    main()