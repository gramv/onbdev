# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-05-hr-manager-workflow-fix/spec.md

## Endpoints

### Manager Application Management

#### POST /applications/{id}/approve-with-job-details

**Purpose:** Manager approves application and sets complete job offer details
**Parameters:** 
- `id` (path): Application ID
- `job_offer` (body): Complete job offer object with title, start_date, pay_rate, supervisor, benefits_eligible
**Response:** 
```json
{
  "success": true,
  "data": {
    "application_id": "string",
    "status": "approved",
    "onboarding_session_id": "string",
    "onboarding_url": "string",
    "job_details": {...}
  }
}
```
**Errors:** 400 (invalid job details), 403 (unauthorized), 404 (application not found)

#### GET /manager/applications/pending

**Purpose:** Get pending applications for manager's properties
**Parameters:** None (uses manager authentication)
**Response:** List of applications with applicant details and application status
**Errors:** 403 (unauthorized), 500 (server error)

### Manager Onboarding Review

#### GET /manager/onboarding/pending-review

**Purpose:** Get onboarding sessions pending manager review
**Parameters:** None (filtered by manager's properties)
**Response:** 
```json
{
  "success": true,
  "data": [
    {
      "session_id": "string",
      "employee": {...},
      "form_data": {...},
      "completion_date": "string",
      "days_pending": number,
      "i9_section2_required": boolean
    }
  ]
}
```
**Errors:** 403 (unauthorized), 500 (server error)

#### POST /manager/onboarding/{session_id}/review

**Purpose:** Manager reviews and approves/rejects completed onboarding
**Parameters:**
- `session_id` (path): Onboarding session ID
- `decision` (body): "approve" | "reject" | "request_changes"
- `comments` (body): Optional review comments
**Response:** Updated onboarding session with manager approval status
**Errors:** 400 (invalid decision), 403 (unauthorized), 404 (session not found)

#### POST /manager/onboarding/{session_id}/i9-section2

**Purpose:** Complete I-9 Section 2 employer verification
**Parameters:**
- `session_id` (path): Onboarding session ID
- `i9_section2_data` (body): Complete I-9 Section 2 form data including document verification
**Response:** Completed I-9 form with both sections
**Errors:** 400 (validation error), 403 (unauthorized), 422 (incomplete data)

### HR Final Approval

#### GET /hr/onboarding/pending-final-approval

**Purpose:** Get onboarding sessions approved by managers, pending HR final approval
**Parameters:** Optional property_id filter
**Response:** List of manager-approved onboarding sessions ready for HR review
**Errors:** 403 (unauthorized), 500 (server error)

#### POST /hr/onboarding/{session_id}/final-approve

**Purpose:** HR performs final approval and creates employee record
**Parameters:**
- `session_id` (path): Onboarding session ID
- `employee_id` (body): Generated employee ID
- `official_documents` (body): Generate official I-9, W-4 PDFs
**Response:** Created employee record with compliance documents
**Errors:** 400 (validation error), 403 (unauthorized), 409 (employee already exists)

### Dashboard Stats

#### GET /manager/dashboard-stats

**Purpose:** Get manager dashboard statistics
**Parameters:** None (filtered by manager's properties)
**Response:**
```json
{
  "success": true,
  "data": {
    "pending_applications": number,
    "pending_onboarding_reviews": number,
    "active_employees": number,
    "expiring_soon": number
  }
}
```
**Errors:** 403 (unauthorized), 500 (server error)

#### GET /hr/dashboard-stats

**Purpose:** Get HR dashboard statistics across all properties
**Parameters:** None
**Response:** Complete system statistics including all properties, managers, employees, and pending items
**Errors:** 403 (unauthorized), 500 (server error)

## Controllers

### ManagerApplicationController
- **approve_application_with_job_details**: Handles complete application approval workflow
- **get_pending_applications**: Returns applications filtered by manager's properties
- **validate_job_offer_details**: Ensures all required job details are provided

### ManagerOnboardingController  
- **get_pending_reviews**: Returns onboarding sessions needing manager review
- **review_onboarding**: Processes manager review decisions
- **complete_i9_section2**: Handles I-9 Section 2 completion with federal compliance
- **validate_i9_documents**: Ensures proper document verification

### HRFinalApprovalController
- **get_pending_final_approvals**: Returns manager-approved sessions for HR review
- **perform_final_approval**: Creates employee records and generates compliance documents
- **generate_official_documents**: Creates final I-9 and W-4 PDFs with signatures

### DashboardStatsController
- **get_manager_stats**: Calculates manager-specific statistics
- **get_hr_stats**: Calculates system-wide HR statistics
- **refresh_stats_cache**: Updates cached statistics after workflow actions