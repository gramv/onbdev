#!/usr/bin/env python3
"""
Comprehensive Backend-Frontend Integration Analysis
Identifies gaps, issues, and inconsistencies between backend API and frontend expectations
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional

class IntegrationAnalyzer:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://localhost:3000"
        self.issues = []
        self.gaps = []
        self.recommendations = []
        
    def analyze_authentication_flow(self):
        """Test authentication endpoints and flow"""
        print("🔐 Analyzing Authentication Flow...")
        
        # Test login endpoint
        try:
            login_data = {
                "email": "hr@hoteltest.com",
                "password": "admin123"
            }
            response = requests.post(f"{self.backend_url}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Login successful: {data.get('user', {}).get('role')}")
                
                # Test token refresh
                token = data.get('token')
                if token:
                    refresh_response = requests.post(
                        f"{self.backend_url}/auth/refresh",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if refresh_response.status_code == 200:
                        print("✅ Token refresh working")
                    else:
                        self.issues.append("Token refresh endpoint failing")
                        
                # Test /auth/me endpoint
                me_response = requests.get(
                    f"{self.backend_url}/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if me_response.status_code == 200:
                    print("✅ /auth/me endpoint working")
                else:
                    self.issues.append("/auth/me endpoint failing")
                    
            else:
                self.issues.append(f"Login endpoint failing: {response.status_code}")
                
        except Exception as e:
            self.issues.append(f"Authentication flow error: {str(e)}")
    
    def analyze_hr_endpoints(self):
        """Test HR-specific endpoints"""
        print("👩‍💼 Analyzing HR Endpoints...")
        
        # Get HR token first
        token = self._get_hr_token()
        if not token:
            self.issues.append("Cannot get HR token for testing")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test dashboard stats
        try:
            response = requests.get(f"{self.backend_url}/hr/dashboard-stats", headers=headers)
            if response.status_code == 200:
                print("✅ HR dashboard stats working")
            else:
                self.issues.append(f"HR dashboard stats failing: {response.status_code}")
        except Exception as e:
            self.issues.append(f"HR dashboard stats error: {str(e)}")
            
        # Test properties endpoint
        try:
            response = requests.get(f"{self.backend_url}/hr/properties", headers=headers)
            if response.status_code == 200:
                properties = response.json()
                print(f"✅ HR properties endpoint working ({len(properties)} properties)")
                
                # Check property structure
                if properties and isinstance(properties, list):
                    prop = properties[0]
                    required_fields = ['id', 'name', 'address', 'city', 'state', 'qr_code_url']
                    missing_fields = [field for field in required_fields if field not in prop]
                    if missing_fields:
                        self.gaps.append(f"Property missing fields: {missing_fields}")
                        
            else:
                self.issues.append(f"HR properties endpoint failing: {response.status_code}")
        except Exception as e:
            self.issues.append(f"HR properties error: {str(e)}")
            
        # Test applications endpoint
        try:
            response = requests.get(f"{self.backend_url}/hr/applications", headers=headers)
            if response.status_code == 200:
                applications = response.json()
                print(f"✅ HR applications endpoint working ({len(applications)} applications)")
            else:
                self.issues.append(f"HR applications endpoint failing: {response.status_code}")
        except Exception as e:
            self.issues.append(f"HR applications error: {str(e)}")
            
        # Test managers endpoint
        try:
            response = requests.get(f"{self.backend_url}/hr/managers", headers=headers)
            if response.status_code == 200:
                managers = response.json()
                print(f"✅ HR managers endpoint working ({len(managers)} managers)")
            else:
                self.issues.append(f"HR managers endpoint failing: {response.status_code}")
        except Exception as e:
            self.issues.append(f"HR managers error: {str(e)}")
    
    def analyze_manager_endpoints(self):
        """Test Manager-specific endpoints"""
        print("👨‍💼 Analyzing Manager Endpoints...")
        
        # Get manager token
        token = self._get_manager_token()
        if not token:
            self.issues.append("Cannot get Manager token for testing")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test manager applications
        try:
            response = requests.get(f"{self.backend_url}/manager/applications", headers=headers)
            if response.status_code == 200:
                applications = response.json()
                print(f"✅ Manager applications endpoint working ({len(applications)} applications)")
            else:
                self.issues.append(f"Manager applications endpoint failing: {response.status_code}")
        except Exception as e:
            self.issues.append(f"Manager applications error: {str(e)}")
            
        # Test manager property
        try:
            response = requests.get(f"{self.backend_url}/manager/property", headers=headers)
            if response.status_code == 200:
                property_data = response.json()
                print("✅ Manager property endpoint working")
            else:
                self.issues.append(f"Manager property endpoint failing: {response.status_code}")
        except Exception as e:
            self.issues.append(f"Manager property error: {str(e)}")
            
        # Test manager dashboard stats
        try:
            response = requests.get(f"{self.backend_url}/manager/dashboard-stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print("✅ Manager dashboard stats working")
            else:
                self.issues.append(f"Manager dashboard stats failing: {response.status_code}")
        except Exception as e:
            self.issues.append(f"Manager dashboard stats error: {str(e)}")
    
    def analyze_application_workflow(self):
        """Test application submission and approval workflow"""
        print("📝 Analyzing Application Workflow...")
        
        # Test public property info
        try:
            response = requests.get(f"{self.backend_url}/properties/prop_test_001/info")
            if response.status_code == 200:
                info = response.json()
                print("✅ Public property info working")
                
                # Check structure
                if 'property' not in info or 'departments_and_positions' not in info:
                    self.gaps.append("Property info missing required structure")
                    
            else:
                self.issues.append(f"Public property info failing: {response.status_code}")
        except Exception as e:
            self.issues.append(f"Public property info error: {str(e)}")
            
        # Test application submission (would need valid data)
        print("⚠️  Application submission test skipped (requires valid form data)")
        
        # Test approval workflow (would need pending application)
        print("⚠️  Approval workflow test skipped (requires pending application)")
    
    def analyze_email_notifications(self):
        """Test email notification system"""
        print("📧 Analyzing Email Notifications...")
        
        # Check if email service is configured
        try:
            # This is indirect - we can't directly test email without sending
            print("⚠️  Email notification test requires actual email sending")
            self.recommendations.append("Implement email notification testing endpoint")
        except Exception as e:
            self.issues.append(f"Email notification analysis error: {str(e)}")
    
    def analyze_data_consistency(self):
        """Check data consistency between endpoints"""
        print("🔍 Analyzing Data Consistency...")
        
        hr_token = self._get_hr_token()
        manager_token = self._get_manager_token()
        
        if not hr_token or not manager_token:
            self.issues.append("Cannot get tokens for consistency testing")
            return
            
        # Compare HR vs Manager application data
        try:
            hr_apps = requests.get(
                f"{self.backend_url}/hr/applications",
                headers={"Authorization": f"Bearer {hr_token}"}
            ).json()
            
            manager_apps = requests.get(
                f"{self.backend_url}/manager/applications", 
                headers={"Authorization": f"Bearer {manager_token}"}
            ).json()
            
            # Check if manager sees subset of HR applications
            if len(manager_apps) > len(hr_apps):
                self.issues.append("Manager seeing more applications than HR (data inconsistency)")
            else:
                print(f"✅ Data consistency check passed (HR: {len(hr_apps)}, Manager: {len(manager_apps)})")
                
        except Exception as e:
            self.issues.append(f"Data consistency check error: {str(e)}")
    
    def analyze_frontend_expectations(self):
        """Analyze what frontend expects vs what backend provides"""
        print("🖥️  Analyzing Frontend Expectations...")
        
        # Based on frontend code analysis, check common patterns
        expectations = [
            {
                "endpoint": "/hr/dashboard-stats",
                "expected_fields": ["totalProperties", "totalManagers", "totalEmployees", "pendingApplications"]
            },
            {
                "endpoint": "/hr/properties", 
                "expected_fields": ["id", "name", "address", "city", "state", "qr_code_url", "manager_ids"]
            },
            {
                "endpoint": "/hr/applications",
                "expected_fields": ["id", "property_id", "department", "position", "applicant_data", "status", "applied_at"]
            }
        ]
        
        hr_token = self._get_hr_token()
        if not hr_token:
            return
            
        headers = {"Authorization": f"Bearer {hr_token}"}
        
        for expectation in expectations:
            try:
                response = requests.get(f"{self.backend_url}{expectation['endpoint']}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list) and data:
                        # Check first item
                        item = data[0]
                        missing_fields = [field for field in expectation['expected_fields'] if field not in item]
                        if missing_fields:
                            self.gaps.append(f"{expectation['endpoint']} missing fields: {missing_fields}")
                    elif isinstance(data, dict):
                        missing_fields = [field for field in expectation['expected_fields'] if field not in data]
                        if missing_fields:
                            self.gaps.append(f"{expectation['endpoint']} missing fields: {missing_fields}")
                            
            except Exception as e:
                self.issues.append(f"Frontend expectation check error for {expectation['endpoint']}: {str(e)}")
    
    def analyze_error_handling(self):
        """Test error handling and response formats"""
        print("⚠️  Analyzing Error Handling...")
        
        # Test invalid endpoints
        try:
            response = requests.get(f"{self.backend_url}/invalid/endpoint")
            if response.status_code != 404:
                self.issues.append(f"Invalid endpoint should return 404, got {response.status_code}")
        except Exception as e:
            self.issues.append(f"Error handling test failed: {str(e)}")
            
        # Test unauthorized access
        try:
            response = requests.get(f"{self.backend_url}/hr/dashboard-stats")
            if response.status_code != 401:
                self.issues.append(f"Unauthorized access should return 401, got {response.status_code}")
        except Exception as e:
            self.issues.append(f"Unauthorized access test failed: {str(e)}")
    
    def _get_hr_token(self) -> Optional[str]:
        """Get HR authentication token"""
        try:
            response = requests.post(f"{self.backend_url}/auth/login", json={
                "email": "hr@hoteltest.com",
                "password": "admin123"
            })
            if response.status_code == 200:
                return response.json().get('token')
        except:
            pass
        return None
    
    def _get_manager_token(self) -> Optional[str]:
        """Get Manager authentication token"""
        try:
            response = requests.post(f"{self.backend_url}/auth/login", json={
                "email": "manager@hoteltest.com", 
                "password": "manager123"
            })
            if response.status_code == 200:
                return response.json().get('token')
        except:
            pass
        return None
    
    def run_comprehensive_analysis(self):
        """Run all analysis tests"""
        print("🚀 Starting Comprehensive Integration Analysis...")
        print("=" * 60)
        
        # Check if backend is running
        try:
            response = requests.get(f"{self.backend_url}/healthz", timeout=5)
            if response.status_code != 200:
                print("❌ Backend not responding properly")
                return
        except Exception as e:
            print(f"❌ Cannot connect to backend: {str(e)}")
            return
            
        print("✅ Backend is running")
        
        # Run all analysis functions
        self.analyze_authentication_flow()
        self.analyze_hr_endpoints()
        self.analyze_manager_endpoints()
        self.analyze_application_workflow()
        self.analyze_email_notifications()
        self.analyze_data_consistency()
        self.analyze_frontend_expectations()
        self.analyze_error_handling()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE INTEGRATION ANALYSIS REPORT")
        print("=" * 60)
        
        print(f"\n🔴 ISSUES FOUND ({len(self.issues)}):")
        for i, issue in enumerate(self.issues, 1):
            print(f"  {i}. {issue}")
            
        print(f"\n🟡 GAPS IDENTIFIED ({len(self.gaps)}):")
        for i, gap in enumerate(self.gaps, 1):
            print(f"  {i}. {gap}")
            
        print(f"\n🟢 RECOMMENDATIONS ({len(self.recommendations)}):")
        for i, rec in enumerate(self.recommendations, 1):
            print(f"  {i}. {rec}")
            
        # Additional recommendations based on analysis
        additional_recs = [
            "Implement consistent error response format across all endpoints",
            "Add request/response validation middleware",
            "Implement comprehensive API documentation with OpenAPI/Swagger",
            "Add endpoint versioning strategy",
            "Implement rate limiting for public endpoints",
            "Add comprehensive logging for debugging",
            "Implement health check endpoints for all services",
            "Add data validation at API boundary",
            "Implement consistent pagination for list endpoints",
            "Add bulk operation endpoints for better performance"
        ]
        
        print(f"\n💡 ADDITIONAL RECOMMENDATIONS:")
        for i, rec in enumerate(additional_recs, 1):
            print(f"  {i}. {rec}")
            
        print("\n" + "=" * 60)
        print("Analysis Complete!")

if __name__ == "__main__":
    analyzer = IntegrationAnalyzer()
    analyzer.run_comprehensive_analysis()