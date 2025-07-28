#!/usr/bin/env python3
"""
Test script for Email Service functionality
Tests all email notification types without requiring SMTP configuration
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.email_service import email_service

async def test_email_service():
    """Test all email notification functions"""
    print("🧪 Testing Email Service...")
    print("=" * 50)
    
    # Test data
    test_data = {
        "applicant_email": "john.doe@email.com",
        "applicant_name": "John Doe",
        "property_name": "Grand Plaza Hotel",
        "position": "Front Desk Agent",
        "job_title": "Front Desk Agent",
        "start_date": "February 15, 2025",
        "pay_rate": 18.50,
        "onboarding_link": "http://localhost:5173/onboarding/test-token-123",
        "manager_name": "Mike Wilson",
        "manager_email": "manager@hoteltest.com"
    }
    
    print(f"📧 Email service configured: {email_service.is_configured}")
    print(f"📧 SMTP Host: {email_service.smtp_host}")
    print(f"📧 From Email: {email_service.from_email}")
    print()
    
    # Test 1: Approval Notification
    print("1️⃣ Testing Approval Notification...")
    try:
        success = await email_service.send_approval_notification(
            applicant_email=test_data["applicant_email"],
            applicant_name=test_data["applicant_name"],
            property_name=test_data["property_name"],
            position=test_data["position"],
            job_title=test_data["job_title"],
            start_date=test_data["start_date"],
            pay_rate=test_data["pay_rate"],
            onboarding_link=test_data["onboarding_link"],
            manager_name=test_data["manager_name"],
            manager_email=test_data["manager_email"]
        )
        print(f"   ✅ Approval notification: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"   ❌ Approval notification failed: {str(e)}")
    
    print()
    
    # Test 2: Rejection Notification
    print("2️⃣ Testing Rejection Notification...")
    try:
        success = await email_service.send_rejection_notification(
            applicant_email=test_data["applicant_email"],
            applicant_name=test_data["applicant_name"],
            property_name=test_data["property_name"],
            position=test_data["position"],
            manager_name=test_data["manager_name"],
            manager_email=test_data["manager_email"]
        )
        print(f"   ✅ Rejection notification: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"   ❌ Rejection notification failed: {str(e)}")
    
    print()
    
    # Test 3: Talent Pool Notification
    print("3️⃣ Testing Talent Pool Notification...")
    try:
        success = await email_service.send_talent_pool_notification(
            applicant_email=test_data["applicant_email"],
            applicant_name=test_data["applicant_name"],
            property_name=test_data["property_name"],
            position=test_data["position"],
            manager_name=test_data["manager_name"],
            manager_email=test_data["manager_email"]
        )
        print(f"   ✅ Talent pool notification: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"   ❌ Talent pool notification failed: {str(e)}")
    
    print()
    print("=" * 50)
    print("✅ Email Service Test Complete!")
    print()
    print("📝 Note: Since SMTP is not configured in development,")
    print("   emails are logged to console instead of being sent.")
    print("   In production, configure SMTP settings in .env file.")

if __name__ == "__main__":
    asyncio.run(test_email_service())