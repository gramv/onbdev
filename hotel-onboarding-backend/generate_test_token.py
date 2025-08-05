#!/usr/bin/env python3
"""Generate a test JWT token for onboarding"""

import jwt
from datetime import datetime, timedelta
import json

# Secret key (should match your backend configuration)
SECRET_KEY = "your-secret-key-here"  # Replace with your actual secret key

# Token payload
payload = {
    "employee_id": "test-employee-001",
    "property_id": "test-property-001",
    "session_id": "test-session-001",
    "exp": datetime.utcnow() + timedelta(days=7),  # 7 day expiration
    "iat": datetime.utcnow(),
    "type": "onboarding"
}

# Generate token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

print("\n=== TEST ONBOARDING TOKEN ===")
print(f"\nToken: {token}")
print(f"\nOnboarding URL: http://localhost:3000/onboard?token={token}")
print(f"\nExpires: {payload['exp']}")
print("\n=== TOKEN PAYLOAD ===")
print(json.dumps(payload, indent=2, default=str))
print("\n")