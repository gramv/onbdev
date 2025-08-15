#!/usr/bin/env python3
"""Create a test manager account with known credentials"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from passlib.context import CryptContext
import uuid

# Load environment
load_dotenv('hotel-onboarding-backend/.env')

# Initialize Supabase
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test credentials
email = "testmanager@demo.com"
password = "password123"
hashed_password = pwd_context.hash(password)

# Check if user exists
existing = supabase.table('users').select('*').eq('email', email).execute()

if existing.data:
    # Update password
    result = supabase.table('users').update({
        'password_hash': hashed_password
    }).eq('email', email).execute()
    print(f"Updated existing user: {email}")
else:
    # Get a property ID (use first available)
    properties = supabase.table('properties').select('id').limit(1).execute()
    property_id = properties.data[0]['id'] if properties.data else str(uuid.uuid4())
    
    # Create new user
    result = supabase.table('users').insert({
        'email': email,
        'password_hash': hashed_password,
        'role': 'manager',
        'first_name': 'Test',
        'last_name': 'Manager',
        'property_id': property_id,
        'is_active': True
    }).execute()
    print(f"Created new user: {email}")

print("\n✅ Manager Login Credentials:")
print(f"Email: {email}")
print(f"Password: {password}")
print("\nYou can now login at: http://localhost:3000/manager")