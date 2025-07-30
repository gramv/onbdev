# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive hotel employee onboarding system built with a FastAPI backend and React/TypeScript frontend. The system handles the complete employee lifecycle from job application to onboarding completion, including document management, digital signatures, and compliance requirements.

**CRITICAL IMPLEMENTATION APPROACH**: This system is being rebuilt using a **brick-by-brick methodology** where each page/component is built individually, tested thoroughly, then connected to the next page. This ensures a stable, working system at each step rather than attempting to build everything at once.

**MODULAR FORM ARCHITECTURE**: The system is designed with complete modularity where individual forms (W-4, I-9, health insurance, etc.) can be sent independently to employees for updates at any time. When an employee's situation changes (marriage, dependents, address), HR can send just the specific form needed for update without requiring a complete onboarding process.

## Three-Phase Onboarding Workflow

1. **Employee Phase**: Complete required forms and documentation
2. **Manager Phase**: Review employee submissions and complete I-9 Section 2
3. **HR Phase**: Final approval and compliance verification

## Brick-by-Brick Implementation Plan

### Phase 1: Foundation & Cleanup (CURRENT FOCUS)
**Status**: ✅ IN PROGRESS - Fixing component prop structure

**Completed Tasks:**
- ✅ Fixed WelcomeStep component to use direct props instead of useOutletContext
- ✅ Fixed PersonalInfoStep component prop structure
- ✅ Fixed I9Section1Step component prop structure
- ✅ Created TestStepComponents for isolated testing
- ✅ Added autoFillManager utility for consistent data management

**Current Task:**
- 🔄 Testing basic component rendering and navigation
- 🔄 Ensuring all step components work with direct props pattern

**Next Steps:**
1. Complete remaining step component fixes (JobDetailsStep, etc.)
2. Create simple navigation wrapper that works
3. Test basic data flow between components
4. Verify each component renders without errors

### Phase 2: Core Page Implementation (PLANNED)
**Approach**: Build → Test → Link pattern

**Page Order** (based on "2025+ New Employee Hire Packet" analysis):

#### Page 1: Manager Forms & Setup
- **Purpose**: Manager completes property setup and employee position details
- **Components**: Property info, job description, manager contact
- **Testing**: Verify manager can complete forms and submit
- **Link**: Direct to employee notification system

#### Page 2: Employee Welcome & Language Selection  
- **Purpose**: Employee receives notification and selects language preference
- **Components**: WelcomeStep (already fixed), language toggle, overview
- **Testing**: Test language switching, welcome flow
- **Link**: Connect to job details confirmation

#### Page 3: Job Details Confirmation
- **Purpose**: Employee reviews and confirms job details set by manager
- **Components**: JobDetailsStep (already fixed), job info display, confirmations
- **Testing**: Verify job details display correctly, confirmations work
- **Link**: Connect to personal information collection

#### Page 4: Personal Information Collection
- **Purpose**: Collect employee personal details and emergency contacts
- **Components**: PersonalInfoStep (already fixed), PersonalInformationForm, EmergencyContactsForm
- **Testing**: Test form validation, data persistence, emergency contacts
- **Link**: Connect to federal compliance forms

#### Page 5: I-9 Section 1 (Federal Compliance)
- **Purpose**: Employee completes I-9 Section 1 employment eligibility verification
- **Components**: I9Section1Step (already fixed), I9Section1Form, digital signature
- **Testing**: Test federal validation, signature capture, compliance rules
- **Link**: Connect to I-9 supplements if needed

#### Page 6: I-9 Supplements A & B (Conditional)
- **Purpose**: Complete I-9 Supplement A (Preparer/Translator) or B (for certain cases)
- **Components**: I9SupplementA, I9SupplementB with smart field mapping
- **Testing**: Test conditional logic, ensure fields stay blank per federal requirements
- **Link**: Connect to document upload

#### Page 7: Document Upload & Verification
- **Purpose**: Upload identity and work authorization documents
- **Components**: DocumentUploadStep, OCR processing, validation
- **Testing**: Test file upload, OCR accuracy, document validation
- **Link**: Connect to W-4 tax information

