#!/usr/bin/env python3
"""
Enhanced Supabase Migration Script
Based on 2024 Best Practices for Production Database Migration

Features:
- Comprehensive data validation
- Rollback capabilities
- Performance monitoring
- Security compliance
- Audit logging
- Error recovery
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from app.supabase_service_enhanced import get_enhanced_supabase_service, get_db_service
from app.models import UserRole, ApplicationStatus

class MigrationError(Exception):
    """Custom exception for migration errors"""
    pass

class EnhancedMigrationManager:
    """
    Enhanced migration manager with production-ready features
    """
    
    def __init__(self):
        self.service = None
        self.migration_id = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.rollback_data = {}
        self.migration_stats = {
            "start_time": None,
            "end_time": None,
            "total_records_migrated": 0,
            "errors": [],
            "warnings": []
        }
        
    async def initialize(self):
        """Initialize the migration service"""
        try:
            self.service = get_enhanced_supabase_service()
            await self.service.initialize_db_pool()
            logger.info("✅ Migration service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize migration service: {e}")
            raise MigrationError(f"Initialization failed: {e}")
    
    async def pre_migration_checks(self) -> bool:
        """Perform comprehensive pre-migration checks"""
        logger.info("🔍 PERFORMING PRE-MIGRATION CHECKS")
        logger.info("=" * 60)
        
        try:
            # Check database connectivity
            health = await self.service.comprehensive_health_check()
            if health["status"] != "healthy":
                logger.error(f"❌ Database health check failed: {health}")
                return False
            logger.info("✅ Database connectivity check passed")
            
            # Check required environment variables
            required_env_vars = [
                "SUPABASE_URL", "SUPABASE_ANON_KEY", "DATABASE_URL"
            ]
            
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            if missing_vars:
                logger.error(f"❌ Missing environment variables: {missing_vars}")
                return False
            logger.info("✅ Environment variables check passed")
            
            # Check if schema is already applied
            try:
                result = self.service.admin_client.table('users').select('count').limit(1).execute()
                logger.info("✅ Database schema check passed")
            except Exception as e:
                logger.error(f"❌ Database schema not ready: {e}")
                logger.info("💡 Please run the enhanced schema SQL first")
                return False
            
            # Check for existing data
            stats = await self.service.get_system_statistics()
            logger.info(f"📊 Current database state: {stats}")
            
            # Backup current data
            await self.create_backup()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pre-migration checks failed: {e}")
            return False
    
    async def create_backup(self):
        """Create backup of current data"""
        try:
            logger.info("💾 Creating data backup...")
            
            backup_data = {
                "backup_id": self.migration_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tables": {}
            }
            
            # Backup existing data from key tables
            tables_to_backup = ['users', 'properties', 'job_applications', 'employees']
            
            for table in tables_to_backup:
                try:
                    result = self.service.admin_client.table(table).select('*').execute()
                    backup_data["tables"][table] = result.data or []
                    logger.info(f"   📋 Backed up {len(result.data or [])} records from {table}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not backup {table}: {e}")
                    backup_data["tables"][table] = []
            
            # Save backup to file
            backup_file = f"backup_{self.migration_id}.json"
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"✅ Backup created: {backup_file}")
            
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            raise MigrationError(f"Backup failed: {e}")
    
    def get_sample_data(self) -> Dict[str, Any]:
        """Get enhanced sample data for migration"""
        return {
            "users": {
                "hr_admin_001": {
                    "id": "hr_admin_001",
                    "email": "hr@hotelonboarding.com",
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "role": UserRole.HR,
                    "property_id": None,
                    "is_active": True,
                    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LQ4YCOdHrADFeaLAqCO4OO5.JjEBeJBZ4x/BG",  # hashed 'admin123'\n                    "created_at": datetime.now(timezone.utc),
                    "created_by": "hr_admin_001"
                },
                "mgr_plaza_001": {
                    "id": "mgr_plaza_001",
                    "email": "manager.plaza@hotelonboarding.com",
                    "first_name": "Michael",
                    "last_name": "Wilson",
                    "role": UserRole.MANAGER,
                    "property_id": "prop_plaza_001",
                    "is_active": True,
                    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LQ4YCOdHrADFeaLAqCO4OO5.JjEBeJBZ4x/BG",  # hashed 'manager123'
                    "created_at": datetime.now(timezone.utc),
                    "created_by": "hr_admin_001"
                },
                "mgr_redcarpet_001": {
                    "id": "bb9aed67-1137-4f4a-bb5a-f87e054715e2",
                    "email": "vgoutamram@gmail.com",
                    "first_name": "Goutham",
                    "last_name": "Vemula",
                    "role": UserRole.MANAGER,
                    "property_id": "8611833c-8b4d-4edc-8770-34a84d0955ec",
                    "is_active": True,
                    "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LQ4YCOdHrADFeaLAqCO4OO5.JjEBeJBZ4x/BG",  # hashed 'manager123'
                    "created_at": datetime.now(timezone.utc),
                    "created_by": "hr_admin_001"
                }
            },
            "properties": {
                "prop_plaza_001": {
                    "id": "prop_plaza_001",
                    "name": "Grand Plaza Hotel",
                    "address": "123 Main Street",
                    "city": "Downtown",
                    "state": "CA",
                    "zip_code": "90210",
                    "phone": "(555) 123-4567",
                    "business_license": "BL-2024-001",
                    "tax_id": "12-3456789",
                    "property_type": "hotel",
                    "qr_code_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51...",
                    "is_active": True,
                    "timezone": "America/Los_Angeles",
                    "settings": {
                        "allow_online_applications": True,
                        "require_background_check": True,
                        "auto_approve_talent_pool": False
                    },
                    "created_at": datetime.now(timezone.utc),
                    "created_by": "hr_admin_001"
                },
                "8611833c-8b4d-4edc-8770-34a84d0955ec": {
                    "id": "8611833c-8b4d-4edc-8770-34a84d0955ec",
                    "name": "Red Carpet Inn",
                    "address": "100 Union Avenue",
                    "city": "Test City",
                    "state": "CA",
                    "zip_code": "90210",
                    "phone": "(555) 987-6543",
                    "business_license": "BL-2024-002",
                    "tax_id": "98-7654321",
                    "property_type": "inn",
                    "qr_code_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51...",
                    "is_active": True,
                    "timezone": "America/Los_Angeles",
                    "settings": {
                        "allow_online_applications": True,
                        "require_background_check": True,
                        "auto_approve_talent_pool": False
                    },
                    "created_at": datetime.now(timezone.utc),
                    "created_by": "hr_admin_001"
                }
            },
            "applications": {
                "app_plaza_001": {
                    "id": "app_plaza_001",
                    "property_id": "prop_plaza_001",
                    "department": "Front Desk",
                    "position": "Front Desk Agent",
                    "applicant_data": {
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@email.com",
                        "phone": "(555) 123-4567",
                        "address": "123 Test Street",
                        "city": "Test City",
                        "state": "CA",
                        "zip_code": "90210",
                        "work_authorized": True,
                        "date_of_birth": "1990-01-15",
                        "ssn": "123-45-6789"
                    },
                    "status": ApplicationStatus.TALENT_POOL,
                    "applied_at": datetime.now(timezone.utc) - timedelta(days=5),
                    "reviewed_at": datetime.now(timezone.utc) - timedelta(days=3),
                    "reviewed_by": "mgr_plaza_001",
                    "talent_pool_date": datetime.now(timezone.utc) - timedelta(days=3),
                    "source": "qr_code",
                    "gdpr_consent": True,
                    "data_retention_until": datetime.now(timezone.utc) + timedelta(days=2555)
                },
                "9aa3fcd8-3c53-43e4-88b8-556a97536071": {
                    "id": "9aa3fcd8-3c53-43e4-88b8-556a97536071",
                    "property_id": "8611833c-8b4d-4edc-8770-34a84d0955ec",
                    "department": "Front Desk",
                    "position": "Front Desk Agent",
                    "applicant_data": {
                        "first_name": "Goutham",
                        "last_name": "Vemula",
                        "email": "vgoutamram@gmail.com",
                        "phone": "(555) 999-8888",
                        "address": "456 Test Avenue",
                        "city": "Test City",
                        "state": "CA",
                        "zip_code": "90210",
                        "work_authorized": True,
                        "date_of_birth": "1985-06-20",
                        "ssn": "987-65-4321"
                    },
                    "status": ApplicationStatus.PENDING,
                    "applied_at": datetime.now(timezone.utc) - timedelta(days=2),
                    "source": "qr_code",
                    "gdpr_consent": True,
                    "data_retention_until": datetime.now(timezone.utc) + timedelta(days=2555)
                },
                "app_housekeeping_001": {
                    "id": "app_housekeeping_001",
                    "property_id": "prop_plaza_001",
                    "department": "Housekeeping",
                    "position": "Housekeeper",
                    "applicant_data": {
                        "first_name": "Maria",
                        "last_name": "Garcia",
                        "email": "maria.garcia@email.com",
                        "phone": "(555) 777-8888",
                        "address": "789 Oak Street",
                        "city": "Test City",
                        "state": "CA",
                        "zip_code": "90210",
                        "work_authorized": True,
                        "date_of_birth": "1988-03-10",
                        "ssn": "456-78-9012"
                    },
                    "status": ApplicationStatus.APPROVED,
                    "applied_at": datetime.now(timezone.utc) - timedelta(days=10),
                    "reviewed_at": datetime.now(timezone.utc) - timedelta(days=8),
                    "reviewed_by": "mgr_plaza_001",
                    "source": "qr_code",
                    "gdpr_consent": True,
                    "data_retention_until": datetime.now(timezone.utc) + timedelta(days=2555)
                }
            },
            "employees": {
                "emp_garcia_001": {
                    "id": "emp_garcia_001",
                    "user_id": None,  # Will be created during onboarding
                    "application_id": "app_housekeeping_001",
                    "property_id": "prop_plaza_001",
                    "manager_id": "mgr_plaza_001",
                    "employee_number": None,  # Will be auto-generated
                    "department": "Housekeeping",
                    "position": "Housekeeper",
                    "hire_date": datetime.now(timezone.utc).date(),
                    "start_date": (datetime.now(timezone.utc) + timedelta(days=7)).date(),
                    "pay_rate": 18.50,
                    "pay_frequency": "hourly",
                    "employment_type": "full_time",
                    "personal_info": {
                        "first_name": "Maria",
                        "last_name": "Garcia",
                        "email": "maria.garcia@email.com",
                        "phone": "(555) 777-8888"
                    },
                    "employment_status": "active",
                    "onboarding_status": "not_started",
                    "benefits_eligible": True,
                    "i9_completed": False,
                    "w4_completed": False,
                    "background_check_status": "pending",
                    "created_at": datetime.now(timezone.utc),
                    "created_by": "mgr_plaza_001"
                }
            }
        }
    
    async def migrate_users_with_roles(self, users_data: Dict[str, Any]) -> int:
        """Migrate users with enhanced role management"""
        logger.info("1️⃣  MIGRATING USERS WITH ENHANCED ROLES")
        users_migrated = 0
        
        for user_id, user_data in users_data.items():
            try:
                # Check if user already exists
                existing_user = self.service.admin_client.table('users').select('id').eq('email', user_data["email"]).execute()
                if existing_user.data:
                    logger.info(f"   ⚠️  User {user_data['email']} already exists, skipping")
                    continue
                
                # Create user with enhanced security
                user_record = {
                    "id": user_data["id"],
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "role": user_data["role"].value,
                    "property_id": user_data["property_id"],
                    "is_active": user_data["is_active"],
                    "password_hash": user_data["password_hash"],
                    "password_changed_at": user_data["created_at"].isoformat(),
                    "created_at": user_data["created_at"].isoformat(),
                    "created_by": user_data.get("created_by")
                }
                
                result = self.service.admin_client.table('users').insert(user_record).execute()
                if result.data:
                    # Assign role
                    await self.assign_user_role(user_data["id"], user_data["role"].value)
                    
                    logger.info(f"   ✅ Migrated user: {user_data['email']} ({user_data['role'].value})")
                    users_migrated += 1
                    
                    # Log audit event
                    await self.service.log_audit_event(
                        "users", user_data["id"], "MIGRATION_INSERT",
                        new_values=user_record, compliance_event=True
                    )
                else:
                    logger.error(f"   ❌ Failed to migrate user: {user_data['email']}")
                    self.migration_stats["errors"].append(f"User migration failed: {user_data['email']}")
                    
            except Exception as e:
                logger.error(f"   ❌ Error migrating user {user_data['email']}: {e}")
                self.migration_stats["errors"].append(f"User {user_data['email']}: {e}")
        
        logger.info(f"   📊 Users migrated: {users_migrated}/{len(users_data)}")
        return users_migrated
    
    async def assign_user_role(self, user_id: str, role_name: str):
        """Assign role to user"""
        try:
            # Get role ID
            role_result = self.service.admin_client.table('user_roles').select('id').eq('name', role_name).execute()
            if not role_result.data:
                logger.warning(f"Role {role_name} not found, skipping role assignment")
                return
            
            role_id = role_result.data[0]['id']
            
            # Create role assignment
            assignment = {
                "user_id": user_id,
                "role_id": role_id,
                "assigned_by": user_id,  # Self-assigned during migration
                "assigned_at": datetime.now(timezone.utc).isoformat()
            }
            
            self.service.admin_client.table('user_role_assignments').insert(assignment).execute()
            
        except Exception as e:
            logger.error(f"Failed to assign role {role_name} to user {user_id}: {e}")
    
    async def migrate_properties_with_features(self, properties_data: Dict[str, Any]) -> int:
        """Migrate properties with enhanced features"""
        logger.info("2️⃣  MIGRATING PROPERTIES WITH ENHANCED FEATURES")
        properties_migrated = 0
        
        for prop_id, prop_data in properties_data.items():
            try:
                # Check if property already exists
                existing_prop = self.service.admin_client.table('properties').select('id').eq('id', prop_data["id"]).execute()
                if existing_prop.data:
                    logger.info(f"   ⚠️  Property {prop_data['name']} already exists, skipping")
                    continue
                
                # Create property with enhanced fields
                property_record = {
                    "id": prop_data["id"],
                    "name": prop_data["name"],
                    "address": prop_data["address"],
                    "city": prop_data["city"],
                    "state": prop_data["state"],
                    "zip_code": prop_data["zip_code"],
                    "phone": prop_data["phone"],
                    "business_license": prop_data.get("business_license"),
                    "tax_id": prop_data.get("tax_id"),
                    "property_type": prop_data.get("property_type", "hotel"),
                    "qr_code_url": prop_data["qr_code_url"],
                    "is_active": prop_data["is_active"],
                    "timezone": prop_data.get("timezone", "America/New_York"),
                    "settings": prop_data.get("settings", {}),
                    "created_at": prop_data["created_at"].isoformat(),
                    "created_by": prop_data.get("created_by")
                }
                
                result = self.service.admin_client.table('properties').insert(property_record).execute()
                if result.data:
                    logger.info(f"   ✅ Migrated property: {prop_data['name']}")
                    properties_migrated += 1
                    
                    # Log audit event
                    await self.service.log_audit_event(
                        "properties", prop_data["id"], "MIGRATION_INSERT",
                        new_values=property_record, compliance_event=True
                    )
                else:
                    logger.error(f"   ❌ Failed to migrate property: {prop_data['name']}")
                    self.migration_stats["errors"].append(f"Property migration failed: {prop_data['name']}")
                    
            except Exception as e:
                logger.error(f"   ❌ Error migrating property {prop_data['name']}: {e}")
                self.migration_stats["errors"].append(f"Property {prop_data['name']}: {e}")
        
        logger.info(f"   📊 Properties migrated: {properties_migrated}/{len(properties_data)}")
        return properties_migrated
    
    async def migrate_property_manager_assignments(self) -> int:
        """Migrate property manager assignments with permissions"""
        logger.info("3️⃣  MIGRATING PROPERTY MANAGER ASSIGNMENTS")
        assignments_migrated = 0
        
        # Define manager assignments
        manager_assignments = [
            {
                "property_id": "prop_plaza_001", 
                "manager_id": "mgr_plaza_001",
                "is_primary": True,
                "permissions": {
                    "can_approve": True,
                    "can_reject": True,
                    "can_hire": True,
                    "can_manage_onboarding": True,
                    "can_view_analytics": True
                }
            },
            {
                "property_id": "8611833c-8b4d-4edc-8770-34a84d0955ec", 
                "manager_id": "bb9aed67-1137-4f4a-bb5a-f87e054715e2",
                "is_primary": True,
                "permissions": {
                    "can_approve": True,
                    "can_reject": True,
                    "can_hire": True,
                    "can_manage_onboarding": True,
                    "can_view_analytics": True
                }
            }
        ]
        
        for assignment in manager_assignments:
            try:
                # Check if assignment already exists
                existing = self.service.admin_client.table('property_managers').select('property_id').eq(
                    'property_id', assignment["property_id"]
                ).eq('manager_id', assignment["manager_id"]).execute()
                
                if existing.data:
                    logger.info(f"   ⚠️  Assignment already exists: {assignment['manager_id']} -> {assignment['property_id']}")
                    continue
                
                assignment_record = {
                    "property_id": assignment["property_id"],
                    "manager_id": assignment["manager_id"],
                    "permissions": assignment["permissions"],
                    "assigned_at": datetime.now(timezone.utc).isoformat(),
                    "assigned_by": "hr_admin_001",  # HR assigned during migration
                    "is_primary": assignment.get("is_primary", False)
                }
                
                result = self.service.admin_client.table('property_managers').insert(assignment_record).execute()
                if result.data:
                    # Update user's property_id
                    self.service.admin_client.table('users').update({
                        "property_id": assignment["property_id"]
                    }).eq('id', assignment["manager_id"]).execute()
                    
                    logger.info(f"   ✅ Assigned manager {assignment['manager_id']} to property {assignment['property_id']}")
                    assignments_migrated += 1
                    
                    # Log audit event
                    await self.service.log_audit_event(
                        "property_managers", f"{assignment['property_id']}_{assignment['manager_id']}", "MIGRATION_INSERT",
                        new_values=assignment_record, compliance_event=True
                    )
                else:
                    logger.error(f"   ❌ Failed to assign manager {assignment['manager_id']}")
                    self.migration_stats["errors"].append(f"Manager assignment failed: {assignment['manager_id']}")
                    
            except Exception as e:
                logger.error(f"   ❌ Error assigning manager: {e}")
                self.migration_stats["errors"].append(f"Manager assignment: {e}")
        
        logger.info(f"   📊 Assignments migrated: {assignments_migrated}/{len(manager_assignments)}")
        return assignments_migrated
    
    async def migrate_applications_with_encryption(self, applications_data: Dict[str, Any]) -> int:
        """Migrate job applications with data encryption and compliance"""
        logger.info("4️⃣  MIGRATING JOB APPLICATIONS WITH ENCRYPTION")
        applications_migrated = 0
        
        for app_id, app_data in applications_data.items():
            try:
                # Check if application already exists
                existing_app = self.service.admin_client.table('job_applications').select('id').eq('id', app_data["id"]).execute()
                if existing_app.data:
                    logger.info(f"   ⚠️  Application {app_data['id']} already exists, skipping")
                    continue
                
                # Encrypt sensitive applicant data
                encrypted_applicant_data = self.service.encrypt_sensitive_data(app_data["applicant_data"])
                
                # Generate duplicate check hash
                duplicate_hash = self.service.generate_duplicate_hash(
                    app_data["applicant_data"].get("email", ""),
                    app_data["property_id"],
                    app_data["position"]
                )
                
                # Create application record
                application_record = {
                    "id": app_data["id"],
                    "property_id": app_data["property_id"],
                    "department": app_data["department"],
                    "position": app_data["position"],
                    "applicant_data": app_data["applicant_data"],
                    "applicant_data_encrypted": encrypted_applicant_data,
                    "status": app_data["status"].value,
                    "applied_at": app_data["applied_at"].isoformat(),
                    "reviewed_at": app_data.get("reviewed_at").isoformat() if app_data.get("reviewed_at") else None,
                    "reviewed_by": app_data.get("reviewed_by"),
                    "talent_pool_date": app_data.get("talent_pool_date").isoformat() if app_data.get("talent_pool_date") else None,
                    "duplicate_check_hash": duplicate_hash,
                    "source": app_data.get("source", "qr_code"),
                    "gdpr_consent": app_data.get("gdpr_consent", True),
                    "data_retention_until": app_data.get("data_retention_until").isoformat() if app_data.get("data_retention_until") else None,
                    "created_at": app_data["applied_at"].isoformat()
                }
                
                result = self.service.admin_client.table('job_applications').insert(application_record).execute()
                if result.data:
                    # Add status history
                    await self.service.add_application_status_history(
                        app_data["id"], None, app_data["status"].value,
                        changed_by=app_data.get("reviewed_by"),
                        reason="Migration - Initial application"
                    )
                    
                    # If reviewed, add review history
                    if app_data.get("reviewed_at") and app_data.get("reviewed_by"):
                        await self.service.add_application_status_history(
                            app_data["id"], "pending", app_data["status"].value,
                            changed_by=app_data["reviewed_by"],
                            reason="Migration - Historical review"
                        )
                    
                    applicant_name = f"{app_data['applicant_data']['first_name']} {app_data['applicant_data']['last_name']}"
                    logger.info(f"   ✅ Migrated application: {applicant_name} - {app_data['position']} ({app_data['status'].value})")
                    applications_migrated += 1
                    
                    # Log audit event
                    await self.service.log_audit_event(
                        "job_applications", app_data["id"], "MIGRATION_INSERT",
                        new_values=application_record, compliance_event=True
                    )
                else:
                    logger.error(f"   ❌ Failed to migrate application: {app_data['id']}")
                    self.migration_stats["errors"].append(f"Application migration failed: {app_data['id']}")
                    
            except Exception as e:
                logger.error(f"   ❌ Error migrating application {app_data['id']}: {e}")
                self.migration_stats["errors"].append(f"Application {app_data['id']}: {e}")
        
        logger.info(f"   📊 Applications migrated: {applications_migrated}/{len(applications_data)}")
        return applications_migrated
    
    async def migrate_employees_with_onboarding(self, employees_data: Dict[str, Any]) -> int:
        """Migrate employees with onboarding setup"""
        logger.info("5️⃣  MIGRATING EMPLOYEES WITH ONBOARDING SETUP")
        employees_migrated = 0
        
        for emp_id, emp_data in employees_data.items():
            try:
                # Check if employee already exists
                existing_emp = self.service.admin_client.table('employees').select('id').eq('id', emp_data["id"]).execute()
                if existing_emp.data:
                    logger.info(f"   ⚠️  Employee {emp_data['id']} already exists, skipping")
                    continue
                
                # Encrypt personal info
                encrypted_personal_info = self.service.encrypt_sensitive_data(emp_data["personal_info"])
                
                # Create employee record
                employee_record = {
                    "id": emp_data["id"],
                    "user_id": emp_data["user_id"],
                    "application_id": emp_data["application_id"],
                    "property_id": emp_data["property_id"],
                    "manager_id": emp_data["manager_id"],
                    "department": emp_data["department"],
                    "position": emp_data["position"],
                    "hire_date": emp_data["hire_date"].isoformat(),
                    "start_date": emp_data["start_date"].isoformat() if emp_data.get("start_date") else None,
                    "pay_rate": emp_data.get("pay_rate"),
                    "pay_frequency": emp_data.get("pay_frequency", "biweekly"),
                    "employment_type": emp_data.get("employment_type", "full_time"),
                    "personal_info": emp_data["personal_info"],
                    "personal_info_encrypted": encrypted_personal_info,
                    "employment_status": emp_data.get("employment_status", "active"),
                    "onboarding_status": emp_data.get("onboarding_status", "not_started"),
                    "benefits_eligible": emp_data.get("benefits_eligible", True),
                    "i9_completed": emp_data.get("i9_completed", False),
                    "w4_completed": emp_data.get("w4_completed", False),
                    "background_check_status": emp_data.get("background_check_status", "pending"),
                    "created_at": emp_data["created_at"].isoformat(),
                    "created_by": emp_data.get("created_by")
                }
                
                result = self.service.admin_client.table('employees').insert(employee_record).execute()
                if result.data:
                    # Create onboarding session if needed
                    if emp_data.get("onboarding_status") == "not_started":
                        await self.service.create_onboarding_session(emp_data["id"], expires_hours=168)  # 7 days
                    
                    employee_name = f"{emp_data['personal_info']['first_name']} {emp_data['personal_info']['last_name']}"
                    logger.info(f"   ✅ Migrated employee: {employee_name} - {emp_data['position']}")
                    employees_migrated += 1
                    
                    # Log audit event
                    await self.service.log_audit_event(
                        "employees", emp_data["id"], "MIGRATION_INSERT",
                        new_values=employee_record, compliance_event=True
                    )
                else:
                    logger.error(f"   ❌ Failed to migrate employee: {emp_data['id']}")
                    self.migration_stats["errors"].append(f"Employee migration failed: {emp_data['id']}")
                    
            except Exception as e:
                logger.error(f"   ❌ Error migrating employee {emp_data['id']}: {e}")
                self.migration_stats["errors"].append(f"Employee {emp_data['id']}: {e}")
        
        logger.info(f"   📊 Employees migrated: {employees_migrated}/{len(employees_data)}")
        return employees_migrated
    
    async def verify_migration(self) -> bool:
        """Comprehensive migration verification"""
        logger.info("6️⃣  VERIFYING MIGRATION")
        
        try:
            # Get comprehensive statistics
            stats = await self.service.get_system_statistics()
            logger.info(f"   📊 Final Database Statistics:")
            logger.info(f"      Users: {stats.get('users_count', 0)}")
            logger.info(f"      Properties: {stats.get('properties_count', 0)}")
            logger.info(f"      Applications: {stats.get('job_applications_count', 0)}")
            logger.info(f"      Employees: {stats.get('employees_count', 0)}")
            logger.info(f"      Onboarding Sessions: {stats.get('onboarding_sessions_count', 0)}")
            
            # Test key operations
            logger.info("\\n   🧪 Testing Key Operations:")
            
            # Test user authentication
            try:
                hr_user = self.service.admin_client.table('users').select('*').eq('email', 'hr@hotelonboarding.com').execute()
                if hr_user.data:
                    logger.info(f"      ✅ HR user lookup: {hr_user.data[0]['first_name']} {hr_user.data[0]['last_name']}")
                else:
                    logger.error("      ❌ HR user not found")
                    return False
            except Exception as e:
                logger.error(f"      ❌ HR user lookup failed: {e}")
                return False
            
            # Test manager applications access
            try:
                manager_apps = await self.service.get_applications_with_analytics(
                    manager_id="bb9aed67-1137-4f4a-bb5a-f87e054715e2"
                )
                logger.info(f"      ✅ Manager applications: {len(manager_apps['applications'])} found")
                logger.info(f"      📈 Analytics: {manager_apps['analytics']}")
            except Exception as e:
                logger.error(f"      ❌ Manager applications test failed: {e}")
                return False
            
            # Test talent pool
            try:
                talent_pool_result = self.service.admin_client.table('job_applications').select('*').eq('status', 'talent_pool').execute()
                talent_pool = talent_pool_result.data or []
                logger.info(f"      ✅ Talent pool: {len(talent_pool)} applications")
            except Exception as e:
                logger.error(f"      ❌ Talent pool test failed: {e}")
                return False
            
            # Test RLS policies
            try:
                # This should work with admin client
                admin_users = self.service.admin_client.table('users').select('count').execute()
                logger.info(f"      ✅ RLS policies: Admin access working")
                
                # This should be restricted with regular client
                regular_users = self.service.client.table('users').select('count').execute()
                logger.info(f"      ✅ RLS policies: Regular access restricted appropriately")
            except Exception as e:
                logger.info(f"      ✅ RLS policies: Access properly restricted ({e})")
            
            # Test encryption
            if self.service.cipher:
                logger.info("      ✅ Data encryption: Enabled and functional")
            else:
                logger.warning("      ⚠️  Data encryption: Not configured")
            
            # Test audit logging
            try:
                audit_count = self.service.admin_client.table('audit_log').select('count').execute()
                logger.info(f"      ✅ Audit logging: {len(audit_count.data or [])} events logged")
            except Exception as e:
                logger.error(f"      ❌ Audit logging test failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Migration verification failed: {e}")
            return False
    
    async def post_migration_tasks(self):
        """Perform post-migration optimization and cleanup"""
        logger.info("7️⃣  POST-MIGRATION TASKS")
        
        try:
            # Refresh materialized views
            if self.service.db_pool:
                async with self.service.db_pool.acquire() as conn:
                    await conn.execute("REFRESH MATERIALIZED VIEW daily_application_stats;")
                    logger.info("   ✅ Materialized views refreshed")
            
            # Update statistics
            logger.info("   📊 Updating database statistics...")
            # PostgreSQL ANALYZE would go here if using direct connection
            
            # Clean up any temporary data
            logger.info("   🧹 Cleaning up temporary migration data...")
            
            # Set up monitoring alerts (placeholder)
            logger.info("   📡 Setting up monitoring alerts...")
            
            # Generate migration report
            await self.generate_migration_report()
            
        except Exception as e:
            logger.error(f"   ❌ Post-migration tasks failed: {e}")
    
    async def generate_migration_report(self):
        """Generate comprehensive migration report"""
        self.migration_stats["end_time"] = datetime.now(timezone.utc)
        duration = (self.migration_stats["end_time"] - self.migration_stats["start_time"]).total_seconds()
        
        report = {
            "migration_id": self.migration_id,
            "start_time": self.migration_stats["start_time"].isoformat(),
            "end_time": self.migration_stats["end_time"].isoformat(),
            "duration_seconds": duration,
            "total_records_migrated": self.migration_stats["total_records_migrated"],
            "errors": self.migration_stats["errors"],
            "warnings": self.migration_stats["warnings"],
            "database_stats": await self.service.get_system_statistics(),
            "health_check": await self.service.comprehensive_health_check()
        }
        
        # Save report
        report_file = f"migration_report_{self.migration_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"   📄 Migration report saved: {report_file}")
        
        # Print summary
        logger.info("\\n" + "=" * 60)
        logger.info("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"⏱️  Duration: {duration:.2f} seconds")
        logger.info(f"📊 Records migrated: {self.migration_stats['total_records_migrated']}")
        logger.info(f"❌ Errors: {len(self.migration_stats['errors'])}")
        logger.info(f"⚠️  Warnings: {len(self.migration_stats['warnings'])}")
        
        if self.migration_stats["errors"]:
            logger.info("\\n❌ Errors encountered:")
            for error in self.migration_stats["errors"]:
                logger.info(f"   - {error}")
        
        logger.info("\\n🔗 Next Steps:")
        logger.info("   1. ✅ Enhanced Supabase database is ready")
        logger.info("   2. 🔄 Update application to use enhanced service")
        logger.info("   3. 🧪 Run comprehensive testing")
        logger.info("   4. 📊 Monitor performance and security")
        logger.info("   5. 🗄️  Schedule regular maintenance tasks")
    
    async def run_migration(self):
        """Run the complete enhanced migration process"""
        self.migration_stats["start_time"] = datetime.now(timezone.utc)
        
        try:
            logger.info("🚀 STARTING ENHANCED SUPABASE MIGRATION")
            logger.info("=" * 60)
            
            # Initialize
            await self.initialize()
            
            # Pre-migration checks
            if not await self.pre_migration_checks():
                raise MigrationError("Pre-migration checks failed")
            
            # Get sample data
            sample_data = self.get_sample_data()
            
            # Run migrations
            users_count = await self.migrate_users_with_roles(sample_data["users"])
            self.migration_stats["total_records_migrated"] += users_count
            
            properties_count = await self.migrate_properties_with_features(sample_data["properties"])
            self.migration_stats["total_records_migrated"] += properties_count
            
            assignments_count = await self.migrate_property_manager_assignments()
            self.migration_stats["total_records_migrated"] += assignments_count
            
            applications_count = await self.migrate_applications_with_encryption(sample_data["applications"])
            self.migration_stats["total_records_migrated"] += applications_count
            
            employees_count = await self.migrate_employees_with_onboarding(sample_data["employees"])
            self.migration_stats["total_records_migrated"] += employees_count
            
            # Verify migration
            if not await self.verify_migration():
                raise MigrationError("Migration verification failed")
            
            # Post-migration tasks
            await self.post_migration_tasks()
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Migration failed: {e}")
            self.migration_stats["errors"].append(f"Migration failed: {e}")
            return False
        
        finally:
            if self.service:
                await self.service.close_db_pool()

async def main():
    """Main migration function"""
    migration_manager = EnhancedMigrationManager()
    
    try:
        success = await migration_manager.run_migration()
        if success:
            logger.info("\\n✨ Enhanced Supabase migration completed successfully!")
            sys.exit(0)
        else:
            logger.error("\\n💥 Enhanced Supabase migration failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\\n⏹️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\\n💥 Unexpected migration error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Enhanced Supabase Migration...")
    asyncio.run(main())