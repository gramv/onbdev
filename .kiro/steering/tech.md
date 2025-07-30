# Technology Stack

## Backend (FastAPI + Python)

- **Framework**: FastAPI with Python 3.12+
- **Package Manager**: Poetry
- **Data Storage**: In-memory dictionaries (development phase)
- **Authentication**: Simple token-based authentication
- **File Processing**: 
  - OCR: Groq AI for document processing (when needed)
  - PDF: PyPDF2, PyMuPDF, pdf2image
  - Images: Pillow
- **PDF Generation**: ReportLab
- **Environment**: python-dotenv for configuration

## Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router DOM v7
- **UI Components**: Radix UI primitives with custom components
- **Styling**: Tailwind CSS with tailwindcss-animate
- **Forms**: React Hook Form with Zod validation
- **HTTP Client**: Axios
- **State Management**: React Context (AuthContext)
- **Testing**: Jest with React Testing Library

## Development Tools

- **Linting**: ESLint with TypeScript support
- **Code Quality**: TypeScript strict mode
- **Package Management**: npm (frontend), Poetry (backend)

## Common Commands

### Backend
```bash
cd hotel-onboarding-backend
poetry install          # Install dependencies
poetry run python -m app.main  # Run development server
poetry add <package>     # Add new dependency
```

### Frontend
```bash
cd hotel-onboarding-frontend
npm install             # Install dependencies
npm run dev            # Start development server
npm run build          # Build for production
npm run test           # Run tests
npm run lint           # Run linter
```

## Environment Configuration

Backend uses `.env` file for:
- Groq API key for OCR processing
- Application secrets
- File storage configuration
- Supabase database credentials (for production)
- Email service configuration (SMTP/SendGrid)

## Modular Employee Onboarding Technical Stack

### Enhanced Backend Architecture

#### Core Services
- **OnboardingOrchestrator**: Workflow state management and transitions
- **FormUpdateService**: Individual form updates with secure token generation
- **I9FormService**: Official USCIS I-9 form integration and PDF generation
- **W4FormService**: Official IRS W-4 form integration and tax calculations
- **NotificationService**: Multi-channel notification system (email, SMS)
- **ComplianceService**: Federal requirement validation and audit trails
- **DocumentService**: Secure document storage and retrieval
- **SignatureService**: ESIGN Act compliant digital signature capture

#### Data Storage
- **Development**: Enhanced in-memory dictionaries with persistence simulation
- **Production**: Supabase PostgreSQL with Row Level Security (RLS)
- **Document Storage**: Encrypted file storage with access controls
- **Audit Trails**: Immutable audit log storage with tamper protection

#### PDF Generation and Processing
- **ReportLab**: Official government form PDF generation
- **PyPDF2/PyMuPDF**: PDF manipulation and field mapping
- **pdf2image**: PDF preview generation
- **Pillow**: Image processing for document verification photos

#### Authentication and Security
- **JWT Tokens**: Short-lived access tokens with refresh mechanism
- **Role-Based Access**: Employee/Manager/HR permission separation
- **Form Update Tokens**: Time-limited, single-use tokens for individual updates
- **Encryption**: AES-256 encryption for PII data at rest

### Enhanced Frontend Architecture

#### Component Structure
```
src/
├── components/
│   ├── onboarding/           # Modular onboarding components
│   │   ├── forms/           # Individual form components
│   │   ├── workflow/        # Workflow management components
│   │   └── compliance/      # Compliance validation components
│   ├── manager/             # Manager-specific interfaces
│   │   ├── review/          # Employee review components
│   │   └── approval/        # Approval workflow components
│   ├── hr/                  # HR-specific interfaces
│   │   ├── dashboard/       # HR dashboard components
│   │   └── compliance/      # Compliance management components
│   └── shared/              # Shared UI components
├── services/                # API service layers
├── hooks/                   # Custom React hooks for onboarding
├── contexts/                # State management contexts
└── utils/                   # Utility functions and helpers
```

#### Key Frontend Technologies
- **React Hook Form**: Advanced form handling with validation
- **Zod**: Runtime type validation and schema definition
- **React Query**: Server state management and caching
- **Framer Motion**: Smooth animations and transitions
- **React Signature Canvas**: Digital signature capture
- **React PDF**: PDF document preview and display

#### State Management
- **OnboardingContext**: Global onboarding state management
- **FormUpdateContext**: Individual form update state
- **ComplianceContext**: Compliance validation state
- **NotificationContext**: Real-time notification management