#### Page 8: W-4 Tax Information (Federal Compliance)
- **Purpose**: Complete W-4 Employee's Withholding Certificate
- **Components**: W4FormStep, W4Form with IRS validation
- **Testing**: Test tax calculations, validation rules, digital signature
- **Link**: Connect to direct deposit setup

#### Page 9: Direct Deposit Setup
- **Purpose**: Set up banking information for payroll
- **Components**: DirectDepositStep, banking validation, security
- **Testing**: Test bank validation, security measures, form submission
- **Link**: Connect to health insurance enrollment

#### Page 10: Health Insurance Enrollment
- **Purpose**: Select health insurance options and dependents
- **Components**: HealthInsuranceStep, plan comparisons, dependent management
- **Testing**: Test plan selection, dependent calculations, enrollment
- **Link**: Connect to company policies

#### Page 11: Company Policies & Acknowledgments
- **Purpose**: Review and acknowledge company policies
- **Components**: CompanyPoliciesStep, policy display, acknowledgments
- **Testing**: Test policy display, acknowledgment tracking
- **Link**: Connect to specialized policy forms

#### Page 12: Human Trafficking Awareness (Federal Requirement)
- **Purpose**: Complete federally required human trafficking awareness training
- **Components**: HumanTraffickingAwareness, training content, certification
- **Testing**: Test training completion, certification generation
- **Link**: Connect to weapons policy if applicable

#### Page 13: Weapons Policy Acknowledgment (Property-Specific)
- **Purpose**: Acknowledge weapons policy for security positions
- **Components**: WeaponsPolicyStep, conditional display based on position
- **Testing**: Test conditional logic, policy acknowledgment
- **Link**: Connect to background check authorization  

#### Page 14: Background Check Authorization
- **Purpose**: Authorize background check processing
- **Components**: BackgroundCheckStep, authorization forms, consent
- **Testing**: Test authorization process, consent management
- **Link**: Connect to photo capture

#### Page 15: Employee Photo Capture
- **Purpose**: Capture employee photo for ID badge and records
- **Components**: PhotoCaptureStep, camera integration, photo validation
- **Testing**: Test camera access, photo quality, storage
- **Link**: Connect to final review

#### Page 16: Employee Final Review & Submission
- **Purpose**: Review all entered information and submit for manager approval
- **Components**: FinalReviewStep, comprehensive summary, submission
- **Testing**: Test complete data review, submission process
- **Link**: Connect to manager review workflow

### Phase 3: Manager Review Integration (PLANNED)
**Purpose**: Integrate manager workflow for completing I-9 Section 2 and final approval

#### Manager Review Dashboard
- **Components**: Manager interface for reviewing submitted onboarding
- **Features**: I-9 Section 2 completion, document verification, approval workflow
- **Testing**: Test manager access, I-9 Section 2 completion, approval process

#### I-9 Section 2 Completion (Manager)
- **Components**: Manager completes I-9 Section 2 within 3 business days
- **Features**: Document review, employer verification, signature
- **Testing**: Test timing compliance, document verification, completion

### Phase 4: Integration & Testing (PLANNED)
**Purpose**: Connect all pages into seamless workflow

#### Navigation System
- **Components**: Step-by-step navigation, progress tracking, back/forward functionality
- **Features**: URL routing, progress persistence, error handling
- **Testing**: Test complete workflow, navigation, data persistence

#### Data Flow Integration
- **Components**: Unified data management, auto-fill functionality, validation
- **Features**: Cross-component data sharing, validation consistency
- **Testing**: Test data flow, validation, auto-fill accuracy

#### PDF Generation & Review
- **Components**: Official document generation using government templates
- **Features**: I-9 PDF generation, W-4 PDF generation, signature integration
- **Testing**: Test PDF accuracy, signature placement, federal compliance

### Phase 5: Production Readiness (PLANNED)
**Purpose**: Final testing and production deployment preparation

