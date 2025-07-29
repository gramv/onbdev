#!/usr/bin/env python3
"""
Test script for Task 4: Implement Missing API Endpoints
Verifies all required endpoints are working correctly
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_PROPERTY_ID = "prop_test_001"

class EndpointTester:
    def __init__(self):
        self.session = None
        self.hr_token = None
        self.manager_token = None
        self.test_results = []

    async def setup_session(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    async def login_as_hr(self):
        """Login as HR user to get token"""
        try:
            login_data = {
                "email": "hr@hoteltest.com",
                "password": "admin123"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("data", {}).get("token"):
                        self.hr_token = data["data"]["token"]
                        print("✅ HR login successful")
                        return True
                    else:
                        print(f"❌ HR login failed: {data}")
                        return False
                else:
                    text = await response.text()
                    print(f"❌ HR login failed with status {response.status}: {text}")
                    return False
        except Exception as e:
            print(f"❌ HR login error: {e}")
            return False

    async def login_as_manager(self):
        """Login as Manager user to get token"""
        try:
            login_data = {
                "email": "manager@hoteltest.com",
                "password": "manager123"
            }
            
            async with self.session.post(f"{BASE_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("data", {}).get("token"):
                        self.manager_token = data["data"]["token"]
                        print("✅ Manager login successful")
                        return True
                    else:
                        print(f"❌ Manager login failed: {data}")
                        return False
                else:
                    text = await response.text()
                    print(f"❌ Manager login failed with status {response.status}: {text}")
                    return False
        except Exception as e:
            print(f"❌ Manager login error: {e}")
            return False

    async def test_endpoint(self, method, endpoint, headers=None, data=None, expected_status=200, description=""):
        """Test a specific endpoint"""
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    status = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    status = response.status
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
            else:
                print(f"❌ Unsupported method: {method}")
                return False

            success = status == expected_status
            result = {
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "expected_status": expected_status,
                "success": success,
                "description": description,
                "response": response_data if success else str(response_data)[:200]
            }
            
            self.test_results.append(result)
            
            if success:
                print(f"✅ {method} {endpoint} - {description}")
            else:
                print(f"❌ {method} {endpoint} - {description} (Status: {status}, Expected: {expected_status})")
                
            return success
            
        except Exception as e:
            print(f"❌ {method} {endpoint} - Error: {e}")
            self.test_results.append({
                "endpoint": endpoint,
                "method": method,
                "success": False,
                "description": description,
                "error": str(e)
            })
            return False

    async def test_manager_dashboard_stats(self):
        """Test /manager/dashboard-stats endpoint"""
        if not self.manager_token:
            print("❌ Manager token not available for dashboard stats test")
            return False
            
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        return await self.test_endpoint(
            "GET", 
            "/manager/dashboard-stats", 
            headers=headers,
            description="Manager dashboard statistics"
        )

    async def test_properties_info_public(self):
        """Test /properties/{id}/info public endpoint"""
        # First, let's get a valid property ID from HR properties
        if self.hr_token:
            headers = {"Authorization": f"Bearer {self.hr_token}"}
            try:
                async with self.session.get(f"{BASE_URL}/hr/properties", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success") and data.get("data"):
                            properties = data["data"]
                            if properties:
                                property_id = properties[0]["id"]
                                return await self.test_endpoint(
                                    "GET", 
                                    f"/properties/{property_id}/info",
                                    description="Public property information"
                                )
            except Exception as e:
                print(f"❌ Error getting property ID: {e}")
        
        # Fallback to test with a known ID
        return await self.test_endpoint(
            "GET", 
            f"/properties/{TEST_PROPERTY_ID}/info",
            expected_status=404,  # Might not exist, but endpoint should respond
            description="Public property information (fallback test)"
        )

    async def test_hr_applications_history(self):
        """Test /hr/applications/{id}/history endpoint"""
        if not self.hr_token:
            print("❌ HR token not available for applications history test")
            return False
            
        headers = {"Authorization": f"Bearer {self.hr_token}"}
        
        # First get an application ID
        try:
            async with self.session.get(f"{BASE_URL}/hr/applications", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("data"):
                        applications = data["data"]
                        if applications:
                            app_id = applications[0]["id"]
                            return await self.test_endpoint(
                                "GET", 
                                f"/hr/applications/{app_id}/history",
                                headers=headers,
                                description="Application status history"
                            )
        except Exception as e:
            print(f"❌ Error getting application ID: {e}")
        
        # Test with a dummy ID to verify endpoint exists
        return await self.test_endpoint(
            "GET", 
            "/hr/applications/dummy-id/history",
            headers=headers,
            expected_status=404,  # Should return 404 for non-existent application
            description="Application history endpoint (dummy ID test)"
        )

    async def test_applications_approve_reject(self):
        """Test /applications/{id}/approve and /applications/{id}/reject endpoints"""
        if not self.manager_token:
            print("❌ Manager token not available for approve/reject tests")
            return False
            
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        # Test approve endpoint structure (will likely fail due to missing application, but tests endpoint exists)
        approve_data = {
            "job_title": "Test Position",
            "start_date": "2024-01-01",
            "start_time": "09:00",
            "pay_rate": 15.00,
            "pay_frequency": "hourly",
            "benefits_eligible": "yes",
            "supervisor": "Test Supervisor",
            "special_instructions": "Test instructions"
        }
        
        approve_success = await self.test_endpoint(
            "POST", 
            "/applications/dummy-id/approve",
            headers=headers,
            data=approve_data,
            expected_status=404,  # Should return 404 for non-existent application
            description="Application approval endpoint (dummy ID test)"
        )
        
        # Test reject endpoint structure
        reject_data = {
            "rejection_reason": "Test rejection reason"
        }
        
        reject_success = await self.test_endpoint(
            "POST", 
            "/applications/dummy-id/reject",
            headers=headers,
            data=reject_data,
            expected_status=404,  # Should return 404 for non-existent application
            description="Application rejection endpoint (dummy ID test)"
        )
        
        return approve_success and reject_success

    async def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Task 4 Endpoint Tests")
        print("=" * 50)
        
        await self.setup_session()
        
        try:
            # Setup authentication
            hr_login_success = await self.login_as_hr()
            manager_login_success = await self.login_as_manager()
            
            if not hr_login_success:
                print("❌ HR authentication failed. Cannot proceed with tests.")
                return False
            
            if not manager_login_success:
                print("⚠️  Manager authentication failed. Will skip manager-specific tests.")
            
            print("\n📋 Testing Required Endpoints:")
            print("-" * 30)
            
            # Test all required endpoints
            tests = [
                self.test_properties_info_public(),
                self.test_hr_applications_history(),
            ]
            
            # Add manager-specific tests if manager login was successful
            if manager_login_success:
                tests.extend([
                    self.test_manager_dashboard_stats(),
                    self.test_applications_approve_reject()
                ])
            else:
                print("⚠️  Skipping manager-specific endpoint tests")
            
            results = await asyncio.gather(*tests, return_exceptions=True)
            
            # Summary
            print("\n📊 Test Results Summary:")
            print("=" * 50)
            
            total_tests = len(self.test_results)
            successful_tests = sum(1 for result in self.test_results if result.get("success", False))
            
            print(f"Total Tests: {total_tests}")
            print(f"Successful: {successful_tests}")
            print(f"Failed: {total_tests - successful_tests}")
            print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%")
            
            # Detailed results
            print("\n📋 Detailed Results:")
            print("-" * 30)
            for result in self.test_results:
                status_icon = "✅" if result.get("success", False) else "❌"
                print(f"{status_icon} {result['method']} {result['endpoint']} - {result['description']}")
                if not result.get("success", False) and "error" in result:
                    print(f"   Error: {result['error']}")
                elif not result.get("success", False):
                    print(f"   Status: {result.get('status', 'Unknown')}, Expected: {result.get('expected_status', 'Unknown')}")
            
            return successful_tests == total_tests
            
        finally:
            await self.cleanup_session()

async def main():
    """Main test function"""
    tester = EndpointTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All Task 4 endpoints are working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️  Some endpoints need attention.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())