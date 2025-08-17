#!/usr/bin/env python3
"""
Create a simple onboarding token that works with the current backend
This token will trigger the test mode in the backend
"""

import jwt
from datetime import datetime, timedelta, timezone
import secrets

# Use the exact JWT secret from .env.test
JWT_SECRET_KEY = "dev-secret"
JWT_ALGORITHM = "HS256"

def create_test_onboarding_token():
    """Create a test onboarding token that triggers test mode"""
    
    # Create a test employee ID that will trigger test mode
    employee_id = f"test-emp-{secrets.token_hex(4)}"
    
    # Token payload matching what OnboardingTokenManager expects
    payload = {
        "employee_id": employee_id,
        "application_id": None,
        "token_type": "onboarding",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "jti": secrets.token_urlsafe(16),
        # Add extra data for test mode
        "test_data": {
            "name": "Goutam Vemula",
            "email": "goutamramv@gmail.com",
            "position": "Software Engineer",
            "property": "Demo Hotel",
            "property_id": "test-prop-001"
        }
    }
    
    # Generate the token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return token, employee_id

def main():
    print("=" * 60)
    print("Creating Test Onboarding Token for Goutam Vemula")
    print("=" * 60)
    
    # Generate the token
    token, employee_id = create_test_onboarding_token()
    
    print(f"\n📋 Test Employee ID: {employee_id}")
    print("\n🔑 Generated Token:")
    print(f"  {token}")
    
    print("\n🔗 Complete Onboarding URL:")
    print(f"  http://localhost:3000/onboard?token={token}")
    
    print("\n📌 Alternative Demo URL (uses hardcoded demo data):")
    print("  http://localhost:3000/onboard?token=demo-token")
    
    print("\n" + "=" * 60)
    print("✅ Token created successfully!")
    print("\nUse either URL above to start the onboarding process.")
    print("The first URL uses your generated token with test data.")
    print("The second URL uses the hardcoded demo mode.")
    print("=" * 60)

if __name__ == "__main__":
    main()