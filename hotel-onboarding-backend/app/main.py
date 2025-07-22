from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid
import json
import os
import base64
from groq import Groq
from dotenv import load_dotenv

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
    "signatures": {}
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

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    if token not in database["users"]:
        raise HTTPException(status_code=401, detail="Invalid token")
    return database["users"][token]

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
