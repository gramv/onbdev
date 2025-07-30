---
inclusion: always
---

# HR Manager Dashboard System

A comprehensive administrative platform for hotel properties that manages job applications, candidates, and property operations through role-based dashboards.

## Product Principles

- **Role-based access control**: HR has system-wide access, Managers have property-specific access
- **Property-centric workflow**: All operations are organized around hotel properties
- **Application lifecycle management**: Track candidates from application to hiring decision
- **QR code integration**: Properties generate QR codes for streamlined job applications
- **Professional hospitality focus**: UI/UX tailored for hotel industry workflows

## User Roles & Permissions

### HR Administrator (`role: 'hr'`)
- Full system access across all properties
- Manage properties, managers, and system settings
- View analytics and reports for all properties
- Access all applications regardless of property

### Property Manager (`role: 'manager'`)
- Property-specific access only (filtered by `property_id`)
- Review and manage applications for assigned property
- Cannot create properties or assign other managers
- Limited to property-specific analytics

## Core Workflows

### 1. Property Setup (HR-driven)
```
HR creates property → assigns manager → generates QR code → property ready for applications
```

### 2. Application Processing (Manager-driven)
```
Candidate applies via QR → manager reviews → approve/reject → status tracking
```

### 3. Talent Pool Management
- Rejected applications move to talent pool
- Managers can review talent pool for future openings
- HR has visibility across all talent pools

## Key Business Rules

- **Property isolation**: Managers only see their assigned property data
- **Application states**: `pending` → `approved`/`rejected` → `talent_pool` (if rejected)
- **QR code uniqueness**: Each property has a unique QR code for applications
- **Manager assignment**: One manager per property (can be reassigned by HR)
- **Data persistence**: All application data retained for compliance and analytics

## UI/UX Standards

- **Dashboard-centric**: Tab-based navigation for different data views
- **Responsive design**: Works on desktop and tablet devices
- **Professional styling**: Clean, corporate appearance suitable for HR workflows
- **Consistent interactions**: Standardized buttons, forms, and data tables
- **Role-appropriate branding**: Different dashboard themes for HR vs Manager roles

## Development Constraints

- **In-memory storage**: Development phase uses dictionaries, not persistent database
- **Simple authentication**: Token-based auth without complex user management
- **Property-first architecture**: All data models reference property relationships

## Modular Employee Onboarding System

### Overview
A comprehensive, modular employee onboarding system that digitizes all 28 pages of the hotel onboarding packet while maintaining exact federal compliance for I-9, W-4, and other required forms. The key innovation is the modular architecture that allows HR to send individual forms to employees for updates without requiring full re-onboarding.

### Core Principles
- **Modular Form Architecture**: Individual forms can be updated independently without full re-onboarding
- **Three-Phase Workflow**: Employee Completion → Manager Review → HR Approval
- **Federal Compliance**: Exact compliance with I-9, W-4, ESIGN Act, and FCRA requirements
- **Multi-Language Support**: English/Spanish support throughout the system
- **Audit Trail**: Comprehensive tracking of all changes and approvals

### Three-Phase Workflow

#### Phase 1: Employee Completion
- Employee receives secure onboarding link after manager approval
- Completes all required forms in logical sequence with progress tracking
- Forms include: Personal Info, I-9 Section 1, W-4, Emergency Contacts, Direct Deposit, Health Insurance, Company Policies, Human Trafficking Awareness, Weapons Policy, Background Check Authorization
- Digital signature capture for all required forms
- Auto-save functionality prevents data loss

#### Phase 2: Manager Review
- Manager receives notification when employee completes their portion
- Reviews all completed employee forms
- Completes I-9 Section 2 with document verification and photo upload
- Adds required manager signatures and attestations
- Can request corrections or approve for HR review

#### Phase 3: HR Approval
- HR receives complete onboarding package for final review
- Validates federal compliance requirements
- Can approve, request corrections, or send specific forms back for updates
- Generates completion certificates and archives all documents
- Maintains proper document retention policies

### Modular Form Update System

