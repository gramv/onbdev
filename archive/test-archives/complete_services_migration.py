#!/usr/bin/env python3

import os
import shutil
import time
from pathlib import Path

def complete_services_migration():
    """Complete migration of all services to use Supabase"""
    
    print("🔧 COMPLETE SERVICES MIGRATION TO SUPABASE")
    print("=" * 60)
    
    # 1. Update OnboardingOrchestrator to use Supabase
    print("\n1️⃣ Migrating OnboardingOrchestrator...")
    
    orchestrator_content = '''"""
Onboarding Orchestrator Service - Supabase Version
Manages the complete onboarding workflow and state transitions
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import logging
from ..models_enhanced import (
    OnboardingSession, OnboardingStatus, OnboardingStep, OnboardingPhase,
    Employee, FormType, SignatureType, AuditEntry, ComplianceCheck,
    generate_secure_token, calculate_expiry_time
)

logger = logging.getLogger(__name__)

class OnboardingOrchestrator:
    """
    Core service for managing onboarding workflow and state transitions
    Handles the three-phase workflow: Employee → Manager → HR
    """
    
    def __init__(self, supabase_service):
        self.supabase_service = supabase_service
        self.default_expiry_hours = 72
        self.total_onboarding_steps = 18
        
        # Define step sequences for each phase
        self.employee_steps = [
            OnboardingStep.WELCOME,
            OnboardingStep.PERSONAL_INFO,
            OnboardingStep.I9_SECTION1,
            OnboardingStep.W4_FORM,
            OnboardingStep.EMERGENCY_CONTACTS,
            OnboardingStep.DIRECT_DEPOSIT,
            OnboardingStep.HEALTH_INSURANCE,
            OnboardingStep.COMPANY_POLICIES,
            OnboardingStep.TRAFFICKING_AWARENESS,
            OnboardingStep.WEAPONS_POLICY,
            OnboardingStep.BACKGROUND_CHECK,
            OnboardingStep.EMPLOYEE_SIGNATURE
        ]
        
        self.manager_steps = [
            OnboardingStep.MANAGER_REVIEW,
            OnboardingStep.I9_SECTION2,
            OnboardingStep.MANAGER_SIGNATURE
        ]
        
        self.hr_steps = [
            OnboardingStep.HR_REVIEW,
            OnboardingStep.COMPLIANCE_CHECK,
            OnboardingStep.HR_APPROVAL
        ]
    
    async def initiate_onboarding(
        self,
        application_id: str,
        employee_id: str,
        property_id: str,
        manager_id: str,
        expires_hours: int = None
    ) -> OnboardingSession:
        """
        Initiate a new onboarding session
        """
        try:
            expires_hours = expires_hours or self.default_expiry_hours
            
            # Create onboarding session
            session = OnboardingSession(
                id=str(uuid.uuid4()),
                application_id=application_id,
                employee_id=employee_id,
                property_id=property_id,
                manager_id=manager_id,
                token=generate_secure_token(),
                status=OnboardingStatus.IN_PROGRESS,
                phase=OnboardingPhase.EMPLOYEE,
                current_step=OnboardingStep.WELCOME,
                expires_at=calculate_expiry_time(expires_hours),
                created_at=datetime.utcnow()
            )
            
            # Store session in Supabase
            await self.supabase_service.create_onboarding_session(session)
            
            # Update employee record
            employee = await self.supabase_service.get_employee_by_id(employee_id)
            if employee:
                await self.supabase_service.update_employee_onboarding_status(
                    employee_id, OnboardingStatus.IN_PROGRESS, session.id
                )
            
            logger.info(f"Onboarding session initiated: {session.id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to initiate onboarding: {e}")
            raise
    
    async def get_session_by_token(self, token: str) -> Optional[OnboardingSession]:
        """
        Get onboarding session by token
        """
        try:
            session = await self.supabase_service.get_onboarding_session_by_token(token)
            
            if session and session.is_expired():
                await self._expire_session(session.id)
                return None
                
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session by token: {e}")
            return None
    
    async def get_session_by_id(self, session_id: str) -> Optional[OnboardingSession]:
        """
        Get onboarding session by ID
        """
        try:
            session = await self.supabase_service.get_onboarding_session_by_id(session_id)
            
            if not session:
                return None
                
            if session.is_expired():
                await self._expire_session(session_id)
                return None
                
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session by ID: {e}")
            return None
    
    async def update_step_progress(
        self,
        session_id: str,
        step: OnboardingStep,
        form_data: Dict[str, Any] = None,
        signature_data: Dict[str, Any] = None
    ) -> bool:
        """
        Update progress for a specific onboarding step
        """
        try:
            session = await self.supabase_service.get_onboarding_session_by_id(session_id)
            
            if not session:
                logger.error(f"Session {session_id} not found")
                return False
                
            if session.is_expired():
                await self._expire_session(session_id)
                return False
            
            # Update session progress
            session.current_step = step
            session.updated_at = datetime.utcnow()
            
            # Store form data if provided
            if form_data:
                await self.supabase_service.store_onboarding_form_data(
                    session_id, step, form_data
                )
            
            # Store signature data if provided
            if signature_data:
                await self.supabase_service.store_onboarding_signature(
                    session_id, step, signature_data
                )
            
            # Update session in Supabase
            await self.supabase_service.update_onboarding_session(session)
            
            # Check if phase is complete
            await self._check_phase_completion(session)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update step progress: {e}")
            return False
    
    async def complete_employee_phase(self, session_id: str) -> bool:
        """
        Complete employee phase and transition to manager review
        """
        try:
            session = await self.supabase_service.get_onboarding_session_by_id(session_id)
            
            if not session:
                return False
                
            # Update session to manager review phase
            session.phase = OnboardingPhase.MANAGER
            session.status = OnboardingStatus.MANAGER_REVIEW
            session.current_step = OnboardingStep.MANAGER_REVIEW
            session.updated_at = datetime.utcnow()
            
            await self.supabase_service.update_onboarding_session(session)
            
            # Update employee status
            await self.supabase_service.update_employee_onboarding_status(
                session.employee_id, OnboardingStatus.MANAGER_REVIEW
            )
            
            logger.info(f"Employee phase completed for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete employee phase: {e}")
            return False
    
    async def complete_manager_phase(self, session_id: str) -> bool:
        """
        Complete manager phase and transition to HR approval
        """
        try:
            session = await self.supabase_service.get_onboarding_session_by_id(session_id)
            
            if not session:
                return False
                
            # Update session to HR approval phase
            session.phase = OnboardingPhase.HR
            session.status = OnboardingStatus.HR_APPROVAL
            session.current_step = OnboardingStep.HR_REVIEW
            session.updated_at = datetime.utcnow()
            
            await self.supabase_service.update_onboarding_session(session)
            
            # Update employee status
            await self.supabase_service.update_employee_onboarding_status(
                session.employee_id, OnboardingStatus.HR_APPROVAL
            )
            
            logger.info(f"Manager phase completed for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete manager phase: {e}")
            return False
    
    async def approve_onboarding(self, session_id: str, approved_by: str) -> bool:
        """
        Approve onboarding and complete the process
        """
        try:
            session = await self.supabase_service.get_onboarding_session_by_id(session_id)
            
            if not session:
                return False
                
            # Update session to approved
            session.status = OnboardingStatus.APPROVED
            session.approved_by = approved_by
            session.approved_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            
            await self.supabase_service.update_onboarding_session(session)
            
            # Update employee status
            await self.supabase_service.update_employee_onboarding_status(
                session.employee_id, OnboardingStatus.APPROVED
            )
            
            logger.info(f"Onboarding approved for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve onboarding: {e}")
            return False
    
    async def reject_onboarding(
        self,
        session_id: str,
        rejected_by: str,
        rejection_reason: str
    ) -> bool:
        """
        Reject onboarding with reason
        """
        try:
            session = await self.supabase_service.get_onboarding_session_by_id(session_id)
            
            if not session:
                return False
                
            # Update session to rejected
            session.status = OnboardingStatus.REJECTED
            session.rejected_by = rejected_by
            session.rejection_reason = rejection_reason
            session.rejected_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            
            await self.supabase_service.update_onboarding_session(session)
            
            # Update employee status
            await self.supabase_service.update_employee_onboarding_status(
                session.employee_id, OnboardingStatus.REJECTED
            )
            
            logger.info(f"Onboarding rejected for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reject onboarding: {e}")
            return False
    
    async def get_pending_manager_reviews(self, manager_id: str) -> List[OnboardingSession]:
        """
        Get onboarding sessions pending manager review
        """
        try:
            return await self.supabase_service.get_onboarding_sessions_by_manager_and_status(
                manager_id, OnboardingStatus.MANAGER_REVIEW
            )
        except Exception as e:
            logger.error(f"Failed to get pending manager reviews: {e}")
            return []
    
    async def get_pending_hr_approvals(self) -> List[OnboardingSession]:
        """
        Get onboarding sessions pending HR approval
        """
        try:
            return await self.supabase_service.get_onboarding_sessions_by_status(
                OnboardingStatus.HR_APPROVAL
            )
        except Exception as e:
            logger.error(f"Failed to get pending HR approvals: {e}")
            return []
    
    async def _check_phase_completion(self, session: OnboardingSession) -> None:
        """
        Check if current phase is complete and auto-transition if needed
        """
        try:
            if session.phase == OnboardingPhase.EMPLOYEE:
                if session.current_step == OnboardingStep.EMPLOYEE_SIGNATURE:
                    await self.complete_employee_phase(session.id)
            elif session.phase == OnboardingPhase.MANAGER:
                if session.current_step == OnboardingStep.MANAGER_SIGNATURE:
                    await self.complete_manager_phase(session.id)
        except Exception as e:
            logger.error(f"Failed to check phase completion: {e}")
    
    async def _expire_session(self, session_id: str) -> None:
        """
        Mark session as expired
        """
        try:
            session = await self.supabase_service.get_onboarding_session_by_id(session_id)
            
            if session:
                session.status = OnboardingStatus.EXPIRED
                session.updated_at = datetime.utcnow()
                
                await self.supabase_service.update_onboarding_session(session)
                
                # Update employee status
                await self.supabase_service.update_employee_onboarding_status(
                    session.employee_id, OnboardingStatus.EXPIRED
                )
                
        except Exception as e:
            logger.error(f"Failed to expire session: {e}")
    
    async def create_audit_entry(
        self,
        session_id: str,
        action: str,
        user_id: str,
        details: Dict[str, Any] = None
    ) -> None:
        """
        Create audit trail entry
        """
        try:
            audit_entry = AuditEntry(
                id=str(uuid.uuid4()),
                session_id=session_id,
                action=action,
                user_id=user_id,
                details=details or {},
                timestamp=datetime.utcnow()
            )
            
            await self.supabase_service.create_audit_entry(audit_entry)
            
        except Exception as e:
            logger.error(f"Failed to create audit entry: {e}")
'''
    
    # Write the updated orchestrator
    with open("hotel-onboarding-backend/app/services/onboarding_orchestrator.py", "w") as f:
        f.write(orchestrator_content)
    
    print("✅ OnboardingOrchestrator migrated to Supabase")
    
    # 2. Update FormUpdateService to use Supabase
    print("\n2️⃣ Migrating FormUpdateService...")
    
    form_service_content = '''"""
Form Update Service - Supabase Version
Handles individual form updates without full re-onboarding
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import logging
from ..models_enhanced import (
    FormUpdateSession, FormType, Employee, generate_secure_token,
    calculate_expiry_time, AuditEntry
)

logger = logging.getLogger(__name__)

class FormUpdateService:
    """
    Service for handling individual form updates
    Allows HR to send specific forms to employees for updates
    """
    
    def __init__(self, supabase_service):
        self.supabase_service = supabase_service
        self.default_expiry_hours = 48
    
    async def create_form_update_session(
        self,
        employee_id: str,
        form_type: FormType,
        requested_by: str,
        expires_hours: int = None
    ) -> FormUpdateSession:
        """
        Create a new form update session
        """
        try:
            expires_hours = expires_hours or self.default_expiry_hours
            
            # Get current employee data
            employee = await self.supabase_service.get_employee_by_id(employee_id)
            if not employee:
                raise ValueError(f"Employee {employee_id} not found")
            
            # Create form update session
            session = FormUpdateSession(
                id=str(uuid.uuid4()),
                employee_id=employee_id,
                form_type=form_type,
                update_token=generate_secure_token(),
                requested_by=requested_by,
                current_data=self._extract_current_form_data(employee, form_type),
                expires_at=calculate_expiry_time(expires_hours),
                created_at=datetime.utcnow()
            )
            
            # Store session in Supabase
            await self.supabase_service.create_form_update_session(session)
            
            logger.info(f"Form update session created: {session.id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create form update session: {e}")
            raise
    
    async def get_session_by_token(self, token: str) -> Optional[FormUpdateSession]:
        """
        Get form update session by token
        """
        try:
            session = await self.supabase_service.get_form_update_session_by_token(token)
            
            if session and session.is_expired():
                await self._expire_session(session.id)
                return None
                
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session by token: {e}")
            return None
    
    async def submit_form_update(
        self,
        session_id: str,
        updated_data: Dict[str, Any],
        signature_data: Dict[str, Any] = None
    ) -> bool:
        """
        Submit form update with new data
        """
        try:
            session = await self.supabase_service.get_form_update_session_by_id(session_id)
            
            if not session:
                logger.error(f"Session {session_id} not found")
                return False
                
            if session.is_expired():
                await self._expire_session(session_id)
                return False
            
            # Update session with new data
            session.updated_data = updated_data
            session.signature_data = signature_data
            session.completed_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            
            await self.supabase_service.update_form_update_session(session)
            
            # Apply updates to employee record
            await self._apply_form_updates(session)
            
            logger.info(f"Form update submitted for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit form update: {e}")
            return False
    
    async def get_pending_updates_for_employee(self, employee_id: str) -> List[FormUpdateSession]:
        """
        Get pending form update sessions for employee
        """
        try:
            return await self.supabase_service.get_form_update_sessions_by_employee(
                employee_id, completed=False
            )
        except Exception as e:
            logger.error(f"Failed to get pending updates: {e}")
            return []
    
    async def get_completed_updates_for_employee(self, employee_id: str) -> List[FormUpdateSession]:
        """
        Get completed form update sessions for employee
        """
        try:
            return await self.supabase_service.get_form_update_sessions_by_employee(
                employee_id, completed=True
            )
        except Exception as e:
            logger.error(f"Failed to get completed updates: {e}")
            return []
    
    def _extract_current_form_data(self, employee: Employee, form_type: FormType) -> Dict[str, Any]:
        """
        Extract current form data from employee record
        """
        try:
            if form_type == FormType.PERSONAL_INFO:
                return employee.personal_info or {}
            elif form_type == FormType.W4:
                return employee.w4_data or {}
            elif form_type == FormType.EMERGENCY_CONTACTS:
                return employee.emergency_contacts or {}
            elif form_type == FormType.DIRECT_DEPOSIT:
                return employee.direct_deposit or {}
            elif form_type == FormType.HEALTH_INSURANCE:
                return employee.health_insurance or {}
            else:
                return {}
        except Exception as e:
            logger.error(f"Failed to extract form data: {e}")
            return {}
    
    async def _apply_form_updates(self, session: FormUpdateSession) -> None:
        """
        Apply form updates to employee record
        """
        try:
            employee = await self.supabase_service.get_employee_by_id(session.employee_id)
            if not employee:
                return
            
            # Apply updates based on form type
            if session.form_type == FormType.PERSONAL_INFO:
                employee.personal_info.update(session.updated_data)
            elif session.form_type == FormType.W4:
                employee.w4_data.update(session.updated_data)
            elif session.form_type == FormType.EMERGENCY_CONTACTS:
                employee.emergency_contacts.update(session.updated_data)
            elif session.form_type == FormType.DIRECT_DEPOSIT:
                employee.direct_deposit.update(session.updated_data)
            elif session.form_type == FormType.HEALTH_INSURANCE:
                employee.health_insurance.update(session.updated_data)
            
            # Update employee record
            employee.updated_at = datetime.utcnow()
            await self.supabase_service.update_employee(employee)
            
            # Create audit entry
            await self._create_audit_entry(session)
            
        except Exception as e:
            logger.error(f"Failed to apply form updates: {e}")
    
    async def _expire_session(self, session_id: str) -> None:
        """
        Mark session as expired
        """
        try:
            session = await self.supabase_service.get_form_update_session_by_id(session_id)
            
            if session:
                session.expired = True
                session.updated_at = datetime.utcnow()
                
                await self.supabase_service.update_form_update_session(session)
                
        except Exception as e:
            logger.error(f"Failed to expire session: {e}")
    
    async def _create_audit_entry(self, session: FormUpdateSession) -> None:
        """
        Create audit trail entry for form update
        """
        try:
            audit_entry = AuditEntry(
                id=str(uuid.uuid4()),
                session_id=session.id,
                action=f"form_update_{session.form_type.value}",
                user_id=session.employee_id,
                details={
                    "form_type": session.form_type.value,
                    "requested_by": session.requested_by,
                    "changes": session.updated_data
                },
                timestamp=datetime.utcnow()
            )
            
            await self.supabase_service.create_audit_entry(audit_entry)
            
        except Exception as e:
            logger.error(f"Failed to create audit entry: {e}")
'''
    
    # Write the updated form service
    with open("hotel-onboarding-backend/app/services/form_update_service.py", "w") as f:
        f.write(form_service_content)
    
    print("✅ FormUpdateService migrated to Supabase")
    
    # 3. Remove old main.py (backup first)
    print("\n3️⃣ Backing up and removing old main.py...")
    
    if os.path.exists("hotel-onboarding-backend/app/main.py"):
        # Create backup
        backup_name = f"hotel-onboarding-backend/app/main_inmemory_backup_{int(time.time())}.py"
        shutil.copy("hotel-onboarding-backend/app/main.py", backup_name)
        print(f"✅ Backed up main.py to {backup_name}")
        
        # Remove old file
        os.remove("hotel-onboarding-backend/app/main.py")
        print("✅ Removed old main.py")
    
    # 4. Update main_enhanced.py to use the migrated services
    print("\n4️⃣ Updating main_enhanced.py to use migrated services...")
    
    # Read current main_enhanced.py
    with open("hotel-onboarding-backend/app/main_enhanced.py", "r") as f:
        main_content = f.read()
    
    # Fix the services initialization
    main_content = main_content.replace(
        '''# Initialize enhanced services (temporarily disabled until services are migrated)
onboarding_orchestrator = None
form_update_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global onboarding_orchestrator, form_update_service
    
    await supabase_service.initialize()
    # TODO: Migrate services to use Supabase instead of in-memory database
    # onboarding_orchestrator = OnboardingOrchestrator(supabase_service)
    # form_update_service = FormUpdateService(supabase_service)''',
        '''# Initialize enhanced services
onboarding_orchestrator = None
form_update_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global onboarding_orchestrator, form_update_service
    
    await supabase_service.initialize()
    onboarding_orchestrator = OnboardingOrchestrator(supabase_service)
    form_update_service = FormUpdateService(supabase_service)'''
    )
    
    # Fix the onboarding session creation
    main_content = main_content.replace(
        '''        # Create simple onboarding session (without orchestrator for now)
        from .models_enhanced import generate_secure_token, calculate_expiry_time
        
        onboarding_token = generate_secure_token()
        expires_at = calculate_expiry_time(72)
        
        # Simple onboarding session object
        class SimpleOnboardingSession:
            def __init__(self, token, expires_at):
                self.token = token
                self.expires_at = expires_at
        
        onboarding_session = SimpleOnboardingSession(onboarding_token, expires_at)''',
        '''        # Create onboarding session
        onboarding_session = await onboarding_orchestrator.initiate_onboarding(
            application_id=application_id,
            employee_id=employee.id,
            property_id=application.property_id,
            manager_id=current_user.id,
            expires_hours=72
        )'''
    )
    
    # Write updated main_enhanced.py
    with open("hotel-onboarding-backend/app/main_enhanced.py", "w") as f:
        f.write(main_content)
    
    print("✅ Updated main_enhanced.py to use migrated services")
    
    print("\n🎉 SERVICES MIGRATION COMPLETE!")
    print("=" * 60)
    print("✅ OnboardingOrchestrator migrated to Supabase")
    print("✅ FormUpdateService migrated to Supabase") 
    print("✅ Old main.py backed up and removed")
    print("✅ main_enhanced.py updated to use migrated services")
    print("")
    print("🔄 Next steps:")
    print("1. Restart the backend server")
    print("2. Run the verification script")
    print("3. Test the approval functionality")

if __name__ == "__main__":
    complete_services_migration()