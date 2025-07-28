#!/usr/bin/env python3
"""
Test manager filtering in HR applications endpoint
"""

import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.pRKnUaBYip5SbScXMQZs3apq8c4YtZc2_-j4NrWDEdQ"
MANAGER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtYW5hZ2VyX2lkIjoibWdyX3Rlc3RfMDAxIiwicHJvcGVydHlfaWQiOiJwcm9wX3Rlc3RfMDAxIiwidG9rZW5fdHlwZSI6Im1hbmFnZXJfYXV0aCIsImlhdCI6MTc1MzY3MzkzMywiZXhwIjoxNzUzNzYwMzMzfQ.SDXhU8b772aePvqZuYaFAs84U6-oQDdcVYAnkZJ3h4A"

def test_application_filtering():
    print("🔍 Testing application filtering...")
    
    # Test 1: HR access to applications
    print("\n1. HR accessing applications")
    try:
        hr_headers = {"Authorization": f"Bearer {HR_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=hr_headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            hr_apps = response.json()
            print(f"   HR sees {len(hr_apps)} applications")
            for app in hr_apps:
                print(f"     - {app.get('applicant_name')} at {app.get('property_name')} ({app.get('property_id')})")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 2: Manager access to applications
    print("\n2. Manager accessing applications")
    try:
        manager_headers = {"Authorization": f"Bearer {MANAGER_TOKEN}"}
        response = requests.get(f"{BACKEND_URL}/hr/applications", headers=manager_headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            manager_apps = response.json()
            print(f"   Manager sees {len(manager_apps)} applications")
            for app in manager_apps:
                print(f"     - {app.get('applicant_name')} at {app.get('property_name')} ({app.get('property_id')})")
            
            # Check if manager only sees their property
            manager_property_ids = set(app.get('property_id') for app in manager_apps)
            print(f"   Manager sees properties: {manager_property_ids}")
            if manager_property_ids == {'prop_test_001'}:
                print("   ✅ Manager correctly filtered to their property")
            else:
                print("   ❌ Manager sees applications from other properties")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_application_filtering()