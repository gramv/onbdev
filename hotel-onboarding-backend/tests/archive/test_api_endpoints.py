#!/usr/bin/env python3
"""
API Endpoint Test Script
Tests the created property and manager via API endpoints
"""

import requests
import json
import sys
from setup_test_data_simple import SimpleTestSetup

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
    
    def test_health_check(self):
        """Test basic API health"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Health check: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def test_manager_login(self, email: str, password: str):
        """Test manager login"""
        print(f"Testing login: {email}")
        
        data = {
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login", json=data)
            print(f"Login response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if "access_token" in result:
                    self.auth_token = result["access_token"]
                    print(f"✅ Login successful - Got token")
                    return True
                else:
                    print(f"❌ Login failed - No token in response: {result}")
                    return False
            else:
                print(f"❌ Login failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_property_application_endpoint(self, property_id: str):
        """Test that property application endpoint is accessible"""
        print(f"Testing application endpoint for property: {property_id}")
        
        # First, try to get property info (if endpoint exists)
        try:
            response = self.session.get(f"{self.base_url}/properties/{property_id}")
            print(f"Property info endpoint: {response.status_code}")
        except:
            print("Property info endpoint may not exist")
        
        # Test application form submission
        application_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@testhotel.com",
            "phone": "(555) 123-4567",
            "phone_is_cell": True,
            "address": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210",
            "department": "Front Desk",
            "position": "Front Desk Associate",
            "work_authorization": "Yes",
            "criminal_conviction": "No",
            "position_preferences": ["Full-time"],
            "availability_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "start_date_preference": "Immediately",
            "terms_agreement": True
        }
        
        try:
            response = self.session.post(f"{self.base_url}/apply/{property_id}", json=application_data)
            print(f"Application submission: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Application submitted successfully: {result.get('id', 'No ID')}")
                return result
            else:
                print(f"❌ Application submission failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Application submission error: {e}")
            return None
    
    def test_manager_dashboard_access(self):
        """Test manager dashboard access with auth token"""
        if not self.auth_token:
            print("❌ No auth token - cannot test dashboard")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = self.session.get(f"{self.base_url}/manager/dashboard", headers=headers)
            print(f"Manager dashboard: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Dashboard access successful")
                return True
            else:
                print(f"❌ Dashboard access failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Dashboard access error: {e}")
            return False
    
    def test_application_approval(self, application_id: str):
        """Test manager application approval"""
        if not self.auth_token:
            print("❌ No auth token - cannot test approval")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        approval_data = {
            "approved": True,
            "notes": "Test approval"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/applications/{application_id}/approve", 
                                       json=approval_data, headers=headers)
            print(f"Application approval: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Application approved successfully")
                return True
            else:
                print(f"❌ Application approval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Application approval error: {e}")
            return False

def main():
    print("=" * 60)
    print("API ENDPOINT TESTING")
    print("=" * 60)
    
    # Get test data
    setup = SimpleTestSetup()
    
    # Get the existing property (assume it exists from previous run)
    try:
        result = setup.client.table('properties').select('*').eq('name', 'Demo Hotel').execute()
        if not result.data:
            print("❌ No test property found. Run setup_test_data_simple.py first")
            return
        
        property_id = result.data[0]['id']
        print(f"Using property ID: {property_id}")
        
    except Exception as e:
        print(f"❌ Failed to get property ID: {e}")
        return
    
    # Initialize tester
    tester = APITester()
    
    # Test 1: Health check
    print("\n1. Testing API health...")
    health_ok = tester.test_health_check()
    
    # Test 2: Manager login
    print("\n2. Testing manager login...")
    login_ok = tester.test_manager_login("manager@demo.com", "demo123")
    
    # Test 3: Application endpoint
    print("\n3. Testing application submission...")
    application_result = tester.test_property_application_endpoint(property_id)
    
    # Test 4: Manager dashboard
    if login_ok:
        print("\n4. Testing manager dashboard...")
        dashboard_ok = tester.test_manager_dashboard_access()
    else:
        print("\n4. Skipping dashboard test (login failed)")
        dashboard_ok = False
    
    # Test 5: Application approval
    if application_result and login_ok:
        print("\n5. Testing application approval...")
        approval_ok = tester.test_application_approval(application_result.get('id'))
    else:
        print("\n5. Skipping approval test (no application or login failed)")
        approval_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Manager Login: {'✅ PASS' if login_ok else '❌ FAIL'}")
    print(f"Application Submission: {'✅ PASS' if application_result else '❌ FAIL'}")
    print(f"Manager Dashboard: {'✅ PASS' if dashboard_ok else '❌ FAIL'}")
    print(f"Application Approval: {'✅ PASS' if approval_ok else '❌ FAIL'}")
    
    if all([health_ok, login_ok, application_result]):
        print("\n🎉 Basic system functionality is working!")
        print(f"Property ID: {property_id}")
        print(f"Manager Credentials: manager@demo.com / demo123")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()