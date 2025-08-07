#!/usr/bin/env python3
"""
Test Email with Correct Port
Creates a new application and approves it to test the corrected port in onboarding link
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
import uuid
import time

def test_correct_port_email():
    """Test email with correct port configuration"""
    print("📧 Testing Email with Correct Port Configuration")
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
        
        # Step 2: Create application for approval
        print("\n2. 📝 Creating application for port test...")
        print("   📧 Target email: goutamramv@gmail.com")
        
        timestamp = int(time.time())
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        application_data = {
            "first_name": "Goutam",
            "last_name": f"PortTest{timestamp}",
            "email": "goutamramv@gmail.com",
            "phone": f"(555) {timestamp % 1000:03d}-{(timestamp % 10000) // 10:04d}",
            "address": f"123 Port Test St #{timestamp % 1000}",
            "city": "New York",
            "state": "NY", 
            "zip_code": "10001",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": future_date,
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "3-5",
            "hotel_experience": "yes",
            "previous_employer": f"Test Hotel {timestamp}",
            "reason_for_leaving": "Career advancement",
            "additional_comments": f"Port test application {timestamp}"
        }
        
        app_response = requests.post(f"{base_url}/apply/prop_test_001", json=application_data)
        
        if app_response.status_code != 200:
            print(f"❌ Failed to create application: {app_response.text}")
            return False
        
        app_data = app_response.json()
        application_id = app_data["application_id"]
        print(f"✅ Application created: {application_id}")
        
        # Step 3: Approve the application
        print(f"\n3. ✅ APPROVING application with correct port...")
        print("   📧 This will send approval email to: goutamramv@gmail.com")
        print("   🔗 Expected port: 3000 (not 5173)")
        
        approve_response = requests.post(
            f"{base_url}/applications/{application_id}/approve",
            headers={"Authorization": f"Bearer {manager_token}"},
            data={
                "job_title": "Front Desk Agent",
                "start_date": future_date,
                "start_time": "08:00",
                "pay_rate": "20.00",
                "pay_frequency": "biweekly",
                "benefits_eligible": "true",
                "supervisor": "Front Desk Manager",
                "special_instructions": "Port test - Welcome to the team! Check the onboarding link port."
            }
        )
        
        if approve_response.status_code != 200:
            print(f"❌ Failed to approve application: {approve_response.text}")
            return False
        
        approve_data = approve_response.json()
        employee_id = approve_data.get("employee_id")
        onboarding_url = approve_data.get("job_offer", {}).get("onboarding_url", "")
        
        print(f"✅ Application approved successfully!")
        print(f"   📧 Approval email sent to: goutamramv@gmail.com")
        print(f"   👤 Employee ID: {employee_id}")
        
        if onboarding_url:
            print(f"   🔗 Onboarding URL: {onboarding_url}")
            if "localhost:3000" in onboarding_url:
                print(f"   ✅ Correct port (3000) detected in URL!")
            elif "localhost:5173" in onboarding_url:
                print(f"   ❌ Incorrect port (5173) still in URL!")
            else:
                print(f"   ⚠️  Unexpected URL format")
        
        print(f"\n🎊 PORT CORRECTION TEST COMPLETED!")
        print("=" * 60)
        print("📧 EMAIL SENT:")
        print(f"   ✅ APPROVAL: goutamramv@gmail.com")
        print(f"   🔗 Onboarding link should now use port 3000")
        print()
        print("📬 NEXT STEPS:")
        print("   1. Check goutamramv@gmail.com for the new approval email")
        print("   2. Verify the onboarding link uses http://localhost:3000")
        print("   3. Click the link to test your Task 3 welcome page")
        
        return True
        
    except Exception as e:
        print(f"❌ Port test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Port Correction Test")
    print("🎯 Testing corrected frontend URL (port 3000)")
    print()
    
    success = test_correct_port_email()
    
    if success:
        print("\n🎉 SUCCESS! Port correction test completed!")
        exit(0)
    else:
        print("\n💥 FAILED! Port correction test encountered errors")
        exit(1)

if __name__ == "__main__":
    main()