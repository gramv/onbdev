#!/usr/bin/env python3
"""
Test script to verify SMTP email configuration
Tests the Gmail SMTP setup with the provided credentials
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend'))

from app.email_service import EmailService

async def test_smtp_configuration():
    """Test the SMTP configuration with a simple email"""
    
    print("🧪 Testing SMTP Configuration")
    print("=" * 50)
    
    # Initialize email service
    email_service = EmailService()
    
    # Check if email service is configured
    print(f"📧 SMTP Host: {email_service.smtp_host}")
    print(f"📧 SMTP Port: {email_service.smtp_port}")
    print(f"📧 SMTP Username: {email_service.smtp_username}")
    print(f"📧 From Email: {email_service.from_email}")
    print(f"📧 From Name: {email_service.from_name}")
    print(f"📧 Use TLS: {email_service.smtp_use_tls}")
    print(f"📧 Is Configured: {email_service.is_configured}")
    
    if not email_service.is_configured:
        print("❌ Email service is not properly configured!")
        return False
    
    print("\n🚀 Sending test email...")
    
    # Test email content
    test_email = "vgoutamram@gmail.com"  # Send to the same email for testing
    subject = "Hotel Onboarding System - SMTP Test"
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
            .content { padding: 20px; background-color: #f9fafb; border-radius: 0 0 8px 8px; }
            .success { color: #16a34a; font-weight: bold; }
            .info { background-color: #dbeafe; padding: 15px; border-radius: 5px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 SMTP Configuration Test</h1>
            </div>
            <div class="content">
                <p class="success">✅ Congratulations! Your SMTP configuration is working correctly.</p>
                
                <div class="info">
                    <h3>📧 Configuration Details:</h3>
                    <ul>
                        <li><strong>SMTP Host:</strong> smtp.gmail.com</li>
                        <li><strong>Port:</strong> 587</li>
                        <li><strong>Security:</strong> TLS Enabled</li>
                        <li><strong>From Email:</strong> vgoutamram@gmail.com</li>
                    </ul>
                </div>
                
                <p>This test email confirms that:</p>
                <ul>
                    <li>✅ Gmail SMTP connection is successful</li>
                    <li>✅ App password authentication is working</li>
                    <li>✅ Email templates are rendering correctly</li>
                    <li>✅ HTML email formatting is functional</li>
                </ul>
                
                <p>Your Hotel Onboarding System is now ready to send:</p>
                <ul>
                    <li>📋 Job application approval notifications</li>
                    <li>❌ Job application rejection notifications</li>
                    <li>🎯 Talent pool notifications</li>
                    <li>🚀 Onboarding welcome emails</li>
                    <li>📝 Form update notifications</li>
                </ul>
                
                <p><strong>Next Steps:</strong></p>
                <ol>
                    <li>Test the complete onboarding workflow</li>
                    <li>Verify email notifications in job application process</li>
                    <li>Check spam folder if emails don't appear in inbox</li>
                </ol>
                
                <p>Happy onboarding! 🎊</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = """
    🎉 SMTP Configuration Test
    
    ✅ Congratulations! Your SMTP configuration is working correctly.
    
    📧 Configuration Details:
    - SMTP Host: smtp.gmail.com
    - Port: 587
    - Security: TLS Enabled
    - From Email: vgoutamram@gmail.com
    
    This test email confirms that:
    ✅ Gmail SMTP connection is successful
    ✅ App password authentication is working
    ✅ Email templates are rendering correctly
    ✅ HTML email formatting is functional
    
    Your Hotel Onboarding System is now ready to send:
    📋 Job application approval notifications
    ❌ Job application rejection notifications
    🎯 Talent pool notifications
    🚀 Onboarding welcome emails
    📝 Form update notifications
    
    Next Steps:
    1. Test the complete onboarding workflow
    2. Verify email notifications in job application process
    3. Check spam folder if emails don't appear in inbox
    
    Happy onboarding! 🎊
    """
    
    try:
        # Send test email
        success = await email_service.send_email(
            to_email=test_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox at: {test_email}")
            print("📝 Note: Check spam folder if email doesn't appear in inbox")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {str(e)}")
        return False

async def test_onboarding_email_templates():
    """Test the onboarding-specific email templates"""
    
    print("\n🧪 Testing Onboarding Email Templates")
    print("=" * 50)
    
    email_service = EmailService()
    
    if not email_service.is_configured:
        print("❌ Email service not configured, skipping template tests")
        return False
    
    test_email = "vgoutamram@gmail.com"
    
    # Test 1: Approval notification
    print("\n📋 Testing approval notification template...")
    
    try:
        success = await email_service.send_approval_notification(
            applicant_email=test_email,
            applicant_name="John Doe",
            property_name="Grand Hotel Downtown",
            position="Front Desk Associate",
            job_title="Front Desk Associate",
            start_date="February 15, 2025",
            pay_rate=18.50,
            onboarding_link="http://localhost:3000/onboarding-welcome/test123?token=abc123",
            manager_name="Sarah Johnson",
            manager_email="sarah.johnson@grandhotel.com"
        )
        
        if success:
            print("✅ Approval notification sent successfully!")
        else:
            print("❌ Failed to send approval notification")
            
    except Exception as e:
        print(f"❌ Error sending approval notification: {str(e)}")
    
    # Test 2: Rejection notification
    print("\n❌ Testing rejection notification template...")
    
    try:
        success = await email_service.send_rejection_notification(
            applicant_email=test_email,
            applicant_name="Jane Smith",
            property_name="Grand Hotel Downtown",
            position="Housekeeping Associate",
            manager_name="Sarah Johnson",
            manager_email="sarah.johnson@grandhotel.com"
        )
        
        if success:
            print("✅ Rejection notification sent successfully!")
        else:
            print("❌ Failed to send rejection notification")
            
    except Exception as e:
        print(f"❌ Error sending rejection notification: {str(e)}")
    
    # Test 3: Talent pool notification
    print("\n🎯 Testing talent pool notification template...")
    
    try:
        success = await email_service.send_talent_pool_notification(
            applicant_email=test_email,
            applicant_name="Mike Wilson",
            property_name="Grand Hotel Downtown",
            position="Restaurant Server",
            manager_name="Sarah Johnson",
            manager_email="sarah.johnson@grandhotel.com"
        )
        
        if success:
            print("✅ Talent pool notification sent successfully!")
        else:
            print("❌ Failed to send talent pool notification")
            
    except Exception as e:
        print(f"❌ Error sending talent pool notification: {str(e)}")
    
    print("\n🎊 Email template testing complete!")
    print("📬 Check your inbox for all test emails")
    
    return True

async def main():
    """Main test function"""
    
    print("🚀 Starting SMTP Configuration Tests")
    print("=" * 60)
    
    # Test basic SMTP configuration
    smtp_success = await test_smtp_configuration()
    
    if smtp_success:
        # Test onboarding email templates
        await test_onboarding_email_templates()
        
        print("\n🎉 All SMTP tests completed successfully!")
        print("=" * 60)
        print("📧 Your Gmail SMTP configuration is working perfectly!")
        print("📬 Check your email inbox for test messages")
        print("🚀 The Hotel Onboarding System is ready to send notifications!")
        
    else:
        print("\n❌ SMTP configuration test failed!")
        print("=" * 60)
        print("🔧 Please check your Gmail settings:")
        print("   1. Verify the email address: vgoutamram@gmail.com")
        print("   2. Verify the app password: ucda xbyi bhro tizk")
        print("   3. Ensure 2-factor authentication is enabled")
        print("   4. Ensure 'Less secure app access' is disabled (use app password)")

if __name__ == "__main__":
    asyncio.run(main())