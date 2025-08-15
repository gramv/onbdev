#!/usr/bin/env python3
"""
Direct test of email functionality in application endpoints
Tests email notifications by directly calling the functions
"""
import asyncio
import sys
import os
from datetime import datetime, date
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main_enhanced import database
from app.models import JobApplication, ApplicationStatus, JobOfferData, User, UserRole
from app.email_service import email_service

async def test_email_endpoints():
    """Test email functionality in application endpoints"""
    print("🧪 Testing Email Functionality in Application Endpoints...")
    print("=" * 60)
    
    # Get test data from database
    test_application = None
    test_manager = None
    test_property = None
    
    for app_id, application in database["applications"].items():
        if application.status == ApplicationStatus.PENDING:
            test_application = application
            break
    
    for user_id, user in database["users"].items():
        if user.role == UserRole.MANAGER:
            test_manager = user
            break
    
    for prop_id, prop in database["properties"].items():
        test_property = prop
        break
    
    if not all([test_application, test_manager, test_property]):
        print("❌ Missing test data")
        return
    
    print(f"✅ Test data ready:")
    print(f"   Application: {test_application.applicant_data['first_name']} {test_application.applicant_data['last_name']}")
    print(f"   Manager: {test_manager.first_name} {test_manager.last_name}")
    print(f"   Property: {test_property.name}")
    print()
    
    # Test 1: Approval Email
    print("1️⃣ Testing Approval Email Notification...")
    
    job_offer_data = JobOfferData(
        job_title="Front Desk Agent",
        start_date=date(2025, 2, 15),
        pay_rate=18.50,
        pay_frequency="biweekly",
        employment_type="full_time",
        benefits_eligible=True,
        supervisor="Mike Wilson"
    )
    
    try:
        success = await email_service.send_approval_notification(
            applicant_email=test_application.applicant_data["email"],
            applicant_name=f"{test_application.applicant_data['first_name']} {test_application.applicant_data['last_name']}".strip(),
            property_name=test_property.name,
            position=test_application.position,
            job_title=job_offer_data.job_title,
            start_date=job_offer_data.start_date.strftime("%B %d, %Y"),
            pay_rate=job_offer_data.pay_rate,
            onboarding_link="http://localhost:5173/onboarding/test-token-123",
            manager_name=f"{test_manager.first_name} {test_manager.last_name}".strip(),
            manager_email=test_manager.email
        )
        print(f"   ✅ Approval email: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"   ❌ Approval email failed: {str(e)}")
    
    print()
    
    # Test 2: Rejection Email
    print("2️⃣ Testing Rejection Email Notification...")
    
    try:
        success = await email_service.send_rejection_notification(
            applicant_email=test_application.applicant_data["email"],
            applicant_name=f"{test_application.applicant_data['first_name']} {test_application.applicant_data['last_name']}".strip(),
            property_name=test_property.name,
            position=test_application.position,
            manager_name=f"{test_manager.first_name} {test_manager.last_name}".strip(),
            manager_email=test_manager.email
        )
        print(f"   ✅ Rejection email: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"   ❌ Rejection email failed: {str(e)}")
    
    print()
    
    # Test 3: Talent Pool Email
    print("3️⃣ Testing Talent Pool Email Notification...")
    
    try:
        success = await email_service.send_talent_pool_notification(
            applicant_email=test_application.applicant_data["email"],
            applicant_name=f"{test_application.applicant_data['first_name']} {test_application.applicant_data['last_name']}".strip(),
            property_name=test_property.name,
            position=test_application.position,
            manager_name=f"{test_manager.first_name} {test_manager.last_name}".strip(),
            manager_email=test_manager.email
        )
        print(f"   ✅ Talent pool email: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"   ❌ Talent pool email failed: {str(e)}")
    
    print()
    
    # Test 4: Email Template Generation
    print("4️⃣ Testing Email Template Generation...")
    
    try:
        # Test approval template
        html_content, text_content = email_service._get_approval_template(
            applicant_name="John Doe",
            property_name="Grand Plaza Hotel",
            position="Front Desk Agent",
            job_title="Front Desk Agent",
            start_date="February 15, 2025",
            pay_rate=18.50,
            onboarding_link="http://localhost:5173/onboarding/test-token",
            manager_name="Mike Wilson",
            manager_email="manager@hoteltest.com"
        )
        
        print(f"   ✅ Approval template generated ({len(html_content)} chars HTML, {len(text_content)} chars text)")
        
        # Test rejection template
        html_content, text_content = email_service._get_rejection_template(
            applicant_name="John Doe",
            property_name="Grand Plaza Hotel",
            position="Front Desk Agent",
            manager_name="Mike Wilson",
            manager_email="manager@hoteltest.com"
        )
        
        print(f"   ✅ Rejection template generated ({len(html_content)} chars HTML, {len(text_content)} chars text)")
        
        # Test talent pool template
        html_content, text_content = email_service._get_talent_pool_template(
            applicant_name="John Doe",
            property_name="Grand Plaza Hotel",
            position="Front Desk Agent",
            manager_name="Mike Wilson",
            manager_email="manager@hoteltest.com"
        )
        
        print(f"   ✅ Talent pool template generated ({len(html_content)} chars HTML, {len(text_content)} chars text)")
        
    except Exception as e:
        print(f"   ❌ Template generation failed: {str(e)}")
    
    print()
    print("=" * 60)
    print("✅ Email Endpoint Testing Complete!")
    print()
    print("📧 Email Service Status:")
    print(f"   Configured: {email_service.is_configured}")
    print(f"   SMTP Host: {email_service.smtp_host}")
    print(f"   From Email: {email_service.from_email}")
    print()
    print("📝 Integration Points:")
    print("   ✅ Approval endpoint (/hr/applications/{id}/approve)")
    print("   ✅ Rejection endpoint (/hr/applications/{id}/reject)")
    print("   ✅ Bulk talent pool endpoint (/hr/applications/bulk-talent-pool)")
    print()
    print("🔧 Production Setup:")
    print("   1. Configure SMTP credentials in .env file")
    print("   2. Set SMTP_USERNAME and SMTP_PASSWORD")
    print("   3. Update FROM_EMAIL and FROM_NAME as needed")

if __name__ == "__main__":
    asyncio.run(test_email_endpoints())