"""
Authentication and token management for the onboarding system
"""
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "72"))  # 3 days default

class OnboardingTokenManager:
    """Manages secure onboarding tokens with JWT"""
    
    @staticmethod
    def create_onboarding_token(
        employee_id: str,
        application_id: Optional[str] = None,
        expires_hours: int = JWT_ACCESS_TOKEN_EXPIRE_HOURS
    ) -> Dict[str, Any]:
        """
        Create a secure onboarding token for an employee
        
        Args:
            employee_id: The employee's ID
            application_id: Optional application ID if coming from job application
            expires_hours: Token expiration in hours
            
        Returns:
            Dictionary containing token and expiration info
        """
        expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
        
        # Create payload with necessary information
        payload = {
            "employee_id": employee_id,
            "application_id": application_id,
            "token_type": "onboarding",
            "iat": datetime.now(timezone.utc),
            "exp": expire,
            "jti": secrets.token_urlsafe(16)  # Unique token ID for revocation if needed
        }
        
        # Generate JWT token
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        return {
            "token": token,
            "expires_at": expire,
            "expires_in_hours": expires_hours,
            "token_id": payload["jti"]
        }
    
    @staticmethod
    def verify_onboarding_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode an onboarding token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Dictionary containing token payload if valid
            
        Raises:
            jwt.ExpiredSignatureError: If token is expired
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Verify token type
            if payload.get("token_type") != "onboarding":
                raise jwt.InvalidTokenError("Invalid token type")
            
            return {
                "valid": True,
                "employee_id": payload.get("employee_id"),
                "application_id": payload.get("application_id"),
                "token_id": payload.get("jti"),
                "issued_at": datetime.fromtimestamp(payload.get("iat"), timezone.utc) if payload.get("iat") else datetime.now(timezone.utc),
                "expires_at": datetime.fromtimestamp(payload.get("exp"), timezone.utc) if payload.get("exp") else None
            }
            
        except jwt.ExpiredSignatureError:
            return {
                "valid": False,
                "error": "Token has expired",
                "error_code": "TOKEN_EXPIRED"
            }
        except jwt.InvalidTokenError as e:
            return {
                "valid": False,
                "error": f"Invalid token: {str(e)}",
                "error_code": "INVALID_TOKEN"
            }
    
    @staticmethod
    def create_manager_token(manager_id: str, property_id: str) -> Dict[str, Any]:
        """Create a secure token for manager authentication"""
        expire = datetime.now(timezone.utc) + timedelta(hours=24)  # Shorter expiration for managers
        
        payload = {
            "manager_id": manager_id,
            "property_id": property_id,
            "token_type": "manager_auth",
            "iat": datetime.now(timezone.utc),
            "exp": expire,
            "jti": secrets.token_urlsafe(16)
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        return {
            "token": token,
            "expires_at": expire,
            "token_id": payload["jti"]
        }
    
    @staticmethod
    def verify_manager_token(token: str) -> Dict[str, Any]:
        """Verify manager authentication token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            if payload.get("token_type") != "manager_auth":
                raise jwt.InvalidTokenError("Invalid token type")
            
            return {
                "valid": True,
                "manager_id": payload.get("manager_id"),
                "property_id": payload.get("property_id"),
                "token_id": payload.get("jti")
            }
            
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError as e:
            return {"valid": False, "error": f"Invalid token: {str(e)}"}

class PasswordManager:
    """Utility class for password hashing and verification"""
    
    def __init__(self):
        # Simple in-memory password storage for development
        self.passwords = {}
    
    def store_password(self, email: str, password: str):
        """Store a password (hashed) for a user"""
        hashed = self.hash_password(password)
        self.passwords[email] = hashed
    
    def verify_user_password(self, email: str, password: str) -> bool:
        """Verify a user's password"""
        if email not in self.passwords:
            return False
        return self.verify_password(password, self.passwords[email])
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_secure_code(length: int = 8) -> str:
        """Generate a secure random code for access codes"""
        return secrets.token_urlsafe(length)[:length].upper()