#!/usr/bin/env python3
"""
Test Script for Beautiful Welcome Page
This script creates test data to demonstrate the complete flow:
1. Creates a property and manager
2. Creates a job application
3. Manager approves the application (creates employee)
4. Shows the welcome page URL for testing
"""

import requests
import json
from datetime import datetime

# Base URL for the backend server
BASE_URL = "http://localhost:8000"

def test_welcome_page_flow():
    print("🚀 Testing Beautiful Welcome Page Flow")
    print("=" * 50)
    
    try:
        # Step 1: Create HR user and property
        print("📋 Step 1: Creating test property and manager...")
        
        # Create property
        property_data = {
            "name": "Grand Vista Hotel & Spa",
            "address": "123 Ocean Drive, Miami Beach, FL 33139",
            "phone": "(305) 555-0123",
            "manager_email": "manager@grandvista.com"
        }
        
        property_response = requests.post(f"{BASE_URL}/hr/properties", json=property_data)
        if property_response.status_code != 200:
            print(f"❌ Failed to create property: {property_response.text}")
            return
            
        property_data = property_response.json()
        property_id = property_data["id"]
        print(f"✅ Created property: {property_data['name']} (ID: {property_id})")
        
        # Step 2: Create job application
        print("\n📝 Step 2: Creating job application...")
        
        app_data = {
            "first_name": "Sarah",
            "last_name": "Johnson", 
            "email": "sarah.johnson@email.com",
            "phone": "(555) 123-4567",
            "department": "Guest Services",
            "position": "Front Desk Agent",
            "availability": "Full-time",
            "experience": "2 years hotel experience"
        }
        
        app_response = requests.post(f"{BASE_URL}/apply/{property_id}", data=app_data)
        if app_response.status_code != 200:
            print(f"❌ Failed to create application: {app_response.text}")
            return
            
        app_result = app_response.json()
        application_id = app_result["application_id"]
        print(f"✅ Created application for {app_data['first_name']} {app_data['last_name']} (ID: {application_id})")
        
        # Step 3: Get manager token (simulate manager login)
        print("\n👔 Step 3: Getting manager access...")
        
        # Find the manager user that was created with the property
        users_response = requests.get(f"{BASE_URL}/debug/users")
        if users_response.status_code != 200:
            print("❌ Failed to get users")
            return
            
        users = users_response.json()
        manager_token = None
        for user in users:
            if user.get("role") == "manager" and user.get("property_id") == property_id:
                manager_token = user["id"]
                break
                
        if not manager_token:
            print("❌ No manager found for property")
            return
            
        print(f"✅ Found manager token: {manager_token}")
        
        # Step 4: Manager approves application
        print("\n✅ Step 4: Manager approving application...")
        
        approval_data = {
            "job_title": "Front Desk Agent",
            "start_date": "2024-02-01",
            "start_time": "9:00 AM",
            "pay_rate": 18.50,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Maria Rodriguez",
            "special_instructions": "Welcome to our amazing team!"
        }
        
        headers = {"Authorization": f"Bearer {manager_token}"}
        approval_response = requests.post(
            f"{BASE_URL}/applications/{application_id}/approve",
            data=approval_data,
            headers=headers
        )
        
        if approval_response.status_code != 200:
            print(f"❌ Failed to approve application: {approval_response.text}")
            return
            
        approval_result = approval_response.json()
        employee_id = approval_result["employee_id"]
        print(f"✅ Application approved! Employee ID: {employee_id}")
        
        # Step 5: Test the welcome page endpoint
        print("\n🎉 Step 5: Testing welcome page data...")
        
        welcome_response = requests.get(f"{BASE_URL}/api/employees/{employee_id}/welcome-data")
        if welcome_response.status_code != 200:
            print(f"❌ Failed to get welcome data: {welcome_response.text}")
            return
            
        welcome_data = welcome_response.json()
        print("✅ Welcome data retrieved successfully!")
        print(f"   Employee: {welcome_data['applicant_data']['first_name']} {welcome_data['applicant_data']['last_name']}")
        print(f"   Property: {welcome_data['property']['name']}")
        print(f"   Position: {welcome_data['employee']['job_details']['job_title']}")
        print(f"   Start Date: {welcome_data['employee']['job_details']['start_date']}")
        
        # Final success message
        print("\n" + "=" * 50)
        print("🎊 SUCCESS! Welcome Page Test Complete!")
        print("=" * 50)
        print(f"📱 Frontend URL: http://localhost:3000/onboarding-welcome/{employee_id}")
        print(f"🔧 API Endpoint: {BASE_URL}/api/employees/{employee_id}/welcome-data")
        print("\n💡 You can now:")
        print(f"   1. Visit the frontend URL to see the beautiful welcome page")
        print(f"   2. Test language switching (English/Spanish)")
        print(f"   3. Click 'Begin My Onboarding' to start the onboarding process")
        print(f"   4. See the property name '{welcome_data['property']['name']}' displayed prominently")
        
        return employee_id
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return None

if __name__ == "__main__":
    employee_id = test_welcome_page_flow()
    if employee_id:
        print(f"\n🔗 Quick Links:")
        print(f"Welcome Page: http://localhost:3000/onboarding-welcome/{employee_id}")
        print(f"API Data: http://localhost:8000/api/employees/{employee_id}/welcome-data")