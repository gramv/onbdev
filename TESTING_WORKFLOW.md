# Onboarding Workflow Testing Guide

## Overview
This guide outlines the systematic testing approach for the integrated hotel onboarding system with candidate flow and manager workflow.

## Pre-Testing Setup
1. Start the frontend server: `cd hotel-onboarding-frontend && npm run dev`
2. Ensure backend is running on port 8000
3. Access the application at `http://localhost:5176/` (or whatever port Vite assigns)

## Testing Plan

### 1. Candidate Onboarding Flow Test

#### Access the Onboarding Portal
- URL format: `http://localhost:5176/onboard?token=<token>`
- For testing, you may need to create a mock token or use the existing token generation

#### Step-by-Step Candidate Flow Testing

**Step 1: Welcome Page**
- ✅ Verify welcome message displays correctly
- ✅ Check language selector (EN/ES) functionality
- ✅ Verify required documents list is shown
- ✅ Test estimated time display

**Step 2: Personal Information Form**
- ✅ Fill out all required fields
- ✅ Test form validation (required fields)
- ✅ Test data persistence when navigating back/forward
- ✅ Verify Spanish translation works

**Step 3: Job Details (Placeholder)**
- ✅ Verify placeholder content displays
- ✅ Test navigation continues properly

**Step 4: Document Upload (Placeholder)**
- ✅ Verify placeholder content displays
- ✅ Test navigation continues properly

**Step 5: I-9 Section 1 Form**
- ✅ Test citizenship status selection
- ✅ Verify form completion and submission
- ✅ Test attestation and signature capture
- ✅ Verify multi-language support

**Step 6: W-4 Tax Form**
- ✅ Test W-4 form integration
- ✅ Verify existing form component works properly
- ✅ Test form submission

**Step 7: Direct Deposit Form**
- ✅ Test bank account information entry
- ✅ Test routing number validation
- ✅ Test account type selection (checking/savings)
- ✅ Test deposit distribution options
- ✅ Test file upload functionality (voided check)

**Step 8: Emergency Contacts Form**
- ✅ Test primary contact information entry
- ✅ Test secondary contact information entry
- ✅ Test relationship selection
- ✅ Test phone number formatting
- ✅ Test medical information section

**Step 9: Health Insurance Form**
- ✅ Test medical plan selection
- ✅ Test coverage tier selection (employee, spouse, children, family)
- ✅ Test dental coverage options
- ✅ Test vision coverage options
- ✅ Test cost calculations
- ✅ Test dependent information entry

**Step 10: Company Policies (Weapons)**
- ✅ Test weapons policy acknowledgment
- ✅ Test signature capture
- ✅ Verify completion

**Step 11: Human Trafficking Awareness**
- ✅ Test awareness training completion
- ✅ Test signature and acknowledgment
- ✅ Verify completion

**Step 12-15: Placeholder Steps**
- ✅ Test navigation through remaining placeholder steps
- ✅ Verify progress tracking

### 2. Manager Dashboard Testing

#### Access Manager Dashboard
- URL: `http://localhost:5176/manager` (or appropriate manager login)
- Login with manager credentials

#### Manager Dashboard Features

**Dashboard Overview**
- ✅ Verify stats cards display correctly
- ✅ Check pending applications count
- ✅ Check pending onboarding reviews count
- ✅ Verify expiring soon notifications

**Onboarding Reviews Tab**
- ✅ View pending onboarding submissions
- ✅ Test employee information display
- ✅ Test progress percentage display
- ✅ Test completion date display

**Review Dialog**
- ✅ Open onboarding review dialog
- ✅ Verify employee summary section
- ✅ Test tabbed information display:
  - Personal Info tab
  - Health Insurance tab
  - Direct Deposit tab
  - Documents tab

**I-9 Section 2 Completion**
- ✅ Click "Complete I-9 Section 2" button
- ✅ Verify I9Section2Form opens in modal
- ✅ Test document verification (List A vs List B+C)
- ✅ Test employment information entry
- ✅ Test digital signature capture
- ✅ Verify form validation
- ✅ Test form submission

**Review Actions**
- ✅ Test review decision selection (approve/reject/request changes)
- ✅ Test comment entry
- ✅ Test review submission

### 3. Integration Testing

**Data Flow**
- ✅ Verify candidate data flows to manager dashboard
- ✅ Test form data persistence across steps
- ✅ Verify manager completion updates employee status

**Navigation**
- ✅ Test back/next button functionality
- ✅ Test step progression
- ✅ Verify progress bar updates

**Error Handling**
- ✅ Test form validation messages
- ✅ Test required field enforcement
- ✅ Test network error scenarios

### 4. Multi-Language Testing
- ✅ Test English/Spanish toggle functionality
- ✅ Verify translations in key components
- ✅ Test form labels and messages in both languages

## Key Components to Verify

### Forms Integration
1. **PersonalInformationForm** - Personal details collection
2. **I9Section1Form** - Employee I-9 completion
3. **W4Form** - Tax withholding setup
4. **DirectDepositForm** - Banking information
5. **EmergencyContactsForm** - Emergency contacts and medical info
6. **HealthInsuranceForm** - Insurance elections
7. **WeaponsPolicyAcknowledgment** - Policy acceptance
8. **HumanTraffickingAwareness** - Training completion
9. **I9Section2Form** - Manager document verification

### Digital Signature Integration
- ✅ Test signature capture in multiple forms
- ✅ Verify legal acknowledgments
- ✅ Test drawn vs typed signatures
- ✅ Verify signature validation

## Expected Behavior

### Successful Candidate Flow
1. Employee completes all onboarding steps
2. Progress reaches 90% (pending manager review)
3. Status changes to "employee_completed"
4. Appears in manager dashboard for review

### Successful Manager Flow
1. Manager reviews all submitted information
2. Completes I-9 Section 2 verification
3. Makes approval decision
4. Employee onboarding status updates to final state

## Common Issues to Watch For

1. **Form Validation**: Ensure all required fields are properly validated
2. **Data Persistence**: Verify form data is maintained across navigation
3. **Signature Capture**: Check that signatures are properly captured and stored
4. **Language Switching**: Ensure translations work consistently
5. **Mobile Responsiveness**: Test on different screen sizes
6. **Step Navigation**: Verify back/next buttons work correctly
7. **Progress Tracking**: Ensure progress bar reflects actual completion

## Completion Criteria

✅ **Candidate Flow**: Employee can complete entire onboarding process
✅ **Manager Flow**: Manager can review and approve onboarding
✅ **I-9 Compliance**: Complete I-9 workflow (Section 1 + Section 2)
✅ **Data Integrity**: All form data is properly collected and displayed
✅ **User Experience**: Smooth navigation and clear instructions
✅ **Error Handling**: Appropriate validation and error messages

---

## Notes for Testing
- The system uses mock data for demonstration
- Real API integration would require backend services
- Focus on UI/UX flow and component integration
- Document any bugs or improvement suggestions