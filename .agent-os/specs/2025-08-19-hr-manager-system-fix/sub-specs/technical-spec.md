# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-19-hr-manager-system-fix/spec.md

## Technical Requirements

### Backend Fixes (Priority 1)

- Fix property creation endpoint `/api/hr/properties` POST method
  - Validate request body properly
  - Handle Supabase insertions with correct field mapping
  - Return proper success response with created property data

- Fix property update endpoint `/api/hr/properties/{id}` PUT method
  - Implement proper update logic
  - Validate property ownership by HR role
  - Handle partial updates correctly

- Fix manager creation endpoint `/api/hr/managers` POST method
  - Implement proper password hashing using bcrypt
  - Create user record with correct role assignment
  - Handle property_managers junction table insertion
  - Generate temporary password and return it (not storing plain text)

- Fix manager-property assignment
  - Correct the property_managers table foreign key relationships
  - Implement proper CASCADE delete rules
  - Add validation to prevent duplicate assignments

### Frontend Components (Priority 2)

- Enhance PropertiesTab component
  - Fix form submission for property creation
  - Add proper error handling and user feedback
  - Implement loading states during API calls

- Enhance ManagersTab component  
  - Fix manager creation form
  - Display assigned properties correctly
  - Add password generation and display for new managers

- Create ManagerReviewDashboard component
  - Application list view filtered by manager's property
  - Detailed application view with all applicant information
  - Approve/Reject actions with comments
  - Status tracking and filtering

### I-9 Section 2 Implementation (Priority 3)

- Create I9Section2 component
  - Document verification interface
  - List of acceptable documents selector
  - Document number and expiry date fields
  - Digital signature capture for employer representative
  - PDF generation with completed Section 2

- Backend I-9 Section 2 endpoint
  - Store Section 2 data securely
  - Validate required fields per federal requirements
  - Generate combined I-9 PDF with both sections
  - Track completion timestamp for compliance

### Integration Requirements

- Ensure property isolation works correctly
  - Managers only see applications for their assigned properties
  - Implement RLS-like filtering at service layer
  - Add property_id validation on all manager endpoints

- Password security
  - Use bcrypt with appropriate salt rounds (12)
  - Never store or log plain text passwords
  - Implement secure password generation for new managers

- API response standardization
  - Use consistent success/error response format
  - Include proper HTTP status codes
  - Return detailed error messages for debugging

### Performance Optimization

- Implement database indexing on frequently queried columns
  - properties.id, users.email, property_managers.user_id
  - job_applications.property_id, job_applications.status

- Add caching for property and manager lists
  - Use React Query or SWR for frontend caching
  - Implement cache invalidation on updates

### Testing Requirements

- Unit tests for all fixed endpoints
- Integration tests for property-manager relationships
- E2E tests for complete HR workflow
- Compliance tests for I-9 Section 2 requirements