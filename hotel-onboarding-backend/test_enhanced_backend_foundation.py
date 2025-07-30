#!/usr/bin/env python3
"""
Test Enhanced Backend Foundation and Models
Comprehensive testing for Task 1: Enhanced Backend Foundation and Models
"""
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import enhanced models and services
from app.models_enhanced import (
    OnboardingSession, OnboardingStatus, OnboardingStep, OnboardingPhase,
    FormUpdateSession, FormUpdateStatus, FormType, Employee, UserRole,
    AuditEntry, ComplianceCheck, DigitalSignature, SignatureType,
    generate_secure_token, calculate_expiry_time, validate_federal_ssn, validate_federal_age
)
from app.services.onboarding_orchestrator import OnboardingOrchestrator
from app.services.form_update_service import FormUpdateService

class TestResults:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []
    
    def run_test(self, test_name: str, test_func):
        """Run a test and record results"""
        self.tests_run += 1
        try:
            test_func()
            self.tests_passed += 1
            print(f"✅ {test_name}")
        except Exception as e:
            self.tests_failed += 1
            self.failures.append(f"{test_name}: {str(e)}")
            print(f"❌ {test_name}: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failures:
            print(f"\nFAILURES:")
            for failure in self.failures:
                print(f"  - {failure}")

def create_test_database() -> Dict[str, Any]:
    """Create test database with sample data"""
    database = {
        "users": {},
        "properties": {},
        "applications": {},
        "employees": {},
        "onboarding_sessions": {},
        "form_update_sessions": {},
        "documents": {},
        "signatures": {},
        "audit_trail": {},
        "compliance_checks": {}
    }
    
    # Create test employee
    test_employee = Employee(
        user_id="user_001",
        property_id="prop_001",
        manager_id="mgr_001",
        department="Front Desk",
        position="Front Desk Agent",
        hire_date=datetime.now().date(),
        personal_info={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@test.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789",
            "date_of_birth": "1990-01-01"
        }
    )
    database["employees"][test_employee.id] = test_employee
    
    return database

def test_enhanced_models():
    """Test enhanced data models"""
    
    def test_onboarding_session_creation():
        """Test OnboardingSession model creation and methods"""
        session = OnboardingSession(
            employee_id="emp_001",
            property_id="prop_001",
            manager_id="mgr_001",
            token="test_token_123",
            expires_at=calculate_expiry_time(72)
        )
        
        assert session.id is not None
        assert session.status == OnboardingStatus.NOT_STARTED
        assert session.phase == OnboardingPhase.EMPLOYEE
        assert session.progress_percentage == 0.0
        assert not session.is_expired()
        assert not session.can_transition_to_manager()
    
    def test_form_update_session_creation():
        """Test FormUpdateSession model creation and methods"""
        session = FormUpdateSession(
            employee_id="emp_001",
            form_type=FormType.W4_FORM,
            update_token="update_token_123",
            requested_by="hr_001",
            expires_at=calculate_expiry_time(168),
            change_reason="Marriage status change"
        )
        
        assert session.id is not None
        assert session.status == FormUpdateStatus.PENDING
        assert session.form_type == FormType.W4_FORM
        assert not session.is_expired()
        assert not session.can_complete()  # Needs signature and approvals
    
    def test_employee_model_methods():
        """Test Employee model methods"""
        employee = Employee(
            user_id="user_001",
            property_id="prop_001",
            manager_id="mgr_001",
            department="Front Desk",
            position="Front Desk Agent",
            hire_date=datetime.now().date(),
            personal_info={
                "first_name": "Jane",
                "last_name": "Smith"
            }
        )
        
        assert employee.get_full_name() == "Jane Smith"
        assert not employee.is_onboarding_complete()
        missing = employee.get_missing_requirements()
        assert "I-9 Form" in missing
        assert "W-4 Form" in missing
    
    def test_digital_signature_model():
        """Test DigitalSignature model"""
        signature = DigitalSignature(
            session_id="session_001",
            employee_id="emp_001",
            signature_type=SignatureType.EMPLOYEE_I9,
            signature_data="<svg>signature_data</svg>",
            signature_hash="hash123",
            signed_by="emp_001",
            signed_by_name="John Doe",
            signed_by_role=UserRole.EMPLOYEE
        )
        
        assert signature.id is not None
        assert signature.signature_type == SignatureType.EMPLOYEE_I9
        assert not signature.is_verified
    
    def test_audit_entry_model():
        """Test AuditEntry model"""
        audit = AuditEntry(
            entity_type="onboarding_session",
            entity_id="session_001",
            action="create",
            new_values={"status": "in_progress"},
            user_id="mgr_001",
            compliance_event=True,
            legal_requirement="Onboarding initiation"
        )
        
        assert audit.id is not None
        assert audit.compliance_event is True
        assert audit.timestamp is not None
    
    # Run model tests
    results = TestResults()
    results.run_test("OnboardingSession Creation", test_onboarding_session_creation)
    results.run_test("FormUpdateSession Creation", test_form_update_session_creation)
    results.run_test("Employee Model Methods", test_employee_model_methods)
    results.run_test("DigitalSignature Model", test_digital_signature_model)
    results.run_test("AuditEntry Model", test_audit_entry_model)
    
    return results

def test_onboarding_orchestrator():
    """Test OnboardingOrchestrator service"""
    database = create_test_database()
    orchestrator = OnboardingOrchestrator(database)
    
    def test_initiate_onboarding():
        """Test onboarding initiation"""
        session = orchestrator.initiate_onboarding(
            application_id="app_001",
            employee_id=list(database["employees"].keys())[0],
            property_id="prop_001",
            manager_id="mgr_001"
        )
        
        assert session.id is not None
        assert session.status == OnboardingStatus.IN_PROGRESS
        assert session.current_step == OnboardingStep.WELCOME
        assert session.token is not None
        assert session.id in database["onboarding_sessions"]
    
    def test_complete_step():
        """Test step completion"""
        # First initiate onboarding
        employee_id = list(database["employees"].keys())[0]
        session = orchestrator.initiate_onboarding(
            application_id="app_001",
            employee_id=employee_id,
            property_id="prop_001",
            manager_id="mgr_001"
        )
        
        # Complete welcome step
        success = orchestrator.complete_step(
            session.id,
            OnboardingStep.WELCOME,
            user_id=employee_id
        )
        
        assert success is True
        updated_session = database["onboarding_sessions"][session.id]
        assert OnboardingStep.WELCOME in updated_session.steps_completed
        assert updated_session.progress_percentage > 0
    
    def test_phase_transitions():
        """Test phase transitions"""
        employee_id = list(database["employees"].keys())[0]
        session = orchestrator.initiate_onboarding(
            application_id="app_001",
            employee_id=employee_id,
            property_id="prop_001",
            manager_id="mgr_001"
        )
        
        # Complete all employee steps
        for step in orchestrator.employee_steps:
            orchestrator.complete_step(session.id, step, user_id=employee_id)
        
        # Should transition to manager review
        success = orchestrator.transition_to_manager_review(session.id, user_id="mgr_001")
        assert success is True
        
        updated_session = database["onboarding_sessions"][session.id]
        assert updated_session.phase == OnboardingPhase.MANAGER
        assert updated_session.status == OnboardingStatus.MANAGER_REVIEW
    
    def test_get_pending_reviews():
        """Test getting pending reviews"""
        employee_id = list(database["employees"].keys())[0]
        session = orchestrator.initiate_onboarding(
            application_id="app_002",
            employee_id=employee_id,
            property_id="prop_001",
            manager_id="mgr_001"
        )
        
        # Complete employee steps and transition to manager
        for step in orchestrator.employee_steps:
            orchestrator.complete_step(session.id, step, user_id=employee_id)
        orchestrator.transition_to_manager_review(session.id, user_id="mgr_001")
        
        # Get pending manager reviews
        pending = orchestrator.get_pending_manager_reviews("mgr_001")
        assert len(pending) > 0
        assert any(s.id == session.id for s in pending)
    
    def test_approve_onboarding():
        """Test final onboarding approval"""
        employee_id = list(database["employees"].keys())[0]
        session = orchestrator.initiate_onboarding(
            application_id="app_003",
            employee_id=employee_id,
            property_id="prop_001",
            manager_id="mgr_001"
        )
        
        # Complete all steps
        for step in orchestrator.employee_steps:
            orchestrator.complete_step(session.id, step, user_id=employee_id)
        orchestrator.transition_to_manager_review(session.id, user_id="mgr_001")
        
        for step in orchestrator.manager_steps:
            orchestrator.complete_step(session.id, step, user_id="mgr_001")
        orchestrator.transition_to_hr_approval(session.id, user_id="hr_001")
        
        # Approve onboarding
        success = orchestrator.approve_onboarding(session.id, "hr_001", "Approved for employment")
        assert success is True
        
        updated_session = database["onboarding_sessions"][session.id]
        assert updated_session.status == OnboardingStatus.APPROVED
        assert updated_session.progress_percentage == 100.0
    
    # Run orchestrator tests
    results = TestResults()
    results.run_test("Initiate Onboarding", test_initiate_onboarding)
    results.run_test("Complete Step", test_complete_step)
    results.run_test("Phase Transitions", test_phase_transitions)
    results.run_test("Get Pending Reviews", test_get_pending_reviews)
    results.run_test("Approve Onboarding", test_approve_onboarding)
    
    return results

def test_form_update_service():
    """Test FormUpdateService"""
    database = create_test_database()
    form_service = FormUpdateService(database)
    
    def test_generate_update_link():
        """Test form update link generation"""
        employee_id = list(database["employees"].keys())[0]
        
        session = form_service.generate_update_link(
            employee_id=employee_id,
            form_type=FormType.W4_FORM,
            change_reason="Marriage status change",
            requested_by="hr_001"
        )
        
        assert session.id is not None
        assert session.form_type == FormType.W4_FORM
        assert session.update_token is not None
        assert session.status == FormUpdateStatus.PENDING
        assert session.id in database["form_update_sessions"]
    
    def test_validate_update_token():
        """Test update token validation"""
        employee_id = list(database["employees"].keys())[0]
        
        session = form_service.generate_update_link(
            employee_id=employee_id,
            form_type=FormType.PERSONAL_INFO,
            change_reason="Address change",
            requested_by="hr_001"
        )
        
        # Validate token
        validated_session = form_service.validate_update_token(session.update_token)
        assert validated_session is not None
        assert validated_session.id == session.id
        
        # Test invalid token
        invalid_session = form_service.validate_update_token("invalid_token")
        assert invalid_session is None
    
    def test_save_form_update():
        """Test saving form update data"""
        employee_id = list(database["employees"].keys())[0]
        
        session = form_service.generate_update_link(
            employee_id=employee_id,
            form_type=FormType.PERSONAL_INFO,
            change_reason="Address change",
            requested_by="hr_001"
        )
        
        # Save updated data
        updated_data = {
            "first_name": "John",
            "last_name": "Doe",
            "address": "456 New Street",
            "city": "New City",
            "state": "CA",
            "zip_code": "90210"
        }
        
        success = form_service.save_form_update(
            session.id,
            updated_data,
            signature_data="<svg>signature</svg>",
            user_id=employee_id
        )
        
        assert success is True
        updated_session = database["form_update_sessions"][session.id]
        assert updated_session.updated_data == updated_data
        assert updated_session.signature_captured is True
    
    def test_approve_form_update():
        """Test form update approval"""
        employee_id = list(database["employees"].keys())[0]
        
        session = form_service.generate_update_link(
            employee_id=employee_id,
            form_type=FormType.W4_FORM,
            change_reason="Tax withholding change",
            requested_by="hr_001"
        )
        
        # Save update data
        updated_data = {"filing_status": "Married filing jointly"}
        form_service.save_form_update(
            session.id,
            updated_data,
            signature_data="<svg>signature</svg>",
            user_id=employee_id
        )
        
        # Approve as manager (if required)
        if session.requires_manager_approval:
            success = form_service.approve_form_update(
                session.id,
                "mgr_001",
                "manager",
                "Approved by manager"
            )
            assert success is True
        
        # Approve as HR
        success = form_service.approve_form_update(
            session.id,
            "hr_001",
            "hr",
            "Approved by HR"
        )
        assert success is True
        
        updated_session = database["form_update_sessions"][session.id]
        assert updated_session.status == FormUpdateStatus.COMPLETED
        assert updated_session.hr_approved_at is not None
    
    def test_get_pending_approvals():
        """Test getting pending approvals"""
        # Create a fresh database for this test to avoid conflicts
        fresh_database = create_test_database()
        fresh_form_service = FormUpdateService(fresh_database)
        employee_id = list(fresh_database["employees"].keys())[0]
        
        # Create multiple update sessions
        session1 = fresh_form_service.generate_update_link(
            employee_id=employee_id,
            form_type=FormType.W4_FORM,
            change_reason="Tax change 1",
            requested_by="hr_001"
        )
        
        session2 = fresh_form_service.generate_update_link(
            employee_id=employee_id,
            form_type=FormType.DIRECT_DEPOSIT,
            change_reason="Bank change",
            requested_by="hr_001"
        )
        
        # Save data for both
        fresh_form_service.save_form_update(session1.id, {"filing_status": "Single"}, 
                                          signature_data="<svg>sig1</svg>", user_id=employee_id)
        fresh_form_service.save_form_update(session2.id, {"bank_name": "New Bank"}, 
                                          signature_data="<svg>sig2</svg>", user_id=employee_id)
        
        # Get pending HR approvals
        pending_hr = fresh_form_service.get_pending_approvals("hr")
        assert len(pending_hr) >= 2
        
        # Get pending manager approvals (should include W4 and direct deposit)
        pending_mgr = fresh_form_service.get_pending_approvals("manager", "prop_001")
        assert len(pending_mgr) >= 2  # Both require manager approval
    
    # Run form update service tests
    results = TestResults()
    results.run_test("Generate Update Link", test_generate_update_link)
    results.run_test("Validate Update Token", test_validate_update_token)
    results.run_test("Save Form Update", test_save_form_update)
    results.run_test("Approve Form Update", test_approve_form_update)
    results.run_test("Get Pending Approvals", test_get_pending_approvals)
    
    return results

def test_utility_functions():
    """Test utility functions"""
    
    def test_generate_secure_token():
        """Test secure token generation"""
        token1 = generate_secure_token()
        token2 = generate_secure_token()
        
        assert token1 != token2
        assert len(token1) > 20  # Should be reasonably long
        assert isinstance(token1, str)
    
    def test_calculate_expiry_time():
        """Test expiry time calculation"""
        expiry = calculate_expiry_time(24)
        now = datetime.utcnow()
        
        assert expiry > now
        assert expiry < now + timedelta(hours=25)  # Should be within 25 hours
    
    def test_validate_federal_ssn():
        """Test SSN validation"""
        # Valid SSN
        assert validate_federal_ssn("123-45-6789") is True
        assert validate_federal_ssn("123456789") is True
        
        # Invalid SSNs
        assert validate_federal_ssn("000-00-0000") is False
        assert validate_federal_ssn("666-00-0000") is False
        assert validate_federal_ssn("900-00-0000") is False
        assert validate_federal_ssn("123-00-0000") is False
        assert validate_federal_ssn("123-45-0000") is False
        assert validate_federal_ssn("111111111") is False  # Known invalid
    
    def test_validate_federal_age():
        """Test age validation"""
        # Valid ages (18+)
        assert validate_federal_age("1990-01-01") is True
        assert validate_federal_age("2000-01-01") is True
        
        # Invalid ages (under 18)
        current_year = datetime.now().year
        future_birth_year = current_year - 17
        assert validate_federal_age(f"{future_birth_year}-01-01") is False
        
        # Invalid format
        assert validate_federal_age("invalid-date") is False
    
    # Run utility tests
    results = TestResults()
    results.run_test("Generate Secure Token", test_generate_secure_token)
    results.run_test("Calculate Expiry Time", test_calculate_expiry_time)
    results.run_test("Validate Federal SSN", test_validate_federal_ssn)
    results.run_test("Validate Federal Age", test_validate_federal_age)
    
    return results

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Backend Foundation and Models")
    print("=" * 60)
    
    all_results = TestResults()
    
    # Test enhanced models
    print("\n📋 Testing Enhanced Data Models...")
    model_results = test_enhanced_models()
    all_results.tests_run += model_results.tests_run
    all_results.tests_passed += model_results.tests_passed
    all_results.tests_failed += model_results.tests_failed
    all_results.failures.extend(model_results.failures)
    
    # Test onboarding orchestrator
    print("\n🎯 Testing Onboarding Orchestrator Service...")
    orchestrator_results = test_onboarding_orchestrator()
    all_results.tests_run += orchestrator_results.tests_run
    all_results.tests_passed += orchestrator_results.tests_passed
    all_results.tests_failed += orchestrator_results.tests_failed
    all_results.failures.extend(orchestrator_results.failures)
    
    # Test form update service
    print("\n📝 Testing Form Update Service...")
    form_results = test_form_update_service()
    all_results.tests_run += form_results.tests_run
    all_results.tests_passed += form_results.tests_passed
    all_results.tests_failed += form_results.tests_failed
    all_results.failures.extend(form_results.failures)
    
    # Test utility functions
    print("\n🔧 Testing Utility Functions...")
    utility_results = test_utility_functions()
    all_results.tests_run += utility_results.tests_run
    all_results.tests_passed += utility_results.tests_passed
    all_results.tests_failed += utility_results.tests_failed
    all_results.failures.extend(utility_results.failures)
    
    # Print overall summary
    all_results.print_summary()
    
    # Return exit code
    return 0 if all_results.tests_failed == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)