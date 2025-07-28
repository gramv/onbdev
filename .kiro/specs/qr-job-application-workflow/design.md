# Design Document

## Overview

This design implements the missing components for the QR code and job application workflow. The system will generate QR codes for properties, handle job application submissions, and manage the complete hiring workflow from application to onboarding. The design prioritizes demo-ready functionality with minimal complexity.

## Architecture

### System Flow
1. **QR Code Generation**: HR generates QR codes for properties that link to job application forms
2. **Application Submission**: Applicants scan QR codes and submit applications via a public form
3. **Application Review**: Managers review applications filtered by their property and department
4. **Approval Process**: Managers approve one candidate per position, others go to talent pool
5. **Notifications**: Basic email notifications for approved/rejected candidates
6. **Onboarding**: Approved candidates receive onboarding links to complete hiring

### Key Components

#### Backend Components
- **QR Code Service**: Generates QR codes using a simple QR library
- **Public Application API**: Handles form submissions without authentication
- **Email Service**: Basic email notifications using SMTP
- **Application Status Manager**: Handles status transitions and talent pool logic

#### Frontend Components
- **QR Code Display**: Shows QR codes in property management
- **Public Application Form**: Standalone form accessible via QR codes
- **Application Management**: Enhanced filtering and approval workflow

## Components and Interfaces

### Backend API Endpoints

#### QR Code Management
```python
@app.post("/hr/properties/{property_id}/qr-code")
async def regenerate_qr_code(property_id: str, current_user: User = Depends(require_hr_or_manager_role)):
    """Generate new QR code for property job applications"""
    # HR can generate for any property
    # Managers can only generate for their assigned property
    # Generate QR code pointing to: /apply/{property_id}
    # Update property.qr_code_url
    # Return QR code data and URL

@app.get("/properties/{property_id}/info")
async def get_property_public_info(property_id: str):
    """Get basic property info for job application form (public access)"""
    # Return property name, address, available departments
    # No authentication required
```

#### Job Application Submission
```python
@app.post("/apply/{property_id}")
async def submit_job_application(property_id: str, application_data: JobApplicationData):
    """Submit job application (public endpoint)"""
    # Validate property exists and is active
    # Create application record with PENDING status
    # Return confirmation message
    # No authentication required

@app.get("/apply/{property_id}")
async def get_application_form_data(property_id: str):
    """Get data needed for application form (public access)"""
    # Return property info, available departments/positions
    # No authentication required
```

#### Enhanced Application Management
```python
@app.put("/hr/applications/{application_id}/approve")
async def approve_application_enhanced(
    application_id: str, 
    job_offer_data: JobOfferData,
    current_user: User = Depends(require_manager_role)
):
    """Approve application and move others to talent pool"""
    # Approve selected application
    # Move other applications for same position to talent pool
    # Create employee record and onboarding token
    # Trigger email notifications
    # Return onboarding link

@app.put("/hr/applications/bulk-talent-pool")
async def move_to_talent_pool(
    application_ids: List[str],
    current_user: User = Depends(require_manager_role)
):
    """Move multiple applications to talent pool"""
    # Update application status to TALENT_POOL
    # Trigger talent pool notification emails
```

### Frontend Components

#### QR Code Display Component
```typescript
interface QRCodeDisplayProps {
  property: Property
  onRegenerate: (propertyId: string) => void
}

// Shows QR code image, application URL, and regenerate button
// Includes copy-to-clipboard functionality for URL sharing
```

#### Public Application Form
```typescript
// Standalone page at /apply/{propertyId}
// No authentication required
// Collects: personal info, position preference, experience
// Submits to /apply/{propertyId} endpoint
// Shows confirmation on successful submission
```

#### Enhanced Application Management
```typescript
// Add bulk actions to ApplicationsTab
// Group applications by position for easier review
// Show talent pool status and management
// One-click approval with job offer details
```

## Data Models

### Enhanced Application Model
```python
class JobApplication:
    id: str
    property_id: str
    status: ApplicationStatus  # PENDING, APPROVED, REJECTED, TALENT_POOL
    position_applied: str
    department: str
    applicant_data: dict
    applied_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
    talent_pool_date: Optional[datetime]  # When moved to talent pool
    rejection_reason: Optional[str]
```

### QR Code Data
```python
class PropertyQRCode:
    property_id: str
    qr_code_url: str  # URL to QR code image
    application_url: str  # URL QR code points to
    generated_at: datetime
    generated_by: str
```

### Job Offer Data
```python
class JobOfferData:
    job_title: str
    start_date: date
    pay_rate: float
    pay_frequency: str
    employment_type: str
    supervisor: str
    benefits_eligible: bool
```

## Error Handling

### QR Code Generation
- Handle QR library failures gracefully
- Fallback to text URL if QR generation fails
- Validate property exists before generating QR code

### Application Submission
- Validate all required fields
- Check property is active and accepting applications
- Handle duplicate submissions (same email + property)
- Sanitize input data to prevent injection attacks

### Email Notifications
- Queue emails for retry on failure
- Log email delivery status
- Provide fallback notification methods
- Handle invalid email addresses gracefully

## Testing Strategy

### Demo Preparation
1. **Test Data Setup**: Create sample properties with QR codes
2. **Application Scenarios**: Generate test applications in various states
3. **End-to-End Testing**: Verify complete workflow from QR scan to onboarding
4. **Error Scenarios**: Test edge cases and error handling

### Integration Testing
- Test QR code generation and scanning
- Verify application submission and approval workflow
- Test email notification delivery
- Validate talent pool management

### Performance Considerations
- QR code generation should be fast (<2 seconds)
- Application form should load quickly on mobile devices
- Email notifications should be asynchronous
- Database queries should be optimized for application filtering

## Security Considerations

### Public Endpoints
- Rate limiting on application submission
- Input validation and sanitization
- CAPTCHA for spam prevention (future enhancement)
- No sensitive data exposure in public endpoints

### QR Code Security
- QR codes should not contain sensitive information
- Application URLs should be time-limited (future enhancement)
- Monitor for QR code abuse or scraping

### Data Protection
- Applicant data should be encrypted at rest
- PII should be handled according to privacy regulations
- Application data retention policies
- Secure email transmission for notifications