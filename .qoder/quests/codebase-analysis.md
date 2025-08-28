# Hotel Employee Onboarding System - Codebase Analysis

## Overview

The Hotel Employee Onboarding System is a comprehensive full-stack web application designed specifically for the hospitality industry to digitize and streamline the employee onboarding process with federal compliance for I-9 and W-4 forms. The system follows a three-phase workflow and emphasizes property-based data isolation and role-based access control.

### Repository Type
**Full-Stack Application** - A complex hospitality management platform with distinct frontend and backend services.

## Architecture

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[React/TypeScript Frontend]
        PWA[Progressive Web App]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Python Backend]
        WS[WebSocket Manager]
        OCR[Google OCR Service]
        PDF[PDF Generation Service]
    end
    
    subgraph "Data Layer"
        DB[(Supabase PostgreSQL)]
        STORAGE[Document Storage]
        CACHE[Redis Cache]
    end
    
    subgraph "External Services"
        EMAIL[Email Service]
        GROQ[Groq API]
        GDOC[Google Document AI]
    end
    
    FE --> API
    FE --> WS
    API --> DB
    API --> STORAGE
    API --> EMAIL
    OCR --> GDOC
    PDF --> GROQ
    WS --> DB
```

### Three-Phase Workflow Architecture

```mermaid
sequenceDiagram
    participant A as Applicant
    participant M as Manager
    participant H as HR
    participant S as System
    
    Note over A,S: Phase 1: Employee Onboarding
    A->>S: Job Application via QR Code
    M->>S: Review & Approve Application
    S->>A: Generate Onboarding Token (7-day JWT)
    A->>S: Complete Federal Forms (I-9, W-4)
    A->>S: Upload Documents & Digital Signatures
    
    Note over A,S: Phase 2: Manager Review
    S->>M: Notify Employee Completion
    M->>S: Review Submissions
    M->>S: Complete I-9 Section 2
    M->>S: Final Approval/Rejection
    
    Note over A,S: Phase 3: HR Oversight
    S->>H: Final Compliance Review
    H->>S: System Integration
    H->>S: Analytics & Reporting
```

## Technology Stack & Dependencies

### Frontend Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 6.0.1
- **Styling**: Tailwind CSS 3.4.16
- **UI Components**: Radix UI + shadcn/ui
- **State Management**: React Context API
- **Form Handling**: React Hook Form + Zod validation
- **HTTP Client**: Axios 1.10.0
- **PDF Generation**: pdf-lib 1.17.1
- **Charts**: Chart.js 4.5.0 + Recharts 2.15.4
- **Internationalization**: i18next 25.3.2
- **Router**: React Router 7.7.0

### Backend Stack
- **Framework**: FastAPI 0.116.1
- **Language**: Python 3.12+
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT (PyJWT 2.10.1)
- **Password Hashing**: bcrypt 4.3.0
- **PDF Processing**: PyMuPDF 1.26.3, ReportLab 4.4.3
- **Document Processing**: Google Cloud Document AI 2.29.0
- **AI Services**: Groq 0.30.0
- **Email**: aiosmtplib 4.0.1
- **WebSockets**: websockets 15.0.1
- **Testing**: pytest 8.4.1

### Infrastructure
- **Database**: Supabase PostgreSQL with Row Level Security (RLS)
- **Deployment**: Vercel (Frontend), Heroku (Backend)
- **Document Storage**: Supabase Storage
- **Real-time Updates**: WebSocket connections
- **API Documentation**: FastAPI automatic OpenAPI

## Component Architecture

### Frontend Component Hierarchy

```mermaid
graph TD
    APP[App.tsx - Main Router]
    
    subgraph "Authentication Flow"
        LOGIN[LoginPage]
        PROTECTED[ProtectedRoute]
    end
    
    subgraph "Dashboard Layouts"
        HRLAYOUT[HRDashboardLayout]
        MGRLAYOUT[ManagerDashboardLayout]
    end
    
    subgraph "Onboarding Components"
        PORTAL[OnboardingFlowPortal]
        I9FORM[I9Section1Form]
        W4FORM[W4Form]
        DOCUPLOAD[DocumentUpload]
        SIGNATURE[DigitalSignatureCapture]
    end
    
    subgraph "Dashboard Components"
        APPS[ApplicationsTab]
        EMPLOYEES[EmployeesTab]
        ANALYTICS[AnalyticsTab]
        NOTIFICATIONS[NotificationCenter]
    end
    
    APP --> LOGIN
    APP --> PROTECTED
    PROTECTED --> HRLAYOUT
    PROTECTED --> MGRLAYOUT
    HRLAYOUT --> APPS
    HRLAYOUT --> EMPLOYEES
    MGRLAYOUT --> ANALYTICS
    PORTAL --> I9FORM
    PORTAL --> W4FORM
    PORTAL --> DOCUPLOAD
    PORTAL --> SIGNATURE
