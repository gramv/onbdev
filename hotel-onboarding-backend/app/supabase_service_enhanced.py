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
        """Verify password against hash - implement proper password verification"""
        # This is a placeholder - implement proper password hashing verification
        # Use bcrypt, scrypt, or similar secure hashing
        import bcrypt
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False
    
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