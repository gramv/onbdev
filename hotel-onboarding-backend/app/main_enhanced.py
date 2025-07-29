#!/usr/bin/env python3
"""
Hotel Employee Onboarding System API - Supabase Only Version
Enhanced with standardized API response formats
"""
from fastapi import FastAPI, HTTPException, Depends, Form, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta, timezone
import uuid
import json
import os
import jwt
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Import our enhanced models and authentication
from .models import *
from .models_enhanced import *
from .auth import OnboardingTokenManager, PasswordManager
from .services.onboarding_orchestrator import OnboardingOrchestrator
from .services.form_update_service import FormUpdateService

# Import Supabase service and email service
from .supabase_service_enhanced import EnhancedSupabaseService
from .email_service import email_service

# Import standardized response system
from .response_models import *
from .response_utils import (
    ResponseFormatter, ResponseMiddleware, success_response, error_response,
    not_found_response, unauthorized_response, forbidden_response,
    validation_error_response, standardize_response, ErrorCode
)

load_dotenv()

app = FastAPI(
    title="Hotel Employee Onboarding System",
    description="Supabase-powered onboarding system with standardized API responses",
    version="3.0.0"
)

# Add response standardization middleware
app.add_middleware(ResponseMiddleware)

# Add custom exception handlers
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with standardized response format"""
    error_code_map = {
        400: ErrorCode.VALIDATION_ERROR,
        401: ErrorCode.AUTHENTICATION_ERROR,
        403: ErrorCode.AUTHORIZATION_ERROR,
        404: ErrorCode.RESOURCE_NOT_FOUND,
        409: ErrorCode.RESOURCE_CONFLICT,
        422: ErrorCode.VALIDATION_ERROR,
        429: ErrorCode.RATE_LIMIT_EXCEEDED,
        500: ErrorCode.INTERNAL_SERVER_ERROR
    }
    
    error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_SERVER_ERROR)
    
    return error_response(
        message=exc.detail,
        error_code=error_code,
        status_code=exc.status_code,
        detail=exc.detail
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with standardized response format"""
    field_errors = {}
    for error in exc.errors():
        field_name = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body' prefix
        error_msg = error["msg"]
        
        if field_name not in field_errors:
            field_errors[field_name] = []
        field_errors[field_name].append(error_msg)
    
    return error_response(
        message="Request validation failed",
        error_code=ErrorCode.VALIDATION_ERROR,
        status_code=422,
        detail="One or more request fields are invalid"
    )

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
token_manager = OnboardingTokenManager()
password_manager = PasswordManager()
security = HTTPBearer()
supabase_service = EnhancedSupabaseService()

# Initialize enhanced services
onboarding_orchestrator = None
form_update_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global onboarding_orchestrator, form_update_service
    
    # Initialize enhanced services (supabase_service is already initialized in __init__)
    onboarding_orchestrator = OnboardingOrchestrator(supabase_service)
    form_update_service = FormUpdateService(supabase_service)
    
    # Initialize test data
    await initialize_test_data()
    print("✅ Supabase-enabled backend started successfully")

async def initialize_test_data():
    """Initialize Supabase database with test data"""
    try:
        existing_users = await supabase_service.get_users()
        if len(existing_users) >= 2:
            return
        
        # Hash passwords properly
        hr_password_hash = supabase_service.hash_password("admin123")
        manager_password_hash = supabase_service.hash_password("manager123")
        
        # Create HR user with hashed password
        hr_user_data = {
            "id": "hr_test_001",
            "email": "hr@hoteltest.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "hr",
            "password_hash": hr_password_hash,
            "is_active": True
        }
        await supabase_service.create_user(hr_user_data)
        
        # Create manager user with hashed password
        manager_user_data = {
            "id": "mgr_test_001", 
            "email": "manager@hoteltest.com",
            "first_name": "Mike",
            "last_name": "Wilson",
            "role": "manager",
            "password_hash": manager_password_hash,
            "is_active": True
        }
        await supabase_service.create_user(manager_user_data)
        
        # Create test property
        property_data = {
            "id": "prop_test_001",
            "name": "Grand Plaza Hotel",
            "address": "123 Main Street",
            "city": "Downtown",
            "state": "CA",
            "zip_code": "90210",
            "phone": "(555) 123-4567",
            "is_active": True
        }
        await supabase_service.create_property(property_data)
        await supabase_service.assign_manager_to_property("mgr_test_001", "prop_test_001")
        
        # Store passwords in memory manager for backward compatibility
        password_manager.store_password("hr@hoteltest.com", "admin123")
        password_manager.store_password("manager@hoteltest.com", "manager123")
        
        logger.info("✅ Test data initialized with proper password hashing")
        
    except Exception as e:
        logger.error(f"Test data initialization error: {e}")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """JWT token validation with Supabase lookup"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY", "fallback-secret"), algorithms=["HS256"])
        token_type = payload.get("token_type")
        
        if token_type == "manager_auth":
            manager_id = payload.get("manager_id")
            user = supabase_service.get_user_by_id_sync(manager_id)
            if not user or user.role != "manager":
                raise HTTPException(
                    status_code=401, 
                    detail="Manager not found"
                )
            return user
            
        elif token_type == "hr_auth":
            user_id = payload.get("user_id")
            user = supabase_service.get_user_by_id_sync(user_id)
            if not user or user.role != "hr":
                raise HTTPException(
                    status_code=401, 
                    detail="HR user not found"
                )
            return user
        
        raise HTTPException(
            status_code=401, 
            detail="Invalid token type"
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401, 
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid token"
        )

def require_manager_role(current_user: User = Depends(get_current_user)) -> User:
    """Require manager role"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=403, 
            detail="Manager access required"
        )
    return current_user

def require_hr_role(current_user: User = Depends(get_current_user)) -> User:
    """Require HR role"""
    if current_user.role != "hr":
        raise HTTPException(
            status_code=403, 
            detail="HR access required"
        )
    return current_user

def require_hr_or_manager_role(current_user: User = Depends(get_current_user)) -> User:
    """Require HR or Manager role"""
    if current_user.role not in ["hr", "manager"]:
        raise HTTPException(
            status_code=403, 
            detail="HR or Manager access required"
        )
    return current_user

