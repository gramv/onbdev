#!/usr/bin/env python3

def add_missing_supabase_methods():
    """Add missing methods to EnhancedSupabaseService"""
    
    print("🔧 Adding Missing Supabase Methods")
    print("=" * 50)
    
    # Read current supabase service
    with open("hotel-onboarding-backend/app/supabase_service_enhanced.py", "r") as f:
        content = f.read()
    
    # Methods to add
    additional_methods = '''
    
    # ==========================================
    # ONBOARDING SESSION METHODS
    # ==========================================
    
    async def create_onboarding_session(self, session):
        """Create onboarding session in Supabase"""
        try:
            session_data = {
                "id": session.id,
                "application_id": session.application_id,
                "employee_id": session.employee_id,
                "property_id": session.property_id,
                "manager_id": session.manager_id,
                "token": session.token,
                "status": session.status.value,
                "phase": session.phase.value,
                "current_step": session.current_step.value,
                "expires_at": session.expires_at.isoformat(),
                "created_at": session.created_at.isoformat()
            }
            
            result = self.client.table("onboarding_sessions").insert(session_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error creating onboarding session: {e}")
            return None
    
    async def get_onboarding_session_by_token(self, token):
        """Get onboarding session by token"""
        try:
            result = self.client.table("onboarding_sessions").select("*").eq("token", token).execute()
            
            if result.data:
                session_data = result.data[0]
                # Convert back to OnboardingSession object
                from .models_enhanced import OnboardingSession, OnboardingStatus, OnboardingPhase, OnboardingStep
                from datetime import datetime
                
                return OnboardingSession(
                    id=session_data["id"],
                    application_id=session_data["application_id"],
                    employee_id=session_data["employee_id"],
                    property_id=session_data["property_id"],
                    manager_id=session_data["manager_id"],
                    token=session_data["token"],
                    status=OnboardingStatus(session_data["status"]),
                    phase=OnboardingPhase(session_data["phase"]),
                    current_step=OnboardingStep(session_data["current_step"]),
                    expires_at=datetime.fromisoformat(session_data["expires_at"]),
                    created_at=datetime.fromisoformat(session_data["created_at"])
                )
            return None
            
        except Exception as e:
            print(f"Error getting onboarding session by token: {e}")
            return None
    
    async def get_onboarding_session_by_id(self, session_id):
        """Get onboarding session by ID"""
        try:
            result = self.client.table("onboarding_sessions").select("*").eq("id", session_id).execute()
            
            if result.data:
                session_data = result.data[0]
                # Convert back to OnboardingSession object
                from .models_enhanced import OnboardingSession, OnboardingStatus, OnboardingPhase, OnboardingStep
                from datetime import datetime
                
                return OnboardingSession(
                    id=session_data["id"],
                    application_id=session_data["application_id"],
                    employee_id=session_data["employee_id"],
                    property_id=session_data["property_id"],
                    manager_id=session_data["manager_id"],
                    token=session_data["token"],
                    status=OnboardingStatus(session_data["status"]),
                    phase=OnboardingPhase(session_data["phase"]),
                    current_step=OnboardingStep(session_data["current_step"]),
                    expires_at=datetime.fromisoformat(session_data["expires_at"]),
                    created_at=datetime.fromisoformat(session_data["created_at"])
                )
            return None
            
        except Exception as e:
            print(f"Error getting onboarding session by ID: {e}")
            return None
    
    async def update_onboarding_session(self, session):
        """Update onboarding session in Supabase"""
        try:
            session_data = {
                "status": session.status.value,
                "phase": session.phase.value,
                "current_step": session.current_step.value,
                "updated_at": session.updated_at.isoformat() if hasattr(session, 'updated_at') else None
            }
            
            # Add optional fields if they exist
            if hasattr(session, 'approved_by') and session.approved_by:
                session_data["approved_by"] = session.approved_by
            if hasattr(session, 'approved_at') and session.approved_at:
                session_data["approved_at"] = session.approved_at.isoformat()
            if hasattr(session, 'rejected_by') and session.rejected_by:
                session_data["rejected_by"] = session.rejected_by
            if hasattr(session, 'rejection_reason') and session.rejection_reason:
                session_data["rejection_reason"] = session.rejection_reason
            if hasattr(session, 'rejected_at') and session.rejected_at:
                session_data["rejected_at"] = session.rejected_at.isoformat()
            
            result = self.client.table("onboarding_sessions").update(session_data).eq("id", session.id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error updating onboarding session: {e}")
            return None
    
    async def update_employee_onboarding_status(self, employee_id, status, session_id=None):
        """Update employee onboarding status"""
        try:
            update_data = {
                "onboarding_status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if session_id:
                update_data["onboarding_session_id"] = session_id
            
            result = self.client.table("employees").update(update_data).eq("id", employee_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error updating employee onboarding status: {e}")
            return None
    
    async def store_onboarding_form_data(self, session_id, step, form_data):
        """Store onboarding form data"""
        try:
            data = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "step": step.value,
                "form_data": form_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("onboarding_form_data").insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error storing onboarding form data: {e}")
            return None
    
    async def store_onboarding_signature(self, session_id, step, signature_data):
        """Store onboarding signature data"""
        try:
            data = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "step": step.value,
                "signature_data": signature_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("onboarding_signatures").insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error storing onboarding signature: {e}")
            return None
    
    async def get_onboarding_sessions_by_manager_and_status(self, manager_id, status):
        """Get onboarding sessions by manager and status"""
        try:
            result = self.client.table("onboarding_sessions").select("*").eq("manager_id", manager_id).eq("status", status.value).execute()
            
            sessions = []
            if result.data:
                from .models_enhanced import OnboardingSession, OnboardingStatus, OnboardingPhase, OnboardingStep
                from datetime import datetime
                
                for session_data in result.data:
                    session = OnboardingSession(
                        id=session_data["id"],
                        application_id=session_data["application_id"],
                        employee_id=session_data["employee_id"],
                        property_id=session_data["property_id"],
                        manager_id=session_data["manager_id"],
                        token=session_data["token"],
                        status=OnboardingStatus(session_data["status"]),
                        phase=OnboardingPhase(session_data["phase"]),
                        current_step=OnboardingStep(session_data["current_step"]),
                        expires_at=datetime.fromisoformat(session_data["expires_at"]),
                        created_at=datetime.fromisoformat(session_data["created_at"])
                    )
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            print(f"Error getting onboarding sessions by manager and status: {e}")
            return []
    
    async def get_onboarding_sessions_by_status(self, status):
        """Get onboarding sessions by status"""
        try:
            result = self.client.table("onboarding_sessions").select("*").eq("status", status.value).execute()
            
            sessions = []
            if result.data:
                from .models_enhanced import OnboardingSession, OnboardingStatus, OnboardingPhase, OnboardingStep
                from datetime import datetime
                
                for session_data in result.data:
                    session = OnboardingSession(
                        id=session_data["id"],
                        application_id=session_data["application_id"],
                        employee_id=session_data["employee_id"],
                        property_id=session_data["property_id"],
                        manager_id=session_data["manager_id"],
                        token=session_data["token"],
                        status=OnboardingStatus(session_data["status"]),
                        phase=OnboardingPhase(session_data["phase"]),
                        current_step=OnboardingStep(session_data["current_step"]),
                        expires_at=datetime.fromisoformat(session_data["expires_at"]),
                        created_at=datetime.fromisoformat(session_data["created_at"])
                    )
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            print(f"Error getting onboarding sessions by status: {e}")
            return []
    
    # ==========================================
    # FORM UPDATE SESSION METHODS
    # ==========================================
    
    async def create_form_update_session(self, session):
        """Create form update session in Supabase"""
        try:
            session_data = {
                "id": session.id,
                "employee_id": session.employee_id,
                "form_type": session.form_type.value,
                "update_token": session.update_token,
                "requested_by": session.requested_by,
                "current_data": session.current_data,
                "expires_at": session.expires_at.isoformat(),
                "created_at": session.created_at.isoformat()
            }
            
            result = self.client.table("form_update_sessions").insert(session_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error creating form update session: {e}")
            return None
    
    async def get_form_update_session_by_token(self, token):
        """Get form update session by token"""
        try:
            result = self.client.table("form_update_sessions").select("*").eq("update_token", token).execute()
            
            if result.data:
                session_data = result.data[0]
                from .models_enhanced import FormUpdateSession, FormType
                from datetime import datetime
                
                return FormUpdateSession(
                    id=session_data["id"],
                    employee_id=session_data["employee_id"],
                    form_type=FormType(session_data["form_type"]),
                    update_token=session_data["update_token"],
                    requested_by=session_data["requested_by"],
                    current_data=session_data["current_data"],
                    expires_at=datetime.fromisoformat(session_data["expires_at"]),
                    created_at=datetime.fromisoformat(session_data["created_at"])
                )
            return None
            
        except Exception as e:
            print(f"Error getting form update session by token: {e}")
            return None
    
    async def get_form_update_session_by_id(self, session_id):
        """Get form update session by ID"""
        try:
            result = self.client.table("form_update_sessions").select("*").eq("id", session_id).execute()
            
            if result.data:
                session_data = result.data[0]
                from .models_enhanced import FormUpdateSession, FormType
                from datetime import datetime
                
                return FormUpdateSession(
                    id=session_data["id"],
                    employee_id=session_data["employee_id"],
                    form_type=FormType(session_data["form_type"]),
                    update_token=session_data["update_token"],
                    requested_by=session_data["requested_by"],
                    current_data=session_data["current_data"],
                    expires_at=datetime.fromisoformat(session_data["expires_at"]),
                    created_at=datetime.fromisoformat(session_data["created_at"])
                )
            return None
            
        except Exception as e:
            print(f"Error getting form update session by ID: {e}")
            return None
    
    async def update_form_update_session(self, session):
        """Update form update session in Supabase"""
        try:
            session_data = {
                "updated_data": session.updated_data,
                "signature_data": getattr(session, 'signature_data', None),
                "completed_at": session.completed_at.isoformat() if hasattr(session, 'completed_at') and session.completed_at else None,
                "updated_at": session.updated_at.isoformat() if hasattr(session, 'updated_at') else None,
                "expired": getattr(session, 'expired', False)
            }
            
            result = self.client.table("form_update_sessions").update(session_data).eq("id", session.id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error updating form update session: {e}")
            return None
    
    async def get_form_update_sessions_by_employee(self, employee_id, completed=None):
        """Get form update sessions by employee"""
        try:
            query = self.client.table("form_update_sessions").select("*").eq("employee_id", employee_id)
            
            if completed is not None:
                if completed:
                    query = query.not_.is_("completed_at", "null")
                else:
                    query = query.is_("completed_at", "null")
            
            result = query.execute()
            
            sessions = []
            if result.data:
                from .models_enhanced import FormUpdateSession, FormType
                from datetime import datetime
                
                for session_data in result.data:
                    session = FormUpdateSession(
                        id=session_data["id"],
                        employee_id=session_data["employee_id"],
                        form_type=FormType(session_data["form_type"]),
                        update_token=session_data["update_token"],
                        requested_by=session_data["requested_by"],
                        current_data=session_data["current_data"],
                        expires_at=datetime.fromisoformat(session_data["expires_at"]),
                        created_at=datetime.fromisoformat(session_data["created_at"])
                    )
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            print(f"Error getting form update sessions by employee: {e}")
            return []
    
    # ==========================================
    # AUDIT TRAIL METHODS
    # ==========================================
    
    async def create_audit_entry(self, audit_entry):
        """Create audit trail entry"""
        try:
            entry_data = {
                "id": audit_entry.id,
                "session_id": audit_entry.session_id,
                "action": audit_entry.action,
                "user_id": audit_entry.user_id,
                "details": audit_entry.details,
                "timestamp": audit_entry.timestamp.isoformat()
            }
            
            result = self.client.table("audit_trail").insert(entry_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error creating audit entry: {e}")
            return None'''
    
    # Add the methods before the last closing brace
    if content.endswith('\n'):
        content = content[:-1]  # Remove trailing newline
    
    # Find the last method and add our methods before the class ends
    insertion_point = content.rfind('\n    def ')
    if insertion_point == -1:
        # If no methods found, add at the end of the class
        insertion_point = content.rfind('\n')
    else:
        # Find the end of the last method
        next_method_or_end = content.find('\n\n', insertion_point + 1)
        if next_method_or_end == -1:
            insertion_point = len(content)
        else:
            insertion_point = next_method_or_end
    
    # Insert the new methods
    new_content = content[:insertion_point] + additional_methods + content[insertion_point:]
    
    # Add necessary imports at the top
    import_additions = '''import uuid
from datetime import datetime
'''
    
    # Find where to insert imports (after existing imports)
    import_insertion = new_content.find('\nclass EnhancedSupabaseService')
    if import_insertion != -1:
        new_content = new_content[:import_insertion] + '\n' + import_additions + new_content[import_insertion:]
    
    # Write the updated file
    with open("hotel-onboarding-backend/app/supabase_service_enhanced.py", "w") as f:
        f.write(new_content)
    
    print("✅ Added missing Supabase methods")
    print("   - Onboarding session CRUD operations")
    print("   - Form update session CRUD operations") 
    print("   - Audit trail methods")
    print("   - Employee onboarding status updates")

if __name__ == "__main__":
    add_missing_supabase_methods()