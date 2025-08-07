#!/usr/bin/env python3
"""
Debug Applications Response
Check what the applications endpoint returns
"""
import requests
import json

def debug_applications():
    """Debug the applications endpoint response"""
    print("🔍 Debugging Applications Response")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    hr_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJyb2xlIjoiaHIiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzcyODAwMSwiZXhwIjoxNzUzODE0NDAxLCJqdGkiOiI3YjIxYmJiNy0zNDBiLTQ2ODQtOGNlZC03Y2IxNzMwYThhODcifQ.WODYfBAFgdoHZ6BVESzTQu2AGDUcFtwtpLbbryh1dKM"
    
    hr_headers = {"Authorization": f"Bearer {hr_token}"}
    
    try:
        print("1. 🔍 Testing applications endpoint...")
        response = requests.get(f"{base_url}/hr/applications", headers=hr_headers)
        
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            applications = response.json()
            print(f"   📝 Found {len(applications)} applications")
            
            if applications:
                print("\n2. 📋 First application structure:")
                first_app = applications[0]
                print(json.dumps(first_app, indent=2))
                
                print("\n3. 🔍 Looking for approved applications...")
                approved_apps = [app for app in applications if app.get("status") == "approved"]
                print(f"   ✅ Found {len(approved_apps)} approved applications")
                
                if approved_apps:
                    print("\n4. 📋 First approved application:")
                    print(json.dumps(approved_apps[0], indent=2))
                else:
                    print("\n4. ⚠️  No approved applications found")
                    print("   Available statuses:")
                    statuses = set(app.get("status", "unknown") for app in applications)
                    for status in statuses:
                        count = len([app for app in applications if app.get("status") == status])
                        print(f"     • {status}: {count} applications")
            else:
                print("   ⚠️  No applications found")
        else:
            print(f"   ❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")

if __name__ == "__main__":
    debug_applications()