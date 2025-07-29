#!/usr/bin/env python3

"""
Fix authentication functions to be properly async
"""

def fix_authentication_functions():
    """Fix the authentication functions in main_enhanced.py"""
    
    filepath = "hotel-onboarding-backend/app/main_enhanced.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix get_current_user function signature
    content = content.replace(
        'async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:',
        'def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:'
    )
    
    # Fix get_current_user_optional function
    content = content.replace(
        'def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:',
        'def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:'
    )
    
    # Remove await from synchronous functions - we'll use sync methods for now
    content = content.replace(
        'user = await supabase_service.get_user_by_id(manager_id)',
        'user = supabase_service.get_user_by_id_sync(manager_id)'
    )
    
    content = content.replace(
        'user = await supabase_service.get_user_by_id(user_id)',
        'user = supabase_service.get_user_by_id_sync(user_id)'
    )
    
    # Fix login endpoint
    content = content.replace(
        'existing_user = await supabase_service.get_user_by_email(email)',
        'existing_user = supabase_service.get_user_by_email_sync(email)'
    )
    
    # Fix property lookups
    content = content.replace(
        'manager_properties = await supabase_service.get_manager_properties(existing_user.id)',
        'manager_properties = supabase_service.get_manager_properties_sync(existing_user.id)'
    )
    
    # Fix property info endpoint
    content = content.replace(
        'property_obj = await supabase_service.get_property_by_id(property_id)',
        'property_obj = supabase_service.get_property_by_id_sync(property_id)'
    )
    
    # Fix application submission
    content = content.replace(
        'existing_applications = await supabase_service.get_applications_by_email_and_property(',
        'existing_applications = supabase_service.get_applications_by_email_and_property_sync('
    )
    
    content = content.replace(
        'created_application = await supabase_service.create_application(job_application)',
        'created_application = supabase_service.create_application_sync(job_application)'
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("✅ Fixed authentication functions")

def add_sync_methods_to_supabase():
    """Add synchronous wrapper methods to Supabase service"""
    
    filepath = "hotel-onboarding-backend/app/supabase_service_enhanced.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add sync wrapper methods at the end of the class
    sync_methods = '''
    # Synchronous wrapper methods for compatibility
    def get_user_by_email_sync(self, email: str) -> Optional[User]:
        """Synchronous wrapper for get_user_by_email"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_user_by_email(email))
        except RuntimeError:
            # Create new event loop if none exists
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_user_by_email(email))
            finally:
                loop.close()
    
    def get_user_by_id_sync(self, user_id: str) -> Optional[User]:
        """Synchronous wrapper for get_user_by_id"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_user_by_id(user_id))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_user_by_id(user_id))
            finally:
                loop.close()
    
    def get_property_by_id_sync(self, property_id: str) -> Optional[Property]:
        """Synchronous wrapper for get_property_by_id"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_property_by_id(property_id))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_property_by_id(property_id))
            finally:
                loop.close()
    
    def get_manager_properties_sync(self, manager_id: str) -> List[Property]:
        """Synchronous wrapper for get_manager_properties"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_manager_properties(manager_id))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_manager_properties(manager_id))
            finally:
                loop.close()
    
    def get_applications_by_email_and_property_sync(self, email: str, property_id: str) -> List[JobApplication]:
        """Synchronous wrapper for get_applications_by_email_and_property"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.get_applications_by_email_and_property(email, property_id))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.get_applications_by_email_and_property(email, property_id))
            finally:
                loop.close()
    
    def create_application_sync(self, application: JobApplication) -> JobApplication:
        """Synchronous wrapper for create_application"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.create_application(application))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.create_application(application))
            finally:
                loop.close()
'''
    
    # Add the sync methods before the last closing of the class
    content = content.rstrip() + sync_methods + '\n'
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("✅ Added synchronous wrapper methods to Supabase service")

def main():
    """Main function"""
    
    print("🔧 Fixing Authentication Functions")
    print("=" * 40)
    
    try:
        # Fix authentication functions
        fix_authentication_functions()
        
        # Add sync methods
        add_sync_methods_to_supabase()
        
        # Test import
        import subprocess
        import os
        
        os.chdir("hotel-onboarding-backend")
        result = subprocess.run([
            "python3", "-c", 
            "from app.main_enhanced import app; print('✅ Backend imports successfully')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend imports successfully")
            print("✅ Authentication functions fixed")
            return True
        else:
            print(f"❌ Import still failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Authentication functions fixed!")
    else:
        print("\n💥 Fix failed!")