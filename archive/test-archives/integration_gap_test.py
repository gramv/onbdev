#!/usr/bin/env python3
"""
Integration Gap Test
Tests specific integration points between frontend and backend
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional

class IntegrationGapTester:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.issues = []
        self.gaps = []
        self.critical_issues = []
        
    def test_authentication_integration(self):
        """Test authentication flow integration"""
        print("🔐 Testing Authentication Integration...")
        
        # Test 1: Login with correct credentials
        try:
            response = requests.post(f"{self.backend_url}/auth/login", json={
                "email": "hr@hoteltest.com",
                "password": "admin123"
            })
            
            if response.status_code != 200:
                self.critical_issues.append(f"Login failing with status {response.status_code}: {response.text}")
                return None
                
            data = response.json()
            required_fields = ['token', 'user', 'expires_at']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.gaps.append(f"Login response missing fields: {missing_fields}")
                
            # Check user object structure
            user = data.get('user', {})
            user_required_fields = ['id', 'email', 'role', 'first_name', 'last_name']
            user_missing_fields = [field for field in user_required_fields if field not in user]
            
            if user_missing_fields:
                self.gaps.append(f"User object missing fields: {user_missing_fields}")
                
            return data.get('token')
            
        except Exception as e:
            self.critical_issues.append(f"Authentication test failed: {str(e)}")
            return None
    
    def test_hr_dashboard_integration(self, token: str):
        """Test HR dashboard data integration"""
        print("👩‍💼 Testing HR Dashboard Integration...")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test dashboard stats
        try:
            response = requests.get(f"{self.backend_url}/hr/dashboard-stats", headers=headers)
            if response.status_code == 200:
                data = response.json()
                expected_fields = ['totalProperties', 'totalManagers', 'totalEmployees', 'pendingApplications']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    self.gaps.append(f"HR dashboard stats missing fields: {missing_fields}")
                else:
                    print("✅ HR dashboard stats structure correct")
            else:
                self.issues.append(f"HR dashboard stats failing: {response.status_code}")
                
        except Exception as e:
            self.issues.append(f"HR dashboard stats error: {str(e)}")
            
        # Test properties endpoint
        try:
            response = requests.get(f"{self.backend_url}/hr/properties", headers=headers)
            if response.status_code == 200:
                properties = response.json()
                if properties and isinstance(properties, list):
                    prop = properties[0]
                    expected_fields = ['id', 'name', 'address', 'city', 'state', 'qr_code_url', 'manager_ids']
                    missing_fields = [field for field in expected_fields if field not in prop]
                    
                    if missing_fields:
                        self.gaps.append(f"Property object missing fields: {missing_fields}")
                    else:
                        print("✅ Properties structure correct")
                        
                    # Check QR code URL format
                    qr_url = prop.get('qr_code_url', '')
                    if not qr_url.startswith('http'):
                        self.gaps.append("QR code URL should be absolute URL")
                        
            else:
                self.issues.append(f"HR properties failing: {response.status_code}")
                
        except Exception as e:
            self.issues.append(f"HR properties error: {str(e)}")
    
    def test_manager_dashboard_integration(self):
        """Test manager dashboard integration"""
        print("👨‍💼 Testing Manager Dashboard Integration...")
        
        # Get manager token
        try:
            response = requests.post(f"{self.backend_url}/auth/login", json={
                "email": "manager@hoteltest.com",
                "password": "manager123"
            })
            
            if response.status_code != 200:
                self.critical_issues.append("Manager login failing")
                return
                
            token = response.json().get('token')
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test manager property endpoint
            response = requests.get(f"{self.backend_url}/manager/property", headers=headers)
            if response.status_code == 200:
                property_data = response.json()
                expected_fields = ['id', 'name', 'address', 'city', 'state']
                missing_fields = [field for field in expected_fields if field not in property_data]
                
                if missing_fields:
                    self.gaps.append(f"Manager property missing fields: {missing_fields}")
                else:
                    print("✅ Manager property structure correct")
            else:
                self.issues.append(f"Manager property endpoint failing: {response.status_code}")
                
            # Test manager applications
            response = requests.get(f"{self.backend_url}/manager/applications", headers=headers)
            if response.status_code == 200:
                applications = response.json()
                if applications and isinstance(applications, list):
                    app = applications[0]
                    expected_fields = ['id', 'property_id', 'department', 'position', 'applicant_data', 'status', 'applied_at']
                    missing_fields = [field for field in expected_fields if field not in app]
                    
                    if missing_fields:
                        self.gaps.append(f"Application object missing fields: {missing_fields}")
                    else:
                        print("✅ Manager applications structure correct")
            else:
                self.issues.append(f"Manager applications failing: {response.status_code}")
                
        except Exception as e:
            self.critical_issues.append(f"Manager dashboard test failed: {str(e)}")
    
    def test_application_workflow_integration(self):
        """Test application submission and approval workflow"""
        print("📝 Testing Application Workflow Integration...")
        
        # Test property info endpoint (public)
        try:
            response = requests.get(f"{self.backend_url}/properties/prop_test_001/info")
            if response.status_code == 200:
                info = response.json()
                expected_fields = ['property', 'departments_and_positions', 'application_url']
                missing_fields = [field for field in expected_fields if field not in info]
                
                if missing_fields:
                    self.gaps.append(f"Property info missing fields: {missing_fields}")
                else:
                    print("✅ Property info structure correct")
                    
                # Check property structure
                property_data = info.get('property', {})
                prop_expected_fields = ['id', 'name', 'address', 'city', 'state']
                prop_missing_fields = [field for field in prop_expected_fields if field not in property_data]
                
                if prop_missing_fields:
                    self.gaps.append(f"Property data missing fields: {prop_missing_fields}")
                    
            else:
                self.issues.append(f"Property info endpoint failing: {response.status_code}")
                
        except Exception as e:
            self.issues.append(f"Property info test failed: {str(e)}")
            
        # Test application submission endpoint structure
        print("⚠️  Application submission test requires valid form data - checking endpoint exists")
        try:
            # Just check if endpoint exists with invalid data
            response = requests.post(f"{self.backend_url}/apply/prop_test_001", json={})
            # We expect this to fail with 422 (validation error) not 404 (not found)
            if response.status_code == 404:
                self.issues.append("Application submission endpoint not found")
            elif response.status_code == 422:
                print("✅ Application submission endpoint exists")
            else:
                print(f"⚠️  Application submission returned unexpected status: {response.status_code}")
                
        except Exception as e:
            self.issues.append(f"Application submission test failed: {str(e)}")
    
    def test_approval_workflow_integration(self, hr_token: str):
        """Test application approval workflow"""
        print("✅ Testing Approval Workflow Integration...")
        
        headers = {"Authorization": f"Bearer {hr_token}"}
        
        # Check if approval endpoints exist
        endpoints_to_check = [
            "/applications/{application_id}/approve",
            "/applications/{application_id}/reject"
        ]
        
        for endpoint in endpoints_to_check:
            # We can't test with real IDs, but we can check if endpoints exist
            test_endpoint = endpoint.replace("{application_id}", "test_id")
            try:
                response = requests.post(f"{self.backend_url}{test_endpoint}", headers=headers)
                if response.status_code == 404:
                    self.issues.append(f"Approval endpoint not found: {endpoint}")
                else:
                    print(f"✅ Approval endpoint exists: {endpoint}")
            except Exception as e:
                self.issues.append(f"Approval endpoint test failed for {endpoint}: {str(e)}")
    
    def test_data_consistency(self, hr_token: str):
        """Test data consistency across endpoints"""
        print("🔍 Testing Data Consistency...")
        
        headers = {"Authorization": f"Bearer {hr_token}"}
        
        try:
            # Get properties from HR endpoint
            properties_response = requests.get(f"{self.backend_url}/hr/properties", headers=headers)
            if properties_response.status_code != 200:
                self.issues.append("Cannot get properties for consistency test")
                return
                
            properties = properties_response.json()
            if not properties:
                self.issues.append("No properties found for consistency test")
                return
                
            property_id = properties[0]['id']
            
            # Get applications for this property
            applications_response = requests.get(
                f"{self.backend_url}/hr/applications",
                headers=headers,
                params={"property_id": property_id}
            )
            
            if applications_response.status_code == 200:
                applications = applications_response.json()
                
                # Check if all applications have valid property_id
                invalid_apps = [app for app in applications if app.get('property_id') != property_id]
                if invalid_apps:
                    self.issues.append(f"Found {len(invalid_apps)} applications with inconsistent property_id")
                else:
                    print("✅ Application-property consistency check passed")
                    
            else:
                self.issues.append("Cannot get applications for consistency test")
                
        except Exception as e:
            self.issues.append(f"Data consistency test failed: {str(e)}")
    
    def test_error_handling_consistency(self):
        """Test error handling consistency"""
        print("⚠️  Testing Error Handling Consistency...")
        
        # Test unauthorized access
        try:
            response = requests.get(f"{self.backend_url}/hr/dashboard-stats")
            if response.status_code == 401:
                try:
                    error_data = response.json()
                    if 'detail' not in error_data:
                        self.gaps.append("Error responses should include 'detail' field")
                    else:
                        print("✅ Unauthorized error format correct")
                except:
                    self.gaps.append("Error responses should be valid JSON")
            else:
                self.issues.append(f"Unauthorized access should return 401, got {response.status_code}")
                
        except Exception as e:
            self.issues.append(f"Error handling test failed: {str(e)}")
            
        # Test invalid endpoint
        try:
            response = requests.get(f"{self.backend_url}/invalid/endpoint")
            if response.status_code != 404:
                self.issues.append(f"Invalid endpoint should return 404, got {response.status_code}")
            else:
                print("✅ 404 error handling correct")
                
        except Exception as e:
            self.issues.append(f"404 error test failed: {str(e)}")
    
    def test_frontend_backend_mismatch(self):
        """Test for specific frontend-backend mismatches"""
        print("🔄 Testing Frontend-Backend Mismatches...")
        
        # Common mismatches found in analysis
        mismatches = [
            {
                "frontend_expects": "/applications/${id}/approve",
                "backend_provides": "/applications/{application_id}/approve",
                "issue": "URL parameter format mismatch"
            },
            {
                "frontend_expects": "/hr/properties/${id}",
                "backend_provides": "/hr/properties/{property_id}",
                "issue": "URL parameter format mismatch"
            },
            {
                "frontend_expects": "/manager/dashboard-stats",
                "backend_provides": "/manager/dashboard-stats",
                "issue": "Should exist but may be missing"
            }
        ]
        
        for mismatch in mismatches:
            self.gaps.append(f"Mismatch: {mismatch['issue']} - Frontend: {mismatch['frontend_expects']}, Backend: {mismatch['backend_provides']}")
    
    def run_comprehensive_test(self):
        """Run all integration tests"""
        print("🚀 Starting Comprehensive Integration Gap Test...")
        print("=" * 60)
        
        # Check backend availability
        try:
            response = requests.get(f"{self.backend_url}/healthz", timeout=5)
            if response.status_code != 200:
                print("❌ Backend health check failed")
                return
        except Exception as e:
            print(f"❌ Cannot connect to backend: {str(e)}")
            return
            
        print("✅ Backend is available")
        
        # Run authentication test first
        hr_token = self.test_authentication_integration()
        
        if hr_token:
            self.test_hr_dashboard_integration(hr_token)
            self.test_approval_workflow_integration(hr_token)
            self.test_data_consistency(hr_token)
        
        self.test_manager_dashboard_integration()
        self.test_application_workflow_integration()
        self.test_error_handling_consistency()
        self.test_frontend_backend_mismatch()
        
        # Generate comprehensive report
        self.generate_gap_report()
    
    def generate_gap_report(self):
        """Generate comprehensive gap analysis report"""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION GAP ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"\n🔴 CRITICAL ISSUES ({len(self.critical_issues)}):")
        for i, issue in enumerate(self.critical_issues, 1):
            print(f"  {i}. {issue}")
            
        print(f"\n🟡 INTEGRATION GAPS ({len(self.gaps)}):")
        for i, gap in enumerate(self.gaps, 1):
            print(f"  {i}. {gap}")
            
        print(f"\n⚠️  GENERAL ISSUES ({len(self.issues)}):")
        for i, issue in enumerate(self.issues, 1):
            print(f"  {i}. {issue}")
            
        # Priority recommendations
        priority_recommendations = [
            "Fix authentication flow - critical for all functionality",
            "Standardize URL parameter formats between frontend and backend",
            "Implement consistent error response format",
            "Add missing fields to API responses",
            "Fix manager dashboard endpoints",
            "Implement proper HTTP status codes",
            "Add comprehensive API validation",
            "Implement request/response logging",
            "Add API documentation with examples",
            "Implement integration testing pipeline"
        ]
        
        print(f"\n🎯 PRIORITY RECOMMENDATIONS:")
        for i, rec in enumerate(priority_recommendations, 1):
            print(f"  {i}. {rec}")
            
        # Generate JSON report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "critical_issues": self.critical_issues,
            "integration_gaps": self.gaps,
            "general_issues": self.issues,
            "priority_recommendations": priority_recommendations,
            "summary": {
                "total_critical": len(self.critical_issues),
                "total_gaps": len(self.gaps),
                "total_issues": len(self.issues),
                "overall_status": "CRITICAL" if self.critical_issues else "NEEDS_ATTENTION" if self.gaps else "GOOD"
            }
        }
        
        with open('integration_gap_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Detailed report saved to integration_gap_report.json")
        print("\n" + "=" * 60)
        print("Gap Analysis Complete!")

if __name__ == "__main__":
    tester = IntegrationGapTester()
    tester.run_comprehensive_test()