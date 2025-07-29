#!/usr/bin/env python3
"""
Test Onboarding Email Workflow
Verify that onboarding emails are sent after application approval
"""
import asyncio
import sys
import os
sys.path.append('hotel-onboarding-backend')

from app.email_service import email_service
from app.supabase_service_enhanced import EnhancedSupabaseService
from app.services.onboarding_orchestrator import OnboardingOrchestrator
from app.models import JobApplication, ApplicationStatus
from datetime import datetime, timezone
import uuid

async def test_complete_approval_email_workflow():
    """Test the complete approval to onboarding email workflow"""
    
    print("🧪 Testing Complete Approval → Onboarding Email Workflow")
    print("=" * 60)
    
    # Initialize services
    supabase_service = EnhancedSupabaseService()
    await supabase_service.initialize()
    
    onboarding_orchestrator = OnboardingOrchestrator(supabase_service)
    
    try:
        # 1. Create test application
        print("\n1️⃣ Creating test application...")
        
        application_id = str(uuid.uuid4())
        test_application = JobApplication(
            id=application_id,
            property_id="prop_test_001",
            department="Front Desk",
            position="Front Desk Agent",
            applicant_data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "goutamramv@gmail.com",  # Using your email for testing
                "phone": "(555) 123-4567",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "zip_code": "90210"
            },
            status=ApplicationStatus.PENDING,
            applied_at=datetime.now(timezone.utc)
        )
        
        created_app = supabase_service.create_application_sync(test_application)
        print(f"✅ Test application created: {application_id}")
        
        # 2. Create employee record (simulating approval)
        print("\n2️⃣ Creating employee record...")
        
        employee_data = {
            "application_id": application_id,
            "property_id": "prop_test_001",
            "manager_id": "mgr_test_001",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "hire_date": "2024-02-01",
            "pay_rate": 18.50,
            "pay_frequency": "hourly",
            "employment_type": "full_time",
            "personal_info": {
                "job_title": "Front Desk Agent",
                "start_time": "9:00 AM",
                "benefits_eligible": "yes",
                "supervisor": "Mike Wilson",
                "special_instructions": "New hire orientation on first day"
            },
            "onboarding_status": "not_started"
        }
        
        employee = await supabase_service.create_employee(employee_data)
        print(f"✅ Employee record created: {employee.id}")
        
        # 3. Create onboarding session
        print("\n3️⃣ Creating onboarding session...")
        
        onboarding_session = await onboarding_orchestrator.initiate_onboarding(
            application_id=application_id,
            employee_id=employee.id,
            property_id="prop_test_001",
            manager_id="mgr_test_001",
            expires_hours=72
        )
        
        print(f"✅ Onboarding session created: {onboarding_session.id}")
        print(f"   Token: {onboarding_session.token}")
        print(f"   Expires: {onboarding_session.expires_at}")
        
        # 4. Generate onboarding URL
        print("\n4️⃣ Generating onboarding URL...")
        
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        onboarding_url = f"{base_url}/onboard?token={onboarding_session.token}"
        
        print(f"✅ Onboarding URL: {onboarding_url}")
        
        # 5. Get property and manager info for email
        print("\n5️⃣ Getting property and manager info...")
        
        property_obj = supabase_service.get_property_by_id_sync("prop_test_001")
        manager = supabase_service.get_user_by_id_sync("mgr_test_001")
        
        print(f"✅ Property: {property_obj.name}")
        print(f"✅ Manager: {manager.first_name} {manager.last_name} ({manager.email})")
        
        # 6. Send approval notification email
        print("\n6️⃣ Sending approval notification email...")
        
        approval_success = await email_service.send_approval_notification(
            applicant_email=test_application.applicant_data["email"],
            applicant_name=f"{test_application.applicant_data['first_name']} {test_application.applicant_data['last_name']}",
            property_name=property_obj.name,
            position=test_application.position,
            job_title=employee_data["position"],
            start_date=employee_data["hire_date"],
            pay_rate=employee_data["pay_rate"],
            onboarding_link=onboarding_url,
            manager_name=f"{manager.first_name} {manager.last_name}",
            manager_email=manager.email
        )
        
        if approval_success:
            print("✅ Approval notification email sent successfully!")
        else:
            print("❌ Failed to send approval notification email")
        
        # 7. Send onboarding welcome email
        print("\n7️⃣ Sending onboarding welcome email...")
        
        welcome_success = await email_service.send_onboarding_welcome_email(
            employee_email=test_application.applicant_data["email"],
            employee_name=f"{test_application.applicant_data['first_name']} {test_application.applicant_data['last_name']}",
            property_name=property_obj.name,
            position=employee_data["position"],
            onboarding_link=onboarding_url,
            manager_name=f"{manager.first_name} {manager.last_name}"
        )
        
        if welcome_success:
            print("✅ Onboarding welcome email sent successfully!")
        else:
            print("❌ Failed to send onboarding welcome email")
        
        # 8. Test results summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"Application Created: ✅")
        print(f"Employee Record: ✅")
        print(f"Onboarding Session: ✅")
        print(f"Approval Email: {'✅' if approval_success else '❌'}")
        print(f"Welcome Email: {'✅' if welcome_success else '❌'}")
        
        print(f"\n📧 Email Configuration Status:")
        print(f"   SMTP Configured: {'✅' if email_service.is_configured else '❌ (Dev Mode)'}")
        print(f"   SMTP Host: {email_service.smtp_host}")
        print(f"   From Email: {email_service.from_email}")
        
        print(f"\n🔗 Onboarding Details:")
        print(f"   Employee: {test_application.applicant_data['first_name']} {test_application.applicant_data['last_name']}")
        print(f"   Email: {test_application.applicant_data['email']}")
        print(f"   Position: {employee_data['position']}")
        print(f"   Property: {property_obj.name}")
        print(f"   Onboarding URL: {onboarding_url}")
        print(f"   Token: {onboarding_session.token}")
        print(f"   Expires: {onboarding_session.expires_at}")
        
        return {
            "approval_email_sent": approval_success,
            "welcome_email_sent": welcome_success,
            "onboarding_url": onboarding_url,
            "token": onboarding_session.token,
            "employee_id": employee.id,
            "session_id": onboarding_session.id
        }
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_email_integration_in_approval_endpoint():
    """Test if the approval endpoint should be sending emails"""
    
    print("\n🔍 CHECKING APPROVAL ENDPOINT EMAIL INTEGRATION")
    print("=" * 60)
    
    # Read the current approval endpoint
    try:
        with open('hotel-onboarding-backend/app/main_enhanced.py', 'r') as f:
            content = f.read()
        
        # Check for email sending in approval endpoint
        has_email_import = 'email_service' in content
        has_approval_email = 'send_approval_notification' in content
        has_welcome_email = 'send_onboarding_welcome_email' in content
        
        print(f"Email Service Import: {'✅' if has_email_import else '❌'}")
        print(f"Approval Email Call: {'✅' if has_approval_email else '❌'}")
        print(f"Welcome Email Call: {'✅' if has_welcome_email else '❌'}")
        
        if not has_email_import:
            print("\n⚠️  ISSUE: Email service not imported in main_enhanced.py")
        
        if not has_approval_email:
            print("\n⚠️  ISSUE: Approval endpoint not sending approval notification email")
        
        if not has_welcome_email:
            print("\n⚠️  ISSUE: Approval endpoint not sending onboarding welcome email")
        
        return {
            "has_email_import": has_email_import,
            "has_approval_email": has_approval_email,
            "has_welcome_email": has_welcome_email
        }
        
    except Exception as e:
        print(f"❌ Failed to check approval endpoint: {e}")
        return None

if __name__ == "__main__":
    async def main():
        # Test the complete workflow
        workflow_result = await test_complete_approval_email_workflow()
        
        # Check endpoint integration
        endpoint_check = await test_email_integration_in_approval_endpoint()
        
        print("\n" + "=" * 60)
        print("🎯 FINAL RECOMMENDATIONS")
        print("=" * 60)
        
        if endpoint_check and not endpoint_check["has_email_import"]:
            print("1. Add email service import to main_enhanced.py")
        
        if endpoint_check and not endpoint_check["has_approval_email"]:
            print("2. Add approval notification email to approval endpoint")
        
        if endpoint_check and not endpoint_check["has_welcome_email"]:
            print("3. Add onboarding welcome email to approval endpoint")
        
        if workflow_result:
            print("4. Email workflow tested successfully - ready for integration")
        else:
            print("4. Email workflow needs debugging")
    
    asyncio.run(main())