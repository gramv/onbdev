#!/usr/bin/env python3
"""
Create test users for Task 2 testing
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

async def create_test_users():
    """Create test users for testing"""
    print(f"{BLUE}{BOLD}Creating Test Users{RESET}")
    
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Test users
    test_users = [
        {
            "email": "freshhr@test.com",
            "password": "test123",
            "name": "Fresh HR User",
            "role": "hr",
            "property_id": None
        },
        {
            "email": "testuser@example.com",
            "password": "pass123",
            "name": "Test Manager",
            "role": "manager",
            "property_id": None
        }
    ]
    
    for user_data in test_users:
        try:
            # Check if user exists
            result = supabase.table("users").select("*").eq("email", user_data["email"]).execute()
            
            if result.data:
                print(f"{YELLOW}User already exists: {user_data['email']}{RESET}")
                continue
            
            # Hash password
            hashed_password = pwd_context.hash(user_data["password"])
            
            # Create user
            user = {
                "email": user_data["email"],
                "password_hash": hashed_password,
                "name": user_data["name"],
                "role": user_data["role"],
                "is_active": True
            }
            
            if user_data["property_id"]:
                user["property_id"] = user_data["property_id"]
            
            result = supabase.table("users").insert(user).execute()
            
            if result.data:
                print(f"{GREEN}✅ Created user: {user_data['email']} (role: {user_data['role']}){RESET}")
            else:
                print(f"{RED}❌ Failed to create user: {user_data['email']}{RESET}")
                
        except Exception as e:
            print(f"{RED}❌ Error creating {user_data['email']}: {str(e)}{RESET}")
    
    print(f"\n{GREEN}{BOLD}Test users ready!{RESET}")
    print(f"HR User: freshhr@test.com / test123")
    print(f"Manager: testuser@example.com / pass123")

if __name__ == "__main__":
    asyncio.run(create_test_users())