```

### Backend Service Architecture

```mermaid
graph TD
    MAIN[main_enhanced.py - FastAPI App]
    
    subgraph "Authentication Layer"
        AUTH[auth.py - JWT Manager]
        PROP[property_access_control.py]
        RBAC[Role-Based Access Control]
    end
    
    subgraph "Core Services"
        SUPABASE[supabase_service_enhanced.py]
        EMAIL[email_service.py]
        PDF[pdf_forms.py]
        OCR[google_ocr_service.py]
    end
    
    subgraph "Business Logic"
        ORCHESTRATOR[OnboardingOrchestrator]
        FORM[FormUpdateService]
        BULK[BulkOperationService]
        ANALYTICS[AnalyticsService]
    end
    
    subgraph "Real-time Features"
        WS[websocket_manager.py]
        NOTIFICATIONS[notification_service.py]
    end
    
    MAIN --> AUTH
    MAIN --> SUPABASE
    MAIN --> EMAIL
    AUTH --> PROP
    AUTH --> RBAC
    SUPABASE --> ORCHESTRATOR
    SUPABASE --> FORM
    WS --> NOTIFICATIONS
```

## Data Models & ORM Mapping

### Core Data Models

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email
        string role
        string first_name
        string last_name
        uuid property_id FK
        boolean is_active
        timestamp created_at
    }
    
    PROPERTIES {
        uuid id PK
        string name
        string address
        string city
        string state
        string zip_code
        string phone
        string qr_code_url
        boolean is_active
        timestamp created_at
    }
    
    JOB_APPLICATIONS {
        uuid id PK
        uuid property_id FK
        string department
        string position
        jsonb applicant_data
        string status
        timestamp applied_at
        uuid reviewed_by FK
        timestamp reviewed_at
    }
    
    EMPLOYEES {
        uuid id PK
        uuid user_id FK
        uuid application_id FK
        uuid property_id FK
        uuid manager_id FK
        string department
        string position
        date hire_date
        jsonb personal_info
        string onboarding_status
        timestamp created_at
    }
    
    ONBOARDING_SESSIONS {
        uuid id PK
        uuid employee_id FK
        string token
        string status
        string current_step
        jsonb form_data
        float progress_percentage
        timestamp expires_at
        timestamp created_at
    }
    
    PROPERTY_MANAGERS {
        uuid property_id FK
        uuid manager_id FK
        timestamp assigned_at
    }
    
    USERS ||--o{ EMPLOYEES : manages
    PROPERTIES ||--o{ JOB_APPLICATIONS : receives
    PROPERTIES ||--o{ EMPLOYEES : employs
    PROPERTIES ||--o{ PROPERTY_MANAGERS : has
    USERS ||--o{ PROPERTY_MANAGERS : assigned_to
    JOB_APPLICATIONS ||--o| EMPLOYEES : creates
    EMPLOYEES ||--|| ONBOARDING_SESSIONS : has
```

