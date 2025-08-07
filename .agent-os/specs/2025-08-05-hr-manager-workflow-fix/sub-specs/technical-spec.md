# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-05-hr-manager-workflow-fix/spec.md

## Technical Requirements

### Backend API Fixes

- **Manager Application Approval Endpoint** - Fix `/applications/{id}/approve` and `/applications/{id}/approve-enhanced` to properly set job details and create onboarding sessions
- **Manager Dashboard Stats** - Fix `/manager/dashboard-stats` to show accurate application and onboarding counts
- **Manager Onboarding Review** - Implement `/manager/onboarding/{session_id}/review` for reviewing completed employee onboarding
- **I-9 Section 2 Completion** - Create `/manager/onboarding/{session_id}/i9-section2` for employer verification
- **HR Final Approval** - Implement `/hr/onboarding/{session_id}/final-approve` for creating employee records
- **Status Transition Management** - Ensure proper status flow: pending → approved → employee_completed → manager_review → hr_approval

### Frontend Component Fixes

- **EnhancedManagerDashboard.tsx** - Fix mock data usage, connect to real API endpoints, implement job detail setting during approval
- **Manager Onboarding Review Interface** - Build complete review interface with form data display, I-9 Section 2 completion, and approval workflow
- **Application Approval Modal** - Create proper job detail setting form with validation
- **I-9 Section 2 Component Integration** - Ensure I9Section2Form properly integrates with manager review workflow
- **HRDashboard.tsx** - Add manager-approved items tab and final approval workflow

### Authentication & Authorization

- **Property-Based Access Control** - Ensure managers only see applications/onboarding for their assigned properties
- **Role-Based Endpoint Protection** - Verify all manager endpoints require manager role and HR endpoints require HR role
- **Supabase Service Integration** - Use existing EnhancedSupabaseService for all data operations with proper authentication

### Data Flow Integration

- **Application Status Management** - Implement proper status transitions with audit trail
- **Onboarding Session Linking** - Ensure approved applications properly create onboarding sessions with job details
- **Progress Tracking** - Maintain accurate progress tracking through all three phases
- **Notification Integration** - Use existing email service for status change notifications

### Error Handling & Validation

- **Standardized API Responses** - Use existing ResponseFormatter for consistent error responses
- **Input Validation** - Validate all form inputs for job details, review comments, and approval decisions
- **Permission Validation** - Proper error messages for unauthorized access attempts
- **Timeout Handling** - Handle I-9 Section 2 completion deadlines (3 business days)

### Performance & UI/UX

- **Loading States** - Proper loading indicators for all async operations
- **Real-time Updates** - Update dashboard stats after actions without full page refresh
- **Form Auto-save** - Implement auto-save for job detail setting and review forms
- **Mobile Responsiveness** - Ensure all manager and HR interfaces work on mobile devices
- **Accessibility** - Maintain WCAG compliance for all interface elements