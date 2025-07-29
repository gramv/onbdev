#!/usr/bin/env python3
"""
Create Working Test Accounts
Bypass Supabase service issues and create accounts directly
"""
import sys
import os
import requests
import json

# Add backend to path
sys.path.insert(0, 'hotel-onboarding-backend')

def create_accounts_directly():
    """Create accounts directly in the backend"""
    print("🔧 Creating test accounts directly...")
    
    try:
        from app.auth import PasswordManager
        
        # Initialize password manager
        password_manager = PasswordManager()
        
        # Create test accounts with passwords
        accounts = [
            {"email": "hr@rcihotel.com", "password": "hr123", "role": "hr"},
            {"email": "vgoutamram@gmail.com", "password": "Gouthi321@", "role": "manager"},
            {"email": "manager@hoteltest.com", "password": "manager123", "role": "manager"}
        ]
        
        for account in accounts:
            password_manager.store_password(account["email"], account["password"])
            print(f"✅ Created {account['role']} account: {account['email']}")
        
        print("\n🎉 Test accounts created successfully!")
        print("=" * 50)
        print("Available accounts:")
        for account in accounts:
            print(f"  {account['role'].upper()}: {account['email']} / {account['password']}")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create accounts: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login(email, password):
    """Test login with created account"""
    print(f"\n🔐 Testing login: {email}")
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful!")
            print(f"   User: {result.get('user', {}).get('first_name', 'Unknown')} {result.get('user', {}).get('last_name', '')}")
            print(f"   Role: {result.get('user', {}).get('role', 'Unknown')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def create_test_application():
    """Create a test application for approval testing"""
    print(f"\n📝 Creating test application...")
    
    try:
        app_data = {
            "first_name": "Goutam",
            "last_name": "Vemula",
            "email": "goutamramv@gmail.com",
            "phone": "(555) 123-4567",
            "address": "123 Tech Street",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94105",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-02-15",  # Future date
            "shift_preference": "day",
            "employment_type": "full_time",
            "experience_years": "3",
            "hotel_experience": "yes",
            "previous_employer": "Tech Hotel Group",
            "reason_for_leaving": "Career advancement",
            "additional_comments": "Email integration test application"
        }
        
        # Try different property IDs
        property_ids = ["rci", "prop_test_001", "test_property"]
        
        for prop_id in property_ids:
            response = requests.post(
                f"http://localhost:8000/apply/{prop_id}",
                json=app_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Application created successfully!")
                print(f"   Property: {prop_id}")
                print(f"   Application ID: {result.get('application_id')}")
                return result.get('application_id')
            else:
                print(f"⚠️  Property {prop_id} failed: {response.status_code}")
        
        print("❌ Failed to create application with any property")
        return None
        
    except Exception as e:
        print(f"❌ Application creation failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 CREATING WORKING TEST ENVIRONMENT")
    print("=" * 60)
    
    # Step 1: Create accounts
    if not create_accounts_directly():
        print("❌ Account creation failed")
        return False
    
    # Step 2: Test logins
    test_accounts = [
        ("hr@rcihotel.com", "hr123"),
        ("vgoutamram@gmail.com", "Gouthi321@"),
        ("manager@hoteltest.com", "manager123")
    ]
    
    login_results = []
    for email, password in test_accounts:
        result = test_login(email, password)
        login_results.append(result)
    
    # Step 3: Create test application
    app_id = create_test_application()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 TEST ENVIRONMENT SUMMARY")
    print("=" * 60)
    
    print(f"Account Creation: ✅")
    print(f"Login Tests: {sum(login_results)}/{len(login_results)} successful")
    print(f"Test Application: {'✅' if app_id else '❌'}")
    
    if any(login_results):
        print("\n🎉 SUCCESS: You can now login with these accounts:")
        for i, (email, password) in enumerate(test_accounts):
            if login_results[i]:
                print(f"  ✅ {email} / {password}")
            else:
                print(f"  ❌ {email} / {password}")
    else:
        print("\n❌ LOGIN ISSUES: None of the accounts work")
        print("🔧 Check backend authentication system")
    
    if app_id:
        print(f"\n📝 Test application ready for approval: {app_id}")
        print("🔗 Use manager account to approve and test email integration")
    
    return any(login_results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)