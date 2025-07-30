#!/usr/bin/env python3
"""Test property creation endpoint"""
import requests
import json

# Test property creation directly
def test_property_creation():
    # Mock HR token (you'll need to replace with actual token)
    # For testing, we can create a simple test
    
    # First, let's test the health endpoint
    try:
        health_response = requests.get("http://localhost:8000/healthz")
        print(f"Health check: {health_response.status_code}")
        print(f"Response: {health_response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test the /hr/users endpoint (which should now exist)
    try:
        # This will fail without proper auth, but we can see if endpoint exists
        users_response = requests.get("http://localhost:8000/hr/users")
        print(f"Users endpoint status: {users_response.status_code}")
        if users_response.status_code == 401:
            print("✅ Users endpoint exists (authentication required)")
        elif users_response.status_code == 404:
            print("❌ Users endpoint not found")
        else:
            print(f"Users endpoint response: {users_response.json()}")
    except Exception as e:
        print(f"Users endpoint test failed: {e}")
    
    # Test property creation endpoint (will fail without auth, but we can see endpoint structure)
    try:
        property_data = {
            'name': 'Test Hotel',
            'address': '123 Test St',
            'city': 'Test City', 
            'state': 'CA',
            'zip_code': '90210',
            'phone': '555-123-4567'
        }
        
        create_response = requests.post("http://localhost:8000/hr/properties", data=property_data)
        print(f"Property creation status: {create_response.status_code}")
        if create_response.status_code == 401:
            print("✅ Property creation endpoint exists (authentication required)")
        elif create_response.status_code == 404:
            print("❌ Property creation endpoint not found")
        else:
            print(f"Property creation response: {create_response.json()}")
    except Exception as e:
        print(f"Property creation test failed: {e}")

if __name__ == "__main__":
    test_property_creation()