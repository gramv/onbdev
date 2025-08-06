#!/usr/bin/env python3
"""
Enhanced Supabase Database Service
Based on 2024 Best Practices for Production Applications

Features:
- Connection pooling and retry logic
- Comprehensive error handling
- Security-first approach with RLS
- Performance optimization
- Audit logging
- Data encryption for sensitive fields
- Federal compliance support
"""

import os
import json
import asyncio
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Any, Union
from contextlib import asynccontextmanager
import logging
from dataclasses import asdict
import uuid
from functools import wraps

# Supabase and database imports
from supabase import create_client, Client
from postgrest.exceptions import APIError
import asyncpg
from cryptography.fernet import Fernet

# Import existing models
from .models import (
    User, Property, JobApplication, Employee, 
    ApplicationStatus, UserRole, JobApplicationData,
    OnboardingSession, OnboardingStatus, OnboardingStep
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseConnectionError(Exception):
    """Custom exception for Supabase connection issues"""
    pass

class SupabaseSecurityError(Exception):
    """Custom exception for security-related issues"""
    pass

class SupabaseComplianceError(Exception):
    """Custom exception for compliance violations"""
    pass

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed database operations"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

import uuid
from datetime import datetime

class EnhancedSupabaseService:
    """
    Enhanced Supabase service with production-ready features
    """
    
    def __init__(self):
        """Initialize Enhanced Supabase client with security and performance features"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")  # For admin operations
        
        if not self.supabase_url or not self.supabase_anon_key:
            raise SupabaseConnectionError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
        
        # Initialize clients
        self.client: Client = create_client(self.supabase_url, self.supabase_anon_key)
        
        # Admin client for privileged operations
        if self.supabase_service_key:
            self.admin_client: Client = create_client(self.supabase_url, self.supabase_service_key)
        else:
            self.admin_client = self.client
            logger.warning("SUPABASE_SERVICE_KEY not set, using anon key for admin operations")
        
        # Initialize encryption
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        if self.encryption_key:
            self.cipher = Fernet(self.encryption_key.encode())
        else:
            logger.warning("ENCRYPTION_KEY not set, sensitive data will not be encrypted")
            self.cipher = None
        
        # Connection pool for direct PostgreSQL access
        self.db_pool = None
        
        # Performance metrics
        self.query_metrics = {
            "total_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0
        }
        
        logger.info("✅ Enhanced Supabase service initialized")
    
    async def initialize_db_pool(self):
        """Initialize direct PostgreSQL connection pool for complex queries"""
        try:
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                self.db_pool = await asyncpg.create_pool(
                    database_url,
                    min_size=5,
                    max_size=20,
                    command_timeout=30
                )
                logger.info("✅ PostgreSQL connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DB pool: {e}")
    
    async def close_db_pool(self):
        """Close the database connection pool"""
        if self.db_pool:
            await self.db_pool.close()
            logger.info("Database connection pool closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection health"""
        try:
            # Simple query to test connection
            result = self.client.table('users').select('id').limit(1).execute()
            return {
                "status": "healthy",
                "connection": "active",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "connection": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in data dictionary"""
        if not self.cipher:
            return data
        
        sensitive_fields = ['ssn', 'date_of_birth', 'phone', 'address', 'email']
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in data and data[field]:
                try:
                    encrypted_value = self.cipher.encrypt(str(data[field]).encode()).decode()
                    encrypted_data[f"{field}_encrypted"] = encrypted_value
                    # Keep original for backward compatibility, remove in production
                    # del encrypted_data[field]
                except Exception as e:
                    logger.error(f"Failed to encrypt field {field}: {e}")
        
        return encrypted_data
    
    def decrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in data dictionary"""
        if not self.cipher:
            return data
        
        decrypted_data = data.copy()
        
        for key, value in data.items():
            if key.endswith('_encrypted') and value:
                try:
                    original_field = key.replace('_encrypted', '')
                    decrypted_value = self.cipher.decrypt(value.encode()).decode()
                    decrypted_data[original_field] = decrypted_value
                except Exception as e:
                    logger.error(f"Failed to decrypt field {key}: {e}")
        
        return decrypted_data
    
    def generate_duplicate_hash(self, email: str, property_id: str, position: str) -> str:
        """Generate hash for duplicate application detection"""
        data = f"{email.lower()}{property_id}{position.lower()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def log_audit_event(self, table_name: str, record_id: str, action: str, 
                            old_values: Optional[Dict] = None, new_values: Optional[Dict] = None,
                            user_id: Optional[str] = None, compliance_event: bool = False):
        """Log audit events for compliance tracking"""
        try:
            audit_data = {
                "id": str(uuid.uuid4()),
                "table_name": table_name,
                "record_id": record_id,
                "action": action,
                "old_values": old_values,
                "new_values": new_values,
                "user_id": user_id,
                "compliance_event": compliance_event,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            result = self.admin_client.table('audit_log').insert(audit_data).execute()
            logger.info(f"Audit event logged: {action} on {table_name}")
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    @retry_on_failure(max_retries=3)
    async def execute_with_metrics(self, operation_name: str, operation_func):
        """Execute database operation with performance metrics"""
        start_time = datetime.now()
        self.query_metrics["total_queries"] += 1
        
        try:
            result = await operation_func()
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.query_metrics["avg_response_time"] = (
                (self.query_metrics["avg_response_time"] * (self.query_metrics["total_queries"] - 1) + execution_time) /
                self.query_metrics["total_queries"]
            )
            
            logger.debug(f"Operation {operation_name} completed in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            self.query_metrics["failed_queries"] += 1
            logger.error(f"Operation {operation_name} failed: {e}")
            raise
    
    # =====================================================
    # ENHANCED USER OPERATIONS
    # =====================================================
    
    async def create_user_with_role(self, user: User, role_assignments: List[str] = None) -> Dict[str, Any]:
        """Create user with proper role assignments and audit logging"""
        try:
            # Encrypt sensitive data
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "property_id": str(user.property_id) if user.property_id else None,
                "is_active": user.is_active,
                "password_hash": user.password_hash,
                "created_at": user.created_at.isoformat(),
                "created_by": str(user.id)  # Self-created for now
            }
            
            # Create user
            result = self.admin_client.table('users').insert(user_data).execute()
            created_user = result.data[0] if result.data else None
            
            if created_user:
                # Assign roles if specified
                if role_assignments:
                    await self.assign_user_roles(str(user.id), role_assignments)
                
                # Log audit event
                await self.log_audit_event(
                    "users", str(user.id), "INSERT", 
                    new_values=user_data, compliance_event=True
                )
                
                logger.info(f"User created successfully: {user.email}")
            
            return created_user
            
        except Exception as e:
            logger.error(f"Failed to create user {user.email}: {e}")
            raise SupabaseConnectionError(f"User creation failed: {e}")
    
    async def assign_user_roles(self, user_id: str, role_names: List[str]) -> List[Dict[str, Any]]:
        """Assign multiple roles to a user"""
        try:
            # Get role IDs
            roles_result = self.admin_client.table('user_roles').select('id, name').in_('name', role_names).execute()
            roles = {role['name']: role['id'] for role in roles_result.data}
            
            # Create role assignments
            assignments = []
            for role_name in role_names:
                if role_name in roles:
                    assignments.append({
                        "user_id": user_id,
                        "role_id": roles[role_name],
                        "assigned_by": user_id,  # Self-assigned for now
                        "assigned_at": datetime.now(timezone.utc).isoformat()
                    })
            
            if assignments:
                result = self.admin_client.table('user_role_assignments').insert(assignments).execute()
                logger.info(f"Assigned {len(assignments)} roles to user {user_id}")
                return result.data
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to assign roles to user {user_id}: {e}")
            raise
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with enhanced security checks"""
        try:
            # Get user with security fields
            result = self.client.table('users').select(
                '*, user_role_assignments(user_roles(name, permissions))'
            ).eq('email', email).eq('is_active', True).execute()
            
            if not result.data:
                logger.warning(f"Authentication failed: User not found - {email}")
                return None
            
            user = result.data[0]
            
            # Check if account is locked
            if user.get('locked_until'):
                locked_until = datetime.fromisoformat(user['locked_until'].replace('Z', '+00:00'))
                if locked_until > datetime.now(timezone.utc):
                    logger.warning(f"Authentication failed: Account locked - {email}")
                    return None
            
            # Verify password (implement your password verification logic)
            # This is a placeholder - implement proper password hashing verification
            if self.verify_password(password, user.get('password_hash', '')):
                # Reset failed attempts on successful login
                await self.reset_failed_login_attempts(user['id'])
                
                # Update last login
                self.admin_client.table('users').update({
                    'last_login_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', user['id']).execute()
                
                logger.info(f"User authenticated successfully: {email}")
                return user
            else:
                # Increment failed attempts
                await self.increment_failed_login_attempts(user['id'])
                logger.warning(f"Authentication failed: Invalid password - {email}")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return None
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash using bcrypt"""
        import bcrypt
        try:
            if not password_hash:
                return False
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    async def increment_failed_login_attempts(self, user_id: str):
        """Increment failed login attempts and lock account if necessary"""
        try:
            # Get current attempts
            result = self.admin_client.table('users').select('failed_login_attempts').eq('id', user_id).execute()
            current_attempts = result.data[0]['failed_login_attempts'] if result.data else 0
            
            new_attempts = current_attempts + 1
            update_data = {'failed_login_attempts': new_attempts}
            
            # Lock account after 5 failed attempts
            if new_attempts >= 5:
                update_data['locked_until'] = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
                logger.warning(f"Account locked due to failed attempts: {user_id}")
            
            self.admin_client.table('users').update(update_data).eq('id', user_id).execute()
            
        except Exception as e:
            logger.error(f"Failed to increment login attempts for {user_id}: {e}")
    
    async def reset_failed_login_attempts(self, user_id: str):
        """Reset failed login attempts on successful authentication"""
        try:
            self.admin_client.table('users').update({
                'failed_login_attempts': 0,
                'locked_until': None
            }).eq('id', user_id).execute()
        except Exception as e:
            logger.error(f"Failed to reset login attempts for {user_id}: {e}")
    
    # =====================================================
    # ENHANCED PROPERTY OPERATIONS
    # =====================================================
    
    async def create_property_with_managers(self, property_obj: Property, manager_ids: List[str] = None) -> Dict[str, Any]:
        """Create property and assign managers in a transaction"""
        try:
            # Prepare property data
            property_data = {
                "id": str(property_obj.id),
                "name": property_obj.name,
                "address": property_obj.address,
                "city": property_obj.city,
                "state": property_obj.state,
                "zip_code": property_obj.zip_code,
                "phone": property_obj.phone,
                "qr_code_url": property_obj.qr_code_url,
                "is_active": property_obj.is_active,
                "created_at": property_obj.created_at.isoformat(),
            }
            
            # Create property
            result = self.admin_client.table('properties').insert(property_data).execute()
            created_property = result.data[0] if result.data else None
            
            if created_property and manager_ids:
                # Assign managers
                await self.assign_managers_to_property(str(property_obj.id), manager_ids)
            
            # Log audit event
            await self.log_audit_event(
                "properties", str(property_obj.id), "INSERT",
                new_values=property_data, compliance_event=True
            )
            
            logger.info(f"Property created successfully: {property_obj.name}")
            return created_property
            
        except Exception as e:
            logger.error(f"Failed to create property {property_obj.name}: {e}")
            raise SupabaseConnectionError(f"Property creation failed: {e}")
    
    async def assign_managers_to_property(self, property_id: str, manager_ids: List[str], 
                                        assigned_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Assign multiple managers to a property with permissions"""
        try:
            assignments = []
            for manager_id in manager_ids:
                assignments.append({
                    "property_id": property_id,
                    "manager_id": manager_id,
                    "assigned_by": assigned_by,
                    "assigned_at": datetime.now(timezone.utc).isoformat(),
                    "permissions": {
                        "can_approve": True,
                        "can_reject": True,
                        "can_hire": True,
                        "can_manage_onboarding": True
                    }
                })
            
            # Use upsert to handle duplicates
            result = self.admin_client.table('property_managers').upsert(assignments).execute()
            
            # Update user property_id for managers
            for manager_id in manager_ids:
                self.admin_client.table('users').update({
                    "property_id": property_id
                }).eq('id', manager_id).execute()
            
            logger.info(f"Assigned {len(manager_ids)} managers to property {property_id}")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to assign managers to property {property_id}: {e}")
            raise
    
    # =====================================================
    # ENHANCED APPLICATION OPERATIONS
    # =====================================================
    
    async def create_job_application_with_validation(self, application: JobApplication) -> Dict[str, Any]:
        """Create job application with duplicate detection and validation"""
        try:
            # Check for duplicates
            duplicate_hash = self.generate_duplicate_hash(
                application.applicant_data.get('email', ''),
                str(application.property_id),
                application.position
            )
            
            existing = self.client.table('job_applications').select('id').eq(
                'duplicate_check_hash', duplicate_hash
            ).execute()
            
            if existing.data:
                raise SupabaseComplianceError(f"Duplicate application detected for {application.applicant_data.get('email')}")
            
            # Encrypt sensitive applicant data
            encrypted_applicant_data = self.encrypt_sensitive_data(application.applicant_data)
            
            # Prepare application data
            application_data = {
                "id": str(application.id),
                "property_id": str(application.property_id),
                "department": application.department,
                "position": application.position,
                "applicant_data": application.applicant_data,
                "applicant_data_encrypted": encrypted_applicant_data,
                "status": application.status.value,
                "applied_at": application.applied_at.isoformat(),
                "duplicate_check_hash": duplicate_hash,
                "source": "qr_code",
                "gdpr_consent": True,  # Assume consent given
                "data_retention_until": (datetime.now(timezone.utc) + timedelta(days=2555)).isoformat()  # 7 years
            }
            
            # Create application
            result = self.client.table('job_applications').insert(application_data).execute()
            created_application = result.data[0] if result.data else None
            
            if created_application:
                # Log status history
                await self.add_application_status_history(
                    str(application.id), None, application.status.value,
                    reason="Initial application submission"
                )
                
                # Log audit event
                await self.log_audit_event(
                    "job_applications", str(application.id), "INSERT",
                    new_values=application_data, compliance_event=True
                )
                
                logger.info(f"Application created successfully: {application.applicant_data.get('email')}")
            
            return created_application
            
        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            raise
    
    async def update_application_status_with_audit(self, application_id: str, new_status: str, 
                                                 reviewed_by: Optional[str] = None, 
                                                 reason: Optional[str] = None,
                                                 notes: Optional[str] = None) -> Dict[str, Any]:
        """Update application status with comprehensive audit trail"""
        try:
            # Get current application
            current_result = self.client.table('job_applications').select('*').eq('id', application_id).execute()
            if not current_result.data:
                raise ValueError(f"Application {application_id} not found")
            
            current_app = current_result.data[0]
            old_status = current_app['status']
            
            # Prepare update data
            update_data = {
                "status": new_status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            if reviewed_by:
                update_data['reviewed_by'] = reviewed_by
                update_data['reviewed_at'] = datetime.now(timezone.utc).isoformat()
            
            if reason:
                update_data['rejection_reason'] = reason
            
            if new_status == 'talent_pool':
                update_data['talent_pool_date'] = datetime.now(timezone.utc).isoformat()
            
            # Update application
            result = self.admin_client.table('job_applications').update(update_data).eq('id', application_id).execute()
            updated_application = result.data[0] if result.data else None
            
            if updated_application:
                # Add to status history
                await self.add_application_status_history(
                    application_id, old_status, new_status,
                    changed_by=reviewed_by, reason=reason, notes=notes
                )
                
                # Log audit event
                await self.log_audit_event(
                    "job_applications", application_id, "UPDATE",
                    old_values=current_app, new_values=updated_application,
                    user_id=reviewed_by, compliance_event=True
                )
                
                logger.info(f"Application {application_id} status updated: {old_status} -> {new_status}")
            
            return updated_application
            
        except Exception as e:
            logger.error(f"Failed to update application status: {e}")
            raise
    
    async def add_application_status_history(self, application_id: str, old_status: Optional[str],
                                           new_status: str, changed_by: Optional[str] = None,
                                           reason: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, Any]:
        """Add detailed application status history"""
        try:
            history_data = {
                "id": str(uuid.uuid4()),
                "application_id": application_id,
                "old_status": old_status,
                "new_status": new_status,
                "changed_by": changed_by,
                "changed_at": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
                "notes": notes,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "system_generated": changed_by is None
                }
            }
            
            result = self.admin_client.table('application_status_history').insert(history_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Failed to add status history: {e}")
            raise
    
    # =====================================================
    # ENHANCED QUERY OPERATIONS
    # =====================================================
    
    async def get_applications_with_analytics(self, property_id: Optional[str] = None, 
                                            manager_id: Optional[str] = None,
                                            filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Get applications with built-in analytics and filtering"""
        try:
            # Build base query
            query = self.client.table('job_applications').select(
                '*, properties(name, city, state), users(first_name, last_name)'
            )
            
            # Apply filters
            if property_id:
                query = query.eq('property_id', property_id)
            elif manager_id:
                # Get manager's properties first
                manager_props = await self.get_manager_properties(manager_id)
                property_ids = [prop['property_id'] for prop in manager_props]
                if property_ids:
                    query = query.in_('property_id', property_ids)
                else:
                    return {"applications": [], "analytics": {}}
            
            if filters:
                if 'status' in filters:
                    query = query.eq('status', filters['status'])
                if 'department' in filters:
                    query = query.eq('department', filters['department'])
                if 'date_from' in filters:
                    query = query.gte('applied_at', filters['date_from'])
                if 'date_to' in filters:
                    query = query.lte('applied_at', filters['date_to'])
            
            # Execute query
            result = query.order('applied_at', desc=True).execute()
            applications = result.data or []
            
            # Decrypt sensitive data
            for app in applications:
                if app.get('applicant_data_encrypted'):
                    app['applicant_data'] = self.decrypt_sensitive_data(app['applicant_data_encrypted'])
            
            # Calculate analytics
            analytics = self.calculate_application_analytics(applications)
            
            return {
                "applications": applications,
                "analytics": analytics,
                "total_count": len(applications)
            }
            
        except Exception as e:
            logger.error(f"Failed to get applications with analytics: {e}")
            raise
    
    def calculate_application_analytics(self, applications: List[Dict]) -> Dict[str, Any]:
        """Calculate analytics from application data"""
        if not applications:
            return {}
        
        total = len(applications)
        status_counts = {}
        department_counts = {}
        position_counts = {}
        
        review_times = []
        approval_times = []
        
        for app in applications:
            # Status counts
            status = app.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Department counts
            dept = app.get('department', 'unknown')
            department_counts[dept] = department_counts.get(dept, 0) + 1
            
            # Position counts
            pos = app.get('position', 'unknown')
            position_counts[pos] = position_counts.get(pos, 0) + 1
            
            # Time calculations
            applied_at = datetime.fromisoformat(app['applied_at'].replace('Z', '+00:00'))
            
            if app.get('reviewed_at'):
                reviewed_at = datetime.fromisoformat(app['reviewed_at'].replace('Z', '+00:00'))
                review_time = (reviewed_at - applied_at).total_seconds() / 3600  # hours
                review_times.append(review_time)
                
                if app.get('status') == 'approved':
                    approval_times.append(review_time)
        
        return {
            "total_applications": total,
            "status_breakdown": status_counts,
            "department_breakdown": department_counts,
            "position_breakdown": position_counts,
            "avg_review_time_hours": sum(review_times) / len(review_times) if review_times else 0,
            "avg_approval_time_hours": sum(approval_times) / len(approval_times) if approval_times else 0,
            "approval_rate": (status_counts.get('approved', 0) / total * 100) if total > 0 else 0,
            "rejection_rate": (status_counts.get('rejected', 0) / total * 100) if total > 0 else 0
        }
    
    # =====================================================
    # ONBOARDING OPERATIONS
    # =====================================================
    
    async def create_onboarding_session(self, employee_id: str, expires_hours: int = 72) -> Dict[str, Any]:
        """Create secure onboarding session with token"""
        try:
            session_id = str(uuid.uuid4())
            token = self.generate_secure_token()
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
            
            session_data = {
                "id": session_id,
                "employee_id": employee_id,
                "token": token,
                "status": OnboardingStatus.NOT_STARTED.value,
                "current_step": OnboardingStep.WELCOME.value,
                "language_preference": "en",
                "steps_completed": [],
                "progress_percentage": 0.0,
                "form_data": {},
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = self.admin_client.table('onboarding_sessions').insert(session_data).execute()
            created_session = result.data[0] if result.data else None
            
            if created_session:
                # Log audit event
                await self.log_audit_event(
                    "onboarding_sessions", session_id, "INSERT",
                    new_values=session_data, compliance_event=True
                )
                
                logger.info(f"Onboarding session created for employee {employee_id}")
            
            return created_session
            
        except Exception as e:
            logger.error(f"Failed to create onboarding session: {e}")
            raise
    
    def generate_secure_token(self) -> str:
        """Generate cryptographically secure token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    # =====================================================
    # HEALTH AND MONITORING
    # =====================================================
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Comprehensive health check with performance metrics"""
        health_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "healthy",
            "database": "supabase_postgresql",
            "connection": "active",
            "performance_metrics": self.query_metrics.copy(),
            "checks": {}
        }
        
        try:
            # Test basic connectivity
            start_time = datetime.now()
            result = self.client.table('users').select('count').limit(1).execute()
            connection_time = (datetime.now() - start_time).total_seconds()
            
            health_data["checks"]["database_connectivity"] = {
                "status": "pass",
                "response_time_ms": connection_time * 1000
            }
            
            # Test RLS policies
            try:
                self.client.table('users').select('*').limit(1).execute()
                health_data["checks"]["rls_policies"] = {"status": "pass"}
            except Exception as e:
                health_data["checks"]["rls_policies"] = {"status": "fail", "error": str(e)}
            
            # Check connection pool
            if self.db_pool:
                pool_status = "active" if not self.db_pool._closed else "closed"
                health_data["checks"]["connection_pool"] = {
                    "status": "pass" if pool_status == "active" else "fail",
                    "pool_status": pool_status
                }
            
            # Check encryption
            health_data["checks"]["encryption"] = {
                "status": "pass" if self.cipher else "warning",
                "encryption_enabled": bool(self.cipher)
            }
            
        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)
            health_data["checks"]["database_connectivity"] = {"status": "fail", "error": str(e)}
        
        return health_data
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            stats = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "database_type": "supabase_postgresql",
                "performance_metrics": self.query_metrics.copy()
            }
            
            # Get table counts
            tables = ['users', 'properties', 'job_applications', 'employees', 'onboarding_sessions']
            for table in tables:
                try:
                    result = self.admin_client.table(table).select('count').execute()
                    stats[f"{table}_count"] = len(result.data) if result.data else 0
                except Exception as e:
                    stats[f"{table}_count"] = f"error: {e}"
            
            # Get recent activity
            try:
                recent_apps = self.client.table('job_applications').select('applied_at').gte(
                    'applied_at', (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
                ).execute()
                stats["applications_last_7_days"] = len(recent_apps.data) if recent_apps.data else 0
            except Exception as e:
                stats["applications_last_7_days"] = f"error: {e}"
            
            return stats
            
        except Exception as e:
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    # =====================================================
    # CLEANUP AND MAINTENANCE
    # =====================================================
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired onboarding sessions"""
        try:
            # Get expired sessions
            expired_result = self.admin_client.table('onboarding_sessions').select('id').lt(
                'expires_at', datetime.now(timezone.utc).isoformat()
            ).not_.in_('status', ['approved', 'completed']).execute()
            
            expired_ids = [session['id'] for session in expired_result.data] if expired_result.data else []
            
            if expired_ids:
                # Delete expired sessions
                self.admin_client.table('onboarding_sessions').delete().in_('id', expired_ids).execute()
                
                # Log cleanup
                await self.log_audit_event(
                    "onboarding_sessions", "bulk_cleanup", "DELETE",
                    old_values={"expired_session_ids": expired_ids},
                    compliance_event=True
                )
                
                logger.info(f"Cleaned up {len(expired_ids)} expired onboarding sessions")
            
            return len(expired_ids)
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
    
    async def archive_old_applications(self, days_old: int = 2555) -> int:
        """Archive applications older than specified days (default 7 years for compliance)"""
        try:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
            
            # Get old applications
            old_apps = self.admin_client.table('job_applications').select('id').lt(
                'applied_at', cutoff_date
            ).execute()
            
            old_app_ids = [app['id'] for app in old_apps.data] if old_apps.data else []
            
            if old_app_ids:
                # In a real implementation, you would move these to an archive table
                # For now, we'll just log the archival
                await self.log_audit_event(
                    "job_applications", "bulk_archive", "ARCHIVE",
                    old_values={"archived_application_ids": old_app_ids},
                    compliance_event=True
                )
                
                logger.info(f"Archived {len(old_app_ids)} old applications")
            
            return len(old_app_ids)
            
        except Exception as e:
            logger.error(f"Failed to archive old applications: {e}")
            return 0
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            result = self.client.table("users").select("*").eq("email", email.lower()).execute()
            
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=UserRole(user_data["role"]),
                    property_id=user_data.get("property_id"),
                    password_hash=user_data.get("password_hash"),  # Include password hash for authentication
                    is_active=user_data.get("is_active", True),
                    created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00'))
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=UserRole(user_data["role"]),
                    property_id=user_data.get("property_id"),
                    password_hash=user_data.get("password_hash"),  # Include password hash for authentication
                    is_active=user_data.get("is_active", True),
                    created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00'))
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    async def get_property_by_id(self, property_id: str) -> Optional[Property]:
        """Get property by ID"""
        try:
            result = self.client.table("properties").select("*").eq("id", property_id).execute()
            
            if result.data:
                prop_data = result.data[0]
                return Property(
                    id=prop_data["id"],
                    name=prop_data["name"],
                    address=prop_data["address"],
                    city=prop_data["city"],
                    state=prop_data["state"],
                    zip_code=prop_data["zip_code"],
                    phone=prop_data["phone"],
                    is_active=prop_data.get("is_active", True),
                    created_at=datetime.fromisoformat(prop_data["created_at"].replace('Z', '+00:00'))
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get property by ID {property_id}: {e}")
            return None
    
    async def get_manager_properties(self, manager_id: str) -> List[Property]:
        """Get properties assigned to a manager"""
        try:
            result = self.client.table("property_managers").select(
                "properties(*)"
            ).eq("manager_id", manager_id).execute()
            
            properties = []
            for item in result.data:
                if item.get("properties"):
                    prop_data = item["properties"]
                    properties.append(Property(
                        id=prop_data["id"],
                        name=prop_data["name"],
                        address=prop_data["address"],
                        city=prop_data["city"],
                        state=prop_data["state"],
                        zip_code=prop_data["zip_code"],
                        phone=prop_data["phone"],
                        is_active=prop_data.get("is_active", True),
                        created_at=datetime.fromisoformat(prop_data["created_at"].replace('Z', '+00:00'))
                    ))
            
            return properties
            
        except Exception as e:
            logger.error(f"Failed to get manager properties for {manager_id}: {e}")
            return []
    
    async def create_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new property using standard client with RLS policies"""
        try:
            # Use the standard client - RLS policies will handle authorization
            result = self.client.table('properties').insert(property_data).execute()
            
            if result.data:
                logger.info(f"Property created successfully: {property_data.get('name')}")
                return {"success": True, "property": result.data[0]}
            else:
                # If no data returned, it might be due to RLS
                logger.warning("Property insert completed but no data returned - check RLS policies")
                return {"success": False, "error": "Property creation failed - please check database permissions"}
                
        except Exception as e:
            error_msg = str(e)
            
            # Provide helpful error messages for common issues
            if "row-level security" in error_msg.lower() or "rls" in error_msg.lower():
                logger.error(f"RLS policy blocking property creation: {e}")
                return {
                    "success": False, 
                    "error": "Database permissions error. Please ensure RLS policies are configured for HR users.",
                    "details": "Run the supabase_rls_setup.sql script in your Supabase SQL editor"
                }
            elif "duplicate key" in error_msg.lower():
                logger.error(f"Property with this ID already exists: {e}")
                return {"success": False, "error": "Property ID already exists"}
            else:
                logger.error(f"Property creation failed: {e}")
                return {"success": False, "error": f"Property creation failed: {error_msg}"}
    
    async def assign_manager_to_property(self, manager_id: str, property_id: str) -> bool:
        """Assign a manager to a property"""
        try:
            result = self.client.table("property_managers").insert({
                "manager_id": manager_id,
                "property_id": property_id,
                "assigned_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to assign manager {manager_id} to property {property_id}: {e}")
            return False
    
    async def get_applications_by_email_and_property(self, email: str, property_id: str) -> List[JobApplication]:
        """Get applications by email and property"""
        try:
            result = self.client.table("job_applications").select("*").eq(
                "applicant_email", email.lower()
            ).eq("property_id", property_id).execute()
            
            applications = []
            for app_data in result.data:
                applications.append(JobApplication(
                    id=app_data["id"],
                    property_id=app_data["property_id"],
                    department=app_data["department"],
                    position=app_data["position"],
                    applicant_data=app_data["applicant_data"],
                    status=ApplicationStatus(app_data["status"]),
                    applied_at=datetime.fromisoformat(app_data["applied_at"].replace('Z', '+00:00'))
                ))
            
            return applications
            
        except Exception as e:
            logger.error(f"Failed to get applications by email {email} and property {property_id}: {e}")
            return []
    
    # Synchronous wrapper methods for compatibility
    def get_user_by_email_sync(self, email: str) -> Optional[User]:
        """Synchronous wrapper for get_user_by_email"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.get_user_by_email(email))
            return future.result()
    
    def get_user_by_id_sync(self, user_id: str) -> Optional[User]:
        """Synchronous wrapper for get_user_by_id"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.get_user_by_id(user_id))
            return future.result()
    
    def get_property_by_id_sync(self, property_id: str) -> Optional[Property]:
        """Synchronous wrapper for get_property_by_id"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.get_property_by_id(property_id))
            return future.result()
    
    def get_manager_properties_sync(self, manager_id: str) -> List[Property]:
        """Synchronous wrapper for get_manager_properties"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.get_manager_properties(manager_id))
            return future.result()
    
    def create_application_sync(self, application: JobApplication) -> JobApplication:
        """Synchronous wrapper for create_application"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.create_application(application))
            return future.result()
    
    def get_applications_by_email_and_property_sync(self, email: str, property_id: str) -> List[JobApplication]:
        """Synchronous wrapper for get_applications_by_email_and_property"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.get_applications_by_email_and_property(email, property_id))
            return future.result()
    
    def get_application_by_id_sync(self, application_id: str) -> Optional[JobApplication]:
        """Synchronous wrapper for get_application_by_id"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.get_application_by_id(application_id))
            return future.result()
    
    def get_employee_by_id_sync(self, employee_id: str) -> Optional[Employee]:
        """Synchronous wrapper for get_employee_by_id"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.get_employee_by_id(employee_id))
            return future.result()
    
    def get_onboarding_session_by_id_sync(self, session_id: str) -> Optional[OnboardingSession]:
        """Synchronous wrapper for get_onboarding_session_by_id"""
        import asyncio
        import concurrent.futures
        
        # Use thread pool to run async function
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, self.get_onboarding_session_by_id(session_id))
            return future.result()
    
    async def get_onboarding_session_by_id(self, session_id: str) -> Optional[OnboardingSession]:
        """Get onboarding session by ID"""
        try:
            response = self.client.table('onboarding_sessions').select('*').eq('id', session_id).execute()
            
            if response.data:
                session_data = response.data[0]
                return OnboardingSession(
                    id=session_data['id'],
                    employee_id=session_data['employee_id'],
                    application_id=session_data.get('application_id'),
                    property_id=session_data['property_id'],
                    manager_id=session_data.get('manager_id'),
                    token=session_data.get('token'),
                    status=OnboardingStatus(session_data.get('status', 'not_started')),
                    expires_at=datetime.fromisoformat(session_data['expires_at']) if session_data.get('expires_at') else None,
                    created_at=datetime.fromisoformat(session_data['created_at']) if session_data.get('created_at') else datetime.now(timezone.utc),
                    updated_at=datetime.fromisoformat(session_data['updated_at']) if session_data.get('updated_at') else datetime.now(timezone.utc)
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting onboarding session by ID {session_id}: {e}")
            return None

    # Dashboard Statistics Methods
    async def get_properties_count(self) -> int:
        """Get count of active properties"""
        try:
            response = self.client.table('properties').select('id', count='exact').eq('is_active', True).execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error getting properties count: {e}")
            return 0
    
    async def get_managers_count(self) -> int:
        """Get count of active managers"""
        try:
            response = self.client.table('users').select('id', count='exact').eq('role', 'manager').eq('is_active', True).execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error getting managers count: {e}")
            return 0
    
    async def get_employees_count(self) -> int:
        """Get count of active employees"""
        try:
            response = self.client.table('employees').select('id', count='exact').eq('employment_status', 'active').execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error getting employees count: {e}")
            return 0
    
    async def get_pending_applications_count(self) -> int:
        """Get count of pending applications"""
        try:
            response = self.client.table('job_applications').select('id', count='exact').eq('status', 'pending').execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Error getting pending applications count: {e}")
            return 0

    async def get_all_properties(self) -> List[Property]:
        """Get all properties"""
        try:
            response = self.client.table('properties').select('*').execute()
            logger.info(f"Raw properties from DB: {len(response.data)} properties found")
            
            properties = []
            for row in response.data:
                try:
                    # Handle various datetime formats
                    created_at = None
                    if row.get('created_at'):
                        created_at_str = row['created_at']
                        # Handle timezone-aware timestamps
                        if 'T' in created_at_str:
                            created_at_str = created_at_str.replace('Z', '+00:00')
                            if '+' not in created_at_str and '-' not in created_at_str[-6:]:
                                created_at_str += '+00:00'
                        created_at = datetime.fromisoformat(created_at_str)
                    
                    prop = Property(
                        id=row['id'],
                        name=row['name'],
                        address=row['address'],
                        city=row.get('city', ''),  # Make city optional
                        state=row.get('state', ''),  # Make state optional
                        zip_code=row.get('zip_code', ''),  # Make zip optional
                        phone=row.get('phone', ''),
                        is_active=row.get('is_active', True),
                        created_at=created_at
                    )
                    properties.append(prop)
                    logger.debug(f"Added property: {prop.name} ({prop.id})")
                except Exception as prop_error:
                    logger.error(f"Error parsing property {row.get('id', 'unknown')}: {prop_error}")
                    logger.error(f"Property data: {row}")
                    
            logger.info(f"Returning {len(properties)} properties")
            return properties
        except Exception as e:
            logger.error(f"Error getting all properties: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    async def get_all_applications(self) -> List[JobApplication]:
        """Get all applications"""
        try:
            response = self.client.table('job_applications').select('*').execute()
            applications = []
            for row in response.data:
                applications.append(JobApplication(
                    id=row['id'],
                    property_id=row['property_id'],
                    department=row['department'],
                    position=row['position'],
                    applicant_data=row['applicant_data'],
                    status=ApplicationStatus(row['status']),
                    applied_at=datetime.fromisoformat(row['applied_at'].replace('Z', '+00:00'))
                ))
            return applications
        except Exception as e:
            logger.error(f"Error getting all applications: {e}")
            return []

    async def get_application_by_id(self, application_id: str) -> Optional[JobApplication]:
        """Get a single application by ID"""
        try:
            response = self.client.table('job_applications').select('*').eq('id', application_id).execute()
            if response.data:
                row = response.data[0]
                return JobApplication(
                    id=row['id'],
                    property_id=row['property_id'],
                    department=row['department'],
                    position=row['position'],
                    applicant_data=row['applicant_data'],
                    status=ApplicationStatus(row['status']),
                    applied_at=datetime.fromisoformat(row['applied_at'].replace('Z', '+00:00'))
                )
            return None
        except Exception as e:
            logger.error(f"Error getting application by ID {application_id}: {e}")
            return None

    async def get_applications_by_properties(self, property_ids: List[str]) -> List[JobApplication]:
        """Get applications for multiple properties"""
        try:
            response = self.client.table('job_applications').select('*').in_('property_id', property_ids).execute()
            applications = []
            for row in response.data:
                applications.append(JobApplication(
                    id=row['id'],
                    property_id=row['property_id'],
                    department=row['department'],
                    position=row['position'],
                    applicant_data=row['applicant_data'],
                    status=ApplicationStatus(row['status']),
                    applied_at=datetime.fromisoformat(row['applied_at'].replace('Z', '+00:00'))
                ))
            return applications
        except Exception as e:
            logger.error(f"Error getting applications by properties: {e}")
            return []

    async def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        try:
            response = self.client.table('employees').select('*').eq('id', employee_id).execute()
            if response.data:
                row = response.data[0]
                return Employee(
                    id=row['id'],
                    property_id=row['property_id'],
                    department=row['department'],
                    position=row['position'],
                    hire_date=datetime.fromisoformat(row['hire_date']).date() if row.get('hire_date') else None,
                    pay_rate=row.get('pay_rate', 0.0),
                    employment_type=row.get('employment_type', 'full_time'),
                    employment_status=row.get('employment_status', 'active'),
                    onboarding_status=OnboardingStatus(row.get('onboarding_status', 'not_started'))
                )
            return None
        except Exception as e:
            logger.error(f"Error getting employee by ID: {e}")
            return None

    async def get_all_employees(self) -> List[Employee]:
        """Get all employees"""
        try:
            response = self.client.table('employees').select('*').execute()
            employees = []
            for row in response.data:
                employees.append(Employee(
                    id=row['id'],
                    property_id=row['property_id'],
                    department=row['department'],
                    position=row['position'],
                    hire_date=datetime.fromisoformat(row['hire_date']).date() if row.get('hire_date') else None,
                    pay_rate=row.get('pay_rate', 0.0),
                    employment_type=row.get('employment_type', 'full_time'),
                    employment_status=row.get('employment_status', 'active'),
                    onboarding_status=OnboardingStatus(row.get('onboarding_status', 'not_started'))
                ))
            return employees
        except Exception as e:
            logger.error(f"Error getting all employees: {e}")
            return []

    async def get_employees_by_property(self, property_id: str) -> List[Employee]:
        """Get employees by property"""
        try:
            response = self.client.table('employees').select('*').eq('property_id', property_id).execute()
            employees = []
            for row in response.data:
                employees.append(Employee(
                    id=row['id'],
                    property_id=row['property_id'],
                    department=row['department'],
                    position=row['position'],
                    hire_date=datetime.fromisoformat(row['hire_date']).date() if row.get('hire_date') else None,
                    pay_rate=row.get('pay_rate', 0.0),
                    employment_type=row.get('employment_type', 'full_time'),
                    employment_status=row.get('employment_status', 'active'),
                    onboarding_status=OnboardingStatus(row.get('onboarding_status', 'not_started'))
                ))
            return employees
        except Exception as e:
            logger.error(f"Error getting employees by property: {e}")
            return []

    async def get_employees_by_properties(self, property_ids: List[str]) -> List[Employee]:
        """Get employees for multiple properties"""
        try:
            response = self.client.table('employees').select('*').in_('property_id', property_ids).execute()
            employees = []
            for row in response.data:
                employees.append(Employee(
                    id=row['id'],
                    property_id=row['property_id'],
                    department=row['department'],
                    position=row['position'],
                    hire_date=datetime.fromisoformat(row['hire_date']).date() if row.get('hire_date') else None,
                    pay_rate=row.get('pay_rate', 0.0),
                    employment_type=row.get('employment_type', 'full_time'),
                    employment_status=row.get('employment_status', 'active'),
                    onboarding_status=OnboardingStatus(row.get('onboarding_status', 'not_started'))
                ))
            return employees
        except Exception as e:
            logger.error(f"Error getting employees by properties: {e}")
            return []

    async def get_users(self) -> List[User]:
        """Get all users"""
        try:
            response = self.client.table('users').select('*').execute()
            users = []
            for row in response.data:
                users.append(User(
                    id=row['id'],
                    email=row['email'],
                    first_name=row.get('first_name'),
                    last_name=row.get('last_name'),
                    role=UserRole(row['role']),
                    is_active=row.get('is_active', True),
                    created_at=datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')) if row.get('created_at') else None
                ))
            return users
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    # ==========================================
    # BULK OPERATIONS METHODS (Phase 1.1)
    # ==========================================
    
    async def bulk_update_applications(self, application_ids: List[str], status: str, reviewed_by: str, action_type: str = None) -> Dict[str, Any]:
        """Bulk update application status"""
        try:
            success_count = 0
            failed_count = 0
            errors = []
            
            for app_id in application_ids:
                try:
                    update_data = {
                        "status": status,
                        "reviewed_by": reviewed_by,
                        "reviewed_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Add specific fields for talent pool
                    if status == "talent_pool":
                        update_data["talent_pool_date"] = datetime.now(timezone.utc).isoformat()
                    
                    result = self.client.table("job_applications").update(update_data).eq("id", app_id).execute()
                    
                    if result.data:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"No data returned for application {app_id}")
                        
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Failed to update application {app_id}: {str(e)}")
            
            return {
                "success_count": success_count,
                "failed_count": failed_count,
                "total_processed": len(application_ids),
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Bulk update applications failed: {e}")
            return {
                "success_count": 0,
                "failed_count": len(application_ids),
                "total_processed": len(application_ids),
                "errors": [str(e)]
            }
    
    async def bulk_move_to_talent_pool(self, application_ids: List[str], reviewed_by: str) -> Dict[str, Any]:
        """Bulk move applications to talent pool"""
        return await self.bulk_update_applications(
            application_ids=application_ids,
            status="talent_pool",
            reviewed_by=reviewed_by,
            action_type="talent_pool"
        )
    
    async def bulk_reactivate_applications(self, application_ids: List[str], reviewed_by: str) -> Dict[str, Any]:
        """Bulk reactivate applications from talent pool"""
        return await self.bulk_update_applications(
            application_ids=application_ids,
            status="pending",
            reviewed_by=reviewed_by,
            action_type="reactivate"
        )
    
    async def send_bulk_notifications(self, application_ids: List[str], notification_type: str, sent_by: str) -> Dict[str, Any]:
        """Send bulk notifications to talent pool applications"""
        try:
            success_count = 0
            failed_count = 0
            errors = []
            
            for app_id in application_ids:
                try:
                    # Get application details for notification
                    app = await self.get_application_by_id(app_id)
                    if not app:
                        failed_count += 1
                        errors.append(f"Application {app_id} not found")
                        continue
                    
                    # Create notification record
                    notification_data = {
                        "id": str(uuid.uuid4()),
                        "application_id": app_id,
                        "notification_type": notification_type,
                        "sent_by": sent_by,
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "recipient_email": app.applicant_data.get("email"),
                        "status": "sent"
                    }
                    
                    result = self.client.table("notifications").insert(notification_data).execute()
                    
                    if result.data:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Failed to create notification for application {app_id}")
                        
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Failed to send notification for application {app_id}: {str(e)}")
            
            return {
                "success_count": success_count,
                "failed_count": failed_count,
                "total_processed": len(application_ids),
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Bulk send notifications failed: {e}")
            return {
                "success_count": 0,
                "failed_count": len(application_ids),
                "total_processed": len(application_ids),
                "errors": [str(e)]
            }
    
    # ==========================================
    # APPLICATION HISTORY METHODS (Phase 1.2)
    # ==========================================
    
    async def get_application_history(self, application_id: str) -> List[Dict[str, Any]]:
        """Get application status history"""
        try:
            result = self.client.table("application_status_history").select("*").eq(
                "application_id", application_id
            ).order("changed_at", desc=True).execute()
            
            history = []
            for record in result.data:
                history.append({
                    "id": record["id"],
                    "application_id": record["application_id"],
                    "previous_status": record.get("previous_status"),
                    "new_status": record["new_status"],
                    "changed_by": record["changed_by"],
                    "changed_at": record["changed_at"],
                    "reason": record.get("reason"),
                    "notes": record.get("notes")
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get application history for {application_id}: {e}")
            return []
    
    async def add_application_status_history(self, application_id: str, previous_status: str, new_status: str, changed_by: str, reason: str = None, notes: str = None) -> bool:
        """Add application status history record"""
        try:
            history_data = {
                "id": str(uuid.uuid4()),
                "application_id": application_id,
                "previous_status": previous_status,
                "new_status": new_status,
                "changed_by": changed_by,
                "changed_at": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
                "notes": notes
            }
            
            result = self.client.table("application_status_history").insert(history_data).execute()
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to add application status history: {e}")
            return False
    
    async def check_duplicate_application(self, email: str, property_id: str, position: str) -> bool:
        """Check for duplicate applications"""
        try:
            result = self.client.table("job_applications").select("id").eq(
                "applicant_email", email.lower()
            ).eq("property_id", property_id).eq("position", position).in_(
                "status", ["pending", "approved", "hired"]
            ).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to check duplicate application: {e}")
            return False
    
    # ==========================================
    # MANAGER MANAGEMENT METHODS (Phase 1.3)
    # ==========================================
    
    async def get_manager_by_id(self, manager_id: str) -> Optional[User]:
        """Get manager details by ID"""
        try:
            result = self.client.table("users").select("*").eq("id", manager_id).eq("role", "manager").execute()
            
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=UserRole(user_data["role"]),
                    is_active=user_data["is_active"],
                    created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')) if user_data.get("created_at") else None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get manager {manager_id}: {e}")
            return None
    
    async def update_manager(self, manager_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update manager details"""
        try:
            # Ensure we only update allowed fields
            allowed_fields = ["first_name", "last_name", "email", "is_active"]
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}
            filtered_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table("users").update(filtered_data).eq("id", manager_id).eq("role", "manager").execute()
            
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=UserRole(user_data["role"]),
                    is_active=user_data["is_active"],
                    created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')) if user_data.get("created_at") else None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to update manager {manager_id}: {e}")
            return None
    
    async def delete_manager(self, manager_id: str) -> bool:
        """Delete manager (soft delete by setting inactive)"""
        try:
            result = self.client.table("users").update({
                "is_active": False,
                "deleted_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", manager_id).eq("role", "manager").execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to delete manager {manager_id}: {e}")
            return False
    
    async def reset_manager_password(self, manager_id: str, new_password: str) -> bool:
        """Reset manager password"""
        try:
            # Hash the password
            from .auth import PasswordManager
            password_manager = PasswordManager()
            hashed_password = password_manager.hash_password(new_password)
            
            result = self.client.table("users").update({
                "password_hash": hashed_password,
                "password_reset_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", manager_id).eq("role", "manager").execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to reset manager password {manager_id}: {e}")
            return False
    
    async def get_manager_performance(self, manager_id: str) -> Dict[str, Any]:
        """Get manager performance metrics"""
        try:
            # Get manager properties
            properties = await self.get_manager_properties(manager_id)
            property_ids = [prop.id for prop in properties]
            
            if not property_ids:
                return {
                    "manager_id": manager_id,
                    "properties_count": 0,
                    "applications_count": 0,
                    "approvals_count": 0,
                    "approval_rate": 0,  # Add missing approval_rate field
                    "average_response_time_days": 0,
                    "properties": []
                }
            
            # Get applications for manager's properties
            applications = await self.get_applications_by_properties(property_ids)
            
            # Get approvals by this manager
            approvals_result = self.client.table("job_applications").select("*").eq(
                "reviewed_by", manager_id
            ).in_("property_id", property_ids).execute()
            
            approvals_count = len(approvals_result.data)
            
            # Calculate average response time
            total_response_time = 0
            response_count = 0
            
            for app_data in approvals_result.data:
                if app_data.get("reviewed_at") and app_data.get("applied_at"):
                    applied_at = datetime.fromisoformat(app_data["applied_at"].replace('Z', '+00:00'))
                    reviewed_at = datetime.fromisoformat(app_data["reviewed_at"].replace('Z', '+00:00'))
                    response_time = (reviewed_at - applied_at).days
                    total_response_time += response_time
                    response_count += 1
            
            avg_response_time = total_response_time / response_count if response_count > 0 else 0
            
            # Calculate approval rate
            approval_rate = (approvals_count / len(applications)) * 100 if len(applications) > 0 else 0
            
            return {
                "manager_id": manager_id,
                "properties_count": len(properties),
                "applications_count": len(applications),
                "approvals_count": approvals_count,
                "approval_rate": round(approval_rate, 2),  # Add missing approval_rate field
                "average_response_time_days": round(avg_response_time, 2),
                "properties": [{"id": prop.id, "name": prop.name} for prop in properties]
            }
            
        except Exception as e:
            logger.error(f"Failed to get manager performance {manager_id}: {e}")
            return {
                "manager_id": manager_id,
                "properties_count": 0,
                "applications_count": 0,
                "approvals_count": 0,
                "approval_rate": 0,  # Add missing approval_rate field
                "average_response_time_days": 0,
                "properties": []
            }
    
    async def get_unassigned_managers(self) -> List[User]:
        """Get managers not assigned to any property"""
        try:
            # Get all manager IDs that are assigned to properties
            assigned_result = self.client.table("property_managers").select("manager_id").execute()
            assigned_manager_ids = [item["manager_id"] for item in assigned_result.data]
            
            # Get all managers
            managers_result = self.client.table("users").select("*").eq("role", "manager").eq("is_active", True).execute()
            
            unassigned_managers = []
            for user_data in managers_result.data:
                if user_data["id"] not in assigned_manager_ids:
                    unassigned_managers.append(User(
                        id=user_data["id"],
                        email=user_data["email"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        role=UserRole(user_data["role"]),
                        is_active=user_data["is_active"],
                        created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')) if user_data.get("created_at") else None
                    ))
            
            return unassigned_managers
            
        except Exception as e:
            logger.error(f"Failed to get unassigned managers: {e}")
            return []
    
    # ==========================================
    # ONBOARDING FORM DATA METHODS
    # ==========================================
    
    def save_onboarding_form_data(self, token: str, employee_id: str, step_id: str, form_data: Dict[str, Any]) -> bool:
        """Save or update onboarding form data for a specific step"""
        try:
            # Check if data already exists for this token and step
            existing = self.client.table("onboarding_form_data").select("id").eq("token", token).eq("step_id", step_id).execute()
            
            if existing.data:
                # Update existing record
                result = self.client.table("onboarding_form_data").update({
                    "form_data": form_data,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("token", token).eq("step_id", step_id).execute()
            else:
                # Insert new record
                result = self.client.table("onboarding_form_data").insert({
                    "token": token,
                    "employee_id": employee_id,
                    "step_id": step_id,
                    "form_data": form_data
                }).execute()
            
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to save onboarding form data: {e}")
            logger.error(f"Token: {token}, Employee: {employee_id}, Step: {step_id}")
            logger.error(f"Error details: {str(e)}")
            return False
    
    def get_onboarding_form_data(self, token: str, step_id: str = None) -> Dict[str, Any]:
        """Get onboarding form data for a token and optional step"""
        try:
            query = self.client.table("onboarding_form_data").select("*").eq("token", token)
            
            if step_id:
                query = query.eq("step_id", step_id)
            
            result = query.execute()
            
            if step_id and result.data:
                # Return single step data
                return result.data[0].get("form_data", {}) if result.data else {}
            else:
                # Return all steps data as a dictionary
                form_data = {}
                for record in result.data:
                    form_data[record["step_id"]] = record["form_data"]
                return form_data
                
        except Exception as e:
            logger.error(f"Failed to get onboarding form data: {e}")
            logger.error(f"Token: {token}, Step: {step_id}")
            logger.error(f"Error details: {str(e)}")
            return {}
    
    def get_all_onboarding_data_by_token(self, token: str) -> List[Dict[str, Any]]:
        """Get all onboarding form data records for a token"""
        try:
            result = self.client.table("onboarding_form_data").select("*").eq("token", token).order("created_at").execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get all onboarding data: {e}")
            return []
    
    def get_onboarding_form_data_by_employee(self, employee_id: str, step_id: str = None) -> Dict[str, Any]:
        """Get onboarding form data for an employee and optional step"""
        try:
            query = self.client.table("onboarding_form_data").select("*").eq("employee_id", employee_id)
            
            if step_id:
                query = query.eq("step_id", step_id)
            
            result = query.execute()
            
            if result.data:
                if step_id:
                    # Return single step data
                    return result.data[0].get("form_data", {}) if result.data else {}
                else:
                    # Return all steps as dict
                    return {item["step_id"]: item["form_data"] for item in result.data}
            
            return {}
        except Exception as e:
            logger.error(f"Failed to get onboarding form data by employee: {e}")
            return {}
    
    # ==========================================
    # DOCUMENT STORAGE METHODS (Supabase Storage)
    # ==========================================
    
    async def create_storage_bucket(self, bucket_name: str, public: bool = False) -> bool:
        """Create a storage bucket in Supabase"""
        try:
            # Check if bucket already exists
            existing_buckets = self.client.storage.list_buckets()
            if any(bucket['name'] == bucket_name for bucket in existing_buckets):
                logger.info(f"Bucket {bucket_name} already exists")
                return True
            
            # Create new bucket
            response = self.client.storage.create_bucket(
                bucket_name,
                {'public': public}
            )
            logger.info(f"Created storage bucket: {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create storage bucket {bucket_name}: {e}")
            return False
    
    async def upload_document_to_storage(self, bucket_name: str, file_path: str, file_data: bytes, 
                                        content_type: str = 'application/octet-stream') -> Dict[str, Any]:
        """Upload document to Supabase storage"""
        try:
            # Ensure bucket exists
            await self.create_storage_bucket(bucket_name)
            
            # Upload file
            response = self.client.storage.from_(bucket_name).upload(
                file_path,
                file_data,
                file_options={
                    "content-type": content_type,
                    "upsert": True  # Overwrite if exists
                }
            )
            
            # Get public URL
            public_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
            
            # Store metadata in database
            metadata = {
                "id": str(uuid.uuid4()),
                "bucket": bucket_name,
                "path": file_path,
                "size": len(file_data),
                "content_type": content_type,
                "public_url": public_url,
                "uploaded_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store metadata in documents table
            self.client.table("documents").insert(metadata).execute()
            
            logger.info(f"Document uploaded to storage: {bucket_name}/{file_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            raise
    
    async def upload_employee_document(self, employee_id: str, document_type: str, 
                                      file_data: bytes, file_name: str, 
                                      content_type: str = 'application/pdf') -> Dict[str, Any]:
        """Upload employee document to Supabase storage"""
        try:
            # Create file path: employee_id/document_type/timestamp_filename
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            file_path = f"{employee_id}/{document_type}/{timestamp}_{file_name}"
            
            # Upload to onboarding-documents bucket
            result = await self.upload_document_to_storage(
                bucket_name="onboarding-documents",
                file_path=file_path,
                file_data=file_data,
                content_type=content_type
            )
            
            # Add employee reference
            result["employee_id"] = employee_id
            result["document_type"] = document_type
            result["original_filename"] = file_name
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload employee document: {e}")
            raise
    
    async def upload_generated_pdf(self, employee_id: str, form_type: str, 
                                  pdf_data: bytes, signed: bool = False) -> Dict[str, Any]:
        """Upload generated PDF to Supabase storage"""
        try:
            # Create file path: employee_id/form_type/timestamp_form.pdf
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            status = "signed" if signed else "draft"
            file_name = f"{form_type}_{status}_{timestamp}.pdf"
            file_path = f"{employee_id}/{form_type}/{file_name}"
            
            # Upload to generated-pdfs bucket
            result = await self.upload_document_to_storage(
                bucket_name="generated-pdfs",
                file_path=file_path,
                file_data=pdf_data,
                content_type="application/pdf"
            )
            
            # Add metadata
            result["employee_id"] = employee_id
            result["form_type"] = form_type
            result["is_signed"] = signed
            result["generated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Store PDF metadata in database
            pdf_metadata = {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "form_type": form_type,
                "storage_path": file_path,
                "storage_url": result["public_url"],
                "is_signed": signed,
                "generated_at": result["generated_at"]
            }
            
            self.client.table("generated_pdfs").insert(pdf_metadata).execute()
            
            logger.info(f"Generated PDF uploaded: {form_type} for employee {employee_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload generated PDF: {e}")
            raise
    
    async def get_document_from_storage(self, bucket_name: str, file_path: str) -> bytes:
        """Download document from Supabase storage"""
        try:
            response = self.client.storage.from_(bucket_name).download(file_path)
            logger.info(f"Document downloaded from storage: {bucket_name}/{file_path}")
            return response
        except Exception as e:
            logger.error(f"Failed to download document: {e}")
            raise
    
    async def delete_document_from_storage(self, bucket_name: str, file_path: str) -> bool:
        """Delete document from Supabase storage"""
        try:
            response = self.client.storage.from_(bucket_name).remove([file_path])
            
            # Also delete metadata from database
            self.client.table("documents").delete().eq("path", file_path).execute()
            
            logger.info(f"Document deleted from storage: {bucket_name}/{file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def list_employee_documents(self, employee_id: str) -> List[Dict[str, Any]]:
        """List all documents for an employee from storage"""
        try:
            # Get from documents table
            result = self.client.table("documents").select("*").eq(
                "path", f"{employee_id}/%"
            ).execute()
            
            documents = []
            for doc in result.data:
                documents.append({
                    "id": doc["id"],
                    "path": doc["path"],
                    "size": doc["size"],
                    "content_type": doc["content_type"],
                    "public_url": doc["public_url"],
                    "uploaded_at": doc["uploaded_at"]
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list employee documents: {e}")
            return []
    
    async def get_employee_generated_pdfs(self, employee_id: str) -> List[Dict[str, Any]]:
        """Get all generated PDFs for an employee"""
        try:
            result = self.client.table("generated_pdfs").select("*").eq(
                "employee_id", employee_id
            ).order("generated_at", desc=True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to get employee generated PDFs: {e}")
            return []
    
    async def initialize_storage_buckets(self) -> bool:
        """Initialize required storage buckets"""
        try:
            # Create onboarding-documents bucket for uploaded documents
            await self.create_storage_bucket("onboarding-documents", public=False)
            
            # Create generated-pdfs bucket for system-generated PDFs
            await self.create_storage_bucket("generated-pdfs", public=False)
            
            # Create employee-photos bucket for profile photos
            await self.create_storage_bucket("employee-photos", public=True)
            
            logger.info("Storage buckets initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize storage buckets: {e}")
            return False
    
    # ==========================================
    # EMPLOYEE SEARCH & MANAGEMENT METHODS (Phase 1.4)
    # ==========================================
    
    async def search_employees(self, search_query: str, property_id: str = None, department: str = None, position: str = None, employment_status: str = None) -> List[Employee]:
        """Search employees with filters"""
        try:
            query = self.client.table("employees").select("*")
            
            # Apply search query if provided
            if search_query:
                # Search in personal info for name or email
                # Note: This is a simplified search - you might want to use full-text search
                query = query.or_(f"personal_info->>first_name.ilike.%{search_query}%,personal_info->>last_name.ilike.%{search_query}%,personal_info->>email.ilike.%{search_query}%")
            
            # Apply filters
            if property_id:
                query = query.eq("property_id", property_id)
            if department:
                query = query.eq("department", department)
            if position:
                query = query.eq("position", position)
            if employment_status:
                query = query.eq("employment_status", employment_status)
            
            result = query.order("created_at", desc=True).execute()
            
            employees = []
            for emp_data in result.data:
                employees.append(Employee(
                    id=emp_data["id"],
                    application_id=emp_data["application_id"],
                    property_id=emp_data["property_id"],
                    manager_id=emp_data["manager_id"],
                    department=emp_data["department"],
                    position=emp_data["position"],
                    hire_date=datetime.fromisoformat(emp_data["hire_date"]).date() if emp_data.get("hire_date") else None,
                    pay_rate=emp_data["pay_rate"],
                    pay_frequency=emp_data["pay_frequency"],
                    employment_type=emp_data["employment_type"],
                    personal_info=emp_data["personal_info"],
                    onboarding_status=OnboardingStatus(emp_data["onboarding_status"]),
                    created_at=datetime.fromisoformat(emp_data["created_at"].replace('Z', '+00:00'))
                ))
            
            return employees
            
        except Exception as e:
            logger.error(f"Failed to search employees: {e}")
            return []
    
    async def update_employee_status(self, employee_id: str, status: str, updated_by: str) -> bool:
        """Update employee employment status"""
        try:
            result = self.client.table("employees").update({
                "employment_status": status,
                "updated_by": updated_by,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", employee_id).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to update employee status {employee_id}: {e}")
            return False
    
    async def get_employee_statistics(self, property_id: str = None) -> Dict[str, Any]:
        """Get employee statistics"""
        try:
            query = self.client.table("employees").select("*")
            
            if property_id:
                query = query.eq("property_id", property_id)
            
            result = query.execute()
            
            employees = result.data
            total_count = len(employees)
            
            # Count by status
            status_counts = {}
            for emp in employees:
                status = emp.get("employment_status", "active")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by department
            department_counts = {}
            for emp in employees:
                dept = emp.get("department", "Unknown")
                department_counts[dept] = department_counts.get(dept, 0) + 1
            
            # Count by onboarding status
            onboarding_counts = {}
            for emp in employees:
                onb_status = emp.get("onboarding_status", "not_started")
                onboarding_counts[onb_status] = onboarding_counts.get(onb_status, 0) + 1
            
            return {
                "total_employees": total_count,
                "by_status": status_counts,
                "by_department": department_counts,
                "by_onboarding_status": onboarding_counts,
                "property_id": property_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get employee statistics: {e}")
            return {
                "total_employees": 0,
                "by_status": {},
                "by_department": {},
                "by_onboarding_status": {},
                "property_id": property_id
            }
    
    def get_onboarding_form_data_by_session(self, session_id: str) -> Dict[str, Any]:
        """Get all form data for an onboarding session"""
        try:
            # In a real implementation, this would fetch from a form_data table
            # For now, return a mock structure
            return {
                "personal_info": {},
                "i9_section1": {},
                "w4_form": {},
                "emergency_contacts": {},
                "direct_deposit": {},
                "health_insurance": {},
                "company_policies": {},
                "background_check": {}
            }
        except Exception as e:
            logger.error(f"Failed to get onboarding form data: {e}")
            return {}
    
    async def get_onboarding_documents(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all documents uploaded for an onboarding session"""
        try:
            # In a real implementation, this would fetch from a documents table
            # For now, return an empty list
            return []
        except Exception as e:
            logger.error(f"Failed to get onboarding documents: {e}")
            return []
    
    def get_onboarding_form_data_by_step(self, session_id: str, step: str) -> Optional[Dict[str, Any]]:
        """Get form data for a specific onboarding step"""
        try:
            # In a real implementation, this would fetch from a form_data table
            # filtered by step
            return None
        except Exception as e:
            logger.error(f"Failed to get form data by step: {e}")
            return None
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """Get all users with a specific role"""
        try:
            response = self.client.table('users').select('*').eq('role', role).execute()
            
            if response.data:
                return [User(**user_data) for user_data in response.data]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get users by role: {e}")
            return []
    
    async def store_onboarding_form_data(self, session_id: str, step: str, form_data: Dict[str, Any]) -> bool:
        """Store form data for an onboarding step"""
        try:
            # In a real implementation, this would store in a form_data table
            logger.info(f"Storing form data for session {session_id}, step {step}")
            return True
        except Exception as e:
            logger.error(f"Failed to store form data: {e}")
            return False
    
    async def store_onboarding_signature(self, session_id: str, step: str, signature_data: Dict[str, Any]) -> bool:
        """Store signature data for an onboarding step"""
        try:
            # In a real implementation, this would store in a signatures table
            logger.info(f"Storing signature for session {session_id}, step {step}")
            return True
        except Exception as e:
            logger.error(f"Failed to store signature: {e}")
            return False
    
    async def create_audit_entry(self, action: str, entity_type: str, entity_id: str, user_id: Optional[str] = None, details: Optional[Dict] = None) -> bool:
        """Create an audit trail entry"""
        try:
            audit_data = {
                "id": str(uuid.uuid4()),
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "user_id": user_id,
                "details": details or {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # In a real implementation, this would store in an audit_trail table
            logger.info(f"Creating audit entry: {action} on {entity_type} {entity_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create audit entry: {e}")
            return False
    
    # ==========================================
    # SCHEDULER SUPPORT METHODS
    # ==========================================
    
    async def get_expiring_onboarding_sessions(self, hours: int = 48) -> List[Dict[str, Any]]:
        """Get onboarding sessions expiring within specified hours"""
        try:
            expiry_cutoff = datetime.now(timezone.utc) + timedelta(hours=hours)
            
            # Get sessions that are not completed and expiring soon
            result = self.client.table("onboarding_sessions").select("*").lt(
                "expires_at", expiry_cutoff.isoformat()
            ).in_(
                "status", ["initiated", "in_progress", "employee_completed"]
            ).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to get expiring sessions: {e}")
            return []
    
    async def update_last_reminder_sent(self, session_id: str) -> bool:
        """Update the last reminder sent timestamp for a session"""
        try:
            result = self.client.table("onboarding_sessions").update({
                "last_reminder_sent": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", session_id).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to update last reminder sent: {e}")
            return False
    
    async def get_hr_users(self) -> List[Dict[str, Any]]:
        """Get all active HR users"""
        try:
            result = self.client.table("users").select("*").eq(
                "role", "hr"
            ).eq("is_active", True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to get HR users: {e}")
            return []
    
    async def get_onboarding_stats(self) -> Dict[str, int]:
        """Get onboarding statistics for HR summary"""
        try:
            stats = {
                "pending_manager_review": 0,
                "pending_hr_review": 0,
                "expiring_in_24h": 0,
                "completed_today": 0,
                "total_active": 0
            }
            
            # Get sessions pending manager review
            manager_result = self.client.table("onboarding_sessions").select("id").eq(
                "status", "employee_completed"
            ).execute()
            stats["pending_manager_review"] = len(manager_result.data) if manager_result.data else 0
            
            # Get sessions pending HR review
            hr_result = self.client.table("onboarding_sessions").select("id").eq(
                "status", "manager_approved"
            ).execute()
            stats["pending_hr_review"] = len(hr_result.data) if hr_result.data else 0
            
            # Get sessions expiring in 24 hours
            expiry_cutoff = datetime.now(timezone.utc) + timedelta(hours=24)
            expiring_result = self.client.table("onboarding_sessions").select("id").lt(
                "expires_at", expiry_cutoff.isoformat()
            ).in_(
                "status", ["initiated", "in_progress"]
            ).execute()
            stats["expiring_in_24h"] = len(expiring_result.data) if expiring_result.data else 0
            
            # Get total active sessions
            active_result = self.client.table("onboarding_sessions").select("id").in_(
                "status", ["initiated", "in_progress", "employee_completed", "manager_approved"]
            ).execute()
            stats["total_active"] = len(active_result.data) if active_result.data else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get onboarding stats: {e}")
            return {
                "pending_manager_review": 0,
                "pending_hr_review": 0,
                "expiring_in_24h": 0,
                "completed_today": 0,
                "total_active": 0
            }
    
    async def get_onboarding_step_data(self, employee_id: str, step_id: str) -> Dict[str, Any]:
        """
        Retrieve saved onboarding step data for a specific employee and step
        """
        try:
            # Try onboarding_form_data table first (this is where data is actually saved)
            form_result = self.client.table("onboarding_form_data").select("*").eq(
                "employee_id", employee_id
            ).eq("step_id", step_id).order("created_at", desc=True).limit(1).execute()
            
            if form_result.data and len(form_result.data) > 0:
                logger.info(f"Found saved data in onboarding_form_data for {employee_id}/{step_id}")
                return form_result.data[0]
            
            # Try onboarding_progress table as fallback (if it exists)
            try:
                progress_result = self.client.table("onboarding_progress").select("*").eq(
                    "employee_id", employee_id
                ).eq("step_id", step_id).execute()
                
                if progress_result.data and len(progress_result.data) > 0:
                    logger.info(f"Found saved data in onboarding_progress for {employee_id}/{step_id}")
                    return progress_result.data[0]
            except Exception as progress_error:
                # Table might not exist, that's okay
                logger.debug(f"onboarding_progress table not accessible: {progress_error}")
            
            logger.info(f"No saved data found for {employee_id}/{step_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get onboarding step data for employee {employee_id}, step {step_id}: {e}")
            return None


# Global instance
enhanced_supabase_service = None

def get_enhanced_supabase_service() -> EnhancedSupabaseService:
    """Get or create Enhanced Supabase service instance"""
    global enhanced_supabase_service
    if enhanced_supabase_service is None:
        enhanced_supabase_service = EnhancedSupabaseService()
    return enhanced_supabase_service

# Async context manager for database operations
@asynccontextmanager
async def get_db_service():
    """Async context manager for database service"""
    service = get_enhanced_supabase_service()
    try:
        await service.initialize_db_pool()
        yield service
    finally:
        await service.close_db_pool()
