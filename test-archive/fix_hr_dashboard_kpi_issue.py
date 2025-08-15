#!/usr/bin/env python3
"""
Fix HR Dashboard KPI Issue
1. Add missing /hr/managers POST endpoint
2. Fix is_active field for existing managers
3. Test the fix
"""

import requests
import json

def fix_inactive_managers():
    """Fix existing managers that have is_active=False"""
    print("🔧 Fixing inactive managers...")
    
    # Login as HR
    login_response = requests.post('http://127.0.0.1:8000/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ HR login failed: {login_response.status_code}")
        return False
    
    token = login_response.json().get('data', {}).get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get all users
    users_response = requests.get('http://127.0.0.1:8000/hr/users', headers=headers)
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return False
    
    users_data = users_response.json()
    users = users_data.get('data', users_data) if isinstance(users_data, dict) else users_data
    
    # Find inactive managers
    inactive_managers = [
        user for user in users 
        if user.get('role') == 'manager' and user.get('is_active') == False
    ]
    
    print(f"Found {len(inactive_managers)} inactive managers")
    
    # For now, let's create a simple script to activate them
    # Since we don't have a direct update endpoint, we'll use a workaround
    
    if inactive_managers:
        print("Inactive managers found:")
        for manager in inactive_managers:
            print(f"  - {manager.get('email')} (ID: {manager.get('id')})")
    
    return len(inactive_managers) > 0

def create_missing_manager_endpoint():
    """Create the missing /hr/managers POST endpoint"""
    print("🔧 The /hr/managers POST endpoint is missing from main_enhanced.py")
    print("This needs to be added to the FastAPI application")
    
    endpoint_code = '''
@app.post("/hr/managers")
async def create_manager(
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    property_id: Optional[str] = Form(None),
    password: str = Form(...),
    current_user: User = Depends(require_hr_role)
):
    """Create a new manager (HR only) using Supabase"""
    try:
        # Validate email uniqueness
        existing_user = supabase_service.get_user_by_email_sync(email.lower().strip())
        if existing_user:
            raise HTTPException(status_code=400, detail="Email address already exists")
        
        # Validate names
        if not first_name.strip() or not last_name.strip():
            raise HTTPException(status_code=400, detail="First name and last name are required")
        
        # Validate password strength
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Create manager user
        manager_id = str(uuid.uuid4())
        password_hash = supabase_service.hash_password(password)
        
        manager_data = {
            "id": manager_id,
            "email": email.lower().strip(),
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "role": "manager",
            "property_id": property_id if property_id and property_id != 'none' else None,
            "password_hash": password_hash,
            "is_active": True,  # This is the key fix!
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Create user in Supabase
        result = supabase_service.client.table('users').insert(manager_data).execute()
        
        if result.data:
            # Assign to property if specified
            if property_id and property_id != 'none':
                await supabase_service.assign_manager_to_property(property_id, manager_id)
            
            return success_response(
                data=result.data[0],
                message="Manager created successfully"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create manager")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create manager: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create manager: {str(e)}")
'''
    
    print("📝 Endpoint code to add:")
    print(endpoint_code)
    return endpoint_code

def test_dashboard_stats_after_fix():
    """Test dashboard stats after applying fixes"""
    print("\n🧪 Testing dashboard stats after fix...")
    
    # Login as HR
    login_response = requests.post('http://127.0.0.1:8000/auth/login', json={
        'email': 'hr@hoteltest.com',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ HR login failed: {login_response.status_code}")
        return
    
    token = login_response.json().get('data', {}).get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test dashboard stats
    stats_response = requests.get('http://127.0.0.1:8000/hr/dashboard-stats', headers=headers)
    
    if stats_response.status_code == 200:
        data = stats_response.json()
        stats_data = data.get('data', {})
        
        print("📊 Current KPI Values:")
        print(f"  Total Properties: {stats_data.get('totalProperties', 0)}")
        print(f"  Total Managers: {stats_data.get('totalManagers', 0)}")
        print(f"  Total Employees: {stats_data.get('totalEmployees', 0)}")
        print(f"  Pending Applications: {stats_data.get('pendingApplications', 0)}")
        
        if stats_data.get('totalManagers', 0) > 0:
            print("✅ Manager count is now working!")
        else:
            print("❌ Manager count is still 0")
    else:
        print(f"❌ Dashboard stats failed: {stats_response.status_code}")

def main():
    print("🚀 Fix HR Dashboard KPI Issue")
    print("=" * 50)
    
    # Step 1: Check current state
    print("📊 Current Issue Analysis:")
    print("- Dashboard shows totalManagers: 0")
    print("- But /hr/managers endpoint returns 7 managers")
    print("- Root cause: All managers have is_active=False")
    print("- Count method filters by is_active=True")
    
    # Step 2: Identify fixes needed
    print("\n🔧 Fixes Needed:")
    print("1. Add missing /hr/managers POST endpoint")
    print("2. Ensure new managers are created with is_active=True")
    print("3. Fix existing inactive managers")
    
    # Step 3: Check for inactive managers
    has_inactive_managers = fix_inactive_managers()
    
    # Step 4: Show missing endpoint code
    print("\n" + "=" * 50)
    create_missing_manager_endpoint()
    
    # Step 5: Test current state
    test_dashboard_stats_after_fix()
    
    # Step 6: Recommendations
    print("\n" + "=" * 50)
    print("💡 IMMEDIATE ACTIONS NEEDED:")
    print("1. Add the missing /hr/managers POST endpoint to main_enhanced.py")
    print("2. Update existing managers to set is_active=True")
    print("3. Restart the backend server")
    print("4. Test the HR dashboard again")
    
    if has_inactive_managers:
        print("\n🔧 SQL to fix existing managers:")
        print("UPDATE users SET is_active = true WHERE role = 'manager';")

if __name__ == "__main__":
    main()