#### Individual Form Updates
HR can send employees secure links to update specific forms:
- **W-4 Updates**: Marriage status, dependents, tax withholding changes
- **Personal Information**: Address, phone, emergency contacts
- **Health Insurance**: Plan changes, dependent additions/removals
- **Direct Deposit**: Banking information updates
- **Emergency Contacts**: Contact information updates only

#### Update Process
1. HR generates secure, time-limited update link for specific form
2. Employee accesses form with current data pre-populated
3. Employee makes changes and provides digital signature
4. System maintains audit trail of all changes
5. Notifications sent to HR and relevant parties

### Federal Compliance Requirements

#### I-9 Form Compliance
- Uses official USCIS I-9 template with exact field mapping
- Employee completes Section 1 with citizenship verification
- Manager completes Section 2 with document verification
- Photo upload for document verification
- Generated PDFs match official government format

#### W-4 Form Compliance
- Uses official IRS W-4 template with exact field mapping
- Real-time tax calculation preview
- Multi-job worksheet integration
- Dependent information validation
- Generated PDFs match official government format

#### Digital Signature Compliance
- ESIGN Act compliant digital signatures
- Proper consent and disclosure processes
- Tamper-proof signature embedding
- Legal metadata capture (IP, timestamp, device info)

#### Background Check Compliance
- FCRA-compliant disclosure and consent
- State-specific authorization requirements
- Fair Credit Reporting Act compliance statements
- Conditional employment handling based on results

### Technical Architecture

#### Backend Services
- **OnboardingOrchestrator**: Manages workflow state and transitions
- **FormUpdateService**: Handles individual form updates with secure tokens
- **I9FormService**: Official I-9 form integration and PDF generation
- **W4FormService**: Official W-4 form integration and tax calculations
- **NotificationService**: Email notifications for all workflow stages
- **ComplianceService**: Federal requirement validation and audit trails

#### Frontend Components
- **Modular Form System**: Reusable form components for full onboarding and updates
- **Manager Dashboard**: Review interface for pending employee onboarding
- **HR Dashboard**: Comprehensive approval interface with compliance checklists
- **Employee Portal**: User-friendly onboarding experience with progress tracking
- **Form Update Portal**: Standalone interface for individual form updates

#### Data Models
- **OnboardingSession**: Tracks complete workflow state and progress
- **FormUpdateSession**: Manages individual form update sessions
- **Employee**: Comprehensive employee data with all form information
- **ComplianceAuditTrail**: Detailed tracking of all compliance-related actions

### User Experience Standards

#### Employee Experience
- Clean, intuitive interface with clear progress indicators
- Multi-language support (English/Spanish)
- Mobile-responsive design for accessibility
- Auto-save prevents data loss
- Clear validation messages and help text

#### Manager Experience
- Dashboard showing pending onboarding reviews
- Clear action items with priority indicators
- Document verification workflow with photo upload
- Approval/rejection workflow with comment capability

#### HR Experience
- Comprehensive package review with compliance checklists
- Individual form update management
- Audit trail visibility for all actions
- Document generation and archival tools
- Compliance reporting and validation

### Security and Privacy

#### Data Protection
- All PII encrypted at rest and in transit
- Role-based access controls (employee/manager/HR)
- Secure token-based authentication
- Comprehensive audit logging

#### Compliance Security
- Document retention automation per federal requirements
- Tamper-proof audit trails
- Secure document storage with access controls
- Automated compliance validation

### Integration Points

#### With Existing HR System
- Seamless transition from job application approval to onboarding
- Employee data synchronization
- Manager assignment and property association
- HR dashboard integration

#### With Payroll Systems
- W-4 data export for tax withholding
- Direct deposit information transfer
- Health insurance enrollment data
- Background check status integration

### Success Metrics

#### Operational Efficiency
- Reduced onboarding time from days to hours
- Elimination of paper forms and manual processing
- Automated compliance validation
- Streamlined manager and HR workflows

#### Compliance Assurance
- 100% federal compliance for all government forms
- Complete audit trails for all actions
- Automated document retention
- Reduced compliance risk and penalties

#### User Satisfaction
- Intuitive user experience for all stakeholders
- Multi-language accessibility
- Mobile-responsive design
- Clear progress tracking and notifications