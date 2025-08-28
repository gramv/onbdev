#!/usr/bin/env python3
"""
Send Direct Approval Email
Directly sends an approval email to test the email service
"""
import sys
import os
import asyncio
import time

# Add the backend path to sys.path
sys.path.insert(0, 'hotel-onboarding-backend')

async def send_direct_approval_email():
    """Send approval email directly using the email service"""
    print("📧 SENDING DIRECT APPROVAL EMAIL")
    print("=" * 60)
    print("🎯 Target: goutamramv@gmail.com")
    print("🔗 Port: 3000 (corrected)")
    print("=" * 60)
    
    try:
        from app.email_service import email_service
        
        # Set environment variable
        os.environ['FRONTEND_URL'] = 'http://localhost:3000'
        
        # Generate unique identifier
        timestamp = int(time.time())
        unique_id = f"DIRECT{timestamp}"
        
        # Create onboarding link with correct port
        onboarding_token = f"direct-test-token-{timestamp}"
        onboarding_link = f"http://localhost:3000/onboarding/{onboarding_token}"
        
        print(f"\n📧 Sending direct approval email...")
        print(f"   🆔 Unique ID: {unique_id}")
        print(f"   🔗 Onboarding Link: {onboarding_link}")
        
        # Send approval email directly
        success = await email_service.send_approval_notification(
            applicant_email="goutamramv@gmail.com",
            applicant_name=f"DIRECT TEST {unique_id}",
            property_name="Grand Plaza Hotel",
            position="Test Position",
            job_title="Direct Email Test",
            start_date="February 15, 2025",
            pay_rate=25.00,
            onboarding_link=onboarding_link,
            manager_name="Test Manager",
            manager_email="manager@hoteltest.com"
        )
        
        if success:
            print(f"✅ DIRECT APPROVAL EMAIL SENT SUCCESSFULLY!")
            print(f"   📧 TO: goutamramv@gmail.com")
            print(f"   🆔 IDENTIFIER: {unique_id}")
            print(f"   🔗 ONBOARDING LINK: {onboarding_link}")
            print(f"   💼 POSITION: Direct Email Test")
            print(f"   💰 PAY: $25.00/hour")
            
            print(f"\n📬 CHECK YOUR EMAIL NOW!")
            print(f"   1. Go to goutamramv@gmail.com")
            print(f"   2. Look for email with '{unique_id}' in the content")
            print(f"   3. Subject should be: 'Congratulations! Job Offer from Grand Plaza Hotel'")
            print(f"   4. The onboarding link should use http://localhost:3000")
            print(f"   5. Click the link to test your Task 3 welcome page")
            
            return True
        else:
            print(f"❌ FAILED TO SEND EMAIL!")
            return False
            
    except Exception as e:
        print(f"❌ Direct email test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    print("🚀 Starting Direct Approval Email Test")
    print("📧 This will send an email directly using the email service")
    print()
    
    success = asyncio.run(send_direct_approval_email())
    
    if success:
        print("\n🎉 SUCCESS! Direct email sent!")
        print("📧 Check goutamramv@gmail.com for the approval email!")
        exit(0)
    else:
        print("\n💥 FAILED! Could not send direct email")
        exit(1)

if __name__ == "__main__":
    main()