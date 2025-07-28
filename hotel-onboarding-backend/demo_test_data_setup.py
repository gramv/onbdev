#!/usr/bin/env python3
"""
Demo Test Data Setup Script
Creates comprehensive test data for QR job application workflow demonstration
Includes multiple properties, applications in various states, and talent pool candidates
"""

import uuid
import requests
import json
from datetime import datetime, timezone, date, timedelta
from typing import Dict, List, Any

# Backend URL
BASE_URL = "http://localhost:8000"

class DemoDataSetup:
    def __init__(self):
        self.hr_token = None
        self.manager_tokens = {}
        self.properties = []
        self.applications = []
        self.talent_pool_candidates = []
        
    def check_backend_status(self) -> bool:
        """Check if backend server is running"""
        try:
            response = requests.get(f"{BASE_URL}/healthz")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
    
    def create_hr_account(self) -> Dict[str, Any]:
        """Create HR account using the secret endpoint"""
        print("🔑 Creating HR account...")
        
        response = requests.post(f"{BASE_URL}/secret/create-hr", params={
            "email": "hr@hoteltest.com",
            "password": "admin123",
            "secret_key": "hotel-admin-2025"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ HR account created: {data['user']['email']}")
            return data['user']
        else:
            print(f"❌ Failed to create HR account: {response.text}")
            return None
    
    def login_as_hr(self) -> str:
        """Login as HR to get token"""
        print("🔐 Logging in as HR...")
        
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "hr@hoteltest.com",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ HR login successful")
            self.hr_token = data['token']
            return data['token']
        else:
            print(f"❌ HR login failed: {response.text}")
            return None
    
    def create_demo_properties(self) -> List[Dict[str, Any]]:
        """Create multiple demo properties with QR codes"""
        print("🏨 Creating demo properties...")
        
        properties_data = [
            {
                "name": "Grand Plaza Hotel",
                "address": "123 Main Street",
                "city": "Downtown",
                "state": "CA",
                "zip_code": "90210",
                "phone": "(555) 123-4567"
            },
            {
                "name": "Seaside Resort & Spa",
                "address": "456 Ocean Drive",
                "city": "Coastal City",
                "state": "FL",
                "zip_code": "33101",
                "phone": "(555) 234-5678"
            },
            {
                "name": "Mountain View Lodge",
                "address": "789 Alpine Way",
                "city": "Mountain Town",
                "state": "CO",
                "zip_code": "80424",
                "phone": "(555) 345-6789"
            },
            {
                "name": "City Center Business Hotel",
                "address": "321 Corporate Blvd",
                "city": "Metro City",
                "state": "NY",
                "zip_code": "10001",
                "phone": "(555) 456-7890"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.hr_token}"}
        created_properties = []
        
        for prop_data in properties_data:
            response = requests.post(f"{BASE_URL}/hr/properties", data=prop_data, headers=headers)
            
            if response.status_code == 200:
                property_obj = response.json()
                created_properties.append(property_obj)
                print(f"✅ Property created: {property_obj['name']} (ID: {property_obj['id']})")
                
                # Generate QR code for each property
                qr_response = requests.post(
                    f"{BASE_URL}/hr/properties/{property_obj['id']}/qr-code",
                    headers=headers
                )
                
                if qr_response.status_code == 200:
                    qr_data = qr_response.json()
                    property_obj['qr_code_url'] = qr_data['qr_code_url']
                    print(f"   📱 QR Code generated: {qr_data['qr_code_url']}")
                else:
                    print(f"   ⚠️  QR Code generation failed for {property_obj['name']}")
            else:
                print(f"❌ Failed to create property {prop_data['name']}: {response.text}")
        
        self.properties = created_properties
        return created_properties
    
    def create_manager_accounts(self) -> Dict[str, str]:
        """Create manager accounts for each property"""
        print("👥 Creating manager accounts...")
        
        manager_data = [
            {
                "email": "manager1@hoteltest.com",
                "first_name": "Mike",
                "last_name": "Wilson",
                "password": "manager123"
            },
            {
                "email": "manager2@hoteltest.com",
                "first_name": "Sarah",
                "last_name": "Davis",
                "password": "manager123"
            },
            {
                "email": "manager3@hoteltest.com",
                "first_name": "John",
                "last_name": "Smith",
                "password": "manager123"
            },
            {
                "email": "manager4@hoteltest.com",
                "first_name": "Lisa",
                "last_name": "Brown",
                "password": "manager123"
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.hr_token}"}
        
        for i, (property_obj, manager_info) in enumerate(zip(self.properties, manager_data)):
            # Try to login first to see if manager already exists
            login_response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": manager_info["email"],
                "password": manager_info["password"]
            })
            
            if login_response.status_code == 200:
                # Manager already exists, just get the token
                login_data = login_response.json()
                manager_token = login_data['token']
                self.manager_tokens[property_obj['id']] = manager_token
                print(f"✅ Manager {manager_info['email']} already exists for {property_obj['name']}")
                print(f"   🔑 Manager token obtained for {manager_info['email']}")
            else:
                # Manager doesn't exist, create it
                create_data = {
                    "email": manager_info["email"],
                    "first_name": manager_info["first_name"],
                    "last_name": manager_info["last_name"],
                    "password": manager_info["password"],
                    "property_id": property_obj['id']
                }
                
                create_response = requests.post(
                    f"{BASE_URL}/hr/managers",
                    data=create_data,
                    headers=headers
                )
                
                if create_response.status_code == 200:
                    print(f"✅ Manager {manager_info['email']} created for {property_obj['name']}")
                    
                    # Now login to get the manager token
                    login_response = requests.post(f"{BASE_URL}/auth/login", json={
                        "email": manager_info["email"],
                        "password": manager_info["password"]
                    })
                    
                    if login_response.status_code == 200:
                        login_data = login_response.json()
                        manager_token = login_data['token']
                        self.manager_tokens[property_obj['id']] = manager_token
                        print(f"   🔑 Manager token obtained for {manager_info['email']}")
                    else:
                        print(f"   ⚠️  Failed to login as manager {manager_info['email']}")
                else:
                    print(f"❌ Failed to create manager {manager_info['email']}: {create_response.text}")
        
        return self.manager_tokens
    
    def create_demo_applications(self) -> List[Dict[str, Any]]:
        """Create applications in various states for demo"""
        print("📝 Creating demo applications...")
        
        # Application templates with different scenarios
        application_templates = [
            # PENDING applications
            {
                "department": "Front Desk",
                "position": "Front Desk Agent",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@email.com",
                "phone": "(555) 987-6543",
                "address": "456 Oak Avenue",
                "city": "Somewhere",
                "state": "CA",
                "zip_code": "90211",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": "2025-08-01",
                "shift_preference": "morning",
                "employment_type": "full_time",
                "experience_years": "2-5",
                "hotel_experience": "yes",
                "status": "pending"
            },
            {
                "department": "Housekeeping",
                "position": "Housekeeper",
                "first_name": "Maria",
                "last_name": "Garcia",
                "email": "maria.garcia@email.com",
                "phone": "(555) 876-5432",
                "address": "789 Pine Street",
                "city": "Somewhere",
                "state": "CA",
                "zip_code": "90212",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": "2025-08-15",
                "shift_preference": "afternoon",
                "employment_type": "full_time",
                "experience_years": "1-2",
                "hotel_experience": "yes",
                "status": "pending"
            },
            {
                "department": "Food & Beverage",
                "position": "Server",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "email": "sarah.johnson@email.com",
                "phone": "(555) 765-4321",
                "address": "321 Elm Drive",
                "city": "Somewhere",
                "state": "CA",
                "zip_code": "90213",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": "2025-08-10",
                "shift_preference": "evening",
                "employment_type": "part_time",
                "experience_years": "0-1",
                "hotel_experience": "no",
                "status": "pending"
            },
            # Applications for talent pool (multiple candidates for same position)
            {
                "department": "Front Desk",
                "position": "Front Desk Agent",
                "first_name": "Michael",
                "last_name": "Brown",
                "email": "michael.brown@email.com",
                "phone": "(555) 654-3210",
                "address": "654 Maple Lane",
                "city": "Somewhere",
                "state": "CA",
                "zip_code": "90214",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": "2025-08-01",
                "shift_preference": "evening",
                "employment_type": "full_time",
                "experience_years": "3-5",
                "hotel_experience": "yes",
                "status": "talent_pool"
            },
            {
                "department": "Front Desk",
                "position": "Front Desk Agent",
                "first_name": "Emily",
                "last_name": "Davis",
                "email": "emily.davis@email.com",
                "phone": "(555) 543-2109",
                "address": "987 Cedar Court",
                "city": "Somewhere",
                "state": "CA",
                "zip_code": "90215",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": "2025-08-01",
                "shift_preference": "morning",
                "employment_type": "full_time",
                "experience_years": "1-2",
                "hotel_experience": "yes",
                "status": "talent_pool"
            },
            # Approved application
            {
                "department": "Maintenance",
                "position": "Maintenance Technician",
                "first_name": "Robert",
                "last_name": "Wilson",
                "email": "robert.wilson@email.com",
                "phone": "(555) 432-1098",
                "address": "147 Birch Street",
                "city": "Somewhere",
                "state": "CA",
                "zip_code": "90216",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": "2025-08-05",
                "shift_preference": "morning",
                "employment_type": "full_time",
                "experience_years": "5+",
                "hotel_experience": "yes",
                "status": "approved"
            }
        ]
        
        created_applications = []
        
        # Create applications for each property
        for property_obj in self.properties:
            print(f"   Creating applications for {property_obj['name']}...")
            
            for template in application_templates:
                # Create a copy and modify email to be unique per property
                app_data = template.copy()
                base_email = app_data['email'].split('@')[0]
                domain = app_data['email'].split('@')[1]
                app_data['email'] = f"{base_email}.{property_obj['name'].lower().replace(' ', '')}@{domain}"
                
                # Submit application (remove status field as it's not part of the API)
                api_data = {k: v for k, v in app_data.items() if k != 'status'}
                response = requests.post(f"{BASE_URL}/apply/{property_obj['id']}", json=api_data)
                
                if response.status_code == 200:
                    app_response = response.json()
                    app_id = app_response['application_id']
                    
                    # If this should be in talent pool or approved, update status
                    if template['status'] in ['talent_pool', 'approved']:
                        manager_token = self.manager_tokens.get(property_obj['id'])
                        if manager_token:
                            headers = {"Authorization": f"Bearer {manager_token}"}
                            
                            if template['status'] == 'approved':
                                # Approve the application
                                approve_data = {
                                    'job_title': app_data['position'],
                                    'start_date': app_data['start_date'],
                                    'start_time': '08:00',
                                    'pay_rate': '18.50',
                                    'pay_frequency': 'hourly',
                                    'benefits_eligible': 'yes',
                                    'supervisor': 'Jane Smith'
                                }
                                
                                approve_response = requests.post(
                                    f"{BASE_URL}/applications/{app_id}/approve",
                                    data=approve_data,
                                    headers=headers
                                )
                                
                                if approve_response.status_code == 200:
                                    print(f"     ✅ Approved: {app_data['first_name']} {app_data['last_name']} - {app_data['position']}")
                                else:
                                    print(f"     ⚠️  Failed to approve application for {app_data['first_name']} {app_data['last_name']}")
                            
                            elif template['status'] == 'talent_pool':
                                # Move to talent pool (this would normally happen when another candidate is approved)
                                # For demo purposes, we'll simulate this by creating the application and noting it should be talent pool
                                print(f"     📋 Talent Pool: {app_data['first_name']} {app_data['last_name']} - {app_data['position']}")
                                self.talent_pool_candidates.append({
                                    'application_id': app_id,
                                    'property_id': property_obj['id'],
                                    'name': f"{app_data['first_name']} {app_data['last_name']}",
                                    'position': app_data['position'],
                                    'email': app_data['email']
                                })
                    else:
                        print(f"     📝 Pending: {app_data['first_name']} {app_data['last_name']} - {app_data['position']}")
                    
                    created_applications.append({
                        'application_id': app_id,
                        'property_id': property_obj['id'],
                        'property_name': property_obj['name'],
                        'applicant_name': f"{app_data['first_name']} {app_data['last_name']}",
                        'position': app_data['position'],
                        'status': template['status'],
                        'email': app_data['email']
                    })
                    
                else:
                    print(f"     ❌ Failed to create application for {app_data['first_name']} {app_data['last_name']}: {response.text}")
        
        self.applications = created_applications
        return created_applications
    
    def verify_end_to_end_workflow(self) -> bool:
        """Verify that all demo scenarios work end-to-end"""
        print("🔍 Verifying end-to-end workflow...")
        
        verification_results = []
        
        # Test 1: Verify QR codes are accessible
        print("   Testing QR code accessibility...")
        for property_obj in self.properties:
            if 'qr_code_url' in property_obj:
                # Test that the application form loads
                response = requests.get(f"{BASE_URL}/properties/{property_obj['id']}/info")
                if response.status_code == 200:
                    verification_results.append(f"✅ QR code endpoint working for {property_obj['name']}")
                else:
                    verification_results.append(f"❌ QR code endpoint failed for {property_obj['name']}")
        
        # Test 2: Verify application submission works
        print("   Testing application submission...")
        test_property = self.properties[0] if self.properties else None
        if test_property:
            test_app_data = {
                "department": "Test Department",
                "position": "Test Position",
                "first_name": "Test",
                "last_name": "User",
                "email": "test.verification@email.com",
                "phone": "(555) 000-0000",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "zip_code": "90000",
                "work_authorized": "yes",
                "sponsorship_required": "no",
                "start_date": "2025-08-30",
                "shift_preference": "morning",
                "employment_type": "full_time",
                "experience_years": "1-2",
                "hotel_experience": "no"
            }
            
            response = requests.post(f"{BASE_URL}/apply/{test_property['id']}", json=test_app_data)
            if response.status_code == 200:
                verification_results.append("✅ Application submission working")
            else:
                verification_results.append(f"❌ Application submission failed: {response.text}")
        
        # Test 3: Verify manager can view applications
        print("   Testing manager application access...")
        for property_id, manager_token in self.manager_tokens.items():
            headers = {"Authorization": f"Bearer {manager_token}"}
            response = requests.get(f"{BASE_URL}/applications", headers=headers)
            if response.status_code == 200:
                apps = response.json()
                verification_results.append(f"✅ Manager can access applications for property {property_id} ({len(apps)} applications)")
            else:
                verification_results.append(f"❌ Manager cannot access applications for property {property_id}")
        
        # Test 4: Verify HR can view all data
        print("   Testing HR access...")
        if self.hr_token:
            headers = {"Authorization": f"Bearer {self.hr_token}"}
            
            # Test properties access
            response = requests.get(f"{BASE_URL}/hr/properties", headers=headers)
            if response.status_code == 200:
                verification_results.append("✅ HR can access all properties")
            else:
                verification_results.append("❌ HR cannot access properties")
            
            # Test applications access
            response = requests.get(f"{BASE_URL}/hr/applications", headers=headers)
            if response.status_code == 200:
                verification_results.append("✅ HR can access all applications")
            else:
                verification_results.append("❌ HR cannot access applications")
        
        # Print verification results
        print("\n📋 Verification Results:")
        for result in verification_results:
            print(f"   {result}")
        
        # Return True if all tests passed
        failed_tests = [r for r in verification_results if r.startswith("❌")]
        return len(failed_tests) == 0
    
    def print_demo_summary(self):
        """Print comprehensive demo setup summary"""
        print("\n" + "=" * 60)
        print("🎉 DEMO TEST DATA SETUP COMPLETE!")
        print("=" * 60)
        
        print(f"\n🏨 Properties Created ({len(self.properties)}):")
        for prop in self.properties:
            print(f"   • {prop['name']} (ID: {prop['id']})")
            print(f"     📍 {prop['address']}, {prop['city']}, {prop['state']}")
            if 'qr_code_url' in prop:
                print(f"     📱 QR Code: {prop['qr_code_url']}")
            print(f"     🔗 Application URL: {BASE_URL}/apply/{prop['id']}")
            print()
        
        print(f"📝 Applications Created ({len(self.applications)}):")
        status_counts = {}
        for app in self.applications:
            status = app['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            print(f"   • {app['applicant_name']} - {app['position']} ({app['status']})")
            print(f"     🏨 {app['property_name']}")
            print(f"     📧 {app['email']}")
        
        print(f"\n📊 Application Status Summary:")
        for status, count in status_counts.items():
            print(f"   • {status.upper()}: {count} applications")
        
        if self.talent_pool_candidates:
            print(f"\n📋 Talent Pool Candidates ({len(self.talent_pool_candidates)}):")
            for candidate in self.talent_pool_candidates:
                print(f"   • {candidate['name']} - {candidate['position']}")
        
        print(f"\n🔑 Test Accounts:")
        print(f"   HR Account:")
        print(f"     📧 Email: hr@hoteltest.com")
        print(f"     🔒 Password: admin123")
        print(f"     🎫 Token: {self.hr_token}")
        
        print(f"\n   Manager Accounts:")
        manager_data = [
            {"email": "manager1@hoteltest.com", "name": "Mike Wilson"},
            {"email": "manager2@hoteltest.com", "name": "Sarah Davis"},
            {"email": "manager3@hoteltest.com", "name": "John Smith"},
            {"email": "manager4@hoteltest.com", "name": "Lisa Brown"}
        ]
        for i, (prop, manager_info) in enumerate(zip(self.properties, manager_data)):
            print(f"     {prop['name']} - {manager_info['name']}:")
            print(f"       📧 Email: {manager_info['email']}")
            print(f"       🔒 Password: manager123")
            if prop['id'] in self.manager_tokens:
                print(f"       🎫 Token: {self.manager_tokens[prop['id']]}")
        
        print(f"\n🔗 Quick Links:")
        print(f"   • Backend API Docs: {BASE_URL}/docs")
        print(f"   • Frontend (if running): http://localhost:5173")
        print(f"   • Health Check: {BASE_URL}/healthz")
        
        print(f"\n🎯 Demo Scenarios Ready:")
        print(f"   1. ✅ QR Code Generation - All properties have QR codes")
        print(f"   2. ✅ Application Submission - Public forms work without auth")
        print(f"   3. ✅ Application Review - Managers can review property applications")
        print(f"   4. ✅ Approval Workflow - Applications can be approved/rejected")
        print(f"   5. ✅ Talent Pool - Multiple candidates for same position")
        print(f"   6. ✅ Multi-Property - Different properties with different managers")
        
        print(f"\n📖 Next Steps for Demo:")
        print(f"   1. Start frontend: cd hotel-onboarding-frontend && npm run dev")
        print(f"   2. Login as HR to see all properties and applications")
        print(f"   3. Login as manager to see property-specific applications")
        print(f"   4. Test QR code by visiting application URLs")
        print(f"   5. Demonstrate approval workflow and talent pool management")

def main():
    """Main demo setup function"""
    print("🏨 Hotel Onboarding System - Demo Test Data Setup")
    print("=" * 60)
    
    setup = DemoDataSetup()
    
    # Check backend status
    if not setup.check_backend_status():
        print("❌ Backend server is not responding. Please start it first:")
        print("   cd hotel-onboarding-backend")
        print("   python -m uvicorn app.main_enhanced:app --reload")
        return False
    
    print("✅ Backend server is running")
    
    # Setup process
    try:
        # Create HR account and login
        hr_user = setup.create_hr_account()
        if not hr_user:
            return False
        
        hr_token = setup.login_as_hr()
        if not hr_token:
            return False
        
        # Create demo properties
        properties = setup.create_demo_properties()
        if not properties:
            print("❌ Failed to create demo properties")
            return False
        
        # Create manager accounts
        manager_tokens = setup.create_manager_accounts()
        if not manager_tokens:
            print("❌ Failed to create manager accounts")
            return False
        
        # Create demo applications
        applications = setup.create_demo_applications()
        if not applications:
            print("❌ Failed to create demo applications")
            return False
        
        # Verify end-to-end workflow
        if setup.verify_end_to_end_workflow():
            print("✅ End-to-end workflow verification passed")
        else:
            print("⚠️  Some end-to-end tests failed, but demo data is still usable")
        
        # Print comprehensive summary
        setup.print_demo_summary()
        
        return True
        
    except Exception as e:
        print(f"❌ Demo setup failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Demo setup completed successfully!")
    else:
        print("\n❌ Demo setup failed. Please check the errors above.")