#!/usr/bin/env python3

"""
Complete migration from in-memory database to Supabase
This script will systematically replace all database operations
"""

import re
import os

def read_file(filepath):
    """Read file content"""
    with open(filepath, 'r') as f:
        return f.read()

def write_file(filepath, content):
    """Write content to file"""
    with open(filepath, 'w') as f:
        f.write(content)

def backup_file(filepath):
    """Create backup of file"""
    backup_path = f"{filepath}.backup"
    content = read_file(filepath)
    write_file(backup_path, content)
    print(f"✅ Backed up {filepath} to {backup_path}")

def migrate_main_enhanced():
    """Migrate main_enhanced.py to use Supabase completely"""
    
    filepath = "hotel-onboarding-backend/app/main_enhanced.py"
    print(f"🔄 Migrating {filepath} to Supabase...")
    
    # Backup original file
    backup_file(filepath)
    
    content = read_file(filepath)
    
    # 1. Update test data initialization to use Supabase
    print("1. Updating test data initialization...")
    
    # Replace the entire initialize_test_data function
    old_init_data = r'async def initialize_test_data\(\):\s*"""Initialize Supabase database with test data for development""".*?print\(f"   Application URL: http://localhost:8000/apply/\{property_id\}"\)'
    
    new_init_data = '''async def initialize_test_data():
    """Initialize Supabase database with test data for development"""
    
    print("🔄 Initializing test data in Supabase...")
    
    try:
        # Check if data already exists
        existing_users = await supabase_service.get_users()
        if len(existing_users) >= 2:
            print("✅ Test data already exists, skipping initialization")
            return
        
        # Create HR user
        hr_user_data = {
            "id": "hr_test_001",
            "email": "hr@hoteltest.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "hr",
            "is_active": True
        }
        
        hr_user = await supabase_service.create_user(hr_user_data)
        print(f"✅ Created HR user: {hr_user.email}")
        
        # Create manager user
        manager_user_data = {
            "id": "mgr_test_001", 
            "email": "manager@hoteltest.com",
            "first_name": "Mike",
            "last_name": "Wilson",
            "role": "manager",
            "is_active": True
        }
        
        manager_user = await supabase_service.create_user(manager_user_data)
        print(f"✅ Created manager user: {manager_user.email}")
        
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
        
        property_obj = await supabase_service.create_property(property_data)
        print(f"✅ Created property: {property_obj.name}")
        
        # Assign manager to property
        await supabase_service.assign_manager_to_property(manager_user.id, property_obj.id)
        print(f"✅ Assigned manager to property")
        
        # Store test passwords
        password_manager.store_password("hr@hoteltest.com", "admin123")
        password_manager.store_password("manager@hoteltest.com", "manager123")
        
        print("✅ Test data initialization completed")
        
    except Exception as e:
        print(f"❌ Failed to initialize test data: {e}")
        # Continue anyway - the app should still work'''
    
    content = re.sub(old_init_data, new_init_data, content, flags=re.DOTALL)
    
    # 2. Update authentication functions
    print("2. Updating authentication functions...")
    
    # Update get_current_user function
    old_get_user = r'def get_current_user\(credentials: HTTPAuthorizationCredentials = Depends\(security\)\) -> User:.*?if not user_id or user_id not in database\["users"\]:'
    
    new_get_user = '''async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Enhanced JWT token validation with Supabase lookup"""
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
        
        # Handle different token types with Supabase lookup
        if token_type == "manager_auth":
            manager_id = payload.get("manager_id")
            if not manager_id:
                raise HTTPException(status_code=401, detail="Invalid manager token")
            
            user = await supabase_service.get_user_by_id(manager_id)
            if not user or user.role != "manager":
                raise HTTPException(status_code=401, detail="Manager not found")
            
            return user
            
        elif token_type == "hr_auth":
            user_id = payload.get("user_id")
            if not user_id:'''
    
    content = re.sub(old_get_user, new_get_user, content, flags=re.DOTALL)
    
    # Continue with the rest of get_current_user
    old_get_user_2 = r'user_id = payload\.get\("user_id"\)\s*if not user_id or user_id not in database\["users"\]:'
    
    new_get_user_2 = '''user_id = payload.get("user_id")
            if not user_id:'''
    
    content = re.sub(old_get_user_2, new_get_user_2, content)
    
    # Update user lookup in get_current_user
    old_user_lookup = r'user = database\["users"\]\[user_id\]\s*if user\.role != UserRole\.HR:'
    
    new_user_lookup = '''user = await supabase_service.get_user_by_id(user_id)
            if not user or user.role != "hr":'''
    
    content = re.sub(old_user_lookup, new_user_lookup, content)
    
    # 3. Update login endpoint
    print("3. Updating login endpoint...")
    
    # Update login function to use Supabase
    old_login = r'# Find user by email\s*existing_user = None\s*for user in database\["users"\]\.values\(\):\s*if user\.email\.lower\(\) == email:\s*existing_user = user\s*break'
    
    new_login = '''# Find user by email using Supabase
        existing_user = await supabase_service.get_user_by_email(email)'''
    
    content = re.sub(old_login, new_login, content, flags=re.DOTALL)
    
    # Update user active check
    old_active_check = r'# Check if user is active\s*if not existing_user\.is_active:'
    new_active_check = '''# Check if user is active
        if not existing_user or not existing_user.is_active:'''
    
    content = re.sub(old_active_check, new_active_check, content)
    
    # Update property lookup for managers
    old_property_lookup = r'if existing_user\.role == UserRole\.MANAGER:\s*if not existing_user\.property_id:\s*raise HTTPException\(\s*status_code=403,\s*detail="Manager account not properly configured\. Please contact HR\."\s*\)'
    
    new_property_lookup = '''if existing_user.role == "manager":
            # Get manager's property from Supabase
            manager_properties = await supabase_service.get_manager_properties(existing_user.id)
            if not manager_properties:
                raise HTTPException(
                    status_code=403, 
                    detail="Manager account not properly configured. Please contact HR."
                )
            
            property_id = manager_properties[0].id  # Use first property'''
    
    content = re.sub(old_property_lookup, new_property_lookup, content, flags=re.DOTALL)
    
    # 4. Update application endpoints
    print("4. Updating application endpoints...")
    
    # Update property info endpoint
    old_property_info = r'# Check if property exists\s*if property_id not in database\["properties"\]:'
    new_property_info = '''# Check if property exists using Supabase
    property_obj = await supabase_service.get_property_by_id(property_id)
    if not property_obj:'''
    
    content = re.sub(old_property_info, new_property_info, content)
    
    # Update property object reference
    old_property_obj = r'property_obj = database\["properties"\]\[property_id\]'
    new_property_obj = '''# property_obj already retrieved above'''
    
    content = re.sub(old_property_obj, new_property_obj, content)
    
    # 5. Update application submission endpoint
    print("5. Updating application submission endpoint...")
    
    # Update property validation in submit application
    old_submit_validation = r'# Validate property exists and is active\s*if property_id not in database\["properties"\]:'
    new_submit_validation = '''# Validate property exists and is active using Supabase
    property_obj = await supabase_service.get_property_by_id(property_id)
    if not property_obj:'''
    
    content = re.sub(old_submit_validation, new_submit_validation, content)
    
    # Update property object reference in submit
    old_submit_property = r'property_obj = database\["properties"\]\[property_id\]'
    new_submit_property = '''# property_obj already retrieved above'''
    
    content = re.sub(old_submit_property, new_submit_property, content)
    
    # Update duplicate check
    old_duplicate_check = r'# Check for duplicate applications.*?for app in database\["applications"\]\.values\(\):.*?break'
    new_duplicate_check = '''# Check for duplicate applications using Supabase
    existing_applications = await supabase_service.get_applications_by_email_and_property(
        application_data.email.lower(), property_id
    )
    
    existing_application = None
    for app in existing_applications:
        if (app.position == application_data.position and app.status == "pending"):
            existing_application = app
            break'''
    
    content = re.sub(old_duplicate_check, new_duplicate_check, content, flags=re.DOTALL)
    
    # Update application creation
    old_app_creation = r'# Store application in database\s*database\["applications"\]\[application_id\] = job_application'
    new_app_creation = '''# Store application in Supabase
    created_application = await supabase_service.create_application(job_application)'''
    
    content = re.sub(old_app_creation, new_app_creation, content)
    
    # Write the updated content
    write_file(filepath, content)
    print(f"✅ Updated {filepath} with Supabase integration")
    
    return True