### Federal Compliance Models

```mermaid
erDiagram
    I9_FORMS {
        uuid id PK
        uuid employee_id FK
        jsonb section1_data
        jsonb section2_data
        string employee_signature
        string manager_signature
        timestamp employee_signed_at
        timestamp manager_signed_at
        string status
    }
    
    W4_FORMS {
        uuid id PK
        uuid employee_id FK
        string first_name
        string last_name
        string address
        string ssn
        string filing_status
        jsonb tax_data
        string signature
        timestamp signed_at
    }
    
    DOCUMENTS {
        uuid id PK
        uuid employee_id FK
        string document_type
        string file_path
        string status
        jsonb ocr_data
        timestamp uploaded_at
    }
    
    EMPLOYEES ||--|| I9_FORMS : completes
    EMPLOYEES ||--|| W4_FORMS : completes
    EMPLOYEES ||--o{ DOCUMENTS : uploads
```

## Business Logic Layer

### Onboarding Flow Architecture

The system implements a sophisticated onboarding flow with federal compliance requirements:

```mermaid
stateDiagram-v2
    [*] --> NotStarted
    NotStarted --> InProgress : Start Onboarding
    
    state InProgress {
        [*] --> PersonalInfo
        PersonalInfo --> I9Section1
        I9Section1 --> DocumentUpload
        DocumentUpload --> W4Form
        W4Form --> DirectDeposit
        DirectDeposit --> EmergencyContacts
        EmergencyContacts --> HealthInsurance
        HealthInsurance --> CompanyPolicies
        CompanyPolicies --> TraffickingAwareness
        TraffickingAwareness --> EmployeeSignature
        EmployeeSignature --> [*]
    }
    
    InProgress --> EmployeeCompleted : All Steps Done
    EmployeeCompleted --> ManagerReview : Manager Starts Review
    
    state ManagerReview {
        [*] --> ReviewSubmissions
        ReviewSubmissions --> I9Section2
        I9Section2 --> ManagerSignature
        ManagerSignature --> [*]
    }
    
    ManagerReview --> Approved : Manager Approves
    ManagerReview --> Rejected : Manager Rejects
    Approved --> [*]
    Rejected --> [*]
```

### Property-Based Access Control

The system enforces strict property isolation to ensure data security:

```mermaid
graph TD
    REQUEST[Incoming Request]
    
    subgraph "Authentication Layer"
        JWT[JWT Token Validation]
        ROLE[Role Extraction]
        PROPERTY[Property ID Extraction]
    end
    
    subgraph "Authorization Layer"
        CHECK{Role Check}
        HR_ACCESS[HR Full Access]
        MGR_ACCESS[Manager Property Access]
        DENY[Access Denied]
    end
    
    subgraph "Data Layer"
        FILTER[Property-Based Filtering]
        QUERY[Database Query]
        RESPONSE[Filtered Response]
    end
    
    REQUEST --> JWT
    JWT --> ROLE
    ROLE --> PROPERTY
    PROPERTY --> CHECK
    
    CHECK -->|HR Role| HR_ACCESS
    CHECK -->|Manager Role| MGR_ACCESS
    CHECK -->|Invalid| DENY
    
    HR_ACCESS --> QUERY
    MGR_ACCESS --> FILTER
    FILTER --> QUERY
    QUERY --> RESPONSE
```

### Federal Compliance Engine

```mermaid
graph TD
    FORM[Form Submission]
    
    subgraph "Validation Layer"
        FIELD[Field Validation]
        BUSINESS[Business Rules]
        FEDERAL[Federal Requirements]
    end
    
    subgraph "Compliance Engine"
        I9VAL[I-9 Validation]
        W4VAL[W-4 Validation]
        DOCVAL[Document Validation]
    end
    
    subgraph "Audit & Storage"
        AUDIT[Audit Trail]
        STORAGE[Secure Storage]
        NOTIFY[Compliance Notifications]
    end
    
    FORM --> FIELD
    FIELD --> BUSINESS
    BUSINESS --> FEDERAL
    
    FEDERAL --> I9VAL
    FEDERAL --> W4VAL
    FEDERAL --> DOCVAL
    
    I9VAL --> AUDIT
    W4VAL --> AUDIT
    DOCVAL --> AUDIT
    
    AUDIT --> STORAGE
    STORAGE --> NOTIFY
```