#### Comprehensive Testing
- **End-to-end workflow testing**: Complete onboarding process from start to finish
- **Federal compliance validation**: Ensure all government requirements are met
- **Multi-language testing**: Verify English/Spanish functionality
- **Manager workflow testing**: Complete manager review and approval process

#### Performance & Security
- **Security audit**: Ensure all personal data is properly protected
- **Performance optimization**: Optimize loading times and user experience
- **Error handling**: Comprehensive error handling and user feedback

## Government Compliance Requirements

### I-9 Employment Eligibility Verification
- **Section 1**: Must be completed by employee on or before first day of work
- **Section 2**: Must be completed by employer within 3 business days of start date
- **Supplements A/B**: Only used in specific circumstances, most fields must remain blank
- **Document Requirements**: Must verify both identity AND work authorization
- **Retention**: Must be retained for 3 years after hire date or 1 year after termination

### W-4 Employee's Withholding Certificate
- **IRS Compliance**: Must use current year IRS form template
- **Validation**: Must validate tax calculations and withholding amounts
- **Digital Signature**: Must capture employee signature with legal compliance metadata
- **Updates**: Employees can update W-4 information at any time

### Federal Documentation Standards
- **Digital Signatures**: Must include timestamp, IP address, legal compliance metadata
- **Data Retention**: All federal forms must be retained per government requirements
- **Privacy Protection**: All personal information must be encrypted and secured
- **Audit Trail**: Complete audit trail required for all compliance-related actions

## Component Architecture

### Step Component Pattern (CURRENT IMPLEMENTATION)
All onboarding step components follow this standardized pattern:

```typescript
interface StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function StepName(props: StepProps) {
  // Component implementation using direct props
  // NO useOutletContext() calls
}
```

### Data Management
- **autoFillManager**: Centralized utility for managing form auto-fill across steps
- **Progress Tracking**: Each step saves progress independently with step ID
- **Validation**: Each component handles its own validation and completion status

## Testing Strategy

### Component-Level Testing
- **Individual Step Testing**: Each step component tested in isolation
- **Props Interface Testing**: Verify all components work with standardized props
- **Validation Testing**: Test form validation and completion logic

### Integration Testing  
- **Navigation Flow**: Test navigation between steps
- **Data Persistence**: Test data saving and loading across steps
- **Language Switching**: Test bilingual functionality

### End-to-End Testing
- **Complete Workflow**: Test entire onboarding process from start to finish
- **Manager Integration**: Test manager review and completion workflow
- **Federal Compliance**: Test all government compliance requirements

## Development Commands

### Backend
```bash
cd hotel-onboarding-backend
poetry install                    # Install dependencies
poetry run python app/main.py     # Run development server on port 8000
poetry run python app/main_enhanced.py  # Run enhanced server on port 8000
poetry run pytest tests/        # Run backend tests
poetry run python -m pytest tests/test_integration.py  # Run integration tests
```

### Frontend
```bash
cd hotel-onboarding-frontend
npm install                       # Install dependencies
npm run dev                      # Start development server (http://localhost:3000)
npm run build                    # Build for production
npm run test                     # Run Jest tests
npm run test:watch              # Run tests in watch mode
npm run lint                    # Run ESLint
npm run test -- --coverage      # Run tests with coverage report
```

### Testing Individual Components
```bash
# Backend: Run specific test file
cd hotel-onboarding-backend
poetry run python test_<filename>.py

# Frontend: Run specific test file
cd hotel-onboarding-frontend
npm test src/__tests__/<filename>.test.tsx
```

### Common Test Scripts
```bash
# Backend test data setup
poetry run python create_test_data.py
poetry run python setup_test_accounts.py

# Testing specific features
poetry run python test_job_application_submission.py
poetry run python test_manager_access_control.py
poetry run python test_email_service.py
```

### Testing Routes
- `/test-steps` - Test individual step components in isolation
- `/onboard` - Main enhanced onboarding portal (under development)
- `/manager` - Manager dashboard for reviews and approvals
- `/job-application` - Public job application form
- `/login` - Authentication page
- `/hr-dashboard` - HR management interface

## Architecture

