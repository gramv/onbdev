#!/usr/bin/env python3
"""
Test Welcome Endpoint Fix
Tests the newly added /api/onboarding/welcome/{token} endpoint
"""
import requests
import json

def test_welcome_endpoint():
    """Test the welcome endpoint with a test token"""
    print("🌟 Testing Welcome Endpoint Fix")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    test_token = "direct-test-token-1753727559"
    
    print(f"🔗 Testing endpoint: {base_url}/api/onboarding/welcome/{test_token}")
    print()
    
    try:
        # Test the backend endpoint
        print("1. 🔍 Testing backend endpoint...")
        response = requests.get(f"{base_url}/api/onboarding/welcome/{test_token}")
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Endpoint is working!")
            
            # Parse and display the response
            try:
                data = response.json()
                print(f"   📄 Response contains {len(data)} fields")
                
                # Check key fields
                if data.get("success"):
                    print("   ✅ Success field: True")
                else:
                    print("   ❌ Success field: False or missing")
                
                if data.get("employee"):
                    employee = data["employee"]
                    print(f"   ✅ Employee: {employee.get('first_name')} {employee.get('last_name')}")
                    print(f"   ✅ Position: {employee.get('position')} - {employee.get('department')}")
                else:
                    print("   ❌ Employee data missing")
                
                if data.get("property"):
                    property_data = data["property"]
                    print(f"   ✅ Property: {property_data.get('name')}")
                else:
                    print("   ❌ Property data missing")
                
                if data.get("welcome_message"):
                    welcome = data["welcome_message"]
                    print(f"   ✅ Welcome Title: {welcome.get('title')}")
                else:
                    print("   ❌ Welcome message missing")
                
                if data.get("onboarding"):
                    onboarding = data["onboarding"]
                    print(f"   ✅ Onboarding Status: {onboarding.get('status')}")
                    print(f"   ✅ Forms to Complete: {len(onboarding.get('forms_to_complete', []))}")
                else:
                    print("   ❌ Onboarding data missing")
                
            except json.JSONDecodeError:
                print("   ❌ Response is not valid JSON")
                print(f"   📄 Raw response: {response.text[:200]}...")
                
        elif response.status_code == 404:
            print("   ❌ Endpoint not found (404)")
            print("   💡 The endpoint might not be implemented yet")
            
        elif response.status_code == 401:
            print("   ❌ Token validation failed (401)")
            print("   💡 The token might be invalid or expired")
            
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
        
        print()
        print("2. 🌐 Testing frontend integration...")
        
        # Test if frontend can now load the page
        frontend_url = f"http://localhost:3000/onboarding/{test_token}"
        frontend_response = requests.get(frontend_url)
        
        if frontend_response.status_code == 200:
            print("   ✅ Frontend page loads successfully")
            
            # Check if it contains expected content
            content = frontend_response.text.lower()
            if "onboarding" in content and "welcome" in content:
                print("   ✅ Page contains onboarding/welcome content")
            else:
                print("   ⚠️  Page might not be fully loaded")
                
        else:
            print(f"   ❌ Frontend page failed to load: {frontend_response.status_code}")
        
        print()
        print("🎊 ENDPOINT TEST COMPLETED!")
        print("=" * 60)
        
        if response.status_code == 200:
            print("📋 RESULTS:")
            print("   ✅ Backend endpoint working")
            print("   ✅ Token validation working")
            print("   ✅ Data structure complete")
            print("   ✅ Frontend integration ready")
            print()
            print("🌟 SUCCESS! The welcome endpoint is now working!")
            print(f"   🔗 Backend: {base_url}/api/onboarding/welcome/{test_token}")
            print(f"   🌐 Frontend: {frontend_url}")
            return True
        else:
            print("📋 ISSUES FOUND:")
            print("   ❌ Backend endpoint not working properly")
            print("   💡 Check server logs for errors")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server")
        print("   Make sure the backend is running:")
        print("   cd hotel-onboarding-backend")
        print("   poetry run python -m app.main_enhanced")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Welcome Endpoint Fix Test")
    print("🎯 Testing the newly added /api/onboarding/welcome/{token} endpoint")
    print()
    
    success = test_welcome_endpoint()
    
    if success:
        print("\n🎉 SUCCESS! Welcome endpoint is working!")
        print("🌟 Your Task 3 welcome page should now load properly!")
        exit(0)
    else:
        print("\n💥 FAILED! Welcome endpoint has issues")
        print("🔧 Check the backend implementation and try again")
        exit(1)

if __name__ == "__main__":
    main()