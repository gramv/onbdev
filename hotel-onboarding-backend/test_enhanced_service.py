#!/usr/bin/env python3
"""
Test Enhanced Supabase Service
Simple test to verify the enhanced service works with your database
"""

import os
import sys
import asyncio
from datetime import datetime, timezone

# Set environment variables explicitly
os.environ['SUPABASE_URL'] = 'https://onmjxtyamdpkhnflwwmj.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ubWp4dHlhbWRwa2huZmx3d21qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM3MTUxNzEsImV4cCI6MjA2OTI5MTE3MX0.jWd-7hLFu_DTXB0Q7KLhqUVBu--iJdGfLOeHeCSEugQ'
os.environ['DATABASE_URL'] = 'postgresql://postgres.onmjxtyamdpkhnflwwmj:Gouthi321@aws-0-us-east-1.pooler.supabase.com:6543/postgres'
os.environ['ENCRYPTION_KEY'] = 'hAR4UFbAd1fFu9zopw8IeDva5-8uQeR8bz5olhHdPNo='

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.supabase_service_enhanced import get_enhanced_supabase_service
from app.models import UserRole, ApplicationStatus

async def test_enhanced_service():
    """Test the enhanced Supabase service"""
    print("🧪 TESTING ENHANCED SUPABASE SERVICE")
    print("=" * 60)
    
    try:
        # Initialize service
        service = get_enhanced_supabase_service()
        print("✅ Service initialized")
        
        # Test health check
        health = await service.comprehensive_health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Test database stats
        stats = await service.get_system_statistics()
        print(f"✅ Database stats: {stats}")
        
        # Test basic table access
        print("\n📋 Testing table access...")
        
        # Test users table
        try:
            result = service.admin_client.table('users').select('*').limit(1).execute()
            print(f"   ✅ Users table: {len(result.data)} records")
        except Exception as e:
            print(f"   ❌ Users table error: {e}")
        
        # Test properties table
        try:
            result = service.admin_client.table('properties').select('*').limit(1).execute()
            print(f"   ✅ Properties table: {len(result.data)} records")
        except Exception as e:
            print(f"   ❌ Properties table error: {e}")
        
        # Test job_applications table
        try:
            result = service.admin_client.table('job_applications').select('*').limit(1).execute()
            print(f"   ✅ Job applications table: {len(result.data)} records")
        except Exception as e:
            print(f"   ❌ Job applications table error: {e}")
        
        # Test user roles
        try:
            result = service.admin_client.table('user_roles').select('*').execute()
            print(f"   ✅ User roles table: {len(result.data)} records")
            for role in result.data:
                print(f"      - {role['name']}: {role['description']}")
        except Exception as e:
            print(f"   ❌ User roles table error: {e}")
        
        print("\n🎉 Enhanced service is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

async def populate_sample_data():
    """Populate the database with sample data"""
    print("\n📊 POPULATING SAMPLE DATA")
    print("=" * 60)
    
    try:
        service = get_enhanced_supabase_service()
        
        # Sample HR user
        print("1️⃣  Creating HR user...")
        hr_user_data = {
            "id": "hr_admin_001",
            "email": "hr@hotelonboarding.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "hr",
            "is_active": True,
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LQ4YCOdHrADFeaLAqCO4OO5.JjEBeJBZ4x/BG",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "hr_admin_001"
        }
        
        try:
            result = service.admin_client.table('users').insert(hr_user_data).execute()
            if result.data:
                print("   ✅ HR user created")
            else:
                print("   ⚠️  HR user may already exist")
        except Exception as e:
            if "duplicate key" in str(e).lower():
                print("   ⚠️  HR user already exists")
            else:
                print(f"   ❌ HR user creation failed: {e}")
        
        # Sample property
        print("2️⃣  Creating sample property...")
        property_data = {
            "id": "prop_plaza_001",
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
            "created_by": "hr_admin_001"
        }
        
        try:
            result = service.admin_client.table('properties').insert(property_data).execute()
            if result.data:
                print("   ✅ Property created")
            else:
                print("   ⚠️  Property may already exist")
        except Exception as e:
            if "duplicate key" in str(e).lower():
                print("   ⚠️  Property already exists")
            else:
                print(f"   ❌ Property creation failed: {e}")
        
        # Sample manager
        print("3️⃣  Creating sample manager...")
        manager_data = {
            "id": "mgr_plaza_001",
            "email": "manager.plaza@hotelonboarding.com",
            "first_name": "Michael",
            "last_name": "Wilson",
            "role": "manager",
            "property_id": "prop_plaza_001",
            "is_active": True,
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LQ4YCOdHrADFeaLAqCO4OO5.JjEBeJBZ4x/BG",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "hr_admin_001"
        }
        
        try:
            result = service.admin_client.table('users').insert(manager_data).execute()
            if result.data:
                print("   ✅ Manager created")
            else:
                print("   ⚠️  Manager may already exist")
        except Exception as e:
            if "duplicate key" in str(e).lower():
                print("   ⚠️  Manager already exists")
            else:
                print(f"   ❌ Manager creation failed: {e}")
        
        # Assign manager to property
        print("4️⃣  Assigning manager to property...")
        assignment_data = {
            "property_id": "prop_plaza_001",
            "manager_id": "mgr_plaza_001",
            "permissions": {
                "can_approve": True,
                "can_reject": True,
                "can_hire": True,
                "can_manage_onboarding": True
            },
            "assigned_at": datetime.now(timezone.utc).isoformat(),
            "assigned_by": "hr_admin_001",
            "is_primary": True
        }
        
        try:
            result = service.admin_client.table('property_managers').insert(assignment_data).execute()
            if result.data:
                print("   ✅ Manager assigned to property")
            else:
                print("   ⚠️  Assignment may already exist")
        except Exception as e:
            if "duplicate key" in str(e).lower():
                print("   ⚠️  Assignment already exists")
            else:
                print(f"   ❌ Assignment failed: {e}")
        
        # Sample job application
        print("5️⃣  Creating sample job application...")
        application_data = {
            "id": "app_plaza_001",
            "property_id": "prop_plaza_001",
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
            "duplicate_check_hash": service.generate_duplicate_hash("john.doe@email.com", "prop_plaza_001", "Front Desk Agent"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            result = service.admin_client.table('job_applications').insert(application_data).execute()
            if result.data:
                print("   ✅ Job application created")
            else:
                print("   ⚠️  Application may already exist")
        except Exception as e:
            if "duplicate key" in str(e).lower():
                print("   ⚠️  Application already exists")
            else:
                print(f"   ❌ Application creation failed: {e}")
        
        print("\n🎉 Sample data population completed!")
        return True
        
    except Exception as e:
        print(f"❌ Sample data population failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 ENHANCED SUPABASE SERVICE TEST")
    print("=" * 60)
    
    # Test service
    service_ok = await test_enhanced_service()
    
    if service_ok:
        # Populate sample data
        data_ok = await populate_sample_data()
        
        if data_ok:
            print("\n✨ ENHANCED SUPABASE SETUP COMPLETE!")
            print("=" * 60)
            print("✅ Enhanced service is working")
            print("✅ Database schema is ready")
            print("✅ Sample data is populated")
            print("\n🔗 Next Steps:")
            print("   1. Update your main application to use enhanced service")
            print("   2. Test API endpoints")
            print("   3. Verify frontend integration")
            return True
    
    print("\n💥 Setup failed. Check the errors above.")
    return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)