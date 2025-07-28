from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from enum import Enum
import uuid
import json
import os
import base64
from groq import Groq
from dotenv import load_dotenv
try:
    from .federal_validation import FederalValidationService
    from .models import I9Section1Data, W4FormData
except ImportError:
    # Fallback for when running as main module
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from federal_validation import FederalValidationService
    from models import I9Section1Data, W4FormData

load_dotenv()

app = FastAPI(title="Hotel Employee Onboarding System")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

database = {
    "users": {},
    "properties": {},
    "applications": {},
    "employees": {},
    "documents": {},
    "approvals": {},
    "document_edits": {},
    "signatures": {},
    "onboarding_sessions": {},
    "session_progress": {},
    "audit_trail": {}
}

class UserRole(str, Enum):
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class DocumentType(str, Enum):
    I9 = "i9"
    W4 = "w4"
    DIRECT_DEPOSIT = "direct_deposit"
    EMERGENCY_CONTACTS = "emergency_contacts"
    INSURANCE = "insurance"
    POLICIES = "policies"

class SignatureType(str, Enum):
    I9 = "i9"
    W4 = "w4"
    GENERAL = "general"

class OnboardingStep(str, Enum):
    PERSONAL_INFO = "personal-info"
    I9_SECTION1 = "i9-section1"
    I9_SUPPLEMENTS = "i9-supplements"
    DOCUMENT_UPLOAD = "document-upload"
    W4_FORM = "w4-form"
    DIRECT_DEPOSIT = "direct-deposit"
    HEALTH_INSURANCE = "health-insurance"
    COMPANY_POLICIES = "company-policies"
    TRAFFICKING_AWARENESS = "trafficking-awareness"
    WEAPONS_POLICY = "weapons-policy"
    EMPLOYEE_REVIEW = "employee-review"

class OnboardingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    EMPLOYEE_COMPLETED = "employee_completed"
    MANAGER_REVIEW = "manager_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_EDIT = "needs_edit"

