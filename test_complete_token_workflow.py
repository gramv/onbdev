#!/usr/bin/env python3
"""
Test Complete Token Workflow
Creates an onboarding session and tests the token-based welcome endpoint
"""
import requests
import json

def test_complete_token_workflow():
    """Test the complete workflow from application approval to token welcome"""
    print("🔄 Testing Complete Token Workflow")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    hr_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJyb2xlIjoiaHIiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzcyODAwMSwiZXhwIjoxNzUzODE0NDAxLCJqdGkiOiI3YjIxYmJiNy0zNDBiLTQ2ODQtOGNlZC03Y2IxNzMwYThhODcifQ.WODYfBAFgdoHZ6BVESzTQu2AGDUcFtwtpLbbryh1dKM"
    
    try:
        # Step 1: Get HR headers
        hr_headers = {"Authorization": f"Bearer {hr_token}"}
        
        # Step 2: Find an approved application or create one
        print("1. 🔍 Finding approved application...")
        apps_response = requests.get(f"{base_url}/hr/applications", headers=hr_headers)
        
        if apps_response.status_code != 200:
            print(f"❌ Failed to get applications: {apps_response.status_code}")
            return False
            
        applications = apps_response.json()
        approved_app = None
        
        for app in applications:
            if app.get("status") == "approved":
                approved_app = app
                break
        
        if not approved_app:
            print("⚠️  No approved applications found. Let me approve one...")
            # Get the first pending application and approve it
            pending_app = None
            for app in applications:
                if app.get("status") == "pending":
                    pending_app = app
                    break
            
            if not pending_app:
                print("❌ No applications found to approve")
                return False
            
            # Approve the application
            approve_response = requests.post(
                f"{base_url}/hr/applications/{pending_app['id']}/approve",
                headers=hr_headers,
                json={"notes": "Approved for testing"}
            )
            
            if approve_response.status_code == 200:
                approved_app = approve_response.json()
                print(f"✅ Approved application: {approved_app['applicant_data']['first_name']} {approved_app['applicant_data']['last_name']}")
            else:
                print(f"❌ Failed to approve application: {approve_response.status_code}")
                return False
        else:
            print(f"✅ Found approved application: {approved_app['applicant_data']['first_name']} {approved_app['applicant_data']['last_name']}")
        
        # Step 3: Initiate onboarding
        print("\n2. 🚀 Initiating onboarding...")
        initiate_response = requests.post(
            f"{base_url}/api/onboarding/initiate/{approved_app['id']}",
            headers=hr_headers
        )
        
        if initiate_response.status_code != 200:
            print(f"❌ Failed to initiate onboarding: {initiate_response.status_code}")
            print(f"   Response: {initiate_response.text}")
            return False
        
        onboarding_data = initiate_response.json()
        print(f"✅ Onboarding initiated successfully!")
        print(f"   📋 Full response: {json.dumps(onboarding_data, indent=2)}")
        
        onboarding_token = onboarding_data.get("token") or onboarding_data.get("onboarding_token")
        employee_id = onboarding_data.get("employee_id")
        
        print(f"   🎫 Token: {onboarding_token}")
        print(f"   👤 Employee ID: {employee_id}")
        
        # Step 4: Test the token-based welcome endpoint
        print("\n3. 🌟 Testing token-based welcome endpoint...")
        welcome_response = requests.get(f"{base_url}/api/onboarding/welcome/{onboarding_token}")
        
        if welcome_response.status_code == 200:
            print("✅ Token welcome endpoint working!")
            welcome_data = welcome_response.json()
            
            print(f"   👤 Employee: {welcome_data.get('employee', {}).get('name', 'N/A')}")
            print(f"   🏨 Property: {welcome_data.get('property', {}).get('name', 'N/A')}")
            print(f"   💼 Job Title: {welcome_data.get('job_details', {}).get('job_title', 'N/A')}")
            print(f"   📅 Start Date: {welcome_data.get('job_details', {}).get('start_date', 'N/A')}")
            print(f"   🎯 Status: {welcome_data.get('onboarding_info', {}).get('status', 'N/A')}")
            
            # Step 5: Test frontend URL
            print(f"\n4. 🌐 Frontend URL ready!")
            frontend_url = f"http://localhost:3000/onboarding/{onboarding_token}"
            print(f"   🔗 URL: {frontend_url}")
            
            # Test if frontend can access the data
            print("\n5. 🧪 Testing frontend accessibility...")
            frontend_response = requests.get(frontend_url)
            
            if frontend_response.status_code == 200:
                print("✅ Frontend URL is accessible!")
                content = frontend_response.text.lower()
                if "no routes matched" not in content:
                    print("✅ No routing errors detected!")
                    print("\n🎊 COMPLETE SUCCESS!")
                    print("=" * 60)
                    print("📋 RESULTS:")
                    print(f"   ✅ Application approved: {approved_app['first_name']} {approved_app['last_name']}")
                    print(f"   ✅ Onboarding initiated: {employee_id}")
                    print(f"   ✅ Token created: {onboarding_token}")
                    print(f"   ✅ API endpoint working: /api/onboarding/welcome/{onboarding_token}")
                    print(f"   ✅ Frontend URL working: {frontend_url}")
                    print()
                    print("🎯 NEXT STEPS:")
                    print(f"   1. Open: {frontend_url}")
                    print("   2. You should see the Task 3 welcome page with real data!")
                    print("   3. No more 'Preparing Your Welcome' loading screen!")
                    return True
                else:
                    print("⚠️  Frontend still has routing issues")
            else:
                print(f"⚠️  Frontend returned status: {frontend_response.status_code}")
            
        else:
            print(f"❌ Token welcome endpoint failed: {welcome_response.status_code}")
            print(f"   Response: {welcome_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Complete Token Workflow Test")
    print("🎯 Testing end-to-end token-based welcome page workflow")
    print()
    
    success = test_complete_token_workflow()
    
    if success:
        print("\n🎉 EXCELLENT! Complete workflow is working!")
        print("🌟 Your Task 3 welcome page should now load with real data!")
    else:
        print("\n💥 WORKFLOW FAILED! Check the errors above")

if __name__ == "__main__":
    main()