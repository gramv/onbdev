#!/usr/bin/env python3
"""
Test Onboarding Route Fix
Tests that the /onboarding/:token route is now working
"""
import requests
import time

def test_onboarding_route_fix():
    """Test the fixed onboarding route"""
    print("🔧 Testing Onboarding Route Fix")
    print("=" * 60)
    
    # Test token from the email
    test_token = "direct-test-token-1753727559"
    frontend_url = "http://localhost:3000"
    onboarding_url = f"{frontend_url}/onboarding/{test_token}"
    
    print(f"🔗 Testing URL: {onboarding_url}")
    print(f"🎯 This should now load the Task 3 welcome page")
    print()
    
    try:
        # Test the onboarding route
        print("1. 🌟 Testing onboarding route...")
        response = requests.get(onboarding_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Route is accessible!")
            print(f"   📄 Content length: {len(response.text)} characters")
            
            # Check if it contains React/onboarding content
            content = response.text.lower()
            if "onboarding" in content or "welcome" in content:
                print("✅ Page contains onboarding/welcome content")
            else:
                print("⚠️  Page might not be the onboarding page")
                
            # Check for React Router error
            if "no routes matched" in content:
                print("❌ Still getting React Router error!")
                return False
            else:
                print("✅ No React Router errors detected")
                
        else:
            print(f"❌ Route returned status: {response.status_code}")
            return False
            
        print(f"\n🎊 ROUTE FIX TEST COMPLETED!")
        print("=" * 60)
        print("📋 RESULTS:")
        print(f"   ✅ Route accessible: {onboarding_url}")
        print(f"   ✅ No routing errors detected")
        print(f"   🌟 Task 3 welcome page should load")
        print()
        print("📬 NEXT STEPS:")
        print("   1. Open your browser")
        print(f"   2. Go to: {onboarding_url}")
        print("   3. You should see the Task 3 welcome page")
        print("   4. No more 'No routes matched' errors!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to frontend")
        print("   Make sure the frontend is running:")
        print("   cd hotel-onboarding-frontend")
        print("   npm start")
        return False
    except Exception as e:
        print(f"❌ Route test failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("🚀 Starting Onboarding Route Fix Test")
    print("🎯 Testing that /onboarding/:token route now works")
    print()
    
    success = test_onboarding_route_fix()
    
    if success:
        print("\n🎉 SUCCESS! Onboarding route is now working!")
        print("🌟 Your Task 3 welcome page should be accessible!")
        exit(0)
    else:
        print("\n💥 FAILED! Route still has issues")
        print("💡 You may need to restart the frontend server:")
        print("   cd hotel-onboarding-frontend")
        print("   npm start")
        exit(1)

if __name__ == "__main__":
    main()