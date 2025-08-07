#!/usr/bin/env python3

"""
QR Code Link Fix Verification Test
Tests that QR codes generate correct URLs and that the frontend responds properly
"""

import requests
import time
import subprocess
import sys
import os

def test_qr_link_functionality():
    print("🔍 Testing QR Code Link Functionality...\n")
    
    # Test 1: Backend QR Generation
    print("1️⃣ Testing Backend QR Generation...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/properties/prop_test_001/qr-code", timeout=5)
        if response.status_code == 200:
            qr_data = response.json()
            application_url = qr_data.get('application_url', '')
            print(f"✅ QR Code generated successfully")
            print(f"   Application URL: {application_url}")
            
            # Verify URL format
            if "http://localhost:3000/apply/" in application_url:
                print("✅ QR Code URL uses correct port (3000)")
            else:
                print(f"❌ QR Code URL uses wrong port: {application_url}")
                return False
        else:
            print(f"❌ QR Generation failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False
    
    # Test 2: Frontend Accessibility
    print("\n2️⃣ Testing Frontend Accessibility...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible on port 3000")
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible on port 3000: {e}")
        return False
    
    # Test 3: Job Application Route
    print("\n3️⃣ Testing Job Application Route...")
    try:
        response = requests.get("http://localhost:3000/apply/prop_test_001", timeout=5)
        if response.status_code == 200:
            print("✅ Job application route accessible")
            
            # Check if it's the React app (should contain React-related content)
            content = response.text
            if "<!DOCTYPE html>" in content and ("react" in content.lower() or "vite" in content.lower()):
                print("✅ Route serves React application")
            else:
                print("⚠️  Route accessible but may not be serving React app")
        else:
            print(f"❌ Job application route failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Job application route not accessible: {e}")
        return False
    
    # Test 4: Property Info API
    print("\n4️⃣ Testing Property Info API...")
    try:
        response = requests.get("http://127.0.0.1:8000/api/properties/prop_test_001/info", timeout=5)
        if response.status_code == 200:
            property_info = response.json()
            print("✅ Property info API working")
            print(f"   Property: {property_info.get('property', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ Property info API failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Property info API not accessible: {e}")
        return False
    
    return True

def check_server_status():
    print("🔍 Checking Server Status...\n")
    
    # Check backend
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend server running on port 8000")
        else:
            print("❌ Backend server not healthy")
            return False
    except:
        print("❌ Backend server not running on port 8000")
        return False
    
    # Check frontend
    try:
        response = requests.get("http://localhost:3000", timeout=3)
        if response.status_code == 200:
            print("✅ Frontend server running on port 3000")
        else:
            print("❌ Frontend server not healthy")
            return False
    except:
        print("❌ Frontend server not running on port 3000")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 QR Code Link Fix Verification\n")
    
    # Check if servers are running
    if not check_server_status():
        print("\n❌ Servers not running properly. Please start them first:")
        print("   Backend: cd hotel-onboarding-backend && python3 -m app.main_enhanced")
        print("   Frontend: cd hotel-onboarding-frontend && npm run dev")
        sys.exit(1)
    
    # Run QR functionality tests
    print("\n" + "="*50)
    if test_qr_link_functionality():
        print("\n🎉 ALL QR CODE TESTS PASSED!")
        print("✅ QR codes now generate correct URLs")
        print("✅ Frontend accessible on correct port")
        print("✅ Job application route working")
        print("✅ QR code links should work properly")
        print("\n🔗 Test QR Code URL: http://localhost:3000/apply/prop_test_001")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("⚠️  QR code links may not work properly")
        sys.exit(1)
    
    print("="*50)