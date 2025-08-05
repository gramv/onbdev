# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Agent OS Integration

This project uses **Agent OS** - a system for better planning and executing software development tasks with AI agents. Agent OS ensures consistent, high-quality code generation aligned with our specific standards and requirements.

### Agent OS Structure
- **Global Standards**: Located at `~/.agent-os/standards/` - defines tech stack, code style, and best practices
- **Product Documentation**: Located at `~/.agent-os/product/` - contains mission, roadmap, and decisions
- **Feature Specifications**: Located at `~/.agent-os/product/specs/` - detailed specs for each feature

### Available Commands
- `/analyze-product` - Analyze existing codebase and create product documentation
- `/plan-product` - Create or update product planning documents
- `/create-spec` - Create detailed feature specifications before implementation
- `/execute-task` - Implement features following specifications and standards

### Development Workflow with Agent OS
1. **Before starting new features**: Run `/create-spec` to create detailed specifications
2. **Follow brick-by-brick methodology**: Build and test each component completely before moving to next
3. **Adhere to standards**: All code must follow patterns defined in Agent OS standards
4. **Maintain documentation**: Update specs and decisions as the project evolves

### Using Agent OS Agents for Complex Tasks
When working on multi-faceted improvements or refactoring:
- **Use specialized agents**: Leverage agents like `frontend-component-fixer`, `onboarding-form-builder`, or `compliance-validator` for specific tasks
- **Parallel execution**: Launch multiple agents concurrently for independent tasks to maximize efficiency
- **Complex refactoring**: For tasks like breaking up large components or implementing cross-component features, use appropriate agents
- **Testing and validation**: Use `test-automation-engineer` and `field-validation-tester` agents to ensure thorough testing

Example workflow for complex changes:
```
1. Use frontend-component-fixer for navigation improvements
2. Use onboarding-form-builder for form restructuring  
3. Use field-validation-tester for cross-field validation
4. Use compliance-validator for federal requirement checks
```

## Project Overview

This is a comprehensive hotel employee onboarding system built with a FastAPI backend and React/TypeScript frontend. The system handles the complete employee lifecycle from job application to onboarding completion, including document management, digital signatures, and compliance requirements.

**CRITICAL IMPLEMENTATION APPROACH**: This system is being rebuilt using a **brick-by-brick methodology** where each page/component is built individually, tested thoroughly, then connected to the next page. This ensures a stable, working system at each step rather than attempting to build everything at once.

**MODULAR FORM ARCHITECTURE**: The system is designed with complete modularity where individual forms (W-4, I-9, health insurance, etc.) can be sent independently to employees for updates at any time. When an employee's situation changes (marriage, dependents, address), HR can send just the specific form needed for update without requiring a complete onboarding process.

## Three-Phase Onboarding Workflow Implementation Plan

### Overview
The system implements a complete digital onboarding workflow that replicates the current paper packet with three distinct phases:
1. **Employee Phase**: Job application → Manager approval → Employee completes onboarding
2. **Manager Phase**: Reviews employee submission → Completes manager sections → Approves or requests corrections
3. **HR Phase**: Final review → Compliance verification → System integration or corrections

### Workflow Entry Points
- **Job Application Submitted**: Candidate applies for position
- **Manager Reviews Application**: 
  - If approved → Manager fills initial employee setup form (Page 1-2)
  - If rejected → Candidate receives gentle rejection + talent pool invitation email
- **After Manager Setup**: Employee receives onboarding link with pre-populated job details

## Phase 0: Manager Initial Setup

Before employee begins onboarding, manager must complete:

### Manager Setup Module
**Maps to**: Pages 1-2 of packet
- **Component**: `ManagerEmployeeSetup.tsx` (to be built)
- **Data collected**:
  - Hotel name/address
  - Employee name, SSN, DOB, gender
  - Address and contact information
  - Position, department, hire date
  - Pay rate, schedule (FT/PT)
  - Initial health insurance selection
  - Manager/supervisor information
- **Actions**: Generate unique onboarding link for employee

## Phase 1: Employee Onboarding Modules

Based on the 28-page onboarding packet analysis, the employee must complete these modules:

### Module Mapping to Paper Packet

