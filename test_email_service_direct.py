#!/usr/bin/env python3
"""
Direct Email Service Test
Tests the email service directly to verify SMTP configuration
"""
import sys
import os
import asyncio

# Add the backend path to sys.path
sys.path.insert(0, 'hotel-onboarding-backend')

async def test_email_service():
    """Test the email service directly"""
    print("📧 Testing Email Service Directly")
    print("=" * 50)
    
    try:
        from app.email_service import email_service
        
        # Check if email service is configured
        print(f"📋 Email Service Configuration:")
        print(f"   SMTP Host: {email_service.smtp_host}")
        print(f"   SMTP Port: {email_service.smtp_port}")
        print(f"   SMTP Username: {email_service.smtp_username}")
        print(f"   SMTP Password: {'*' * len(email_service.smtp_password) if email_service.smtp_password else 'Not set'}")
        print(f"   From Email: {email_service.from_email}")
        print(f"   Is Configured: {email_service.is_configured}")
        
        if not email_service.is_configured:
            print("❌ Email service is not configured properly!")
            return False
        
        # Test sending approval email
        print(f"\n📧 Testing approval email to goutamramv@gmail.com...")
        
        success = await email_service.send_approval_notification(
            applicant_email="goutamramv@gmail.com",
            applicant_name="Goutam Vemula",
            property_name="Grand Plaza Hotel",
            position="Bartender",
            job_title="Bartender",
            start_date="February 15, 2025",
            pay_rate=20.00,
            onboarding_link="http://localhost:5173/onboarding/test-token-123",
            manager_name="Test Manager",
            manager_email="manager@hoteltest.com"
        )
        
        if success:
            print("✅ Approval email sent successfully!")
        else:
            print("❌ Failed to send approval email!")
            return False
        
        # Test sending rejection email
        print(f"\n📧 Testing rejection email to gvemula@mail.yu.edu...")
        
        success = await email_service.send_rejection_notification(
            applicant_email="gvemula@mail.yu.edu",
            applicant_name="Goutham Vemula",
            property_name="Grand Plaza Hotel",
            position="Housekeeper",
            manager_name="Test Manager",
            manager_email="manager@hoteltest.com"
        )
        
        if success:
            print("✅ Rejection email sent successfully!")
        else:
            print("❌ Failed to send rejection email!")
            return False
        
        print(f"\n🎉 All email tests passed!")
        print(f"📬 Check your email inboxes:")
        print(f"   • goutamramv@gmail.com (approval email)")
        print(f"   • gvemula@mail.yu.edu (rejection email)")
        
        return True
        
    except Exception as e:
        print(f"❌ Email service test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Direct Email Service Test")
    print("🎯 Testing SMTP configuration and email sending")
    print()
    
    success = asyncio.run(test_email_service())
    
    if success:
        print("\n🎉 SUCCESS! Email service is working correctly!")
        exit(0)
    else:
        print("\n💥 FAILED! Email service has issues")
        exit(1)

if __name__ == "__main__":
    main()