# Product Requirements Document (PRD)
## Hotel Employee Onboarding System - HR & Manager Module Redesign

### Document Version
- **Version**: 1.0
- **Date**: January 2025
- **Status**: Planning Phase
- **Author**: System Architecture Team

---

## 1. Executive Summary

### 1.1 Purpose
This document outlines the complete redesign of the HR Admin and Manager modules for the Hotel Employee Onboarding System. The redesign aims to eliminate duplicate code, establish clear role boundaries, and introduce a modular form distribution system for ongoing employee management.

### 1.2 Scope
- Complete removal and replacement of existing HR/Manager functionality
- Preservation of working Job Application and Employee Onboarding flows
- Introduction of modular form distribution system
- Implementation of proper authentication and authorization

### 1.3 Goals
1. **Eliminate Redundancy**: Remove 50+ duplicate endpoints and 7 duplicate dashboard components
2. **Clear Role Separation**: Distinct functionality for HR, Managers, and Employees
3. **Modular Architecture**: Enable sending individual forms to employees as needed
4. **Federal Compliance**: Maintain I-9, W-4, and other federal requirements
5. **Property Isolation**: Ensure managers only access their assigned properties

---

## 2. User Personas

### 2.1 HR Administrator
**Profile**: Corporate HR staff managing multiple hotel properties
- **Access Level**: System-wide
- **Primary Tasks**:
  - Manage hotel properties
  - Create and assign managers
  - Send forms/modules to employees
  - Monitor compliance deadlines
  - Generate reports
- **Pain Points**:
  - Managing multiple properties
  - Tracking compliance across locations
  - Coordinating with property managers

### 2.2 Property Manager
**Profile**: On-site manager responsible for hiring and onboarding
- **Access Level**: Property-specific
- **Primary Tasks**:
  - Review job applications
  - Approve new hires
  - Complete I-9 Section 2
  - Track onboarding progress
- **Pain Points**:
  - Federal compliance deadlines
  - Managing multiple simultaneous onboardings
  - Document verification

### 2.3 Employee
**Profile**: New or existing hotel employee
- **Access Level**: Token-based temporary access
- **Primary Tasks**:
  - Complete onboarding forms
  - Update tax/banking information
  - Complete required training
- **Pain Points**:
  - Complex forms
  - Limited time to complete
  - Language barriers

---

## 3. Core Features

### 3.1 HR Admin System

#### 3.1.1 Initial Setup
- **Secret Key Authentication**: One-time setup using environment variable SECRET_KEY
- **First HR Creation**: Create initial super admin account
- **System Configuration**: Set default values and preferences

#### 3.1.2 Property Management
- **Create Property**: Add new hotel locations with full details
- **Update Property**: Modify property information
- **Delete Property**: Soft delete with data retention
- **Property Dashboard**: View property-specific metrics

#### 3.1.3 Manager Management
- **Create Manager Account**: Email, temporary password, role assignment
- **Assign to Property**: Link managers to one or more properties
- **Revoke Access**: Remove property access or deactivate account
- **Performance Metrics**: View manager activity and metrics

#### 3.1.4 Module Distribution System
**Purpose**: Send specific forms to employees without full onboarding

**Module Types**:
1. **W-4 Tax Update** 
   - Annual updates
   - Life event changes
   - State tax forms

2. **I-9 Reverification**
   - Work authorization expiry
   - Document updates
   - Section 3 completion

3. **Direct Deposit**
   - Bank account changes
   - Payment method updates

4. **Health Insurance**
   - Open enrollment
   - Life event changes
   - Beneficiary updates

5. **Human Trafficking Training**
   - Annual requirement for hospitality
   - Compliance tracking
   - Certificate generation

6. **Policy Updates**
   - Company policy changes
   - Acknowledgment requirements
   - Safety protocols

**Distribution Features**:
- Single or bulk sending
- Expiration tracking
- Reminder notifications
- Completion monitoring
- Audit trail

### 3.2 Manager System

#### 3.2.1 Dashboard
- **Application Queue**: New applications pending review
- **Onboarding Pipeline**: Active onboardings with progress
- **Compliance Alerts**: Upcoming deadlines and requirements
- **Property Statistics**: Hiring metrics and trends

#### 3.2.2 Application Management
- **Review Applications**: View candidate details and documents
- **Approve/Reject**: Make hiring decisions with comments
- **Generate Onboarding Token**: Create 7-day access token for approved candidates
- **Talent Pool**: Mark promising candidates for future openings

