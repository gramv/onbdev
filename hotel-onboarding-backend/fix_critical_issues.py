#!/usr/bin/env python3
"""
Critical Issues Fix Script
Addresses the top 3 issues identified in the comprehensive test report
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
HR_TOKEN = None

def authenticate_hr():
    """Get HR authentication token"""
    global HR_TOKEN
    try:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json={"email": "freshhr@test.com", "password": "test123"})
        if response.status_code == 200:
            HR_TOKEN = response.json()["data"]["token"]
            print("✅ HR Authentication successful")
            return True
        else:
            print(f"❌ HR Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HR Authentication error: {e}")
        return False

def test_manager_property_assignment():
    """Test if we can create a property assignment for the manager"""
    print("\n🔧 Testing Manager Property Assignment Fix...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Try to create a test property first
    try:
        property_data = {
            "name": "Test Hotel Property",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "CA",
            "zip_code": "90210"
        }
        response = requests.post(f"{BASE_URL}/api/properties", 
                               json=property_data, headers=headers)
        if response.status_code in [200, 201]:
            property_id = response.json().get("data", {}).get("id")
            print(f"✅ Test property created: {property_id}")
            
            # Now try to assign manager to property
            assignment_data = {
                "manager_id": "a120ae58-7f72-49e0-ae95-abb209df438e",
                "property_id": property_id
            }
            response = requests.post(f"{BASE_URL}/api/property-managers", 
                                   json=assignment_data, headers=headers)
            if response.status_code in [200, 201]:
                print("✅ Manager assigned to property")
                return True
            else:
                print(f"⚠️  Manager assignment endpoint: {response.status_code}")
        else:
            print(f"⚠️  Property creation endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Property assignment test failed: {e}")
    
    # If direct API doesn't work, provide manual instructions
    print("\n📝 MANUAL FIX REQUIRED:")
    print("Run this SQL in your Supabase dashboard:")
    print("""
    -- Create test property
    INSERT INTO properties (id, name, address, city, state, zip_code)
    VALUES (gen_random_uuid(), 'Test Hotel Property', '123 Test St', 'Test City', 'CA', '90210');
    
    -- Assign manager to property  
    INSERT INTO property_managers (manager_id, property_id)
    SELECT 'a120ae58-7f72-49e0-ae95-abb209df438e', id 
    FROM properties WHERE name = 'Test Hotel Property';
    """)
    
    return False

def test_manager_authentication_after_fix():
    """Test manager authentication after property assignment"""
    print("\n🧪 Testing Manager Authentication...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", 
                               json={"email": "testuser@example.com", "password": "pass123"})
        if response.status_code == 200:
            print("✅ Manager authentication now working!")
            token = response.json()["data"]["token"]
            
            # Test manager dashboard access
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/manager/dashboard", headers=headers)
            if response.status_code == 200:
                print("✅ Manager dashboard accessible")
            else:
                print(f"⚠️  Manager dashboard: {response.status_code}")
                
        elif response.status_code == 403:
            print("❌ Manager still not assigned to property")
            error_msg = response.json().get('error', 'Unknown error')
            print(f"   Error: {error_msg}")
        else:
            print(f"❌ Manager authentication failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Manager authentication test failed: {e}")

def check_compliance_engine():
    """Check if compliance engine is working"""
    print("\n🔧 Testing Compliance Engine...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/compliance/dashboard", headers=headers)
        if response.status_code == 200:
            print("✅ Compliance dashboard working")
        elif response.status_code == 500:
            print("❌ Compliance engine import error still exists")
            print("📝 FIX REQUIRED: Add import in app/main_enhanced.py:")
            print("   from app.compliance_engine import compliance_engine")
        else:
            print(f"⚠️  Compliance dashboard: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Compliance test failed: {e}")

def test_notification_sending():
    """Test notification sending functionality"""
    print("\n🔧 Testing Notification System...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    # Test GET notifications (should work)
    try:
        response = requests.get(f"{BASE_URL}/api/notifications", headers=headers)
        if response.status_code == 200:
            notifications = response.json().get("data", [])
            print(f"✅ Notification retrieval working ({len(notifications)} notifications)")
        else:
            print(f"❌ Notification retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Notification retrieval error: {e}")
    
    # Test POST notifications (likely to fail)
    try:
        notification_data = {
            "title": "Test Notification",
            "message": "Testing notification system",
            "type": "system",
            "priority": "normal"
        }
        response = requests.post(f"{BASE_URL}/api/notifications", 
                               json=notification_data, headers=headers)
        if response.status_code in [200, 201]:
            print("✅ Notification sending working")
        elif response.status_code == 405:
            print("❌ Notification sending: Method Not Allowed")
            print("📝 FIX REQUIRED: Add POST method to notification endpoint")
        else:
            print(f"⚠️  Notification sending: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Notification sending test failed: {e}")

def run_quick_validation():
    """Run quick validation of key endpoints"""
    print("\n🧪 Running Quick System Validation...")
    
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    
    endpoints_to_test = [
        ("/api/analytics/dashboard", "Analytics Dashboard"),
        ("/api/audit-logs", "Audit Logs"),
        ("/api/employees", "Employee Management"), 
        ("/api/hr/onboarding/pending", "HR Onboarding"),
        ("/healthz", "System Health")
    ]
    
    working_endpoints = 0
    total_endpoints = len(endpoints_to_test)
    
    for endpoint, name in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", 
                                  headers=headers if endpoint != "/healthz" else {})
            if response.status_code == 200:
                print(f"  ✅ {name}")
                working_endpoints += 1
            else:
                print(f"  ❌ {name}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
    
    print(f"\n📊 System Health: {working_endpoints}/{total_endpoints} endpoints working")
    if working_endpoints >= total_endpoints * 0.8:
        print("🎯 System Status: GOOD")
    elif working_endpoints >= total_endpoints * 0.6:
        print("⚠️  System Status: FAIR")
    else:
        print("❌ System Status: NEEDS ATTENTION")

def main():
    """Main execution function"""
    print("🚀 CRITICAL ISSUES FIX SCRIPT")
    print("=" * 50)
    print("Addressing top issues from comprehensive test report")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Authenticate
    if not authenticate_hr():
        print("❌ Cannot proceed without HR authentication")
        return
    
    # Step 2: Test and provide fixes for critical issues
    test_manager_property_assignment()
    check_compliance_engine()
    test_notification_sending()
    
    # Step 3: Test manager authentication after potential fixes
    test_manager_authentication_after_fix()
    
    # Step 4: Quick system validation
    run_quick_validation()
    
    print("\n" + "=" * 50)
    print("🏁 CRITICAL ISSUES ANALYSIS COMPLETE")
    print("\n💡 NEXT STEPS:")
    print("1. Apply the SQL fixes shown above in Supabase")
    print("2. Fix compliance_engine import in app/main_enhanced.py") 
    print("3. Add POST method to notification endpoint")
    print("4. Restart the server")
    print("5. Re-run comprehensive tests")
    
    print(f"\nExpected improvement: 75-85% test pass rate")

if __name__ == "__main__":
    main()