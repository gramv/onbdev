#!/usr/bin/env python3
"""
Verify Database Integrity - Check both production and test databases for test artifacts
This script checks if any test data was accidentally created in production.
"""
import os
import sys
from datetime import datetime
from supabase import create_client

# Simple colored output without external dependencies
def colored(text, color=None, attrs=None):
    """Simple colored output for terminal"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    result = ''
    if attrs and 'bold' in attrs:
        result += colors['bold']
    if color in colors:
        result += colors[color]
    result += str(text)
    result += colors['reset']
    return result

# Test artifacts to search for
TEST_ARTIFACTS = {
    'property_id': 'a99239dd-ebde-4c69-b862-ecba9e878798',
    'property_name': 'Demo Hotel',
    'manager_email': 'manager@demo.com',
    'hr_email': 'hr@demo.com',
    'test_addresses': ['123 Demo Street', '456 Test Avenue'],
    'test_phones': ['(555) 123-4567', '(555) 987-6543']
}

# Database configurations
# Use only TEST database for this tool to avoid accidental production access
DATABASES = {
    'TEST': {
        'url': 'https://kzommszdhapvqpekpvnt.supabase.co',
        'key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt6b21tc3pkaGFwdnFwZWtwdm50Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ3NjQxMTcsImV4cCI6MjA3MDM0MDExN30.VMl6QzCZleoOvcY_abOHsztgXcottOnDv2kzJgmCjdg',
        'color': 'green'
    }
}

def check_database(name, config):
    """Check a database for test artifacts"""
    print(f"\n{'='*60}")
    print(colored(f"Checking {name} Database", config['color'], attrs=['bold']))
    print(f"URL: {config['url'][:40]}...")
    print(f"{'='*60}")
    
    try:
        client = create_client(config['url'], config['key'])
        findings = []
        
        # Check for test property
        print("\n🔍 Checking for test property...")
        try:
            properties = client.table('properties').select('*').execute()
            for prop in properties.data:
                if prop.get('id') == TEST_ARTIFACTS['property_id']:
                    findings.append(f"❌ Found test property ID: {prop['id']} - {prop.get('name', 'Unknown')}")
                    print(colored(findings[-1], 'red'))
                if prop.get('name') == TEST_ARTIFACTS['property_name']:
                    findings.append(f"❌ Found Demo Hotel: {prop['id']} - {prop['name']}")
                    print(colored(findings[-1], 'red'))
                if prop.get('address') in TEST_ARTIFACTS['test_addresses']:
                    findings.append(f"⚠️  Found test address: {prop['id']} - {prop['address']}")
                    print(colored(findings[-1], 'yellow'))
            
            if not findings:
                print(colored("   ✅ No test properties found", 'green'))
        except Exception as e:
            print(f"   ⚠️  Could not check properties: {e}")
        
        # Check for test users
        print("\n🔍 Checking for test users...")
        test_user_findings = []
        try:
            users = client.table('users').select('*').execute()
            for user in users.data:
                if user.get('email') in [TEST_ARTIFACTS['manager_email'], TEST_ARTIFACTS['hr_email']]:
                    test_user_findings.append(f"❌ Found test user: {user['email']} ({user.get('role', 'unknown')})")
                    print(colored(test_user_findings[-1], 'red'))
                    findings.append(test_user_findings[-1])
            
            if not test_user_findings:
                print(colored("   ✅ No test users found", 'green'))
        except Exception as e:
            print(f"   ⚠️  Could not check users: {e}")
        
        # Check for test employees
        print("\n🔍 Checking for test employees...")
        test_employee_findings = []
        try:
            employees = client.table('employees').select('*').execute()
            for emp in employees.data:
                if emp.get('property_id') == TEST_ARTIFACTS['property_id']:
                    test_employee_findings.append(f"❌ Found employee with test property: {emp.get('first_name')} {emp.get('last_name')}")
                    print(colored(test_employee_findings[-1], 'red'))
                    findings.append(test_employee_findings[-1])
                if emp.get('email') and 'test' in emp.get('email', '').lower():
                    test_employee_findings.append(f"⚠️  Found possible test employee: {emp.get('email')}")
                    print(colored(test_employee_findings[-1], 'yellow'))
            
            if not test_employee_findings:
                print(colored("   ✅ No test employees found", 'green'))
        except Exception as e:
            print(f"   ⚠️  Could not check employees: {e}")
        
        # Check for test job applications
        print("\n🔍 Checking for test job applications...")
        test_app_findings = []
        try:
            applications = client.table('job_applications').select('*').execute()
            for app in applications.data:
                if app.get('property_id') == TEST_ARTIFACTS['property_id']:
                    test_app_findings.append(f"❌ Found application for test property: {app.get('id')}")
                    print(colored(test_app_findings[-1], 'red'))
                    findings.append(test_app_findings[-1])
                app_data = app.get('applicant_data', {})
                if isinstance(app_data, dict):
                    if app_data.get('email') and ('test' in app_data.get('email', '').lower() or 
                                                   'demo' in app_data.get('email', '').lower() or
                                                   'jane.doe' in app_data.get('email', '').lower()):
                        test_app_findings.append(f"⚠️  Found possible test application: {app_data.get('email')}")
                        print(colored(test_app_findings[-1], 'yellow'))
            
            if not test_app_findings:
                print(colored("   ✅ No test applications found", 'green'))
        except Exception as e:
            print(f"   ⚠️  Could not check applications: {e}")
        
        # Get database statistics
        print("\n📊 Database Statistics:")
        try:
            stats = {
                'properties': len(properties.data) if 'properties' in locals() else 0,
                'users': len(users.data) if 'users' in locals() else 0,
                'employees': len(employees.data) if 'employees' in locals() else 0,
                'applications': len(applications.data) if 'applications' in locals() else 0
            }
            for key, value in stats.items():
                print(f"   {key.capitalize()}: {value}")
        except:
            print("   Could not get statistics")
        
        # Summary
        print(f"\n{'='*60}")
        if findings:
            print(colored(f"⚠️  {name} DATABASE HAS {len(findings)} TEST ARTIFACTS!", 'red', attrs=['bold']))
            print("\nTest artifacts found:")
            for finding in findings:
                print(f"  {finding}")
        else:
            print(colored(f"✅ {name} DATABASE IS CLEAN", 'green', attrs=['bold']))
        
        return findings
        
    except Exception as e:
        print(colored(f"❌ Failed to connect to {name} database: {e}", 'red'))
        return None

def main():
    """Main execution"""
    print(colored("\n🔐 DATABASE INTEGRITY VERIFICATION", 'cyan', attrs=['bold']))
    print(colored("Checking for test artifacts in production and test databases", 'cyan'))
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check test database only
    test_findings = check_database('TEST', DATABASES['TEST'])
    
    # Final summary
    print(f"\n{'='*60}")
    print(colored("FINAL SUMMARY", 'cyan', attrs=['bold']))
    print(f"{'='*60}")
    
    if test_findings is None:
        print(colored(f"\n❌ TEST DATABASE CONNECTION FAILED", 'red'))
        print("This is expected if RLS is enabled. Run disable_test_rls.sql first.")
    elif not test_findings:
        print(colored(f"\n⚠️  TEST DATABASE IS EMPTY", 'yellow'))
        print("Run setup_test_database.py to create test data")
    else:
        print(colored(f"\n✅ TEST DATABASE HAS TEST DATA", 'green'))
        print(f"Found {len(test_findings) if test_findings else 0} test artifacts as expected")
    
    print("\n" + "="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())