#### 3.2.3 Onboarding Oversight
- **Progress Tracking**: Monitor employee completion status
- **I-9 Section 2**: Complete employer verification within 3 days
- **Document Verification**: Review uploaded documents
- **Request Corrections**: Send specific forms back for updates

### 3.3 Employee Features (Existing - Preserved)

#### 3.3.1 Job Application
- Multi-step application form
- Document upload
- Digital signature
- Property-specific positions

#### 3.3.2 Onboarding Portal
- 14-step onboarding process
- Progress saving
- Multi-language support (English/Spanish)
- Mobile responsive

#### 3.3.3 Module Updates (New)
- Targeted form access via unique token
- Pre-populated with existing data
- Only update changed fields
- Automatic expiration

---

## 4. User Workflows

### 4.1 HR Admin Setup Flow
```
1. System admin sets SECRET_KEY in environment
2. Navigate to /setup
3. Enter secret key
4. Create first HR admin account
5. Login with new credentials
6. Begin property/manager setup
```

### 4.2 Property & Manager Setup Flow
```
1. HR creates property record
2. HR creates manager account
3. Manager receives email with credentials
4. Manager logs in and changes password
5. HR assigns manager to property
6. Manager can now review applications
```

### 4.3 Hiring Flow
```
1. Candidate submits application
2. Manager reviews in dashboard
3. Manager approves application
4. System generates onboarding token
5. Employee receives onboarding link
6. Employee completes onboarding
7. Manager completes I-9 Section 2
8. HR performs final verification
```

### 4.4 Module Update Flow
```
1. HR identifies need (e.g., annual W-4 update)
2. HR selects employees and module type
3. System generates unique tokens
4. Employees receive email with link
5. Employees complete specific form
6. System updates records
7. HR monitors completion
```

---

## 5. Functional Requirements

### 5.1 Authentication & Authorization

#### 5.1.1 User Authentication
- **FR-AUTH-001**: System shall support email/password authentication
- **FR-AUTH-002**: System shall enforce password complexity requirements
- **FR-AUTH-003**: System shall support password reset via email
- **FR-AUTH-004**: System shall implement JWT token-based sessions
- **FR-AUTH-005**: System shall support token refresh without re-login

#### 5.1.2 Role-Based Access Control
- **FR-RBAC-001**: System shall support three roles: HR, Manager, Employee
- **FR-RBAC-002**: HR shall have system-wide access
- **FR-RBAC-003**: Managers shall only access assigned properties
- **FR-RBAC-004**: Employees shall only access via temporary tokens
- **FR-RBAC-005**: System shall log all access attempts

### 5.2 Property Management

- **FR-PROP-001**: HR shall create properties with name, address, contact info
- **FR-PROP-002**: Properties shall have unique identifiers
- **FR-PROP-003**: Properties can be edited by HR only
- **FR-PROP-004**: Property deletion shall be soft-delete only
- **FR-PROP-005**: Properties shall track active employee count

### 5.3 Manager Management

- **FR-MGR-001**: HR shall create manager accounts
- **FR-MGR-002**: Managers shall be assigned to one or more properties
- **FR-MGR-003**: Manager access can be revoked without deletion
- **FR-MGR-004**: System shall track manager activity
- **FR-MGR-005**: Managers cannot access other properties' data

### 5.4 Module Distribution

- **FR-MOD-001**: HR shall send specific forms to employees
- **FR-MOD-002**: Each module shall have unique access token
- **FR-MOD-003**: Tokens shall expire after 7 days
- **FR-MOD-004**: System shall send reminder emails
- **FR-MOD-005**: Completed modules shall update employee records
- **FR-MOD-006**: System shall maintain audit trail of all updates

### 5.5 Compliance Tracking

- **FR-COMP-001**: System shall track I-9 completion deadlines
- **FR-COMP-002**: System shall alert managers of approaching deadlines
- **FR-COMP-003**: System shall prevent expired document acceptance
- **FR-COMP-004**: System shall maintain document retention schedule
- **FR-COMP-005**: System shall generate compliance reports

---

## 6. Non-Functional Requirements

### 6.1 Performance
- **NFR-PERF-001**: Page load time < 3 seconds on 3G connection
- **NFR-PERF-002**: API response time < 200ms average
- **NFR-PERF-003**: Support 500+ concurrent users
- **NFR-PERF-004**: Database queries optimized with indexes

