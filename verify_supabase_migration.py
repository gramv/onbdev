#!/usr/bin/env python3

"""
Verify that ALL database operations are using Supabase, not in-memory
"""

import re

def check_for_inmemory_references():
    """Check for any remaining in-memory database references"""
    
    filepath = "hotel-onboarding-backend/app/main_enhanced.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    print("🔍 Checking for in-memory database references...")
    
    # Search for database dictionary references
    inmemory_patterns = [
        r'database\["',
        r'database\[\'',
        r'database\.get\(',
        r'database\[.*?\]',
        r'in database\[',
        r'database\[.*?\] =',
        r'del database\['
    ]
    
    found_issues = []
    
    for i, line in enumerate(content.split('\n'), 1):
        for pattern in inmemory_patterns:
            if re.search(pattern, line):
                found_issues.append(f"Line {i}: {line.strip()}")
    
    if found_issues:
        print("❌ Found in-memory database references:")
        for issue in found_issues[:10]:  # Show first 10
            print(f"   {issue}")
        if len(found_issues) > 10:
            print(f"   ... and {len(found_issues) - 10} more")
        return False
    else:
        print("✅ No in-memory database references found")
        return True

def check_specific_application_issue():
    """Check the specific application ID that's failing"""
    
    failing_app_id = "5de48b19-1a42-4bc9-8069-48ae94d59953"
    
    print(f"\n🔍 Checking specific failing application: {failing_app_id}")
    
    import requests
    
    # Login as manager
    login_response = requests.post("http://127.0.0.1:8000/auth/login", json={
        "email": "manager@hoteltest.com",
        "password": "manager123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    manager_token = login_response.json()["token"]
    
    # Get applications
    apps_response = requests.get("http://127.0.0.1:8000/manager/applications", 
                                headers={"Authorization": f"Bearer {manager_token}"})
    
    if apps_response.status_code != 200:
        print(f"❌ Failed to get applications: {apps_response.status_code}")
        return False
    
    applications = apps_response.json()
    
    print(f"Found {len(applications)} applications:")
    
    found_failing_app = False
    for app in applications:
        app_id = app.get('id')
        name = f"{app.get('applicant_data', {}).get('first_name', 'Unknown')} {app.get('applicant_data', {}).get('last_name', 'Unknown')}"
        status = app.get('status')
        
        print(f"   - {app_id}: {name} ({status})")
        
        if app_id == failing_app_id:
            found_failing_app = True
            print(f"   ⚠️  FOUND THE FAILING APPLICATION!")
            print(f"       Status: {status}")
            print(f"       Department: {app.get('department')}")
            print(f"       Position: {app.get('position')}")
    
    if not found_failing_app:
        print(f"❌ The failing application {failing_app_id} was NOT found in the current applications")
        print("   This confirms the issue - frontend has stale data!")
        return False
    
    return True

def check_approval_endpoint_implementation():
    """Check if the approval endpoint is properly implemented"""
    
    filepath = "hotel-onboarding-backend/app/main_enhanced.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    print("\n🔍 Checking approval endpoint implementation...")
    
    # Look for the approval endpoint
    approval_pattern = r'@app\.post\("/applications/\{application_id\}/approve"\)'
    
    if re.search(approval_pattern, content):
        print("✅ Approval endpoint found")
        
        # Check if it uses Supabase
        endpoint_start = content.find('@app.post("/applications/{application_id}/approve")')
        if endpoint_start != -1:
            # Get the next 50 lines after the endpoint
            lines = content[endpoint_start:].split('\n')[:50]
            endpoint_content = '\n'.join(lines)
            
            if 'supabase_service' in endpoint_content:
                print("✅ Approval endpoint uses Supabase")
            else:
                print("❌ Approval endpoint does NOT use Supabase")
                print("First few lines of endpoint:")
                for i, line in enumerate(lines[:10]):
                    print(f"   {i+1}: {line}")
                return False
    else:
        print("❌ Approval endpoint not found")
        return False
    
    return True

def main():
    """Main verification function"""
    
    print("🔍 Verifying Complete Supabase Migration")
    print("=" * 50)
    
    # Check 1: In-memory references
    check1 = check_for_inmemory_references()
    
    # Check 2: Specific failing application
    check2 = check_specific_application_issue()
    
    # Check 3: Approval endpoint implementation
    check3 = check_approval_endpoint_implementation()
    
    print(f"\n📊 Verification Results:")
    print(f"   In-memory references: {'✅ CLEAN' if check1 else '❌ FOUND'}")
    print(f"   Failing application: {'✅ EXISTS' if check2 else '❌ MISSING'}")
    print(f"   Approval endpoint: {'✅ SUPABASE' if check3 else '❌ ISSUES'}")
    
    if not check1:
        print(f"\n🔧 Action Required:")
        print(f"   1. Remove all in-memory database references")
        print(f"   2. Replace with Supabase service calls")
        print(f"   3. Test all endpoints thoroughly")
    
    if not check2:
        print(f"\n🔧 Frontend Issue:")
        print(f"   1. Frontend has stale data")
        print(f"   2. Application {failing_app_id} doesn't exist")
        print(f"   3. Frontend needs to refresh data")
    
    if not check3:
        print(f"\n🔧 Backend Issue:")
        print(f"   1. Approval endpoint not properly migrated")
        print(f"   2. Still using in-memory database")
        print(f"   3. Need to complete Supabase migration")
    
    return check1 and check2 and check3

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Migration verification passed!")
    else:
        print("\n💥 Migration verification failed - issues found!")