@app.get("/healthz")
async def healthz():
    """Health check with Supabase status"""
    try:
        connection_status = await supabase_service.health_check()
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "3.0.0",
            "database": "supabase",
            "connection": connection_status
        }
        return success_response(data=health_data)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return error_response(
            message="Health check failed",
            error_code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=503,
            detail=str(e)
        )

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: Request):
    """Login with Supabase user lookup"""
    try:
        body = await request.json()
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")
        
        if not email or not password:
            return error_response(
                message="Email and password are required",
                error_code=ErrorCode.VALIDATION_ERROR,
                status_code=400,
                detail="Both email and password fields must be provided"
            )
        
        # Find user in Supabase
        existing_user = supabase_service.get_user_by_email_sync(email)
        if not existing_user:
            return error_response(
                message="Invalid credentials",
                error_code=ErrorCode.AUTHENTICATION_ERROR,
                status_code=401,
                detail="Email or password is incorrect"
            )
        
        # Verify password from Supabase stored hash
        if not existing_user.password_hash:
            return error_response(
                message="Invalid credentials",
                error_code=ErrorCode.AUTHENTICATION_ERROR,
                status_code=401,
                detail="Account not properly configured"
            )
        
        # Use the enhanced supabase service password verification
        if not supabase_service.verify_password(password, existing_user.password_hash):
            return error_response(
                message="Invalid credentials",
                error_code=ErrorCode.AUTHENTICATION_ERROR,
                status_code=401,
                detail="Email or password is incorrect"
            )
        
        # Generate token
        if existing_user.role == "manager":
            manager_properties = supabase_service.get_manager_properties_sync(existing_user.id)
            if not manager_properties:
                return error_response(
                    message="Manager not configured",
                    error_code=ErrorCode.AUTHORIZATION_ERROR,
                    status_code=403,
                    detail="Manager account is not assigned to any property"
                )
            
            expire = datetime.now(timezone.utc) + timedelta(hours=24)
            payload = {
                "manager_id": existing_user.id,
                "role": existing_user.role,
                "token_type": "manager_auth",
                "exp": expire
            }
            token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY", "fallback-secret"), algorithm="HS256")
            
        elif existing_user.role == "hr":
            expire = datetime.now(timezone.utc) + timedelta(hours=24)
            payload = {
                "user_id": existing_user.id,
                "role": existing_user.role,
                "token_type": "hr_auth",
                "exp": expire
            }
            token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY", "fallback-secret"), algorithm="HS256")
        else:
            return error_response(
                message="Role not authorized",
                error_code=ErrorCode.AUTHORIZATION_ERROR,
                status_code=403,
                detail=f"Role '{existing_user.role}' is not authorized for login"
            )
        
        login_data = LoginResponseData(
            token=token,
            user={
                "id": existing_user.id,
                "email": existing_user.email,
                "role": existing_user.role,
                "first_name": existing_user.first_name,
                "last_name": existing_user.last_name
            },
            expires_at=expire.isoformat(),
            token_type="Bearer"
        )
        
        return success_response(
            data=login_data.model_dump(),
            message="Login successful"
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return error_response(
            message="Login failed",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=500,
            detail="An unexpected error occurred during login"
        )

@app.post("/auth/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh JWT token for authenticated user using Supabase"""
    try:
        # Generate new token based on user role
        if current_user.role == "manager":
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            if not manager_properties:
                return error_response(
                    message="Manager not configured",
                    error_code=ErrorCode.AUTHORIZATION_ERROR,
                    status_code=403,
                    detail="Manager account is not assigned to any property"
                )
            
            expire = datetime.now(timezone.utc) + timedelta(hours=24)
            payload = {
                "manager_id": current_user.id,
                "role": current_user.role,
                "token_type": "manager_auth",
                "exp": expire
            }
            token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY", "fallback-secret"), algorithm="HS256")
            
        elif current_user.role == "hr":
            expire = datetime.now(timezone.utc) + timedelta(hours=24)
            payload = {
                "user_id": current_user.id,
                "role": current_user.role,
                "token_type": "hr_auth",
                "exp": expire
            }
            token = jwt.encode(payload, os.getenv("JWT_SECRET_KEY", "fallback-secret"), algorithm="HS256")
        else:
            return error_response(
                message="Role not authorized",
                error_code=ErrorCode.AUTHORIZATION_ERROR,
                status_code=403,
                detail=f"Role '{current_user.role}' is not authorized for token refresh"
            )
        
        refresh_data = {
            "token": token,
            "expires_at": expire.isoformat(),
            "token_type": "Bearer"
        }
        
        return success_response(
            data=refresh_data,
            message="Token refreshed successfully"
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return error_response(
            message="Token refresh failed",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=500,
            detail="An unexpected error occurred during token refresh"
        )

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (token invalidation handled client-side)"""
    return success_response(
        message="Logged out successfully"
    )

@app.get("/auth/me", response_model=UserInfoResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    user_data = UserInfoData(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        property_id=current_user.property_id
    )
    
    return success_response(
        data=user_data.model_dump(),
        message="User information retrieved successfully"
    )

@app.get("/manager/applications", response_model=ApplicationsResponse)
async def get_manager_applications(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    current_user: User = Depends(require_manager_role)
):
    """Get applications for manager's property using Supabase"""
    try:
        # Get manager's properties from Supabase
        manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
        if not manager_properties:
            return success_response(
                data=[],
                message="No applications found - manager not assigned to any property"
            )
        
        property_id = manager_properties[0].id
        
        # Get applications from Supabase
        applications = await supabase_service.get_applications_by_property(property_id)
        
        # Apply filters
        if search:
            search_lower = search.lower()
            applications = [app for app in applications if 
                          search_lower in app.applicant_data.get('first_name', '').lower() or
                          search_lower in app.applicant_data.get('last_name', '').lower() or
                          search_lower in app.applicant_data.get('email', '').lower()]
        
        if status and status != 'all':
            applications = [app for app in applications if app.status == status]
        
        if department and department != 'all':
            applications = [app for app in applications if app.department == department]
        
        # Convert to standardized format
        result = []
        for app in applications:
            app_data = ApplicationData(
                id=app.id,
                property_id=app.property_id,
                department=app.department,
                position=app.position,
                applicant_data=app.applicant_data,
                status=app.status,
                applied_at=app.applied_at.isoformat(),
                reviewed_by=getattr(app, 'reviewed_by', None),
                reviewed_at=getattr(app, 'reviewed_at', None).isoformat() if getattr(app, 'reviewed_at', None) else None
            )
            result.append(app_data.model_dump())
        
        return success_response(
            data=result,
            message=f"Retrieved {len(result)} applications for manager"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve manager applications: {e}")
        return error_response(
            message="Failed to retrieve applications",
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            detail="An error occurred while fetching applications data"
        )

@app.get("/hr/dashboard-stats", response_model=DashboardStatsResponse)
async def get_hr_dashboard_stats(current_user: User = Depends(require_hr_role)):
    """Get dashboard statistics for HR using Supabase"""
    try:
        # Get counts from Supabase
        total_properties = await supabase_service.get_properties_count()
        total_managers = await supabase_service.get_managers_count()
        total_employees = await supabase_service.get_employees_count()
        pending_applications = await supabase_service.get_pending_applications_count()
        
        stats_data = DashboardStatsData(
            totalProperties=total_properties,
            totalManagers=total_managers,
            totalEmployees=total_employees,
            pendingApplications=pending_applications
        )
        
        return success_response(
            data=stats_data.model_dump(),
            message="Dashboard statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve HR dashboard stats: {e}")
        return error_response(
            message="Failed to retrieve dashboard statistics",
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            detail="An error occurred while fetching dashboard data"
        )

@app.get("/hr/properties", response_model=PropertiesResponse)
async def get_hr_properties(current_user: User = Depends(require_hr_role)):
    """Get all properties for HR using Supabase"""
    try:
        properties = await supabase_service.get_all_properties()
        
        # Convert to standardized format
        result = []
        for prop in properties:
            # Get manager assignments for this property
            try:
                manager_response = supabase_service.client.table('manager_properties').select('manager_id').eq('property_id', prop.id).execute()
                manager_ids = [row['manager_id'] for row in manager_response.data]
            except Exception:
                manager_ids = []
            
            # Generate QR code URL for job applications
            base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            qr_code_url = f"{base_url}/apply/{prop.id}"
            
            property_data = PropertyData(
                id=prop.id,
                name=prop.name,
                address=prop.address,
                city=prop.city,
                state=prop.state,
                zip_code=prop.zip_code,
                phone=prop.phone,
                manager_ids=manager_ids,
                qr_code_url=qr_code_url,
                is_active=prop.is_active,
                created_at=prop.created_at.isoformat() if prop.created_at else None
            )
            result.append(property_data.model_dump())
        
        return success_response(
            data=result,
            message=f"Retrieved {len(result)} properties"
        )
        
    except Exception as e:
        logger.error(f"Failed to retrieve HR properties: {e}")
        return error_response(
            message="Failed to retrieve properties",
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            detail="An error occurred while fetching properties data"
        )

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
    """Create a new property (HR only) using Supabase"""
    try:
        property_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "phone": phone,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = await supabase_service.create_property(property_data)
        
        return {
            "message": "Property created successfully",
            "property": result.get("property", property_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create property: {str(e)}")

@app.put("/hr/properties/{id}")
async def update_property(
    id: str,
    name: str = Form(...),
    address: str = Form(...), 
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
    phone: str = Form(""),
    current_user: User = Depends(require_hr_role)
):
    """Update an existing property (HR only) using Supabase"""
    try:
        # Check if property exists
        property_obj = supabase_service.get_property_by_id_sync(id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Update property
        update_data = {
            "name": name,
            "address": address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "phone": phone
        }
        
        result = supabase_service.client.table('properties').update(update_data).eq('id', id).execute()
        
        return {
            "message": "Property updated successfully",
            "property": {**update_data, "id": id}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update property: {str(e)}")

@app.delete("/hr/properties/{id}")
async def delete_property(
    id: str,
    current_user: User = Depends(require_hr_role)
):
    """Delete a property (HR only) using Supabase"""
    try:
        # Check if property exists
        property_obj = supabase_service.get_property_by_id_sync(id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Check for active applications or employees
        applications = await supabase_service.get_applications_by_property(id)
        employees = await supabase_service.get_employees_by_property(id)
        
        active_applications = [app for app in applications if app.status == "pending"]
        active_employees = [emp for emp in employees if emp.employment_status == "active"]
        
        if active_applications or active_employees:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete property with active applications or employees"
            )
        
        # Delete property
        result = supabase_service.client.table('properties').delete().eq('id', id).execute()
        
        return {"message": "Property deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete property: {str(e)}")

@app.get("/hr/properties/{id}/managers")
async def get_property_managers(
    id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get all managers assigned to a property using Supabase"""
    try:
        # Verify property exists
        property_obj = supabase_service.get_property_by_id_sync(id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Get manager assignments for this property
        response = supabase_service.client.table('manager_properties').select('manager_id').eq('property_id', id).execute()
        
        manager_ids = [row['manager_id'] for row in response.data]
        
        # Get manager details
        managers = []
        for manager_id in manager_ids:
            manager = supabase_service.get_user_by_id_sync(manager_id)
            if manager and manager.role == "manager":
                managers.append({
                    "id": manager.id,
                    "email": manager.email,
                    "first_name": manager.first_name,
                    "last_name": manager.last_name,
                    "is_active": manager.is_active,
                    "created_at": manager.created_at.isoformat() if manager.created_at else None
                })
        
        return managers
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get property managers: {str(e)}")

@app.post("/hr/properties/{id}/managers")
async def assign_manager_to_property(
    id: str,
    manager_id: str = Form(...),
    current_user: User = Depends(require_hr_role)
):
    """Assign a manager to a property (HR only) using Supabase"""
    try:
        # Verify property exists
        property_obj = supabase_service.get_property_by_id_sync(id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Verify manager exists and is a manager
        manager = supabase_service.get_user_by_id_sync(manager_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        if manager.role != "manager":
            raise HTTPException(status_code=400, detail="User is not a manager")
        
        if not manager.is_active:
            raise HTTPException(status_code=400, detail="Cannot assign inactive manager")
        
        # Check if already assigned
        existing = supabase_service.client.table('manager_properties').select('*').eq('manager_id', manager_id).eq('property_id', id).execute()
        
        if existing.data:
            return {
                "success": False,
                "message": "Manager is already assigned to this property"
            }
        
        # Create assignment
        assignment_data = {
            "manager_id": manager_id,
            "property_id": id,
            "assigned_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase_service.client.table('manager_properties').insert(assignment_data).execute()
        
        return {
            "success": True,
            "message": "Manager assigned to property successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign manager: {str(e)}")

@app.delete("/hr/properties/{id}/managers/{manager_id}")
async def remove_manager_from_property(
    id: str,
    manager_id: str,
    current_user: User = Depends(require_hr_role)
):
    """Remove a manager from a property (HR only) using Supabase"""
    try:
        # Verify property and manager exist
        property_obj = supabase_service.get_property_by_id_sync(id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        manager = supabase_service.get_user_by_id_sync(manager_id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Remove assignment
        result = supabase_service.client.table('manager_properties').delete().eq('manager_id', manager_id).eq('property_id', id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Manager assignment not found")
        
        return {
            "success": True,
            "message": "Manager removed from property successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove manager: {str(e)}")

@app.get("/hr/applications", response_model=ApplicationsResponse)
async def get_hr_applications(
    property_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("applied_at"),
    sort_order: Optional[str] = Query("desc"),
    limit: Optional[int] = Query(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get applications with advanced filtering for HR/Manager using Supabase"""
    try:
        # Get applications based on user role
        if current_user.role == "manager":
            # Manager can only see applications for their properties
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            if not manager_properties:
                return []
            property_ids = [prop.id for prop in manager_properties]
            applications = await supabase_service.get_applications_by_properties(property_ids)
        else:
            # HR can see all applications or filter by property
            if property_id:
                applications = await supabase_service.get_applications_by_property(property_id)
            else:
                applications = await supabase_service.get_all_applications()
        
        # Apply filters
        if status:
            applications = [app for app in applications if app.status == status]
        
        if department:
            applications = [app for app in applications if app.department.lower() == department.lower()]
        
        if position:
            applications = [app for app in applications if app.position.lower() == position.lower()]
        
        if search:
            search_lower = search.lower()
            applications = [app for app in applications if 
                          search_lower in app.applicant_data.get('first_name', '').lower() or
                          search_lower in app.applicant_data.get('last_name', '').lower() or
                          search_lower in app.applicant_data.get('email', '').lower()]
        
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
        
        # Sort applications
        reverse = sort_order.lower() == "desc"
        if sort_by == "applied_at":
            applications.sort(key=lambda x: x.applied_at, reverse=reverse)
        elif sort_by == "name":
            applications.sort(key=lambda x: f"{x.applicant_data.get('first_name', '')} {x.applicant_data.get('last_name', '')}", reverse=reverse)
        elif sort_by == "status":
            applications.sort(key=lambda x: x.status, reverse=reverse)
        
        # Apply limit
        if limit:
            applications = applications[:limit]
        
        # Convert to standardized format
        result = []
        for app in applications:
            app_data = ApplicationData(
                id=app.id,
                property_id=app.property_id,
                department=app.department,
                position=app.position,
                applicant_data=app.applicant_data,
                status=app.status,
                applied_at=app.applied_at.isoformat(),
                reviewed_by=getattr(app, 'reviewed_by', None),
                reviewed_at=getattr(app, 'reviewed_at', None).isoformat() if getattr(app, 'reviewed_at', None) else None
            )
            result.append(app_data.model_dump())
        
        return success_response(
            data=result,
            message=f"Retrieved {len(result)} applications"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve HR applications: {e}")
        return error_response(
            message="Failed to retrieve applications",
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            detail="An error occurred while fetching applications data"
        )

@app.get("/manager/property")
async def get_manager_property(current_user: User = Depends(require_manager_role)):
    """Get manager's assigned property details using Supabase"""
    try:
        # Get manager's properties
        manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
        if not manager_properties:
            raise HTTPException(status_code=404, detail="Manager not assigned to any property")
        
        # Return the first property (assuming single property assignment for now)
        property_obj = manager_properties[0]
        
        return {
            "id": property_obj.id,
            "name": property_obj.name,
            "address": property_obj.address,
            "city": property_obj.city,
            "state": property_obj.state,
            "zip_code": property_obj.zip_code,
            "phone": property_obj.phone,
            "is_active": property_obj.is_active,
            "created_at": property_obj.created_at.isoformat() if property_obj.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve manager property: {str(e)}")

@app.get("/manager/dashboard-stats")
async def get_manager_dashboard_stats(current_user: User = Depends(require_manager_role)):
    """Get dashboard statistics for manager's property using Supabase"""
    try:
        # Get manager's properties
        manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
        if not manager_properties:
            raise HTTPException(status_code=404, detail="Manager not assigned to any property")
        
        property_id = manager_properties[0].id
        
        # Get applications and employees for this property
        applications = await supabase_service.get_applications_by_property(property_id)
        employees = await supabase_service.get_employees_by_property(property_id)
        
        # Calculate stats
        pending_applications = len([app for app in applications if app.status == "pending"])
        approved_applications = len([app for app in applications if app.status == "approved"])
        total_employees = len(employees)
        active_employees = len([emp for emp in employees if emp.employment_status == "active"])
        onboarding_in_progress = len([emp for emp in employees if emp.onboarding_status == OnboardingStatus.IN_PROGRESS])
        
        return {
            "pendingApplications": pending_applications,
            "approvedApplications": approved_applications,
            "totalApplications": len(applications),
            "totalEmployees": total_employees,
            "activeEmployees": active_employees,
            "onboardingInProgress": onboarding_in_progress
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve manager dashboard stats: {str(e)}")

@app.get("/api/employees/{id}/welcome-data")
async def get_employee_welcome_data(
    id: str,
    token: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get comprehensive welcome data for the onboarding welcome page using Supabase"""
    try:
        # For now, implement basic functionality to get employee data
        employee = await supabase_service.get_employee_by_id(id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get property information
        property_obj = supabase_service.get_property_by_id_sync(employee.property_id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return {
            "employee": {
                "id": employee.id,
                "department": employee.department,
                "position": employee.position,  
                "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
                "pay_rate": employee.pay_rate,
                "employment_type": employee.employment_type
            },
            "property": {
                "id": property_obj.id,
                "name": property_obj.name,
                "address": property_obj.address,
                "city": property_obj.city,
                "state": property_obj.state,
                "phone": property_obj.phone
            },
            "applicant_data": {
                "first_name": "Employee",
                "last_name": "User", 
                "email": "employee@hotel.com",
                "phone": "(555) 123-4567"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve welcome data: {str(e)}")

@app.get("/api/employees")
async def get_employees(
    property_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get employees with filtering and search capabilities using Supabase"""
    try:
        # Get employees based on user role
        if current_user.role == "manager":
            # Manager can only see employees from their properties
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            if not manager_properties:
                return []
            property_ids = [prop.id for prop in manager_properties]
            employees = await supabase_service.get_employees_by_properties(property_ids)
        elif current_user.role == "hr":
            # HR can see all employees, optionally filtered by property
            if property_id:
                employees = await supabase_service.get_employees_by_property(property_id)
            else:
                employees = await supabase_service.get_all_employees()
        else:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Apply filters
        if department:
            employees = [emp for emp in employees if emp.department.lower() == department.lower()]
        
        if status:
            employees = [emp for emp in employees if emp.employment_status.lower() == status.lower()]
        
        # Apply search (basic implementation)
        if search:
            search_lower = search.lower()
            employees = [emp for emp in employees if 
                        search_lower in emp.department.lower() or
                        search_lower in emp.position.lower()]
        
        # Convert to dict format for frontend compatibility
        result = []
        for emp in employees:
            result.append({
                "id": emp.id,
                "property_id": emp.property_id,
                "department": emp.department,
                "position": emp.position,
                "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
                "pay_rate": emp.pay_rate,
                "employment_type": emp.employment_type,
                "employment_status": emp.employment_status,
                "onboarding_status": emp.onboarding_status.value if emp.onboarding_status else "not_started"
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employees: {str(e)}")

@app.post("/applications/{id}/approve")
async def approve_application(
    id: str,
    job_title: str = Form(...),
    start_date: str = Form(...),
    start_time: str = Form(...),
    pay_rate: float = Form(...),
    pay_frequency: str = Form(...),
    benefits_eligible: str = Form(...),
    supervisor: str = Form(...),
    special_instructions: str = Form(""),
    current_user: User = Depends(require_manager_role)
):
    """Approve application using Supabase"""
    try:
        # Get application from Supabase
        application = await supabase_service.get_application_by_id(id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Verify manager access
        manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
        property_ids = [prop.id for prop in manager_properties]
        
        if application.property_id not in property_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update application status
        await supabase_service.update_application_status(id, "approved", current_user.id)
        
        # Create employee record
        employee_data = {
            "application_id": id,
            "property_id": application.property_id,
            "manager_id": current_user.id,
            "department": application.department,
            "position": job_title,
            "hire_date": start_date,
            "pay_rate": pay_rate,
            "pay_frequency": pay_frequency,
            "employment_type": application.applicant_data.get("employment_type", "full_time"),
            "personal_info": {
                "job_title": job_title,
                "start_time": start_time,
                "benefits_eligible": benefits_eligible,
                "supervisor": supervisor,
                "special_instructions": special_instructions
            },
            "onboarding_status": "not_started"
        }
        
        employee = await supabase_service.create_employee(employee_data)
        
        # Create onboarding session
        onboarding_session = await onboarding_orchestrator.initiate_onboarding(
            application_id=id,
            employee_id=employee.id,
            property_id=application.property_id,
            manager_id=current_user.id,
            expires_hours=72
        )
        
        # Move competing applications to talent pool
        talent_pool_count = await supabase_service.move_competing_applications_to_talent_pool(
            application.property_id, application.position, id, current_user.id
        )
        
        # Generate onboarding URL
        base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        onboarding_url = f"{base_url}/onboard?token={onboarding_session.token}"
        
        # Get property and manager info for emails
        property_obj = supabase_service.get_property_by_id_sync(application.property_id)
        manager = supabase_service.get_user_by_id_sync(current_user.id)
        
        # Send approval notification email with job details
        try:
            approval_email_sent = await email_service.send_approval_notification(
                applicant_email=application.applicant_data["email"],
                applicant_name=f"{application.applicant_data['first_name']} {application.applicant_data['last_name']}",
                property_name=property_obj.name if property_obj else "Hotel Property",
                position=application.position,
                job_title=job_title,
                start_date=start_date,
                pay_rate=pay_rate,
                onboarding_link=onboarding_url,
                manager_name=f"{manager.first_name} {manager.last_name}" if manager else "Hiring Manager",
                manager_email=manager.email if manager else "manager@hotel.com"
            )
            
            # Send onboarding welcome email with detailed instructions
            welcome_email_sent = await email_service.send_onboarding_welcome_email(
                employee_email=application.applicant_data["email"],
                employee_name=f"{application.applicant_data['first_name']} {application.applicant_data['last_name']}",
                property_name=property_obj.name if property_obj else "Hotel Property",
                position=job_title,
                onboarding_link=onboarding_url,
                manager_name=f"{manager.first_name} {manager.last_name}" if manager else "Hiring Manager"
            )
            
        except Exception as e:
            print(f"Email sending error: {e}")
            approval_email_sent = False
            welcome_email_sent = False
        
        return {
            "message": "Application approved successfully",
            "employee_id": employee.id,
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
                "message": f"{talent_pool_count} other applications moved to talent pool"
            },
            "email_notifications": {
                "approval_email_sent": approval_email_sent,
                "welcome_email_sent": welcome_email_sent,
                "recipient": application.applicant_data["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

@app.post("/applications/{id}/reject")
async def reject_application(
    id: str,
    rejection_reason: str = Form(...),
    current_user: User = Depends(require_manager_role)
):
    """Reject application with reason (Manager only) using Supabase"""
    try:
        # Get application
        application = await supabase_service.get_application_by_id(id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Verify manager access
        manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
        property_ids = [prop.id for prop in manager_properties]
        
        if application.property_id not in property_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if application.status != "pending":
            raise HTTPException(status_code=400, detail="Application is not pending")
        
        if not rejection_reason.strip():
            raise HTTPException(status_code=400, detail="Rejection reason is required")
        
        # Move to talent pool instead of reject
        await supabase_service.update_application_status(id, "talent_pool", current_user.id)
        
        # Update rejection reason
        update_data = {
            "rejection_reason": rejection_reason.strip(),
            "talent_pool_date": datetime.now(timezone.utc).isoformat()
        }
        supabase_service.client.table('job_applications').update(update_data).eq('id', id).execute()
        
        return {
            "message": "Application moved to talent pool successfully",
            "status": "talent_pool",
            "rejection_reason": rejection_reason.strip()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject application: {str(e)}")

@app.get("/hr/applications/talent-pool")
async def get_talent_pool(
    property_id: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get talent pool applications using Supabase"""
    try:
        # Get talent pool applications
        query = supabase_service.client.table('job_applications').select('*').eq('status', 'talent_pool')
        
        # Filter by property for managers
        if current_user.role == "manager":
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            if not manager_properties:
                return []
            property_ids = [prop.id for prop in manager_properties]
            query = query.in_('property_id', property_ids)
        elif property_id:
            query = query.eq('property_id', property_id)
        
        if position:
            query = query.eq('position', position)
        
        response = query.execute()
        
        applications = []
        for row in response.data:
            # Apply search filter
            if search:
                search_lower = search.lower()
                applicant_data = row.get('applicant_data', {})
                if not (search_lower in applicant_data.get('first_name', '').lower() or
                       search_lower in applicant_data.get('last_name', '').lower() or
                       search_lower in applicant_data.get('email', '').lower()):
                    continue
            
            applications.append({
                "id": row['id'],
                "property_id": row['property_id'],
                "department": row['department'],
                "position": row['position'],
                "applicant_data": row['applicant_data'],
                "status": row['status'],
                "applied_at": row['applied_at'],
                "rejection_reason": row.get('rejection_reason'),
                "talent_pool_date": row.get('talent_pool_date')
            })
        
        return applications
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve talent pool: {str(e)}")

@app.post("/hr/applications/{id}/reactivate")
async def reactivate_application(
    id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Reactivate application from talent pool using Supabase"""
    try:
        # Get application
        application = await supabase_service.get_application_by_id(id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        if application.status != "talent_pool":
            raise HTTPException(status_code=400, detail="Application is not in talent pool")
        
        # Verify access for managers
        if current_user.role == "manager":
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            property_ids = [prop.id for prop in manager_properties]
            if application.property_id not in property_ids:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Reactivate application
        await supabase_service.update_application_status(id, "pending", current_user.id)
        
        # Clear talent pool data
        update_data = {
            "rejection_reason": None,
            "talent_pool_date": None
        }
        supabase_service.client.table('job_applications').update(update_data).eq('id', id).execute()
        
        return {
            "message": "Application reactivated successfully",
            "status": "pending"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reactivate application: {str(e)}")

@app.get("/hr/users")
async def get_hr_users(
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_hr_role)
):
    """Get all users with filtering and search capabilities (HR only) using Supabase"""
    try:
        # Build query for users
        query = supabase_service.client.table('users').select('*')
        
        # Filter by role if specified
        if role:
            query = query.eq('role', role)
        
        # Filter by active status if specified
        if is_active is not None:
            query = query.eq('is_active', is_active)
        
        response = query.execute()
        
        users = []
        for row in response.data:
            # Apply search filter
            if search:
                search_lower = search.lower()
                if not (search_lower in row['email'].lower() or
                       search_lower in (row.get('first_name') or '').lower() or
                       search_lower in (row.get('last_name') or '').lower()):
                    continue
            
            # Get additional info for managers (property assignments)
            property_info = []
            if row['role'] == 'manager':
                try:
                    manager_properties = await supabase_service.get_manager_properties(row['id'])
                    property_info = [
                        {
                            "id": prop.id,
                            "name": prop.name,
                            "city": prop.city,
                            "state": prop.state
                        } for prop in manager_properties
                    ]
                except Exception:
                    # If there's an error getting properties, continue with empty list
                    property_info = []
            
            users.append({
                "id": row['id'],
                "email": row['email'],
                "first_name": row.get('first_name'),
                "last_name": row.get('last_name'),
                "role": row['role'],
                "is_active": row.get('is_active', True),
                "created_at": row.get('created_at'),
                "properties": property_info
            })
        
        return users
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

@app.get("/hr/managers")
async def get_managers(
    property_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_hr_role)
):
    """Get all managers with filtering and search capabilities (HR only) using Supabase"""
    try:
        # Get all manager users
        query = supabase_service.client.table('users').select('*').eq('role', 'manager')
        
        if is_active is not None:
            query = query.eq('is_active', is_active)
        
        response = query.execute()
        
        managers = []
        for row in response.data:
            # Apply search filter
            if search:
                search_lower = search.lower()
                if not (search_lower in row['email'].lower() or
                       search_lower in (row.get('first_name') or '').lower() or
                       search_lower in (row.get('last_name') or '').lower()):
                    continue
            
            # Get manager's properties using service method
            manager_properties = await supabase_service.get_manager_properties(row['id'])
            property_ids = [prop.id for prop in manager_properties]
            
            # Filter by property if specified
            if property_id and property_id not in property_ids:
                continue
            
            # Convert manager properties to property info
            property_info = []
            for prop in manager_properties:
                property_info.append({
                    "id": prop.id,
                    "name": prop.name,
                    "city": prop.city,
                    "state": prop.state
                })
            
            managers.append({
                "id": row['id'],
                "email": row['email'],
                "first_name": row.get('first_name'),
                "last_name": row.get('last_name'),
                "is_active": row.get('is_active', True),
                "created_at": row.get('created_at'),
                "properties": property_info
            })
        
        return managers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve managers: {str(e)}")

@app.get("/hr/employees")
async def get_hr_employees(
    property_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_hr_role)
):
    """Get employees for HR with advanced filtering using Supabase"""
    try:
        # Get all employees or filter by property
        if property_id:
            employees = await supabase_service.get_employees_by_property(property_id)
        else:
            employees = await supabase_service.get_all_employees()
        
        # Apply filters
        if department:
            employees = [emp for emp in employees if emp.department.lower() == department.lower()]
        
        if status:
            employees = [emp for emp in employees if emp.employment_status.lower() == status.lower()]
        
        # Apply search (basic implementation)
        if search:
            search_lower = search.lower()
            employees = [emp for emp in employees if 
                        search_lower in emp.department.lower() or
                        search_lower in emp.position.lower()]
        
        # Convert to dict format for frontend compatibility
        result = []
        for emp in employees:
            # Get property info
            property_obj = supabase_service.get_property_by_id_sync(emp.property_id)
            
            result.append({
                "id": emp.id,
                "property_id": emp.property_id,
                "property_name": property_obj.name if property_obj else "Unknown",
                "department": emp.department,
                "position": emp.position,
                "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
                "pay_rate": emp.pay_rate,
                "employment_type": emp.employment_type,
                "employment_status": emp.employment_status,
                "onboarding_status": emp.onboarding_status.value if emp.onboarding_status else "not_started"
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve HR employees: {str(e)}")

@app.get("/hr/employees/{id}")
async def get_hr_employee_detail(
    id: str,
    current_user: User = Depends(require_hr_role)
):
    """Get detailed employee information for HR using Supabase"""
    try:
        employee = await supabase_service.get_employee_by_id(id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get property info
        property_obj = supabase_service.get_property_by_id_sync(employee.property_id)
        
        return {
            "id": employee.id,
            "property_id": employee.property_id,
            "property_name": property_obj.name if property_obj else "Unknown",
            "department": employee.department,
            "position": employee.position,
            "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
            "pay_rate": employee.pay_rate,
            "employment_type": employee.employment_type,
            "employment_status": employee.employment_status,
            "onboarding_status": employee.onboarding_status.value if employee.onboarding_status else "not_started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve employee details: {str(e)}")

@app.get("/hr/applications/departments")
async def get_application_departments(current_user: User = Depends(require_hr_or_manager_role)):
    """Get list of departments from applications using Supabase"""
    try:
        # Get applications based on user role
        if current_user.role == "manager":
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            if not manager_properties:
                return []
            property_ids = [prop.id for prop in manager_properties]
            applications = await supabase_service.get_applications_by_properties(property_ids)
        else:
            applications = await supabase_service.get_all_applications()
        
        # Extract unique departments
        departments = list(set(app.department for app in applications if app.department))
        departments.sort()
        
        return departments
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve departments: {str(e)}")

@app.get("/hr/applications/positions")
async def get_application_positions(
    department: Optional[str] = Query(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get list of positions from applications, optionally filtered by department using Supabase"""
    try:
        # Get applications based on user role
        if current_user.role == "manager":
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            if not manager_properties:
                return []
            property_ids = [prop.id for prop in manager_properties]
            applications = await supabase_service.get_applications_by_properties(property_ids)
        else:
            applications = await supabase_service.get_all_applications()
        
        # Filter by department if specified
        if department:
            applications = [app for app in applications if app.department.lower() == department.lower()]
        
        # Extract unique positions
        positions = list(set(app.position for app in applications if app.position))
        positions.sort()
        
        return positions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve positions: {str(e)}")

@app.get("/hr/applications/stats")
async def get_application_stats(current_user: User = Depends(require_hr_or_manager_role)):
    """Get application statistics using Supabase"""
    try:
        # Get applications based on user role
        if current_user.role == "manager":
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            if not manager_properties:
                return {"total": 0, "pending": 0, "approved": 0, "talent_pool": 0}
            property_ids = [prop.id for prop in manager_properties]
            applications = await supabase_service.get_applications_by_properties(property_ids)
        else:
            applications = await supabase_service.get_all_applications()
        
        # Calculate stats
        total = len(applications)
        pending = len([app for app in applications if app.status == "pending"])
        approved = len([app for app in applications if app.status == "approved"])
        talent_pool = len([app for app in applications if app.status == "talent_pool"])
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "talent_pool": talent_pool,
            "by_department": {}  # Could be expanded later
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application stats: {str(e)}")

@app.post("/apply/{id}")
async def submit_job_application(id: str, application_data: JobApplicationData):
    """Submit job application to Supabase"""
    try:
        # Validate property exists
        property_obj = supabase_service.get_property_by_id_sync(id)
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        if not property_obj.is_active:
            raise HTTPException(status_code=400, detail="Property not accepting applications")
        
        # Check for duplicates
        existing_applications = supabase_service.get_applications_by_email_and_property_sync(
            application_data.email.lower(), id
        )
        
        for app in existing_applications:
            if app.position == application_data.position and app.status == "pending":
                raise HTTPException(status_code=400, detail="Duplicate application exists")
        
        # Create application
        application_id = str(uuid.uuid4())
        
        job_application = JobApplication(
            id=application_id,
            property_id=id,
            department=application_data.department,
            position=application_data.position,
            applicant_data={
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
            },
            status=ApplicationStatus.PENDING,
            applied_at=datetime.now(timezone.utc)
        )
        
        # Store in Supabase
        created_application = supabase_service.create_application_sync(job_application)
        
        return {
            "success": True,
            "message": "Application submitted successfully!",
            "application_id": application_id,
            "property_name": property_obj.name,
            "position_applied": f"{application_data.position} - {application_data.department}",
            "next_steps": "Our hiring team will review your application and contact you within 3-5 business days."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application submission failed: {str(e)}")

@app.get("/properties/{id}/info")
async def get_property_public_info(id: str):
    """Get property info using Supabase"""
    try:
        property_obj = supabase_service.get_property_by_id_sync(id)
        if not property_obj or not property_obj.is_active:
            raise HTTPException(status_code=404, detail="Property not found")
        
        departments_and_positions = {
            "Front Desk": ["Front Desk Agent", "Night Auditor", "Guest Services Representative", "Concierge"],
            "Housekeeping": ["Housekeeper", "Housekeeping Supervisor", "Laundry Attendant", "Public Area Attendant"],
            "Food & Beverage": ["Server", "Bartender", "Host/Hostess", "Kitchen Staff", "Banquet Server"],
            "Maintenance": ["Maintenance Technician", "Engineering Assistant", "Groundskeeper"]
        }
        
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
            "application_url": f"/apply/{id}",
            "is_accepting_applications": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get property info: {str(e)}")

# ==========================================
# BULK OPERATIONS ENDPOINTS (Phase 1.1)
# ==========================================

@app.post("/hr/applications/bulk-action")
async def bulk_application_action(
    application_ids: List[str] = Form(...),
    action: str = Form(...),
    rejection_reason: Optional[str] = Form(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Perform bulk actions on multiple applications"""
    try:
        if not application_ids:
            raise HTTPException(status_code=400, detail="No application IDs provided")
        
        valid_actions = ["reject", "approve", "talent_pool"]
        if action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
        
        if action == "reject" and not rejection_reason:
            raise HTTPException(status_code=400, detail="Rejection reason required for reject action")
        
        # Use new bulk operation method
        if action == "reject":
            result = await supabase_service.bulk_update_applications(
                application_ids=application_ids,
                status="rejected",
                reviewed_by=current_user.id,
                action_type="reject"
            )
        elif action == "talent_pool":
            result = await supabase_service.bulk_move_to_talent_pool(
                application_ids=application_ids,
                reviewed_by=current_user.id
            )
        elif action == "approve":
            result = await supabase_service.bulk_update_applications(
                application_ids=application_ids,
                status="approved",
                reviewed_by=current_user.id,
                action_type="approve"
            )
        
        return {
            "message": f"Bulk {action} completed",
            "processed": result["total_processed"],
            "successful": result["success_count"],
            "failed": result["failed_count"],
            "errors": result["errors"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk action failed: {str(e)}")

@app.post("/hr/applications/bulk-status-update")
async def bulk_status_update(
    application_ids: List[str] = Form(...),
    new_status: str = Form(...),
    reason: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Perform bulk status updates on multiple applications"""
    try:
        if not application_ids:
            raise HTTPException(status_code=400, detail="No application IDs provided")
        
        # Validate status
        valid_statuses = ["pending", "approved", "rejected", "talent_pool", "hired"]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")
        
        # Use bulk update method
        result = await supabase_service.bulk_update_applications(
            application_ids=application_ids,
            status=new_status,
            reviewed_by=current_user.id,
            action_type="status_update"
        )
        
        # Add status history for each successful update
        for app_id in application_ids:
            if app_id not in [error for error in result.get("errors", []) if app_id in error]:
                await supabase_service.add_application_status_history(
                    application_id=app_id,
                    previous_status="pending",  # You might want to fetch actual previous status
                    new_status=new_status,
                    changed_by=current_user.id,
                    reason=reason,
                    notes=notes
                )
        
        return {
            "message": f"Bulk status update to {new_status} completed",
            "processed": result["total_processed"],
            "successful": result["success_count"],
            "failed": result["failed_count"],
            "errors": result["errors"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk status update failed: {str(e)}")

@app.post("/hr/applications/bulk-reactivate")
async def bulk_reactivate_applications(
    application_ids: List[str] = Form(...),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Reactivate talent pool candidates by moving them back to pending status"""
    try:
        if not application_ids:
            raise HTTPException(status_code=400, detail="No application IDs provided")
        
        result = await supabase_service.bulk_reactivate_applications(
            application_ids=application_ids,
            reviewed_by=current_user.id
        )
        
        # Add status history for successful reactivations
        for app_id in application_ids:
            if app_id not in [error for error in result.get("errors", []) if app_id in error]:
                await supabase_service.add_application_status_history(
                    application_id=app_id,
                    previous_status="talent_pool",
                    new_status="pending",
                    changed_by=current_user.id,
                    reason="Reactivated from talent pool",
                    notes="Candidate reactivated for new opportunity consideration"
                )
        
        return {
            "message": "Bulk reactivation completed",
            "processed": result["total_processed"],
            "successful": result["success_count"],
            "failed": result["failed_count"],
            "errors": result["errors"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk reactivation failed: {str(e)}")

@app.post("/hr/applications/bulk-talent-pool")
async def bulk_move_to_talent_pool(
    application_ids: List[str] = Form(...),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Bulk move applications to talent pool"""
    try:
        if not application_ids:
            raise HTTPException(status_code=400, detail="No application IDs provided")
        
        result = await supabase_service.bulk_move_to_talent_pool(
            application_ids=application_ids,
            reviewed_by=current_user.id
        )
        
        # Add status history for successful moves
        for app_id in application_ids:
            if app_id not in [error for error in result.get("errors", []) if app_id in error]:
                await supabase_service.add_application_status_history(
                    application_id=app_id,
                    previous_status="pending",
                    new_status="talent_pool",
                    changed_by=current_user.id,
                    reason="Moved to talent pool",
                    notes="Application moved to talent pool for future opportunities"
                )
        
        return {
            "message": "Bulk move to talent pool completed",
            "processed": result["total_processed"],
            "successful": result["success_count"],
            "failed": result["failed_count"],
            "errors": result["errors"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk talent pool move failed: {str(e)}")

@app.post("/hr/applications/bulk-talent-pool-notify")
async def bulk_talent_pool_notify(
    application_ids: List[str] = Form(...),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Send email notifications to talent pool candidates about new opportunities"""
    try:
        if not application_ids:
            raise HTTPException(status_code=400, detail="No application IDs provided")
        
        result = await supabase_service.send_bulk_notifications(
            application_ids=application_ids,
            notification_type="talent_pool_opportunity",
            sent_by=current_user.id
        )
        
        return {
            "message": "Bulk talent pool notifications sent",
            "processed": result["total_processed"],
            "successful": result["success_count"],
            "failed": result["failed_count"],
            "errors": result["errors"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk notification failed: {str(e)}")

# ==========================================
# APPLICATION HISTORY & ENHANCED WORKFLOW (Phase 1.2)
# ==========================================

@app.get("/hr/applications/{id}/history")
async def get_application_history(
    id: str,
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get status change history for a specific application"""
    try:
        # Check if application exists
        application = await supabase_service.get_application_by_id(id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Check access permissions for managers
        if current_user.role == UserRole.MANAGER:
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            manager_property_ids = [prop.id for prop in manager_properties]
            if application.property_id not in manager_property_ids:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Get application history
        history = await supabase_service.get_application_history(id)
        
        # Enrich history with user details
        enriched_history = []
        for record in history:
            # Get user info for who made the change
            changed_by_user = await supabase_service.get_user_by_id(record["changed_by"])
            
            enriched_record = {
                "id": record["id"],
                "application_id": record["application_id"],
                "previous_status": record["previous_status"],
                "new_status": record["new_status"],
                "changed_by": record["changed_by"],
                "changed_by_name": f"{changed_by_user.first_name} {changed_by_user.last_name}".strip() if changed_by_user else "Unknown User",
                "changed_by_email": changed_by_user.email if changed_by_user else "unknown@email.com",
                "changed_at": record["changed_at"],
                "reason": record.get("reason"),
                "notes": record.get("notes")
            }
            enriched_history.append(enriched_record)
        
        return {
            "application_id": id,
            "history": enriched_history,
            "total_entries": len(enriched_history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get application history: {str(e)}")

@app.post("/applications/check-duplicate")
async def check_duplicate_application(
    email: str = Form(...),
    property_id: str = Form(...),
    position: str = Form(...)
):
    """Check for duplicate applications (same email + property + position)"""
    try:
        # Check for existing applications
        is_duplicate = await supabase_service.check_duplicate_application(
            email=email.lower(),
            property_id=property_id,
            position=position
        )
        
        return {
            "is_duplicate": is_duplicate,
            "message": "Duplicate application found" if is_duplicate else "No duplicate found",
            "checked_criteria": {
                "email": email.lower(),
                "property_id": property_id,
                "position": position
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check duplicate application: {str(e)}")

# ==========================================
# MANAGER CRUD OPERATIONS (Phase 1.3)
# ==========================================

@app.get("/hr/managers/{id}")
async def get_manager_details(
    id: str,
    current_user: User = Depends(require_hr_role)
):
    """Get manager details by ID (HR only)"""
    try:
        manager = await supabase_service.get_manager_by_id(id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Get manager's properties
        properties = supabase_service.get_manager_properties_sync(id)
        
        return {
            "id": manager.id,
            "email": manager.email,
            "first_name": manager.first_name,
            "last_name": manager.last_name,
            "role": manager.role.value,
            "is_active": manager.is_active,
            "created_at": manager.created_at.isoformat() if manager.created_at else None,
            "assigned_properties": [
                {
                    "id": prop.id,
                    "name": prop.name,
                    "address": prop.address,
                    "city": prop.city,
                    "state": prop.state
                } for prop in properties
            ],
            "properties_count": len(properties)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get manager details: {str(e)}")

@app.put("/hr/managers/{id}")
async def update_manager(
    id: str,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    is_active: bool = Form(True),
    current_user: User = Depends(require_hr_role)
):
    """Update manager details (HR only)"""
    try:
        # Check if manager exists
        existing_manager = await supabase_service.get_manager_by_id(id)
        if not existing_manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Check if email is already in use by another user
        if email.lower() != existing_manager.email.lower():
            existing_user = await supabase_service.get_user_by_email(email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already in use")
        
        # Update manager
        update_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email.lower(),
            "is_active": is_active
        }
        
        updated_manager = await supabase_service.update_manager(id, update_data)
        if not updated_manager:
            raise HTTPException(status_code=500, detail="Failed to update manager")
        
        return {
            "success": True,
            "message": "Manager updated successfully",
            "manager": {
                "id": updated_manager.id,
                "email": updated_manager.email,
                "first_name": updated_manager.first_name,
                "last_name": updated_manager.last_name,
                "role": updated_manager.role.value,
                "is_active": updated_manager.is_active
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update manager: {str(e)}")

@app.delete("/hr/managers/{id}")
async def delete_manager(
    id: str,
    current_user: User = Depends(require_hr_role)
):
    """Delete manager (soft delete) (HR only)"""
    try:
        # Check if manager exists
        manager = await supabase_service.get_manager_by_id(id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Check if manager has any assigned properties
        properties = supabase_service.get_manager_properties_sync(id)
        if properties:
            property_names = [prop.name for prop in properties]
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete manager. Please unassign from properties first: {', '.join(property_names)}"
            )
        
        # Soft delete the manager
        success = await supabase_service.delete_manager(id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete manager")
        
        return {
            "success": True,
            "message": f"Manager {manager.first_name} {manager.last_name} has been deactivated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete manager: {str(e)}")

@app.post("/hr/managers/{id}/reset-password")
async def reset_manager_password(
    id: str,
    new_password: str = Form(...),
    current_user: User = Depends(require_hr_role)
):
    """Reset manager password (HR only)"""
    try:
        # Check if manager exists
        manager = await supabase_service.get_manager_by_id(id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Validate password strength
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Reset password
        success = await supabase_service.reset_manager_password(id, new_password)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset password")
        
        # Store password in password manager for authentication
        password_manager.store_password(manager.email, new_password)
        
        return {
            "success": True,
            "message": f"Password reset successfully for {manager.first_name} {manager.last_name}",
            "manager_email": manager.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset manager password: {str(e)}")

@app.get("/hr/managers/{id}/performance")
async def get_manager_performance(
    id: str,
    current_user: User = Depends(require_hr_role)
):
    """Get manager performance metrics (HR only)"""
    try:
        # Check if manager exists
        manager = await supabase_service.get_manager_by_id(id)
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
        
        # Get performance data
        performance_data = await supabase_service.get_manager_performance(id)
        
        return {
            "manager_id": id,
            "manager_name": f"{manager.first_name} {manager.last_name}",
            "manager_email": manager.email,
            "performance": performance_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get manager performance: {str(e)}")

@app.get("/hr/managers/unassigned")
async def get_unassigned_managers(current_user: User = Depends(require_hr_role)):
    """Get all managers not assigned to any property (HR only)"""
    try:
        unassigned_managers = await supabase_service.get_unassigned_managers()
        
        return {
            "managers": [
                {
                    "id": manager.id,
                    "email": manager.email,
                    "first_name": manager.first_name,
                    "last_name": manager.last_name,
                    "is_active": manager.is_active,
                    "created_at": manager.created_at.isoformat() if manager.created_at else None
                } for manager in unassigned_managers
            ],
            "total": len(unassigned_managers)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unassigned managers: {str(e)}")

# ==========================================
# EMPLOYEE SEARCH & MANAGEMENT (Phase 1.4)
# ==========================================

@app.get("/hr/employees/search")
async def search_employees(
    q: str = Query(...),
    property_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    employment_status: Optional[str] = Query(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Search employees with filters"""
    try:
        # For managers, restrict to their properties only
        if current_user.role == UserRole.MANAGER:
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            manager_property_ids = [prop.id for prop in manager_properties]
            
            if property_id and property_id not in manager_property_ids:
                raise HTTPException(status_code=403, detail="Access denied to this property")
            
            # If no property_id specified, search only in manager's properties
            if not property_id and manager_property_ids:
                property_id = manager_property_ids[0]  # Use first property as default
        
        # Search employees
        employees = await supabase_service.search_employees(
            search_query=q,
            property_id=property_id,
            department=department,
            position=position,
            employment_status=employment_status
        )
        
        # Format response
        formatted_employees = []
        for emp in employees:
            personal_info = emp.personal_info or {}
            formatted_employees.append({
                "id": emp.id,
                "application_id": emp.application_id,
                "property_id": emp.property_id,
                "manager_id": emp.manager_id,
                "department": emp.department,
                "position": emp.position,
                "hire_date": emp.hire_date.isoformat() if emp.hire_date else None,
                "pay_rate": emp.pay_rate,
                "pay_frequency": emp.pay_frequency,
                "employment_type": emp.employment_type,
                "employment_status": getattr(emp, 'employment_status', 'active'),
                "onboarding_status": emp.onboarding_status.value if emp.onboarding_status else "not_started",
                "personal_info": {
                    "first_name": personal_info.get("first_name"),
                    "last_name": personal_info.get("last_name"),
                    "email": personal_info.get("email"),
                    "phone": personal_info.get("phone")
                },
                "created_at": emp.created_at.isoformat() if emp.created_at else None
            })
        
        return {
            "employees": formatted_employees,
            "total": len(formatted_employees),
            "search_criteria": {
                "query": q,
                "property_id": property_id,
                "department": department,
                "position": position,
                "employment_status": employment_status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search employees: {str(e)}")

@app.put("/hr/employees/{employee_id}/status")
async def update_employee_status(
    employee_id: str,
    new_status: str = Form(...),
    reason: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Update employee employment status"""
    try:
        # Check if employee exists
        employee = await supabase_service.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # For managers, check access to employee's property
        if current_user.role == UserRole.MANAGER:
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            manager_property_ids = [prop.id for prop in manager_properties]
            if employee.property_id not in manager_property_ids:
                raise HTTPException(status_code=403, detail="Access denied to this employee")
        
        # Validate status
        valid_statuses = ["active", "inactive", "terminated", "on_leave", "probation"]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # Update employee status
        success = await supabase_service.update_employee_status(
            employee_id=employee_id,
            status=new_status,
            updated_by=current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update employee status")
        
        return {
            "success": True,
            "message": f"Employee status updated to {new_status}",
            "employee_id": employee_id,
            "new_status": new_status,
            "updated_by": f"{current_user.first_name} {current_user.last_name}",
            "reason": reason,
            "notes": notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update employee status: {str(e)}")

@app.get("/hr/employees/stats")
async def get_employee_statistics(
    property_id: Optional[str] = Query(None),
    current_user: User = Depends(require_hr_or_manager_role)
):
    """Get employee statistics"""
    try:
        # For managers, restrict to their properties
        if current_user.role == UserRole.MANAGER:
            manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
            manager_property_ids = [prop.id for prop in manager_properties]
            
            if property_id and property_id not in manager_property_ids:
                raise HTTPException(status_code=403, detail="Access denied to this property")
            
            # If no property specified, use first manager property
            if not property_id and manager_property_ids:
                property_id = manager_property_ids[0]
        
        # Get employee statistics
        stats = await supabase_service.get_employee_statistics(property_id=property_id)
        
        # Get property info if property_id is specified
        property_info = None
        if property_id:
            property_obj = await supabase_service.get_property_by_id(property_id)
            if property_obj:
                property_info = {
                    "id": property_obj.id,
                    "name": property_obj.name,
                    "city": property_obj.city,
                    "state": property_obj.state
                }
        
        return {
            "statistics": stats,
            "property": property_info,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": f"{current_user.first_name} {current_user.last_name}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get employee statistics: {str(e)}")

@app.post("/secret/create-hr")
async def create_hr_user(email: str, password: str, secret_key: str):
    """Create HR user with secret key"""
    
    if secret_key != "hotel-admin-2025":
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    try:
        # Check if user already exists
        existing_user = supabase_service.get_user_by_email_sync(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create HR user data with hashed password
        from datetime import datetime, timezone
        import uuid
        import bcrypt
        
        # Hash the password for secure storage
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        hr_user_data = {
            "id": str(uuid.uuid4()),  # Full UUID
            "email": email,
            "first_name": "HR",
            "last_name": "Admin",
            "role": "hr",
            "is_active": True,
            "password_hash": password_hash,  # Store hashed password in Supabase
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in Supabase (with password hash)
        result = supabase_service.client.table('users').insert(hr_user_data).execute()
        
        # No need to store password in memory anymore - it's in Supabase
        
        return {
            "success": True,
            "message": "HR user created successfully",
            "user_id": hr_user_data["id"],
            "email": email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create HR user: {str(e)}")

@app.post("/secret/create-manager")
async def create_manager_user(email: str, password: str, property_name: str, secret_key: str):
    """Create Manager user with secret key"""
    
    if secret_key != "hotel-admin-2025":
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    try:
        # Check if user already exists
        existing_user = supabase_service.get_user_by_email_sync(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create manager and property
        from datetime import datetime, timezone
        import uuid
        
        manager_id = f"mgr_{str(uuid.uuid4())[:8]}"
        property_id = f"prop_{str(uuid.uuid4())[:8]}"
        
        # Create manager user
        manager_user_data = {
            "id": manager_id,
            "email": email,
            "first_name": "Manager",
            "last_name": "User",
            "role": "manager",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Create property
        property_data = {
            "id": property_id,
            "name": property_name,
            "address": "123 Business Street",
            "city": "Business City",
            "state": "CA",
            "zip_code": "90210",
            "phone": "(555) 123-4567",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in Supabase
        supabase_service.client.table('users').insert(manager_user_data).execute()
        supabase_service.client.table('properties').insert(property_data).execute()
        
        # Assign manager to property
        assignment_data = {
            "manager_id": manager_id,
            "property_id": property_id,
            "assigned_at": datetime.now(timezone.utc).isoformat()
        }
        supabase_service.client.table('manager_properties').insert(assignment_data).execute()
        
        # Store password
        password_manager.store_password(email, password)
        
        return {
            "success": True,
            "message": "Manager user and property created successfully",
            "manager_id": manager_id,
            "property_id": property_id,
            "email": email,
            "property_name": property_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create manager: {str(e)}")

# ===== MANAGER REVIEW APIs =====

@app.get("/api/manager/onboarding/{session_id}/review")
async def get_onboarding_for_manager_review(
    session_id: str,
    current_user: User = Depends(require_manager_role)
):
    """Get onboarding session for manager review"""
    try:
        # Get session
        session = await onboarding_orchestrator.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        # Verify manager has access to this session
        if session.manager_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this onboarding session")
        
        # Verify session is in manager review phase
        if session.status != OnboardingStatus.MANAGER_REVIEW:
            raise HTTPException(
                status_code=400, 
                detail=f"Session is not ready for manager review. Current status: {session.status}"
            )
        
        # Get employee data
        employee = await supabase_service.get_employee_by_id(session.employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Get all form data submitted by employee
        form_data = await supabase_service.get_onboarding_form_data(session_id)
        
        # Get documents uploaded by employee
        documents = await supabase_service.get_onboarding_documents(session_id)
        
        return {
            "session": session,
            "employee": employee,
            "form_data": form_data,
            "documents": documents,
            "next_steps": {
                "required": ["i9_section2", "manager_signature"],
                "optional": ["request_changes"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get onboarding for review: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve onboarding session: {str(e)}")

@app.post("/api/manager/onboarding/{session_id}/i9-section2")
async def complete_i9_section2(
    session_id: str,
    form_data: Dict[str, Any],
    signature_data: Dict[str, Any],
    current_user: User = Depends(require_manager_role)
):
    """Complete I-9 Section 2 verification"""
    try:
        # Get session
        session = await onboarding_orchestrator.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        # Verify manager has access
        if session.manager_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this onboarding session")
        
        # Verify session is in correct state
        if session.status != OnboardingStatus.MANAGER_REVIEW:
            raise HTTPException(
                status_code=400, 
                detail=f"Session is not ready for I-9 Section 2. Current status: {session.status}"
            )
        
        # Validate I-9 Section 2 data
        required_fields = [
            "document_title_list_a",
            "issuing_authority_list_a",
            "document_number_list_a",
            "expiration_date_list_a"
        ]
        
        # Check if using List B + C instead
        if not form_data.get("document_title_list_a"):
            required_fields = [
                "document_title_list_b",
                "issuing_authority_list_b",
                "document_number_list_b",
                "expiration_date_list_b",
                "document_title_list_c",
                "issuing_authority_list_c",
                "document_number_list_c",
                "expiration_date_list_c"
            ]
        
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required I-9 Section 2 fields: {', '.join(missing_fields)}"
            )
        
        # Store I-9 Section 2 data
        await onboarding_orchestrator.update_step_progress(
            session_id,
            OnboardingStep.I9_SECTION2,
            form_data,
            signature_data
        )
        
        # Create audit entry
        await onboarding_orchestrator.create_audit_entry(
            session_id,
            "I9_SECTION2_COMPLETED",
            current_user.id,
            {
                "completed_by": f"{current_user.first_name} {current_user.last_name}",
                "verification_date": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "success": True,
            "message": "I-9 Section 2 completed successfully",
            "next_step": "manager_signature"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete I-9 Section 2: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete I-9 Section 2: {str(e)}")

@app.post("/api/manager/onboarding/{session_id}/approve")
async def manager_approve_onboarding(
    session_id: str,
    signature_data: Dict[str, Any],
    notes: Optional[str] = None,
    current_user: User = Depends(require_manager_role)
):
    """Manager approves onboarding and sends to HR"""
    try:
        # Get session
        session = await onboarding_orchestrator.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        # Verify manager has access
        if session.manager_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this onboarding session")
        
        # Verify I-9 Section 2 is completed
        i9_section2_data = await supabase_service.get_onboarding_form_data_by_step(
            session_id, 
            OnboardingStep.I9_SECTION2
        )
        
        if not i9_section2_data:
            raise HTTPException(
                status_code=400,
                detail="I-9 Section 2 must be completed before approval"
            )
        
        # Store manager signature
        await onboarding_orchestrator.update_step_progress(
            session_id,
            OnboardingStep.MANAGER_SIGNATURE,
            {"approval_notes": notes} if notes else None,
            signature_data
        )
        
        # Complete manager phase
        success = await onboarding_orchestrator.complete_manager_phase(session_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to complete manager phase")
        
        # Create audit entry
        await onboarding_orchestrator.create_audit_entry(
            session_id,
            "MANAGER_APPROVED",
            current_user.id,
            {
                "approved_by": f"{current_user.first_name} {current_user.last_name}",
                "approval_notes": notes,
                "approved_at": datetime.utcnow().isoformat()
            }
        )
        
        # Send email notification to HR
        employee = await supabase_service.get_employee_by_id(session.employee_id)
        property_obj = await supabase_service.get_property_by_id(session.property_id)
        
        if employee and property_obj:
            # Get HR users for notification
            hr_users = await supabase_service.get_users_by_role("hr")
            
            for hr_user in hr_users:
                await email_service.send_email(
                    hr_user.email,
                    f"Onboarding Ready for HR Approval - {employee.first_name} {employee.last_name}",
                    f"""
                    <h2>Onboarding Ready for HR Approval</h2>
                    <p>Manager has completed review and approved the onboarding for:</p>
                    <ul>
                        <li><strong>Employee:</strong> {employee.first_name} {employee.last_name}</li>
                        <li><strong>Position:</strong> {employee.position}</li>
                        <li><strong>Property:</strong> {property_obj.name}</li>
                        <li><strong>Manager:</strong> {current_user.first_name} {current_user.last_name}</li>
                    </ul>
                    <p>Please log in to the HR dashboard to complete the final approval.</p>
                    """,
                    f"Onboarding ready for HR approval: {employee.first_name} {employee.last_name}"
                )
        
        return {
            "success": True,
            "message": "Onboarding approved and sent to HR",
            "new_status": OnboardingStatus.HR_APPROVAL
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve onboarding: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve onboarding: {str(e)}")

@app.post("/api/manager/onboarding/{session_id}/request-changes")
async def manager_request_changes(
    session_id: str,
    requested_changes: List[Dict[str, str]],  # [{"form": "personal_info", "reason": "..."}]
    current_user: User = Depends(require_manager_role)
):
    """Request changes from employee"""
    try:
        # Get session
        session = await onboarding_orchestrator.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        # Verify manager has access
        if session.manager_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this onboarding session")
        
        # Update session status
        session.status = OnboardingStatus.IN_PROGRESS
        session.phase = OnboardingPhase.EMPLOYEE
        session.requested_changes = requested_changes
        session.updated_at = datetime.utcnow()
        
        await supabase_service.update_onboarding_session(session)
        
        # Create audit entry
        await onboarding_orchestrator.create_audit_entry(
            session_id,
            "CHANGES_REQUESTED",
            current_user.id,
            {
                "requested_by": f"{current_user.first_name} {current_user.last_name}",
                "changes": requested_changes
            }
        )
        
        # Send email to employee
        employee = await supabase_service.get_employee_by_id(session.employee_id)
        
        if employee and employee.email:
            changes_list = "\n".join([
                f"- {change['form']}: {change['reason']}" 
                for change in requested_changes
            ])
            
            await email_service.send_email(
                employee.email,
                "Changes Required - Your Onboarding Application",
                f"""
                <h2>Changes Required</h2>
                <p>Your manager has requested the following changes to your onboarding application:</p>
                <ul>
                {"".join([f"<li><strong>{change['form']}:</strong> {change['reason']}</li>" for change in requested_changes])}
                </ul>
                <p>Please log back in to your onboarding portal to make these updates.</p>
                <p><a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/onboard?token={session.token}">Update My Information</a></p>
                """,
                f"Changes required for your onboarding:\n{changes_list}"
            )
        
        return {
            "success": True,
            "message": "Changes requested from employee",
            "requested_changes": requested_changes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to request changes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to request changes: {str(e)}")

# ===== HR APPROVAL APIs =====

@app.get("/api/hr/onboarding/pending")
async def get_pending_hr_approvals(
    current_user: User = Depends(require_hr_role)
):
    """Get all onboarding sessions pending HR approval"""
    try:
        # Get sessions pending HR approval
        sessions = await onboarding_orchestrator.get_pending_hr_approvals()
        
        # Enrich with employee and property data
        enriched_sessions = []
        
        for session in sessions:
            employee = await supabase_service.get_employee_by_id(session.employee_id)
            property_obj = await supabase_service.get_property_by_id(session.property_id)
            manager = await supabase_service.get_user_by_id(session.manager_id)
            
            enriched_sessions.append({
                "session": session,
                "employee": employee,
                "property": property_obj,
                "manager": manager,
                "days_since_submission": (datetime.utcnow() - session.created_at).days
            })
        
        return {
            "pending_count": len(enriched_sessions),
            "sessions": enriched_sessions
        }
        
    except Exception as e:
        logger.error(f"Failed to get pending HR approvals: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve pending approvals: {str(e)}")

@app.post("/api/hr/onboarding/{session_id}/approve")
async def hr_approve_onboarding(
    session_id: str,
    signature_data: Dict[str, Any],
    notes: Optional[str] = None,
    current_user: User = Depends(require_hr_role)
):
    """Final HR approval for onboarding"""
    try:
        # Get session
        session = await onboarding_orchestrator.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        # Verify session is in HR approval phase
        if session.status != OnboardingStatus.HR_APPROVAL:
            raise HTTPException(
                status_code=400,
                detail=f"Session is not ready for HR approval. Current status: {session.status}"
            )
        
        # Create audit entry for compliance check
        await onboarding_orchestrator.create_audit_entry(
            session_id,
            "COMPLIANCE_CHECK_PASSED",
            current_user.id,
            {
                "check_type": "final_approval",
                "checked_by": f"{current_user.first_name} {current_user.last_name}",
                "notes": notes,
                "checked_at": datetime.utcnow().isoformat()
            }
        )
        
        # Store HR signature
        await onboarding_orchestrator.update_step_progress(
            session_id,
            OnboardingStep.HR_APPROVAL,
            {"approval_notes": notes} if notes else None,
            signature_data
        )
        
        # Approve onboarding
        success = await onboarding_orchestrator.approve_onboarding(
            session_id,
            current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to approve onboarding")
        
        # Create audit entry
        await onboarding_orchestrator.create_audit_entry(
            session_id,
            "HR_APPROVED",
            current_user.id,
            {
                "approved_by": f"{current_user.first_name} {current_user.last_name}",
                "approval_notes": notes,
                "approved_at": datetime.utcnow().isoformat()
            }
        )
        
        # Send congratulations email to employee
        employee = await supabase_service.get_employee_by_id(session.employee_id)
        property_obj = await supabase_service.get_property_by_id(session.property_id)
        
        if employee and employee.email and property_obj:
            await email_service.send_email(
                employee.email,
                f"Welcome to {property_obj.name} - Onboarding Complete!",
                f"""
                <h2>🎉 Congratulations, {employee.first_name}!</h2>
                <p>Your onboarding has been approved and you're officially part of the {property_obj.name} team!</p>
                <h3>What's Next:</h3>
                <ul>
                    <li>Your start date: <strong>{employee.start_date}</strong></li>
                    <li>Report to: <strong>{property_obj.address}</strong></li>
                    <li>Your position: <strong>{employee.position}</strong></li>
                </ul>
                <p>If you have any questions, please contact HR or your manager.</p>
                <p>We're excited to have you on the team!</p>
                """,
                f"Welcome to {property_obj.name}! Your onboarding is complete."
            )
        
        return {
            "success": True,
            "message": "Onboarding approved successfully",
            "new_status": OnboardingStatus.APPROVED,
            "employee": employee
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve onboarding: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to approve onboarding: {str(e)}")

@app.post("/api/hr/onboarding/{session_id}/reject")
async def hr_reject_onboarding(
    session_id: str,
    rejection_reason: str,
    current_user: User = Depends(require_hr_role)
):
    """HR rejection of onboarding"""
    try:
        # Get session
        session = await onboarding_orchestrator.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        # Reject onboarding
        success = await onboarding_orchestrator.reject_onboarding(
            session_id,
            current_user.id,
            rejection_reason
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reject onboarding")
        
        # Create audit entry
        await onboarding_orchestrator.create_audit_entry(
            session_id,
            "HR_REJECTED",
            current_user.id,
            {
                "rejected_by": f"{current_user.first_name} {current_user.last_name}",
                "rejection_reason": rejection_reason,
                "rejected_at": datetime.utcnow().isoformat()
            }
        )
        
        # Send email to employee and manager
        employee = await supabase_service.get_employee_by_id(session.employee_id)
        manager = await supabase_service.get_user_by_id(session.manager_id)
        property_obj = await supabase_service.get_property_by_id(session.property_id)
        
        if employee and employee.email:
            await email_service.send_email(
                employee.email,
                "Update on Your Onboarding Application",
                f"""
                <h2>Onboarding Application Update</h2>
                <p>Dear {employee.first_name},</p>
                <p>After careful review, we are unable to proceed with your onboarding at this time.</p>
                <p><strong>Reason:</strong> {rejection_reason}</p>
                <p>If you have questions or would like to discuss this decision, please contact HR.</p>
                """,
                f"Your onboarding application has been updated. Reason: {rejection_reason}"
            )
        
        if manager and manager.email:
            await email_service.send_email(
                manager.email,
                f"Onboarding Rejected - {employee.first_name if employee else 'Employee'}",
                f"""
                <h2>Onboarding Rejected by HR</h2>
                <p>The onboarding for {employee.first_name} {employee.last_name} has been rejected.</p>
                <p><strong>Reason:</strong> {rejection_reason}</p>
                <p><strong>Property:</strong> {property_obj.name if property_obj else 'N/A'}</p>
                """,
                f"Onboarding rejected for {employee.first_name if employee else 'employee'}. Reason: {rejection_reason}"
            )
        
        return {
            "success": True,
            "message": "Onboarding rejected",
            "new_status": OnboardingStatus.REJECTED
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reject onboarding: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reject onboarding: {str(e)}")

@app.post("/api/hr/onboarding/{session_id}/request-changes")
async def hr_request_changes(
    session_id: str,
    requested_changes: List[Dict[str, str]],  # [{"form": "w4_form", "reason": "..."}]
    request_from: str = "employee",  # "employee" or "manager"
    current_user: User = Depends(require_hr_role)
):
    """HR requests specific form updates"""
    try:
        # Get session
        session = await onboarding_orchestrator.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Onboarding session not found")
        
        # Determine who should make changes
        if request_from == "manager":
            # Send back to manager review
            session.status = OnboardingStatus.MANAGER_REVIEW
            session.phase = OnboardingPhase.MANAGER
        else:
            # Send back to employee
            session.status = OnboardingStatus.IN_PROGRESS
            session.phase = OnboardingPhase.EMPLOYEE
        
        session.requested_changes = requested_changes
        session.updated_at = datetime.utcnow()
        
        await supabase_service.update_onboarding_session(session)
        
        # Create audit entry
        await onboarding_orchestrator.create_audit_entry(
            session_id,
            "HR_REQUESTED_CHANGES",
            current_user.id,
            {
                "requested_by": f"{current_user.first_name} {current_user.last_name}",
                "request_from": request_from,
                "changes": requested_changes
            }
        )
        
        # Send appropriate email
        employee = await supabase_service.get_employee_by_id(session.employee_id)
        manager = await supabase_service.get_user_by_id(session.manager_id)
        
        changes_html = "".join([
            f"<li><strong>{change['form']}:</strong> {change['reason']}</li>" 
            for change in requested_changes
        ])
        
        if request_from == "manager" and manager and manager.email:
            await email_service.send_email(
                manager.email,
                "HR Review - Changes Required",
                f"""
                <h2>HR has requested changes</h2>
                <p>Please review and update the following items:</p>
                <ul>{changes_html}</ul>
                <p>Log in to the manager dashboard to make these updates.</p>
                """,
                f"HR has requested changes to the onboarding"
            )
        elif employee and employee.email:
            await email_service.send_email(
                employee.email,
                "Update Required - Your Onboarding Application",
                f"""
                <h2>Updates Required</h2>
                <p>HR has requested the following updates to your onboarding:</p>
                <ul>{changes_html}</ul>
                <p><a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/onboard?token={session.token}">Update My Information</a></p>
                """,
                f"HR has requested updates to your onboarding"
            )
        
        return {
            "success": True,
            "message": f"Changes requested from {request_from}",
            "requested_changes": requested_changes,
            "new_phase": session.phase
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to request changes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to request changes: {str(e)}")

# ===== EMAIL NOTIFICATION HELPERS =====

@app.post("/api/internal/send-phase-completion-email")
async def send_phase_completion_email(
    session_id: str,
    phase_completed: str
):
    """Internal endpoint to send phase completion emails"""
    try:
        session = await onboarding_orchestrator.get_session_by_id(session_id)
        if not session:
            return {"success": False, "message": "Session not found"}
        
        employee = await supabase_service.get_employee_by_id(session.employee_id)
        property_obj = await supabase_service.get_property_by_id(session.property_id)
        manager = await supabase_service.get_user_by_id(session.manager_id)
        
        if phase_completed == "employee" and manager and manager.email:
            await email_service.send_email(
                manager.email,
                f"Onboarding Ready for Review - {employee.first_name} {employee.last_name}",
                f"""
                <h2>Employee Onboarding Completed</h2>
                <p>{employee.first_name} {employee.last_name} has completed their onboarding forms.</p>
                <p><strong>Position:</strong> {employee.position}</p>
                <p><strong>Property:</strong> {property_obj.name}</p>
                <p>Please log in to complete I-9 Section 2 verification within 3 business days.</p>
                """,
                f"{employee.first_name} {employee.last_name} has completed onboarding"
            )
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to send phase completion email: {e}")
        return {"success": False, "message": str(e)}

# ===== COMPLIANCE ENDPOINTS =====

@app.post("/api/compliance/validate-i9-supplement-a")
async def validate_i9_supplement_a(
    form_data: dict,
    auto_filled_fields: List[str],
    current_user=Depends(get_current_user)
):
    """Validate I-9 Supplement A compliance requirements"""
    try:
        # Get user role
        user_role = UserRole(current_user.role)
        
        # Validate auto-fill compliance
        is_valid, violations = compliance_engine.validate_auto_fill_compliance(
            DocumentCategory.I9_SUPPLEMENT_A,
            form_data,
            auto_filled_fields,
            user_role,
            current_user.id,
            form_data.get('document_id', '')
        )
        
        # Validate supplement A restrictions
        is_valid_supplement, supplement_violations = compliance_engine.validate_i9_supplement_a_restrictions(
            form_data,
            user_role,
            current_user.id,
            form_data.get('document_id', '')
        )
        
        all_violations = violations + supplement_violations
        
        return {
            "is_compliant": is_valid and is_valid_supplement,
            "violations": all_violations,
            "user_role": user_role.value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Compliance validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compliance/validate-i9-supplement-b-access")
async def validate_i9_supplement_b_access(
    current_user=Depends(get_current_user)
):
    """Validate I-9 Supplement B access control"""
    try:
        user_role = UserRole(current_user.role)
        
        is_valid, violations = compliance_engine.validate_i9_supplement_b_access(
            user_role,
            current_user.id,
            'supplement-b-check'
        )
        
        return {
            "has_access": is_valid,
            "violations": violations,
            "user_role": user_role.value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Access validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compliance/validate-digital-signature")
async def validate_digital_signature(
    signature_data: dict,
    document_category: str,
    current_user=Depends(get_current_user)
):
    """Validate digital signature ESIGN Act compliance"""
    try:
        user_role = UserRole(current_user.role)
        doc_category = DocumentCategory(document_category)
        
        is_valid, violations = compliance_engine.validate_digital_signature_compliance(
            doc_category,
            signature_data,
            user_role,
            current_user.id,
            signature_data.get('document_id', '')
        )
        
        return {
            "is_compliant": is_valid,
            "violations": violations,
            "esign_metadata_present": all([
                signature_data.get('signature_hash'),
                signature_data.get('timestamp'),
                signature_data.get('ip_address'),
                signature_data.get('user_agent')
            ]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Signature validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compliance/i9-deadlines/{id}")
async def get_i9_deadlines(
    id: str,
    current_user=Depends(get_current_user)
):
    """Get I-9 Section 2 deadline information for an employee"""
    try:
        # Get employee hire date
        employee = await supabase_service.get_employee_by_id(id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        hire_date = datetime.strptime(employee.hire_date, "%Y-%m-%d").date()
        
        # Check if I-9 Section 2 is completed
        onboarding_session = await supabase_service.get_active_onboarding_by_employee(id)
        section2_completed = False
        section2_date = None
        
        if onboarding_session and onboarding_session.get('i9_section2_data'):
            section2_completed = True
            section2_date = onboarding_session['i9_section2_data'].get('verification_date')
            if section2_date:
                section2_date = datetime.strptime(section2_date, "%Y-%m-%d").date()
        
        # Validate compliance
        is_compliant, deadline, warnings = compliance_engine.validate_i9_three_day_compliance(
            id,
            f"i9-{id}",
            hire_date,
            section2_date
        )
        
        return {
            "employee_id": employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}",
            "hire_date": hire_date.isoformat(),
            "deadline_date": deadline.deadline_date.isoformat(),
            "business_days_remaining": deadline.business_days_remaining,
            "is_compliant": is_compliant,
            "section2_completed": section2_completed,
            "section2_completion_date": section2_date.isoformat() if section2_date else None,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get I-9 deadlines: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compliance/dashboard")
async def get_compliance_dashboard(
    current_user=Depends(get_current_user)
):
    """Get compliance dashboard data"""
    try:
        user_role = UserRole(current_user.role)
        property_id = current_user.property_id if hasattr(current_user, 'property_id') else None
        
        dashboard = compliance_engine.get_compliance_dashboard(user_role, property_id)
        
        return {
            "dashboard": dashboard,
            "user_role": user_role.value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get compliance dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/compliance/audit-trail")
async def get_compliance_audit_trail(
    employee_id: Optional[str] = None,
    document_id: Optional[str] = None,
    limit: int = 100,
    current_user=Depends(get_current_user)
):
    """Get compliance audit trail entries"""
    try:
        # In production, this would query from database
        # For now, return mock data structure
        entries = [
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "action": "I-9 Section 1 Completed",
                "documentType": "I-9 Form",
                "documentId": document_id or "i9-001",
                "userId": employee_id or "emp-123",
                "userName": "John Doe",
                "userRole": "employee",
                "ipAddress": "192.168.1.100",
                "details": "Employee completed I-9 Section 1 with citizenship attestation",
                "complianceType": "i9",
                "severity": "info",
                "federalReference": "Immigration and Nationality Act Section 274A"
            }
        ]
        
        return {
            "entries": entries,
            "total": len(entries),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Document Retention Endpoints

@app.post("/api/retention/calculate")
async def calculate_retention_date(
    document_type: str,
    hire_date: str,
    termination_date: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """Calculate document retention date based on federal requirements"""
    try:
        doc_type = DocumentType(document_type)
        hire_dt = datetime.strptime(hire_date, "%Y-%m-%d").date()
        term_dt = datetime.strptime(termination_date, "%Y-%m-%d").date() if termination_date else None
        
        if doc_type == DocumentType.I9_FORM:
            retention_date, method = retention_service.calculate_i9_retention_date(hire_dt, term_dt)
        elif doc_type == DocumentType.W4_FORM:
            retention_date, method = retention_service.calculate_w4_retention_date(hire_dt.year)
        else:
            # Default 3-year retention
            retention_date = hire_dt + timedelta(days=3*365)
            method = "3 years from hire date (default)"
        
        return {
            "document_type": document_type,
            "hire_date": hire_date,
            "termination_date": termination_date,
            "retention_end_date": retention_date.isoformat(),
            "calculation_method": method,
            "days_until_expiration": (retention_date - date.today()).days
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate retention: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/retention/dashboard")
async def get_retention_dashboard(
    current_user=Depends(get_current_user)
):
    """Get document retention dashboard"""
    try:
        user_role = UserRole(current_user.role)
        dashboard = retention_service.get_retention_dashboard(user_role)
        
        return {
            "dashboard": dashboard,
            "user_role": user_role.value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get retention dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/retention/legal-hold/{id}")
async def place_legal_hold(
    id: str,
    reason: str,
    current_user=Depends(get_current_user)
):
    """Place legal hold on a document"""
    try:
        if current_user.role != 'hr':
            raise HTTPException(status_code=403, detail="Only HR can place legal holds")
        
        success = retention_service.place_legal_hold(id, reason)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "success": True,
            "document_id": id,
            "action": "legal_hold_placed",
            "reason": reason,
            "placed_by": current_user.email,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to place legal hold: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")