### 6.2 Security
- **NFR-SEC-001**: All passwords hashed with bcrypt
- **NFR-SEC-002**: PII encrypted at rest and in transit
- **NFR-SEC-003**: Session timeout after 24 hours
- **NFR-SEC-004**: Rate limiting on all endpoints
- **NFR-SEC-005**: SQL injection prevention

### 6.3 Usability
- **NFR-USE-001**: Mobile responsive design
- **NFR-USE-002**: Support for English and Spanish
- **NFR-USE-003**: Accessibility compliance (WCAG 2.1 AA)
- **NFR-USE-004**: Browser compatibility (Chrome, Firefox, Safari, Edge)

### 6.4 Reliability
- **NFR-REL-001**: 99.9% uptime SLA
- **NFR-REL-002**: Automated backups every 24 hours
- **NFR-REL-003**: Disaster recovery plan
- **NFR-REL-004**: Graceful error handling

---

## 7. System Architecture

### 7.1 High-Level Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   HR Dashboard  │     │ Manager Dashboard│     │ Employee Portal │
│   (React SPA)   │     │   (React SPA)   │     │  (React SPA)   │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                                 ▼
                      ┌─────────────────────┐
                      │                     │
                      │   FastAPI Backend   │
                      │   (REST API)        │
                      │                     │
                      └──────────┬──────────┘
                                 │
                                 ▼
                      ┌─────────────────────┐
                      │                     │
                      │   Supabase         │
                      │   (PostgreSQL)      │
                      │                     │
                      └─────────────────────┘
```

### 7.2 Data Flow
1. Frontend makes authenticated API request
2. Backend validates JWT token
3. Backend checks role-based permissions
4. Backend queries database with RLS
5. Backend returns filtered data
6. Frontend renders response

---

## 8. Success Metrics

### 8.1 Technical Metrics
- **Code Reduction**: 60% fewer lines of code
- **API Endpoints**: Reduced from 50+ to ~20
- **Response Time**: < 200ms for 95% of requests
- **Test Coverage**: > 80% for critical paths

### 8.2 Business Metrics
- **Onboarding Time**: Reduce by 30%
- **Compliance Rate**: 100% I-9 deadline compliance
- **Manager Efficiency**: 50% less time on admin tasks
- **Employee Satisfaction**: > 4.5/5 rating

### 8.3 Quality Metrics
- **Bug Rate**: < 1 critical bug per month
- **Uptime**: 99.9% availability
- **Security**: Zero data breaches
- **Audit**: Pass federal compliance audit

---

## 9. Risks & Mitigation

### 9.1 Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|---------|------------|------------|
| Data migration fails | High | Low | Comprehensive backup strategy |
| Performance degradation | Medium | Medium | Load testing before deployment |
| Security vulnerability | High | Low | Security audit and penetration testing |

### 9.2 Business Risks
| Risk | Impact | Probability | Mitigation |
|------|---------|------------|------------|
| User adoption issues | High | Medium | Training and documentation |
| Compliance violation | High | Low | Legal review of all forms |
| Property isolation breach | High | Low | Extensive testing of access control |

---

## 10. Timeline & Phases

### Phase 1: Foundation (Week 1)
- Document creation and approval
- Database schema design
- Remove duplicate code
- Set up project structure

### Phase 2: Authentication (Week 2)
- HR setup with secret key
- Login system implementation
- Role-based middleware
- Session management

### Phase 3: HR Features (Week 3)
- Property CRUD operations
- Manager account management
- Property assignment system
- Audit logging

### Phase 4: Manager Features (Week 4)
- Manager dashboard
- Application review interface
- I-9 Section 2 completion
- Progress tracking

### Phase 5: Module Distribution (Week 5)
- Token generation system
- Module sending interface
- Tracking dashboard
- Email notifications

### Phase 6: Testing & Polish (Week 6)
- Integration testing
- UI/UX improvements
- Performance optimization
- Documentation

### Phase 7: Deployment (Week 7)
- Production setup
- Data migration
- User training
- Go-live support

---

## 11. Appendices

### Appendix A: Glossary
- **RLS**: Row Level Security
- **JWT**: JSON Web Token
- **PII**: Personally Identifiable Information
- **SPA**: Single Page Application
- **CRUD**: Create, Read, Update, Delete

### Appendix B: Related Documents
- Technical Specification
- Database Schema Design
- API Documentation
- Migration Plan

### Appendix C: Compliance Requirements
- I-9 Employment Eligibility Verification
- W-4 Employee's Withholding Certificate
- State-specific requirements
- Industry-specific training (Human Trafficking)

---

*End of Product Requirements Document*