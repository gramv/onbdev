# Spec Requirements Document

> Spec: HR Manager Workflow Fix
> Created: 2025-08-05
> Status: Planning

## Overview

Analyze and fix all HR and manager related code to implement a proper three-phase workflow (Application → Manager Review/Approval → Employee Onboarding → Manager Verification → HR Final Approval) with complete role-based access control and workflow orchestration.

## User Stories

### Manager Application Review and Approval

As a Manager, I want to review job applications for my property and approve candidates with specific job details (title, start date, compensation, supervisor) so that approved applicants can begin their onboarding process with the correct job information pre-populated.

**Detailed Workflow**: Manager logs in → Views pending applications for their property → Reviews applicant details → Sets job offer details (title, start date, pay rate, supervisor, benefits eligibility) → Approves application → System creates onboarding session → Employee receives onboarding link with job details already configured.

### Manager Onboarding Review and I-9 Section 2 Completion

As a Manager, I want to review completed employee onboarding submissions, verify documents, complete I-9 Section 2 verification, and approve the onboarding for HR final review so that the employee verification process is complete before HR creates the final employee record.

**Detailed Workflow**: Manager receives notification when employee completes onboarding → Reviews all submitted forms (personal info, W-4, health insurance, direct deposit) → Verifies employee identity documents → Completes I-9 Section 2 within 3 business days → Either approves for HR review or requests corrections → HR receives notification for final approval.

### HR Complete Workflow Management

As an HR user, I want complete oversight of the entire workflow from application management through employee record creation so that I can ensure compliance, manage talent pools, and maintain proper employee records.

**Detailed Workflow**: HR can view all applications across properties → Manage talent pools → Review manager-approved onboardings → Perform final compliance checks → Create official employee records → Generate required government documents → Archive completed processes according to federal retention requirements.

## Spec Scope

1. **Manager Dashboard Enhancement** - Fix EnhancedManagerDashboard to properly handle application approvals with job detail setting and onboarding reviews with I-9 Section 2 completion
2. **Application Approval Workflow** - Complete the manager application approval process that sets job details and creates onboarding sessions
3. **Three-Phase Status Management** - Implement proper status transitions through application → manager_review → employee_completed → manager_approved → hr_final_approval
4. **Manager Onboarding Review** - Build complete manager review interface for completed employee onboarding with I-9 Section 2 completion
5. **HR Dashboard Integration** - Ensure HR dashboard properly shows manager-approved items awaiting final HR approval
6. **Role-Based Access Control** - Fix authentication and authorization for proper manager property access and HR system-wide access
7. **API Endpoint Consolidation** - Standardize all manager and HR endpoints to use consistent response formats and proper error handling

## Out of Scope

- Employee onboarding portal modifications (this is working correctly)
- New feature development beyond fixing existing broken workflows
- Database schema changes (use existing Supabase schema)
- Email notification system changes (use existing email service)

## Expected Deliverable

1. **Fully Functional Manager Approval Workflow** - Managers can approve applications, set job details, and create onboarding sessions that work end-to-end
2. **Complete Manager Onboarding Review** - Managers can review completed onboarding, complete I-9 Section 2, and approve for HR review
3. **Working HR Final Approval Process** - HR can review manager-approved onboardings and create final employee records
4. **Proper Role-Based Access** - All endpoints respect property-based access for managers and system-wide access for HR
5. **Consistent API Responses** - All manager and HR endpoints use standardized response formats with proper error handling