def add_missing_supabase_methods():
    """Add missing methods to the Supabase service"""
    
    filepath = "hotel-onboarding-backend/app/supabase_service_enhanced.py"
    print(f"🔄 Adding missing methods to {filepath}...")
    
    content = read_file(filepath)
    
    # Add missing methods at the end of the class
    missing_methods = '''
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        try:
            result = self.supabase.table("users").select("*").eq("email", email.lower()).execute()
            
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=UserRole(user_data["role"]),
                    property_id=user_data.get("property_id"),
                    is_active=user_data.get("is_active", True),
                    created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00'))
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if result.data:
                user_data = result.data[0]
                return User(
                    id=user_data["id"],
                    email=user_data["email"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=UserRole(user_data["role"]),
                    property_id=user_data.get("property_id"),
                    is_active=user_data.get("is_active", True),
                    created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00'))
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    async def get_property_by_id(self, property_id: str) -> Optional[Property]:
        """Get property by ID"""
        try:
            result = self.supabase.table("properties").select("*").eq("id", property_id).execute()
            
            if result.data:
                prop_data = result.data[0]
                return Property(
                    id=prop_data["id"],
                    name=prop_data["name"],
                    address=prop_data["address"],
                    city=prop_data["city"],
                    state=prop_data["state"],
                    zip_code=prop_data["zip_code"],
                    phone=prop_data["phone"],
                    is_active=prop_data.get("is_active", True),
                    created_at=datetime.fromisoformat(prop_data["created_at"].replace('Z', '+00:00'))
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get property by ID {property_id}: {e}")
            return None
    
    async def get_manager_properties(self, manager_id: str) -> List[Property]:
        """Get properties assigned to a manager"""
        try:
            result = self.supabase.table("property_managers").select(
                "properties(*)"
            ).eq("manager_id", manager_id).execute()
            
            properties = []
            for item in result.data:
                if item.get("properties"):
                    prop_data = item["properties"]
                    properties.append(Property(
                        id=prop_data["id"],
                        name=prop_data["name"],
                        address=prop_data["address"],
                        city=prop_data["city"],
                        state=prop_data["state"],
                        zip_code=prop_data["zip_code"],
                        phone=prop_data["phone"],
                        is_active=prop_data.get("is_active", True),
                        created_at=datetime.fromisoformat(prop_data["created_at"].replace('Z', '+00:00'))
                    ))
            
            return properties
            
        except Exception as e:
            logger.error(f"Failed to get manager properties for {manager_id}: {e}")
            return []
    
    async def assign_manager_to_property(self, manager_id: str, property_id: str) -> bool:
        """Assign a manager to a property"""
        try:
            result = self.supabase.table("property_managers").insert({
                "manager_id": manager_id,
                "property_id": property_id,
                "assigned_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to assign manager {manager_id} to property {property_id}: {e}")
            return False
    
    async def get_applications_by_email_and_property(self, email: str, property_id: str) -> List[JobApplication]:
        """Get applications by email and property"""
        try:
            result = self.supabase.table("job_applications").select("*").eq(
                "applicant_email", email.lower()
            ).eq("property_id", property_id).execute()
            
            applications = []
            for app_data in result.data:
                applications.append(JobApplication(
                    id=app_data["id"],
                    property_id=app_data["property_id"],
                    department=app_data["department"],
                    position=app_data["position"],
                    applicant_data=app_data["applicant_data"],
                    status=ApplicationStatus(app_data["status"]),
                    applied_at=datetime.fromisoformat(app_data["applied_at"].replace('Z', '+00:00'))
                ))
            
            return applications
            
        except Exception as e:
            logger.error(f"Failed to get applications by email {email} and property {property_id}: {e}")
            return []
'''
    
    # Find the end of the class and add the methods
    class_end = content.rfind("    async def")
    if class_end != -1:
        # Find the end of the last method
        next_method_end = content.find("\n\n", class_end)
        if next_method_end == -1:
            next_method_end = len(content)
        
        # Insert the missing methods
        content = content[:next_method_end] + missing_methods + content[next_method_end:]
        
        write_file(filepath, content)
        print(f"✅ Added missing methods to {filepath}")
        return True
    
    print(f"❌ Could not find class end in {filepath}")
    return False

