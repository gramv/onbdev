#!/usr/bin/env python3
"""
Test Token Welcome Endpoint
Tests the new /api/onboarding/welcome/{token} endpoint
"""
import requests
import json

def test_token_welcome_endpoint():
    """Test the new token-based welcome endpoint"""
    print("🔧 Testing Token Welcome Endpoint")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    test_token = "direct-test-token-1753727559"
    
    print(f"🔗 Testing endpoint: {base_url}/api/onboarding/welcome/{test_token}")
    print()
    
    try:
        # Test the new endpoint
        print("1. 🌟 Testing token-based welcome endpoint...")
        response = requests.get(f"{base_url}/api/onboarding/welcome/{test_token}")
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint is working!")
            data = response.json()
            
            print(f"   👤 Employee: {data.get('employee', {}).get('name', 'N/A')}")
            print(f"   🏨 Property: {data.get('property', {}).get('name', 'N/A')}")
            print(f"   💼 Job Title: {data.get('job_details', {}).get('job_title', 'N/A')}")
            print(f"   📅 Start Date: {data.get('job_details', {}).get('start_date', 'N/A')}")
            print(f"   🎯 Onboarding Status: {data.get('onboarding_info', {}).get('status', 'N/A')}")
            
            return True
            
        elif response.status_code == 404:
            print("❌ Token not found - this might be expected if no onboarding session exists")
            print(f"   Response: {response.text}")
            return False
            
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend")
        print("   Make sure the backend is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Token Welcome Endpoint Test")
    print("🎯 Testing the new /api/onboarding/welcome/{token} endpoint")
    print()
    
    success = test_token_welcome_endpoint()
    
    if success:
        print("\n🎉 SUCCESS! Token welcome endpoint is working!")
        print("🌟 The frontend should now be able to load welcome data!")
    else:
        print("\n💥 FAILED! Token welcome endpoint has issues")
        print("💡 This might be because no onboarding session exists with that token")
        print("   You may need to create test data or use a different token")

if __name__ == "__main__":
    main()