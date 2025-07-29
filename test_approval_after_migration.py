#!/usr/bin/env python3

import requests
import json
import time

def test_approval_after_migration():
    """Test approval functionality after complete Supabase migration"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Approval After Complete Supabase Migration")
    print("=" * 60)
    
    # Step 1: Get current applications
    print("\n1️⃣ Getting current applications...")
    try:
        response = requests.get(f"{base_url}/api/applications")
        if response.status_code == 200:
            applications = response.json()
            print(f"✅ Found {len(applications)} applications")
            
            # Find a pending application
            pending_apps = [app for app in applications if app.get('status') == 'pending']
            if not pending_apps:
                print("❌ No pending applications found. Creating one...")
                
                # Create a test application
                test_app = {
                    "first_name": "Migration",
                    "last_name": "Test",
                    "email": f"migration.test.{int(time.time())}@example.com",
                    "phone": "555-0123",
                    "position": "Front Desk",
                    "property_id": "prop_001",
                    "availability": "Full-time",
                    "experience": "2 years hotel experience"
                }
                
                create_response = requests.post(f"{base_url}/api/applications", json=test_app)
                if create_response.status_code == 201:
                    app_data = create_response.json()
                    app_id = app_data['id']
                    print(f"✅ Created test application: {app_id}")
                else:
                    print(f"❌ Failed to create application: {create_response.status_code}")
                    return False
            else:
                app_id = pending_apps[0]['id']
                print(f"✅ Using pending application: {app_id}")
        else:
            print(f"❌ Failed to get applications: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting applications: {e}")
        return False
    
    # Step 2: Test approval
    print(f"\n2️⃣ Testing approval for application {app_id}...")
    try:
        approval_data = {
            "status": "approved",
            "notes": "Approved after Supabase migration test"
        }
        
        response = requests.put(f"{base_url}/api/applications/{app_id}/approve", json=approval_data)
        print(f"📤 Approval request status: {response.status_code}")
        print(f"📤 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Approval successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Approval failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during approval: {e}")
        return False

if __name__ == "__main__":
    success = test_approval_after_migration()
    if success:
        print("\n🎉 Migration test PASSED - Approval working with Supabase!")
    else:
        print("\n❌ Migration test FAILED - Need to investigate further")