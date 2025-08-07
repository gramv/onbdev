#!/usr/bin/env python3
"""
Hotel Employee Onboarding System API - Supabase Version
Enhanced implementation with persistent Supabase storage
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

# Import Supabase service
from .supabase_service_enhanced import SupabaseService

load_dotenv()

app = FastAPI(
    title="Hotel Employee Onboarding System",
    description="Comprehensive onboarding system with Supabase persistent storage",
    version="3.0.0"
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

# Initialize Supabase service
supabase_service = SupabaseService()

# Initialize enhanced services with Supabase
onboarding_orchestrator = None
form_update_service = None

async def initialize_services():
    """Initialize enhanced onboarding services with Supabase"""
    global onboarding_orchestrator, form_update_service
    
    # Initialize Supabase connection
    await supabase_service.initialize()
    
    # Initialize services with Supabase backend
    onboarding_orchestrator = OnboardingOrchestrator(supabase_service)
    form_update_service = FormUpdateService(supabase_service)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await initialize_services()
    print("✅ Supabase-enabled backend started successfully")

# Health Check
@app.get("/healthz")
async def healthz():
    """Health check with Supabase connection status"""
    try:
        # Test Supabase connection
        connection_status = await supabase_service.health_check()
        
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc),
            "version": "3.0.0",
            "database": "supabase",
            "connection": connection_status
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc),
            "version": "3.0.0",
            "database": "supabase",
            "error": str(e)
        }

# TODO: Replace all in-memory database operations with Supabase calls
# This is a template - actual endpoints need to be migrated

