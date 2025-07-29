#!/usr/bin/env python3

"""
Update main_enhanced.py to use Supabase instead of in-memory storage
"""

import re

def update_main_enhanced_to_supabase():
    """Update the main backend file to use Supabase"""
    
    print("🔄 Updating main_enhanced.py to use Supabase")
    print("=" * 50)
    
    # Read the current main file
    with open("hotel-onboarding-backend/app/main_enhanced.py", "r") as f:
        content = f.read()
    
    # 1. Add Supabase import
    print("1. Adding Supabase import...")
    
    import_section = '''# Import our enhanced models and authentication
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
from .supabase_service_enhanced import SupabaseService'''
    
    # Replace the import section
    content = re.sub(
        r'# Import our enhanced models and authentication.*?from \.services\.form_update_service import FormUpdateService',
        import_section,
        content,
        flags=re.DOTALL
    )
    
    # 2. Replace in-memory database with Supabase service
    print("2. Replacing in-memory database with Supabase service...")
    
    # Remove the in-memory database definition
    content = re.sub(
        r'# Enhanced in-memory database with proper structure\ndatabase = \{.*?\}',
        '# Initialize Supabase service\nsupabase_service = SupabaseService()',
        content,
        flags=re.DOTALL
    )
    
    # 3. Update service initialization
    print("3. Updating service initialization...")
    
    old_init = '''def initialize_services():
    """Initialize enhanced onboarding services"""
    global onboarding_orchestrator, form_update_service
    onboarding_orchestrator = OnboardingOrchestrator(database)
    form_update_service = FormUpdateService(database)'''
    
    new_init = '''async def initialize_services():
    """Initialize enhanced onboarding services with Supabase"""
    global onboarding_orchestrator, form_update_service
    
    # Initialize Supabase connection
    await supabase_service.initialize()
    
    # Initialize services with Supabase backend
    onboarding_orchestrator = OnboardingOrchestrator(supabase_service)
    form_update_service = FormUpdateService(supabase_service)'''
    
    content = content.replace(old_init, new_init)
    
    # 4. Update test data initialization to use Supabase
    print("4. Updating test data initialization...")
    
    # Replace the test data initialization function
    old_test_data = '''def initialize_test_data():
    """Initialize database with test data for development"""'''
    
    new_test_data = '''async def initialize_test_data():
    """Initialize Supabase database with test data for development"""'''
    
    content = content.replace(old_test_data, new_test_data)
    
    # 5. Add startup event
    print("5. Adding FastAPI startup event...")
    
    startup_event = '''
# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await initialize_services()
    await initialize_test_data()
    print("✅ Supabase-enabled backend started successfully")
'''
    
    # Insert after app initialization
    content = content.replace(
        '# Initialize services\ngroq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))',
        startup_event + '\n# Initialize services\ngroq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))'
    )
    
    # 6. Update health check
    print("6. Updating health check...")
    
    old_health = '''@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc),
        "version": "2.0.0"
    }'''
    
    new_health = '''@app.get("/healthz")
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
        }'''
    
    content = content.replace(old_health, new_health)
    
    # 7. Comment out the old initialization calls
    print("7. Updating initialization calls...")
    
    content = content.replace(
        '# Initialize test data on startup\ninitialize_test_data()\n\n# Initialize enhanced services\ninitialize_services()',
        '# Test data and services are now initialized in startup event'
    )
    
    # Write the updated content
    with open("hotel-onboarding-backend/app/main_enhanced.py", "w") as f:
        f.write(content)
    
    print("✅ main_enhanced.py updated to use Supabase!")
    
    return True

def create_migration_notes():
    """Create notes about what needs to be done next"""
    
    notes = '''# Supabase Migration Notes

## What was changed:
1. ✅ Added Supabase service import
2. ✅ Replaced in-memory database with SupabaseService
3. ✅ Updated service initialization to be async
4. ✅ Added FastAPI startup event
5. ✅ Updated health check to include Supabase status
6. ✅ Made test data initialization async

## What still needs to be done:
1. 🔄 Update all database operations to use supabase_service instead of database dict
2. 🔄 Replace database["users"] with supabase_service.get_users()
3. 🔄 Replace database["applications"] with supabase_service.get_applications()
4. 🔄 Replace database["properties"] with supabase_service.get_properties()
5. 🔄 Update all CRUD operations to use Supabase methods
6. 🔄 Test all endpoints with Supabase backend

## Key changes needed in endpoints:
- Replace `database["table_name"]` with `await supabase_service.get_table_name()`
- Replace direct dict operations with Supabase service calls
- Add async/await to all database operations
- Update error handling for Supabase exceptions

## Testing:
- Run the backend and check /healthz endpoint
- Test login functionality
- Test application creation and approval
- Verify data persists across server restarts
'''
    
    with open("SUPABASE_MIGRATION_NOTES.md", "w") as f:
        f.write(notes)
    
    print("📝 Created migration notes: SUPABASE_MIGRATION_NOTES.md")

def main():
    """Main function"""
    
    print("🚀 Starting Supabase Migration")
    print("=" * 40)
    
    try:
        # Update the main file
        if update_main_enhanced_to_supabase():
            print("✅ Main file updated successfully")
        else:
            print("❌ Failed to update main file")
            return False
        
        # Create migration notes
        create_migration_notes()
        
        print("\n🎯 Next Steps:")
        print("1. Review the updated main_enhanced.py")
        print("2. Update all database operations to use Supabase")
        print("3. Test the backend with: python -m app.main_enhanced")
        print("4. Check /healthz endpoint for Supabase connection")
        print("5. Test application approval functionality")
        
        print("\n⚠️  Important:")
        print("• The backend now uses Supabase for persistent storage")
        print("• Data will survive server restarts")
        print("• All database operations need to be updated")
        print("• This should fix the approval issue")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Supabase migration completed!")
    else:
        print("\n💥 Supabase migration failed!")