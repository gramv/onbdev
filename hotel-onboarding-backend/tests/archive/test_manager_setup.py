#!/usr/bin/env python3
"""
Test script for manager employee setup endpoints
"""
import requests
import json
from datetime import datetime, date, timedelta

# Base URL
BASE_URL = "http://localhost:8000"

# Test data
test_application_id = "test-app-001"
test_manager_token = None

def login_as_manager():
    """Login as test manager"""
    global test_manager_token
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if response.status_code == 200:
        data = response.json()
        test_manager_token = data["data"]["token"]
        print("✅ Manager login successful")
        return True
    else:
        print(f"❌ Manager login failed: {response.text}")
        return False

def test_enhanced_approval():
    """Test enhanced application approval endpoint"""
    headers = {"Authorization": f"Bearer {test_manager_token}"}
    
    approval_data = {
        "job_offer": {
            "job_title": "Front Desk Agent",
            "start_date": (date.today() + timedelta(days=14)).isoformat(),
            "pay_rate": 18.50,
            "pay_frequency": "hourly",
            "employment_type": "full_time",
            "supervisor": "John Smith",
            "benefits_eligible": True
        },
        "orientation_date": (date.today() + timedelta(days=10)).isoformat(),
        "orientation_time": "9:00 AM",
        "orientation_location": "Main Conference Room",
        "uniform_size": "Medium",
        "parking_location": "Employee Lot A",
        "locker_number": "42",
        "training_requirements": "Customer service training, PMS system training",
        "special_instructions": "Please bring two forms of ID for I-9 verification",
        "health_plan_selection": "hra_4k",
        "dental_coverage": True,
        "vision_coverage": False,
        "send_onboarding_email": True
    }
    
    response = requests.post(
        f"{BASE_URL}/applications/{test_application_id}/approve-enhanced",
        json=approval_data,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Enhanced approval successful")
        print(f"   Redirect to: {data['data']['redirect_to']}")
        return True
    else:
        print(f"❌ Enhanced approval failed: {response.text}")
        return False

def test_employee_setup():
    """Test manager employee setup endpoint"""
    headers = {"Authorization": f"Bearer {test_manager_token}"}
    
    setup_data = {
        "property_id": "prop_test_001",
        "property_name": "Grand Plaza Hotel",
        "property_address": "123 Main Street",
        "property_city": "Downtown",
        "property_state": "CA",
        "property_zip": "90210",
        "property_phone": "(555) 123-4567",
        
        "employee_first_name": "Jane",
        "employee_middle_initial": "M",
        "employee_last_name": "Doe",
        "employee_email": "jane.doe@example.com",
        "employee_phone": "(555) 987-6543",
        "employee_address": "456 Oak Avenue",
        "employee_city": "Suburbia",
        "employee_state": "CA",
        "employee_zip": "90211",
        
        "department": "Front Office",
        "position": "Front Desk Agent",
        "job_title": "Front Desk Agent",
        "hire_date": date.today().isoformat(),
        "start_date": (date.today() + timedelta(days=14)).isoformat(),
        "employment_type": "full_time",
        "work_schedule": "Monday-Friday 7AM-3PM",
        
        "pay_rate": 18.50,
        "pay_frequency": "hourly",
        "overtime_eligible": True,
        
        "supervisor_name": "John Smith",
        "supervisor_title": "Front Office Manager",
        "supervisor_email": "john.smith@hotel.com",
        "supervisor_phone": "(555) 123-4568",
        "reporting_location": "Front Desk",
        
        "benefits_eligible": True,
        "health_insurance_eligible": True,
        "health_insurance_start_date": (date.today() + timedelta(days=30)).isoformat(),
        "pto_eligible": True,
        "pto_accrual_rate": "1 day per month",
        
        "health_plan_selection": "hra_4k",
        "dental_coverage": True,
        "vision_coverage": False,
        
        "uniform_required": True,
        "uniform_size": "Medium",
        "parking_assigned": True,
        "parking_location": "Employee Lot A",
        "locker_assigned": True,
        "locker_number": "42",
        
        "orientation_date": (date.today() + timedelta(days=10)).isoformat(),
        "orientation_time": "9:00 AM",
        "orientation_location": "Main Conference Room",
        "training_requirements": "Customer service training, PMS system training",
        
        "manager_id": "mgr_test_001",
        "manager_name": "Mike Wilson",
        "manager_signature": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCI+CiAgPHBhdGggZD0iTTEwLDUwIEw1MCwzMCBMOTAsNTAgTDEzMCwzMCBMMTcwLDUwIiBzdHJva2U9ImJsYWNrIiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9IjIiLz4KPC9zdmc+",
        "manager_signature_date": datetime.now().isoformat(),
        
        "application_id": test_application_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/manager/employee-setup",
        json=setup_data,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Employee setup successful")
        print(f"   Employee ID: {data['data']['employee_id']}")
        print(f"   Onboarding URL: {data['data']['onboarding_url']}")
        print(f"   Token: {data['data']['token']}")
        print(f"   Expires at: {data['data']['expires_at']}")
        return True
    else:
        print(f"❌ Employee setup failed: {response.text}")
        return False

def test_get_application_for_setup():
    """Test getting application data for setup"""
    headers = {"Authorization": f"Bearer {test_manager_token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/manager/employee-setup/{test_application_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Get application for setup successful")
        print(f"   Property: {data['data']['property_name']}")
        print(f"   Department: {data['data']['department']}")
        print(f"   Position: {data['data']['position']}")
        return True
    else:
        print(f"❌ Get application for setup failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Manager Employee Setup Endpoints")
    print("=" * 50)
    
    if not login_as_manager():
        print("❌ Failed to login as manager. Exiting.")
        return
    
    print("\n1️⃣ Testing Enhanced Application Approval")
    test_enhanced_approval()
    
    print("\n2️⃣ Testing Get Application for Setup")
    test_get_application_for_setup()
    
    print("\n3️⃣ Testing Employee Setup Creation")
    test_employee_setup()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()