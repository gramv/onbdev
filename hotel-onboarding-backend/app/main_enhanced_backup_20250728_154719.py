"""
Enhanced Hotel Employee Onboarding System API
Comprehensive implementation with JWT authentication and full onboarding workflow
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta, timezone
import uuid
import json
import os
import base64
import jwt
from groq import Groq
from dotenv import load_dotenv

# Import our enhanced models and authentication
from .models import *
from .models_enhanced import *
from .auth import OnboardingTokenManager, PasswordManager
from .pdf_forms import pdf_form_service
from .pdf_api import router as pdf_router
from .federal_validation import FederalValidationService
from .qr_service import qr_service
from .email_service import email_service
from .services.onboarding_orchestrator import OnboardingOrchestrator
from .services.form_update_service import FormUpdateService

load_dotenv()

app = FastAPI(
    title="Hotel Employee Onboarding System",
    description="Comprehensive onboarding system with secure token-based authentication",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include PDF API routes
app.include_router(pdf_router)

# Initialize services
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
token_manager = OnboardingTokenManager()
password_manager = PasswordManager()
security = HTTPBearer()

# Enhanced in-memory database with proper structure
database = {
    "users": {},
    "properties": {},
    "applications": {},
    "employees": {},
    "onboarding_sessions": {},
    "form_update_sessions": {},  # For individual form updates
    "documents": {},
    "signatures": {},
    "approvals": {},
    "review_actions": {},
    "file_storage": {},  # For storing uploaded files
    "compliance_audit_trail": {},  # For federal compliance audit logs
    "application_status_history": {},  # For tracking application status changes
    "audit_trail": {},  # Enhanced audit trail for onboarding system
    "notifications": {}  # Notification tracking
}

# Initialize enhanced services after database is defined
onboarding_orchestrator = None
form_update_service = None

def initialize_services():
    """Initialize enhanced onboarding services"""
    global onboarding_orchestrator, form_update_service
    onboarding_orchestrator = OnboardingOrchestrator(database)
    form_update_service = FormUpdateService(database)

# Test Data Initialization
def initialize_test_data():
    """Initialize database with test data for development"""
    
    # Generate consistent IDs for testing
    hr_user_id = "hr_test_001"
    manager_user_id = "mgr_test_001"
    property_id = "prop_test_001"
    application_id = "app_test_001"
    
    # HR User
    hr_user = User(
        id=hr_user_id,
        email="hr@hoteltest.com",
        first_name="Sarah",
        last_name="Johnson", 
        role=UserRole.HR,
        created_at=datetime.now(timezone.utc)
    )
    database["users"][hr_user_id] = hr_user
    
    # Manager User  
    manager_user = User(
        id=manager_user_id,
        email="manager@hoteltest.com",
        first_name="Mike", 
        last_name="Wilson",
        role=UserRole.MANAGER,
        property_id=property_id,
        created_at=datetime.now(timezone.utc)
    )
    database["users"][manager_user_id] = manager_user
    
    # Test Property with QR code generation
    try:
        qr_data = qr_service.generate_qr_code(property_id)
        qr_code_url = qr_data["qr_code_url"]
    except Exception as e:
        # Fallback URL if QR generation fails during initialization
        qr_code_url = f"http://localhost:3000/apply/{property_id}"
        print(f"⚠️  QR code generation failed during initialization: {e}")
    
    property_obj = Property(
        id=property_id,
        name="Grand Plaza Hotel",
        address="123 Main Street",
        city="Downtown", 
        state="CA",
        zip_code="90210",
        phone="(555) 123-4567",
        qr_code_url=qr_code_url,
        manager_ids=[manager_user_id],
        created_at=datetime.now(timezone.utc)
    )
    database["properties"][property_id] = property_obj
    
    # Test Application
    application = JobApplication(
        id=application_id,
        property_id=property_id,
        department="Front Desk",
        position="Front Desk Agent",
        applicant_data={
            "first_name": "John",
            "last_name": "Doe", 
            "email": "john.doe@email.com",
            "phone": "(555) 987-6543",
            "address": "456 Oak Avenue",
            "city": "Somewhere",
            "state": "CA", 
            "zip_code": "90211",
            "work_authorized": "yes",
            "sponsorship_required": "no",
            "start_date": "2025-02-01",
            "shift_preference": "morning",
            "employment_type": "full_time",
            "experience_years": "2-5",
            "hotel_experience": "yes"
        },
        status=ApplicationStatus.PENDING,
        applied_at=datetime.now(timezone.utc)
    )
    database["applications"][application_id] = application
    
    # Create test employees
    test_employees = [
        {
            "id": "emp_test_001",
            "user_id": "user_emp_001",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@hoteltest.com",
            "department": "Front Desk",
            "position": "Front Desk Agent",
            "employment_status": "active",
            "onboarding_status": OnboardingStatus.APPROVED,
            "hire_date": date(2024, 12, 1),
            "pay_rate": 18.50
        },
        {
            "id": "emp_test_002", 
            "user_id": "user_emp_002",
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@hoteltest.com",
            "department": "Housekeeping",
            "position": "Housekeeper",
            "employment_status": "active",
            "onboarding_status": OnboardingStatus.IN_PROGRESS,
            "hire_date": date(2025, 1, 15),
            "pay_rate": 16.00
        },
        {
            "id": "emp_test_003",
            "user_id": "user_emp_003", 
            "first_name": "Carol",
            "last_name": "Davis",
            "email": "carol.davis@hoteltest.com",
            "department": "Food & Beverage",
            "position": "Server",
            "employment_status": "active",
            "onboarding_status": OnboardingStatus.EMPLOYEE_COMPLETED,
            "hire_date": date(2025, 1, 20),
            "pay_rate": 15.00
        },
        {
            "id": "emp_test_004",
            "user_id": "user_emp_004",
            "first_name": "David",
            "last_name": "Wilson",
            "email": "david.wilson@hoteltest.com", 
            "department": "Maintenance",
            "position": "Maintenance Technician",
            "employment_status": "on_leave",
            "onboarding_status": OnboardingStatus.APPROVED,
            "hire_date": date(2024, 10, 1),
            "pay_rate": 22.00
        },
        {
            "id": "emp_test_005",
            "user_id": "user_emp_005",
            "first_name": "Emma",
            "last_name": "Brown",
            "email": "emma.brown@hoteltest.com",
            "department": "Front Desk", 
            "position": "Night Auditor",
            "employment_status": "active",
            "onboarding_status": OnboardingStatus.NOT_STARTED,
            "hire_date": date(2025, 2, 1),
            "pay_rate": 17.50
        }
    ]
    
    for emp_data in test_employees:
        # Create user account for employee
        employee_user = User(
            id=emp_data["user_id"],
            email=emp_data["email"],
            first_name=emp_data["first_name"],
            last_name=emp_data["last_name"],
            role=UserRole.EMPLOYEE,
            property_id=property_id,
            created_at=datetime.now(timezone.utc)
        )
        database["users"][emp_data["user_id"]] = employee_user
        
        # Create employee record
        employee = Employee(
            id=emp_data["id"],
            user_id=emp_data["user_id"],
            property_id=property_id,
            manager_id=manager_user_id,
            department=emp_data["department"],
            position=emp_data["position"],
            hire_date=emp_data["hire_date"],
            employment_status=emp_data["employment_status"],
            onboarding_status=emp_data["onboarding_status"],
            pay_rate=emp_data["pay_rate"],
            pay_frequency="biweekly",
            employment_type="full_time",
            created_at=datetime.now(timezone.utc)
        )
        database["employees"][emp_data["id"]] = employee
    
    # Initialize test passwords
    password_manager.store_password("hr@hoteltest.com", "admin123")
    password_manager.store_password("manager@hoteltest.com", "manager123")
    
    print("✅ Test data initialized:")
    print(f"   HR: hr@hoteltest.com (Token: {hr_user_id})")
    print(f"   Manager: manager@hoteltest.com (Token: {manager_user_id})")
    print(f"   Property: Grand Plaza Hotel (ID: {property_id})")
    print(f"   Application: John Doe - Front Desk Agent (ID: {application_id})")
    print(f"   Employees: {len(test_employees)} test employees created")
    print(f"   Application URL: http://localhost:8000/apply/{property_id}")

# Initialize test data on startup
initialize_test_data()

# Initialize enhanced services
initialize_services()

# Enhanced Authentication Dependencies and Middleware
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Enhanced JWT token validation with proper error handling"""
    token = credentials.credentials
    
    try:
        # Decode JWT token with proper secret key
        payload = jwt.decode(
            token, 
            os.getenv("JWT_SECRET_KEY", "fallback-secret"), 
            algorithms=["HS256"]
        )
        
        # Validate token structure
        token_type = payload.get("token_type")
        if not token_type:
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        # Handle different token types with proper validation
        if token_type == "manager_auth":
            manager_id = payload.get("manager_id")
            if not manager_id or manager_id not in database["users"]:
                raise HTTPException(status_code=401, detail="Manager not found")
            
            user = database["users"][manager_id]
            if user.role != UserRole.MANAGER:
                raise HTTPException(status_code=401, detail="Invalid manager token")
            
            return user
            
        elif token_type == "hr_auth":
            user_id = payload.get("user_id")
            if not user_id or user_id not in database["users"]:
                raise HTTPException(status_code=401, detail="HR user not found")
            
            user = database["users"][user_id]
            if user.role != UserRole.HR:
                raise HTTPException(status_code=401, detail="Invalid HR token")
            
            return user
        
        else:
            raise HTTPException(status_code=401, detail="Unsupported token type")
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401, 
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Authentication system error: {str(e)}"
        )

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:
    """Optional JWT token validation - returns None if no token provided"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        
        # Decode JWT token with proper secret key
        payload = jwt.decode(
            token, 
            os.getenv("JWT_SECRET_KEY", "fallback-secret"), 
            algorithms=["HS256"]
        )
        
        # Validate token structure
        token_type = payload.get("token_type")
        if not token_type:
            return None
        
        # Handle different token types with proper validation
        if token_type == "manager_auth":
            manager_id = payload.get("manager_id")
            if not manager_id or manager_id not in database["users"]:
                return None
            
            user = database["users"][manager_id]
            if user.role != UserRole.MANAGER:
                return None
            
            return user
            
        elif token_type == "hr_auth":
            user_id = payload.get("user_id")
            if not user_id or user_id not in database["users"]:
                return None
            
            user = database["users"][user_id]
            if user.role != UserRole.HR:
                return None
            
            return user
        
        else:
            return None
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    except Exception as e:
        logger.error(f"Optional authentication error: {str(e)}")
        return None

# Role-based access control decorators
def require_hr_role(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires HR role"""
    if current_user.role != UserRole.HR:
        raise HTTPException(
            status_code=403, 
            detail="HR access required. Current role: " + current_user.role.value
        )
    return current_user

def require_manager_role(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires Manager role"""
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=403, 
            detail="Manager access required. Current role: " + current_user.role.value
        )
    return current_user

# Application status tracking helper
def track_application_status_change(
    application_id: str,
    old_status: ApplicationStatus,
    new_status: ApplicationStatus,
    changed_by: str,
    reason: Optional[str] = None,
    notes: Optional[str] = None
):
    """Track application status changes for history"""
    status_change_id = str(uuid.uuid4())
    status_change = ApplicationStatusChange(
        id=status_change_id,
        application_id=application_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        changed_at=datetime.now(timezone.utc),
        reason=reason,
        notes=notes
    )
    database["application_status_history"][status_change_id] = status_change
    return status_change

def require_hr_or_manager_role(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires HR or Manager role"""
    if current_user.role not in [UserRole.HR, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403, 
            detail="HR or Manager access required. Current role: " + current_user.role.value
        )
    return current_user

def require_property_access(current_user: User = Depends(get_current_user)):
    """Dependency that validates property access for managers"""
    def check_property_access(property_id: str) -> User:
        if current_user.role == UserRole.HR:
            return current_user  # HR has access to all properties
        elif current_user.role == UserRole.MANAGER:
            if not current_user.property_id:
                raise HTTPException(status_code=403, detail="Manager not assigned to any property")
            if current_user.property_id != property_id:
                raise HTTPException(status_code=403, detail="Access denied to this property")
            return current_user
        else:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return check_property_access

def get_onboarding_session(token: str) -> OnboardingSession:
    """Get onboarding session from secure token"""
    result = token_manager.verify_onboarding_token(token)
    
    if not result.get("valid"):
        error_code = result.get("error_code", "INVALID_TOKEN")
        if error_code == "TOKEN_EXPIRED":
            raise HTTPException(status_code=401, detail="Onboarding link has expired")
        else:
            raise HTTPException(status_code=401, detail="Invalid onboarding link")
    
    employee_id = result["employee_id"]
    
    # Find active session for this employee
    for session in database["onboarding_sessions"].values():
        if (session.employee_id == employee_id and 
            session.status in [OnboardingStatus.IN_PROGRESS, OnboardingStatus.EMPLOYEE_COMPLETED]):
            return session
    
    raise HTTPException(status_code=404, detail="Active onboarding session not found")

# Health Check
@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc),
        "version": "2.0.0"
    }

# Public Property Info Endpoint (No Authentication Required)
@app.get("/properties/{property_id}/info")
async def get_property_public_info(property_id: str):
    """Get basic property information for job application form (public access)"""
    
    # Check if property exists
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    # Check if property is active
    if not property_obj.is_active:
        raise HTTPException(status_code=404, detail="Property is not accepting applications")
    
    # Define available departments and positions based on hotel operations
    departments_and_positions = {
        "Front Desk": [
            "Front Desk Agent",
            "Night Auditor",
            "Guest Services Representative",
            "Concierge"
        ],
        "Housekeeping": [
            "Housekeeper",
            "Housekeeping Supervisor",
            "Laundry Attendant",
            "Public Area Attendant"
        ],
        "Food & Beverage": [
            "Server",
            "Bartender",
            "Host/Hostess",
            "Kitchen Staff",
            "Banquet Server"
        ],
        "Maintenance": [
            "Maintenance Technician",
            "Engineering Assistant",
            "Groundskeeper"
        ]
    }
    
    # Return basic property information needed for the application form
    return {
        "property": {
            "id": property_obj.id,
            "name": property_obj.name,
            "address": property_obj.address,
            "city": property_obj.city,
            "state": property_obj.state,
            "zip_code": property_obj.zip_code,
            "phone": property_obj.phone
        },
        "departments_and_positions": departments_and_positions,
        "application_url": f"/apply/{property_id}",
        "is_accepting_applications": True
    }

# Job Application Submission Endpoint (No Authentication Required)
@app.post("/apply/{property_id}")
async def submit_job_application(property_id: str, application_data: JobApplicationData):
    """Submit job application (public endpoint)"""
    
    # Validate property exists and is active
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    # Check if property is accepting applications
    if not property_obj.is_active:
        raise HTTPException(status_code=400, detail="Property is not currently accepting applications")
    
    # Validate department and position are available for this property
    departments_and_positions = {
        "Front Desk": [
            "Front Desk Agent",
            "Night Auditor", 
            "Guest Services Representative",
            "Concierge"
        ],
        "Housekeeping": [
            "Housekeeper",
            "Housekeeping Supervisor",
            "Laundry Attendant",
            "Public Area Attendant"
        ],
        "Food & Beverage": [
            "Server",
            "Bartender",
            "Host/Hostess",
            "Kitchen Staff",
            "Banquet Server"
        ],
        "Maintenance": [
            "Maintenance Technician",
            "Engineering Assistant",
            "Groundskeeper"
        ]
    }
    
    # Validate department exists
    if application_data.department not in departments_and_positions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid department. Available departments: {list(departments_and_positions.keys())}"
        )
    
    # Validate position exists in the department
    if application_data.position not in departments_and_positions[application_data.department]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid position for {application_data.department}. Available positions: {departments_and_positions[application_data.department]}"
        )
    
    # Check for duplicate applications (same email + property + position)
    existing_application = None
    for app in database["applications"].values():
        if (app.property_id == property_id and 
            app.applicant_data.get("email", "").lower() == application_data.email.lower() and
            app.position == application_data.position and
            app.status == ApplicationStatus.PENDING):
            existing_application = app
            break
    
    if existing_application:
        raise HTTPException(
            status_code=400,
            detail=f"You have already submitted an application for {application_data.position} at this property. Please wait for a response before applying again."
        )
    
    # Create application record
    application_id = str(uuid.uuid4())
    
    # Convert application data to dictionary format expected by JobApplication model
    applicant_data = {
        "first_name": application_data.first_name,
        "last_name": application_data.last_name,
        "email": application_data.email,
        "phone": application_data.phone,
        "address": application_data.address,
        "city": application_data.city,
        "state": application_data.state,
        "zip_code": application_data.zip_code,
        "work_authorized": application_data.work_authorized,
        "sponsorship_required": application_data.sponsorship_required,
        "start_date": application_data.start_date,
        "shift_preference": application_data.shift_preference,
        "employment_type": application_data.employment_type,
        "experience_years": application_data.experience_years,
        "hotel_experience": application_data.hotel_experience,
        "previous_employer": application_data.previous_employer,
        "reason_for_leaving": application_data.reason_for_leaving,
        "additional_comments": application_data.additional_comments
    }
    
    # Create JobApplication instance
    job_application = JobApplication(
        id=application_id,
        property_id=property_id,
        department=application_data.department,
        position=application_data.position,
        applicant_data=applicant_data,
        status=ApplicationStatus.PENDING,
        applied_at=datetime.now(timezone.utc)
    )
    
    # Store application in database
    database["applications"][application_id] = job_application
    
    # Return confirmation response
    return JobApplicationResponse(
        success=True,
        message="Your application has been submitted successfully!",
        application_id=application_id,
        property_name=property_obj.name,
        position_applied=f"{application_data.position} - {application_data.department}",
        next_steps="Our hiring team will review your application and contact you within 3-5 business days. Thank you for your interest in joining our team!"
    )

