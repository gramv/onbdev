# Project Structure

## Root Level Organization

```
├── hotel-onboarding-backend/    # FastAPI backend application
├── hotel-onboarding-frontend/   # React frontend application
├── official-forms/              # PDF templates (for future use)
├── .kiro/                      # Kiro IDE configuration and specs
└── testing files              # Test reports and checklists
```

## Backend Structure (`hotel-onboarding-backend/`)

```
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── main_enhanced.py     # Enhanced version with additional features
│   ├── models.py            # Pydantic data models
│   ├── auth.py              # Authentication utilities
│   └── pdf_forms.py         # PDF form processing
├── tests/                   # Test files
├── pyproject.toml          # Poetry dependencies
├── .env                    # Environment variables
└── setup scripts          # Database and test data setup
```

## Frontend Structure (`hotel-onboarding-frontend/`)

```
├── src/
│   ├── components/
│   │   ├── ui/             # Reusable UI components (Radix-based)
│   │   └── form components # Specialized form components
│   ├── pages/              # Route-level page components (HR/Manager dashboards)
│   ├── contexts/           # React contexts (AuthContext)
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility functions
│   ├── assets/             # Static assets
│   └── __tests__/          # Component tests
├── public/                 # Static files
└── config files           # Vite, TypeScript, Tailwind configs
```

## Key Architectural Patterns

### Backend Patterns
- **In-memory database**: Uses Python dictionaries for data storage (development phase)
- **Role-based access**: HR vs Manager permissions determine API access
- **Application workflow**: Submit → Review → Approve/Reject → Track status
- **Token-based auth**: Simple token system for user sessions

### Frontend Patterns
- **Context providers**: AuthContext for global authentication state
- **Component composition**: UI components built with Radix primitives
- **Form handling**: React Hook Form with Zod validation
- **Route protection**: Role-based dashboard access (HR vs Manager)
- **Dashboard architecture**: Tab-based navigation for different data views

### File Naming Conventions
- **Components**: PascalCase (e.g., `JobApplicationForm.tsx`)
- **Pages**: PascalCase with "Page" suffix (e.g., `LoginPage.tsx`)
- **Utilities**: camelCase (e.g., `utils.ts`)
- **Contexts**: PascalCase with "Context" suffix (e.g., `AuthContext.tsx`)
- **Dashboards**: PascalCase with "Dashboard" suffix (e.g., `HRDashboard.tsx`)

### Import Organization
- External libraries first
- Internal components/utilities second
- Relative imports last
- Group related imports together

## Modular Employee Onboarding Structure

### Enhanced Backend Structure (`hotel-onboarding-backend/`)

```
├── app/
│   ├── __init__.py
│   ├── main.py                    # Main FastAPI application
│   ├── main_enhanced.py           # Enhanced version with onboarding
│   ├── models.py                  # Pydantic data models
│   ├── auth.py                    # Authentication utilities
│   │
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   ├── onboarding_orchestrator.py    # Workflow management
│   │   ├── form_update_service.py        # Individual form updates
│   │   ├── i9_form_service.py           # I-9 form integration
│   │   ├── w4_form_service.py           # W-4 form integration
│   │   ├── notification_service.py      # Email/SMS notifications
│   │   ├── compliance_service.py        # Federal compliance validation
│   │   ├── document_service.py          # Document storage/retrieval
│   │   └── signature_service.py         # Digital signature handling
│   │
│   ├── api/                       # API route handlers
│   │   ├── __init__.py
│   │   ├── onboarding.py          # Onboarding workflow endpoints
│   │   ├── forms.py               # Form update endpoints
│   │   ├── manager.py             # Manager-specific endpoints
│   │   ├── hr.py                  # HR-specific endpoints
│   │   └── compliance.py          # Compliance endpoints
│   │
│   ├── database/                  # Database management
│   │   ├── __init__.py
│   │   ├── supabase_service_enhanced.py  # Enhanced Supabase integration
│   │   ├── models.py              # Database models
│   │   └── migrations/            # Database migration scripts
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── pdf_generation.py     # PDF creation utilities
│       ├── encryption.py         # Data encryption utilities
│       ├── validation.py         # Form validation utilities
│       └── compliance_validation.py  # Federal compliance checks
│
├── tests/                         # Comprehensive test suite
│   ├── __init__.py
│   ├── unit/                      # Unit tests
│   │   ├── test_services/         # Service layer tests
│   │   ├── test_api/              # API endpoint tests
│   │   └── test_utils/            # Utility function tests
│   ├── integration/               # Integration tests
│   │   ├── test_workflows/        # Complete workflow tests
│   │   ├── test_compliance/       # Compliance validation tests
│   │   └── test_database/         # Database integration tests
│   └── e2e/                       # End-to-end tests
│       ├── test_onboarding_flow.py
│       ├── test_form_updates.py
│       └── test_compliance_flow.py
│
├── schemas/                       # Database schemas
│   ├── supabase_enhanced_schema.sql
│   ├── migration_scripts/
│   └── seed_data/
│
└── config/                        # Configuration files
    ├── settings.py                # Application settings
    ├── compliance_config.py       # Federal compliance configuration
    └── notification_templates/    # Email/SMS templates
```

