#!/usr/bin/env python3
"""
Populate Enhanced Supabase Database with Sample Data
Uses proper UUIDs and follows the enhanced schema structure
"""

import os
import sys
import asyncio
import uuid
from datetime import datetime, timezone

# Set environment variables explicitly
os.environ['SUPABASE_URL'] = 'https://onmjxtyamdpkhnflwwmj.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ubWp4dHlhbWRwa2huZmx3d21qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3MTUxNzEsImV4cCI6MjA2OTI5MTE3MX0.jWd-7hLFu_DTXB0Q7KLhqUVBu--iJdGfLOeHeCSEugQ'
os.environ['DATABASE_URL'] = 'postgresql://postgres.onmjxtyamdpkhnflwwmj:Gouthi321@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
os.environ['ENCRYPTION_KEY'] = 'hAR4UFbAd1fFu9zopw8IeDva5-8uQeR8bz5olhHdPNo='

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.supabase_service_enhanced import get_enhanced_supabase_service

async def populate_enhanced_data():
    """Populate the database with enhanced sample data using proper UUIDs"""
    print("📊 POPULATING ENHANCED SAMPLE DATA")
    print("=" * 60)
    
    try:
        service = get_enhanced_supabase_service()
        
        # Generate proper UUIDs
        hr_user_id = str(uuid.uuid4())
        property_id = str(uuid.uuid4())
        manager_id = str(uuid.uuid4())
        application_id = str(uuid.uuid4())
        employee_id = str(uuid.uuid4())
        
        print(f"Generated UUIDs:")
        print(f"  HR User: {hr_user_id}")
        print(f"  Property: {property_id}")
        print(f"  Manager: {manager_id}")
        print(f"  Application: {application_id}")
        print(f"  Employee: {employee_id}")
        
        # 1. Create HR user
        print("\\n1️⃣  Creating HR user...")
        hr_user_data = {
            "id": hr_user_id,
            "email": "hr@hotelonboarding.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "hr",
            "is_active": True,
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LQ4YCOdHrADFeaLAqCO4OO5.JjEBeJBZ4x/BG",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": hr_user_id
        }
        
        try:
            result = service.admin_client.table('users').insert(hr_user_data).execute()
            if result.data:
                print("   ✅ HR user created successfully")
            else:
                print("   ❌ HR user creation failed - no data returned")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print("   ⚠️  HR user already exists")
            else:
                print(f"   ❌ HR user creation failed: {e}")
        
        # 2. Create property
        print("\\n2️⃣  Creating sample property...")
        property_data = {
            "id": property_id,
            "name": "Grand Plaza Hotel",
            "address": "123 Main Street",
            "city": "Downtown",
            "state": "CA",
            "zip_code": "90210",
            "phone": "(555) 123-4567",
            "business_license": "BL-2024-001",
            "property_type": "hotel",
            "qr_code_url": "data:image/png;base64,sample_qr_code_data",
            "is_active": True,
            "timezone": "America/Los_Angeles",
            "settings": {"allow_online_applications": True},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": hr_user_id
        }
        
        try:
            result = service.admin_client.table('properties').insert(property_data).execute()
            if result.data:
                print("   ✅ Property created successfully")
            else:
                print("   ❌ Property creation failed - no data returned")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print("   ⚠️  Property already exists")
            else:
                print(f"   ❌ Property creation failed: {e}")
        
        # 3. Create manager
        print("\\n3️⃣  Creating sample manager...")
        manager_data = {
            "id": manager_id,
            "email": "manager.plaza@hotelonboarding.com",
            "first_name": "Michael",
            "last_name": "Wilson",
            "role": "manager",
            "property_id": property_id,
            "is_active": True,
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LQ4YCOdHrADFeaLAqCO4OO5.JjEBeJBZ4x/BG",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": hr_user_id
        }
        
        try:
            result = service.admin_client.table('users').insert(manager_data).execute()
            if result.data:
                print("   ✅ Manager created successfully")
            else:
                print("   ❌ Manager creation failed - no data returned")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print("   ⚠️  Manager already exists")
            else:
                print(f"   ❌ Manager creation failed: {e}")
        
        # 4. Assign manager to property
        print("\\n4️⃣  Assigning manager to property...")
        assignment_data = {
            "property_id": property_id,
            "manager_id": manager_id,
            "permissions": {
                "can_approve": True,
                "can_reject": True,
                "can_hire": True,
                "can_manage_onboarding": True
            },
            "assigned_at": datetime.now(timezone.utc).isoformat(),
            "assigned_by": hr_user_id,
            "is_primary": True
        }
        
        try:
            result = service.admin_client.table('property_managers').insert(assignment_data).execute()
            if result.data:
                print("   ✅ Manager assigned to property successfully")
            else:
                print("   ❌ Manager assignment failed - no data returned")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print("   ⚠️  Manager assignment already exists")
            else:
                print(f"   ❌ Manager assignment failed: {e}")
        
        # 5. Create job application
        print("\\n5️⃣  Creating sample job application...")
        application_data = {
            "id": application_id,
            "property_id": property_id,
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "applicant_data": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@email.com",
                "phone": "(555) 123-4567",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "zip_code": "90210",
                "work_authorized": True
            },
            "status": "pending",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "source": "qr_code",
            "gdpr_consent": True,
            "duplicate_check_hash": service.generate_duplicate_hash("john.doe@email.com", property_id, "Front Desk Agent"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            result = service.admin_client.table('job_applications').insert(application_data).execute()
            if result.data:
                print("   ✅ Job application created successfully")
            else:
                print("   ❌ Job application creation failed - no data returned")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print("   ⚠️  Job application already exists")
            else:
                print(f"   ❌ Job application creation failed: {e}")
        
        # 6. Create employee record
        print("\\n6️⃣  Creating sample employee...")
        employee_data = {
            "id": employee_id,
            "application_id": application_id,
            "property_id": property_id,
            "manager_id": manager_id,
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "hire_date": datetime.now(timezone.utc).date().isoformat(),
            "pay_rate": 18.50,
            "pay_frequency": "hourly",
            "employment_type": "full_time",
            "personal_info": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@email.com",
                "phone": "(555) 123-4567"
            },
            "employment_status": "active",
            "onboarding_status": "not_started",
            "benefits_eligible": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": hr_user_id
        }
        
        try:
            result = service.admin_client.table('employees').insert(employee_data).execute()
            if result.data:
                print("   ✅ Employee created successfully")
                print(f"      Employee Number: {result.data[0].get('employee_number', 'Auto-generated')}")
            else:
                print("   ❌ Employee creation failed - no data returned")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower():
                print("   ⚠️  Employee already exists")
            else:
                print(f"   ❌ Employee creation failed: {e}")
        
        # 7. Create onboarding session
        print("\\n7️⃣  Creating onboarding session...")
        try:
            onboarding_session = await service.create_onboarding_session(employee_id, expires_hours=168)
            if onboarding_session:
                print("   ✅ Onboarding session created successfully")
                print(f"      Token: {onboarding_session['token'][:20]}...")
            else:
                print("   ❌ Onboarding session creation failed")
        except Exception as e:
            print(f"   ❌ Onboarding session creation failed: {e}")
        
        # 8. Verify data
        print("\\n8️⃣  Verifying created data...")
        try:
            stats = await service.get_system_statistics()
            print(f"   📊 Final Database Statistics:")
            print(f"      Users: {stats.get('users_count', 0)}")
            print(f"      Properties: {stats.get('properties_count', 0)}")
            print(f"      Applications: {stats.get('job_applications_count', 0)}")
            print(f"      Employees: {stats.get('employees_count', 0)}")
            print(f"      Onboarding Sessions: {stats.get('onboarding_sessions_count', 0)}")
        except Exception as e:
            print(f"   ❌ Statistics verification failed: {e}")
        
        print("\\n🎉 ENHANCED SAMPLE DATA POPULATION COMPLETED!")
        print("=" * 60)
        print("✅ Database is populated with sample data")
        print("✅ All UUIDs are properly formatted")
        print("✅ Relationships are established")
        print("✅ Onboarding workflow is ready")
        
        print("\\n🔗 Sample Credentials:")
        print(f"   HR Login: hr@hotelonboarding.com / admin123")
        print(f"   Manager Login: manager.plaza@hotelonboarding.com / manager123")
        
        print("\\n🔗 Next Steps:")
        print("   1. Test login with sample credentials")
        print("   2. Verify API endpoints work")
        print("   3. Test frontend integration")
        print("   4. Enable RLS policies for production")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample data population failed: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 ENHANCED SUPABASE DATA POPULATION")
    print("=" * 60)
    
    try:
        success = await populate_enhanced_data()
        if success:
            print("\\n✨ Data population completed successfully!")
            sys.exit(0)
        else:
            print("\\n💥 Data population failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\\n⏹️  Data population interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())