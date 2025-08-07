#!/usr/bin/env python3
"""
Generate proper JWT tokens for testing the QR job application workflow
"""

import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hotel-onboarding-super-secret-key-2025")
JWT_ALGORITHM = "HS256"

def generate_hr_token(user_id: str = "hr_test_001", expires_hours: int = 24):
    """Generate HR authentication token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    
    payload = {
        "user_id": user_id,
        "token_type": "hr_auth",
        "iat": datetime.now(timezone.utc),
        "exp": expire
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def generate_manager_token(manager_id: str = "mgr_test_001", property_id: str = "prop_test_001", expires_hours: int = 24):
    """Generate Manager authentication token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    
    payload = {
        "manager_id": manager_id,
        "property_id": property_id,
        "token_type": "manager_auth",
        "iat": datetime.now(timezone.utc),
        "exp": expire
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def main():
    """Generate and display test tokens"""
    print("🔐 Generating JWT Test Tokens")
    print("=" * 50)
    
    # Generate tokens
    hr_token = generate_hr_token()
    manager_token = generate_manager_token()
    
    print(f"\n✅ HR Token:")
    print(f"   {hr_token}")
    
    print(f"\n✅ Manager Token:")
    print(f"   {manager_token}")
    
    print(f"\n📋 Usage in tests:")
    print(f'   HR_TOKEN = "{hr_token}"')
    print(f'   MANAGER_TOKEN = "{manager_token}"')
    
    # Verify tokens work
    try:
        hr_payload = jwt.decode(hr_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        manager_payload = jwt.decode(manager_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        print(f"\n✅ Token Verification:")
        print(f"   HR Token Type: {hr_payload.get('token_type')}")
        print(f"   HR User ID: {hr_payload.get('user_id')}")
        print(f"   Manager Token Type: {manager_payload.get('token_type')}")
        print(f"   Manager ID: {manager_payload.get('manager_id')}")
        print(f"   Property ID: {manager_payload.get('property_id')}")
        
    except Exception as e:
        print(f"❌ Token verification failed: {e}")

if __name__ == "__main__":
    main()