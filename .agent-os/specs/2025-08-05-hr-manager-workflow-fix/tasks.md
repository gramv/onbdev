# Spec Tasks

## Tasks

- [ ] 1. Fix Manager Application Approval Workflow
  - [ ] 1.1 Write tests for manager application approval with job details
  - [ ] 1.2 Fix `/applications/{id}/approve-enhanced` endpoint to properly set job details and create onboarding sessions
  - [ ] 1.3 Update manager authentication to properly check property access
  - [ ] 1.4 Fix application status transitions from pending → approved
  - [ ] 1.5 Ensure onboarding session creation includes job details in form_data
  - [ ] 1.6 Verify all tests pass for manager application approval

- [ ] 2. Build Manager Onboarding Review System
  - [ ] 2.1 Write tests for manager onboarding review workflow
  - [ ] 2.2 Create `/manager/onboarding/pending-review` endpoint to get completed employee onboarding
  - [ ] 2.3 Implement `/manager/onboarding/{session_id}/review` for manager approval/rejection
  - [ ] 2.4 Create `/manager/onboarding/{session_id}/i9-section2` endpoint for I-9 Section 2 completion
  - [ ] 2.5 Update onboarding status transitions: employee_completed → manager_review → hr_approval
  - [ ] 2.6 Verify all tests pass for manager onboarding review

- [ ] 3. Fix Manager Dashboard Frontend
  - [ ] 3.1 Write tests for EnhancedManagerDashboard component functionality
  - [ ] 3.2 Replace mock data with real API calls to manager endpoints
  - [ ] 3.3 Build job detail setting form for application approval
  - [ ] 3.4 Integrate I9Section2Form component properly in manager review workflow
  - [ ] 3.5 Add proper loading states and error handling for all async operations
  - [ ] 3.6 Verify all tests pass for manager dashboard functionality

- [ ] 4. Implement HR Final Approval Workflow
  - [ ] 4.1 Write tests for HR final approval process
  - [ ] 4.2 Create `/hr/onboarding/pending-final-approval` endpoint for manager-approved items
  - [ ] 4.3 Implement `/hr/onboarding/{session_id}/final-approve` for creating employee records
  - [ ] 4.4 Build HR dashboard tab for final approvals with proper UI
  - [ ] 4.5 Generate official compliance documents (I-9, W-4 PDFs) on final approval
  - [ ] 4.6 Verify all tests pass for HR final approval workflow

- [ ] 5. Fix Authentication and Role-Based Access
  - [ ] 5.1 Write tests for property-based manager access control
  - [ ] 5.2 Update all manager endpoints to check property access permissions
  - [ ] 5.3 Ensure HR endpoints have system-wide access while managers are property-restricted
  - [ ] 5.4 Fix authentication middleware to properly validate tokens and roles
  - [ ] 5.5 Add proper error responses for unauthorized access attempts
  - [ ] 5.6 Verify all tests pass for authentication and authorization

- [ ] 6. Standardize API Responses and Error Handling
  - [ ] 6.1 Write tests for consistent API response formats
  - [ ] 6.2 Update all manager and HR endpoints to use ResponseFormatter
  - [ ] 6.3 Implement proper input validation for all forms and requests
  - [ ] 6.4 Add comprehensive error handling with meaningful error messages
  - [ ] 6.5 Ensure all API responses follow the standardized format
  - [ ] 6.6 Verify all tests pass for API response consistency

- [ ] 7. Integration Testing and End-to-End Workflow
  - [ ] 7.1 Write comprehensive integration tests for complete three-phase workflow
  - [ ] 7.2 Test full workflow: Application → Manager Approval → Employee Onboarding → Manager Review → HR Approval
  - [ ] 7.3 Verify proper status transitions and data flow throughout the entire process  
  - [ ] 7.4 Test error handling and edge cases for the complete workflow
  - [ ] 7.5 Ensure all notifications and email triggers work correctly
  - [ ] 7.6 Verify all integration tests pass for the complete HR/Manager workflow system