### Backend (hotel-onboarding-backend/)
- **Framework**: FastAPI with Python 3.12+
- **Database**: In-memory database (dictionary-based) for development
- **Key Files**:
  - `app/main.py`: Core FastAPI application with basic functionality
  - `app/main_enhanced.py`: Enhanced version with additional features (primary implementation)
  - `app/models.py`: Comprehensive Pydantic models for all data structures
  - `app/auth.py`: Authentication and authorization logic
  - `app/pdf_forms.py`: PDF form generation and processing with government templates
  - `app/i9_section2.py`: I-9 Section 2 employer verification logic
  - `app/email_service.py`: Email notification service for onboarding workflows
  - `app/qr_service.py`: QR code generation for job application links
  - `app/document_service.py`: Document upload and OCR processing
  - `app/compliance_engine.py`: Federal compliance validation engine
- **External Services**: Groq API for OCR/vision processing of documents
- **Dependencies**: Managed via Poetry (`pyproject.toml`)

### Frontend (hotel-onboarding-frontend/)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Radix UI components with Tailwind CSS
- **State Management**: React Context API (AuthContext, LanguageContext)
- **Routing**: React Router v7 with navigation hooks
- **Internationalization**: i18next for EN/ES language support
- **Key Pages**:
  - `HomePage.tsx`: Landing page
  - `LoginPage.tsx`: Authentication
  - `HRDashboard.tsx`: HR management interface
  - `ManagerDashboard.tsx`: Manager review interface
  - `JobApplicationFormV2.tsx`: Public job application (enhanced version)
  - `EnhancedOnboardingPortal.tsx`: Primary employee onboarding workflow with government compliance
  - `OnboardingWelcome.tsx`: Employee onboarding welcome page
  - `OnboardingComplete.tsx`: Completion confirmation page
- **Components**: Modular form components in `components/` including:
  - `I9Section1Form.tsx`: Federal-compliant I-9 Section 1 with validation
  - `W4Form.tsx`: IRS-compliant W-4 Employee's Withholding Certificate
  - `HealthInsuranceForm.tsx`: Health insurance enrollment
  - `DirectDepositForm.tsx`: Banking information setup
  - `EmergencyContactsForm.tsx`: Emergency contact information
  - `DigitalSignatureCapture.tsx`: Legal signature capture component
  - `PDFViewer.tsx`: Document preview component
- **Testing**: Comprehensive Jest test suite with React Testing Library

## Data Models

The system uses comprehensive Pydantic models defined in `models.py`:
- **User Management**: User, Property models with role-based access
- **Applications**: JobApplication with validation and status tracking
- **Onboarding**: OnboardingSession with progress tracking and step management
- **Documents**: Document, DigitalSignature with OCR and approval workflows
- **Forms**: Specialized models for I-9, W-4, health insurance, personal info

## Authentication

- Token-based authentication using user IDs as tokens
- Role-based access control (HR, Manager, Employee)
- Special endpoints for HR user creation with secret keys
- Property-based access restrictions for managers

## Environment Setup

