#!/usr/bin/env python3
"""
Set password for manager@demo.com in test database
Uses bcrypt hashing to match backend expectations
"""
import os
import sys
import bcrypt
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

# Verify we're on test database
if 'kzommszdhapvqpekpvnt' not in url:
    print("ERROR: This script is for TEST database only!")
    print(f"Current URL: {url}")
    sys.exit(1)

print(f"Setting password for manager in TEST database")
print("=" * 60)

# Create Supabase client
client = create_client(url, key)

def hash_password(password: str) -> str:
    """Hash password using bcrypt (matching backend)"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def main():
    """Set password for manager@demo.com"""
    
    # Password to set
    password = "demo123"
    password_hash = hash_password(password)
    
    print(f"\n1. Generating bcrypt hash for password...")
    print(f"   Password: {password}")
    print(f"   Hash: {password_hash[:20]}...")
    
    # Update manager's password
    print(f"\n2. Updating manager@demo.com password...")
    try:
        result = client.table('users').update({
            'password_hash': password_hash,
            'updated_at': datetime.now().isoformat()
        }).eq('email', 'manager@demo.com').execute()
        
        if result.data:
            print(f"   ✅ Password updated successfully")
            user = result.data[0]
            print(f"   Manager ID: {user['id']}")
            print(f"   Property ID: {user.get('property_id', 'Not set')}")
        else:
            print(f"   ❌ No user found with email manager@demo.com")
            return False
            
    except Exception as e:
        print(f"   ❌ Error updating password: {e}")
        return False
    
    # Verify the user setup
    print(f"\n3. Verifying manager setup...")
    try:
        # Get user details
        user_result = client.table('users').select('*').eq('email', 'manager@demo.com').execute()
        if user_result.data:
            user = user_result.data[0]
            print(f"   Email: {user['email']}")
            print(f"   Role: {user['role']}")
            print(f"   Property ID: {user.get('property_id', 'Not set')}")
            print(f"   Has Password: {'Yes' if user.get('password_hash') else 'No'}")
            
            # Check property_managers link
            if user.get('property_id'):
                pm_result = client.table('property_managers').select('*').eq('manager_id', user['id']).execute()
                if pm_result.data:
                    print(f"   Property Link: ✅ Found in property_managers table")
                else:
                    print(f"   Property Link: ⚠️  Not found in property_managers table")
                    
    except Exception as e:
        print(f"   ⚠️  Error verifying: {e}")
    
    # Test authentication
    print(f"\n4. Testing authentication...")
    print(f"   To test login, run:")
    print(f'   curl -X POST http://localhost:8000/auth/login \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"email": "manager@demo.com", "password": "demo123"}}\'')
    
    print("\n" + "=" * 60)
    print("✅ PASSWORD SETUP COMPLETE!")
    print("=" * 60)
    print(f"\nManager Login Credentials:")
    print(f"  Email: manager@demo.com")
    print(f"  Password: demo123")
    print(f"\nLogin URL: http://localhost:3000/manager")
    
    return True

if __name__ == "__main__":
    # Install bcrypt if needed
    try:
        import bcrypt
    except ImportError:
        print("Installing bcrypt...")
        os.system("python3 -m pip install bcrypt --break-system-packages")
        import bcrypt
    
    success = main()
    sys.exit(0 if success else 1)