class User(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    property_id: Optional[str] = None
    created_at: datetime

class Property(BaseModel):
    id: str
    name: str
    address: str
    qr_code_url: str
    manager_ids: List[str] = []
    created_at: datetime

class JobApplication(BaseModel):
    id: str
    property_id: str
    department: str
    position: str
    applicant_data: Dict[str, Any]
    status: ApplicationStatus
    created_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

class Employee(BaseModel):
    id: str
    user_id: str
    manager_id: str
    property_id: str
    hire_date: date
    department: str
    position: str
    status: str
    job_details: Dict[str, Any]
    created_at: datetime

class Document(BaseModel):
    id: str
    employee_id: str
    type: DocumentType
    file_url: Optional[str] = None
    ocr_data: Dict[str, Any] = {}
    form_data: Dict[str, Any] = {}
    status: DocumentStatus
    version: int = 1
    created_at: datetime

class Approval(BaseModel):
    id: str
    document_id: str
    approver_id: str
    status: DocumentStatus
    comments: Optional[str] = None
    timestamp: datetime

class I9Section1(BaseModel):
    last_name: str
    first_name: str
    middle_initial: Optional[str] = ""
    other_last_names: Optional[str] = ""
    address: str
    apt_number: Optional[str] = ""
    city: str
    state: str
    zip_code: str
    date_of_birth: str
    ssn: str
    email: str
    phone: str
    citizenship_status: str  # "1", "2", "3", or "4"
    uscis_number: Optional[str] = ""
    i94_number: Optional[str] = ""
    passport_info: Optional[str] = ""
    signature: str
    signature_date: str

class I9Section2(BaseModel):
    document_title_1: str
    issuing_authority_1: str
    document_number_1: str
    expiration_date_1: Optional[str] = ""
    document_title_2: Optional[str] = ""
    issuing_authority_2: Optional[str] = ""
    document_number_2: Optional[str] = ""
    expiration_date_2: Optional[str] = ""
    additional_info: Optional[str] = ""
    first_day_employment: str
    employer_name: str
    employer_signature: str
    employer_date: str

class W4Form(BaseModel):
    first_name: str
    middle_initial: Optional[str] = ""
    last_name: str
    address: str
    city: str
    state: str
    zip_code: str
    ssn: str
    filing_status: str  # "Single", "Married filing jointly", "Married filing separately", "Head of household"
    
    multiple_jobs_checkbox: bool = False
    spouse_works_checkbox: bool = False
    
    dependents_amount: Optional[float] = 0
    other_credits: Optional[float] = 0
    
    other_income: Optional[float] = 0
    deductions: Optional[float] = 0
    extra_withholding: Optional[float] = 0
    
    signature: str
    signature_date: str

class SignatureData(BaseModel):
    signature_data: str
    signature_type: SignatureType
    document_id: str
    signed_by: str
    signed_at: datetime
    ip_address: Optional[str] = ""
    user_agent: Optional[str] = ""

class OnboardingSession(BaseModel):
    id: str
    employee_id: str
    status: OnboardingStatus
    current_step: OnboardingStep
    steps_completed: List[OnboardingStep] = []
    progress_percentage: float = 0.0
    form_data: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    employee_completed_at: Optional[datetime] = None
    expires_at: datetime
    language_preference: str = "en"

class SessionProgressUpdate(BaseModel):
    step: OnboardingStep
    form_data: Optional[Dict[str, Any]] = None
    completed: bool = False

class SessionSaveRequest(BaseModel):
    step: OnboardingStep
    form_data: Dict[str, Any]
    auto_save: bool = True

class StepValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    missing_fields: List[str] = []

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    if token not in database["users"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    return database["users"][token]

def validate_employee_access(employee_id: str, current_user: User) -> Employee:
    """Validate that the current user has access to the employee's data"""
    if employee_id not in database["employees"]:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = database["employees"][employee_id]
    
    # Employee can only access their own data
    if current_user.role == UserRole.EMPLOYEE:
        if current_user.id != employee.user_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Manager can access employees in their property
    elif current_user.role == UserRole.MANAGER:
        if current_user.property_id != employee.property_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # HR has full access (no additional checks needed)
    elif current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return employee

def get_or_create_onboarding_session(employee_id: str) -> OnboardingSession:
    """Get existing session or create new one for employee"""
    # Look for existing active session
    for session in database["onboarding_sessions"].values():
        if session.employee_id == employee_id and session.status not in [OnboardingStatus.APPROVED, OnboardingStatus.REJECTED]:
            return session
    
    # Create new session
    session_id = str(uuid.uuid4())
    session = OnboardingSession(
        id=session_id,
        employee_id=employee_id,
        status=OnboardingStatus.NOT_STARTED,
        current_step=OnboardingStep.PERSONAL_INFO,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=7)  # 7-day expiration
    )
    database["onboarding_sessions"][session_id] = session
    return session

def calculate_progress_percentage(steps_completed: List[OnboardingStep]) -> float:
    """Calculate completion percentage based on completed steps"""
    total_steps = 11  # Total number of onboarding steps
    completed_count = len(steps_completed)
    return round((completed_count / total_steps) * 100, 1)

def validate_step_completion(step: OnboardingStep, form_data: Dict[str, Any]) -> StepValidationResult:
    """Validate that a step has required data for completion with federal compliance"""
    errors = []
    warnings = []
    missing_fields = []
    
    if step == OnboardingStep.PERSONAL_INFO:
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'ssn', 'email', 'phone', 'address', 'city', 'state', 'zip_code']
        for field in required_fields:
            if not form_data.get(field):
                missing_fields.append(field)
                errors.append(f"Missing required field: {field}")
        
        # Federal compliance validation for personal info
        if form_data.get('date_of_birth'):
            age_validation = FederalValidationService.validate_age(form_data['date_of_birth'])
            for error in age_validation.errors:
                errors.append(f"FEDERAL COMPLIANCE: {error.message}")
            for warning in age_validation.warnings:
                warnings.append(f"FEDERAL WARNING: {warning.message}")
        
        if form_data.get('ssn'):
            ssn_validation = FederalValidationService.validate_ssn(form_data['ssn'])
            for error in ssn_validation.errors:
                errors.append(f"FEDERAL COMPLIANCE: {error.message}")
            for warning in ssn_validation.warnings:
                warnings.append(f"FEDERAL WARNING: {warning.message}")
    
    elif step == OnboardingStep.I9_SECTION1:
        # Federal I-9 compliance validation
        try:
            i9_data = I9Section1Data(**form_data)
            i9_validation = FederalValidationService.validate_i9_section1(i9_data)
            
            for error in i9_validation.errors:
                errors.append(f"I-9 FEDERAL COMPLIANCE: {error.message}")
                if error.field not in missing_fields:
                    missing_fields.append(error.field)
            
            for warning in i9_validation.warnings:
                warnings.append(f"I-9 FEDERAL WARNING: {warning.message}")
                
        except ValueError as e:
            errors.append(f"I-9 Form validation error: {str(e)}")
            # Fall back to basic required field check
            required_fields = ['employee_last_name', 'employee_first_name', 'address_street', 'address_city', 'address_state', 'address_zip', 'date_of_birth', 'ssn', 'email', 'phone', 'citizenship_status']
            for field in required_fields:
                if not form_data.get(field):
                    missing_fields.append(field)
                    errors.append(f"Missing required I-9 field: {field}")
    
    elif step == OnboardingStep.W4_FORM:
        # Federal W-4 compliance validation
        try:
            w4_data = W4FormData(**form_data)
            w4_validation = FederalValidationService.validate_w4_form(w4_data)
            
            for error in w4_validation.errors:
                errors.append(f"W-4 FEDERAL COMPLIANCE: {error.message}")
                if error.field not in missing_fields:
                    missing_fields.append(error.field)
            
            for warning in w4_validation.warnings:
                warnings.append(f"W-4 FEDERAL WARNING: {warning.message}")
                
        except ValueError as e:
            errors.append(f"W-4 Form validation error: {str(e)}")
            # Fall back to basic required field check
            required_fields = ['first_name', 'last_name', 'address', 'city', 'state', 'zip_code', 'ssn', 'filing_status', 'signature_date']
            for field in required_fields:
                if not form_data.get(field):
                    missing_fields.append(field)
                    errors.append(f"Missing required W-4 field: {field}")
    
    elif step == OnboardingStep.DIRECT_DEPOSIT:
        required_fields = ['bank_name', 'routing_number', 'account_number', 'account_type']
        for field in required_fields:
            if not form_data.get(field):
                missing_fields.append(field)
                errors.append(f"Missing required direct deposit field: {field}")
        
        # Validate routing number format (9 digits)
        if form_data.get('routing_number'):
            routing = str(form_data['routing_number']).replace('-', '').replace(' ', '')
            if not routing.isdigit() or len(routing) != 9:
                errors.append("BANKING COMPLIANCE: Routing number must be exactly 9 digits")
        
        # Validate account number (basic format check)
        if form_data.get('account_number'):
            account = str(form_data['account_number']).replace('-', '').replace(' ', '')
            if not account.isdigit() or len(account) < 4 or len(account) > 17:
                errors.append("BANKING COMPLIANCE: Account number must be 4-17 digits")
    
    elif step == OnboardingStep.HEALTH_INSURANCE:
        # Health insurance can be waived, so check for either election or waiver
        if not form_data.get('medical_plan') and not form_data.get('is_waived'):
            errors.append("Must either select health insurance plan or waive coverage")
        
        # If waiving coverage, require waiver reason
        if form_data.get('is_waived') and not form_data.get('waiver_reason'):
            errors.append("Waiver reason is required when declining health insurance coverage")
    
    elif step == OnboardingStep.COMPANY_POLICIES:
        # Require acknowledgment of all policy sections
        required_acknowledgments = ['general_policies', 'safety_policies', 'harassment_policy', 'drug_alcohol_policy']
        for acknowledgment in required_acknowledgments:
            if not form_data.get(acknowledgment):
                missing_fields.append(acknowledgment)
                errors.append(f"Must acknowledge {acknowledgment.replace('_', ' ')}")
    
    elif step == OnboardingStep.TRAFFICKING_AWARENESS:
        # Require completion of trafficking awareness training
        if not form_data.get('training_completed'):
            errors.append("Human trafficking awareness training must be completed")
        if not form_data.get('acknowledgment_signed'):
            errors.append("Human trafficking awareness acknowledgment must be signed")
    
    elif step == OnboardingStep.WEAPONS_POLICY:
        # Require weapons policy acknowledgment
        if not form_data.get('policy_acknowledged'):
            errors.append("Weapons policy must be acknowledged")
        if not form_data.get('agreement_signed'):
            errors.append("Weapons policy agreement must be signed")
    
    elif step == OnboardingStep.EMPLOYEE_REVIEW:
        # Final review step - ensure all previous steps are completed
        if not form_data.get('employee_signature'):
            errors.append("Employee signature is required for final submission")
        if not form_data.get('final_acknowledgment'):
            errors.append("Final acknowledgment of all information accuracy is required")
    
    is_valid = len(errors) == 0
    return StepValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, missing_fields=missing_fields)