The system expects the following environment variables:
- `GROQ_API_KEY`: For OCR document processing
- `GROQ_MODEL`: Model to use (default: llama-3.3-70b-versatile)
- `GROQ_MAX_TOKENS`: Token limit for API calls
- `GROQ_TEMPERATURE`: Temperature for API responses
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`: Email configuration
- `EMAIL_FROM`: Sender email address for notifications

## Development Notes

- CORS is fully disabled for development (allow all origins)
- File uploads are stored in base64 format in the in-memory database
- The system includes test data creation scripts (`create_test_data.py`, `setup_test_accounts.py`)
- Enhanced components are the primary implementations with federal compliance and validation
- Onboarding workflow supports multi-language (EN/ES) and government compliance requirements
- **CRITICAL**: Always test each component individually before integrating into the full workflow
- **CRITICAL**: Follow the brick-by-brick approach - build one page, test it, then move to the next
- **CRITICAL**: Never attempt to build the entire onboarding experience at once

## API Endpoints Structure

### Public Endpoints (No Auth Required)
- `GET /api/properties/{property_id}/public-info` - Public property information
- `POST /api/job-application` - Submit job application
- `GET /api/qr/{qr_id}` - Redirect from QR code scan

### HR Endpoints (HR Role Required)
- `POST /api/hr/create` - Create HR user with secret key
- `GET /api/hr/dashboard` - HR dashboard data
- `POST /api/properties` - Create new property
- `GET /api/analytics/*` - Analytics endpoints

### Manager Endpoints (Manager Role Required)
- `GET /api/managers/dashboard` - Manager dashboard data
- `POST /api/managers/complete-i9-section2` - Complete I-9 Section 2
- `PUT /api/applications/{app_id}/status` - Update application status
- `GET /api/managers/talent-pool` - View talent pool

### Employee Endpoints (Employee Role Required)
- `GET /api/onboarding/session` - Get onboarding session
- `POST /api/onboarding/step/{step_id}` - Submit step data
- `POST /api/documents/upload` - Upload documents
- `GET /api/forms/pdf/*` - Generate PDF forms

## Key Implementation Patterns

### Navigation Hook Pattern
```typescript
// Use the simplified navigation hook
import { useSimpleNavigation } from '@/hooks/use-simple-navigation';

function Component() {
  const { navigateToStep, navigateBack } = useSimpleNavigation();
  // Use for step navigation
}
```

### Form Validation Pattern
```typescript
// All forms use Zod schemas with React Hook Form
const schema = z.object({
  field: z.string().min(1, "Required"),
  // Federal compliance validations
});
```

### API Request Pattern
```typescript
// Consistent error handling and auth headers
const response = await axios.post('/api/endpoint', data, {
  headers: { Authorization: `Bearer ${token}` }
});
```

## Common Issues & Solutions

### Port Conflicts
- Backend runs on port 8000
- Frontend runs on port 3000
- Kill existing processes: `lsof -ti:8000 | xargs kill -9`

### Component Props Issues
- All step components use direct props, not useOutletContext
- Follow the StepProps interface pattern

### Navigation Issues
- Use the simplified navigation hook (use-simple-navigation.ts)
- Avoid complex routing libraries for step navigation

### Testing Failed Imports
- Ensure all test files import from correct paths
- Use `@/` alias for src directory imports

## Security Considerations

- All sensitive data encrypted in transit
- Authentication tokens stored securely
- File uploads validated for type and size
- SQL injection prevented via Pydantic models
- XSS protection through React's built-in escaping
- CSRF protection via token-based auth


## Testing Individual Components

### Running a Single Test
```bash
# Backend
cd hotel-onboarding-backend
poetry run pytest tests/test_specific_file.py::test_function_name -v

# Frontend
cd hotel-onboarding-frontend
npm test -- --testNamePattern="specific test name"
```

### Utility Scripts
- `start_backend.sh`: Starts backend server in background
- `stop_servers.sh`: Stops all running servers
- `restart_servers.sh`: Restarts both frontend and backend

## Key Backend Services

### OnboardingOrchestrator (`app/services/onboarding_orchestrator.py`)
Manages the complete onboarding workflow state machine, handling transitions between employee, manager, and HR phases.

### FormUpdateService (`app/services/form_update_service.py`)
Enables individual form updates outside the full onboarding flow, critical for the modular architecture.

### Email Service (`app/email_service.py`)
Handles all notification emails including onboarding invitations, approval notifications, and form update requests.

### PDF Forms (`app/pdf_forms.py`)
Generates official government-compliant PDFs for I-9, W-4, and other federal forms with exact field mapping.

## Common Gotchas

1. **Component Props**: All step components must use direct props, not `useOutletContext()`
2. **File Paths**: Always use absolute paths when working with file operations
3. **Testing**: The `/test-steps` route is crucial for testing components in isolation
4. **Enhanced vs Basic**: Use `main_enhanced.py` for full onboarding features, `main.py` for basic HR functionality
5. **Form IDs**: Each form component expects consistent IDs for progress tracking (e.g., 'welcome', 'personal-info', 'i9-section1')
