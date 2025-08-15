#!/usr/bin/env python3
"""
Fix test users with proper passwords
"""

import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

async def fix_test_users():
    """Fix test users with proper passwords"""
    print(f"{BLUE}{BOLD}Fixing Test Users{RESET}")
    
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Test users to fix
    test_users = [
        {
            "email": "freshhr@test.com",
            "password": "test123",
            "role": "hr"
        },
        {
            "email": "testuser@example.com",
            "password": "pass123",
            "role": "manager"
        }
    ]
    
    for user_data in test_users:
        try:
            # Hash password
            hashed_password = pwd_context.hash(user_data["password"])
            
            # Update user with password hash and correct role
            update_data = {
                "password_hash": hashed_password,
                "role": user_data["role"]
            }
            
            result = supabase.table("users").update(update_data).eq("email", user_data["email"]).execute()
            
            if result.data:
                print(f"{GREEN}✅ Updated user: {user_data['email']} (role: {user_data['role']}){RESET}")
                print(f"   Password: {user_data['password']}")
            else:
                print(f"{RED}❌ Failed to update user: {user_data['email']}{RESET}")
                
        except Exception as e:
            print(f"{RED}❌ Error updating {user_data['email']}: {str(e)}{RESET}")
    
    # Verify the updates
    print(f"\n{BOLD}Verifying updates...{RESET}")
    for user_data in test_users:
        result = supabase.table("users").select("email, role, password_hash").eq("email", user_data["email"]).execute()
        if result.data and result.data[0]["password_hash"]:
            print(f"{GREEN}✅ {user_data['email']}: Password set, Role: {result.data[0]['role']}{RESET}")
        else:
            print(f"{RED}❌ {user_data['email']}: Password NOT set{RESET}")
    
    print(f"\n{GREEN}{BOLD}Test users fixed!{RESET}")
    print(f"HR User: freshhr@test.com / test123")
    print(f"Manager: testuser@example.com / pass123")

if __name__ == "__main__":
    asyncio.run(fix_test_users())