def create_audit_entry(user_id: str, action: str, details: Dict[str, Any]):
    """Create audit trail entry for compliance tracking"""
    audit_id = str(uuid.uuid4())
    audit_entry = {
        "id": audit_id,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "action": action,
        "details": details,
        "ip_address": None,  # Could be populated from request headers
        "user_agent": None   # Could be populated from request headers
    }
    database["audit_trail"][audit_id] = audit_entry

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/auth/login")
async def login(email: EmailStr, password: str):
    existing_user = None
    for user in database["users"].values():
        if user.email == email:
            existing_user = user
            break
    
    if existing_user:
        return {"token": existing_user.id, "user": existing_user}
    
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        role=UserRole.HR if email.endswith("@hr.com") else UserRole.MANAGER,
        created_at=datetime.now()
    )
    database["users"][user_id] = user
    return {"token": user_id, "user": user}

@app.post("/secret/create-hr")
async def create_hr_user(email: EmailStr, password: str, secret_key: str):
    if secret_key != "hotel-admin-2025":
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        role=UserRole.HR,
        created_at=datetime.now()
    )
    database["users"][user_id] = user
    return {"message": "HR user created successfully", "user": user}

@app.post("/hr/properties")
async def create_property(
    name: str = Form(...),
    address: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Only HR can create properties")
    
    property_id = str(uuid.uuid4())
    qr_code_url = f"https://app.domain.com/apply/{property_id}"
    
    property_obj = Property(
        id=property_id,
        name=name,
        address=address,
        qr_code_url=qr_code_url,
        created_at=datetime.now()
    )
    
    database["properties"][property_id] = property_obj
    return property_obj

@app.get("/hr/properties")
async def get_properties(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.HR:
        return list(database["properties"].values())
    elif current_user.role == UserRole.MANAGER:
        return [p for p in database["properties"].values() if current_user.id in p.manager_ids]
    else:
        raise HTTPException(status_code=403, detail="Access denied")

@app.post("/properties/{property_id}/managers")
async def assign_manager(
    property_id: str,
    manager_email: EmailStr,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Only HR can assign managers")
    
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    manager_id = str(uuid.uuid4())
    manager = User(
        id=manager_id,
        email=manager_email,
        role=UserRole.MANAGER,
        property_id=property_id,
        created_at=datetime.now()
    )
    
    database["users"][manager_id] = manager
    database["properties"][property_id].manager_ids.append(manager_id)
    
    for user_id, user in database["users"].items():
        if user.email == manager_email and user.role == UserRole.MANAGER:
            user.property_id = property_id
    
    return {"message": "Manager assigned successfully", "manager": manager}

@app.get("/apply/{property_id}")
async def get_application_form(property_id: str):
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    departments = [
        "Housekeeping", "Front Desk", "Maintenance", "Food Service", "Management"
    ]
    
    positions_by_dept = {
        "Housekeeping": ["Housekeeper", "Room Attendant", "Laundry Attendant"],
        "Front Desk": ["Front Desk Agent", "Night Auditor", "Guest Services"],
        "Maintenance": ["Maintenance Technician", "Groundskeeper"],
        "Food Service": ["Cook", "Server", "Dishwasher", "Kitchen Assistant"],
        "Management": ["Assistant Manager", "Supervisor"]
    }
    
    return {
        "property": property_obj,
        "departments": departments,
        "positions": positions_by_dept
    }

@app.post("/apply/{property_id}")
async def submit_application(
    property_id: str,
    department: str = Form(...),
    position: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
    work_authorized: str = Form(...),
    sponsorship_required: str = Form(...),
    start_date: str = Form(...),
    shift_preference: str = Form(...),
    employment_type: str = Form(...),
    experience_years: str = Form(...),
    hotel_experience: str = Form(...)
):
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    application_id = str(uuid.uuid4())
    application = JobApplication(
        id=application_id,
        property_id=property_id,
        department=department,
        position=position,
        applicant_data={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "work_authorized": work_authorized,
            "sponsorship_required": sponsorship_required,
            "start_date": start_date,
            "shift_preference": shift_preference,
            "employment_type": employment_type,
            "experience_years": experience_years,
            "hotel_experience": hotel_experience
        },
        status=ApplicationStatus.PENDING,
        created_at=datetime.now()
    )
    
    database["applications"][application_id] = application
    return {"message": "Application submitted successfully", "application_id": application_id}

@app.get("/applications")
async def get_applications(
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.MANAGER, UserRole.HR]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    applications = []
    for app in database["applications"].values():
        if current_user.role == UserRole.MANAGER:
            if current_user.property_id != app.property_id:
                continue
        
        if department and app.department != department:
            continue
            
        applications.append(app)
    
    return applications

@app.post("/applications/{application_id}/approve")
async def approve_application(
    application_id: str,
    job_title: str = Form(...),
    start_date: str = Form(...),
    start_time: str = Form(...),
    pay_rate: float = Form(...),
    pay_frequency: str = Form(...),
    benefits_eligible: str = Form(...),
    supervisor: str = Form(...),
    special_instructions: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can approve applications")
    
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    if current_user.property_id != application.property_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    application.status = ApplicationStatus.APPROVED
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.now()
    
    employee_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    employee_user = User(
        id=user_id,
        email=application.applicant_data["email"],
        role=UserRole.EMPLOYEE,
        property_id=application.property_id,
        created_at=datetime.now()
    )
    database["users"][user_id] = employee_user
    
    employee = Employee(
        id=employee_id,
        user_id=user_id,
        manager_id=current_user.id,
        property_id=application.property_id,
        hire_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
        department=application.department,
        position=job_title,
        status="pending_onboarding",
        job_details={
            "job_title": job_title,
            "start_date": start_date,
            "start_time": start_time,
            "pay_rate": pay_rate,
            "pay_frequency": pay_frequency,
            "benefits_eligible": benefits_eligible,
            "supervisor": supervisor,
            "special_instructions": special_instructions
        },
        created_at=datetime.now()
    )
    database["employees"][employee_id] = employee
    
    for app_id, app in database["applications"].items():
        if (app.property_id == application.property_id and 
            app.department == application.department and 
            app.status == ApplicationStatus.PENDING and
            app_id != application_id):
            app.status = ApplicationStatus.REJECTED
    
    return {
        "message": "Application approved successfully",
        "employee_id": employee_id,
        "onboarding_link": f"https://app.domain.com/onboard/{employee_id}"
    }

@app.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can reject applications")
    
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    if current_user.property_id != application.property_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    application.status = ApplicationStatus.REJECTED
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.now()
    
    return {"message": "Application rejected successfully"}

@app.get("/onboard/{employee_id}")
async def get_onboarding_info(employee_id: str):
    if employee_id not in database["employees"]:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = database["employees"][employee_id]
    property_obj = database["properties"][employee.property_id]
    
    return {
        "employee": employee,
        "property": property_obj,
        "required_documents": [
            {"type": "i9", "name": "I-9 Employment Eligibility Verification", "required": True},
            {"type": "w4", "name": "W-4 Employee's Withholding Certificate", "required": True},
            {"type": "direct_deposit", "name": "Direct Deposit Authorization", "required": True},
            {"type": "emergency_contacts", "name": "Emergency Contact Information", "required": True},
            {"type": "insurance", "name": "Health Insurance Enrollment", "required": True},
            {"type": "policies", "name": "Company Policies Acknowledgment", "required": True}
        ]
    }

@app.get("/api/employees/{employee_id}/welcome-data")
async def get_employee_welcome_data(employee_id: str):
    """Get comprehensive welcome data for the beautiful onboarding welcome page"""
    if employee_id not in database["employees"]:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = database["employees"][employee_id]
    property_obj = database["properties"][employee.property_id]
    
    # Find the original application to get applicant data
    applicant_data = {"first_name": "Employee", "last_name": "", "email": "", "phone": ""}
    for application in database["applications"].values():
        if (application.property_id == employee.property_id and 
            application.status == ApplicationStatus.APPROVED and
            application.department == employee.department):
            applicant_data = application.applicant_data
            break
    
    return {
        "employee": employee,
        "property": property_obj,
        "applicant_data": applicant_data
    }

@app.post("/onboard/{employee_id}/upload-document")
async def upload_document(
    employee_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...)
):
    if employee_id not in database["employees"]:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    file_content = await file.read()
    
    ocr_data = {}
    if file.content_type and file.content_type.startswith('image/'):
        try:
            ocr_data = await process_document_with_groq(file_content, document_type)
        except Exception as e:
            ocr_data = {"error": f"Groq OCR processing failed: {str(e)}"}
    
    document_id = str(uuid.uuid4())
    document = Document(
        id=document_id,
        employee_id=employee_id,
        type=DocumentType(document_type),
        file_url=f"/documents/{document_id}",
        ocr_data=ocr_data,
        status=DocumentStatus.PENDING,
        created_at=datetime.now()
    )
    
    database["documents"][document_id] = document
    
    import base64
    database[f"file_{document_id}"] = base64.b64encode(file_content).decode()
    
    return {"document_id": document_id, "ocr_data": ocr_data}

async def process_document_with_groq(file_content: bytes, document_type: str) -> Dict[str, Any]:
    """Process document using Groq API for OCR with vision capabilities"""
    try:
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        if document_type == "i9":
            prompt = """Analyze this I-9 Employment Eligibility Verification document image and extract the following information in JSON format:
            {
              "last_name": "",
              "first_name": "",
              "middle_initial": "",
              "other_last_names": "",
              "address": "",
              "apt_number": "",
              "city": "",
              "state": "",
              "zip_code": "",
              "date_of_birth": "",
              "ssn": "",
              "email": "",
              "phone": "",
              "document_title": "",
              "document_number": "",
              "issuing_authority": "",
              "expiration_date": ""
            }
            Only return valid JSON. If a field is not visible or unclear, use empty string. Focus on accuracy."""
        
        elif document_type == "w4":
            prompt = """Analyze this W-4 Employee's Withholding Certificate document image and extract the following information in JSON format:
            {
              "first_name": "",
              "middle_initial": "",
              "last_name": "",
              "address": "",
              "city": "",
              "state": "",
              "zip_code": "",
              "ssn": "",
              "filing_status": ""
            }
            Only return valid JSON. If a field is not visible or unclear, use empty string. Focus on accuracy."""
        
        else:
            prompt = """Analyze this document image and extract any visible text and key information in JSON format:
            {
              "document_type": "",
              "extracted_text": "",
              "key_fields": {}
            }
            Only return valid JSON."""
        
        response = groq_client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            max_tokens=int(os.getenv("GROQ_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("GROQ_TEMPERATURE", "0.1"))
        )
        
        ocr_data = json.loads(response.choices[0].message.content)
        return ocr_data
        
    except Exception as e:
        return {"error": f"Groq OCR processing failed: {str(e)}"}

@app.post("/onboard/{employee_id}/submit-form")
async def submit_form(
    employee_id: str,
    document_type: str = Form(...),
    form_data: str = Form(...)
):
    if employee_id not in database["employees"]:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        form_json = json.loads(form_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid form data")
    
    document = None
    for doc in database["documents"].values():
        if doc.employee_id == employee_id and doc.type == document_type:
            document = doc
            break
    
    if not document:
        document_id = str(uuid.uuid4())
        document = Document(
            id=document_id,
            employee_id=employee_id,
            type=DocumentType(document_type),
            status=DocumentStatus.PENDING,
            created_at=datetime.now()
        )
        database["documents"][document_id] = document
    
    document.form_data = form_json
    
    return {"message": "Form submitted successfully", "document_id": document.id}

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    if document_id not in database["documents"]:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = database["documents"][document_id]
    
    file_content = None
    if f"file_{document_id}" in database:
        import base64
        file_content = base64.b64decode(database[f"file_{document_id}"])
    
    return {
        "document": document,
        "has_file": file_content is not None
    }

@app.get("/employees/{employee_id}/documents")
async def get_employee_documents(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    if employee_id not in database["employees"]:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = database["employees"][employee_id]
    
    if current_user.role == UserRole.MANAGER:
        if current_user.property_id != employee.property_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role not in [UserRole.HR, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    documents = []
    for doc in database["documents"].values():
        if doc.employee_id == employee_id:
            documents.append(doc)
    
    return {"employee": employee, "documents": documents}

@app.post("/documents/{document_id}/approve")
async def approve_document(
    document_id: str,
    comments: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.MANAGER, UserRole.HR]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if document_id not in database["documents"]:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = database["documents"][document_id]
    employee = database["employees"][document.employee_id]
    
    if current_user.role == UserRole.MANAGER:
        if current_user.property_id != employee.property_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    document.status = DocumentStatus.APPROVED
    
    approval_id = str(uuid.uuid4())
    approval = Approval(
        id=approval_id,
        document_id=document_id,
        approver_id=current_user.id,
        status=DocumentStatus.APPROVED,
        comments=comments,
        timestamp=datetime.now()
    )
    database["approvals"][approval_id] = approval
    
    return {"message": "Document approved successfully"}

@app.post("/documents/{document_id}/request-edit")
async def request_document_edit(
    document_id: str,
    comments: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.MANAGER, UserRole.HR]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if document_id not in database["documents"]:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document = database["documents"][document_id]
    employee = database["employees"][document.employee_id]
    
    if current_user.role == UserRole.MANAGER:
        if current_user.property_id != employee.property_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    document.status = DocumentStatus.NEEDS_EDIT
    
    edit_id = str(uuid.uuid4())
    database["document_edits"][edit_id] = {
        "id": edit_id,
        "document_id": document_id,
        "requested_by": current_user.id,
        "comments": comments,
        "timestamp": datetime.now(),
        "status": "pending"
    }
    
    return {"message": "Edit request submitted successfully"}

# =====================================
# ONBOARDING SESSION MANAGEMENT ENDPOINTS
# =====================================

@app.get("/api/onboarding/session/{employee_id}")
async def get_onboarding_session(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retrieve current onboarding progress and session data"""
    # Validate access to employee data
    employee = validate_employee_access(employee_id, current_user)
    
    # Get or create onboarding session
    session = get_or_create_onboarding_session(employee_id)
    
    # Update session if it was just accessed
    session.updated_at = datetime.now()
    
    # Create audit entry
    create_audit_entry(
        user_id=current_user.id,
        action="session_accessed",
        details={"employee_id": employee_id, "session_id": session.id}
    )
    
    return {
        "session": session,
        "employee": employee,
        "step_definitions": {
            "personal-info": {"name": "Personal Information", "order": 1, "required": True},
            "i9-section1": {"name": "I-9 Section 1", "order": 2, "required": True},
            "i9-supplements": {"name": "I-9 Supplements", "order": 3, "required": False},
            "document-upload": {"name": "Document Upload", "order": 4, "required": True},
            "w4-form": {"name": "W-4 Tax Form", "order": 5, "required": True},
            "direct-deposit": {"name": "Direct Deposit", "order": 6, "required": True},
            "health-insurance": {"name": "Health Insurance", "order": 7, "required": True},
            "company-policies": {"name": "Company Policies", "order": 8, "required": True},
            "trafficking-awareness": {"name": "Human Trafficking Awareness", "order": 9, "required": True},
            "weapons-policy": {"name": "Weapons Policy", "order": 10, "required": True},
            "employee-review": {"name": "Final Review", "order": 11, "required": True}
        }
    }

@app.post("/api/onboarding/session/{employee_id}/progress")
async def update_onboarding_progress(
    employee_id: str,
    progress_update: SessionProgressUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update progress when user completes a step"""
    # Validate access to employee data
    employee = validate_employee_access(employee_id, current_user)
    
    # Get existing session
    session = get_or_create_onboarding_session(employee_id)
    
    # Validate step completion if marked as completed
    if progress_update.completed:
        validation_result = validate_step_completion(progress_update.step, progress_update.form_data or {})
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Step validation failed",
                    "errors": validation_result.errors,
                    "missing_fields": validation_result.missing_fields
                }
            )
    
    # Update session data
    if progress_update.form_data:
        if progress_update.step.value not in session.form_data:
            session.form_data[progress_update.step.value] = {}
        session.form_data[progress_update.step.value].update(progress_update.form_data)
    
    # Mark step as completed if validation passed
    if progress_update.completed and progress_update.step not in session.steps_completed:
        session.steps_completed.append(progress_update.step)
        
        # Update current step to next step
        step_order = {
            OnboardingStep.PERSONAL_INFO: OnboardingStep.I9_SECTION1,
            OnboardingStep.I9_SECTION1: OnboardingStep.I9_SUPPLEMENTS,
            OnboardingStep.I9_SUPPLEMENTS: OnboardingStep.DOCUMENT_UPLOAD,
            OnboardingStep.DOCUMENT_UPLOAD: OnboardingStep.W4_FORM,
            OnboardingStep.W4_FORM: OnboardingStep.DIRECT_DEPOSIT,
            OnboardingStep.DIRECT_DEPOSIT: OnboardingStep.HEALTH_INSURANCE,
            OnboardingStep.HEALTH_INSURANCE: OnboardingStep.COMPANY_POLICIES,
            OnboardingStep.COMPANY_POLICIES: OnboardingStep.TRAFFICKING_AWARENESS,
            OnboardingStep.TRAFFICKING_AWARENESS: OnboardingStep.WEAPONS_POLICY,
            OnboardingStep.WEAPONS_POLICY: OnboardingStep.EMPLOYEE_REVIEW
        }
        
        if progress_update.step in step_order:
            session.current_step = step_order[progress_update.step]
        elif progress_update.step == OnboardingStep.EMPLOYEE_REVIEW:
            session.status = OnboardingStatus.EMPLOYEE_COMPLETED
            session.employee_completed_at = datetime.now()
    
    # Update progress percentage
    session.progress_percentage = calculate_progress_percentage(session.steps_completed)
    session.updated_at = datetime.now()
    
    # Update employee onboarding status
    if employee_id in database["employees"]:
        if session.status == OnboardingStatus.EMPLOYEE_COMPLETED:
            database["employees"][employee_id].status = "pending_manager_review"
    
    # Create audit entry
    create_audit_entry(
        user_id=current_user.id,
        action="step_completed" if progress_update.completed else "step_progress",
        details={
            "employee_id": employee_id,
            "session_id": session.id,
            "step": progress_update.step.value,
            "completed": progress_update.completed
        }
    )
    
    return {
        "message": "Progress updated successfully",
        "session": session,
        "validation_result": validation_result if progress_update.completed else None
    }

@app.post("/api/onboarding/session/{employee_id}/save")
async def auto_save_session_data(
    employee_id: str,
    save_request: SessionSaveRequest,
    current_user: User = Depends(get_current_user)
):
    """Auto-save functionality for in-progress forms"""
    # Validate access to employee data
    employee = validate_employee_access(employee_id, current_user)
    
    # Get existing session
    session = get_or_create_onboarding_session(employee_id)
    
    # Save form data without validation (auto-save)
    if save_request.step.value not in session.form_data:
        session.form_data[save_request.step.value] = {}
    
    session.form_data[save_request.step.value].update(save_request.form_data)
    session.updated_at = datetime.now()
    
    # Create audit entry for auto-save (less detailed)
    if not save_request.auto_save:  # Only log manual saves
        create_audit_entry(
            user_id=current_user.id,
            action="manual_save",
            details={
                "employee_id": employee_id,
                "session_id": session.id,
                "step": save_request.step.value
            }
        )
    
    return {
        "message": "Data saved successfully",
        "saved_at": session.updated_at,
        "step": save_request.step.value
    }

@app.get("/api/onboarding/session/{employee_id}/step/{step_name}")
async def get_step_data(
    employee_id: str,
    step_name: str,
    current_user: User = Depends(get_current_user)
):
    """Retrieve specific step data and form values"""
    # Validate access to employee data
    employee = validate_employee_access(employee_id, current_user)
    
    # Validate step name
    try:
        step = OnboardingStep(step_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid step name: {step_name}")
    
    # Get existing session
    session = get_or_create_onboarding_session(employee_id)
    
    # Check if user has access to this step (can't skip ahead)
    step_order = [
        OnboardingStep.PERSONAL_INFO,
        OnboardingStep.I9_SECTION1,
        OnboardingStep.I9_SUPPLEMENTS,
        OnboardingStep.DOCUMENT_UPLOAD,
        OnboardingStep.W4_FORM,
        OnboardingStep.DIRECT_DEPOSIT,
        OnboardingStep.HEALTH_INSURANCE,
        OnboardingStep.COMPANY_POLICIES,
        OnboardingStep.TRAFFICKING_AWARENESS,
        OnboardingStep.WEAPONS_POLICY,
        OnboardingStep.EMPLOYEE_REVIEW
    ]
    
    current_step_index = step_order.index(session.current_step)
    requested_step_index = step_order.index(step)
    
    # Allow access to current step, previous completed steps, or if user is manager/HR
    if (current_user.role == UserRole.EMPLOYEE and 
        requested_step_index > current_step_index and 
        step not in session.steps_completed):
        raise HTTPException(
            status_code=403, 
            detail="Cannot access future steps. Complete current step first."
        )
    
    # Get form data for this step
    step_data = session.form_data.get(step_name, {})
    
    # Check if step is completed
    is_completed = step in session.steps_completed
    
    # Get validation result for completed steps
    validation_result = None
    if is_completed:
        validation_result = validate_step_completion(step, step_data)
    
    return {
        "step": step_name,
        "form_data": step_data,
        "is_completed": is_completed,
        "can_edit": current_user.role in [UserRole.MANAGER, UserRole.HR] or not is_completed,
        "validation_result": validation_result,
        "employee": employee,
        "session_info": {
            "current_step": session.current_step,
            "progress_percentage": session.progress_percentage,
            "status": session.status
        }
    }

# Manager Review Endpoints
@app.get("/api/onboarding/sessions/pending-review")
async def get_pending_review_sessions(
    current_user: User = Depends(get_current_user)
):
    """Get all sessions pending manager review"""
    if current_user.role not in [UserRole.MANAGER, UserRole.HR]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    pending_sessions = []
    for session in database["onboarding_sessions"].values():
        if session.status == OnboardingStatus.EMPLOYEE_COMPLETED:
            employee = database["employees"].get(session.employee_id)
            if employee:
                # Managers can only see employees in their property
                if current_user.role == UserRole.MANAGER:
                    if current_user.property_id != employee.property_id:
                        continue
                
                pending_sessions.append({
                    "session": session,
                    "employee": employee
                })
    
    return {"pending_sessions": pending_sessions}

@app.post("/api/onboarding/session/{employee_id}/review")
async def submit_manager_review(
    employee_id: str,
    action: str = Form(...),  # "approve", "reject", "request_changes"
    comments: str = Form(""),
    current_user: User = Depends(get_current_user)
):
    """Submit manager review for completed onboarding"""
    if current_user.role not in [UserRole.MANAGER, UserRole.HR]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate access to employee data
    employee = validate_employee_access(employee_id, current_user)
    
    # Get session
    session = get_or_create_onboarding_session(employee_id)
    
    if session.status != OnboardingStatus.EMPLOYEE_COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail="Session is not ready for manager review"
        )
    
    # Process review action
    if action == "approve":
        session.status = OnboardingStatus.APPROVED
        employee.status = "onboarding_complete"
        employee.onboarding_completed_at = datetime.now()
    elif action == "reject":
        session.status = OnboardingStatus.REJECTED
        employee.status = "onboarding_rejected"
    elif action == "request_changes":
        session.status = OnboardingStatus.IN_PROGRESS
        # Reset to appropriate step based on what needs changes
        session.current_step = OnboardingStep.PERSONAL_INFO
        employee.status = "pending_onboarding"
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    session.updated_at = datetime.now()
    
    # Create audit entry
    create_audit_entry(
        user_id=current_user.id,
        action=f"manager_review_{action}",
        details={
            "employee_id": employee_id,
            "session_id": session.id,
            "comments": comments,
            "action": action
        }
    )
    
    return {
        "message": f"Review {action} submitted successfully",
        "session": session,
        "employee": employee
    }

# =====================================
# FEDERAL COMPLIANCE VALIDATION ENDPOINTS
# =====================================

@app.post("/api/compliance/validate/personal-info")
async def validate_personal_info_compliance(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Validate personal information for federal compliance"""
    try:
        # Age validation
        age_result = None
        if request_data.get('date_of_birth'):
            age_result = FederalValidationService.validate_age(request_data['date_of_birth'])
        
        # SSN validation
        ssn_result = None
        if request_data.get('ssn'):
            ssn_result = FederalValidationService.validate_ssn(request_data['ssn'])
        
        # Create audit entry
        create_audit_entry(
            user_id=current_user.id,
            action="personal_info_validation",
            details={
                "validation_type": "personal_info",
                "has_age_data": bool(request_data.get('date_of_birth')),
                "has_ssn_data": bool(request_data.get('ssn')),
                "age_valid": age_result.is_valid if age_result else None,
                "ssn_valid": ssn_result.is_valid if ssn_result else None
            }
        )
        
        return {
            "age_validation": age_result,
            "ssn_validation": ssn_result,
            "overall_compliant": all([
                result.is_valid for result in [age_result, ssn_result] if result is not None
            ])
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")

@app.post("/api/compliance/validate/i9-section1")
async def validate_i9_section1_compliance(
    form_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Validate I-9 Section 1 for federal immigration compliance"""
    try:
        # Convert form data to I9Section1Data model
        i9_data = I9Section1Data(**form_data)
        
        # Perform federal validation
        validation_result = FederalValidationService.validate_i9_section1(i9_data)
        
        # Generate compliance audit entry
        audit_entry = FederalValidationService.generate_compliance_audit_entry(
            form_type="I-9_Section_1",
            validation_result=validation_result,
            user_info={"id": current_user.id, "email": current_user.email}
        )
        
        # Store audit entry
        database["audit_trail"][audit_entry.audit_id] = audit_entry.dict()
        
        # Create regular audit entry
        create_audit_entry(
            user_id=current_user.id,
            action="i9_section1_validation",
            details={
                "validation_type": "i9_section1",
                "compliance_status": audit_entry.compliance_status,
                "error_count": audit_entry.error_count,
                "warning_count": audit_entry.warning_count,
                "audit_id": audit_entry.audit_id
            }
        )
        
        return {
            "validation_result": validation_result,
            "compliance_audit": audit_entry,
            "federal_compliance_status": "COMPLIANT" if validation_result.is_valid else "NON_COMPLIANT"
        }
        
    except ValueError as e:
        # Handle validation errors in the data model itself
        error_message = str(e)
        if "FEDERAL COMPLIANCE" in error_message:
            # This is a federal compliance violation
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Federal compliance violation detected",
                    "compliance_error": error_message,
                    "severity": "CRITICAL",
                    "legal_reference": "Immigration and Nationality Act Section 274A"
                }
            )
        else:
            raise HTTPException(status_code=400, detail=f"I-9 data validation error: {error_message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"I-9 validation system error: {str(e)}")

@app.post("/api/compliance/validate/w4-form")
async def validate_w4_form_compliance(
    form_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Validate W-4 form for federal tax compliance"""
    try:
        # Convert form data to W4FormData model
        w4_data = W4FormData(**form_data)
        
        # Perform federal validation
        validation_result = FederalValidationService.validate_w4_form(w4_data)
        
        # Generate compliance audit entry
        audit_entry = FederalValidationService.generate_compliance_audit_entry(
            form_type="W-4_Tax_Form",
            validation_result=validation_result,
            user_info={"id": current_user.id, "email": current_user.email}
        )
        
        # Store audit entry
        database["audit_trail"][audit_entry.audit_id] = audit_entry.dict()
        
        # Create regular audit entry
        create_audit_entry(
            user_id=current_user.id,
            action="w4_form_validation",
            details={
                "validation_type": "w4_form",
                "compliance_status": audit_entry.compliance_status,
                "error_count": audit_entry.error_count,
                "warning_count": audit_entry.warning_count,
                "audit_id": audit_entry.audit_id
            }
        )
        
        return {
            "validation_result": validation_result,
            "compliance_audit": audit_entry,
            "federal_compliance_status": "COMPLIANT" if validation_result.is_valid else "NON_COMPLIANT"
        }
        
    except ValueError as e:
        # Handle validation errors in the data model itself
        error_message = str(e)
        if "FEDERAL TAX COMPLIANCE" in error_message:
            # This is a federal tax compliance violation
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Federal tax compliance violation detected",
                    "compliance_error": error_message,
                    "severity": "CRITICAL",
                    "legal_reference": "Internal Revenue Code Section 3402"
                }
            )
        else:
            raise HTTPException(status_code=400, detail=f"W-4 data validation error: {error_message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"W-4 validation system error: {str(e)}")

@app.get("/api/compliance/audit-trail/{employee_id}")
async def get_compliance_audit_trail(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retrieve compliance audit trail for an employee"""
    # Validate access to employee data
    validate_employee_access(employee_id, current_user)
    
    # Get all audit entries related to this employee
    employee_audits = []
    for audit_entry in database["audit_trail"].values():
        # Check if audit entry is related to this employee
        if (audit_entry.get("details", {}).get("employee_id") == employee_id or
            audit_entry.get("user_id") == employee_id):
            employee_audits.append(audit_entry)
    
    # Sort by timestamp (most recent first)
    employee_audits.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {
        "employee_id": employee_id,
        "audit_entries": employee_audits,
        "total_entries": len(employee_audits)
    }

@app.get("/api/compliance/status/{employee_id}")
async def get_employee_compliance_status(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get overall compliance status for an employee"""
    # Validate access to employee data
    employee = validate_employee_access(employee_id, current_user)
    
    # Get onboarding session
    session = get_or_create_onboarding_session(employee_id)
    
    # Check compliance status for each critical step
    compliance_status = {
        "overall_compliant": True,
        "critical_violations": [],
        "warnings": [],
        "step_compliance": {}
    }
    
    # Check I-9 compliance
    if OnboardingStep.I9_SECTION1 in session.steps_completed:
        i9_data = session.form_data.get("i9-section1", {})
        if i9_data:
            try:
                i9_section1 = I9Section1Data(**i9_data)
                i9_validation = FederalValidationService.validate_i9_section1(i9_section1)
                compliance_status["step_compliance"]["i9_section1"] = {
                    "compliant": i9_validation.is_valid,
                    "errors": [err.message for err in i9_validation.errors],
                    "warnings": [warn.message for warn in i9_validation.warnings]
                }
                if not i9_validation.is_valid:
                    compliance_status["overall_compliant"] = False
                    compliance_status["critical_violations"].extend([err.message for err in i9_validation.errors])
            except Exception as e:
                compliance_status["overall_compliant"] = False
                compliance_status["critical_violations"].append(f"I-9 validation error: {str(e)}")
    
    # Check W-4 compliance
    if OnboardingStep.W4_FORM in session.steps_completed:
        w4_data = session.form_data.get("w4-form", {})
        if w4_data:
            try:
                w4_form = W4FormData(**w4_data)
                w4_validation = FederalValidationService.validate_w4_form(w4_form)
                compliance_status["step_compliance"]["w4_form"] = {
                    "compliant": w4_validation.is_valid,
                    "errors": [err.message for err in w4_validation.errors],
                    "warnings": [warn.message for warn in w4_validation.warnings]
                }
                if not w4_validation.is_valid:
                    compliance_status["overall_compliant"] = False
                    compliance_status["critical_violations"].extend([err.message for err in w4_validation.errors])
            except Exception as e:
                compliance_status["overall_compliant"] = False
                compliance_status["critical_violations"].append(f"W-4 validation error: {str(e)}")
    
    return {
        "employee": employee,
        "session": session,
        "compliance_status": compliance_status,
        "compliance_summary": {
            "status": "COMPLIANT" if compliance_status["overall_compliant"] else "NON_COMPLIANT",
            "critical_violation_count": len(compliance_status["critical_violations"]),
            "warning_count": len(compliance_status["warnings"]),
            "last_updated": session.updated_at
        }
    }

# =====================================
# SESSION ANALYTICS AND REPORTING
# =====================================

@app.get("/api/onboarding/analytics/sessions")
async def get_session_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get analytics about onboarding sessions"""
    if current_user.role not in [UserRole.MANAGER, UserRole.HR]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Filter sessions based on user role
    relevant_sessions = []
    for session in database["onboarding_sessions"].values():
        employee = database["employees"].get(session.employee_id)
        if employee:
            # Managers can only see sessions in their property
            if current_user.role == UserRole.MANAGER:
                if current_user.property_id != employee.property_id:
                    continue
            relevant_sessions.append({"session": session, "employee": employee})
    
    # Calculate analytics
    total_sessions = len(relevant_sessions)
    status_counts = {}
    step_completion_stats = {}
    
    for item in relevant_sessions:
        session = item["session"]
        # Count by status
        status = session.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count step completions
        for step in session.steps_completed:
            step_name = step.value
            step_completion_stats[step_name] = step_completion_stats.get(step_name, 0) + 1
    
    return {
        "total_sessions": total_sessions,
        "status_distribution": status_counts,
        "step_completion_stats": step_completion_stats,
        "average_progress": sum([s["session"].progress_percentage for s in relevant_sessions]) / total_sessions if total_sessions > 0 else 0,
        "sessions_pending_review": status_counts.get("employee_completed", 0),
        "sessions_approved": status_counts.get("approved", 0),
        "compliance_summary": {
            "total_audited": len(database["audit_trail"]),
            "recent_violations": 0  # Could be calculated based on audit trail
        }
    }
