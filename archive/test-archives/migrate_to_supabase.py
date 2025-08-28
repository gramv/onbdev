#!/usr/bin/env python3

"""
Migrate the main backend from in-memory storage to Supabase
"""

import os
import sys
import shutil
from datetime import datetime

def backup_current_main():
    """Backup the current main_enhanced.py file"""
    
    backup_name = f"main_enhanced_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    backup_path = f"hotel-onboarding-backend/app/{backup_name}"
    
    try:
        shutil.copy2("hotel-onboarding-backend/app/main_enhanced.py", backup_path)
        print(f"✅ Backed up current main_enhanced.py to {backup_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to backup main file: {e}")
        return False

def check_supabase_setup():
    """Check if Supabase is properly configured"""
    
    print("🔍 Checking Supabase configuration...")
    
    # Check environment variables
    env_file = "hotel-onboarding-backend/.env"
    
    if not os.path.exists(env_file):
        print("❌ .env file not found")
        return False
    
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "DATABASE_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ Supabase environment variables found")
    
    # Check if Supabase service exists
    supabase_service_path = "hotel-onboarding-backend/app/supabase_service_enhanced.py"
    
    if not os.path.exists(supabase_service_path):
        print("❌ Supabase service file not found")
        return False
    
    print("✅ Supabase service file exists")
    
    # Check if schema files exist
    schema_files = [
        "hotel-onboarding-backend/supabase_enhanced_schema.sql",
        "hotel-onboarding-backend/supabase_schema_step1_tables.sql"
    ]
    
    for schema_file in schema_files:
        if os.path.exists(schema_file):
            print(f"✅ Found schema file: {schema_file}")
            return True
    
    print("⚠️  No schema files found, but continuing...")
    return True

def create_supabase_migration_plan():
    """Create a plan for migrating to Supabase"""
    
    print("\n📋 Supabase Migration Plan")
    print("=" * 50)
    
    steps = [
        "1. Setup Supabase database schema",
        "2. Test Supabase connection", 
        "3. Create Supabase-enabled main backend",
        "4. Migrate existing data (if any)",
        "5. Update imports and dependencies",
        "6. Test all endpoints with Supabase",
        "7. Deploy and verify"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print(f"\n🎯 Current Status:")
    print(f"   • Backend: Using in-memory storage")
    print(f"   • Target: Switch to Supabase PostgreSQL")
    print(f"   • Impact: Persistent data storage")
    print(f"   • Benefits: Data survives server restarts")

def setup_supabase_schema():
    """Setup the Supabase database schema"""
    
    print("\n🗄️  Setting up Supabase schema...")
    
    # Check if we have schema setup scripts
    setup_scripts = [
        "hotel-onboarding-backend/apply_enhanced_schema.py",
        "hotel-onboarding-backend/apply_schema_steps.py"
    ]
    
    for script in setup_scripts:
        if os.path.exists(script):
            print(f"✅ Found schema setup script: {script}")
            print(f"   Run: python3 {script}")
            return script
    
    print("⚠️  No schema setup scripts found")
    return None

def create_supabase_main_template():
    """Create a template for the Supabase-enabled main backend"""
    
    template = '''#!/usr/bin/env python3
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

'''
    
    template_path = "hotel-onboarding-backend/app/main_supabase_template.py"
    
    with open(template_path, 'w') as f:
        f.write(template)
    
    print(f"✅ Created Supabase main template: {template_path}")
    return template_path

def main():
    """Main migration function"""
    
    print("🚀 Starting Migration to Supabase")
    print("=" * 60)
    
    # Step 1: Check current setup
    if not check_supabase_setup():
        print("❌ Supabase setup check failed")
        return False
    
    # Step 2: Backup current main file
    if not backup_current_main():
        print("❌ Backup failed")
        return False
    
    # Step 3: Create migration plan
    create_supabase_migration_plan()
    
    # Step 4: Setup schema
    schema_script = setup_supabase_schema()
    
    # Step 5: Create template
    template_path = create_supabase_main_template()
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Run schema setup: python3 {schema_script}" if schema_script else "1. Setup Supabase schema manually")
    print(f"2. Test Supabase connection")
    print(f"3. Migrate endpoints from in-memory to Supabase")
    print(f"4. Update main_enhanced.py to use Supabase")
    print(f"5. Test all functionality")
    
    print(f"\n⚠️  IMPORTANT:")
    print(f"   • Current backend uses in-memory storage")
    print(f"   • Data will be lost on server restart")
    print(f"   • Supabase provides persistent storage")
    print(f"   • This migration is essential for production")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n✅ Migration preparation complete!")
    else:
        print(f"\n❌ Migration preparation failed!")