### Enhanced Frontend Structure (`hotel-onboarding-frontend/`)

```
├── src/
│   ├── components/
│   │   ├── ui/                    # Base UI components (existing)
│   │   │
│   │   ├── onboarding/            # Modular onboarding components
│   │   │   ├── forms/             # Individual form components
│   │   │   │   ├── PersonalInfoForm.tsx
│   │   │   │   ├── I9Section1Form.tsx
│   │   │   │   ├── W4Form.tsx
│   │   │   │   ├── EmergencyContactsForm.tsx
│   │   │   │   ├── DirectDepositForm.tsx
│   │   │   │   ├── HealthInsuranceForm.tsx
│   │   │   │   ├── CompanyPoliciesForm.tsx
│   │   │   │   ├── HumanTraffickingAwareness.tsx
│   │   │   │   ├── WeaponsPolicyForm.tsx
│   │   │   │   └── BackgroundCheckForm.tsx
│   │   │   │
│   │   │   ├── workflow/          # Workflow management components
│   │   │   │   ├── OnboardingWelcome.tsx
│   │   │   │   ├── ProgressTracker.tsx
│   │   │   │   ├── StepNavigation.tsx
│   │   │   │   └── WorkflowManager.tsx
│   │   │   │
│   │   │   ├── compliance/        # Compliance components
│   │   │   │   ├── I9ComplianceValidator.tsx
│   │   │   │   ├── W4ComplianceValidator.tsx
│   │   │   │   ├── DigitalSignatureCapture.tsx
│   │   │   │   └── ComplianceChecklist.tsx
│   │   │   │
│   │   │   └── updates/           # Individual form update components
│   │   │       ├── FormUpdatePortal.tsx
│   │   │       ├── UpdateNotification.tsx
│   │   │       └── ChangeTracker.tsx
│   │   │
│   │   ├── manager/               # Manager-specific components
│   │   │   ├── review/            # Employee review components
│   │   │   │   ├── OnboardingReview.tsx
│   │   │   │   ├── I9Section2Form.tsx
│   │   │   │   ├── DocumentVerification.tsx
│   │   │   │   └── ManagerApproval.tsx
│   │   │   │
│   │   │   └── dashboard/         # Manager dashboard components
│   │   │       ├── PendingOnboarding.tsx
│   │   │       ├── OnboardingQueue.tsx
│   │   │       └── ManagerActions.tsx
│   │   │
│   │   ├── hr/                    # HR-specific components
│   │   │   ├── dashboard/         # HR dashboard components
│   │   │   │   ├── OnboardingOverview.tsx
│   │   │   │   ├── ComplianceReview.tsx
│   │   │   │   ├── AuditTrailViewer.tsx
│   │   │   │   └── DocumentPackage.tsx
│   │   │   │
│   │   │   ├── approval/          # HR approval components
│   │   │   │   ├── FinalApproval.tsx
│   │   │   │   ├── CorrectionRequest.tsx
│   │   │   │   ├── CompletionCertificate.tsx
│   │   │   │   └── HRActions.tsx
│   │   │   │
│   │   │   └── management/        # HR management components
│   │   │       ├── FormUpdateManager.tsx
│   │   │       ├── ComplianceReports.tsx
│   │   │       └── DocumentRetention.tsx
│   │   │
│   │   └── shared/                # Shared components
│   │       ├── FormWrapper.tsx
│   │       ├── ValidationMessage.tsx
│   │       ├── LoadingSpinner.tsx
│   │       └── ErrorBoundary.tsx
│   │
│   ├── pages/                     # Route-level pages
│   │   ├── onboarding/            # Onboarding pages
│   │   │   ├── OnboardingWelcome.tsx
│   │   │   ├── OnboardingPortal.tsx
│   │   │   ├── FormUpdatePortal.tsx
│   │   │   └── OnboardingComplete.tsx
│   │   │
│   │   ├── manager/               # Manager pages
│   │   │   ├── ManagerDashboard.tsx
│   │   │   ├── OnboardingReview.tsx
│   │   │   └── ManagerApproval.tsx
│   │   │
│   │   └── hr/                    # HR pages
│   │       ├── HRDashboard.tsx
│   │       ├── OnboardingApproval.tsx
│   │       ├── ComplianceReview.tsx
│   │       └── FormUpdateManagement.tsx
│   │
│   ├── contexts/                  # State management contexts
│   │   ├── AuthContext.tsx        # Authentication context
│   │   ├── OnboardingContext.tsx  # Onboarding workflow state
│   │   ├── FormUpdateContext.tsx  # Form update state
│   │   ├── ComplianceContext.tsx  # Compliance validation state
│   │   └── NotificationContext.tsx # Real-time notifications
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useOnboarding.ts       # Onboarding workflow hooks
│   │   ├── useFormUpdate.ts       # Form update hooks
│   │   ├── useCompliance.ts       # Compliance validation hooks
│   │   ├── useSignature.ts        # Digital signature hooks
│   │   └── useNotifications.ts    # Notification hooks
│   │
│   ├── services/                  # API service layers
│   │   ├── api.ts                 # Base API configuration
│   │   ├── onboardingService.ts   # Onboarding API calls
│   │   ├── formUpdateService.ts   # Form update API calls
│   │   ├── managerService.ts      # Manager API calls
│   │   ├── hrService.ts           # HR API calls
│   │   └── complianceService.ts   # Compliance API calls
│   │
│   ├── utils/                     # Utility functions
│   │   ├── formValidation.ts      # Form validation utilities
│   │   ├── complianceValidation.ts # Compliance validation utilities
│   │   ├── pdfUtils.ts            # PDF handling utilities
│   │   ├── signatureUtils.ts      # Digital signature utilities
│   │   └── dateUtils.ts           # Date/time utilities
│   │
│   ├── types/                     # TypeScript type definitions
│   │   ├── onboarding.ts          # Onboarding-related types
│   │   ├── forms.ts               # Form data types
│   │   ├── compliance.ts          # Compliance-related types
│   │   ├── api.ts                 # API response types
│   │   └── user.ts                # User and role types
│   │
│   └── __tests__/                 # Test files
│       ├── components/            # Component tests
│       │   ├── onboarding/        # Onboarding component tests
│       │   ├── manager/           # Manager component tests
│       │   └── hr/                # HR component tests
│       ├── hooks/                 # Hook tests
│       ├── services/              # Service tests
│       ├── utils/                 # Utility tests
│       └── integration/           # Integration tests
│           ├── OnboardingFlow.test.tsx
│           ├── FormUpdateFlow.test.tsx
│           └── ComplianceFlow.test.tsx
│
├── public/                        # Static assets
│   ├── forms/                     # Official form templates
│   │   ├── i9-template.pdf
│   │   └── w4-template.pdf
│   ├── images/                    # Image assets
│   └── locales/                   # Translation files
│       ├── en.json
│       └── es.json
│
└── config/                        # Configuration files
    ├── vite.config.ts             # Vite configuration
    ├── tailwind.config.js         # Tailwind CSS configuration
    ├── jest.config.js             # Jest testing configuration
    └── tsconfig.json              # TypeScript configuration
```

### Key Architectural Patterns for Onboarding

#### Modular Form Architecture
- Each form component is self-contained and reusable
- Forms can be used in full onboarding or standalone updates
- Consistent validation and state management across all forms
- Form dependencies and conditional rendering support

#### Three-Phase Workflow Management
- Clear separation of employee, manager, and HR phases
- State transitions with validation and audit trails
- Role-based access controls for each phase
- Notification system for workflow progression

#### Compliance-First Design
- Federal compliance validation built into every component
- Official form template integration
- Digital signature compliance with ESIGN Act
- Audit trail and document retention automation

#### Service Layer Architecture
- Business logic separated from API endpoints
- Reusable services for common operations
- Comprehensive error handling and validation
- Async processing for heavy operations (PDF generation, notifications)

#### Security and Privacy Architecture
- Encryption at rest and in transit
- Role-based access controls
- Secure token-based authentication
- Comprehensive audit logging