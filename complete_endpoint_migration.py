#!/usr/bin/env python3

"""
Complete the migration of all endpoints to use Supabase
"""

import re

def update_manager_applications_endpoint():
    """Update the manager applications endpoint to use Supabase"""
    
    filepath = "hotel-onboarding-backend/app/main_enhanced.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find and replace the manager applications endpoint
    old_manager_apps = r'@app\.get\("/manager/applications"\)\s*async def get_manager_applications\(.*?\):\s*"""Get applications for manager's property""".*?return applications'
    
    new_manager_apps = '''@app.get("/manager/applications")
async def get_manager_applications(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    current_user: User = Depends(require_manager_role)
):
    """Get applications for manager's property using Supabase"""
    try:
        # Get manager's properties
        manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
        if not manager_properties:
            return []
        
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
        
        # Convert to dict format for frontend compatibility
        result = []
        for app in applications:
            result.append({
                "id": app.id,
                "property_id": app.property_id,
                "department": app.department,
                "position": app.position,
                "applicant_data": app.applicant_data,
                "status": app.status,
                "applied_at": app.applied_at.isoformat(),
                "reviewed_by": getattr(app, 'reviewed_by', None),
                "reviewed_at": getattr(app, 'reviewed_at', None).isoformat() if getattr(app, 'reviewed_at', None) else None
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get manager applications: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")'''
    
    content = re.sub(old_manager_apps, new_manager_apps, content, flags=re.DOTALL)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("✅ Updated manager applications endpoint")

def update_application_approval_endpoint():
    """Update the application approval endpoint to use Supabase"""
    
    filepath = "hotel-onboarding-backend/app/main_enhanced.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find and replace the application approval endpoint
    old_approval = r'@app\.post\("/applications/\{application_id\}/approve"\)\s*async def approve_application\(.*?\):\s*"""Approve application and create secure onboarding session""".*?return \{'
    
    new_approval = '''@app.post("/applications/{application_id}/approve")
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
    """Approve application and create secure onboarding session using Supabase"""
    if current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Only managers can approve applications")
    
    # Get application from Supabase
    application = await supabase_service.get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Verify manager has access to this property
    manager_properties = supabase_service.get_manager_properties_sync(current_user.id)
    property_ids = [prop.id for prop in manager_properties]
    
    if application.property_id not in property_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update application status
    await supabase_service.update_application_status(
        application_id, 
        "approved", 
        current_user.id
    )
    
    # Create employee record
    employee_data = {
        "application_id": application_id,
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
    try:
        onboarding_session = onboarding_orchestrator.initiate_onboarding(
            application_id=application_id,
            employee_id=employee.id,
            property_id=application.property_id,
            manager_id=current_user.id,
            expires_hours=72
        )
        session_id = onboarding_session.id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create onboarding session: {str(e)}")
    
    # Move other applications to talent pool
    await supabase_service.move_competing_applications_to_talent_pool(
        application.property_id,
        application.position,
        application_id,
        current_user.id
    )
    
    # Generate onboarding URL
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    onboarding_url = f"{base_url}/onboard?token={onboarding_session.token}"
    
    return {'''
    
    content = re.sub(old_approval, new_approval, content, flags=re.DOTALL)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("✅ Updated application approval endpoint")

def add_missing_supabase_methods_part2():
    """Add more missing methods to Supabase service"""
    
    filepath = "hotel-onboarding-backend/app/supabase_service_enhanced.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    additional_methods = '''
    async def get_applications_by_property(self, property_id: str) -> List[JobApplication]:
        """Get all applications for a property"""
        try:
            result = self.supabase.table("job_applications").select("*").eq(
                "property_id", property_id
            ).order("applied_at", desc=True).execute()
            
            applications = []
            for app_data in result.data:
                applications.append(JobApplication(
                    id=app_data["id"],
                    property_id=app_data["property_id"],
                    department=app_data["department"],
                    position=app_data["position"],
                    applicant_data=app_data["applicant_data"],
                    status=ApplicationStatus(app_data["status"]),
                    applied_at=datetime.fromisoformat(app_data["applied_at"].replace('Z', '+00:00')),
                    reviewed_by=app_data.get("reviewed_by"),
                    reviewed_at=datetime.fromisoformat(app_data["reviewed_at"].replace('Z', '+00:00')) if app_data.get("reviewed_at") else None
                ))
            
            return applications
            
        except Exception as e:
            logger.error(f"Failed to get applications for property {property_id}: {e}")
            return []
    
    async def get_application_by_id(self, application_id: str) -> Optional[JobApplication]:
        """Get application by ID"""
        try:
            result = self.supabase.table("job_applications").select("*").eq(
                "id", application_id
            ).execute()
            
            if result.data:
                app_data = result.data[0]
                return JobApplication(
                    id=app_data["id"],
                    property_id=app_data["property_id"],
                    department=app_data["department"],
                    position=app_data["position"],
                    applicant_data=app_data["applicant_data"],
                    status=ApplicationStatus(app_data["status"]),
                    applied_at=datetime.fromisoformat(app_data["applied_at"].replace('Z', '+00:00')),
                    reviewed_by=app_data.get("reviewed_by"),
                    reviewed_at=datetime.fromisoformat(app_data["reviewed_at"].replace('Z', '+00:00')) if app_data.get("reviewed_at") else None
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get application {application_id}: {e}")
            return None
    
    async def update_application_status(self, application_id: str, status: str, reviewed_by: str) -> bool:
        """Update application status"""
        try:
            result = self.supabase.table("job_applications").update({
                "status": status,
                "reviewed_by": reviewed_by,
                "reviewed_at": datetime.now(timezone.utc).isoformat()
            }).eq("id", application_id).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Failed to update application status {application_id}: {e}")
            return False
    
    async def create_employee(self, employee_data: dict) -> Employee:
        """Create employee record"""
        try:
            # Generate employee ID
            employee_id = str(uuid.uuid4())
            
            # Prepare employee data for insertion
            insert_data = {
                "id": employee_id,
                "application_id": employee_data["application_id"],
                "property_id": employee_data["property_id"],
                "manager_id": employee_data["manager_id"],
                "department": employee_data["department"],
                "position": employee_data["position"],
                "hire_date": employee_data["hire_date"],
                "pay_rate": employee_data["pay_rate"],
                "pay_frequency": employee_data["pay_frequency"],
                "employment_type": employee_data["employment_type"],
                "personal_info": employee_data["personal_info"],
                "onboarding_status": employee_data["onboarding_status"],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            result = self.supabase.table("employees").insert(insert_data).execute()
            
            if result.data:
                emp_data = result.data[0]
                return Employee(
                    id=emp_data["id"],
                    application_id=emp_data["application_id"],
                    property_id=emp_data["property_id"],
                    manager_id=emp_data["manager_id"],
                    department=emp_data["department"],
                    position=emp_data["position"],
                    hire_date=datetime.fromisoformat(emp_data["hire_date"]).date() if emp_data["hire_date"] else None,
                    pay_rate=emp_data["pay_rate"],
                    pay_frequency=emp_data["pay_frequency"],
                    employment_type=emp_data["employment_type"],
                    personal_info=emp_data["personal_info"],
                    onboarding_status=OnboardingStatus(emp_data["onboarding_status"]),
                    created_at=datetime.fromisoformat(emp_data["created_at"].replace('Z', '+00:00'))
                )
            
            raise Exception("No data returned from employee creation")
            
        except Exception as e:
            logger.error(f"Failed to create employee: {e}")
            raise
    
    async def move_competing_applications_to_talent_pool(self, property_id: str, position: str, approved_app_id: str, reviewed_by: str) -> int:
        """Move competing applications to talent pool"""
        try:
            # Get competing applications
            result = self.supabase.table("job_applications").select("*").eq(
                "property_id", property_id
            ).eq("position", position).eq("status", "pending").neq("id", approved_app_id).execute()
            
            count = 0
            for app_data in result.data:
                # Update to talent pool
                self.supabase.table("job_applications").update({
                    "status": "talent_pool",
                    "reviewed_by": reviewed_by,
                    "reviewed_at": datetime.now(timezone.utc).isoformat(),
                    "talent_pool_date": datetime.now(timezone.utc).isoformat()
                }).eq("id", app_data["id"]).execute()
                count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to move competing applications to talent pool: {e}")
            return 0
'''
    
    # Add the methods before the sync methods
    sync_methods_start = content.find("    # Synchronous wrapper methods for compatibility")
    if sync_methods_start != -1:
        content = content[:sync_methods_start] + additional_methods + "\n" + content[sync_methods_start:]
    else:
        content = content.rstrip() + additional_methods + '\n'
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print("✅ Added additional Supabase methods")

def main():
    """Main function"""
    
    print("🔄 Completing Endpoint Migration to Supabase")
    print("=" * 50)
    
    try:
        # Add missing Supabase methods
        add_missing_supabase_methods_part2()
        
        # Update manager applications endpoint
        update_manager_applications_endpoint()
        
        # Update application approval endpoint
        update_application_approval_endpoint()
        
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
            print("✅ Endpoint migration completed")
            return True
        else:
            print(f"❌ Import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Endpoint migration completed!")
    else:
        print("\n💥 Migration failed!")