# Enhanced Authentication Endpoints
@app.post("/auth/login")
async def login(request: Request):
    """Enhanced login with proper JSON handling, password validation, and session management"""
    try:
        # Handle JSON request body with proper error handling
        try:
            body = await request.json()
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid JSON format in request body"
            )
        
        # Validate required fields
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")
        
        if not email or not password:
            raise HTTPException(
                status_code=400, 
                detail="Email and password are required"
            )
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise HTTPException(
                status_code=400, 
                detail="Invalid email format"
            )
        
        # Find user by email
        existing_user = None
        for user in database["users"].values():
            if user.email.lower() == email:
                existing_user = user
                break
        
        if not existing_user:
            raise HTTPException(
                status_code=401, 
                detail="Invalid email or password"
            )
        
        # Verify password
        if not password_manager.verify_user_password(email, password):
            raise HTTPException(
                status_code=401, 
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not existing_user.is_active:
            raise HTTPException(
                status_code=403, 
                detail="Account is deactivated. Please contact administrator."
            )
        
        # Generate appropriate JWT token based on role
        if existing_user.role == UserRole.MANAGER:
            if not existing_user.property_id:
                raise HTTPException(
                    status_code=403, 
                    detail="Manager account not properly configured. Please contact HR."
                )
            
            token_data = token_manager.create_manager_token(
                existing_user.id, 
                existing_user.property_id
            )
            
        elif existing_user.role == UserRole.HR:
            # Create HR auth token with extended expiration
            expire = datetime.now(timezone.utc) + timedelta(hours=24)
            payload = {
                "user_id": existing_user.id,
                "role": existing_user.role.value,
                "token_type": "hr_auth",
                "iat": datetime.now(timezone.utc),
                "exp": expire,
                "jti": str(uuid.uuid4())
            }
            
            token = jwt.encode(
                payload, 
                os.getenv("JWT_SECRET_KEY", "fallback-secret"), 
                algorithm="HS256"
            )
            
            token_data = {
                "token": token,
                "expires_at": expire,
                "token_id": payload["jti"]
            }
            
        else:
            raise HTTPException(
                status_code=403, 
                detail="Role not authorized for dashboard access"
            )
        
        # Update user's last login timestamp
        existing_user.updated_at = datetime.now(timezone.utc)
        
        # Prepare response with user information
        user_response = {
            "id": existing_user.id,
            "email": existing_user.email,
            "role": existing_user.role.value,
            "first_name": existing_user.first_name,
            "last_name": existing_user.last_name,
            "property_id": existing_user.property_id,
            "is_active": existing_user.is_active
        }
        
        # Add property information for managers
        if existing_user.role == UserRole.MANAGER and existing_user.property_id:
            property_obj = database["properties"].get(existing_user.property_id)
            if property_obj:
                user_response["property_name"] = property_obj.name
        
        return {
            "success": True,
            "token": token_data["token"],
            "user": user_response,
            "expires_at": token_data["expires_at"].isoformat(),
            "token_type": "Bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Login system error: {str(e)}"
        )

@app.post("/auth/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh JWT token for authenticated user"""
    try:
        # Generate new token based on user role
        if current_user.role == UserRole.MANAGER:
            if not current_user.property_id:
                raise HTTPException(
                    status_code=403, 
                    detail="Manager account not properly configured"
                )
            
            token_data = token_manager.create_manager_token(
                current_user.id, 
                current_user.property_id
            )
            
        elif current_user.role == UserRole.HR:
            expire = datetime.now(timezone.utc) + timedelta(hours=24)
            payload = {
                "user_id": current_user.id,
                "role": current_user.role.value,
                "token_type": "hr_auth",
                "iat": datetime.now(timezone.utc),
                "exp": expire,
                "jti": str(uuid.uuid4())
            }
            
            token = jwt.encode(
                payload, 
                os.getenv("JWT_SECRET_KEY", "fallback-secret"), 
                algorithm="HS256"
            )
            
            token_data = {
                "token": token,
                "expires_at": expire,
                "token_id": payload["jti"]
            }
        else:
            raise HTTPException(
                status_code=403, 
                detail="Token refresh not available for this role"
            )
        
        return {
            "success": True,
            "token": token_data["token"],
            "expires_at": token_data["expires_at"].isoformat(),
            "token_type": "Bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Token refresh failed: {str(e)}"
        )

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (token invalidation would be implemented with token blacklist in production)"""
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    user_info = {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "property_id": current_user.property_id,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }
    
    # Add property information for managers
    if current_user.role == UserRole.MANAGER and current_user.property_id:
        property_obj = database["properties"].get(current_user.property_id)
        if property_obj:
            user_info["property_name"] = property_obj.name
            user_info["property_address"] = f"{property_obj.address}, {property_obj.city}, {property_obj.state}"
    
    return user_info

@app.post("/secret/create-hr")
async def create_hr_user(email: EmailStr, password: str, secret_key: str):
    """Create HR user with secret key"""
    if secret_key != "hotel-admin-2025":
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    # Normalize email to lowercase
    email = email.lower()
    
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        role=UserRole.HR,
        created_at=datetime.now(timezone.utc)
    )
    database["users"][user_id] = user
    
    # Store password in password manager
    password_manager.store_password(email, password)
    
    return {"message": "HR user created successfully", "user": user}

# Property Management
@app.post("/hr/properties")
async def create_property(
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
    phone: str = Form(""),
    current_user: User = Depends(require_hr_role)
):
    """Create a new property (HR only)"""
    
    property_id = str(uuid.uuid4())
    
    try:
        # Generate QR code for the new property
        qr_data = qr_service.generate_qr_code(property_id)
        qr_code_url = qr_data["qr_code_url"]
    except Exception as e:
        # Fallback to basic URL if QR generation fails
        qr_code_url = f"http://localhost:3000/apply/{property_id}"
    
    property_obj = Property(
        id=property_id,
        name=name,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        phone=phone,
        qr_code_url=qr_code_url,
        created_at=datetime.now(timezone.utc)
    )
    
    database["properties"][property_id] = property_obj
    return property_obj

@app.get("/hr/properties")
async def get_properties(current_user: User = Depends(require_hr_role)):
    """Get all properties (HR only)"""
    return list(database["properties"].values())

@app.put("/hr/properties/{property_id}")
async def update_property(
    property_id: str,
    name: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
    phone: str = Form(""),
    current_user: User = Depends(require_hr_role)
):
    """Update an existing property (HR only)"""
    
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    # Update property fields
    property_obj.name = name
    property_obj.address = address
    property_obj.city = city
    property_obj.state = state
    property_obj.zip_code = zip_code
    property_obj.phone = phone
    
    return property_obj

@app.delete("/hr/properties/{property_id}")
async def delete_property(
    property_id: str,
    current_user: User = Depends(require_hr_role)
):
    """Delete a property (HR only)"""
    
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Check if property has active applications or employees
    active_applications = [app for app in database["applications"].values() 
                          if app.property_id == property_id and app.status == ApplicationStatus.PENDING]
    active_employees = [emp for emp in database["employees"].values() 
                       if emp.property_id == property_id]
    
    if active_applications or active_employees:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete property with active applications or employees"
        )
    
    # Remove property
    del database["properties"][property_id]
    
    return {"message": "Property deleted successfully"}

# Enhanced Manager Assignment APIs

@app.get("/hr/properties/{property_id}/managers")
async def get_property_managers(
    property_id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get all managers assigned to a property"""
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    # Check access for managers
    if current_user.role == UserRole.MANAGER:
        if current_user.id not in property_obj.manager_ids:
            raise HTTPException(status_code=403, detail="Access denied to this property")
    
    managers = []
    for manager_id in property_obj.manager_ids:
        if manager_id in database["users"]:
            manager = database["users"][manager_id]
            managers.append({
                "id": manager.id,
                "email": manager.email,
                "first_name": manager.first_name,
                "last_name": manager.last_name,
                "is_active": manager.is_active,
                "created_at": manager.created_at.isoformat()
            })
    
    return managers

@app.post("/hr/properties/{property_id}/managers")
async def assign_manager_to_property(
    property_id: str,
    manager_id: str = Form(...),
    current_user: User = Depends(require_hr_role)
):
    """Assign a manager to a property (HR only)"""
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    if manager_id not in database["users"]:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    manager = database["users"][manager_id]
    if manager.role != UserRole.MANAGER:
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    if not manager.is_active:
        raise HTTPException(status_code=400, detail="Cannot assign inactive manager")
    
    property_obj = database["properties"][property_id]
    
    # Check if manager is already assigned
    if manager_id in property_obj.manager_ids:
        return {
            "success": False,
            "message": "Manager is already assigned to this property"
        }
    
    # Add manager to property
    property_obj.manager_ids.append(manager_id)
    
    # Update manager's primary property assignment
    manager.property_id = property_id
    manager.updated_at = datetime.now(timezone.utc)
    
    return {
        "success": True,
        "message": "Manager assigned successfully",
        "manager": {
            "id": manager.id,
            "name": f"{manager.first_name} {manager.last_name}".strip(),
            "email": manager.email
        }
    }

@app.delete("/hr/properties/{property_id}/managers/{manager_id}")
async def remove_manager_from_property(
    property_id: str,
    manager_id: str,
    current_user: User = Depends(require_hr_role)
):
    """Remove a manager from a property (HR only)"""
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    if manager_id not in property_obj.manager_ids:
        raise HTTPException(status_code=404, detail="Manager not assigned to this property")
    
    # Remove manager from property
    property_obj.manager_ids.remove(manager_id)
    
    # Clear manager's property assignment if this was their primary property
    if manager_id in database["users"]:
        manager = database["users"][manager_id]
        if manager.property_id == property_id:
            manager.property_id = None
            manager.updated_at = datetime.now(timezone.utc)
    
    return {
        "success": True,
        "message": "Manager removed successfully",
        "property_id": property_id,
        "manager_id": manager_id
    }

@app.get("/hr/managers/unassigned")
async def get_unassigned_managers(current_user: User = Depends(require_hr_role)):
    """Get all managers not assigned to any property (HR only)"""
    unassigned_managers = []
    
    for user in database["users"].values():
        if (user.role == UserRole.MANAGER and 
            user.is_active and 
            not user.property_id):
            unassigned_managers.append({
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat()
            })
    
    return unassigned_managers

# Enhanced Property Management APIs

@app.get("/hr/properties/search")
async def search_properties(
    q: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    has_manager: Optional[bool] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Search and filter properties with advanced options"""
    properties = list(database["properties"].values())
    
    # For managers, only show their assigned properties
    if current_user.role == UserRole.MANAGER:
        properties = [p for p in properties if current_user.id in p.manager_ids]
    
    # Apply search query
    if q:
        q_lower = q.lower()
        properties = [
            p for p in properties
            if (q_lower in p.name.lower() or
                q_lower in p.address.lower() or
                q_lower in p.city.lower() or
                q_lower in p.state.lower())
        ]
    
    # Apply filters
    if city:
        properties = [p for p in properties if p.city.lower() == city.lower()]
    
    if state:
        properties = [p for p in properties if p.state.upper() == state.upper()]
    
    if has_manager is not None:
        if has_manager:
            properties = [p for p in properties if len(p.manager_ids) > 0]
        else:
            properties = [p for p in properties if len(p.manager_ids) == 0]
    
    if is_active is not None:
        properties = [p for p in properties if p.is_active == is_active]
    
    # Enrich with manager information
    enriched_properties = []
    for prop in properties:
        managers = []
        for manager_id in prop.manager_ids:
            if manager_id in database["users"]:
                manager = database["users"][manager_id]
                managers.append({
                    "id": manager.id,
                    "name": f"{manager.first_name} {manager.last_name}".strip(),
                    "email": manager.email
                })
        
        # Count employees and applications for this property
        employee_count = len([e for e in database["employees"].values() if e.property_id == prop.id])
        application_count = len([a for a in database["applications"].values() if a.property_id == prop.id])
        pending_applications = len([a for a in database["applications"].values() 
                                   if a.property_id == prop.id and a.status == ApplicationStatus.PENDING])
        
        enriched_prop = {
            "id": prop.id,
            "name": prop.name,
            "address": prop.address,
            "city": prop.city,
            "state": prop.state,
            "zip_code": prop.zip_code,
            "phone": prop.phone,
            "qr_code_url": prop.qr_code_url,
            "is_active": prop.is_active,
            "created_at": prop.created_at.isoformat(),
            "managers": managers,
            "stats": {
                "employee_count": employee_count,
                "application_count": application_count,
                "pending_applications": pending_applications
            }
        }
        enriched_properties.append(enriched_prop)
    
    # Sort by name
    enriched_properties.sort(key=lambda x: x["name"])
    
    return enriched_properties

@app.get("/hr/properties/{property_id}")
async def get_property_details(
    property_id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get detailed property information"""
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    # Check access for managers
    if current_user.role == UserRole.MANAGER:
        if current_user.id not in property_obj.manager_ids:
            raise HTTPException(status_code=403, detail="Access denied to this property")
    
    # Get managers
    managers = []
    for manager_id in property_obj.manager_ids:
        if manager_id in database["users"]:
            manager = database["users"][manager_id]
            managers.append({
                "id": manager.id,
                "name": f"{manager.first_name} {manager.last_name}".strip(),
                "email": manager.email,
                "is_active": manager.is_active
            })
    
    # Get employees
    employees = []
    for employee in database["employees"].values():
        if employee.property_id == property_id:
            user = database["users"].get(employee.user_id)
            employees.append({
                "id": employee.id,
                "name": f"{user.first_name} {user.last_name}".strip() if user else "Unknown",
                "email": user.email if user else "",
                "department": employee.department,
                "position": employee.position,
                "employment_status": employee.employment_status,
                "hire_date": employee.hire_date.isoformat()
            })
    
    # Get applications
    applications = []
    for app in database["applications"].values():
        if app.property_id == property_id:
            applications.append({
                "id": app.id,
                "applicant_name": f"{app.applicant_data.get('first_name', '')} {app.applicant_data.get('last_name', '')}".strip(),
                "position": app.position,
                "department": app.department,
                "status": app.status,
                "applied_at": app.applied_at.isoformat()
            })
    
    return {
        "id": property_obj.id,
        "name": property_obj.name,
        "address": property_obj.address,
        "city": property_obj.city,
        "state": property_obj.state,
        "zip_code": property_obj.zip_code,
        "phone": property_obj.phone,
        "qr_code_url": property_obj.qr_code_url,
        "is_active": property_obj.is_active,
        "created_at": property_obj.created_at.isoformat(),
        "managers": managers,
        "employees": employees,
        "applications": applications,
        "stats": {
            "manager_count": len(managers),
            "employee_count": len(employees),
            "application_count": len(applications),
            "pending_applications": len([a for a in applications if a["status"] == "pending"])
        }
    }

@app.post("/hr/properties/{property_id}/qr-code")
async def regenerate_qr_code(
    property_id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Generate QR code for property job applications (HR + Manager access)"""
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    # Check manager access - managers can only generate QR codes for their assigned properties
    if current_user.role == UserRole.MANAGER:
        if current_user.id not in property_obj.manager_ids:
            raise HTTPException(
                status_code=403, 
                detail="Access denied. Managers can only generate QR codes for their assigned properties."
            )
    
    try:
        # Generate QR code using the QR service
        qr_data = qr_service.generate_qr_code(property_id)
        
        # Generate printable version as well
        printable_qr_data = qr_service.generate_printable_qr_code(property_id, property_obj.name)
        
        # Update property with new QR code URL
        property_obj.qr_code_url = qr_data["qr_code_url"]
        
        return {
            "success": True,
            "property_id": property_id,
            "property_name": property_obj.name,
            "qr_code_url": qr_data["qr_code_url"],
            "printable_qr_url": printable_qr_data["printable_qr_url"],
            "application_url": qr_data["application_url"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": current_user.id,
            "qr_code_size": qr_data["size"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate QR code: {str(e)}"
        )

@app.post("/hr/properties/{property_id}/activate")
async def activate_property(
    property_id: str,
    current_user: User = Depends(require_hr_role)
):
    """Activate a property (HR only)"""
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    property_obj.is_active = True
    
    return {
        "success": True,
        "message": "Property activated successfully",
        "property_id": property_id
    }

@app.post("/hr/properties/{property_id}/deactivate")
async def deactivate_property(
    property_id: str,
    current_user: User = Depends(require_hr_role)
):
    """Deactivate a property (HR only)"""
    if property_id not in database["properties"]:
        raise HTTPException(status_code=404, detail="Property not found")
    
    property_obj = database["properties"][property_id]
    
    # Check for active applications
    active_applications = [
        app for app in database["applications"].values()
        if app.property_id == property_id and app.status == ApplicationStatus.PENDING
    ]
    
    if active_applications:
        return {
            "success": False,
            "message": f"Cannot deactivate property with {len(active_applications)} pending applications",
            "pending_applications": len(active_applications)
        }
    
    property_obj.is_active = False
    
    return {
        "success": True,
        "message": "Property deactivated successfully",
        "property_id": property_id
    }

# Enhanced Employee Management APIs
@app.get("/hr/employees")
async def get_employees(
    property_id: Optional[str] = None,
    department: Optional[str] = None,
    employment_status: Optional[str] = None,
    onboarding_status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get employees with comprehensive filtering and search"""
    employees = list(database["employees"].values())
    
    # For managers, only show employees from their property
    if current_user.role == UserRole.MANAGER:
        if not current_user.property_id:
            raise HTTPException(status_code=400, detail="Manager not assigned to property")
        employees = [emp for emp in employees if emp.property_id == current_user.property_id]
    elif property_id:  # HR can filter by property
        employees = [emp for emp in employees if emp.property_id == property_id]
    
    # Apply filters
    if department:
        employees = [emp for emp in employees if emp.department.lower() == department.lower()]
    
    if employment_status:
        employees = [emp for emp in employees if emp.employment_status == employment_status]
    
    if onboarding_status:
        employees = [emp for emp in employees if emp.onboarding_status == onboarding_status]
    
    # Apply search
    if search:
        search_lower = search.lower()
        filtered_employees = []
        for emp in employees:
            user = database["users"].get(emp.user_id)
            if user:
                if (search_lower in user.email.lower() or
                    search_lower in (user.first_name or "").lower() or
                    search_lower in (user.last_name or "").lower() or
                    search_lower in emp.department.lower() or
                    search_lower in emp.position.lower()):
                    filtered_employees.append(emp)
        employees = filtered_employees
    
    # Enrich with user and property information
    enriched_employees = []
    for emp in employees:
        user = database["users"].get(emp.user_id)
        property_obj = database["properties"].get(emp.property_id)
        manager = database["users"].get(emp.manager_id)
        
        if user:  # Only include if user exists
            enriched_emp = {
                "id": emp.id,
                "user_id": emp.user_id,
                "employee_number": emp.employee_number,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "department": emp.department,
                "position": emp.position,
                "hire_date": emp.hire_date.isoformat(),
                "start_date": emp.start_date.isoformat() if emp.start_date else None,
                "employment_status": emp.employment_status,
                "onboarding_status": emp.onboarding_status,
                "pay_rate": emp.pay_rate,
                "pay_frequency": emp.pay_frequency,
                "employment_type": emp.employment_type,
                "property": {
                    "id": property_obj.id,
                    "name": property_obj.name
                } if property_obj else None,
                "manager": {
                    "id": manager.id,
                    "name": f"{manager.first_name} {manager.last_name}".strip(),
                    "email": manager.email
                } if manager else None,
                "created_at": emp.created_at.isoformat(),
                "onboarding_completed_at": emp.onboarding_completed_at.isoformat() if emp.onboarding_completed_at else None
            }
            enriched_employees.append(enriched_emp)
    
    # Sort by hire date (newest first)
    enriched_employees.sort(key=lambda x: x["hire_date"], reverse=True)
    
    return enriched_employees

@app.get("/hr/employees/{employee_id}")
async def get_employee_details(
    employee_id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get detailed employee information"""
    if employee_id not in database["employees"]:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = database["employees"][employee_id]
    
    # Check access for managers
    if current_user.role == UserRole.MANAGER:
        if current_user.property_id != employee.property_id:
            raise HTTPException(status_code=403, detail="Access denied to this employee")
    
    # Get user information
    user = database["users"].get(employee.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Employee user record not found")
    
    # Get property information
    property_obj = database["properties"].get(employee.property_id)
    
    # Get manager information
    manager = database["users"].get(employee.manager_id)
    
    # Get onboarding session if exists
    onboarding_session = None
    for session in database["onboarding_sessions"].values():
        if session.employee_id == employee_id:
            onboarding_session = {
                "id": session.id,
                "status": session.status,
                "current_step": session.current_step,
                "progress_percentage": session.progress_percentage,
                "created_at": session.created_at.isoformat(),
                "employee_completed_at": session.employee_completed_at.isoformat() if session.employee_completed_at else None,
                "approved_at": session.approved_at.isoformat() if session.approved_at else None
            }
            break
    
    return {
        "id": employee.id,
        "user_id": employee.user_id,
        "employee_number": employee.employee_number,
        "application_id": employee.application_id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": f"{user.first_name} {user.last_name}".strip(),
        "department": employee.department,
        "position": employee.position,
        "hire_date": employee.hire_date.isoformat(),
        "start_date": employee.start_date.isoformat() if employee.start_date else None,
        "employment_status": employee.employment_status,
        "onboarding_status": employee.onboarding_status,
        "pay_rate": employee.pay_rate,
        "pay_frequency": employee.pay_frequency,
        "employment_type": employee.employment_type,
        "personal_info": employee.personal_info,
        "emergency_contacts": employee.emergency_contacts,
        "property": {
            "id": property_obj.id,
            "name": property_obj.name,
            "address": f"{property_obj.address}, {property_obj.city}, {property_obj.state}"
        } if property_obj else None,
        "manager": {
            "id": manager.id,
            "name": f"{manager.first_name} {manager.last_name}".strip(),
            "email": manager.email
        } if manager else None,
        "onboarding_session": onboarding_session,
        "created_at": employee.created_at.isoformat(),
        "updated_at": employee.updated_at.isoformat() if employee.updated_at else None,
        "onboarding_completed_at": employee.onboarding_completed_at.isoformat() if employee.onboarding_completed_at else None
    }

@app.get("/hr/employees/search")
async def search_employees(
    q: str,
    property_id: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Search employees by name, email, or employee number"""
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    employees = list(database["employees"].values())
    
    # For managers, only search within their property
    if current_user.role == UserRole.MANAGER:
        if not current_user.property_id:
            raise HTTPException(status_code=400, detail="Manager not assigned to property")
        employees = [emp for emp in employees if emp.property_id == current_user.property_id]
    elif property_id:  # HR can filter by property
        employees = [emp for emp in employees if emp.property_id == property_id]
    
    # Perform search
    search_lower = q.lower().strip()
    search_results = []
    
    for emp in employees:
        user = database["users"].get(emp.user_id)
        if not user:
            continue
        
        # Calculate relevance score
        score = 0
        
        # Exact matches get highest score
        if search_lower == user.email.lower():
            score += 100
        elif search_lower == emp.employee_number:
            score += 100
        elif search_lower == f"{user.first_name} {user.last_name}".lower():
            score += 90
        
        # Partial matches
        if search_lower in user.email.lower():
            score += 50
        if search_lower in (user.first_name or "").lower():
            score += 40
        if search_lower in (user.last_name or "").lower():
            score += 40
        if search_lower in emp.department.lower():
            score += 30
        if search_lower in emp.position.lower():
            score += 30
        if emp.employee_number and search_lower in emp.employee_number.lower():
            score += 60
        
        if score > 0:
            property_obj = database["properties"].get(emp.property_id)
            search_results.append({
                "id": emp.id,
                "employee_number": emp.employee_number,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "email": user.email,
                "department": emp.department,
                "position": emp.position,
                "employment_status": emp.employment_status,
                "property_name": property_obj.name if property_obj else "Unknown",
                "relevance_score": score
            })
    
    # Sort by relevance score (highest first)
    search_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Apply limit
    return search_results[:limit]

@app.put("/hr/employees/{employee_id}/status")
async def update_employee_status(
    employee_id: str,
    employment_status: Optional[str] = Form(None),
    onboarding_status: Optional[str] = Form(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Update employee employment or onboarding status"""
    if employee_id not in database["employees"]:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee = database["employees"][employee_id]
    
    # Check access for managers
    if current_user.role == UserRole.MANAGER:
        if current_user.property_id != employee.property_id:
            raise HTTPException(status_code=403, detail="Access denied to this employee")
    
    changes_made = []
    
    # Update employment status
    if employment_status:
        valid_employment_statuses = ["active", "on_leave", "terminated", "resigned"]
        if employment_status not in valid_employment_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid employment status. Must be one of: {valid_employment_statuses}"
            )
        
        if employee.employment_status != employment_status:
            old_status = employee.employment_status
            employee.employment_status = employment_status
            changes_made.append(f"Employment status changed from {old_status} to {employment_status}")
    
    # Update onboarding status (managers can only update certain statuses)
    if onboarding_status:
        valid_onboarding_statuses = [status.value for status in OnboardingStatus]
        if onboarding_status not in valid_onboarding_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid onboarding status. Must be one of: {valid_onboarding_statuses}"
            )
        
        # Managers can only approve/reject completed onboarding
        if current_user.role == UserRole.MANAGER:
            allowed_manager_statuses = ["approved", "rejected"]
            if onboarding_status not in allowed_manager_statuses:
                raise HTTPException(
                    status_code=403, 
                    detail="Managers can only approve or reject completed onboarding"
                )
        
        if employee.onboarding_status != onboarding_status:
            old_status = employee.onboarding_status
            employee.onboarding_status = onboarding_status
            changes_made.append(f"Onboarding status changed from {old_status} to {onboarding_status}")
            
            # Set completion timestamp if approved
            if onboarding_status == "approved":
                employee.onboarding_completed_at = datetime.now(timezone.utc)
    
    # Update timestamp
    employee.updated_at = datetime.now(timezone.utc)
    
    return {
        "success": True,
        "message": f"Employee status updated. Changes: {', '.join(changes_made) if changes_made else 'No changes made'}",
        "employee_id": employee_id,
        "changes": changes_made,
        "current_status": {
            "employment_status": employee.employment_status,
            "onboarding_status": employee.onboarding_status
        }
    }

@app.get("/hr/employees/stats")
async def get_employee_statistics(
    property_id: Optional[str] = None,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get employee statistics and metrics"""
    employees = list(database["employees"].values())
    
    # Filter by property for managers
    if current_user.role == UserRole.MANAGER:
        if not current_user.property_id:
            raise HTTPException(status_code=400, detail="Manager not assigned to property")
        employees = [emp for emp in employees if emp.property_id == current_user.property_id]
    elif property_id:  # HR can filter by property
        employees = [emp for emp in employees if emp.property_id == property_id]
    
    # Calculate statistics
    total_employees = len(employees)
    
    # Employment status breakdown
    employment_stats = {}
    for status in ["active", "on_leave", "terminated", "resigned"]:
        employment_stats[status] = len([e for e in employees if e.employment_status == status])
    
    # Onboarding status breakdown
    onboarding_stats = {}
    for status in OnboardingStatus:
        onboarding_stats[status.value] = len([e for e in employees if e.onboarding_status == status.value])
    
    # Department breakdown
    department_stats = {}
    for emp in employees:
        dept = emp.department
        department_stats[dept] = department_stats.get(dept, 0) + 1
    
    # Recent hires (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.now(timezone.utc).date() - timedelta(days=30)
    recent_hires = len([e for e in employees if e.hire_date >= thirty_days_ago])
    
    # Average pay rate by department
    pay_stats = {}
    for dept in department_stats.keys():
        dept_employees = [e for e in employees if e.department == dept and e.pay_rate]
        if dept_employees:
            avg_pay = sum(e.pay_rate for e in dept_employees) / len(dept_employees)
            pay_stats[dept] = round(avg_pay, 2)
    
    return {
        "total_employees": total_employees,
        "employment_status": employment_stats,
        "onboarding_status": onboarding_stats,
        "department_breakdown": department_stats,
        "recent_hires_30_days": recent_hires,
        "average_pay_by_department": pay_stats,
        "property_filter": property_id if current_user.role == UserRole.HR else current_user.property_id
    }

@app.get("/hr/users")
async def get_users(current_user: User = Depends(require_hr_role)):
    """Get all users (HR only)"""
    return list(database["users"].values())

# Dashboard Stats Endpoint
@app.get("/hr/dashboard-stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Get dashboard statistics for HR"""
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Only HR can access dashboard stats")
    
    total_properties = len([p for p in database["properties"].values() if p.is_active])
    total_managers = len([u for u in database["users"].values() if u.role == UserRole.MANAGER and u.is_active])
    total_employees = len([u for u in database["users"].values() if u.role == UserRole.EMPLOYEE and u.is_active])
    pending_applications = len([a for a in database["applications"].values() if a.status == ApplicationStatus.PENDING])
    
    return {
        "totalProperties": total_properties,
        "totalManagers": total_managers,
        "totalEmployees": total_employees,
        "pendingApplications": pending_applications
    }

# Enhanced Application Management APIs
@app.get("/hr/applications")
async def get_applications(
    property_id: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    position: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "applied_at",
    sort_order: Optional[str] = "desc",
    limit: Optional[int] = None,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get applications with advanced filtering, search, and sorting"""
    applications = list(database["applications"].values())
    
    # Filter by property for managers
    if current_user.role == UserRole.MANAGER:
        if not current_user.property_id:
            raise HTTPException(status_code=400, detail="Manager not assigned to property")
        applications = [app for app in applications if app.property_id == current_user.property_id]
    elif property_id:  # HR can filter by property
        applications = [app for app in applications if app.property_id == property_id]
    
    # Apply filters
    if status:
        applications = [app for app in applications if app.status == status]
    
    if department:
        applications = [app for app in applications if app.department.lower() == department.lower()]
    
    if position:
        applications = [app for app in applications if app.position.lower() == position.lower()]
    
    # Date range filtering
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            applications = [app for app in applications if app.applied_at >= from_date]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format. Use ISO format.")
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            applications = [app for app in applications if app.applied_at <= to_date]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format. Use ISO format.")
    
    # Apply search
    if search:
        search_lower = search.lower()
        applications = [
            app for app in applications
            if (search_lower in app.applicant_data.get("first_name", "").lower() or
                search_lower in app.applicant_data.get("last_name", "").lower() or
                search_lower in app.applicant_data.get("email", "").lower() or
                search_lower in app.applicant_data.get("phone", "").lower() or
                search_lower in app.position.lower() or
                search_lower in app.department.lower())
        ]
    
    # Enrich with property and reviewer information
    enriched_applications = []
    for app in applications:
        property_obj = database["properties"].get(app.property_id)
        reviewer = database["users"].get(app.reviewed_by) if app.reviewed_by else None
        
        # Calculate days since application
        days_since_applied = (datetime.now(timezone.utc) - app.applied_at).days
        
        enriched_app = {
            "id": app.id,
            "property_id": app.property_id,
            "property_name": property_obj.name if property_obj else "Unknown Property",
            "department": app.department,
            "position": app.position,
            "applicant_name": f"{app.applicant_data.get('first_name', '')} {app.applicant_data.get('last_name', '')}".strip(),
            "applicant_email": app.applicant_data.get("email", ""),
            "applicant_phone": app.applicant_data.get("phone", ""),
            "status": app.status,
            "applied_at": app.applied_at.isoformat(),
            "days_since_applied": days_since_applied,
            "reviewed_by": f"{reviewer.first_name} {reviewer.last_name}" if reviewer else None,
            "reviewed_by_id": app.reviewed_by,
            "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
            "rejection_reason": app.rejection_reason,
            "talent_pool_date": app.talent_pool_date.isoformat() if app.talent_pool_date else None,
            "applicant_data": app.applicant_data,
            "priority": "high" if days_since_applied > 7 and app.status == "pending" else "normal"
        }
        enriched_applications.append(enriched_app)
    
    # Apply sorting
    valid_sort_fields = ["applied_at", "applicant_name", "position", "department", "status", "days_since_applied"]
    if sort_by not in valid_sort_fields:
        sort_by = "applied_at"
    
    reverse_sort = sort_order.lower() == "desc"
    
    if sort_by == "applied_at":
        enriched_applications.sort(key=lambda x: x["applied_at"], reverse=reverse_sort)
    elif sort_by == "applicant_name":
        enriched_applications.sort(key=lambda x: x["applicant_name"], reverse=reverse_sort)
    elif sort_by == "days_since_applied":
        enriched_applications.sort(key=lambda x: x["days_since_applied"], reverse=reverse_sort)
    else:
        enriched_applications.sort(key=lambda x: x[sort_by], reverse=reverse_sort)
    
    # Apply limit
    if limit and limit > 0:
        enriched_applications = enriched_applications[:limit]
    
    return enriched_applications

# Talent Pool Management Endpoints (must come before parameterized routes)
@app.get("/hr/applications/talent-pool")
async def get_talent_pool_applications(
    property_id: Optional[str] = None,
    position: Optional[str] = None,
    department: Optional[str] = None,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get applications in talent pool with filtering options"""
    print(f"DEBUG: talent-pool endpoint called by user {current_user.id}")
    talent_pool_apps = []
    
    for app in database["applications"].values():
        if app.status != ApplicationStatus.TALENT_POOL:
            continue
        
        # Access control
        if current_user.role == UserRole.MANAGER:
            if current_user.property_id != app.property_id:
                continue
        
        # Apply filters
        if property_id and app.property_id != property_id:
            continue
        if position and app.position != position:
            continue
        if department and app.department != department:
            continue
        
        # Add property name for display
        property_obj = database["properties"].get(app.property_id)
        app_data = {
            "id": app.id,
            "property_id": app.property_id,
            "property_name": property_obj.name if property_obj else "Unknown Property",
            "department": app.department,
            "position": app.position,
            "applicant_data": app.applicant_data,
            "applied_at": app.applied_at.isoformat(),
            "talent_pool_date": app.talent_pool_date.isoformat() if app.talent_pool_date else None,
            "reviewed_by": app.reviewed_by,
            "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None
        }
        talent_pool_apps.append(app_data)
    
    # Sort by talent pool date (most recent first)
    talent_pool_apps.sort(key=lambda x: x["talent_pool_date"] or "", reverse=True)
    
    return {
        "success": True,
        "applications": talent_pool_apps,
        "total_count": len(talent_pool_apps)
    }

@app.post("/hr/applications/bulk-talent-pool")
async def bulk_move_to_talent_pool(
    application_ids: List[str],
    current_user: User = Depends(require_manager_role)
):
    """Bulk move applications to talent pool (Manager only)"""
    if not application_ids:
        raise HTTPException(status_code=400, detail="No application IDs provided")
    
    moved_count = 0
    errors = []
    current_time = datetime.now(timezone.utc)
    
    for app_id in application_ids:
        try:
            if app_id not in database["applications"]:
                errors.append(f"Application {app_id} not found")
                continue
            
            application = database["applications"][app_id]
            
            # Check access
            if current_user.property_id != application.property_id:
                errors.append(f"Access denied to application {app_id}")
                continue
            
            # Only move pending applications
            if application.status != ApplicationStatus.PENDING:
                errors.append(f"Application {app_id} is not pending (current status: {application.status})")
                continue
            
            # Move to talent pool
            application.status = ApplicationStatus.TALENT_POOL
            application.talent_pool_date = current_time
            application.reviewed_by = current_user.id
            application.reviewed_at = current_time
            moved_count += 1
            
            # Send talent pool notification email
            try:
                property_obj = database["properties"][application.property_id]
                manager_name = f"{current_user.first_name} {current_user.last_name}".strip()
                
                await email_service.send_talent_pool_notification(
                    applicant_email=application.applicant_data["email"],
                    applicant_name=f"{application.applicant_data['first_name']} {application.applicant_data['last_name']}".strip(),
                    property_name=property_obj.name,
                    position=application.position,
                    manager_name=manager_name,
                    manager_email=current_user.email
                )
            except Exception as email_error:
                # Log email error but don't fail the bulk operation
                print(f"Failed to send talent pool email for application {app_id}: {str(email_error)}")
            
        except Exception as e:
            errors.append(f"Error processing application {app_id}: {str(e)}")
    
    return {
        "success": True,
        "moved_count": moved_count,
        "total_requested": len(application_ids),
        "errors": errors,
        "message": f"Successfully moved {moved_count} applications to talent pool"
    }

@app.get("/hr/applications/{application_id}")
async def get_application_details(
    application_id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get detailed application information"""
    print(f"DEBUG: parameterized endpoint called with application_id={application_id}")
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    
    # Check access for managers
    if current_user.role == UserRole.MANAGER:
        if current_user.property_id != application.property_id:
            raise HTTPException(status_code=403, detail="Access denied to this application")
    
    # Get property information
    property_obj = database["properties"].get(application.property_id)
    
    # Get reviewer information
    reviewer = None
    if application.reviewed_by:
        reviewer_user = database["users"].get(application.reviewed_by)
        if reviewer_user:
            reviewer = {
                "id": reviewer_user.id,
                "name": f"{reviewer_user.first_name} {reviewer_user.last_name}".strip(),
                "email": reviewer_user.email
            }
    
    # Calculate application metrics
    days_since_applied = (datetime.now(timezone.utc) - application.applied_at).days
    
    return {
        "id": application.id,
        "property": {
            "id": property_obj.id,
            "name": property_obj.name,
            "address": f"{property_obj.address}, {property_obj.city}, {property_obj.state}"
        } if property_obj else None,
        "department": application.department,
        "position": application.position,
        "status": application.status,
        "applied_at": application.applied_at.isoformat(),
        "days_since_applied": days_since_applied,
        "reviewed_by": reviewer,
        "reviewed_at": application.reviewed_at.isoformat() if application.reviewed_at else None,
        "rejection_reason": application.rejection_reason,
        "applicant_data": application.applicant_data,
        "priority": "high" if days_since_applied > 7 and application.status == "pending" else "normal"
    }

@app.post("/hr/applications/{application_id}/approve")
async def approve_application_enhanced(
    application_id: str,
    job_offer_data: JobOfferData = None,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Enhanced application approval with talent pool logic (Manager only)"""
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    
    # Check access - HR can access all applications, managers only their property
    if current_user.role == UserRole.MANAGER and current_user.property_id != application.property_id:
        raise HTTPException(status_code=403, detail="Access denied to this application")
    
    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Application is not pending")
    
    # If no job offer data provided, create default job offer
    if job_offer_data is None:
        job_offer_data = JobOfferData(
            job_title=application.position,
            start_date=datetime.now().date() + timedelta(days=7),  # Default start date
            pay_rate=15.0,  # Default pay rate
            pay_frequency="hourly",
            employment_type="full_time",
            supervisor=f"{current_user.first_name} {current_user.last_name}".strip() or "Manager"
        )
    
    # Validate start date is not in the past
    if job_offer_data.start_date < datetime.now().date():
        raise HTTPException(status_code=400, detail="Start date cannot be in the past")
    
    # Track status change
    old_status = application.status
    track_application_status_change(
        application_id=application_id,
        old_status=old_status,
        new_status=ApplicationStatus.APPROVED,
        changed_by=current_user.id,
        reason="Application approved with job offer",
        notes=f"Job offer: {job_offer_data.job_title} at ${job_offer_data.pay_rate}/hour"
    )
    
    # Update application status to approved
    application.status = ApplicationStatus.APPROVED
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.now(timezone.utc)
    
    # Create employee record
    employee_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    # Create user account for employee
    employee_user = User(
        id=user_id,
        email=application.applicant_data["email"],
        first_name=application.applicant_data["first_name"],
        last_name=application.applicant_data["last_name"],
        role=UserRole.EMPLOYEE,
        property_id=application.property_id,
        created_at=datetime.now(timezone.utc)
    )
    database["users"][user_id] = employee_user
    
    # Create employee record
    employee = Employee(
        id=employee_id,
        user_id=user_id,
        application_id=application_id,
        property_id=application.property_id,
        manager_id=current_user.id,
        department=application.department,
        position=job_offer_data.job_title,
        hire_date=job_offer_data.start_date,
        start_date=job_offer_data.start_date,
        pay_rate=job_offer_data.pay_rate,
        pay_frequency=job_offer_data.pay_frequency,
        employment_type=job_offer_data.employment_type,
        employment_status="active",
        onboarding_status=OnboardingStatus.NOT_STARTED,
        created_at=datetime.now(timezone.utc)
    )
    database["employees"][employee_id] = employee
    
    # TALENT POOL LOGIC: Move other applications for same position to talent pool
    talent_pool_count = 0
    current_time = datetime.now(timezone.utc)
    
    for app_id, app in database["applications"].items():
        if (app_id != application_id and  # Don't affect the approved application
            app.property_id == application.property_id and  # Same property
            app.position == application.position and  # Same position
            app.status == ApplicationStatus.PENDING):  # Only pending applications
            
            # Move to talent pool
            app.status = ApplicationStatus.TALENT_POOL
            app.talent_pool_date = current_time
            app.reviewed_by = current_user.id
            app.reviewed_at = current_time
            talent_pool_count += 1
    
    # Generate onboarding token
    onboarding_token_data = token_manager.create_onboarding_token(employee_id, application_id)
    
    # Get property and manager information for email
    property_obj = database["properties"][application.property_id]
    manager_name = f"{current_user.first_name} {current_user.last_name}".strip()
    onboarding_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/onboarding/{onboarding_token_data['token']}"
    
    # Send approval notification email
    try:
        await email_service.send_approval_notification(
            applicant_email=application.applicant_data["email"],
            applicant_name=f"{application.applicant_data['first_name']} {application.applicant_data['last_name']}".strip(),
            property_name=property_obj.name,
            position=application.position,
            job_title=job_offer_data.job_title,
            start_date=job_offer_data.start_date.strftime("%B %d, %Y"),
            pay_rate=job_offer_data.pay_rate,
            onboarding_link=onboarding_link,
            manager_name=manager_name,
            manager_email=current_user.email
        )
    except Exception as e:
        # Log email error but don't fail the approval process
        print(f"Failed to send approval email: {str(e)}")
    
    # Send talent pool notifications for moved applications
    try:
        for app_id, app in database["applications"].items():
            if (app_id != application_id and 
                app.property_id == application.property_id and 
                app.position == application.position and 
                app.status == ApplicationStatus.TALENT_POOL and
                app.talent_pool_date == current_time):  # Only newly moved applications
                
                await email_service.send_talent_pool_notification(
                    applicant_email=app.applicant_data["email"],
                    applicant_name=f"{app.applicant_data['first_name']} {app.applicant_data['last_name']}".strip(),
                    property_name=property_obj.name,
                    position=app.position,
                    manager_name=manager_name,
                    manager_email=current_user.email
                )
    except Exception as e:
        # Log email error but don't fail the approval process
        print(f"Failed to send talent pool emails: {str(e)}")
    
    return {
        "success": True,
        "message": "Application approved successfully",
        "application_id": application_id,
        "employee_id": employee_id,
        "job_offer": {
            "job_title": job_offer_data.job_title,
            "start_date": job_offer_data.start_date.isoformat(),
            "pay_rate": job_offer_data.pay_rate,
            "pay_frequency": job_offer_data.pay_frequency,
            "benefits_eligible": job_offer_data.benefits_eligible,
            "supervisor": job_offer_data.supervisor,
            "employment_type": job_offer_data.employment_type
        },
        "onboarding": {
            "token": onboarding_token_data["token"],
            "expires_at": onboarding_token_data["expires_at"].isoformat(),
            "onboarding_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/onboarding/{onboarding_token_data['token']}"
        },
        "talent_pool": {
            "moved_to_talent_pool": talent_pool_count,
            "message": f"{talent_pool_count} other applications for {application.position} moved to talent pool"
        }
    }

@app.post("/hr/applications/{application_id}/reject")
async def reject_application(
    application_id: str,
    rejection_reason: str = Form(...),
    current_user: User = Depends(require_manager_role)
):
    """Reject application with reason (Manager only)"""
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    
    # Check access
    if current_user.property_id != application.property_id:
        raise HTTPException(status_code=403, detail="Access denied to this application")
    
    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Application is not pending")
    
    if not rejection_reason.strip():
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    
    # Track status change
    old_status = application.status
    track_application_status_change(
        application_id=application_id,
        old_status=old_status,
        new_status=ApplicationStatus.REJECTED,
        changed_by=current_user.id,
        reason=rejection_reason.strip(),
        notes="Application rejected by manager"
    )
    
    # Update application - Move to TALENT_POOL instead of REJECTED
    current_time = datetime.now(timezone.utc)
    application.status = ApplicationStatus.TALENT_POOL
    application.reviewed_by = current_user.id
    application.reviewed_at = current_time
    application.rejection_reason = rejection_reason.strip()
    application.talent_pool_date = current_time
    
    # Track status change to talent pool
    track_application_status_change(
        application_id=application_id,
        old_status=old_status,
        new_status=ApplicationStatus.TALENT_POOL,
        changed_by=current_user.id,
        reason=f"Rejected for current position: {rejection_reason.strip()}",
        notes="Application rejected but moved to talent pool for future opportunities"
    )
    
    # Get property and manager information for email
    property_obj = database["properties"][application.property_id]
    manager_name = f"{current_user.first_name} {current_user.last_name}".strip()
    
    # Send talent pool notification email instead of rejection email
    try:
        await email_service.send_talent_pool_notification(
            applicant_email=application.applicant_data["email"],
            applicant_name=f"{application.applicant_data['first_name']} {application.applicant_data['last_name']}".strip(),
            property_name=property_obj.name,
            position=application.position,
            manager_name=manager_name,
            manager_email=current_user.email
        )
    except Exception as e:
        # Log email error but don't fail the rejection process
        print(f"Failed to send talent pool email: {str(e)}")
    
    return {
        "success": True,
        "message": "Application rejected and moved to talent pool for future opportunities",
        "application_id": application_id,
        "rejection_reason": rejection_reason.strip(),
        "reviewed_by": f"{current_user.first_name} {current_user.last_name}".strip(),
        "reviewed_at": application.reviewed_at.isoformat(),
        "talent_pool_date": application.talent_pool_date.isoformat(),
        "status": "talent_pool",
        "talent_pool_message": "Candidate has been added to talent pool for future opportunities"
    }

@app.post("/hr/applications/{application_id}/reactivate")
async def reactivate_from_talent_pool(
    application_id: str,
    current_user: User = Depends(require_manager_role)
):
    """Reactivate application from talent pool back to pending status"""
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    
    # Check access
    if current_user.property_id != application.property_id:
        raise HTTPException(status_code=403, detail="Access denied to this application")
    
    if application.status != ApplicationStatus.TALENT_POOL:
        raise HTTPException(status_code=400, detail="Application is not in talent pool")
    
    # Reactivate application
    application.status = ApplicationStatus.PENDING
    application.talent_pool_date = None
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.now(timezone.utc)
    
    return {
        "success": True,
        "message": "Application reactivated successfully",
        "application_id": application_id,
        "new_status": ApplicationStatus.PENDING,
        "reactivated_by": f"{current_user.first_name} {current_user.last_name}".strip(),
        "reactivated_at": application.reviewed_at.isoformat()
    }

@app.get("/hr/applications/stats")
async def get_application_statistics(
    property_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get application statistics and metrics"""
    applications = list(database["applications"].values())
    
    # Filter by property for managers
    if current_user.role == UserRole.MANAGER:
        if not current_user.property_id:
            raise HTTPException(status_code=400, detail="Manager not assigned to property")
        applications = [app for app in applications if app.property_id == current_user.property_id]
    elif property_id:  # HR can filter by property
        applications = [app for app in applications if app.property_id == property_id]
    
    # Apply date filters
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            applications = [app for app in applications if app.applied_at >= from_date]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format")
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            applications = [app for app in applications if app.applied_at <= to_date]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format")
    
    # Calculate statistics
    total_applications = len(applications)
    
    # Status breakdown
    status_stats = {}
    for status in ApplicationStatus:
        status_stats[status.value] = len([a for a in applications if a.status == status.value])
    
    # Department breakdown
    department_stats = {}
    for app in applications:
        dept = app.department
        department_stats[dept] = department_stats.get(dept, 0) + 1
    
    # Position breakdown
    position_stats = {}
    for app in applications:
        pos = app.position
        position_stats[pos] = position_stats.get(pos, 0) + 1
    
    # Time-based metrics
    now = datetime.now(timezone.utc)
    
    # Applications by time period
    today = now.date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    
    time_stats = {
        "today": len([a for a in applications if a.applied_at.date() == today]),
        "this_week": len([a for a in applications if a.applied_at.date() >= this_week_start]),
        "this_month": len([a for a in applications if a.applied_at.date() >= this_month_start])
    }
    
    # Pending applications by age
    pending_apps = [a for a in applications if a.status == ApplicationStatus.PENDING]
    pending_by_age = {
        "0_3_days": len([a for a in pending_apps if (now - a.applied_at).days <= 3]),
        "4_7_days": len([a for a in pending_apps if 4 <= (now - a.applied_at).days <= 7]),
        "8_14_days": len([a for a in pending_apps if 8 <= (now - a.applied_at).days <= 14]),
        "over_14_days": len([a for a in pending_apps if (now - a.applied_at).days > 14])
    }
    
    # Approval rate
    reviewed_apps = [a for a in applications if a.status in [ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]]
    approved_apps = [a for a in applications if a.status == ApplicationStatus.APPROVED]
    
    approval_rate = 0
    if reviewed_apps:
        approval_rate = round((len(approved_apps) / len(reviewed_apps)) * 100, 1)
    
    # Average review time (for reviewed applications)
    avg_review_time_hours = 0
    if reviewed_apps:
        total_review_time = sum(
            (a.reviewed_at - a.applied_at).total_seconds() / 3600 
            for a in reviewed_apps if a.reviewed_at
        )
        avg_review_time_hours = round(total_review_time / len(reviewed_apps), 1)
    
    return {
        "total_applications": total_applications,
        "status_breakdown": status_stats,
        "department_breakdown": department_stats,
        "position_breakdown": position_stats,
        "time_periods": time_stats,
        "pending_by_age": pending_by_age,
        "approval_rate_percent": approval_rate,
        "average_review_time_hours": avg_review_time_hours,
        "property_filter": property_id if current_user.role == UserRole.HR else current_user.property_id
    }

@app.get("/hr/applications/departments")
async def get_application_departments(current_user: User = Depends(require_hr_or_manager_role)):
    """Get list of departments from applications"""
    applications = list(database["applications"].values())
    
    # Filter by property for managers
    if current_user.role == UserRole.MANAGER:
        if not current_user.property_id:
            raise HTTPException(status_code=400, detail="Manager not assigned to property")
        applications = [app for app in applications if app.property_id == current_user.property_id]
    
    departments = list(set(app.department for app in applications))
    departments.sort()
    
    return departments

@app.get("/hr/applications/positions")
async def get_application_positions(
    department: Optional[str] = None,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get list of positions from applications, optionally filtered by department"""
    applications = list(database["applications"].values())
    
    # Filter by property for managers
    if current_user.role == UserRole.MANAGER:
        if not current_user.property_id:
            raise HTTPException(status_code=400, detail="Manager not assigned to property")
        applications = [app for app in applications if app.property_id == current_user.property_id]
    
    # Filter by department if provided
    if department:
        applications = [app for app in applications if app.department.lower() == department.lower()]
    
    positions = list(set(app.position for app in applications))
    positions.sort()
    
    return positions

@app.post("/hr/applications/bulk-action")
async def bulk_application_action(
    application_ids: List[str] = Form(...),
    action: str = Form(...),
    rejection_reason: Optional[str] = Form(None),
    current_user: User = Depends(require_manager_role)
):
    """Perform bulk actions on multiple applications (Manager only)"""
    if not application_ids:
        raise HTTPException(status_code=400, detail="No application IDs provided")
    
    valid_actions = ["reject"]
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
    
    if action == "reject" and not rejection_reason:
        raise HTTPException(status_code=400, detail="Rejection reason required for reject action")
    
    results = []
    
    for app_id in application_ids:
        try:
            if app_id not in database["applications"]:
                results.append({"application_id": app_id, "success": False, "error": "Application not found"})
                continue
            
            application = database["applications"][app_id]
            
            # Check access
            if current_user.property_id != application.property_id:
                results.append({"application_id": app_id, "success": False, "error": "Access denied"})
                continue
            
            if application.status != ApplicationStatus.PENDING:
                results.append({"application_id": app_id, "success": False, "error": "Application not pending"})
                continue
            
            # Perform action
            if action == "reject":
                # Track status change
                old_status = application.status
                track_application_status_change(
                    application_id=app_id,
                    old_status=old_status,
                    new_status=ApplicationStatus.REJECTED,
                    changed_by=current_user.id,
                    reason=rejection_reason,
                    notes="Bulk rejection action"
                )
                
                application.status = ApplicationStatus.REJECTED
                application.reviewed_by = current_user.id
                application.reviewed_at = datetime.now(timezone.utc)
                application.rejection_reason = rejection_reason
                
                results.append({"application_id": app_id, "success": True, "action": "rejected"})
            
        except Exception as e:
            results.append({"application_id": app_id, "success": False, "error": str(e)})
    
    successful_count = len([r for r in results if r["success"]])
    
    return {
        "success": True,
        "message": f"Bulk action completed. {successful_count}/{len(application_ids)} applications processed successfully.",
        "action": action,
        "results": results,
        "summary": {
            "total_processed": len(application_ids),
            "successful": successful_count,
            "failed": len(application_ids) - successful_count
        }
    }

@app.post("/hr/applications/bulk-status-update")
async def bulk_status_update(
    application_ids: List[str] = Form(...),
    new_status: str = Form(...),
    reason: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Perform bulk status updates on multiple applications"""
    if not application_ids:
        raise HTTPException(status_code=400, detail="No application IDs provided")
    
    # Validate status
    try:
        target_status = ApplicationStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")
    
    results = []
    
    for app_id in application_ids:
        try:
            if app_id not in database["applications"]:
                results.append({"application_id": app_id, "success": False, "error": "Application not found"})
                continue
            
            application = database["applications"][app_id]
            
            # Check access permissions
            if current_user.role == UserRole.MANAGER and current_user.property_id != application.property_id:
                results.append({"application_id": app_id, "success": False, "error": "Access denied"})
                continue
            
            # Track status change
            old_status = application.status
            if old_status != target_status:
                track_application_status_change(
                    application_id=app_id,
                    old_status=old_status,
                    new_status=target_status,
                    changed_by=current_user.id,
                    reason=reason,
                    notes=notes
                )
                
                # Update application status
                application.status = target_status
                application.reviewed_by = current_user.id
                application.reviewed_at = datetime.now(timezone.utc)
                
                # Set specific fields based on status
                if target_status == ApplicationStatus.TALENT_POOL:
                    application.talent_pool_date = datetime.now(timezone.utc)
                elif target_status == ApplicationStatus.REJECTED and reason:
                    application.rejection_reason = reason
                
                results.append({"application_id": app_id, "success": True, "old_status": old_status.value, "new_status": target_status.value})
            else:
                results.append({"application_id": app_id, "success": True, "message": "Status unchanged"})
            
        except Exception as e:
            results.append({"application_id": app_id, "success": False, "error": str(e)})
    
    successful_count = len([r for r in results if r["success"]])
    
    return {
        "success": True,
        "message": f"Bulk status update completed. {successful_count}/{len(application_ids)} applications processed successfully.",
        "new_status": new_status,
        "results": results,
        "summary": {
            "total_processed": len(application_ids),
            "successful": successful_count,
            "failed": len(application_ids) - successful_count
        }
    }

@app.post("/hr/applications/bulk-talent-pool-notify")
async def bulk_talent_pool_notify(
    application_ids: List[str] = Form(...),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Send email notifications to talent pool candidates about new opportunities"""
    if not application_ids:
        raise HTTPException(status_code=400, detail="No application IDs provided")
    
    results = []
    
    for app_id in application_ids:
        try:
            if app_id not in database["applications"]:
                results.append({"application_id": app_id, "success": False, "error": "Application not found"})
                continue
            
            application = database["applications"][app_id]
            
            # Check access permissions
            if current_user.role == UserRole.MANAGER and current_user.property_id != application.property_id:
                results.append({"application_id": app_id, "success": False, "error": "Access denied"})
                continue
            
            # Only send notifications to talent pool candidates
            if application.status != ApplicationStatus.TALENT_POOL:
                results.append({"application_id": app_id, "success": False, "error": "Application not in talent pool"})
                continue
            
            # Get property information
            property_obj = database["properties"].get(application.property_id)
            if not property_obj:
                results.append({"application_id": app_id, "success": False, "error": "Property not found"})
                continue
            
            # Send talent pool notification email
            try:
                email_service.send_talent_pool_notification(
                    applicant_email=application.applicant_data.get("email"),
                    applicant_name=f"{application.applicant_data.get('first_name', '')} {application.applicant_data.get('last_name', '')}".strip(),
                    property_name=property_obj.name,
                    position=application.position,
                    department=application.department
                )
                results.append({"application_id": app_id, "success": True, "action": "email_sent"})
            except Exception as email_error:
                results.append({"application_id": app_id, "success": False, "error": f"Email failed: {str(email_error)}"})
            
        except Exception as e:
            results.append({"application_id": app_id, "success": False, "error": str(e)})
    
    successful_count = len([r for r in results if r["success"]])
    
    return {
        "success": True,
        "message": f"Bulk email notification completed. {successful_count}/{len(application_ids)} emails sent successfully.",
        "results": results,
        "summary": {
            "total_processed": len(application_ids),
            "successful": successful_count,
            "failed": len(application_ids) - successful_count
        }
    }

@app.post("/hr/applications/bulk-reactivate")
async def bulk_reactivate_applications(
    application_ids: List[str] = Form(...),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Reactivate talent pool candidates by moving them back to pending status"""
    if not application_ids:
        raise HTTPException(status_code=400, detail="No application IDs provided")
    
    results = []
    
    for app_id in application_ids:
        try:
            if app_id not in database["applications"]:
                results.append({"application_id": app_id, "success": False, "error": "Application not found"})
                continue
            
            application = database["applications"][app_id]
            
            # Check access permissions
            if current_user.role == UserRole.MANAGER and current_user.property_id != application.property_id:
                results.append({"application_id": app_id, "success": False, "error": "Access denied"})
                continue
            
            # Only reactivate talent pool candidates
            if application.status != ApplicationStatus.TALENT_POOL:
                results.append({"application_id": app_id, "success": False, "error": "Application not in talent pool"})
                continue
            
            # Track status change
            old_status = application.status
            track_application_status_change(
                application_id=app_id,
                old_status=old_status,
                new_status=ApplicationStatus.PENDING,
                changed_by=current_user.id,
                reason="Reactivated from talent pool",
                notes="Candidate reactivated for new opportunity consideration"
            )
            
            # Update application status
            application.status = ApplicationStatus.PENDING
            application.reviewed_by = current_user.id
            application.reviewed_at = datetime.now(timezone.utc)
            application.talent_pool_date = None  # Clear talent pool date
            
            results.append({"application_id": app_id, "success": True, "action": "reactivated"})
            
        except Exception as e:
            results.append({"application_id": app_id, "success": False, "error": str(e)})
    
    successful_count = len([r for r in results if r["success"]])
    
    return {
        "success": True,
        "message": f"Bulk reactivation completed. {successful_count}/{len(application_ids)} applications reactivated successfully.",
        "results": results,
        "summary": {
            "total_processed": len(application_ids),
            "successful": successful_count,
            "failed": len(application_ids) - successful_count
        }
    }

@app.get("/hr/applications/{application_id}/history")
async def get_application_history(
    application_id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get status change history for a specific application"""
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    
    # Check access permissions
    if current_user.role == UserRole.MANAGER and current_user.property_id != application.property_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get status history for this application
    history = []
    for status_change in database["application_status_history"].values():
        if status_change.application_id == application_id:
            # Get user info for who made the change
            changed_by_user = database["users"].get(status_change.changed_by)
            changed_by_name = "Unknown User"
            if changed_by_user:
                changed_by_name = f"{changed_by_user.first_name} {changed_by_user.last_name}".strip()
                if not changed_by_name:
                    changed_by_name = changed_by_user.email
            
            history.append({
                "id": status_change.id,
                "old_status": status_change.old_status.value,
                "new_status": status_change.new_status.value,
                "changed_by": changed_by_name,
                "changed_by_id": status_change.changed_by,
                "changed_at": status_change.changed_at.isoformat(),
                "reason": status_change.reason,
                "notes": status_change.notes
            })
    
    # Sort by timestamp, most recent first
    history.sort(key=lambda x: x["changed_at"], reverse=True)
    
    return {
        "application_id": application_id,
        "current_status": application.status.value,
        "history": history
    }

# Enhanced Manager Management APIs
@app.get("/hr/managers")
async def get_managers(
    property_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_hr_role)
):
    """Get all managers with filtering and search capabilities (HR only)"""
    managers = []
    
    for user in database["users"].values():
        if user.role == UserRole.MANAGER:
            # Apply filters
            if property_id and user.property_id != property_id:
                continue
            
            if is_active is not None and user.is_active != is_active:
                continue
            
            # Apply search
            if search:
                search_lower = search.lower()
                if not (search_lower in user.email.lower() or
                       search_lower in (user.first_name or "").lower() or
                       search_lower in (user.last_name or "").lower()):
                    continue
            
            # Get property information
            property_info = None
            if user.property_id and user.property_id in database["properties"]:
                property_obj = database["properties"][user.property_id]
                property_info = {
                    "id": property_obj.id,
                    "name": property_obj.name,
                    "address": f"{property_obj.address}, {property_obj.city}, {property_obj.state}"
                }
            
            # Calculate performance metrics
            if user.property_id:
                # Applications reviewed by this manager
                reviewed_apps = [
                    app for app in database["applications"].values()
                    if app.reviewed_by == user.id
                ]
                
                # Employees managed
                managed_employees = [
                    emp for emp in database["employees"].values()
                    if emp.manager_id == user.id
                ]
                
                performance_stats = {
                    "applications_reviewed": len(reviewed_apps),
                    "applications_approved": len([a for a in reviewed_apps if a.status == ApplicationStatus.APPROVED]),
                    "applications_rejected": len([a for a in reviewed_apps if a.status == ApplicationStatus.REJECTED]),
                    "employees_managed": len(managed_employees),
                    "active_employees": len([e for e in managed_employees if e.employment_status == "active"])
                }
            else:
                performance_stats = {
                    "applications_reviewed": 0,
                    "applications_approved": 0,
                    "applications_rejected": 0,
                    "employees_managed": 0,
                    "active_employees": 0
                }
            
            manager_data = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "property": property_info,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "performance": performance_stats
            }
            
            managers.append(manager_data)
    
    # Sort by name
    managers.sort(key=lambda x: x["full_name"])
    
    return managers

@app.get("/hr/managers/{manager_id}")
async def get_manager_details(
    manager_id: str,
    current_user: User = Depends(require_hr_role)
):
    """Get detailed manager information (HR only)"""
    if manager_id not in database["users"]:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    manager = database["users"][manager_id]
    if manager.role != UserRole.MANAGER:
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    # Get property information
    property_info = None
    if manager.property_id and manager.property_id in database["properties"]:
        property_obj = database["properties"][manager.property_id]
        property_info = {
            "id": property_obj.id,
            "name": property_obj.name,
            "address": property_obj.address,
            "city": property_obj.city,
            "state": property_obj.state,
            "zip_code": property_obj.zip_code,
            "phone": property_obj.phone
        }
    
    # Get managed employees
    managed_employees = []
    for employee in database["employees"].values():
        if employee.manager_id == manager_id:
            user = database["users"].get(employee.user_id)
            managed_employees.append({
                "id": employee.id,
                "name": f"{user.first_name} {user.last_name}".strip() if user else "Unknown",
                "email": user.email if user else "",
                "department": employee.department,
                "position": employee.position,
                "employment_status": employee.employment_status,
                "hire_date": employee.hire_date.isoformat()
            })
    
    # Get reviewed applications
    reviewed_applications = []
    for app in database["applications"].values():
        if app.reviewed_by == manager_id:
            reviewed_applications.append({
                "id": app.id,
                "applicant_name": f"{app.applicant_data.get('first_name', '')} {app.applicant_data.get('last_name', '')}".strip(),
                "position": app.position,
                "department": app.department,
                "status": app.status,
                "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
                "rejection_reason": app.rejection_reason
            })
    
    # Calculate detailed performance metrics
    performance_metrics = {
        "applications_reviewed": len(reviewed_applications),
        "applications_approved": len([a for a in reviewed_applications if a["status"] == "approved"]),
        "applications_rejected": len([a for a in reviewed_applications if a["status"] == "rejected"]),
        "approval_rate": 0,
        "employees_managed": len(managed_employees),
        "active_employees": len([e for e in managed_employees if e["employment_status"] == "active"]),
        "departments_managed": len(set(e["department"] for e in managed_employees))
    }
    
    if performance_metrics["applications_reviewed"] > 0:
        performance_metrics["approval_rate"] = round(
            (performance_metrics["applications_approved"] / performance_metrics["applications_reviewed"]) * 100, 1
        )
    
    return {
        "id": manager.id,
        "email": manager.email,
        "first_name": manager.first_name,
        "last_name": manager.last_name,
        "full_name": f"{manager.first_name} {manager.last_name}".strip(),
        "property": property_info,
        "is_active": manager.is_active,
        "created_at": manager.created_at.isoformat(),
        "updated_at": manager.updated_at.isoformat() if manager.updated_at else None,
        "managed_employees": managed_employees,
        "reviewed_applications": reviewed_applications,
        "performance": performance_metrics
    }

@app.get("/hr/managers/performance")
async def get_managers_performance_summary(current_user: User = Depends(require_hr_role)):
    """Get performance summary for all managers (HR only)"""
    performance_data = []
    
    for user in database["users"].values():
        if user.role == UserRole.MANAGER and user.is_active:
            # Get property name
            property_name = "Unassigned"
            if user.property_id and user.property_id in database["properties"]:
                property_obj = database["properties"][user.property_id]
                property_name = property_obj.name
            
            # Calculate metrics
            reviewed_apps = [app for app in database["applications"].values() if app.reviewed_by == user.id]
            managed_employees = [emp for emp in database["employees"].values() if emp.manager_id == user.id]
            
            approved_count = len([a for a in reviewed_apps if a.status == ApplicationStatus.APPROVED])
            approval_rate = (approved_count / len(reviewed_apps) * 100) if reviewed_apps else 0
            
            performance_data.append({
                "manager_id": user.id,
                "manager_name": f"{user.first_name} {user.last_name}".strip(),
                "property_name": property_name,
                "applications_reviewed": len(reviewed_apps),
                "applications_approved": approved_count,
                "approval_rate": round(approval_rate, 1),
                "employees_managed": len(managed_employees),
                "active_employees": len([e for e in managed_employees if e.employment_status == "active"])
            })
    
    # Sort by applications reviewed (most active first)
    performance_data.sort(key=lambda x: x["applications_reviewed"], reverse=True)
    
    return performance_data

@app.post("/hr/managers")
async def create_manager(
    email: EmailStr = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    property_id: Optional[str] = Form(None),
    password: str = Form(...),
    current_user: User = Depends(require_hr_role)
):
    """Create a new manager (HR only)"""
    # Validate email format and uniqueness
    email_lower = email.lower().strip()
    
    for user in database["users"].values():
        if user.email.lower() == email_lower:
            raise HTTPException(status_code=400, detail="Email address already exists")
    
    # Validate names
    if not first_name.strip() or not last_name.strip():
        raise HTTPException(status_code=400, detail="First name and last name are required")
    
    # Validate password strength
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    # Validate property if provided
    if property_id:
        if property_id not in database["properties"]:
            raise HTTPException(status_code=404, detail="Property not found")
        
        property_obj = database["properties"][property_id]
        if not property_obj.is_active:
            raise HTTPException(status_code=400, detail="Cannot assign manager to inactive property")
    
    # Create manager user
    manager_id = str(uuid.uuid4())
    manager = User(
        id=manager_id,
        email=email_lower,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        role=UserRole.MANAGER,
        property_id=property_id,
        created_at=datetime.now(timezone.utc)
    )
    
    database["users"][manager_id] = manager
    
    # Store hashed password
    password_manager.store_password(email_lower, password)
    
    # Assign to property if specified
    if property_id:
        property_obj = database["properties"][property_id]
        if manager_id not in property_obj.manager_ids:
            property_obj.manager_ids.append(manager_id)
    
    # Get property name for response
    property_name = None
    if property_id:
        property_obj = database["properties"][property_id]
        property_name = property_obj.name
    
    return {
        "success": True,
        "message": "Manager created successfully",
        "manager": {
            "id": manager.id,
            "email": manager.email,
            "first_name": manager.first_name,
            "last_name": manager.last_name,
            "full_name": f"{manager.first_name} {manager.last_name}".strip(),
            "property_id": manager.property_id,
            "property_name": property_name,
            "is_active": manager.is_active,
            "created_at": manager.created_at.isoformat()
        }
    }

@app.put("/hr/managers/{manager_id}")
async def update_manager(
    manager_id: str,
    email: Optional[EmailStr] = Form(None),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    property_id: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    current_user: User = Depends(require_hr_role)
):
    """Update manager information (HR only)"""
    if manager_id not in database["users"]:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    manager = database["users"][manager_id]
    if manager.role != UserRole.MANAGER:
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    # Track changes for response
    changes_made = []
    
    # Update email if provided
    if email:
        email_lower = email.lower().strip()
        # Check for email conflicts
        for user_id, user in database["users"].items():
            if user_id != manager_id and user.email.lower() == email_lower:
                raise HTTPException(status_code=400, detail="Email address already exists")
        
        if manager.email != email_lower:
            old_email = manager.email
            manager.email = email_lower
            # Update password storage
            if old_email in password_manager.passwords:
                password_manager.passwords[email_lower] = password_manager.passwords[old_email]
                del password_manager.passwords[old_email]
            changes_made.append(f"Email updated from {old_email} to {email_lower}")
    
    # Update names if provided
    if first_name and first_name.strip() != manager.first_name:
        manager.first_name = first_name.strip()
        changes_made.append("First name updated")
    
    if last_name and last_name.strip() != manager.last_name:
        manager.last_name = last_name.strip()
        changes_made.append("Last name updated")
    
    # Update property assignment if provided
    if property_id is not None:  # Allow None to unassign
        old_property_id = manager.property_id
        
        if property_id == "":  # Empty string means unassign
            property_id = None
        
        if property_id and property_id not in database["properties"]:
            raise HTTPException(status_code=404, detail="Property not found")
        
        if property_id != old_property_id:
            # Remove from old property
            if old_property_id and old_property_id in database["properties"]:
                old_property = database["properties"][old_property_id]
                if manager_id in old_property.manager_ids:
                    old_property.manager_ids.remove(manager_id)
            
            # Add to new property
            if property_id:
                new_property = database["properties"][property_id]
                if manager_id not in new_property.manager_ids:
                    new_property.manager_ids.append(manager_id)
                changes_made.append(f"Assigned to property: {new_property.name}")
            else:
                changes_made.append("Unassigned from property")
            
            manager.property_id = property_id
    
    # Update active status if provided
    if is_active is not None and is_active != manager.is_active:
        manager.is_active = is_active
        changes_made.append(f"Status changed to {'active' if is_active else 'inactive'}")
    
    # Update timestamp
    manager.updated_at = datetime.now(timezone.utc)
    
    # Get property name for response
    property_name = None
    if manager.property_id and manager.property_id in database["properties"]:
        property_obj = database["properties"][manager.property_id]
        property_name = property_obj.name
    
    return {
        "success": True,
        "message": f"Manager updated successfully. Changes: {', '.join(changes_made) if changes_made else 'No changes made'}",
        "manager": {
            "id": manager.id,
            "email": manager.email,
            "first_name": manager.first_name,
            "last_name": manager.last_name,
            "full_name": f"{manager.first_name} {manager.last_name}".strip(),
            "property_id": manager.property_id,
            "property_name": property_name,
            "is_active": manager.is_active,
            "updated_at": manager.updated_at.isoformat()
        },
        "changes": changes_made
    }

@app.delete("/hr/managers/{manager_id}")
async def delete_manager(
    manager_id: str,
    current_user: User = Depends(require_hr_role)
):
    """Delete a manager (HR only)"""
    if manager_id not in database["users"]:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    manager = database["users"][manager_id]
    if manager.role != UserRole.MANAGER:
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    # Check for active responsibilities
    managed_employees = [emp for emp in database["employees"].values() if emp.manager_id == manager_id]
    pending_applications = [app for app in database["applications"].values() 
                           if app.property_id == manager.property_id and app.status == ApplicationStatus.PENDING]
    
    if managed_employees:
        return {
            "success": False,
            "message": f"Cannot delete manager with {len(managed_employees)} managed employees",
            "managed_employees": len(managed_employees),
            "pending_applications": len(pending_applications)
        }
    
    if pending_applications:
        return {
            "success": False,
            "message": f"Cannot delete manager with {len(pending_applications)} pending applications to review",
            "pending_applications": len(pending_applications)
        }
    
    # Remove from property assignments
    if manager.property_id and manager.property_id in database["properties"]:
        property_obj = database["properties"][manager.property_id]
        if manager_id in property_obj.manager_ids:
            property_obj.manager_ids.remove(manager_id)
    
    # Remove password
    if manager.email in password_manager.passwords:
        del password_manager.passwords[manager.email]
    
    # Delete manager
    del database["users"][manager_id]
    
    return {
        "success": True,
        "message": "Manager deleted successfully",
        "manager_id": manager_id
    }

@app.post("/hr/managers/{manager_id}/reset-password")
async def reset_manager_password(
    manager_id: str,
    new_password: str = Form(...),
    current_user: User = Depends(require_hr_role)
):
    """Reset manager password (HR only)"""
    if manager_id not in database["users"]:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    manager = database["users"][manager_id]
    if manager.role != UserRole.MANAGER:
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    # Validate password strength
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    # Update password
    password_manager.store_password(manager.email, new_password)
    manager.updated_at = datetime.now(timezone.utc)
    
    return {
        "success": True,
        "message": "Password reset successfully",
        "manager_id": manager_id
    }

# Enhanced Employee Management APIs
    
    manager = database["users"][manager_id]
    if manager.role != UserRole.MANAGER:
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    # Remove from property assignments
    if manager.property_id and manager.property_id in database["properties"]:
        property_obj = database["properties"][manager.property_id]
        if manager_id in property_obj.manager_ids:
            property_obj.manager_ids.remove(manager_id)
    
    # Remove manager from database
    del database["users"][manager_id]
    
    return {"message": "Manager deleted successfully"}

@app.get("/hr/managers/{manager_id}/performance")
async def get_manager_performance(
    manager_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get manager performance metrics"""
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Only HR can access manager performance")
    
    if manager_id not in database["users"]:
        raise HTTPException(status_code=404, detail="Manager not found")
    
    manager = database["users"][manager_id]
    if manager.role != UserRole.MANAGER:
        raise HTTPException(status_code=400, detail="User is not a manager")
    
    # Calculate performance metrics
    total_applications = 0
    approved_applications = 0
    rejected_applications = 0
    pending_applications = 0
    total_employees = 0
    
    # Count applications for manager's property
    if manager.property_id:
        for app in database["applications"].values():
            if app.property_id == manager.property_id:
                total_applications += 1
                if app.status == ApplicationStatus.APPROVED:
                    approved_applications += 1
                elif app.status == ApplicationStatus.REJECTED:
                    rejected_applications += 1
                elif app.status == ApplicationStatus.PENDING:
                    pending_applications += 1
        
        # Count employees for manager's property
        for emp in database["employees"].values():
            if emp.property_id == manager.property_id:
                total_employees += 1
    
    approval_rate = (approved_applications / total_applications * 100) if total_applications > 0 else 0
    
    return {
        "manager_id": manager_id,
        "manager_name": f"{manager.first_name} {manager.last_name}",
        "property_id": manager.property_id,
        "metrics": {
            "total_applications": total_applications,
            "approved_applications": approved_applications,
            "rejected_applications": rejected_applications,
            "pending_applications": pending_applications,
            "approval_rate": round(approval_rate, 1),
            "total_employees": total_employees
        }
    }

# Application Management
@app.get("/apply/{property_id}")
async def get_application_form(property_id: str):
    """Get application form for a property"""
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
    """Submit job application"""
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
        applied_at=datetime.now(timezone.utc)
    )
    
    database["applications"][application_id] = application
    return {"message": "Application submitted successfully", "application_id": application_id}

# Enhanced Application Approval with Onboarding Session Creation
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
    """Approve application and create secure onboarding session"""
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can approve applications")
    
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    if current_user.property_id != application.property_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update application
    application.status = ApplicationStatus.APPROVED
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.now(timezone.utc)
    
    # Create employee record
    employee_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    employee_user = User(
        id=user_id,
        email=application.applicant_data["email"],
        first_name=application.applicant_data["first_name"],
        last_name=application.applicant_data["last_name"],
        role=UserRole.EMPLOYEE,
        property_id=application.property_id,
        created_at=datetime.now(timezone.utc)
    )
    database["users"][user_id] = employee_user
    
    employee = Employee(
        id=employee_id,
        user_id=user_id,
        application_id=application_id,
        property_id=application.property_id,
        manager_id=current_user.id,
        department=application.department,
        position=job_title,
        hire_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
        pay_rate=pay_rate,
        pay_frequency=pay_frequency,
        employment_type=application.applicant_data.get("employment_type", "full_time"),
        personal_info={
            "job_title": job_title,
            "start_time": start_time,
            "benefits_eligible": benefits_eligible,
            "supervisor": supervisor,
            "special_instructions": special_instructions
        },
        onboarding_status=OnboardingStatus.NOT_STARTED,
        created_at=datetime.now(timezone.utc)
    )
    database["employees"][employee_id] = employee
    
    # Create secure onboarding session using the orchestrator service
    try:
        onboarding_session = onboarding_orchestrator.initiate_onboarding(
            application_id=application_id,
            employee_id=employee_id,
            property_id=application.property_id,
            manager_id=current_user.id,
            expires_hours=72  # 3 days
        )
        session_id = onboarding_session.id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create onboarding session: {str(e)}")
    
    # TALENT POOL LOGIC: Move other applications for same position to talent pool
    talent_pool_count = 0
    current_time = datetime.now(timezone.utc)
    
    for app_id, app in database["applications"].items():
        if (app_id != application_id and  # Don't affect the approved application
            app.property_id == application.property_id and  # Same property
            app.position == application.position and  # Same position
            app.status == ApplicationStatus.PENDING):  # Only pending applications
            
            # Move to talent pool
            app.status = ApplicationStatus.TALENT_POOL
            app.talent_pool_date = current_time
            app.reviewed_by = current_user.id
            app.reviewed_at = current_time
            talent_pool_count += 1
    
    # Generate onboarding URL
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    onboarding_url = f"{base_url}/onboard?token={onboarding_session.token}"
    
    return {
        "message": "Application approved successfully",
        "employee_id": employee_id,
        "onboarding": {
            "onboarding_url": onboarding_url,
            "token": onboarding_session.token,
            "expires_at": onboarding_session.expires_at.isoformat()
        },
        "employee_info": {
            "name": f"{application.applicant_data['first_name']} {application.applicant_data['last_name']}",
            "email": application.applicant_data["email"],
            "position": job_title,
            "department": application.department
        },
        "talent_pool": {
            "moved_to_talent_pool": talent_pool_count,
            "message": f"{talent_pool_count} other applications for {application.position} moved to talent pool"
        }
    }

@app.post("/applications/{application_id}/reject")
async def reject_application_manager(
    application_id: str,
    rejection_reason: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Reject application and move to talent pool (Manager only)"""
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can reject applications")
    
    if application_id not in database["applications"]:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = database["applications"][application_id]
    if current_user.property_id != application.property_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Application is not pending")
    
    if not rejection_reason.strip():
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    
    # Track status change
    old_status = application.status
    current_time = datetime.now(timezone.utc)
    
    # Update application - Move to TALENT_POOL instead of REJECTED
    application.status = ApplicationStatus.TALENT_POOL
    application.reviewed_by = current_user.id
    application.reviewed_at = current_time
    application.rejection_reason = rejection_reason.strip()
    application.talent_pool_date = current_time
    
    # Track status change to talent pool
    track_application_status_change(
        application_id=application_id,
        old_status=old_status,
        new_status=ApplicationStatus.TALENT_POOL,
        changed_by=current_user.id,
        reason=f"Rejected for current position: {rejection_reason.strip()}",
        notes="Application rejected but moved to talent pool for future opportunities"
    )
    
    # Get property and manager information for email
    property_obj = database["properties"][application.property_id]
    manager_name = f"{current_user.first_name} {current_user.last_name}".strip()
    
    # Send talent pool notification email instead of rejection email
    try:
        await email_service.send_talent_pool_notification(
            applicant_email=application.applicant_data["email"],
            applicant_name=f"{application.applicant_data['first_name']} {application.applicant_data['last_name']}".strip(),
            property_name=property_obj.name,
            position=application.position,
            manager_name=manager_name,
            manager_email=current_user.email
        )
    except Exception as e:
        # Log email error but don't fail the rejection process
        print(f"Failed to send talent pool email: {str(e)}")
    
    return {
        "success": True,
        "message": "Application rejected and moved to talent pool for future opportunities",
        "application_id": application_id,
        "rejection_reason": rejection_reason.strip(),
        "reviewed_by": f"{current_user.first_name} {current_user.last_name}".strip(),
        "reviewed_at": application.reviewed_at.isoformat(),
        "talent_pool_date": application.talent_pool_date.isoformat(),
        "status": "talent_pool",
        "talent_pool_message": "Candidate has been added to talent pool for future opportunities"
    }

# Secure Onboarding Access
@app.get("/onboard/verify")
async def verify_onboarding_token(token: str):
    """Verify onboarding token and return session info"""
    session = get_onboarding_session(token)
    employee = database["employees"][session.employee_id]
    employee_user = database["users"][employee.user_id]
    property_obj = database["properties"][employee.property_id]
    
    return {
        "valid": True,
        "session": {
            "id": session.id,
            "status": session.status,
            "current_step": session.current_step,
            "progress_percentage": session.progress_percentage,
            "language_preference": session.language_preference,
            "expires_at": session.expires_at
        },
        "employee": {
            "id": employee.id,
            "name": f"{employee_user.first_name} {employee_user.last_name}",
            "email": employee_user.email,
            "position": employee.position,
            "department": employee.department,
            "hire_date": employee.hire_date,
            "personal_info": employee.personal_info
        },
        "property": {
            "name": property_obj.name,
            "address": property_obj.address
        },
        "onboarding_steps": [step.value for step in OnboardingStep]
    }

@app.post("/onboard/update-progress")
async def update_onboarding_progress(
    token: str,
    progress_data: OnboardingProgressUpdate
):
    """Update onboarding progress"""
    session = get_onboarding_session(token)
    
    # Update session
    session.current_step = progress_data.step
    session.updated_at = datetime.now(timezone.utc)
    
    if progress_data.language_preference:
        session.language_preference = progress_data.language_preference
    
    # Update form data
    if progress_data.form_data:
        session.form_data.update(progress_data.form_data)
    
    # Update progress percentage
    steps = list(OnboardingStep)
    current_index = steps.index(progress_data.step)
    session.progress_percentage = (current_index + 1) / len(steps) * 100
    
    # Check if employee portion is completed
    if progress_data.step == OnboardingStep.EMPLOYEE_SIGNATURE:
        session.status = OnboardingStatus.EMPLOYEE_COMPLETED
        session.employee_completed_at = datetime.now(timezone.utc)
    
    return {
        "message": "Progress updated successfully",
        "current_step": session.current_step,
        "progress_percentage": session.progress_percentage,
        "status": session.status
    }

# PDF Generation Endpoints
@app.post("/onboard/generate-pdf/{form_type}")
async def generate_form_pdf(
    form_type: str,
    token: str,
    form_data: Dict[str, Any]
):
    """Generate PDF for specific form type"""
    session = get_onboarding_session(token)
    employee = database["employees"][session.employee_id]
    employee_user = database["users"][employee.user_id]
    
    # Combine employee data with form data
    complete_data = {
        "first_name": employee_user.first_name,
        "last_name": employee_user.last_name,
        "email": employee_user.email,
        "ssn": form_data.get("ssn", ""),
        "date_of_birth": form_data.get("date_of_birth", ""),
        "phone": form_data.get("phone", ""),
        "address": form_data.get("address", ""),
        "city": form_data.get("city", ""),
        "state": form_data.get("state", ""),
        "zip_code": form_data.get("zip_code", ""),
        **form_data
    }
    
    try:
        if form_type == "i9":
            pdf_bytes = pdf_form_service.fill_i9_form(complete_data)
        elif form_type == "w4":
            pdf_bytes = pdf_form_service.fill_w4_form(complete_data)
        elif form_type == "health_insurance":
            pdf_bytes = pdf_form_service.create_health_insurance_form(complete_data)
        elif form_type == "direct_deposit":
            pdf_bytes = pdf_form_service.create_direct_deposit_form(complete_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid form type")
        
        # Store PDF for later retrieval
        pdf_id = str(uuid.uuid4())
        database["generated_pdfs"] = database.get("generated_pdfs", {})
        database["generated_pdfs"][pdf_id] = {
            "pdf_data": base64.b64encode(pdf_bytes).decode(),
            "form_type": form_type,
            "employee_id": employee.id,
            "session_id": session.id,
            "created_at": datetime.now(timezone.utc),
            "signed": False
        }
        
        return {
            "pdf_id": pdf_id,
            "form_type": form_type,
            "pdf_url": f"/api/onboard/pdf/{pdf_id}",
            "preview_url": f"/api/onboard/pdf/{pdf_id}/preview"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.get("/onboard/pdf/{pdf_id}")
async def get_pdf(pdf_id: str):
    """Retrieve generated PDF"""
    if "generated_pdfs" not in database or pdf_id not in database["generated_pdfs"]:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    pdf_data = database["generated_pdfs"][pdf_id]
    pdf_bytes = base64.b64decode(pdf_data["pdf_data"])
    
    from fastapi.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={pdf_data['form_type']}_form.pdf"}
    )

@app.get("/onboard/pdf/{pdf_id}/preview")
async def preview_pdf(pdf_id: str):
    """Get PDF preview as base64 for embedded viewing"""
    if "generated_pdfs" not in database or pdf_id not in database["generated_pdfs"]:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    pdf_data = database["generated_pdfs"][pdf_id]
    
    return {
        "pdf_id": pdf_id,
        "form_type": pdf_data["form_type"],
        "pdf_base64": pdf_data["pdf_data"],
        "signed": pdf_data["signed"],
        "created_at": pdf_data["created_at"]
    }

@app.post("/onboard/pdf/{pdf_id}/sign")
async def sign_pdf(
    pdf_id: str,
    signature_data: Dict[str, Any]
):
    """Add digital signature to PDF"""
    if "generated_pdfs" not in database or pdf_id not in database["generated_pdfs"]:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    pdf_record = database["generated_pdfs"][pdf_id]
    
    # Store signature data
    signature_id = str(uuid.uuid4())
    database["pdf_signatures"] = database.get("pdf_signatures", {})
    database["pdf_signatures"][signature_id] = {
        "pdf_id": pdf_id,
        "signature_data": signature_data["signature_data"],
        "signer_name": signature_data["signer_name"],
        "signer_role": signature_data.get("signer_role", "employee"),
        "signed_at": datetime.now(timezone.utc),
        "ip_address": signature_data.get("ip_address", ""),
        "signature_type": signature_data.get("signature_type", "employee")
    }
    
    # Mark PDF as signed
    pdf_record["signed"] = True
    pdf_record["signature_id"] = signature_id
    pdf_record["signed_at"] = datetime.now(timezone.utc)
    
    return {
        "message": "PDF signed successfully",
        "signature_id": signature_id,
        "pdf_id": pdf_id,
        "signed_at": pdf_record["signed_at"]
    }

# Manager Dashboard Endpoints
@app.get("/manager/property")
async def get_manager_property(current_user: User = Depends(require_manager_role)):
    """Get manager's assigned property details"""
    if not current_user.property_id:
        raise HTTPException(status_code=404, detail="Manager not assigned to any property")
    
    property_obj = database["properties"].get(current_user.property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return {
        "id": property_obj.id,
        "name": property_obj.name,
        "address": property_obj.address,
        "city": property_obj.city,
        "state": property_obj.state,
        "zip_code": property_obj.zip_code,
        "phone": property_obj.phone,
        "qr_code_url": property_obj.qr_code_url,
        "is_active": property_obj.is_active,
        "created_at": property_obj.created_at.isoformat(),
        "manager_ids": property_obj.manager_ids
    }

@app.get("/manager/dashboard-stats")
async def get_manager_dashboard_stats(current_user: User = Depends(require_manager_role)):
    """Get dashboard statistics for manager's property"""
    manager_id = current_user.id
    
    # Find manager's property
    manager_property = None
    for prop_id, prop in database["properties"].items():
        if manager_id in prop.manager_ids:
            manager_property = prop_id
            break
    
    if not manager_property:
        raise HTTPException(status_code=404, detail="Manager not assigned to any property")
    
    # Get applications for this property
    property_applications = [
        app for app in database["applications"].values()
        if app.property_id == manager_property
    ]
    
    # Get employees for this property
    property_employees = [
        emp for emp in database["employees"].values()
        if emp.property_id == manager_property
    ]
    
    # Calculate stats
    pending_applications = len([app for app in property_applications if app.status == "pending"])
    approved_applications = len([app for app in property_applications if app.status == "approved"])
    
    return {
        "propertyId": manager_property,
        "propertyName": database["properties"][manager_property].name,
        "totalApplications": len(property_applications),
        "pendingApplications": pending_applications,
        "approvedApplications": approved_applications,
        "totalEmployees": len(property_employees),
        "recentApplications": sorted(property_applications, key=lambda x: x.applied_at, reverse=True)[:5]
    }

@app.get("/manager/applications")
async def get_manager_applications(current_user: User = Depends(require_manager_role)):
    """Get all applications for manager's property"""
    manager_id = current_user.id
    
    # Find manager's property
    manager_property = None
    for prop_id, prop in database["properties"].items():
        if manager_id in prop.manager_ids:
            manager_property = prop_id
            break
    
    if not manager_property:
        raise HTTPException(status_code=404, detail="Manager not assigned to any property")
    
    # Get applications for this property
    property_applications = [
        app for app in database["applications"].values()
        if app.property_id == manager_property
    ]
    
    # Sort by submission date (newest first)
    property_applications.sort(key=lambda x: x.applied_at, reverse=True)
    
    # Format applications for response (similar to HR endpoint)
    formatted_applications = []
    for app in property_applications:
        formatted_app = {
            "id": app.id,
            "property_id": app.property_id,
            "property_name": database["properties"][app.property_id].name,
            "department": app.department,
            "position": app.position,
            "applicant_name": f"{app.applicant_data.get('first_name', '')} {app.applicant_data.get('last_name', '')}".strip(),
            "applicant_email": app.applicant_data.get("email", ""),
            "applicant_phone": app.applicant_data.get("phone", ""),
            "status": app.status,
            "applied_at": app.applied_at.isoformat(),
            "applicant_data": app.applicant_data
        }
        formatted_applications.append(formatted_app)
    
    return formatted_applications

# Manager Review Endpoints
@app.get("/manager/pending-reviews")
async def get_pending_reviews(current_user: User = Depends(get_current_user)):
    """Get all onboarding sessions pending manager review"""
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can access reviews")
    
    pending_reviews = []
    for session in database["onboarding_sessions"].values():
        if session.status == OnboardingStatus.EMPLOYEE_COMPLETED:
            employee = database["employees"][session.employee_id]
            if employee.manager_id == current_user.id:
                employee_user = database["users"][employee.user_id]
                
                pending_reviews.append({
                    "session": session,
                    "employee": {
                        "id": employee.id,
                        "name": f"{employee_user.first_name} {employee_user.last_name}",
                        "email": employee_user.email,
                        "position": employee.position,
                        "department": employee.department,
                        "hire_date": employee.hire_date
                    },
                    "days_pending": (datetime.now(timezone.utc) - session.employee_completed_at).days if session.employee_completed_at else 0
                })
    
    return pending_reviews

@app.post("/manager/review/{session_id}")
async def submit_manager_review(
    session_id: str,
    review_data: ManagerReviewRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit manager review for onboarding session"""
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only managers can submit reviews")
    
    if session_id not in database["onboarding_sessions"]:
        raise HTTPException(status_code=404, detail="Onboarding session not found")
    
    session = database["onboarding_sessions"][session_id]
    employee = database["employees"][session.employee_id]
    
    if employee.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update session based on review action
    if review_data.action == "approve":
        session.status = OnboardingStatus.MANAGER_REVIEW
        session.current_step = OnboardingStep.I9_SECTION2
        session.reviewed_by = current_user.id
        session.manager_review_started_at = datetime.now(timezone.utc)
    elif review_data.action == "reject":
        session.status = OnboardingStatus.REJECTED
        session.rejection_reason = review_data.comments
    else:  # request_changes
        session.status = OnboardingStatus.IN_PROGRESS
        session.current_step = OnboardingStep.EMPLOYEE_SIGNATURE  # Send back to employee
    
    session.manager_comments = review_data.comments
    session.updated_at = datetime.now(timezone.utc)
    
    return {
        "message": f"Review {review_data.action} submitted successfully",
        "session_status": session.status,
        "next_step": session.current_step
    }

# ============================================================================
# FEDERAL COMPLIANCE VALIDATION ENDPOINTS
# ============================================================================

@app.post("/api/validate/age", response_model=FederalValidationResult)
async def validate_employee_age(request: dict):
    """
    Validate employee age meets federal requirements (18+ for hotel positions)
    CRITICAL: Federal law compliance endpoint - blocks employment of minors
    Reference: Fair Labor Standards Act (FLSA) 29 U.S.C. § 203
    """
    try:
        date_of_birth = request.get("date_of_birth")
        if not date_of_birth:
            raise HTTPException(
                status_code=400, 
                detail="Date of birth is required for federal age validation"
            )
        
        result = FederalValidationService.validate_age(date_of_birth)
        
        # Log compliance check
        audit_entry = FederalValidationService.generate_compliance_audit_entry(
            "AGE_VALIDATION",
            result,
            {"id": "system", "email": "system@compliance.gov"}
        )
        database["compliance_audit_trail"][audit_entry.audit_id] = audit_entry
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Age validation error: {str(e)}")

@app.post("/api/validate/ssn", response_model=FederalValidationResult)
async def validate_ssn(request: dict):
    """
    Validate Social Security Number meets federal requirements
    Reference: 26 U.S.C. § 3401 (IRS), 42 U.S.C. § 405 (SSA)
    """
    try:
        ssn = request.get("ssn")
        if not ssn:
            raise HTTPException(
                status_code=400,
                detail="SSN is required for federal tax compliance validation"
            )
        
        result = FederalValidationService.validate_ssn(ssn)
        
        # Log compliance check (with SSN masked for security)
        audit_entry = FederalValidationService.generate_compliance_audit_entry(
            "SSN_VALIDATION",
            result,
            {"id": "system", "email": "system@compliance.gov"}
        )
        database["compliance_audit_trail"][audit_entry.audit_id] = audit_entry
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SSN validation error: {str(e)}")

@app.post("/api/validate/i9-section1", response_model=FederalValidationResult)
async def validate_i9_section1(request: I9ValidationRequest):
    """
    Validate I-9 Section 1 meets federal immigration compliance requirements
    Reference: 8 U.S.C. § 1324a, 8 CFR § 274a
    """
    try:
        result = FederalValidationService.validate_i9_section1(request.form_data)
        
        # Log compliance check
        audit_entry = FederalValidationService.generate_compliance_audit_entry(
            "I9_SECTION1_VALIDATION",
            result,
            {"id": "system", "email": "system@compliance.gov"}
        )
        database["compliance_audit_trail"][audit_entry.audit_id] = audit_entry
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"I-9 validation error: {str(e)}")

@app.post("/api/validate/w4-form", response_model=FederalValidationResult)
async def validate_w4_form(request: W4ValidationRequest):
    """
    Validate W-4 form meets federal tax compliance requirements
    Reference: 26 U.S.C. § 3402, IRS Publication 15
    """
    try:
        result = FederalValidationService.validate_w4_form(request.form_data)
        
        # Log compliance check
        audit_entry = FederalValidationService.generate_compliance_audit_entry(
            "W4_FORM_VALIDATION",
            result,
            {"id": "system", "email": "system@compliance.gov"}
        )
        database["compliance_audit_trail"][audit_entry.audit_id] = audit_entry
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"W-4 validation error: {str(e)}")

@app.post("/api/validate/comprehensive", response_model=FederalValidationResult)
async def validate_comprehensive_compliance(request: ComprehensiveValidationRequest):
    """
    Comprehensive federal compliance validation across all forms
    Validates personal info, I-9 data, and W-4 data for complete compliance check
    """
    try:
        combined_result = FederalValidationResult(is_valid=True)
        
        # Validate personal info if provided
        if request.personal_info:
            age_result = FederalValidationService.validate_age(request.personal_info.date_of_birth)
            ssn_result = FederalValidationService.validate_ssn(request.personal_info.ssn)
            
            combined_result.errors.extend(age_result.errors + ssn_result.errors)
            combined_result.warnings.extend(age_result.warnings + ssn_result.warnings)
            combined_result.compliance_notes.extend(age_result.compliance_notes + ssn_result.compliance_notes)
            
            if not age_result.is_valid or not ssn_result.is_valid:
                combined_result.is_valid = False
        
        # Validate I-9 data if provided
        if request.i9_data:
            i9_result = FederalValidationService.validate_i9_section1(request.i9_data)
            combined_result.errors.extend(i9_result.errors)
            combined_result.warnings.extend(i9_result.warnings)
            combined_result.compliance_notes.extend(i9_result.compliance_notes)
            
            if not i9_result.is_valid:
                combined_result.is_valid = False
        
        # Validate W-4 data if provided
        if request.w4_data:
            w4_result = FederalValidationService.validate_w4_form(request.w4_data)
            combined_result.errors.extend(w4_result.errors)
            combined_result.warnings.extend(w4_result.warnings)
            combined_result.compliance_notes.extend(w4_result.compliance_notes)
            
            if not w4_result.is_valid:
                combined_result.is_valid = False
        
        # Cross-form validation (name and SSN consistency)
        if request.personal_info and request.i9_data:
            if (request.personal_info.first_name != request.i9_data.employee_first_name or
                request.personal_info.last_name != request.i9_data.employee_last_name):
                combined_result.warnings.append(FederalValidationError(
                    field='name_consistency',
                    message='Name differences detected between personal info and I-9 form',
                    legal_code='CONSISTENCY-NAME',
                    severity='warning',
                    compliance_note='Names should match across all forms for compliance'
                ))
            
            if request.personal_info.ssn != request.i9_data.ssn:
                combined_result.is_valid = False
                combined_result.errors.append(FederalValidationError(
                    field='ssn_consistency',
                    message='SSN mismatch between personal info and I-9 form',
                    legal_code='CONSISTENCY-SSN',
                    severity='error',
                    compliance_note='SSN must be consistent across all forms for federal compliance'
                ))
        
        if request.personal_info and request.w4_data:
            if (request.personal_info.first_name != request.w4_data.first_name or
                request.personal_info.last_name != request.w4_data.last_name):
                combined_result.warnings.append(FederalValidationError(
                    field='name_consistency_w4',
                    message='Name differences detected between personal info and W-4 form',
                    legal_code='CONSISTENCY-NAME-W4',
                    severity='warning',
                    compliance_note='Names should match across all forms for tax compliance'
                ))
            
            if request.personal_info.ssn != request.w4_data.ssn:
                combined_result.is_valid = False
                combined_result.errors.append(FederalValidationError(
                    field='ssn_consistency_w4',
                    message='SSN mismatch between personal info and W-4 form',
                    legal_code='CONSISTENCY-SSN-W4',
                    severity='error',
                    compliance_note='SSN must be consistent across all forms for tax compliance'
                ))
        
        # Add final compliance status
        if combined_result.is_valid:
            combined_result.compliance_notes.append('FEDERAL COMPLIANCE VERIFIED: All forms meet federal employment law requirements')
        else:
            combined_result.compliance_notes.append('FEDERAL COMPLIANCE FAILURE: Critical violations detected that must be resolved before employment can proceed')
        
        # Log comprehensive compliance check
        audit_entry = FederalValidationService.generate_compliance_audit_entry(
            "COMPREHENSIVE_VALIDATION",
            combined_result,
            {"id": "system", "email": "system@compliance.gov"}
        )
        database["compliance_audit_trail"][audit_entry.audit_id] = audit_entry
        
        return combined_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive validation error: {str(e)}")

@app.get("/api/compliance/audit-trail")
async def get_compliance_audit_trail(limit: int = 100):
    """
    Retrieve federal compliance audit trail
    Used for legal compliance documentation and reporting
    """
    try:
        audit_entries = list(database["compliance_audit_trail"].values())
        # Sort by timestamp, most recent first
        audit_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return {
            "total_entries": len(audit_entries),
            "entries": audit_entries[:limit],
            "compliance_summary": {
                "total_validations": len(audit_entries),
                "compliant_validations": len([e for e in audit_entries if e.compliance_status == "COMPLIANT"]),
                "non_compliant_validations": len([e for e in audit_entries if e.compliance_status == "NON_COMPLIANT"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit trail retrieval error: {str(e)}")

@app.get("/api/compliance/legal-codes")
async def get_legal_compliance_codes():
    """
    Retrieve all legal compliance codes and their meanings
    Reference documentation for federal compliance requirements
    """
    legal_codes = {
        "FLSA-203": {
            "law": "Fair Labor Standards Act Section 203",
            "description": "Federal minimum age requirements for employment",
            "reference": "29 U.S.C. § 203",
            "severity": "CRITICAL - Employment blocking"
        },
        "FLSA-203-CHILD-LABOR": {
            "law": "Fair Labor Standards Act Child Labor Provisions", 
            "description": "Prohibits employment of minors under 18 in most hotel positions",
            "reference": "29 U.S.C. § 203",
            "severity": "CRITICAL - Employment blocking"
        },
        "IRC-3401-SSN": {
            "law": "Internal Revenue Code Section 3401",
            "description": "SSN required for federal tax withholding",
            "reference": "26 U.S.C. § 3401",
            "severity": "CRITICAL - Tax compliance"
        },
        "SSA-405-FORMAT": {
            "law": "Social Security Act Section 405",
            "description": "SSN format requirements",
            "reference": "42 U.S.C. § 405",
            "severity": "HIGH - Invalid SSN"
        },
        "INA-274A-REQUIRED": {
            "law": "Immigration and Nationality Act Section 274A",
            "description": "Required fields for I-9 employment verification",
            "reference": "8 U.S.C. § 1324a",
            "severity": "CRITICAL - Immigration compliance"
        },
        "IRC-3402-REQUIRED": {
            "law": "Internal Revenue Code Section 3402",
            "description": "Required fields for W-4 tax withholding",
            "reference": "26 U.S.C. § 3402",
            "severity": "CRITICAL - Tax compliance"
        }
    }
    
    return {
        "legal_codes": legal_codes,
        "compliance_note": "All legal codes reference current federal law as of 2025. Consult legal counsel for interpretation and compliance requirements.",
        "last_updated": datetime.now().isoformat()
    }

# ============================================================================
# EMPLOYEE MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/employees")
async def get_employees(
    property_id: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get employees with filtering and search capabilities"""
    
    # Get all employees
    employees = list(database["employees"].values())
    
    # Filter by user role
    if current_user.role == UserRole.MANAGER:
        # Managers can only see employees from their property
        employees = [emp for emp in employees if emp.property_id == current_user.property_id]
    elif current_user.role == UserRole.HR:
        # HR can see all employees, optionally filtered by property
        if property_id:
            employees = [emp for emp in employees if emp.property_id == property_id]
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Apply filters
    if department:
        employees = [emp for emp in employees if emp.department.lower() == department.lower()]
    
    if status:
        employees = [emp for emp in employees if emp.employment_status.lower() == status.lower()]
    
    # Apply search
    if search:
        search_lower = search.lower()
        filtered_employees = []
        for emp in employees:
            # Get user info for name and email search
            user = database["users"].get(emp.user_id)
            if user:
                if (search_lower in (user.first_name or "").lower() or
                    search_lower in (user.last_name or "").lower() or
                    search_lower in user.email.lower() or
                    search_lower in emp.department.lower() or
                    search_lower in emp.position.lower()):
                    filtered_employees.append(emp)
        employees = filtered_employees
    
    # Enrich employee data with user info and property info
    enriched_employees = []
    for emp in employees:
        user = database["users"].get(emp.user_id)
        property_obj = database["properties"].get(emp.property_id)
        manager = database["users"].get(emp.manager_id)
        
        if user and property_obj:
            enriched_employees.append({
                "id": emp.id,
                "employee_number": emp.employee_number,
                "user_id": emp.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "property_id": emp.property_id,
                "property_name": property_obj.name,
                "department": emp.department,
                "position": emp.position,
                "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
                "start_date": emp.start_date.isoformat() if emp.start_date else None,
                "employment_status": emp.employment_status,
                "onboarding_status": emp.onboarding_status,
                "pay_rate": emp.pay_rate,
                "pay_frequency": emp.pay_frequency,
                "employment_type": emp.employment_type,
                "manager_name": f"{manager.first_name} {manager.last_name}" if manager else None,
                "created_at": emp.created_at.isoformat(),
                "onboarding_completed_at": emp.onboarding_completed_at.isoformat() if emp.onboarding_completed_at else None
            })
    
    return {
        "employees": enriched_employees,
        "total": len(enriched_employees)
    }

@app.get("/api/employees/{employee_id}")
async def get_employee_details(
    employee_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed employee information"""
    
    employee = database["employees"].get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check access permissions
    if current_user.role == UserRole.MANAGER:
        if employee.property_id != current_user.property_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get related data
    user = database["users"].get(employee.user_id)
    property_obj = database["properties"].get(employee.property_id)
    manager = database["users"].get(employee.manager_id)
    application = database["applications"].get(employee.application_id) if employee.application_id else None
    
    # Get onboarding session if exists
    onboarding_session = None
    for session in database["onboarding_sessions"].values():
        if session.employee_id == employee_id:
            onboarding_session = session
            break
    
    if not user or not property_obj:
        raise HTTPException(status_code=404, detail="Employee data incomplete")
    
    return {
        "id": employee.id,
        "employee_number": employee.employee_number,
        "user_id": employee.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "property_id": employee.property_id,
        "property_name": property_obj.name,
        "property_address": f"{property_obj.address}, {property_obj.city}, {property_obj.state} {property_obj.zip_code}",
        "department": employee.department,
        "position": employee.position,
        "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
        "start_date": employee.start_date.isoformat() if employee.start_date else None,
        "employment_status": employee.employment_status,
        "onboarding_status": employee.onboarding_status,
        "pay_rate": employee.pay_rate,
        "pay_frequency": employee.pay_frequency,
        "employment_type": employee.employment_type,
        "manager_id": employee.manager_id,
        "manager_name": f"{manager.first_name} {manager.last_name}" if manager else None,
        "personal_info": employee.personal_info,
        "emergency_contacts": employee.emergency_contacts,
        "created_at": employee.created_at.isoformat(),
        "onboarding_completed_at": employee.onboarding_completed_at.isoformat() if employee.onboarding_completed_at else None,
        "application_data": {
            "id": application.id,
            "applied_at": application.applied_at.isoformat(),
            "applicant_data": application.applicant_data
        } if application else None,
        "onboarding_progress": {
            "status": onboarding_session.status,
            "current_step": onboarding_session.current_step,
            "progress_percentage": onboarding_session.progress_percentage,
            "steps_completed": onboarding_session.steps_completed,
            "employee_completed_at": onboarding_session.employee_completed_at.isoformat() if onboarding_session and onboarding_session.employee_completed_at else None,
            "manager_review_started_at": onboarding_session.manager_review_started_at.isoformat() if onboarding_session and onboarding_session.manager_review_started_at else None
        } if onboarding_session else None
    }

@app.put("/api/employees/{employee_id}/status")
async def update_employee_status(
    employee_id: str,
    status_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update employee status (employment_status or onboarding_status)"""
    
    employee = database["employees"].get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check access permissions
    if current_user.role == UserRole.MANAGER:
        if employee.property_id != current_user.property_id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update status fields
    if "employment_status" in status_data:
        valid_statuses = ["active", "inactive", "terminated", "on_leave"]
        if status_data["employment_status"] not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid employment status. Must be one of: {valid_statuses}")
        employee.employment_status = status_data["employment_status"]
    
    if "onboarding_status" in status_data:
        try:
            employee.onboarding_status = OnboardingStatus(status_data["onboarding_status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid onboarding status")
    
    employee.updated_at = datetime.now(timezone.utc)
    
    return {
        "message": "Employee status updated successfully",
        "employee_id": employee_id,
        "employment_status": employee.employment_status,
        "onboarding_status": employee.onboarding_status
    }

@app.get("/api/employees/filters/options")
async def get_employee_filter_options(current_user: User = Depends(get_current_user)):
    """Get available filter options for employees"""
    
    if current_user.role not in [UserRole.HR, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get employees based on user role
    employees = list(database["employees"].values())
    if current_user.role == UserRole.MANAGER:
        employees = [emp for emp in employees if emp.property_id == current_user.property_id]
    
    # Extract unique values for filters
    departments = list(set(emp.department for emp in employees if emp.department))
    statuses = list(set(emp.employment_status for emp in employees if emp.employment_status))
    
    # Get properties for HR users
    properties = []
    if current_user.role == UserRole.HR:
        properties = [
            {"id": prop.id, "name": prop.name}
            for prop in database["properties"].values()
            if prop.is_active
        ]
    
    return {
        "departments": sorted(departments),
        "statuses": sorted(statuses),
        "properties": properties
    }

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/hr/analytics/overview")
async def get_analytics_overview(current_user: User = Depends(get_current_user)):
    """Get comprehensive analytics overview for HR dashboard"""
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Only HR can access analytics")
    
    # Basic counts
    total_properties = len([p for p in database["properties"].values() if p.is_active])
    total_managers = len([u for u in database["users"].values() if u.role == UserRole.MANAGER and u.is_active])
    total_employees = len([u for u in database["users"].values() if u.role == UserRole.EMPLOYEE and u.is_active])
    total_applications = len(database["applications"])
    
    # Application status breakdown
    applications = list(database["applications"].values())
    pending_applications = len([a for a in applications if a.status == ApplicationStatus.PENDING])
    approved_applications = len([a for a in applications if a.status == ApplicationStatus.APPROVED])
    rejected_applications = len([a for a in applications if a.status == ApplicationStatus.REJECTED])
    
    # Recent activity (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_applications = [a for a in applications if a.applied_at >= thirty_days_ago]
    recent_employees = [u for u in database["users"].values() 
                      if u.role == UserRole.EMPLOYEE and u.created_at >= thirty_days_ago]
    
    # Department breakdown
    department_stats = {}
    for app in applications:
        dept = app.department
        if dept not in department_stats:
            department_stats[dept] = {"total": 0, "pending": 0, "approved": 0, "rejected": 0}
        department_stats[dept]["total"] += 1
        if app.status == ApplicationStatus.PENDING:
            department_stats[dept]["pending"] += 1
        elif app.status == ApplicationStatus.APPROVED:
            department_stats[dept]["approved"] += 1
        elif app.status == ApplicationStatus.REJECTED:
            department_stats[dept]["rejected"] += 1
    
    return {
        "overview": {
            "totalProperties": total_properties,
            "totalManagers": total_managers,
            "totalEmployees": total_employees,
            "totalApplications": total_applications,
            "pendingApplications": pending_applications,
            "approvedApplications": approved_applications,
            "rejectedApplications": rejected_applications
        },
        "recentActivity": {
            "newApplications": len(recent_applications),
            "newEmployees": len(recent_employees)
        },
        "departmentStats": department_stats,
        "applicationTrends": {
            "pending": pending_applications,
            "approved": approved_applications,
            "rejected": rejected_applications
        }
    }

@app.get("/hr/analytics/property-performance")
async def get_property_performance(current_user: User = Depends(get_current_user)):
    """Get property performance analytics"""
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Only HR can access analytics")
    
    properties = list(database["properties"].values())
    applications = list(database["applications"].values())
    users = list(database["users"].values())
    
    property_performance = []
    
    for prop in properties:
        if not prop.is_active:
            continue
            
        # Applications for this property
        prop_applications = [a for a in applications if a.property_id == prop.id]
        
        # Managers for this property
        prop_managers = [u for u in users if u.role == UserRole.MANAGER and u.property_id == prop.id and u.is_active]
        
        # Employees for this property
        prop_employees = [u for u in users if u.role == UserRole.EMPLOYEE and u.property_id == prop.id and u.is_active]
        
        # Application status breakdown
        pending = len([a for a in prop_applications if a.status == ApplicationStatus.PENDING])
        approved = len([a for a in prop_applications if a.status == ApplicationStatus.APPROVED])
        rejected = len([a for a in prop_applications if a.status == ApplicationStatus.REJECTED])
        
        # Recent activity (last 7 days)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_applications = len([a for a in prop_applications if a.applied_at >= week_ago])
        
        property_performance.append({
            "propertyId": prop.id,
            "propertyName": prop.name,
            "city": prop.city,
            "state": prop.state,
            "managersCount": len(prop_managers),
            "employeesCount": len(prop_employees),
            "totalApplications": len(prop_applications),
            "pendingApplications": pending,
            "approvedApplications": approved,
            "rejectedApplications": rejected,
            "recentApplications": recent_applications,
            "approvalRate": round((approved / len(prop_applications)) * 100, 1) if prop_applications else 0
        })
    
    return {"propertyPerformance": property_performance}

@app.get("/hr/analytics/employee-trends")
async def get_employee_trends(current_user: User = Depends(get_current_user)):
    """Get employee statistics and trends"""
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Only HR can access analytics")
    
    employees = [u for u in database["users"].values() if u.role == UserRole.EMPLOYEE and u.is_active]
    applications = list(database["applications"].values())
    
    # Monthly hiring trends (last 6 months)
    monthly_trends = []
    for i in range(6):
        month_start = datetime.now(timezone.utc).replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        month_employees = [e for e in employees if month_start <= e.created_at < month_end]
        month_applications = [a for a in applications if month_start <= a.applied_at < month_end]
        
        monthly_trends.append({
            "month": month_start.strftime("%Y-%m"),
            "newEmployees": len(month_employees),
            "applications": len(month_applications)
        })
    
    # Department distribution
    department_distribution = {}
    for app in applications:
        if app.status == ApplicationStatus.APPROVED:
            dept = app.department
            department_distribution[dept] = department_distribution.get(dept, 0) + 1
    
    # Property distribution
    property_distribution = {}
    properties = {p.id: p.name for p in database["properties"].values()}
    for emp in employees:
        if emp.property_id:
            prop_name = properties.get(emp.property_id, "Unknown")
            property_distribution[prop_name] = property_distribution.get(prop_name, 0) + 1
    
    return {
        "monthlyTrends": list(reversed(monthly_trends)),
        "departmentDistribution": department_distribution,
        "propertyDistribution": property_distribution,
        "totalEmployees": len(employees)
    }

@app.get("/hr/analytics/export")
async def export_analytics_data(
    format: str = "json",
    current_user: User = Depends(get_current_user)
):
    """Export analytics data in various formats"""
    if current_user.role != UserRole.HR:
        raise HTTPException(status_code=403, detail="Only HR can export analytics")
    
    # Get all analytics data
    overview_data = await get_analytics_overview(current_user)
    property_data = await get_property_performance(current_user)
    employee_data = await get_employee_trends(current_user)
    
    export_data = {
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "exportedBy": current_user.email,
        "overview": overview_data,
        "propertyPerformance": property_data,
        "employeeTrends": employee_data
    }
    
    if format.lower() == "json":
        return export_data
    else:
        raise HTTPException(status_code=400, detail="Only JSON format is currently supported")



# =====================================
# ENHANCED ONBOARDING ORCHESTRATOR ENDPOINTS
# =====================================

@app.get("/api/employees/{employee_id}/welcome-data")
async def get_employee_welcome_data(
    employee_id: str,
    token: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get comprehensive welcome data for the onboarding welcome page
    Supports both authenticated access and token-based access
    """
    try:
        # Validate access - either authenticated user or valid token
        if not current_user and not token:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # If token provided, validate it
        if token:
            session = onboarding_orchestrator.get_session_by_token(token)
            if not session or session.employee_id != employee_id:
                raise HTTPException(status_code=401, detail="Invalid or expired onboarding token")
        
        # Check if employee exists
        if employee_id not in database["employees"]:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee = database["employees"][employee_id]
        
        # Get property information
        if employee.property_id not in database["properties"]:
            raise HTTPException(status_code=404, detail="Property not found")
        
        property_obj = database["properties"][employee.property_id]
        
        # Find the original application to get applicant data
        applicant_data = {
            "first_name": "Employee", 
            "last_name": "", 
            "email": "", 
            "phone": ""
        }
        
        for application in database["applications"].values():
            if (application.property_id == employee.property_id and 
                application.status == ApplicationStatus.APPROVED and
                application.department == employee.department):
                applicant_data = application.applicant_data
                break
        
        # Create audit entry for welcome page access
        audit_entry = AuditEntry(
            entity_type="employee",
            entity_id=employee_id,
            action="welcome_page_access",
            user_id=current_user.id if current_user else "token_access",
            timestamp=datetime.utcnow(),
            ip_address="unknown",  # Could be extracted from request
            user_agent="unknown",  # Could be extracted from request
            compliance_event=True,
            legal_requirement="Employee onboarding access tracking"
        )
        
        if employee_id not in database["audit_trail"]:
            database["audit_trail"][employee_id] = []
        database["audit_trail"][employee_id].append(audit_entry)
        
        return {
            "employee": employee,
            "property": property_obj,
            "applicant_data": applicant_data,
            "onboarding_token": token  # Include token for frontend use
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get welcome data for employee {employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get welcome data: {str(e)}")

@app.get("/api/onboarding/welcome/{token}")
async def get_welcome_data_by_token(token: str):
    """
    Get welcome data using onboarding token (Task 3 endpoint)
    This endpoint allows access to welcome data using just the onboarding token
    """
    try:
        # Find the onboarding session by token
        onboarding_session = None
        for session_id, session in database["onboarding_sessions"].items():
            if session.token == token:
                onboarding_session = session
                break
        
        if not onboarding_session:
            raise HTTPException(status_code=404, detail="Invalid or expired onboarding token")
        
        # Check if token is expired
        if onboarding_session.expires_at and datetime.utcnow() > onboarding_session.expires_at:
            raise HTTPException(status_code=401, detail="Onboarding token has expired")
        
        # Get employee data
        employee_id = onboarding_session.employee_id
        if employee_id not in database["employees"]:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee = database["employees"][employee_id]
        
        # Get property data
        property_id = employee.property_id
        if property_id not in database["properties"]:
            raise HTTPException(status_code=404, detail="Property not found")
        
        property_data = database["properties"][property_id]
        
        # Get application data for additional info
        application_data = None
        for app_id, app in database["applications"].items():
            if app.id == onboarding_session.application_id:
                application_data = app
                break
        
        # Create welcome data response
        welcome_data = {
            "employee": {
                "id": employee.id,
                "name": f"{employee.personal_info.first_name} {employee.personal_info.last_name}",
                "email": employee.personal_info.email,
                "phone": employee.personal_info.phone,
                "employee_id": employee.employee_id,
                "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
                "status": employee.status.value
            },
            "property": {
                "id": property_data.id,
                "name": property_data.name,
                "address": property_data.address,
                "manager_ids": property_data.manager_ids
            },
            "job_details": {
                "job_title": employee.job_details.job_title,
                "department": employee.job_details.department,
                "start_date": employee.job_details.start_date.isoformat() if employee.job_details.start_date else None,
                "pay_rate": employee.job_details.pay_rate,
                "employment_type": employee.job_details.employment_type,
                "supervisor": employee.job_details.supervisor,
                "benefits_eligible": employee.job_details.benefits_eligible,
                "special_instructions": employee.job_details.special_instructions
            },
            "applicant_data": {
                "first_name": application_data.first_name if application_data else employee.personal_info.first_name,
                "last_name": application_data.last_name if application_data else employee.personal_info.last_name,
                "email": application_data.email if application_data else employee.personal_info.email,
                "phone": application_data.phone if application_data else employee.personal_info.phone
            },
            "onboarding_info": {
                "session_id": onboarding_session.id,
                "token": onboarding_session.token,
                "status": onboarding_session.status.value,
                "current_step": onboarding_session.current_step.value,
                "phase": onboarding_session.phase.value,
                "progress_percentage": onboarding_session.progress_percentage,
                "expires_at": onboarding_session.expires_at.isoformat() if onboarding_session.expires_at else None
            }
        }
        
        # Create audit entry
        audit_entry = AuditEntry(
            entity_type="onboarding_session",
            entity_id=onboarding_session.id,
            action="welcome_page_token_access",
            user_id="token_access",
            timestamp=datetime.utcnow(),
            changes={"token_used": token[:8] + "..."}  # Log partial token for security
        )
        database["audit_trail"].append(audit_entry)
        
        return welcome_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get welcome data by token {token[:8]}...: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get welcome data: {str(e)}")

@app.post("/api/onboarding/initiate/{application_id}")
async def initiate_onboarding(
    application_id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """
    Initiate onboarding for an approved application
    """
    try:
        # Validate application exists and is approved
        if application_id not in database["applications"]:
            raise HTTPException(status_code=404, detail="Application not found")
        
        application = database["applications"][application_id]
        if application.status != ApplicationStatus.APPROVED:
            raise HTTPException(status_code=400, detail="Application must be approved before onboarding")
        
        # Find or create employee record
        employee_id = None
        for emp_id, employee in database["employees"].items():
            if employee.application_id == application_id:
                employee_id = emp_id
                break
        
        if not employee_id:
            # Create employee record from application
            employee_id = str(uuid.uuid4())
            employee = Employee(
                id=employee_id,
                user_id=str(uuid.uuid4()),
                application_id=application_id,
                property_id=application.property_id,
                manager_id=current_user.id if current_user.role == UserRole.MANAGER else application.property_id,
                department=application.department,
                position=application.position,
                hire_date=date.today(),
                personal_info=application.applicant_data,
                onboarding_status=OnboardingStatus.NOT_STARTED
            )
            database["employees"][employee_id] = employee
        
        # Get manager ID
        manager_id = current_user.id if current_user.role == UserRole.MANAGER else application.property_id
        
        # Initiate onboarding session
        session = onboarding_orchestrator.initiate_onboarding(
            application_id=application_id,
            employee_id=employee_id,
            property_id=application.property_id,
            manager_id=manager_id
        )
        
        return {
            "success": True,
            "session_id": session.id,
            "onboarding_token": session.token,
            "onboarding_url": f"/onboarding/{session.token}",
            "expires_at": session.expires_at.isoformat(),
            "employee_id": employee_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate onboarding: {str(e)}")

@app.get("/api/onboarding/session/{token}")
async def get_onboarding_session(token: str):
    """
    Get onboarding session by token (public access for employee)
    """
    try:
        session = onboarding_orchestrator.get_session_by_token(token)
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found or expired")
        
        # Get employee info
        employee = database["employees"].get(session.employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get property info
        property_obj = database["properties"].get(session.property_id)
        
        return {
            "session": {
                "id": session.id,
                "status": session.status.value,
                "current_step": session.current_step.value,
                "phase": session.phase.value,
                "progress_percentage": session.progress_percentage,
                "steps_completed": [step.value for step in session.steps_completed],
                "expires_at": session.expires_at.isoformat()
            },
            "employee": {
                "id": employee.id,
                "name": employee.get_full_name(),
                "department": employee.department,
                "position": employee.position
            },
            "property": {
                "name": property_obj.name if property_obj else "Unknown Property",
                "address": property_obj.address if property_obj else ""
            },
            "next_step": onboarding_orchestrator.get_next_step(session.id).value if onboarding_orchestrator.get_next_step(session.id) else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding session: {str(e)}")

@app.post("/api/onboarding/complete-step/{token}")
async def complete_onboarding_step(
    token: str,
    step_data: Dict[str, Any]
):
    """
    Complete an onboarding step (public access for employee)
    """
    try:
        session = onboarding_orchestrator.get_session_by_token(token)
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found or expired")
        
        step = OnboardingStep(step_data.get("step"))
        form_data = step_data.get("form_data")
        signature_data = step_data.get("signature_data")
        
        success = onboarding_orchestrator.complete_step(
            session_id=session.id,
            step=step,
            form_data=form_data,
            signature_data=signature_data,
            user_id=session.employee_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to complete step")
        
        # Get updated session
        updated_session = database["onboarding_sessions"][session.id]
        
        return {
            "success": True,
            "step_completed": step.value,
            "progress_percentage": updated_session.progress_percentage,
            "next_step": onboarding_orchestrator.get_next_step(session.id).value if onboarding_orchestrator.get_next_step(session.id) else None,
            "phase": updated_session.phase.value,
            "status": updated_session.status.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete step: {str(e)}")

@app.get("/api/manager/pending-onboarding")
async def get_pending_manager_reviews(
    current_user: User = Depends(require_manager_role)
):
    """
    Get onboarding sessions pending manager review
    """
    try:
        pending_sessions = onboarding_orchestrator.get_pending_manager_reviews(current_user.id)
        
        result = []
        for session in pending_sessions:
            employee = database["employees"].get(session.employee_id)
            if employee:
                result.append({
                    "session_id": session.id,
                    "employee": {
                        "id": employee.id,
                        "name": employee.get_full_name(),
                        "department": employee.department,
                        "position": employee.position
                    },
                    "status": session.status.value,
                    "current_step": session.current_step.value,
                    "progress_percentage": session.progress_percentage,
                    "employee_completed_at": session.employee_completed_at.isoformat() if session.employee_completed_at else None,
                    "manager_review_started_at": session.manager_review_started_at.isoformat() if session.manager_review_started_at else None
                })
        
        return {"pending_reviews": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending reviews: {str(e)}")

@app.get("/api/hr/pending-approvals")
async def get_pending_hr_approvals(
    current_user: User = Depends(require_hr_role)
):
    """
    Get onboarding sessions pending HR approval
    """
    try:
        pending_sessions = onboarding_orchestrator.get_pending_hr_approvals()
        
        result = []
        for session in pending_sessions:
            employee = database["employees"].get(session.employee_id)
            manager = database["users"].get(session.manager_id)
            property_obj = database["properties"].get(session.property_id)
            
            if employee:
                result.append({
                    "session_id": session.id,
                    "employee": {
                        "id": employee.id,
                        "name": employee.get_full_name(),
                        "department": employee.department,
                        "position": employee.position
                    },
                    "manager": {
                        "name": f"{manager.first_name} {manager.last_name}" if manager else "Unknown"
                    },
                    "property": {
                        "name": property_obj.name if property_obj else "Unknown"
                    },
                    "status": session.status.value,
                    "progress_percentage": session.progress_percentage,
                    "hr_review_started_at": session.hr_review_started_at.isoformat() if session.hr_review_started_at else None
                })
        
        return {"pending_approvals": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending approvals: {str(e)}")

@app.post("/api/manager/approve-onboarding/{session_id}")
async def manager_approve_onboarding(
    session_id: str,
    approval_data: Dict[str, Any],
    current_user: User = Depends(require_manager_role)
):
    """
    Manager approval of onboarding
    """
    try:
        session = database["onboarding_sessions"].get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        if session.manager_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to approve this onboarding")
        
        action = approval_data.get("action", "approve")
        comments = approval_data.get("comments")
        
        if action == "approve":
            success = onboarding_orchestrator.transition_to_hr_approval(session_id, current_user.id)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to approve onboarding")
            
            return {"success": True, "message": "Onboarding approved and sent to HR"}
            
        elif action == "reject":
            reason = approval_data.get("reason", "Manager rejection")
            success = onboarding_orchestrator.reject_onboarding(session_id, current_user.id, reason, comments)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to reject onboarding")
            
            return {"success": True, "message": "Onboarding rejected"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process manager approval: {str(e)}")

@app.post("/api/hr/approve-onboarding/{session_id}")
async def hr_approve_onboarding(
    session_id: str,
    approval_data: Dict[str, Any],
    current_user: User = Depends(require_hr_role)
):
    """
    HR final approval of onboarding
    """
    try:
        session = database["onboarding_sessions"].get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        action = approval_data.get("action", "approve")
        comments = approval_data.get("comments")
        
        if action == "approve":
            success = onboarding_orchestrator.approve_onboarding(session_id, current_user.id, comments)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to approve onboarding")
            
            return {"success": True, "message": "Onboarding fully approved"}
            
        elif action == "reject":
            reason = approval_data.get("reason", "HR rejection")
            success = onboarding_orchestrator.reject_onboarding(session_id, current_user.id, reason, comments)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to reject onboarding")
            
            return {"success": True, "message": "Onboarding rejected"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process HR approval: {str(e)}")

# =====================================
# FORM UPDATE SERVICE ENDPOINTS
# =====================================

@app.post("/api/forms/generate-update-link")
async def generate_form_update_link(
    update_request: Dict[str, Any],
    current_user: User = Depends(require_hr_role)
):
    """
    Generate secure link for individual form update
    """
    try:
        employee_id = update_request.get("employee_id")
        form_type = FormType(update_request.get("form_type"))
        change_reason = update_request.get("change_reason")
        expires_hours = update_request.get("expires_hours", 168)  # 7 days default
        
        if not all([employee_id, form_type, change_reason]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Validate employee exists
        if employee_id not in database["employees"]:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        session = form_update_service.generate_update_link(
            employee_id=employee_id,
            form_type=form_type,
            change_reason=change_reason,
            requested_by=current_user.id,
            expires_hours=expires_hours
        )
        
        return {
            "success": True,
            "session_id": session.id,
            "update_token": session.update_token,
            "update_url": f"/form-update/{session.update_token}",
            "expires_at": session.expires_at.isoformat(),
            "form_type": form_type.value,
            "current_data": session.current_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate update link: {str(e)}")

@app.get("/api/forms/update/{token}")
async def get_form_update_session(token: str):
    """
    Get form update session by token (public access for employee)
    """
    try:
        session = form_update_service.validate_update_token(token)
        if not session:
            raise HTTPException(status_code=404, detail="Form update session not found or expired")
        
        # Get employee info
        employee = database["employees"].get(session.employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return {
            "session": {
                "id": session.id,
                "form_type": session.form_type.value,
                "status": session.status.value,
                "change_reason": session.change_reason,
                "expires_at": session.expires_at.isoformat(),
                "requires_signature": session.requires_signature
            },
            "employee": {
                "id": employee.id,
                "name": employee.get_full_name(),
                "department": employee.department,
                "position": employee.position
            },
            "current_data": session.current_data,
            "updated_data": session.updated_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get form update session: {str(e)}")

@app.post("/api/forms/submit-update/{token}")
async def submit_form_update(
    token: str,
    update_data: Dict[str, Any]
):
    """
    Submit form update data (public access for employee)
    """
    try:
        session = form_update_service.validate_update_token(token)
        if not session:
            raise HTTPException(status_code=404, detail="Form update session not found or expired")
        
        form_data = update_data.get("form_data")
        signature_data = update_data.get("signature_data")
        
        if not form_data:
            raise HTTPException(status_code=400, detail="Form data is required")
        
        success = form_update_service.save_form_update(
            session_id=session.id,
            form_data=form_data,
            signature_data=signature_data,
            user_id=session.employee_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to save form update")
        
        return {
            "success": True,
            "message": "Form update submitted successfully",
            "requires_approval": session.requires_hr_approval or session.requires_manager_approval
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit form update: {str(e)}")

@app.get("/api/manager/pending-form-updates")
async def get_pending_manager_form_updates(
    current_user: User = Depends(require_manager_role)
):
    """
    Get form updates pending manager approval
    """
    try:
        pending_updates = form_update_service.get_pending_approvals(
            approver_role="manager",
            property_id=current_user.property_id
        )
        
        result = []
        for session in pending_updates:
            employee = database["employees"].get(session.employee_id)
            if employee:
                result.append({
                    "session_id": session.id,
                    "form_type": session.form_type.value,
                    "employee": {
                        "id": employee.id,
                        "name": employee.get_full_name(),
                        "department": employee.department,
                        "position": employee.position
                    },
                    "change_reason": session.change_reason,
                    "change_summary": session.change_summary,
                    "requested_at": session.requested_at.isoformat(),
                    "expires_at": session.expires_at.isoformat()
                })
        
        return {"pending_updates": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending form updates: {str(e)}")

@app.get("/api/hr/pending-form-updates")
async def get_pending_hr_form_updates(
    current_user: User = Depends(require_hr_role)
):
    """
    Get form updates pending HR approval
    """
    try:
        pending_updates = form_update_service.get_pending_approvals(approver_role="hr")
        
        result = []
        for session in pending_updates:
            employee = database["employees"].get(session.employee_id)
            property_obj = database["properties"].get(employee.property_id) if employee else None
            
            if employee:
                result.append({
                    "session_id": session.id,
                    "form_type": session.form_type.value,
                    "employee": {
                        "id": employee.id,
                        "name": employee.get_full_name(),
                        "department": employee.department,
                        "position": employee.position
                    },
                    "property": {
                        "name": property_obj.name if property_obj else "Unknown"
                    },
                    "change_reason": session.change_reason,
                    "change_summary": session.change_summary,
                    "requested_at": session.requested_at.isoformat(),
                    "expires_at": session.expires_at.isoformat(),
                    "manager_approved": session.manager_approved_at is not None
                })
        
        return {"pending_updates": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending form updates: {str(e)}")

@app.post("/api/manager/approve-form-update/{session_id}")
async def manager_approve_form_update(
    session_id: str,
    approval_data: Dict[str, Any],
    current_user: User = Depends(require_manager_role)
):
    """
    Manager approval of form update
    """
    try:
        session = database["form_update_sessions"].get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Form update session not found")
        
        # Validate manager has access to this employee
        employee = database["employees"].get(session.employee_id)
        if not employee or employee.property_id != current_user.property_id:
            raise HTTPException(status_code=403, detail="Not authorized to approve this form update")
        
        action = approval_data.get("action", "approve")
        comments = approval_data.get("comments")
        
        if action == "approve":
            success = form_update_service.approve_form_update(
                session_id=session_id,
                approver_id=current_user.id,
                approver_role="manager",
                comments=comments
            )
            if not success:
                raise HTTPException(status_code=400, detail="Failed to approve form update")
            
            return {"success": True, "message": "Form update approved"}
            
        elif action == "reject":
            reason = approval_data.get("reason", "Manager rejection")
            success = form_update_service.reject_form_update(session_id, current_user.id, reason, comments)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to reject form update")
            
            return {"success": True, "message": "Form update rejected"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process manager approval: {str(e)}")

@app.post("/api/hr/approve-form-update/{session_id}")
async def hr_approve_form_update(
    session_id: str,
    approval_data: Dict[str, Any],
    current_user: User = Depends(require_hr_role)
):
    """
    HR approval of form update
    """
    try:
        session = database["form_update_sessions"].get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Form update session not found")
        
        action = approval_data.get("action", "approve")
        comments = approval_data.get("comments")
        
        if action == "approve":
            success = form_update_service.approve_form_update(
                session_id=session_id,
                approver_id=current_user.id,
                approver_role="hr",
                comments=comments
            )
            if not success:
                raise HTTPException(status_code=400, detail="Failed to approve form update")
            
            return {"success": True, "message": "Form update approved and applied"}
            
        elif action == "reject":
            reason = approval_data.get("reason", "HR rejection")
            success = form_update_service.reject_form_update(session_id, current_user.id, reason, comments)
            if not success:
                raise HTTPException(status_code=400, detail="Failed to reject form update")
            
            return {"success": True, "message": "Form update rejected"}
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process HR approval: {str(e)}")

@app.get("/api/employee/{employee_id}/form-update-history")
async def get_employee_form_update_history(
    employee_id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """
    Get form update history for employee
    """
    try:
        # Validate access
        if current_user.role == UserRole.MANAGER:
            employee = database["employees"].get(employee_id)
            if not employee or employee.property_id != current_user.property_id:
                raise HTTPException(status_code=403, detail="Not authorized to view this employee's history")
        
        update_history = form_update_service.get_employee_update_history(employee_id)
        
        result = []
        for session in update_history:
            result.append({
                "session_id": session.id,
                "form_type": session.form_type.value,
                "status": session.status.value,
                "change_reason": session.change_reason,
                "change_summary": session.change_summary,
                "requested_at": session.requested_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "requested_by": session.requested_by,
                "manager_approved": session.manager_approved_at is not None,
                "hr_approved": session.hr_approved_at is not None
            })
        
        return {"update_history": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get form update history: {str(e)}")

# Onboarding Welcome Endpoint (Task 3)
@app.get("/api/onboarding/welcome/{token}")
async def get_onboarding_welcome(token: str):
    """
    Get onboarding welcome page data using secure token
    This endpoint supports Task 3 welcome page functionality
    """
    try:
        # Verify the onboarding token
        result = token_manager.verify_onboarding_token(token)
        
        if not result.get("valid"):
            error_code = result.get("error_code", "INVALID_TOKEN")
            if error_code == "TOKEN_EXPIRED":
                raise HTTPException(status_code=401, detail="Onboarding link has expired")
            else:
                raise HTTPException(status_code=401, detail="Invalid onboarding link")
        
        employee_id = result["employee_id"]
        
        # Get employee information
        employee = database["employees"].get(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get property information
        property_obj = database["properties"].get(employee.property_id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Get user information
        user = database["users"].get(employee.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find active onboarding session
        onboarding_session = None
        for session in database["onboarding_sessions"].values():
            if (session.employee_id == employee_id and 
                session.status in [OnboardingStatus.IN_PROGRESS, OnboardingStatus.NOT_STARTED]):
                onboarding_session = session
                break
        
        if not onboarding_session:
            # Create a new onboarding session if none exists
            session_id = str(uuid.uuid4())
            onboarding_session = OnboardingSession(
                id=session_id,
                employee_id=employee_id,
                property_id=employee.property_id,
                manager_id=employee.manager_id,
                status=OnboardingStatus.NOT_STARTED,
                current_step="welcome",
                phase="employee",
                started_at=datetime.now(timezone.utc),
                form_completion_data={},
                audit_trail=[]
            )
            database["onboarding_sessions"][session_id] = onboarding_session
        
        # Prepare welcome page data
        welcome_data = {
            "success": True,
            "token": token,
            "employee": {
                "id": employee.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "department": employee.department,
                "position": employee.position,
                "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
                "employment_type": employee.employment_type,
                "pay_rate": employee.pay_rate
            },
            "property": {
                "id": property_obj.id,
                "name": property_obj.name,
                "address": property_obj.address,
                "city": property_obj.city,
                "state": property_obj.state,
                "phone": property_obj.phone
            },
            "onboarding": {
                "session_id": onboarding_session.id,
                "status": onboarding_session.status.value,
                "current_step": onboarding_session.current_step,
                "phase": onboarding_session.phase,
                "progress_percentage": 0,  # Will be calculated based on completed forms
                "estimated_completion_time": "45-60 minutes",
                "forms_to_complete": [
                    "Personal Information",
                    "I-9 Employment Eligibility Verification",
                    "W-4 Tax Withholding",
                    "Emergency Contacts",
                    "Direct Deposit Information",
                    "Health Insurance Enrollment",
                    "Company Policies Acknowledgment",
                    "Human Trafficking Awareness",
                    "Weapons Policy Agreement",
                    "Background Check Authorization"
                ]
            },
            "welcome_message": {
                "title": f"Welcome to {property_obj.name}!",
                "subtitle": f"Complete your onboarding for {employee.position}",
                "description": "We're excited to have you join our team! Please complete the following forms to finalize your employment. All information is secure and confidential.",
                "next_steps": "Click 'Begin Onboarding' to start the process. You can save your progress and return at any time using this link."
            },
            "support": {
                "contact_email": "hr@hoteltest.com",
                "contact_phone": property_obj.phone,
                "help_text": "If you have any questions or need assistance, please contact our HR team."
            }
        }
        
        return welcome_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load onboarding welcome: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)