| Module | Component | Packet Pages | Description |
|--------|-----------|--------------|-------------|
| 1. Welcome & Personal Info | `WelcomeStep.tsx`, `PersonalInfoStep.tsx` | Page 5 | Language selection, personal details |
| 2. Job Details Confirmation | `JobDetailsStep.tsx` | Page 2 | Review position, pay rate, start date |
| 3. Emergency Contacts | `EmergencyContactsStep.tsx` | N/A | Emergency contact information |
| 4. Company Policies | `CompanyPoliciesStep.tsx` | Pages 3-6, 9, 20 | All company policy acknowledgments |
| 5. I-9 Section 1 | `I9Section1Step.tsx` | Page 10 | Employment eligibility (by first day) |
| 6. I-9 Supplements | `I9SupplementsStep.tsx` | Pages 12-13 | Conditional - only if applicable |
| 7. W-4 Tax Form | `W4FormStep.tsx` | Pages 15-17 | 2025 federal tax withholding |
| 8. Direct Deposit | `DirectDepositStep.tsx` | Page 18 | Banking information |
| 9. Human Trafficking | `TraffickingAwarenessStep.tsx` | Pages 19, 21 | Federal requirement for hospitality |
| 10. Weapons Policy | `WeaponsPolicyStep.tsx` | Page 22 | Weapons prohibition acknowledgment |
| 11. Health Insurance | `HealthInsuranceStep.tsx` | Pages 23-28 | Benefits election or waiver |
| 12. Document Upload | `DocumentUploadStep.tsx` | Page 1 ref | I-9 documents, voided check |
| 13. Final Review | `FinalReviewStep.tsx` | N/A | Review all info, submit |

## Phase 2: Manager Review Modules

After employee submission, manager receives notification to complete:

### Manager Responsibilities
1. **Review Employee Information**: Verify all submitted data matches initial setup
2. **I-9 Section 2**: Complete within 3 business days (Page 11)
3. **Document Verification**: Verify uploaded documents match requirements
4. **Approval Actions**:
   - Approve and send to HR
   - Request corrections on specific modules with comments

## Phase 3: HR Final Review

HR performs final compliance review and system integration:

