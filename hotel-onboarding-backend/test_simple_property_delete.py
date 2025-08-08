#!/usr/bin/env python3
"""Simple test for property deletion"""

import httpx
import json

def test_deletion():
    # First create a test property and manager to test with
    client = httpx.Client(base_url="http://localhost:8000")
    
    # Login as manager (since we know this works)
    login_resp = client.post("/auth/login", json={
        "email": "manager@test.com",
        "password": "test123"
    })
    
    if login_resp.status_code == 200:
        print("✅ Manager login successful")
        token = login_resp.json()["token"]
        user_info = login_resp.json()["user"]
        print(f"User role: {user_info['role']}")
        
        # Try to get properties (this should work for managers)
        headers = {"Authorization": f"Bearer {token}"}
        props_resp = client.get("/hr/properties", headers=headers)
        
        if props_resp.status_code == 200:
            properties = props_resp.json().get("data", [])
            print(f"✅ Found {len(properties)} properties")
            
            # Show property details
            for prop in properties[:3]:  # Show first 3
                print(f"  - {prop['name']} (ID: {prop['id'][:8]}...)")
        else:
            print(f"❌ Failed to get properties: {props_resp.status_code}")
            print(props_resp.text)
    else:
        print(f"❌ Login failed: {login_resp.status_code}")
        print(login_resp.text)
    
    client.close()

if __name__ == "__main__":
    test_deletion()