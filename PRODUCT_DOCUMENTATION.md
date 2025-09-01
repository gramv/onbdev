# Hotel Employee Onboarding System - Product Documentation

## **System Overview**
A comprehensive digital onboarding platform specifically designed for the hospitality industry with strict federal compliance requirements (I-9, W-4 forms). The system implements a three-phase workflow with property-based access control, real-time collaboration, and federal compliance automation.

## **Architecture & Technology Stack**

### **Backend (FastAPI + Python 3.12+)**
- **Framework**: FastAPI with async/await patterns
- **Database**: Supabase (PostgreSQL) with Row Level Security
- **Authentication**: JWT-based with role-based access control
- **OCR**: Google Document AI (government IDs only - no fallbacks for security)
- **PDF Generation**: PyMuPDF and ReportLab for federal forms
- **Real-time**: WebSocket manager for dashboard updates
- **Email**: SMTP notifications and document delivery

### **Frontend (React + TypeScript)**
- **Framework**: React 18 with TypeScript and Vite
- **UI Library**: Radix UI components with Tailwind CSS
- **State Management**: Context API with custom hooks
- **Features**: Multi-language support (English/Spanish), PWA capabilities, real-time sync

## **Three-Phase Workflow**

### **Phase 1: Employee Self-Service**
Employees complete their onboarding independently using a secure 7-day JWT token:
1. **Welcome** (2 min) - Language selection and introduction
2. **Personal Information** (8 min) - Contact details, emergency contacts
3. **Job Details Confirmation** (3 min) - Verify position and start date
4. **Company Policies** (10 min) - Review and acknowledge policies
5. **I-9 Complete** (20 min) - Federal employment verification with digital signature
6. **W-4 Tax Form** (10 min) - Federal tax withholding information
7. **Direct Deposit** (5 min) - Banking information setup
8. **Human Trafficking Awareness** (5 min) - Required federal training
9. **Weapons Policy** (2 min) - Workplace safety acknowledgment
10. **Health Insurance** (8 min) - Benefits enrollment
11. **Document Upload** (5 min) - Supporting documents
12. **Final Review** (5 min) - Review and submit all information

### **Phase 2: Manager Review**
Property managers review and verify employee submissions:
- Review all employee-submitted information
- Complete I-9 Section 2 verification (within 3 business days)
- Request corrections if needed
- Approve or reject the onboarding package

### **Phase 3: HR Final Approval**
HR administrators perform final compliance review:
- System-wide oversight across all properties
- Final compliance verification
- Integration with payroll and HR systems
- Audit trail maintenance

## **User Roles & Authentication**

### **HR Users (15-20 users)**
- **Access**: Full system access across all properties
- **Authentication**: Persistent JWT tokens with hr_auth type
- **Capabilities**:
  - View all applications and employees system-wide
  - Override manager decisions
  - Generate compliance reports
  - Manage properties and managers
  - Access analytics and audit trails

### **Managers (200+ users)**
- **Access**: Property-specific access only
- **Authentication**: Persistent JWT tokens with manager_auth type
- **Property Isolation**: All queries filtered by property_id for security
- **Capabilities**:
  - View applications and employees for their property only
  - Approve/reject job applications
  - Review onboarding submissions
  - Complete I-9 Section 2 verification
  - Generate property-specific reports

### **Employees (Unlimited)**
- **Access**: Stateless 7-day JWT tokens (no permanent accounts)
- **Authentication**: Temporary onboarding tokens
- **Capabilities**:
  - Complete onboarding steps
  - Upload documents
  - Digital signature capture
  - View their own progress

## **Federal Compliance Features**

### **I-9 Employment Verification**
- **Section 1**: Employee completes by first day of work
- **Section 2**: Manager completes within 3 business days
- **Digital Signatures**: Precise coordinate mapping between frontend/backend
- **Document Verification**: Google Document AI OCR for government IDs
- **Audit Trail**: Complete compliance tracking

### **W-4 Tax Forms**
- **Federal Requirements**: Automatic validation and error checking
- **Digital Signatures**: Legally compliant electronic signatures
- **PDF Generation**: Official IRS-compliant forms

### **Document Security**
- **OCR Processing**: Google Document AI only (no fallbacks for security)
- **Storage**: Encrypted document storage with retention policies
- **Access Control**: Role-based document access

## **Key Technical Features**

### **Property-Based Access Control**
```python
# Every database query must include property_id filtering
employees = await supabase.get_employees_by_property(property_id)
# Security violation - never allowed:
employees = await supabase.get_all_employees()
```

### **Real-time Updates**
- WebSocket connections for dashboard updates
- Live progress tracking
- Instant notification delivery
- Collaborative review process

### **Performance & Scalability**
- **Connection Pooling**: 50 max, 10 min connections
- **Caching**: Frequently accessed data with LRU cache
- **Database Indexes**: Property-based query optimization
- **Async Operations**: Non-blocking I/O throughout

### **PDF Signature Coordination**
```typescript
// Frontend (pdf-lib) - bottom-left origin
{ x: 150, y: 142, width: 200, height: 50 }

// Backend (PyMuPDF) - coordinate transformation required
{ x: 150, y: 650, width: 200, height: 50 }
```

## **Development Practices**

### **"Brick-by-Brick" Methodology**
1. Build one component completely
2. Test in isolation
3. Connect to next component
4. Verify integration
5. Move to next component

### **Security-First Approach**
- Property isolation enforced at service layer
- No mock data in production
- JWT token management with expiration
- Row Level Security (RLS) in database
- Encrypted sensitive data storage

### **Step Component Pattern**
All onboarding steps follow standardized props interface:
```typescript
interface StepProps {
  currentStep: { id: string, name: string, order: number, required: boolean }
  progress: { completedSteps: string[], currentStepIndex: number, totalSteps: number, percentComplete: number }
  markStepComplete: (stepId: string, data?: any) => Promise<void>
  saveProgress: (stepId: string, data?: any) => Promise<void>
  language: 'en' | 'es'
  employee: Employee
  property: Property
}
```

## **Production Deployment**

### **Environment Requirements**
- **Python**: 3.12+ required
- **Node**: 20 LTS required
- **Database**: Supabase (PostgreSQL) only
- **Package Management**: pip and requirements.txt (no Poetry in production)

### **Critical Environment Variables**
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` - Database connection
- `GOOGLE_CREDENTIALS_BASE64` - OCR service credentials
- `JWT_SECRET_KEY` - Authentication security
- `FRONTEND_URL` - CORS and email links

### **Database Indexes (Production)**
```sql
CREATE INDEX idx_employees_property_id ON employees(property_id);
CREATE INDEX idx_applications_property_status ON job_applications(property_id, status);
CREATE INDEX idx_managers_property ON property_managers(property_id);
```

## **Compliance & Audit**

### **Federal Requirements**
- I-9 forms must be completed within federal deadlines
- W-4 forms require proper validation
- Document retention policies enforced
- Audit trails for all form modifications

### **System Monitoring**
- Response times < 200ms target
- Property isolation verification
- Compliance deadline tracking
- Error logging and alerting

This system represents a mature, enterprise-grade solution with comprehensive federal compliance, security best practices, and scalable architecture designed specifically for the hospitality industry's unique onboarding requirements.
