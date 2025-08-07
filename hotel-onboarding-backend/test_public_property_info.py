#!/usr/bin/env python3
"""
Test script for the public property info endpoint
Tests all requirements for task 2: Public Property Info Endpoint
"""

import requests
import json

def test_public_property_info_endpoint():
    """Test the /properties/{property_id}/info endpoint"""
    
    base_url = "http://localhost:8000"
    test_property_id = "prop_test_001"
    
    print("🧪 Testing Public Property Info Endpoint")
    print("=" * 50)
    
    # Test 1: Valid property returns correct data
    print("\n✅ Test 1: Valid property returns correct information")
    try:
        response = requests.get(f"{base_url}/properties/{test_property_id}/info")
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify required fields are present
            assert "property" in data, "Property information missing"
            assert "departments_and_positions" in data, "Departments and positions missing"
            assert "application_url" in data, "Application URL missing"
            assert "is_accepting_applications" in data, "Application status missing"
            
            # Verify property details
            property_info = data["property"]
            required_property_fields = ["id", "name", "address", "city", "state", "zip_code"]
            for field in required_property_fields:
                assert field in property_info, f"Property field '{field}' missing"
            
            # Verify departments and positions structure
            departments = data["departments_and_positions"]
            expected_departments = ["Front Desk", "Housekeeping", "Food & Beverage", "Maintenance"]
            
            for dept in expected_departments:
                assert dept in departments, f"Department '{dept}' missing"
                assert isinstance(departments[dept], list), f"Positions for '{dept}' should be a list"
                assert len(departments[dept]) > 0, f"No positions available for '{dept}'"
            
            print(f"   ✓ Property: {property_info['name']}")
            print(f"   ✓ Departments: {len(departments)} departments available")
            print(f"   ✓ Application URL: {data['application_url']}")
            print(f"   ✓ Accepting applications: {data['is_accepting_applications']}")
            
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Non-existent property returns 404
    print("\n✅ Test 2: Non-existent property returns 404")
    try:
        response = requests.get(f"{base_url}/properties/nonexistent/info")
        
        if response.status_code == 404:
            print("   ✓ Correctly returns 404 for non-existent property")
        else:
            print(f"   ❌ Expected 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: No authentication required (public access)
    print("\n✅ Test 3: Public access (no authentication required)")
    try:
        # Make request without any authorization headers
        response = requests.get(
            f"{base_url}/properties/{test_property_id}/info",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("   ✓ Endpoint accessible without authentication")
        else:
            print(f"   ❌ Failed without auth: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Verify specific departments and positions match hotel operations
    print("\n✅ Test 4: Verify departments and positions are appropriate for hotel")
    try:
        response = requests.get(f"{base_url}/properties/{test_property_id}/info")
        data = response.json()
        departments = data["departments_and_positions"]
        
        # Check Front Desk positions
        front_desk_positions = departments["Front Desk"]
        expected_front_desk = ["Front Desk Agent", "Night Auditor"]
        for pos in expected_front_desk:
            assert pos in front_desk_positions, f"Missing Front Desk position: {pos}"
        
        # Check Housekeeping positions
        housekeeping_positions = departments["Housekeeping"]
        assert "Housekeeper" in housekeeping_positions, "Missing Housekeeper position"
        
        # Check Food & Beverage positions
        fb_positions = departments["Food & Beverage"]
        assert "Server" in fb_positions, "Missing Server position"
        
        # Check Maintenance positions
        maintenance_positions = departments["Maintenance"]
        assert "Maintenance Technician" in maintenance_positions, "Missing Maintenance Technician position"
        
        print("   ✓ All expected hotel positions are available")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n🎉 All tests passed! Public Property Info Endpoint is working correctly.")
    print("\n📋 Requirements Verification:")
    print("   ✓ Implements /properties/{property_id}/info GET endpoint")
    print("   ✓ Returns basic property information for application form")
    print("   ✓ Includes available departments and positions")
    print("   ✓ No authentication required (public access)")
    print("   ✓ Proper error handling for non-existent properties")
    
    return True

if __name__ == "__main__":
    success = test_public_property_info_endpoint()
    exit(0 if success else 1)