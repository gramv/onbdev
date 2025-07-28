#!/usr/bin/env python3
"""
Comprehensive test for QR Code Implementation - Task 5
"""
import requests
import json
import os
from datetime import datetime, timezone, timedelta
import jwt

# Test configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"
SECRET_KEY = "hotel-onboarding-super-secret-key-2025"

def create_hr_token() -> str:
    """Create HR JWT token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "user_id": "hr_test_001",
        "token_type": "hr_auth",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def create_manager_token() -> str:
    """Create Manager JWT token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "manager_id": "mgr_test_001",
        "token_type": "manager_auth",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def test_backend_qr_generation():
    """Test backend QR code generation endpoint"""
    print("🧪 Testing Backend QR Code Generation...")
    
    hr_token = create_hr_token()
    headers = {"Authorization": f"Bearer {hr_token}"}
    
    # Test QR code generation for HR
    response = requests.post(f"{BACKEND_URL}/hr/properties/prop_test_001/qr-code", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ HR QR Code generation successful!")
        print(f"   Property: {data.get('property_name')}")
        print(f"   Application URL: {data.get('application_url')}")
        print(f"   Has QR Code: {'✅' if data.get('qr_code_url') else '❌'}")
        print(f"   Has Printable QR: {'✅' if data.get('printable_qr_url') else '❌'}")
        
        # Test Manager access
        manager_token = create_manager_token()
        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        
        manager_response = requests.post(f"{BACKEND_URL}/hr/properties/prop_test_001/qr-code", headers=manager_headers)
        
        if manager_response.status_code == 200:
            print("✅ Manager QR Code generation successful!")
            return True
        else:
            print(f"❌ Manager QR Code generation failed: {manager_response.status_code}")
            print(f"   Error: {manager_response.text}")
            return False
    else:
        print(f"❌ HR QR Code generation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_properties_endpoint():
    """Test properties endpoint for QR code data"""
    print("\n🧪 Testing Properties Endpoint...")
    
    hr_token = create_hr_token()
    headers = {"Authorization": f"Bearer {hr_token}"}
    
    response = requests.get(f"{BACKEND_URL}/hr/properties", headers=headers)
    
    if response.status_code == 200:
        properties = response.json()
        if properties:
            prop = properties[0]
            print("✅ Properties endpoint successful!")
            print(f"   Property: {prop.get('name')}")
            print(f"   Has QR Code URL: {'✅' if prop.get('qr_code_url') else '❌'}")
            return True
        else:
            print("❌ No properties found")
            return False
    else:
        print(f"❌ Properties endpoint failed: {response.status_code}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("\n🧪 Testing Frontend Accessibility...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible!")
            print(f"   Status: {response.status_code}")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_qr_code_components():
    """Test QR code component implementation"""
    print("\n🧪 Testing QR Code Component Implementation...")
    
    # Check if QR code display component exists
    import os
    qr_component_path = "hotel-onboarding-frontend/src/components/ui/qr-code-display.tsx"
    
    if os.path.exists(qr_component_path):
        print("✅ QR Code Display component exists!")
        
        # Check component content
        with open(qr_component_path, 'r') as f:
            content = f.read()
            
        required_features = [
            "QRCodeDisplay",
            "QRCodeCard", 
            "handlePrint",
            "handleDownload",
            "handleRegenerateQR",
            "printable_qr_url"
        ]
        
        missing_features = []
        for feature in required_features:
            if feature not in content:
                missing_features.append(feature)
        
        if not missing_features:
            print("✅ All required QR code features implemented!")
            return True
        else:
            print(f"❌ Missing features: {missing_features}")
            return False
    else:
        print("❌ QR Code Display component not found!")
        return False

def test_properties_tab_integration():
    """Test PropertiesTab integration"""
    print("\n🧪 Testing PropertiesTab Integration...")
    
    properties_tab_path = "hotel-onboarding-frontend/src/components/dashboard/PropertiesTab.tsx"
    
    if os.path.exists(properties_tab_path):
        with open(properties_tab_path, 'r') as f:
            content = f.read()
        
        integration_checks = [
            "QRCodeDisplay",
            "qr-code-display",
            "onRegenerate={fetchProperties}"
        ]
        
        missing_integrations = []
        for check in integration_checks:
            if check not in content:
                missing_integrations.append(check)
        
        if not missing_integrations:
            print("✅ PropertiesTab QR integration complete!")
            return True
        else:
            print(f"❌ Missing integrations: {missing_integrations}")
            return False
    else:
        print("❌ PropertiesTab component not found!")
        return False

def test_manager_dashboard_integration():
    """Test ManagerDashboard integration"""
    print("\n🧪 Testing ManagerDashboard Integration...")
    
    manager_dashboard_path = "hotel-onboarding-frontend/src/pages/ManagerDashboard.tsx"
    
    if os.path.exists(manager_dashboard_path):
        with open(manager_dashboard_path, 'r') as f:
            content = f.read()
        
        integration_checks = [
            "QRCodeCard",
            "qr-code-display",
            "onRegenerate={fetchPropertyData}"
        ]
        
        missing_integrations = []
        for check in integration_checks:
            if check not in content:
                missing_integrations.append(check)
        
        if not missing_integrations:
            print("✅ ManagerDashboard QR integration complete!")
            return True
        else:
            print(f"❌ Missing integrations: {missing_integrations}")
            return False
    else:
        print("❌ ManagerDashboard component not found!")
        return False

def main():
    """Run all QR code implementation tests"""
    print("🚀 Starting QR Code Implementation Tests (Task 5)...\n")
    
    tests = [
        ("Backend QR Generation", test_backend_qr_generation),
        ("Properties Endpoint", test_properties_endpoint),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("QR Code Components", test_qr_code_components),
        ("PropertiesTab Integration", test_properties_tab_integration),
        ("ManagerDashboard Integration", test_manager_dashboard_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 QR CODE IMPLEMENTATION TEST RESULTS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All QR code functionality tests passed!")
        print("✅ Task 5 - Frontend QR Code Display and Printing - COMPLETED")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Review implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)