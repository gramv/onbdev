#!/usr/bin/env python3

"""
QR URL Diagnosis - Step by step investigation
"""

import requests
import sys

def test_frontend_route():
    """Test if the frontend route /apply/:propertyId actually works"""
    print("🔍 STEP 1: Testing Frontend Route Directly")
    
    test_url = "http://localhost:3000/apply/prop_test_001"
    print(f"Testing URL: {test_url}")
    
    try:
        response = requests.get(test_url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"Content Length: {len(content)} characters")
            
            # Check if it's actually serving the React app
            if "<!DOCTYPE html>" in content:
                print("✅ Returns HTML content")
                
                if "react" in content.lower() or "vite" in content.lower():
                    print("✅ Appears to be React/Vite app")
                else:
                    print("⚠️  HTML but may not be React app")
                    
                # Check for job application specific content
                if "job" in content.lower() or "application" in content.lower():
                    print("✅ Contains job/application related content")
                else:
                    print("⚠️  No job/application content detected")
                    
                return True
            else:
                print("❌ Not returning HTML content")
                print(f"Content preview: {content[:200]}...")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_frontend_root():
    """Test if frontend root is accessible"""
    print("\n🔍 STEP 2: Testing Frontend Root")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        print(f"Frontend root status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Frontend root accessible")
            return True
        else:
            print("❌ Frontend root not accessible")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend root failed: {e}")
        return False

def test_react_routing():
    """Test if React Router is handling the route"""
    print("\n🔍 STEP 3: Testing React Router Configuration")
    
    # Test a few different routes to see routing behavior
    test_routes = [
        "http://localhost:3000/",
        "http://localhost:3000/login", 
        "http://localhost:3000/apply/prop_test_001",
        "http://localhost:3000/nonexistent-route"
    ]
    
    for route in test_routes:
        try:
            response = requests.get(route, timeout=5)
            print(f"{route} -> {response.status_code}")
            
            # Check if all routes return the same HTML (SPA behavior)
            if response.status_code == 200:
                content_length = len(response.text)
                print(f"  Content length: {content_length}")
                
        except requests.exceptions.RequestException as e:
            print(f"{route} -> ERROR: {e}")

def check_vite_config():
    """Check if Vite is configured for SPA routing"""
    print("\n🔍 STEP 4: Checking Vite Configuration")
    
    try:
        with open("hotel-onboarding-frontend/vite.config.ts", "r") as f:
            config = f.read()
            
        print("Vite config found")
        
        # Check for SPA fallback configuration
        if "historyApiFallback" in config or "index.html" in config:
            print("✅ SPA routing configuration detected")
        else:
            print("⚠️  No explicit SPA routing configuration")
            
        # Check server configuration
        if "server" in config:
            print("✅ Server configuration present")
        else:
            print("⚠️  No server configuration")
            
    except FileNotFoundError:
        print("❌ Vite config not found")
    except Exception as e:
        print(f"❌ Error reading Vite config: {e}")

def check_app_routing():
    """Check App.tsx routing configuration"""
    print("\n🔍 STEP 5: Checking App.tsx Routing")
    
    try:
        with open("hotel-onboarding-frontend/src/App.tsx", "r") as f:
            app_content = f.read()
            
        print("App.tsx found")
        
        # Check for the apply route
        if '/apply/:propertyId' in app_content:
            print("✅ /apply/:propertyId route found in App.tsx")
        else:
            print("❌ /apply/:propertyId route NOT found in App.tsx")
            
        # Check for JobApplicationForm import
        if 'JobApplicationForm' in app_content:
            print("✅ JobApplicationForm component imported")
        else:
            print("❌ JobApplicationForm component NOT imported")
            
        # Check for Router setup
        if 'BrowserRouter' in app_content or 'Router' in app_content:
            print("✅ Router setup detected")
        else:
            print("❌ No Router setup detected")
            
    except FileNotFoundError:
        print("❌ App.tsx not found")
    except Exception as e:
        print(f"❌ Error reading App.tsx: {e}")

def main():
    print("🚨 QR URL DIAGNOSIS - ROOT CAUSE INVESTIGATION")
    print("=" * 60)
    
    # Step 1: Test the actual URL
    frontend_works = test_frontend_route()
    
    # Step 2: Test frontend root
    root_works = test_frontend_root()
    
    # Step 3: Test routing behavior
    test_react_routing()
    
    # Step 4: Check Vite config
    check_vite_config()
    
    # Step 5: Check App routing
    check_app_routing()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS SUMMARY:")
    
    if not root_works:
        print("❌ ISSUE: Frontend server not accessible")
        print("   SOLUTION: Restart frontend server on port 3000")
        
    elif not frontend_works:
        print("❌ ISSUE: /apply/:propertyId route not working")
        print("   POSSIBLE CAUSES:")
        print("   - React Router not configured properly")
        print("   - Vite not serving SPA correctly")
        print("   - JobApplicationForm component missing/broken")
        
    else:
        print("✅ Frontend route appears to be working")
        print("   The issue might be elsewhere (QR generation, etc.)")
        
    print("\n🔧 NEXT STEPS:")
    print("1. Fix any issues identified above")
    print("2. Test the complete QR code generation flow")
    print("3. Verify QR codes contain correct URLs")

if __name__ == "__main__":
    main()