### Database Schema (Supabase)

#### Core Tables
```sql
-- Onboarding sessions with workflow tracking
onboarding_sessions (
  id, application_id, employee_id, manager_id, property_id,
  status, current_step, phase, started_at, completed_at,
  form_completion_data, audit_trail
)

-- Individual form update sessions
form_update_sessions (
  id, employee_id, form_type, update_token, requested_by,
  current_data, updated_data, expires_at, completed_at
)

-- Comprehensive employee data
employees (
  id, application_id, property_id, personal_info,
  i9_data, w4_data, health_insurance, direct_deposit,
  policy_acknowledgments, compliance_status
)

-- Document storage metadata
documents (
  id, employee_id, document_type, file_path, 
  encryption_key, uploaded_at, retention_expires_at
)

-- Audit trail for compliance
audit_trail (
  id, entity_type, entity_id, action, user_id,
  changes, timestamp, ip_address, user_agent
)
```

#### Row Level Security (RLS)
- Employees can only access their own data
- Managers can access employees from their assigned property
- HR has system-wide access with audit logging
- Form update tokens provide temporary, scoped access

### API Endpoints

#### Onboarding Workflow
```python
# Core onboarding endpoints
POST /api/onboarding/initiate/{application_id}
GET /api/onboarding/session/{session_id}
POST /api/onboarding/complete-step/{session_id}
POST /api/onboarding/transition/{session_id}/{phase}

# Form update endpoints
POST /api/forms/generate-update-link
GET /api/forms/update/{token}
POST /api/forms/submit-update/{token}
GET /api/forms/update-status/{session_id}
```

#### Manager Endpoints
```python
# Manager review and approval
GET /api/manager/pending-onboarding
GET /api/manager/review/{session_id}
POST /api/manager/complete-i9-section2/{session_id}
POST /api/manager/approve/{session_id}
```

#### HR Endpoints
```python
# HR dashboard and approval
GET /api/hr/pending-approvals
GET /api/hr/compliance-review/{session_id}
POST /api/hr/approve-onboarding/{session_id}
POST /api/hr/request-correction/{session_id}
GET /api/hr/generate-certificate/{session_id}
```

### Development Workflow

#### Backend Development
```bash
cd hotel-onboarding-backend
poetry install
poetry run python -m app.main_enhanced  # Enhanced onboarding server
poetry run pytest tests/                # Run test suite
```

#### Frontend Development
```bash
cd hotel-onboarding-frontend
npm install
npm run dev                             # Development server
npm run test                           # Jest test suite
npm run test:e2e                       # End-to-end tests
```

#### Database Management
```bash
# Supabase schema management
poetry run python apply_enhanced_schema.py
poetry run python populate_sample_data.py
poetry run python test_enhanced_database.py
```

### Testing Strategy

#### Unit Testing
- Form component validation testing
- Service layer business logic testing
- Compliance validation testing
- PDF generation accuracy testing

#### Integration Testing
- Complete workflow testing (employee → manager → HR)
- Individual form update workflow testing
- Authentication and authorization testing
- Database transaction testing

#### End-to-End Testing
- Full user journey testing with Playwright
- Cross-browser compatibility testing
- Mobile responsiveness testing
- Performance and load testing

#### Compliance Testing
- I-9 form accuracy against USCIS templates
- W-4 form accuracy against IRS templates
- Digital signature ESIGN Act compliance
- FCRA background check compliance
- Document retention policy validation

### Security Implementation

#### Data Encryption
- AES-256 encryption for PII at rest
- TLS 1.3 for data in transit
- Key rotation and management
- Secure key storage with environment variables

#### Authentication Security
- JWT with short expiration and refresh tokens
- Rate limiting on authentication endpoints
- Account lockout after failed attempts
- Multi-factor authentication support

#### Audit and Compliance
- Comprehensive audit logging for all actions
- Tamper-proof audit trail storage
- Compliance report generation
- Automated compliance validation

### Performance Optimization

#### Frontend Performance
- Code splitting for onboarding modules
- Lazy loading of form components
- Image optimization for document uploads
- Service worker for offline capability

#### Backend Performance
- Database query optimization with indexes
- Caching for frequently accessed data
- Async processing for document generation
- Background job processing for notifications

#### Monitoring and Alerting
- Application performance monitoring (APM)
- Error tracking and alerting
- Compliance violation alerts
- System health monitoring