#!/usr/bin/env python3

import requests
import json

def simulate_browser_behavior():
    """Simulate exactly what the browser/frontend does"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🌐 Simulating Browser/Frontend Behavior")
    print("=" * 50)
    
    # Step 1: Login exactly like frontend
    print("\n1. 🔐 Frontend login simulation...")
    login_payload = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    login_response = requests.post(
        f"{base_url}/auth/login",
        json=login_payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    login_data = login_response.json()
    token = login_data["token"]
    user_role = login_data.get("user", {}).get("role")
    
    print(f"✅ Login successful")
    print(f"   Role: {user_role}")
    print(f"   Token: {token[:30]}...")
    
    # Step 2: Fetch applications exactly like frontend
    print(f"\n2. 📋 Fetching applications (frontend style)...")
    
    # This is exactly what the frontend does
    endpoint = f"{base_url}/manager/applications" if user_role == "manager" else f"{base_url}/hr/applications"
    
    apps_response = requests.get(
        endpoint,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        },
        params={
            # These are the default params the frontend might send
            "search": None,
            "status": None,
            "department": None,
            "property_id": None
        }
    )
    
    print(f"Applications fetch status: {apps_response.status_code}")
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to fetch applications: {apps_response.text}")
        return False
    
    applications = apps_response.json()
    pending_apps = [app for app in applications if app.get("status") == "pending"]
    
    print(f"✅ Found {len(applications)} total applications")
    print(f"   Pending: {len(pending_apps)}")
    
    if not pending_apps:
        print("⚠️  No pending applications found. Creating one...")
        
        # Create a test application
        property_id = "prop_test_001"
        app_data = {
            "first_name": "Browser",
            "last_name": "Simulation",
            "email": "browser.simulation@example.com",
            "phone": "(555) 222-3333",
            "address": "222 Browser St",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-09-10",
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "2-5",
            "hotel_experience": "yes"
        }
        
        create_response = requests.post(f"{base_url}/apply/{property_id}", json=app_data)
        
        if create_response.status_code != 200:
            print(f"❌ Failed to create application: {create_response.status_code}")
            return False
        
        new_app_id = create_response.json()["application_id"]
        print(f"✅ Created application: {new_app_id}")
        
        # Refetch applications
        apps_response = requests.get(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
        )
        
        if apps_response.status_code == 200:
            applications = apps_response.json()
            pending_apps = [app for app in applications if app.get("status") == "pending"]
    
    if not pending_apps:
        print("❌ Still no pending applications")
        return False
    
    target_app = pending_apps[0]
    app_id = target_app["id"]
    
    print(f"✅ Using application: {app_id}")
    print(f"   Name: {target_app.get('applicant_data', {}).get('first_name')} {target_app.get('applicant_data', {}).get('last_name')}")
    print(f"   Status: {target_app.get('status')}")
    
    # Step 3: Simulate frontend approval exactly
    print(f"\n3. ✅ Simulating frontend approval...")
    
    # This is exactly what the frontend jobOfferData contains
    job_offer_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-09-10",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Mike Wilson",
        "special_instructions": "Browser simulation test"
    }
    
    print("Job offer data:")
    for key, value in job_offer_data.items():
        print(f"   {key}: '{value}' (type: {type(value).__name__})")
    
    # Simulate FormData creation (this is what happens in the browser)
    # Object.entries(jobOfferData).forEach(([key, value]) => { formData.append(key, value) })
    
    # Test with requests.post using data= (which simulates FormData)
    approval_response = requests.post(
        f"{base_url}/applications/{app_id}/approve",
        data=job_offer_data,  # This is what FormData becomes
        headers={
            "Authorization": f"Bearer {token}",
            # Note: When using FormData, the browser sets Content-Type automatically
            # We don't set it here to let requests handle it
        }
    )
    
    print(f"\nApproval response:")
    print(f"   Status: {approval_response.status_code}")
    print(f"   Headers: {dict(approval_response.headers)}")
    
    if approval_response.status_code == 200:
        print("✅ Approval successful!")
        response_data = approval_response.json()
        print(f"   Employee ID: {response_data.get('employee_id')}")
        print(f"   Message: {response_data.get('message')}")
        return True
    else:
        print("❌ Approval failed!")
        
        # Detailed error analysis
        print(f"   Response text: {approval_response.text}")
        
        try:
            error_data = approval_response.json()
            print(f"   Error JSON: {json.dumps(error_data, indent=4)}")
            
            if 'detail' in error_data and isinstance(error_data['detail'], list):
                print("\n   Validation errors:")
                for error in error_data['detail']:
                    loc = error.get('loc', [])
                    msg = error.get('msg', 'Unknown error')
                    input_val = error.get('input', 'N/A')
                    error_type = error.get('type', 'unknown')
                    
                    print(f"     - Location: {' -> '.join(str(x) for x in loc)}")
                    print(f"       Type: {error_type}")
                    print(f"       Message: {msg}")
                    print(f"       Input: {input_val}")
        except Exception as e:
            print(f"   JSON parse error: {e}")
        
        return False

def test_with_different_content_types():
    """Test with different content types to see if that's the issue"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("\n🧪 Testing Different Content Types")
    print("=" * 40)
    
    # Login
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()["token"]
    
    # Get a pending application or create one
    apps_response = requests.get(f"{base_url}/manager/applications", 
                                headers={"Authorization": f"Bearer {token}"})
    
    if apps_response.status_code != 200:
        print("❌ Failed to get applications")
        return
    
    applications = apps_response.json()
    pending_apps = [app for app in applications if app.get("status") == "pending"]
    
    if not pending_apps:
        print("⚠️  No pending applications for content type test")
        return
    
    app_id = pending_apps[0]["id"]
    
    job_data = {
        "job_title": "Front Desk Agent",
        "start_date": "2025-09-15",
        "start_time": "09:00",
        "pay_rate": "18.50",
        "pay_frequency": "bi-weekly",
        "benefits_eligible": "yes",
        "supervisor": "Mike Wilson",
        "special_instructions": "Content type test"
    }
    
    test_cases = [
        {
            "name": "Form data (default)",
            "method": lambda: requests.post(
                f"{base_url}/applications/{app_id}/approve",
                data=job_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        },
        {
            "name": "Form data with explicit content-type",
            "method": lambda: requests.post(
                f"{base_url}/applications/{app_id}/approve",
                data=job_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
        },
        {
            "name": "JSON data",
            "method": lambda: requests.post(
                f"{base_url}/applications/{app_id}/approve",
                json=job_data,
                headers={"Authorization": f"Bearer {token}"}
            )
        }
    ]
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        
        try:
            response = test_case['method']()
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Success!")
                break
            else:
                try:
                    error = response.json()
                    if 'detail' in error:
                        print(f"   ❌ Error: {error['detail']}")
                    else:
                        print(f"   ❌ Error: {error}")
                except:
                    print(f"   ❌ Raw: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Browser Simulation Debug")
    print("=" * 60)
    
    success = simulate_browser_behavior()
    
    if not success:
        test_with_different_content_types()
    
    if success:
        print("\n🎉 Browser simulation successful!")
        print("The backend is working correctly.")
        print("If frontend is still failing, check:")
        print("1. Browser console for JavaScript errors")
        print("2. Network tab for actual request details")
        print("3. Token validity in frontend")
        print("4. Application data freshness")
    else:
        print("\n💥 Browser simulation failed")
        print("There might be a deeper backend issue")