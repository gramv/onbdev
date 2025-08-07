#!/usr/bin/env python3

import requests
import json

def debug_manager_property_access():
    """Debug manager property access and find the correct property"""
    
    print("🔍 DEBUGGING MANAGER PROPERTY ACCESS")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Step 1: Login as manager
    print("\n1️⃣ Logging in as manager...")
    try:
        login_data = {
            "email": "vgoutamram@gmail.com",
            "password": "Gouthi321@"
        }
        
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            auth_result = response.json()
            token = auth_result['token']
            user_info = auth_result['user']
            print(f"✅ Login successful")
            print(f"   User: {user_info['first_name']} {user_info['last_name']}")
            print(f"   Email: {user_info['email']}")
            print(f"   Role: {user_info['role']}")
            print(f"   User ID: {user_info['id']}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Get manager's applications to see what property they manage
    print(f"\n2️⃣ Getting manager's applications to find their property...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/manager/applications", headers=headers)
        
        if response.status_code == 200:
            applications = response.json()
            print(f"✅ Found {len(applications)} applications")
            
            if applications:
                # Get the property ID from existing applications
                property_id = applications[0]['property_id']
                print(f"✅ Manager's property ID: {property_id}")
                return property_id, token
            else:
                print("❌ No applications found for this manager")
                # Let's try to get all properties to see what's available
                print("\n🔍 Checking available properties...")
                
                # Try to get property info for common property IDs
                test_properties = ["prop_test_001", "prop_001", "rci_hotel_001"]
                
                for prop_id in test_properties:
                    try:
                        prop_response = requests.get(f"{base_url}/properties/{prop_id}/info")
                        if prop_response.status_code == 200:
                            prop_data = prop_response.json()
                            print(f"✅ Found property: {prop_id} - {prop_data['property']['name']}")
                            return prop_id, token
                    except:
                        continue
                
                print("❌ Could not find manager's property")
                return None, token
                
        else:
            print(f"❌ Failed to get applications: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, token
    except Exception as e:
        print(f"❌ Error getting applications: {e}")
        return None, token

def test_approval_with_correct_property():
    """Test approval with the correct property for the manager"""
    
    property_id, token = debug_manager_property_access()
    
    if not property_id or not token:
        print("❌ Could not determine manager's property")
        return False
    
    print(f"\n3️⃣ Creating test application for property {property_id}...")
    
    base_url = "http://localhost:8000"
    
    try:
        import time
        test_app = {
            "first_name": "Manager",
            "last_name": "PropertyTest",
            "email": f"property.test.{int(time.time())}@example.com",
            "phone": "5550123456",
            "address": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-08-01",
            "shift_preference": "Day",
            "employment_type": "full_time",
            "experience_years": "2",
            "hotel_experience": "yes",
            "previous_employer": "Test Hotel",
            "reason_for_leaving": "Career advancement",
            "additional_comments": "Test application for correct property"
        }
        
        create_response = requests.post(f"{base_url}/apply/{property_id}", json=test_app)
        if create_response.status_code == 200:
            app_data = create_response.json()
            app_id = app_data['application_id']
            print(f"✅ Created test application: {app_id}")
            print(f"   Property: {property_id}")
        else:
            print(f"❌ Failed to create application: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating application: {e}")
        return False
    
    # Step 4: Test approval with proper data
    print(f"\n4️⃣ Testing approval with proper form data...")
    try:
        form_data = {
            'job_title': 'Front Desk Agent',
            'start_date': '2025-08-01',
            'start_time': '09:00',
            'pay_rate': '18.50',
            'pay_frequency': 'hourly',
            'benefits_eligible': 'yes',
            'supervisor': 'Sarah Manager',
            'special_instructions': 'Complete onboarding by start date'
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{base_url}/applications/{app_id}/approve", data=form_data, headers=headers)
        
        print(f"📤 Approval request status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Approval successful!")
            print(f"   Message: {result.get('message')}")
            print(f"   Employee ID: {result.get('employee_id')}")
            print(f"   Onboarding URL: {result.get('onboarding', {}).get('onboarding_url', 'Not provided')}")
            return True
        else:
            print(f"❌ Approval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during approval: {e}")
        return False

if __name__ == "__main__":
    success = test_approval_with_correct_property()
    
    print(f"\n📊 RESULT:")
    print("=" * 30)
    if success:
        print("✅ Manager approval working correctly!")
        print("✅ Frontend validation fix should prevent 422 errors")
        print("✅ Proper form data results in successful approval")
    else:
        print("❌ Issues found with manager approval process")
        print("🔧 Check manager property assignment and permissions")