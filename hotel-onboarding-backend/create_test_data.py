#!/usr/bin/env python3
"""
Direct database setup script - adds test data directly to the backend
This modifies the main_enhanced.py file to include test data on startup
"""

import uuid
from datetime import datetime, timezone, date

def generate_test_data():
    """Generate test data structure"""
    
    # Create test users
    hr_user_id = str(uuid.uuid4())
    manager_user_id = str(uuid.uuid4())
    property_id = str(uuid.uuid4())
    application_id = str(uuid.uuid4())
    
    test_data = {
        "users": {
            hr_user_id: {
                "id": hr_user_id,
                "email": "hr@hoteltest.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "role": "hr",
                "property_id": None,
                "created_at": datetime.now(timezone.utc)
            },
            manager_user_id: {
                "id": manager_user_id,
                "email": "manager@hoteltest.com", 
                "first_name": "Mike",
                "last_name": "Wilson",
                "role": "manager",
                "property_id": property_id,
                "created_at": datetime.now(timezone.utc)
            }
        },
        "properties": {
            property_id: {
                "id": property_id,
                "name": "Grand Plaza Hotel",
                "address": "123 Main Street",
                "city": "Downtown",
                "state": "CA",
                "zip_code": "90210",
                "phone": "(555) 123-4567",
                "qr_code_url": f"https://app.domain.com/apply/{property_id}",
                "manager_ids": [manager_user_id],
                "created_at": datetime.now(timezone.utc)
            }
        },
        "applications": {
            application_id: {
                "id": application_id,
                "property_id": property_id,
                "department": "Front Desk",
                "position": "Front Desk Agent",
                "applicant_data": {
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
                "status": "pending",
                "applied_at": datetime.now(timezone.utc),
                "reviewed_by": None,
                "reviewed_at": None
            }
        }
    }
    
    return test_data, {
        "hr_user_id": hr_user_id,
        "manager_user_id": manager_user_id,
        "property_id": property_id,
        "application_id": application_id
    }

def create_database_init_code():
    """Create the code to initialize test data"""
    test_data, ids = generate_test_data()
    
    init_code = f'''
# Test Data Initialization
def initialize_test_data():
    """Initialize database with test data for development"""
    
    # HR User
    hr_user = User(
        id="{ids['hr_user_id']}",
        email="hr@hoteltest.com",
        first_name="Sarah",
        last_name="Johnson", 
        role=UserRole.HR,
        created_at=datetime.now(timezone.utc)
    )
    database["users"]["{ids['hr_user_id']}"] = hr_user
    
    # Manager User  
    manager_user = User(
        id="{ids['manager_user_id']}",
        email="manager@hoteltest.com",
        first_name="Mike", 
        last_name="Wilson",
        role=UserRole.MANAGER,
        property_id="{ids['property_id']}",
        created_at=datetime.now(timezone.utc)
    )
    database["users"]["{ids['manager_user_id']}"] = manager_user
    
    # Test Property
    property_obj = Property(
        id="{ids['property_id']}",
        name="Grand Plaza Hotel",
        address="123 Main Street",
        city="Downtown", 
        state="CA",
        zip_code="90210",
        phone="(555) 123-4567",
        qr_code_url="https://app.domain.com/apply/{ids['property_id']}",
        manager_ids=["{ids['manager_user_id']}"],
        created_at=datetime.now(timezone.utc)
    )
    database["properties"]["{ids['property_id']}"] = property_obj
    
    # Test Application
    application = JobApplication(
        id="{ids['application_id']}",
        property_id="{ids['property_id']}",
        department="Front Desk",
        position="Front Desk Agent",
        applicant_data={{
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
        }},
        status=ApplicationStatus.PENDING,
        applied_at=datetime.now(timezone.utc)
    )
    database["applications"]["{ids['application_id']}"] = application
    
    print("✅ Test data initialized:")
    print(f"   HR: hr@hoteltest.com (ID: {ids['hr_user_id']})")
    print(f"   Manager: manager@hoteltest.com (ID: {ids['manager_user_id']})")
    print(f"   Property: Grand Plaza Hotel (ID: {ids['property_id']})")
    print(f"   Application: John Doe - Front Desk Agent (ID: {ids['application_id']})")

# Initialize test data on startup
initialize_test_data()
'''
    
    return init_code, ids

def main():
    """Add test data initialization to main_enhanced.py"""
    
    print("🏨 Adding test data to backend...")
    
    # Read the current main_enhanced.py file
    try:
        with open('hotel-onboarding-backend/app/main_enhanced.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ main_enhanced.py not found. Make sure you're in the right directory.")
        return
    
    # Check if test data already exists
    if "initialize_test_data" in content:
        print("⚠️  Test data initialization already exists in main_enhanced.py")
        return
    
    # Generate the initialization code
    init_code, ids = create_database_init_code()
    
    # Find the right place to insert (after database initialization)
    insert_point = content.find('# Authentication Dependencies')
    if insert_point == -1:
        insert_point = content.find('def get_current_user')
    
    if insert_point == -1:
        print("❌ Could not find insertion point in main_enhanced.py")
        return
    
    # Insert the test data code
    new_content = content[:insert_point] + init_code + "\n" + content[insert_point:]
    
    # Write back to file
    with open('hotel-onboarding-backend/app/main_enhanced.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Test data added to main_enhanced.py")
    print("\n📋 Test Accounts Available:")
    print("HR Account:")
    print("  Email: hr@hoteltest.com")
    print("  Password: password123")
    print(f"  User ID: {ids['hr_user_id']}")
    
    print("\nManager Account:")
    print("  Email: manager@hoteltest.com") 
    print("  Password: password123")
    print(f"  User ID: {ids['manager_user_id']}")
    
    print(f"\n🏨 Test Property:")
    print(f"  Name: Grand Plaza Hotel")
    print(f"  ID: {ids['property_id']}")
    
    print(f"\n📝 Test Application:")
    print(f"  ID: {ids['application_id']}")
    print(f"  Applicant: John Doe - Front Desk Agent")
    
    print(f"\n🚀 Next Steps:")
    print(f"  1. Restart the backend server:")
    print(f"     cd hotel-onboarding-backend")
    print(f"     python -m uvicorn app.main_enhanced:app --reload")
    print(f"  2. Test login endpoints:")
    print(f"     POST /auth/login with hr@hoteltest.com")
    print(f"     POST /auth/login with manager@hoteltest.com")

if __name__ == "__main__":
    main()