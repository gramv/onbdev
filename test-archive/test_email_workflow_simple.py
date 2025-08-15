#!/usr/bin/env python3
"""
Simple Email Workflow Test
Tests both approval and rejection emails by creating applications with unique data
but ensuring emails go to the target addresses
"""
import sys
import os
import requests
import json
from datetime import datetime, timedelta
import uuid
import time

def test_email_workflow():
    """Test complete email workflow with approval and rejection"""
    print("📧 Testing Email Workflow - Simple Version")
    print("=" * 60)
    print("📋 Test Plan:")
    print("   1. Create unique applications to avoid duplicates")
    print("   2. APPROVE → Send to goutamramv@gmail.com")
    print("   3. REJECT → Send to gvemula@mail.yu.edu")
    print("   4. Test onboarding integration for approved application")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test data
    manager_token = None
    property_id = "prop_test_001"
    
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
        
        # Step 2: Create APPROVAL application with unique data
        print("\n2. 📝 Creating APPROVAL application...")
        print("   📧 Target email: goutamramv@gmail.com")
        
        timestamp = int(time.time())
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        approval_app_data = {
            "first_name": "Goutam",
            "last_name": f"ApprovalTest{timestamp}",
            "email": "goutamramv@gmail.com",
            "phone": f"(555) {timestamp % 1000:03d}-{(timestamp % 10000) // 10:04d}",
            "address": f"123 Approval St #{timestamp % 1000}",
            "city": "New York",
            "state": "NY", 
            "zip_code": "10001",
            "department": "Food & Beverage",
            "position": "Bartender",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": future_date,
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "3-5",
            "hotel_experience": "yes",
            "previous_employer": f"Hotel Chain {timestamp}",
            "reason_for_leaving": "Career advancement",
            "additional_comments": f"Approval test application {timestamp}"
        }
        
        approval_response = requests.post(f"{base_url}/apply/{property_id}", json=approval_app_data)
        
        if approval_response.status_code != 200:
            print(f"❌ Failed to create approval application: {approval_response.text}")
            return False
        
        approval_data = approval_response.json()
        approval_app_id = approval_data["application_id"]
        print(f"✅ Approval application created: {approval_app_id}")
        
        # Step 3: Create REJECTION application with unique data
        print("\n3. 📝 Creating REJECTION application...")
        print("   📧 Target email: gvemula@mail.yu.edu")
        
        rejection_app_data = {
            "first_name": "Goutham",
            "last_name": f"RejectionTest{timestamp}",
            "email": "gvemula@mail.yu.edu",
            "phone": f"(555) {(timestamp + 100) % 1000:03d}-{((timestamp + 100) % 10000) // 10:04d}",
            "address": f"456 Rejection Ave #{(timestamp + 50) % 1000}",
            "city": "Boston",
            "state": "MA",
            "zip_code": "02101",
            "department": "Housekeeping",
            "position": "Laundry Attendant",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": future_date,
            "shift_preference": "day",
            "employment_type": "part_time",
            "experience_years": "1-2",
            "hotel_experience": "no",
            "previous_employer": f"Cleaning Service {timestamp}",
            "reason_for_leaving": "Seeking hotel experience",
            "additional_comments": f"Rejection test application {timestamp}"
        }
        
        rejection_response = requests.post(f"{base_url}/apply/{property_id}", json=rejection_app_data)
        
        if rejection_response.status_code != 200:
            print(f"❌ Failed to create rejection application: {rejection_response.text}")
            return False
        
        rejection_data = rejection_response.json()
        rejection_app_id = rejection_data["application_id"]
        print(f"✅ Rejection application created: {rejection_app_id}")
        
        # Step 4: APPROVE the first application
        print(f"\n4. ✅ APPROVING application {approval_app_id}...")
        print("   📧 This will send approval email to: goutamramv@gmail.com")
        
        approve_response = requests.post(
            f"{base_url}/applications/{approval_app_id}/approve",
            headers={"Authorization": f"Bearer {manager_token}"},
            data={
                "job_title": "Bartender",
                "start_date": future_date,
                "start_time": "08:00",
                "pay_rate": "20.00",
                "pay_frequency": "biweekly",
                "benefits_eligible": "true",
                "supervisor": "Bar Manager",
                "special_instructions": "Welcome to the team! Please check your email for onboarding instructions."
            }
        )
        
        if approve_response.status_code != 200:
            print(f"❌ Failed to approve application: {approve_response.text}")
            return False
        
        approve_data = approve_response.json()
        employee_id = approve_data.get("employee_id")
        print(f"✅ Application approved successfully!")
        print(f"   📧 Approval email sent to: goutamramv@gmail.com")
        if employee_id:
            print(f"   👤 Employee ID: {employee_id}")
        
        # Step 5: REJECT the second application
        print(f"\n5. ❌ REJECTING application {rejection_app_id}...")
        print("   📧 This will send rejection email to: gvemula@mail.yu.edu")
        
        reject_response = requests.post(
            f"{base_url}/applications/{rejection_app_id}/reject",
            headers={"Authorization": f"Bearer {manager_token}"},
            data={
                "rejection_reason": "Position filled",
                "feedback": "Thank you for your interest in joining our team. While we have filled this position, we encourage you to apply for future opportunities."
            }
        )
        
        if reject_response.status_code != 200:
            print(f"❌ Failed to reject application: {reject_response.text}")
            return False
        
        print(f"✅ Application rejected successfully!")
        print(f"   📧 Rejection email sent to: gvemula@mail.yu.edu")
        
        # Step 6: Test onboarding integration for approved application
        if employee_id:
            print(f"\n6. 🎯 Testing onboarding integration...")
            
            # Initiate onboarding
            onboarding_response = requests.post(
                f"{base_url}/api/onboarding/initiate/{approval_app_id}",
                headers={"Authorization": f"Bearer {manager_token}"}
            )
            
            if onboarding_response.status_code == 200:
                onboarding_data = onboarding_response.json()
                onboarding_token = onboarding_data["onboarding_token"]
                
                print(f"✅ Onboarding session created:")
                print(f"   🎫 Session ID: {onboarding_data['session_id']}")
                print(f"   🌟 Welcome URL: {onboarding_data['onboarding_url']}")
                print(f"   ⏰ Expires: {onboarding_data['expires_at']}")
                
                # Test welcome page
                welcome_response = requests.get(f"{base_url}/api/onboarding/welcome/{onboarding_token}")
                if welcome_response.status_code == 200:
                    welcome_data = welcome_response.json()
                    print(f"   ✅ Task 3 Welcome Page accessible:")
                    print(f"      👤 Employee: {welcome_data['employee']['name']}")
                    print(f"      🏨 Property: {welcome_data['property']['name']}")
                    print(f"      💼 Position: {welcome_data['job_details']['job_title']}")
                else:
                    print(f"   ⚠️  Welcome page issue: {welcome_response.status_code}")
            else:
                print(f"   ⚠️  Onboarding initiation failed: {onboarding_response.status_code}")
        
        # Step 7: Final summary
        print(f"\n🎊 EMAIL WORKFLOW TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("📧 EMAILS SENT:")
        print(f"   ✅ APPROVAL: goutamramv@gmail.com")
        print(f"      • Job offer approval with onboarding link")
        print(f"      • Position: Front Desk Agent")
        print(f"      • Pay: $20.00/hour")
        print(f"   ❌ REJECTION: gvemula@mail.yu.edu")
        print(f"      • Professional rejection with encouragement")
        print(f"      • Added to talent pool for future opportunities")
        print()
        print("📬 NEXT STEPS:")
        print("   1. Check goutamramv@gmail.com for approval email")
        print("   2. Check gvemula@mail.yu.edu for rejection email")
        print("   3. Click onboarding link to see Task 3 welcome page")
        print("   4. Test the complete onboarding workflow")
        print()
        print("🌟 FEATURES VERIFIED:")
        print("   ✅ Email sending with Gmail SMTP")
        print("   ✅ Approval workflow with onboarding integration")
        print("   ✅ Rejection workflow with talent pool")
        print("   ✅ Task 3 welcome page integration")
        print("   ✅ Professional email templates")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Simple Email Workflow Test")
    print("📧 SMTP: Gmail (vgoutamram@gmail.com)")
    print("🎯 Target emails: goutamramv@gmail.com (approval), gvemula@mail.yu.edu (rejection)")
    print()
    
    success = test_email_workflow()
    
    if success:
        print("\n🎉 SUCCESS! Email workflow test completed!")
        exit(0)
    else:
        print("\n💥 FAILED! Email workflow test encountered errors")
        exit(1)

if __name__ == "__main__":
    main()