## API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | Manager/HR login with JWT token generation | No |
| POST | `/auth/refresh` | Refresh JWT token | Yes |
| GET | `/auth/me` | Get current user information | Yes |

### Property Management (HR Only)

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| GET | `/api/properties` | List all properties | HR |
| POST | `/api/properties` | Create new property | HR |
| PUT | `/api/properties/{id}` | Update property | HR |
| DELETE | `/api/properties/{id}` | Soft delete property | HR |

### Manager Endpoints

| Method | Endpoint | Description | Access Control |
|--------|----------|-------------|----------------|
| GET | `/manager/applications` | Get applications for manager's property | Property-based |
| POST | `/manager/applications/{id}/approve` | Approve job application | Property-based |
| GET | `/manager/employees` | Get employees for manager's property | Property-based |
| POST | `/manager/create-onboarding-token` | Generate employee onboarding token | Property-based |

### Onboarding Endpoints

| Method | Endpoint | Description | Auth Type |
|--------|----------|-------------|-----------|
| GET | `/onboarding/{employee_id}/progress` | Get onboarding progress | Onboarding Token |
| POST | `/onboarding/{employee_id}/save-step` | Save step progress | Onboarding Token |
| POST | `/onboarding/{employee_id}/complete-step` | Mark step complete | Onboarding Token |

### Document Processing

| Method | Endpoint | Description | Features |
|--------|----------|-------------|----------|
| POST | `/api/forms/i9/generate` | Generate I-9 PDF | OCR Integration |
| POST | `/api/forms/w4/generate` | Generate W-4 PDF | Federal Compliance |
| POST | `/api/documents/upload` | Upload verification documents | Google Document AI |
| POST | `/api/documents/ocr` | Process document OCR | Groq API |

## Real-Time Features & WebSocket Integration

### WebSocket Architecture

```mermaid
graph TD
    CLIENT[Frontend Client]
    
    subgraph "WebSocket Layer"
        WS_MGR[WebSocket Manager]
        AUTH_WS[WebSocket Authentication]
        ROOMS[Property-Based Rooms]
    end
    
    subgraph "Event System"
        EVENTS[Event Dispatcher]
        FILTERS[Property Filters]
        BROADCAST[Selective Broadcasting]
    end
    
    subgraph "Data Updates"
        APP_EVENTS[Application Events]
        PROGRESS[Progress Updates]
        NOTIFICATIONS[Real-time Notifications]
    end
    
    CLIENT --> WS_MGR
    WS_MGR --> AUTH_WS
    AUTH_WS --> ROOMS
    
    ROOMS --> EVENTS
    EVENTS --> FILTERS
    FILTERS --> BROADCAST
    
    BROADCAST --> APP_EVENTS
    BROADCAST --> PROGRESS
    BROADCAST --> NOTIFICATIONS
```

### Real-Time Event Types

1. **Application Events**
   - New application submissions
   - Status changes (pending → approved → onboarding)
   - Manager review completions

2. **Onboarding Progress**
   - Step completions
   - Form submissions
   - Document uploads
   - Signature captures

3. **System Notifications**
   - Compliance deadline reminders
   - Manager task assignments
   - HR oversight alerts

## Security & Compliance Architecture

### Multi-Layer Security Model

