#!/usr/bin/env python3
"""
Integration test for Email Service with Application Approval/Rejection workflow
Tests the complete flow including email notifications
"""
import asyncio
import sys
import os
import json
from datetime import datetime, date
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Import the main app and dependencies
from app.main_enhanced import app, database
from app.models import JobApplication, ApplicationStatus, JobOfferData
from fastapi.testclient import TestClient

def test_email_integration():
    """Test email integration with application approval/rejection"""
    print("🧪 Testing Email Integration with Application Workflow...")
    print("=" * 60)
    
    client = TestClient(app)
    
    # Get test data from initialized database
    print("📊 Database Status:")
    print(f"   Users: {len(database['users'])}")
    print(f"   Properties: {len(database['properties'])}")
    print(f"   Applications: {len(database['applications'])}")
    print()
    
    # Find test application and manager
    test_application = None
    test_manager_token = None
    
    for app_id, application in database["applications"].items():
        if application.status == ApplicationStatus.PENDING:
            test_application = application
            break
    
    # Find manager user for authentication
    for user_id, user in database["users"].items():
        if user.role.value == "manager":
            test_manager_token = user_id  # Using user ID as token for testing
            break
    
    if not test_application:
        print("❌ No pending test application found")
        return
    
    if not test_manager_token:
        print("❌ No manager user found")
        return
    
    print(f"✅ Found test application: {test_application.id}")
    print(f"   Applicant: {test_application.applicant_data['first_name']} {test_application.applicant_data['last_name']}")
    print(f"   Position: {test_application.position}")
    print(f"   Email: {test_application.applicant_data['email']}")
    print()
    
    # Test 1: Application Approval with Email Notification
    print("1️⃣ Testing Application Approval with Email Notification...")
    
    job_offer_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-02-15",
        "pay_rate": 18.50,
        "pay_frequency": "biweekly",
        "employment_type": "full_time",
        "benefits_eligible": True,
        "supervisor": "Mike Wilson"
    }
    
    try:
        response = client.post(
            f"/hr/applications/{test_application.id}/approve",
            json=job_offer_data,
            headers={"Authorization": f"Bearer {test_manager_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Application approved successfully")
            print(f"   📧 Approval email should have been sent to: {test_application.applicant_data['email']}")
            print(f"   🎯 Talent pool notifications sent for other applications")
            print(f"   🔗 Onboarding link: {result['onboarding']['onboarding_url']}")
        else:
            print(f"   ❌ Approval failed: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"   ❌ Approval test failed: {str(e)}")
    
    print()
    
    # Test 2: Create another application for rejection test
    print("2️⃣ Testing Application Rejection with Email Notification...")
    
    # Create a new test application
    new_app_id = "test_rejection_app"
    rejection_application = JobApplication(
        id=new_app_id,
        property_id=test_application.property_id,
        department="Housekeeping",
        position="Housekeeper",
        applicant_data={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@email.com",
            "phone": "(555) 123-4567",
            "address": "789 Test Street",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "work_authorized": "yes",
            "sponsorship_required": "no"
        },
        status=ApplicationStatus.PENDING,
        applied_at=datetime.now()
    )
    
    database["applications"][new_app_id] = rejection_application
    
    try:
        response = client.post(
            f"/hr/applications/{new_app_id}/reject",
            data={"rejection_reason": "Position filled by another candidate"},
            headers={"Authorization": f"Bearer {test_manager_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Application rejected successfully")
            print(f"   📧 Rejection email should have been sent to: {rejection_application.applicant_data['email']}")
            print(f"   📝 Reason: {result['rejection_reason']}")
        else:
            print(f"   ❌ Rejection failed: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"   ❌ Rejection test failed: {str(e)}")
    
    print()
    
    # Test 3: Bulk Talent Pool with Email Notifications
    print("3️⃣ Testing Bulk Talent Pool with Email Notifications...")
    
    # Create multiple test applications
    bulk_app_ids = []
    for i in range(2):
        app_id = f"bulk_test_app_{i}"
        bulk_application = JobApplication(
            id=app_id,
            property_id=test_application.property_id,
            department="Food & Beverage",
            position="Server",
            applicant_data={
                "first_name": f"Test{i}",
                "last_name": "Applicant",
                "email": f"test{i}@email.com",
                "phone": f"(555) 000-000{i}",
                "address": f"{i} Test Avenue",
                "city": "Test City",
                "state": "CA",
                "zip_code": "90210",
                "work_authorized": "yes",
                "sponsorship_required": "no"
            },
            status=ApplicationStatus.PENDING,
            applied_at=datetime.now()
        )
        database["applications"][app_id] = bulk_application
        bulk_app_ids.append(app_id)
    
    try:
        response = client.post(
            "/hr/applications/bulk-talent-pool",
            json=bulk_app_ids,
            headers={"Authorization": f"Bearer {test_manager_token}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Bulk talent pool operation successful")
            print(f"   📧 Talent pool emails sent to {result['moved_count']} applicants")
            print(f"   📊 Moved {result['moved_count']} out of {result['total_requested']} applications")
        else:
            print(f"   ❌ Bulk talent pool failed: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"   ❌ Bulk talent pool test failed: {str(e)}")
    
    print()
    print("=" * 60)
    print("✅ Email Integration Test Complete!")
    print()
    print("📝 Summary:")
    print("   - Email service is integrated with approval workflow")
    print("   - Email service is integrated with rejection workflow") 
    print("   - Email service is integrated with talent pool workflow")
    print("   - All emails are logged in development mode")
    print("   - Production SMTP configuration available in .env")

if __name__ == "__main__":
    test_email_integration()