### HR Responsibilities
1. **Compliance Verification**: Ensure federal requirements met
2. **Document Audit**: Verify all required documents present
3. **Final Actions**:
   - Approve and add employee to system
   - Request manager corrections (with CC)
   - Request employee corrections (manager CC'd)

## Implementation Stages

### Stage 1: Employee Side (Current Focus)
- [ ] Fix all 16 step components to use direct props pattern
- [ ] Build missing modules if any
- [ ] Create employee onboarding flow navigation
- [ ] Implement progress tracking and auto-save
- [ ] Add module-level validation

### Stage 2: Manager Side
- [ ] Create manager dashboard
- [ ] Build I-9 Section 2 interface
- [ ] Implement document review screens
- [ ] Add approval/correction workflow
- [ ] Create manager notification system

### Stage 3: HR Side
- [ ] Build HR dashboard with queue
- [ ] Create compliance verification tools
- [ ] Implement final approval workflow
- [ ] Add correction request system
- [ ] Build employee system integration

### Stage 4: Workflow Integration
- [ ] Connect all three phases
- [ ] Implement email notifications
- [ ] Add real-time status updates
- [ ] Create audit trail
- [ ] End-to-end testing

### Stage 5: Polish & Deploy
- [ ] Security audit
- [ ] Performance optimization
- [ ] Multi-language testing
- [ ] Compliance validation
- [ ] Production deployment

## Technical Architecture

### API Endpoints
```
# Manager endpoints (requires auth)
POST /api/applications/{id}/approve - Manager approves application, generates JWT
POST /api/applications/{id}/reject - Manager rejects (talent pool)
POST /api/manager/onboarding/{id}/review - Manager completes I-9 Section 2
POST /api/manager/onboarding/{id}/request-correction - Request employee corrections

# Employee endpoints (JWT token auth)
GET /api/onboarding/validate-token - Validate JWT and get session info
GET /api/onboarding/session - Get current onboarding progress (JWT required)
POST /api/onboarding/step/{step_id}/save - Save step progress (JWT required)
POST /api/onboarding/step/{step_id}/complete - Complete step (JWT required)
POST /api/onboarding/submit - Submit final onboarding (JWT required)

# HR endpoints (requires auth)
POST /api/hr/onboarding/{id}/approve - HR final approval
POST /api/hr/onboarding/{id}/regenerate-token - Generate new 7-day token
GET /api/hr/onboarding/expired - List expired/incomplete onboardings
```

### Key Features
- **Modular Independence**: Each module saves/submits independently
- **Correction Workflow**: Individual modules can be sent back for fixes
- **Compliance Tracking**: Federal requirement timers and validations
- **Audit Trail**: Complete history of all actions and changes

## Development Notes

- **Backend Python Version**: Use Python3 for backend implementation, not Poetry
  - Transition away from Poetry dependency management
  - Use standard Python virtual environments and `requirements.txt`
  - Ensure compatibility with Python 3.12+

- **NO MOCK DATA - PRODUCTION SYSTEM**: This is a production system. All OCR and document processing must use real API calls to extract actual data from uploaded documents. Never return hardcoded/mock data for document processing, authentication, or any other production features.

## Scalability Architecture

### System Capacity
The system is designed to handle:
- **15-20 HR users** with full dashboard access
- **200+ Managers** with property-specific access
- **Unlimited employees** (stateless onboarding sessions only)

### Key Architecture Decisions

#### User Account Model
1. **Only Managers and HR have accounts** - Full authentication with username/password
2. **Employees are stateless** - No user accounts, no login credentials
3. **Employee Access via JWT tokens**:
   - When manager approves job application, system generates 7-day JWT token
   - Unique onboarding URL created: `https://onboarding.hotel.com/onboard?token={JWT}`
   - Token contains: employee_id, property_id, position, expiry
   - URL sent to employee via email/SMS
   - No password required - just click the link
   - After 7 days, token expires and HR must generate new link if needed

#### Access Control
1. **Managers have limited scope** - Can only see their property's data
2. **HR has global view** - But with pagination and filtering
3. **Employees have temporary access** - Only to their own onboarding session

#### Security Benefits
- No employee credentials to manage or reset
- Reduced attack surface (no employee login page)
- Automatic expiration prevents stale access
- Each onboarding session is isolated

### Production Deployment Recommendations

#### 1. Simple Caching Layer (Priority: High)
```python
# Add to backend for frequently accessed data
from functools import lru_cache
import asyncio

@lru_cache(maxsize=128)
async def get_cached_properties():
    return await supabase.get_all_properties()

# Clear cache every 5 minutes
async def cache_invalidator():
    while True:
        await asyncio.sleep(300)
        get_cached_properties.cache_clear()
```

#### 2. Connection Pool Configuration
```python
# In supabase_service_enhanced.py
max_connections = 50  # Increase from 20
min_connections = 10  # Increase from 5
```

#### 3. Multi-Worker Deployment
```bash
# Production deployment command
gunicorn app.main_enhanced:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

#### 4. Database Indexes (Run once)
```sql
-- Optimize common queries
CREATE INDEX idx_employees_property_id ON employees(property_id);
CREATE INDEX idx_applications_property_status ON job_applications(property_id, status);
CREATE INDEX idx_managers_property ON property_managers(property_id);
CREATE INDEX idx_onboarding_token ON onboarding_tokens(token) WHERE expires_at > NOW();
```

#### 5. API Response Optimization
- Implement pagination on all list endpoints (already done for most)
- Add `select` parameter to return only needed fields
- Use database views for complex joins

### Performance Monitoring
- Monitor response times for API endpoints
- Track database connection pool usage
- Set up alerts for slow queries (>1s)
- Monitor memory usage of Node.js frontend 

## I-9 and W-4 Module Implementation Status

### Completed Features
✅ **Backend API Endpoints**
- `POST /api/onboarding/{employee_id}/i9-section1` - Save I-9 Section 1 data
- `GET /api/onboarding/{employee_id}/i9-section1` - Retrieve I-9 Section 1 data
- `POST /api/onboarding/{employee_id}/i9-section1/generate-pdf` - Generate I-9 PDF
- `POST /api/onboarding/{employee_id}/w4-form` - Save W-4 form data
- `GET /api/onboarding/{employee_id}/w4-form` - Retrieve W-4 form data
- `POST /api/onboarding/{employee_id}/w4-form/generate-pdf` - Generate W-4 PDF

✅ **Frontend Integration**
- I9Section1Step now saves data to backend on form save and signature
- W4FormStep now saves data to backend on form save and signature
- Digital signature capture integrated via ReviewAndSign component
- Signature metadata includes timestamp, user agent for compliance

✅ **PDF Generation**
- PDFFormFiller class with official I-9 and W-4 field mappings
- Signature embedding in PDFs
- Federal compliance metadata

### Pending Implementation
❌ **Manager Interface for I-9 Section 2**
- Manager dashboard component to complete Section 2
- Document verification interface
- 3-day deadline tracking from hire date

❌ **Compliance Deadline Tracking**
- I-9 Section 1: Must be completed by first day of work
- I-9 Section 2: Must be completed within 3 business days
- Visual indicators and alerts for approaching deadlines

❌ **Full Workflow Testing**
- End-to-end test of employee completing I-9/W-4
- Manager review and Section 2 completion
- PDF generation and storage

### Database Tables Required
```sql
-- I-9 Forms table
CREATE TABLE i9_forms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id UUID REFERENCES employees(id),
  section VARCHAR(20), -- 'section1', 'section2', 'section3'
  form_data JSONB,
  signed BOOLEAN DEFAULT false,
  signature_data TEXT,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- W-4 Forms table
CREATE TABLE w4_forms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id UUID REFERENCES employees(id),
  tax_year INTEGER,
  form_data JSONB,
  signed BOOLEAN DEFAULT false,
  signature_data TEXT,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_i9_employee_section ON i9_forms(employee_id, section);
CREATE INDEX idx_w4_employee_year ON w4_forms(employee_id, tax_year);
```

## Development Commands

### Backend
```bash
cd hotel-onboarding-backend
python3 -m venv venv              # Create virtual environment
source venv/bin/activate          # Activate (Linux/Mac)
pip install -r requirements.txt   # Install dependencies
python3 -m app.main_enhanced      # Run enhanced server
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
```

### Testing Routes
- `/test-steps` - Test individual step components in isolation
- `/onboard` - Main enhanced onboarding portal (under development)
- `/manager` - Manager dashboard for reviews and approvals
- `/hr` - HR dashboard for final approvals (to be built)

## Architecture

### Backend (hotel-onboarding-backend/)
- **Framework**: FastAPI with Python 3.12+
- **Database**: Supabase (PostgreSQL)
- **Key Files**:
  - `app/main_enhanced.py`: Primary backend with all endpoints
  - `app/models.py`: Comprehensive Pydantic models
  - `app/supabase_service_enhanced.py`: Database service layer
  - `app/auth.py`: Authentication and authorization
  - `app/pdf_forms.py`: PDF generation for federal forms
- **External Services**: Groq API for OCR/vision processing

### Frontend (hotel-onboarding-frontend/)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Radix UI components with Tailwind CSS
- **State Management**: React Context API (AuthContext, LanguageContext)
- **Form Management**: React Hook Form with Zod validation

## Component Architecture

### Step Component Pattern
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

## Form Signature Flow Rules

### Single Review and Sign Flow
- **Each form must have only one integrated review/sign flow within its main step component**
- **No separate review/sign steps** - Review and signature functionality must be part of the form step itself
- **Session state preservation** - If a form is already signed, show the PDF preview directly without re-entering review mode
- **Prevent duplicate signatures** - Once signed, forms should not allow re-signing unless explicitly cleared

### Consistent Signature Positioning
- **All PDF signatures must use standardized positions defined in the frontend generators**
- **Backend PDF generation must match frontend signature coordinates exactly**
- **W-4 Signature Position**: x: 150, y: 650 (from bottom-left origin in backend PyMuPDF)
- **W-4 Signature Position**: x: 150, y: 142 (from bottom-left origin in frontend pdf-lib)
- **I-9 Employee Signature Position**: x: 350, y: 650 (from bottom-left origin)
- **Coordinate system**: Always document whether using top-left or bottom-left origin

## Government Compliance Requirements

### I-9 Employment Eligibility Verification
- **Section 1**: Must be completed by employee on or before first day of work
- **Section 2**: Must be completed by employer within 3 business days of start date
- **Supplements A/B**: Only used in specific circumstances
- **Document Requirements**: Must verify both identity AND work authorization
- **Retention**: 3 years after hire or 1 year after termination (whichever is later)

### W-4 Employee's Withholding Certificate
- **IRS Compliance**: Must use current year (2025) IRS form template
- **Digital Signature**: Must capture with timestamp and compliance metadata
- **Updates**: Employees can update W-4 at any time

### Federal Documentation Standards
- **Digital Signatures**: Must include timestamp, IP address, legal metadata
- **Data Retention**: All federal forms retained per requirements
- **Privacy Protection**: All personal information encrypted
- **Audit Trail**: Complete audit trail for compliance actions

## Agent OS Usage Guidelines

### When to Use Agent OS Commands

1. **Starting New Features**
   - Always run `/create-spec` before implementing any new feature
   - Review the generated spec and adjust if needed
   - Ensure spec aligns with federal compliance requirements

2. **Implementing Features**
   - Use `/execute-task` to implement features according to specs
   - Agent OS will follow the brick-by-brick methodology automatically
   - All code will adhere to our established patterns and standards

3. **Project Analysis**
   - Run `/analyze-product` periodically to assess progress
   - Use insights to update roadmap and priorities
   - Identify technical debt and compliance gaps

### Agent OS Standards Override

While Agent OS provides global standards, this project has specific overrides:

1. **Component Pattern**: Always use direct props (StepProps interface), never useOutletContext
2. **Federal Compliance**: I-9 and W-4 requirements take precedence over generic form patterns
3. **Modular Architecture**: Each form must be independently deployable
4. **Security**: PII handling must follow our specific encryption standards

### Integration with Existing Workflow

Agent OS complements our existing development process:
- Continue using git flow for version control
- Maintain PR reviews for all changes
- Run compliance tests before merging
- Update Agent OS specs when requirements change

For more details on Agent OS configuration, see:
- `~/.agent-os/standards/` - Our customized standards
- `~/.agent-os/product/` - Product documentation
- `~/.agent-os/product/specs/` - Feature specifications