```mermaid
graph TD
    REQUEST[HTTP Request]
    
    subgraph "Layer 1: Network Security"
        CORS[CORS Policy]
        HTTPS[HTTPS Enforcement]
        RATE[Rate Limiting]
    end
    
    subgraph "Layer 2: Authentication"
        JWT_AUTH[JWT Validation]
        TOKEN[Token Expiration]
        REFRESH[Refresh Logic]
    end
    
    subgraph "Layer 3: Authorization"
        RBAC[Role-Based Access]
        PROPERTY_ACL[Property ACL]
        ENDPOINT[Endpoint Guards]
    end
    
    subgraph "Layer 4: Data Security"
        RLS[Row Level Security]
        ENCRYPTION[Data Encryption]
        AUDIT[Audit Logging]
    end
    
    REQUEST --> CORS
    CORS --> HTTPS
    HTTPS --> RATE
    RATE --> JWT_AUTH
    JWT_AUTH --> TOKEN
    TOKEN --> REFRESH
    REFRESH --> RBAC
    RBAC --> PROPERTY_ACL
    PROPERTY_ACL --> ENDPOINT
    ENDPOINT --> RLS
    RLS --> ENCRYPTION
    ENCRYPTION --> AUDIT
```

### Federal Compliance Requirements

1. **I-9 Employment Eligibility Verification**
   - Section 1: Employee completion within first day
   - Section 2: Manager verification within 3 business days
   - Document verification with OCR validation
   - Digital signature with legal attestation

2. **W-4 Tax Withholding**
   - 2025 IRS-compliant form structure
   - Tax calculation validation
   - Digital signature requirements
   - Proper field mapping to official templates

3. **Document Retention**
   - 3 years after hire or 1 year after termination
   - Secure encrypted storage
   - Audit trail for all access
   - Compliance reporting capabilities

## Performance & Scalability

### System Capacity Design

- **HR Users**: 15-20 with full system access
- **Managers**: 200+ with property-specific access
- **Employees**: Unlimited (stateless onboarding sessions)
- **Properties**: Multi-tenant architecture

### Optimization Strategies

1. **Database Performance**
   - Strategic indexing on frequently queried fields
   - Connection pooling with asyncpg
   - Property-based data partitioning
   - Optimized RLS policies

2. **API Performance**
   - Response caching with intelligent invalidation
   - Pagination for large datasets
   - Optimistic updates for real-time features
   - Background job processing

3. **Frontend Performance**
   - Code splitting and lazy loading
   - Component-level caching
   - Progressive Web App capabilities
   - Mobile-first responsive design

## Testing Strategy

### Backend Testing
- **Unit Tests**: Individual service and utility functions
- **Integration Tests**: Database operations and API endpoints
- **Property Access Tests**: Comprehensive isolation verification
- **Federal Compliance Tests**: Form validation and PDF generation
- **WebSocket Tests**: Real-time functionality validation

### Frontend Testing
- **Component Tests**: Individual React component functionality
- **Integration Tests**: Form flows and API interactions
- **E2E Tests**: Complete onboarding workflows
- **Accessibility Tests**: WCAG compliance validation
- **Mobile Tests**: Cross-device compatibility

### Testing Infrastructure
- **Backend**: pytest with async support
- **Frontend**: Jest + React Testing Library
- **E2E**: Playwright for comprehensive workflow testing
- **Performance**: Load testing with simulated user scenarios

## Deployment & Infrastructure

### Development Environment
- **Frontend**: Vite dev server on localhost:3000
- **Backend**: FastAPI with uvicorn on localhost:8000
- **Database**: Supabase test environment
- **Hot Module Replacement**: Real-time development updates

### Production Environment
- **Frontend**: Vercel deployment with CDN
- **Backend**: Heroku with auto-scaling
- **Database**: Supabase production with RLS enabled
- **Monitoring**: Performance tracking and error reporting

### Environment Configuration
- **Development**: Local environment variables
- **Staging**: Vercel preview deployments
- **Production**: Secure environment variable management
- **Backup**: Automated database backups and recovery procedures