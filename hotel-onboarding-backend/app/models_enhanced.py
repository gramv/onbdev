"""
Enhanced Data Models for Modular Employee Onboarding System
Comprehensive implementation with federal compliance and modular form updates
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, timedelta
from enum import Enum
import uuid
import re

# =====================================
# ENHANCED ENUMS FOR ONBOARDING SYSTEM
# =====================================

class UserRole(str, Enum):
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class OnboardingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    EMPLOYEE_COMPLETED = "employee_completed"
    MANAGER_REVIEW = "manager_review"
    HR_APPROVAL = "hr_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OnboardingPhase(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr"

class OnboardingStep(str, Enum):
    WELCOME = "welcome"
    PERSONAL_INFO = "personal_info"
    I9_SECTION1 = "i9_section1"
    W4_FORM = "w4_form"
    EMERGENCY_CONTACTS = "emergency_contacts"
    DIRECT_DEPOSIT = "direct_deposit"
    HEALTH_INSURANCE = "health_insurance"
    COMPANY_POLICIES = "company_policies"
    TRAFFICKING_AWARENESS = "trafficking_awareness"
    WEAPONS_POLICY = "weapons_policy"
    BACKGROUND_CHECK = "background_check"
    EMPLOYEE_SIGNATURE = "employee_signature"
    MANAGER_REVIEW = "manager_review"
    I9_SECTION2 = "i9_section2"
    MANAGER_SIGNATURE = "manager_signature"
    HR_REVIEW = "hr_review"
    COMPLIANCE_CHECK = "compliance_check"
    HR_APPROVAL = "hr_approval"
    COMPLETED = "completed"

class FormType(str, Enum):
    PERSONAL_INFO = "personal_info"
    W4_FORM = "w4_form"
    I9_SECTION1 = "i9_section1"
    I9_SECTION2 = "i9_section2"
    DIRECT_DEPOSIT = "direct_deposit"
    EMERGENCY_CONTACTS = "emergency_contacts"
    HEALTH_INSURANCE = "health_insurance"
    COMPANY_POLICIES = "company_policies"
    TRAFFICKING_AWARENESS = "trafficking_awareness"
    WEAPONS_POLICY = "weapons_policy"
    BACKGROUND_CHECK = "background_check"

class DocumentType(str, Enum):
    I9_FORM = "i9_form"
    W4_FORM = "w4_form"
    DIRECT_DEPOSIT_FORM = "direct_deposit_form"
    EMERGENCY_CONTACTS = "emergency_contacts"
    HEALTH_INSURANCE = "health_insurance"
    COMPANY_POLICIES = "company_policies"
    BACKGROUND_CHECK = "background_check"
    PHOTO_ID = "photo_id"
    WORK_AUTHORIZATION = "work_authorization"
    VOIDED_CHECK = "voided_check"

class SignatureType(str, Enum):
    EMPLOYEE_I9 = "employee_i9"
    EMPLOYEE_W4 = "employee_w4"
    EMPLOYEE_POLICIES = "employee_policies"
    EMPLOYEE_FINAL = "employee_final"
    MANAGER_I9 = "manager_i9"
    MANAGER_APPROVAL = "manager_approval"
    HR_APPROVAL = "hr_approval"

class FormUpdateStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_CORRECTION = "requires_correction"

# =====================================
# ENHANCED ONBOARDING SESSION MODEL
# =====================================

class OnboardingSession(BaseModel):
    """Enhanced onboarding session with comprehensive workflow tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    application_id: Optional[str] = None
    property_id: str
    manager_id: Optional[str] = None
    
    # Session management
    token: str
    status: OnboardingStatus = OnboardingStatus.NOT_STARTED
    current_step: OnboardingStep = OnboardingStep.WELCOME
    phase: OnboardingPhase = OnboardingPhase.EMPLOYEE
    language_preference: str = "en"  # en, es
    
    # Progress tracking
    steps_completed: List[OnboardingStep] = Field(default_factory=list)
    progress_percentage: float = 0.0
    total_steps: int = 18  # Total number of onboarding steps
    
    # Change requests
    requested_changes: Optional[List[Dict[str, str]]] = None
    
    # Form completion tracking
    completed_forms: Dict[FormType, Dict[str, Any]] = Field(default_factory=dict)
    required_signatures: Dict[SignatureType, Optional[str]] = Field(default_factory=dict)
    uploaded_documents: Dict[DocumentType, Dict[str, Any]] = Field(default_factory=dict)
    
    # Workflow timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    employee_completed_at: Optional[datetime] = None
    manager_review_started_at: Optional[datetime] = None
    hr_review_started_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    expires_at: datetime
    
    # Review and approval
    reviewed_by: Optional[str] = None  # Manager ID
    hr_reviewed_by: Optional[str] = None  # HR ID
    manager_comments: Optional[str] = None
    hr_comments: Optional[str] = None
    rejection_reason: Optional[str] = None
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    
    # Notifications and communication
    notifications_sent: List[Dict[str, Any]] = Field(default_factory=list)
    last_reminder_sent: Optional[datetime] = None
    
    # Compliance tracking
    federal_compliance_checks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Security and access
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_progress(self) -> float:
        """Calculate completion progress percentage"""
        if not self.steps_completed:
            return 0.0
        return (len(self.steps_completed) / self.total_steps) * 100.0
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def can_transition_to_manager(self) -> bool:
        """Check if session can transition to manager review"""
        required_employee_steps = [
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
        return all(step in self.steps_completed for step in required_employee_steps)
    
    def can_transition_to_hr(self) -> bool:
        """Check if session can transition to HR approval"""
        required_manager_steps = [
            OnboardingStep.MANAGER_REVIEW,
            OnboardingStep.I9_SECTION2,
            OnboardingStep.MANAGER_SIGNATURE
        ]
        return (self.can_transition_to_manager() and 
                all(step in self.steps_completed for step in required_manager_steps))

# =====================================
# FORM UPDATE SESSION MODEL
# =====================================

class FormUpdateSession(BaseModel):
    """Individual form update session for modular updates"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    form_type: FormType
    update_token: str
    
    # Request details
    requested_by: str  # HR user ID
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    completed_at: Optional[datetime] = None
    
    # Form data
    current_data: Dict[str, Any] = Field(default_factory=dict)
    updated_data: Optional[Dict[str, Any]] = None
    change_reason: str
    change_summary: Optional[str] = None
    
    # Status and workflow
    status: FormUpdateStatus = FormUpdateStatus.PENDING
    requires_manager_approval: bool = False
    requires_hr_approval: bool = True
    
    # Approval tracking
    manager_approved_at: Optional[datetime] = None
    manager_approved_by: Optional[str] = None
    hr_approved_at: Optional[datetime] = None
    hr_approved_by: Optional[str] = None
    
    # Notifications
    employee_notified_at: Optional[datetime] = None
    completion_notified_at: Optional[datetime] = None
    
    # Security and audit
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Compliance
    requires_signature: bool = True
    signature_captured: bool = False
    signature_data: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if update session has expired"""
        return datetime.utcnow() > self.expires_at
    
    def can_complete(self) -> bool:
        """Check if update can be completed"""
        if self.requires_signature and not self.signature_captured:
            return False
        if self.requires_manager_approval and not self.manager_approved_at:
            return False
        if self.requires_hr_approval and not self.hr_approved_at:
            return False
        return True

# =====================================
# COMPREHENSIVE EMPLOYEE MODEL
# =====================================

class Employee(BaseModel):
    """Enhanced employee model with comprehensive onboarding data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None  # Can be None for employees not yet linked to users
    employee_number: Optional[str] = None
    application_id: Optional[str] = None
    property_id: str
    manager_id: Optional[str] = None  # Manager can be assigned later
    
    # Employment information
    department: str
    position: str
    job_level: Optional[str] = None
    hire_date: date
    start_date: Optional[date] = None
    probation_end_date: Optional[date] = None
    
    # Compensation
    pay_rate: Optional[float] = None
    pay_frequency: str = "biweekly"
    employment_type: str = "full_time"
    
    # Personal information (encrypted in production)
    personal_info: Optional[Dict[str, Any]] = None  # Can be None initially
    emergency_contacts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Government forms data
    i9_data: Optional[Dict[str, Any]] = None
    w4_data: Optional[Dict[str, Any]] = None
    
    # Benefits and policies
    health_insurance: Optional[Dict[str, Any]] = None
    direct_deposit: Optional[Dict[str, Any]] = None
    policy_acknowledgments: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Training and compliance
    trafficking_awareness_completed: bool = False
    trafficking_awareness_completed_at: Optional[datetime] = None
    background_check_authorized: bool = False
    background_check_authorized_at: Optional[datetime] = None
    weapons_policy_acknowledged: bool = False
    weapons_policy_acknowledged_at: Optional[datetime] = None
    
    # Status tracking
    employment_status: str = "active"
    onboarding_status: OnboardingStatus = OnboardingStatus.NOT_STARTED
    onboarding_session_id: Optional[str] = None
    
    # Benefits eligibility
    benefits_eligible: bool = True
    health_insurance_eligible: bool = True
    pto_eligible: bool = True
    
    # Compliance status
    i9_completed: bool = False
    w4_completed: bool = False
    background_check_status: str = "pending"
    
    # Document management
    uploaded_documents: Dict[DocumentType, Dict[str, Any]] = Field(default_factory=dict)
    signatures: Dict[SignatureType, Dict[str, Any]] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    onboarding_completed_at: Optional[datetime] = None
    hired_at: Optional[datetime] = None
    
    # Audit and compliance
    compliance_audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    form_update_history: List[str] = Field(default_factory=list)  # Form update session IDs
    
    def get_full_name(self) -> str:
        """Get employee's full name"""
        first_name = self.personal_info.get("first_name", "")
        last_name = self.personal_info.get("last_name", "")
        return f"{first_name} {last_name}".strip()
    
    def is_onboarding_complete(self) -> bool:
        """Check if onboarding is fully complete"""
        return (self.onboarding_status == OnboardingStatus.APPROVED and
                self.i9_completed and self.w4_completed)
    
    def get_missing_requirements(self) -> List[str]:
        """Get list of missing onboarding requirements"""
        missing = []
        if not self.i9_completed:
            missing.append("I-9 Form")
        if not self.w4_completed:
            missing.append("W-4 Form")
        if not self.trafficking_awareness_completed:
            missing.append("Human Trafficking Awareness Training")
        if not self.background_check_authorized:
            missing.append("Background Check Authorization")
        if not self.weapons_policy_acknowledged:
            missing.append("Weapons Policy Acknowledgment")
        return missing

# =====================================
# DOCUMENT AND SIGNATURE MODELS
# =====================================

class OnboardingDocument(BaseModel):
    """Document model for onboarding system"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    employee_id: str
    document_type: DocumentType
    document_category: str  # federal_form, company_policy, etc.
    
    # File information
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    
    # Processing and OCR
    ocr_data: Dict[str, Any] = Field(default_factory=dict)
    processing_status: str = "pending"
    
    # Form data for digital forms
    form_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Status and review
    status: str = "pending"  # pending, uploaded, processed, approved, rejected
    version: int = 1
    
    # Review information
    reviewed_by: Optional[str] = None
    review_comments: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    # Compliance tracking
    federal_form: bool = False
    retention_required_until: Optional[date] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class DigitalSignature(BaseModel):
    """Digital signature model with legal compliance"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    employee_id: str
    document_id: Optional[str] = None
    signature_type: SignatureType
    
    # Signature data
    signature_data: str  # SVG or base64 image data
    signature_hash: str  # For integrity verification
    
    # Signer information
    signed_by: str  # User ID
    signed_by_name: str
    signed_by_role: UserRole
    
    # Legal compliance metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Verification
    is_verified: bool = False
    verification_method: Optional[str] = None
    verification_data: Optional[Dict[str, Any]] = None
    
    # Legal attestation
    legal_attestation: Optional[str] = None
    witness_signature: Optional[str] = None
    witness_name: Optional[str] = None

# =====================================
# AUDIT TRAIL AND COMPLIANCE MODELS
# =====================================

class AuditEntry(BaseModel):
    """Comprehensive audit trail entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str  # onboarding_session, employee, form_update, etc.
    entity_id: str
    action: str  # create, update, delete, approve, reject, etc.
    
    # Change tracking
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes_summary: Optional[str] = None
    
    # User context
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[UserRole] = None
    
    # Request context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    # Compliance and legal
    compliance_event: bool = False
    legal_requirement: Optional[str] = None
    retention_required_until: Optional[date] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ComplianceCheck(BaseModel):
    """Federal compliance validation result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    form_type: FormType
    employee_id: str
    session_id: str
    
    # Validation results
    status: ComplianceStatus
    is_compliant: bool
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Legal requirements
    federal_requirements_met: List[str] = Field(default_factory=list)
    federal_requirements_failed: List[str] = Field(default_factory=list)
    
    # Validation metadata
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validated_by: str  # System or user ID
    validation_version: str = "1.0"
    
    # Compliance notes
    compliance_notes: List[str] = Field(default_factory=list)
    legal_citations: List[str] = Field(default_factory=list)

# =====================================
# NOTIFICATION AND COMMUNICATION MODELS
# =====================================

class NotificationRecord(BaseModel):
    """Notification tracking model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_email: str
    recipient_name: str
    notification_type: str  # welcome, reminder, approval_required, etc.
    
    # Content
    subject: str
    message: str
    template_used: Optional[str] = None
    
    # Context
    session_id: Optional[str] = None
    employee_id: Optional[str] = None
    form_update_id: Optional[str] = None
    
    # Delivery tracking
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    
    # Status
    status: str = "sent"  # sent, delivered, failed, bounced
    error_message: Optional[str] = None

# =====================================
# REQUEST/RESPONSE MODELS
# =====================================

class OnboardingTokenRequest(BaseModel):
    """Request model for generating onboarding tokens"""
    employee_id: str
    expires_hours: Optional[int] = 72
    language_preference: Optional[str] = "en"
    send_notification: bool = True

class OnboardingTokenResponse(BaseModel):
    """Response model for onboarding token generation"""
    token: str
    onboarding_url: str
    expires_at: datetime
    employee_info: Dict[str, Any]
    session_id: str

class FormUpdateTokenRequest(BaseModel):
    """Request model for generating form update tokens"""
    employee_id: str
    form_type: FormType
    change_reason: str
    expires_hours: Optional[int] = 168  # 7 days default
    send_notification: bool = True

class FormUpdateTokenResponse(BaseModel):
    """Response model for form update token generation"""
    token: str
    update_url: str
    expires_at: datetime
    form_type: FormType
    current_data: Dict[str, Any]
    session_id: str

class OnboardingProgressUpdate(BaseModel):
    """Model for updating onboarding progress"""
    step: OnboardingStep
    form_data: Optional[Dict[str, Any]] = None
    signature_data: Optional[str] = None
    language_preference: Optional[str] = None
    
class ManagerReviewRequest(BaseModel):
    """Manager review and approval request"""
    action: str  # approve, reject, request_changes
    comments: Optional[str] = None
    specific_forms: Optional[List[FormType]] = None
    i9_section2_data: Optional[Dict[str, Any]] = None

class HRApprovalRequest(BaseModel):
    """HR final approval request"""
    action: str  # approve, reject, request_changes
    comments: Optional[str] = None
    correction_requests: Optional[List[Dict[str, Any]]] = None
    generate_certificate: bool = True

# =====================================
# VALIDATION MODELS
# =====================================

class FederalValidationError(BaseModel):
    """Federal compliance validation error"""
    field: str
    message: str
    legal_code: str
    severity: str  # error, warning, info
    compliance_note: Optional[str] = None

class FederalValidationResult(BaseModel):
    """Federal compliance validation result"""
    is_valid: bool
    form_type: FormType
    errors: List[FederalValidationError] = Field(default_factory=list)
    warnings: List[FederalValidationError] = Field(default_factory=list)
    compliance_notes: List[str] = Field(default_factory=list)
    legal_citations: List[str] = Field(default_factory=list)

# =====================================
# ANALYTICS AND REPORTING MODELS
# =====================================

class OnboardingAnalytics(BaseModel):
    """Onboarding analytics and metrics"""
    property_id: str
    date_range_start: date
    date_range_end: date
    
    # Completion metrics
    total_onboarding_sessions: int = 0
    completed_sessions: int = 0
    in_progress_sessions: int = 0
    expired_sessions: int = 0
    
    # Time metrics
    avg_completion_time_hours: Optional[float] = None
    avg_employee_phase_hours: Optional[float] = None
    avg_manager_review_hours: Optional[float] = None
    avg_hr_approval_hours: Optional[float] = None
    
    # Form update metrics
    total_form_updates: int = 0
    completed_form_updates: int = 0
    pending_form_updates: int = 0
    
    # Compliance metrics
    compliance_rate: float = 0.0
    federal_violations: int = 0
    
    # Department breakdown
    department_breakdown: Dict[str, Dict[str, int]] = Field(default_factory=dict)

# =====================================
# CONFIGURATION MODELS
# =====================================

class OnboardingConfiguration(BaseModel):
    """System configuration for onboarding"""
    # Session settings
    default_session_expiry_hours: int = 72
    reminder_intervals_hours: List[int] = Field(default_factory=lambda: [24, 48, 72])
    
    # Form update settings
    default_form_update_expiry_hours: int = 168  # 7 days
    require_manager_approval_for_updates: List[FormType] = Field(default_factory=list)
    
    # Notification settings
    send_welcome_notifications: bool = True
    send_reminder_notifications: bool = True
    send_completion_notifications: bool = True
    
    # Compliance settings
    strict_federal_validation: bool = True
    require_digital_signatures: bool = True
    audit_all_actions: bool = True
    
    # Language settings
    supported_languages: List[str] = Field(default_factory=lambda: ["en", "es"])
    default_language: str = "en"

# =====================================
# UTILITY FUNCTIONS
# =====================================

def generate_secure_token() -> str:
    """Generate a secure token for sessions"""
    import secrets
    return secrets.token_urlsafe(32)

def calculate_expiry_time(hours: int) -> datetime:
    """Calculate expiry time from current time"""
    return datetime.utcnow() + timedelta(hours=hours)

def validate_federal_ssn(ssn: str) -> bool:
    """Validate SSN format and known invalid patterns"""
    # Remove formatting
    ssn_clean = re.sub(r'[^\d]', '', ssn)
    
    # Must be exactly 9 digits
    if len(ssn_clean) != 9:
        return False
    
    # Check invalid patterns
    area = ssn_clean[:3]
    group = ssn_clean[3:5]
    serial = ssn_clean[5:9]
    
    # Invalid area numbers
    if area in ['000', '666'] or int(area) >= 900:
        return False
    
    # Invalid group/serial
    if group == '00' or serial == '0000':
        return False
    
    # Known invalid SSNs (test/placeholder numbers)
    known_invalid = [
        '111111111', '222222222', '333333333', '444444444',
        '555555555', '777777777', '888888888', '999999999'
    ]
    
    return ssn_clean not in known_invalid

def validate_federal_age(date_of_birth: str) -> bool:
    """Validate employee is at least 18 years old"""
    try:
        birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age >= 18
    except ValueError:
        return False