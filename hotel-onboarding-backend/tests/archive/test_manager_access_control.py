#!/usr/bin/env python3
"""
Test manager access control for QR code generation
"""
import requests
import json

def test_manager_access_control():
    """Test that managers can only access their assigned properties"""
    base_url = "http://localhost:8000"
    
    # Login as manager
    login_data = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    try:
        print("🔐 Logging in as Manager...")
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Manager login failed: {login_response.status_code}")
            return False
        
        login_result = login_response.json()
        token = login_result["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Manager login successful")
        
        # Test access to assigned property (should work)
        assigned_property_id = "prop_test_001"
        print(f"📱 Testing access to assigned property {assigned_property_id}...")
        qr_response = requests.post(f"{base_url}/hr/properties/{assigned_property_id}/qr-code", headers=headers)
        
        if qr_response.status_code == 200:
            print("✅ Manager can access assigned property")
        else:
            print(f"❌ Manager cannot access assigned property: {qr_response.status_code}")
            return False
        
        # Test access to non-existent property (should fail)
        fake_property_id = "fake_property_123"
        print(f"📱 Testing access to non-existent property {fake_property_id}...")
        fake_response = requests.post(f"{base_url}/hr/properties/{fake_property_id}/qr-code", headers=headers)
        
        if fake_response.status_code == 404:
            print("✅ Manager correctly denied access to non-existent property")
        else:
            print(f"❌ Unexpected response for non-existent property: {fake_response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Manager Access Control")
    print("=" * 35)
    
    success = test_manager_access_control()
    
    if success:
        print("\n🎉 Access control test passed!")
    else:
        print("\n❌ Access control test failed!")
        
    exit(0 if success else 1)