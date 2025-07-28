#!/usr/bin/env python3
"""
Test script to verify QR code functionality
"""
import requests
import json
from datetime import datetime, timezone, timedelta
import jwt

# Test configuration
BASE_URL = "http://localhost:8000"
SECRET_KEY = "hotel-onboarding-super-secret-key-2025"  # This should match the one in main_enhanced.py

def create_test_token(user_id: str, role: str = "hr") -> str:
    """Create a test JWT token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    if role == "hr":
        payload = {
            "user_id": user_id,
            "token_type": "hr_auth",
            "exp": expire
        }
    else:
        payload = {
            "manager_id": user_id,
            "token_type": "manager_auth",
            "exp": expire
        }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def test_qr_generation():
    """Test QR code generation endpoint"""
    print("🧪 Testing QR Code Generation...")
    
    # Create HR token
    hr_token = create_test_token("hr_test_001", "hr")
    headers = {"Authorization": f"Bearer {hr_token}"}
    
    # Test QR code generation
    property_id = "prop_test_001"
    response = requests.post(f"{BASE_URL}/hr/properties/{property_id}/qr-code", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ QR Code generated successfully!")
        print(f"   Property: {data.get('property_name')}")
        print(f"   Application URL: {data.get('application_url')}")
        print(f"   QR Code URL length: {len(data.get('qr_code_url', ''))}")
        print(f"   Printable QR URL length: {len(data.get('printable_qr_url', ''))}")
        return True
    else:
        print(f"❌ QR Code generation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_property_info():
    """Test public property info endpoint"""
    print("\n🧪 Testing Property Info Endpoint...")
    
    property_id = "prop_test_001"
    response = requests.get(f"{BASE_URL}/properties/{property_id}/info")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Property info retrieved successfully!")
        print(f"   Property: {data.get('name')}")
        print(f"   Address: {data.get('address')}")
        return True
    else:
        print(f"❌ Property info failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

if __name__ == "__main__":
    print("🚀 Starting QR Code Functionality Tests...\n")
    
    # Test QR generation
    qr_success = test_qr_generation()
    
    # Test property info
    info_success = test_property_info()
    
    print(f"\n📊 Test Results:")
    print(f"   QR Generation: {'✅ PASS' if qr_success else '❌ FAIL'}")
    print(f"   Property Info: {'✅ PASS' if info_success else '❌ FAIL'}")
    
    if qr_success and info_success:
        print("\n🎉 All QR code functionality tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the backend implementation.")