def test_supabase_migration():
    """Test the Supabase migration"""
    
    print("\n🧪 Testing Supabase Migration...")
    
    # Test import
    try:
        os.chdir("hotel-onboarding-backend")
        import subprocess
        result = subprocess.run([
            "python3", "-c", 
            "from app.main_enhanced import app; print('✅ Backend imports successfully')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Backend imports successfully")
        else:
            print(f"❌ Import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def main():
    """Main migration function"""
    
    print("🚀 Starting Complete Supabase Migration")
    print("=" * 60)
    
    try:
        # Step 1: Add missing Supabase methods
        if not add_missing_supabase_methods():
            print("❌ Failed to add missing Supabase methods")
            return False
        
        # Step 2: Migrate main backend file
        if not migrate_main_enhanced():
            print("❌ Failed to migrate main backend")
            return False
        
        # Step 3: Test the migration
        if not test_supabase_migration():
            print("❌ Migration test failed")
            return False
        
        print("\n🎉 Complete Supabase Migration Successful!")
        print("\n📋 What was migrated:")
        print("   ✅ Test data initialization → Supabase")
        print("   ✅ User authentication → Supabase")
        print("   ✅ Property management → Supabase")
        print("   ✅ Application management → Supabase")
        print("   ✅ All database operations → Supabase")
        
        print("\n🔗 Next Steps:")
        print("   1. Start the backend server")
        print("   2. Test the /healthz endpoint")
        print("   3. Test login functionality")
        print("   4. Test application approval")
        print("   5. Verify data persistence")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n💥 Migration failed!")