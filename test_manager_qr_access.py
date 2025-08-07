#!/usr/bin/env python3
"""
Test Manager QR Code Access

This test verifies that managers can access QR code functionality for their assigned properties.
"""

import requests
import json
import sys

BACKEND_URL = "http://localhost:8000"

def test_manager_qr_access():
    """Test manager access to QR code functionality"""
    
    print("🧪 TESTING MANAGER QR CODE ACCESS")
    print("=" * 50)
    
    # Step 1: Login as HR to set up test data
    print("\n1️⃣  HR LOGIN (Setup)")
    hr_login = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=hr_login)
    if response.status_code != 200:
        print("❌ HR login failed")
        return False
    
    hr_auth = response.json()
    hr_token = hr_auth["token"]
    hr_headers = {"Authorization": f"Bearer {hr_token}"}
    print("✅ HR logged in successfully")
    
    # Step 2: Get existing property
    print("\n2️⃣  GET PROPERTY")
    response = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get properties")
        return False
    
    properties = response.json()
    if not properties:
        print("❌ No properties found")
        return False
    
    property_id = properties[0]["id"]
    property_name = properties[0]["name"]
    print(f"✅ Using property: {property_name} (ID: {property_id})")
    
    # Step 3: Get manager and assign to property
    print("\n3️⃣  ASSIGN MANAGER TO PROPERTY")
    response = requests.get(f"{BACKEND_URL}/hr/managers", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get managers")
        return False
    
    managers = response.json()
    if not managers:
        print("❌ No managers found")
        return False
    
    manager_id = managers[0]["id"]
    manager_email = managers[0]["email"]
    print(f"✅ Found manager: {manager_email} (ID: {manager_id})")
    
    # Assign manager to property
    assign_data = {"manager_id": manager_id}
    response = requests.post(f"{BACKEND_URL}/hr/properties/{property_id}/managers", 
                           json=assign_data, headers=hr_headers)
    
    if response.status_code == 200:
        print("✅ Manager assigned to property successfully")
    else:
        print(f"⚠️  Manager assignment response: {response.status_code} - {response.text}")
        # Continue anyway, manager might already be assigned
    
    # Step 4: Login as manager
    print("\n4️⃣  MANAGER LOGIN")
    manager_login = {
        "email": "manager@hoteltest.com",
        "password": "manager123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=manager_login)
    if response.status_code != 200:
        print(f"❌ Manager login failed: {response.status_code} - {response.text}")
        return False
    
    manager_auth = response.json()
    manager_token = manager_auth["token"]
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    print(f"✅ Manager logged in: {manager_auth['user']['first_name']} {manager_auth['user']['last_name']}")
    print(f"   Manager Property ID: {manager_auth['user'].get('property_id', 'None')}")
    
    # Step 5: Test manager QR code access
    print("\n5️⃣  TEST MANAGER QR CODE ACCESS")
    
    # Try to generate QR code as manager
    response = requests.post(f"{BACKEND_URL}/hr/properties/{property_id}/qr-code", 
                           headers=manager_headers)
    
    print(f"   QR Code Request: POST /hr/properties/{property_id}/qr-code")
    print(f"   Response Status: {response.status_code}")
    
    if response.status_code == 200:
        qr_data = response.json()
        print("✅ Manager can access QR code functionality!")
        print(f"   Application URL: {qr_data['application_url']}")
        print(f"   QR Code Generated: {'Yes' if qr_data.get('qr_code_url') else 'No'}")
        return True
    elif response.status_code == 403:
        error_detail = response.json().get("detail", "")
        print(f"❌ Manager access denied: {error_detail}")
        
        # Check if it's the specific manager assignment issue
        if "assigned properties" in error_detail.lower():
            print("🔍 DEBUGGING: Manager assignment issue")
            
            # Check property details
            response = requests.get(f"{BACKEND_URL}/hr/properties/{property_id}", headers=hr_headers)
            if response.status_code == 200:
                prop_details = response.json()
                print(f"   Property Manager IDs: {prop_details.get('manager_ids', [])}")
                print(f"   Manager User ID: {manager_id}")
                
                if manager_id not in prop_details.get('manager_ids', []):
                    print("❌ Manager is not properly assigned to property")
                else:
                    print("✅ Manager is assigned to property")
            
        return False
    else:
        print(f"❌ Unexpected error: {response.status_code} - {response.text}")
        return False

def fix_manager_qr_access():
    """Fix manager QR code access by ensuring proper property assignment"""
    
    print("\n🔧 FIXING MANAGER QR ACCESS")
    print("=" * 50)
    
    # Login as HR
    hr_login = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=hr_login)
    if response.status_code != 200:
        print("❌ HR login failed")
        return False
    
    hr_auth = response.json()
    hr_token = hr_auth["token"]
    hr_headers = {"Authorization": f"Bearer {hr_token}"}
    
    # Get manager
    response = requests.get(f"{BACKEND_URL}/hr/managers", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get managers")
        return False
    
    managers = response.json()
    if not managers:
        print("❌ No managers found")
        return False
    
    manager_id = managers[0]["id"]
    
    # Get properties
    response = requests.get(f"{BACKEND_URL}/hr/properties", headers=hr_headers)
    if response.status_code != 200:
        print("❌ Could not get properties")
        return False
    
    properties = response.json()
    if not properties:
        print("❌ No properties found")
        return False
    
    property_id = properties[0]["id"]
    
    # Force assign manager to property
    print(f"🔧 Assigning manager {manager_id} to property {property_id}")
    
    assign_data = {"manager_id": manager_id}
    response = requests.post(f"{BACKEND_URL}/hr/properties/{property_id}/managers", 
                           json=assign_data, headers=hr_headers)
    
    if response.status_code == 200:
        print("✅ Manager assignment successful")
        
        # Verify assignment
        response = requests.get(f"{BACKEND_URL}/hr/properties/{property_id}", headers=hr_headers)
        if response.status_code == 200:
            prop_details = response.json()
            if manager_id in prop_details.get('manager_ids', []):
                print("✅ Manager assignment verified")
                return True
            else:
                print("❌ Manager assignment not reflected in property")
        
    else:
        print(f"❌ Manager assignment failed: {response.status_code} - {response.text}")
    
    return False

if __name__ == "__main__":
    print("🚀 Starting Manager QR Code Access Test...")
    
    try:
        # First test current state
        success = test_manager_qr_access()
        
        if not success:
            print("\n🔧 Attempting to fix manager access...")
            fix_success = fix_manager_qr_access()
            
            if fix_success:
                print("\n🔄 Retesting after fix...")
                success = test_manager_qr_access()
        
        if success:
            print("\n🎉 Manager QR code access is working!")
        else:
            print("\n💥 Manager QR code access is still failing.")
            print("\n🔍 POSSIBLE SOLUTIONS:")
            print("   1. Check manager assignment to property")
            print("   2. Verify manager property_id in user record")
            print("   3. Check QR code endpoint permissions")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)