# Hotel Employee Onboarding System - API Documentation

## Table of Contents
1. [Authentication](#authentication)
2. [Employee Onboarding Flow](#employee-onboarding-flow)
3. [Manager Endpoints](#manager-endpoints)
4. [HR Endpoints](#hr-endpoints)
5. [WebSocket Events](#websocket-events)
6. [Error Responses](#error-responses)
7. [Cache Strategy](#cache-strategy)

## Base URL
```
Production: https://api.yourdomain.com
Development: http://localhost:8000
```

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "manager|hr|employee",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
}
```

### Token Usage
All authenticated endpoints require the JWT token in the Authorization header:
```http
Authorization: Bearer <token>
```

## Employee Onboarding Flow

### 1. Job Application
```http
POST /api/apply/{property_id}
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@email.com",
  "phone": "555-0123",
  "department": "Front Desk",
  "position": "Receptionist",
  "availability": {
    "start_date": "2024-02-01",
    "shifts": ["morning", "afternoon"]
  }
}
```

### 2. Onboarding Token (After Approval)
Employee receives token via email for stateless onboarding access.

### 3. Onboarding Steps
```http
GET /api/onboarding/current-step
Authorization: Bearer <onboarding_token>

POST /api/onboarding/save-progress
Authorization: Bearer <onboarding_token>
Content-Type: application/json

{
  "step": "personal_info",
  "data": {
    "ssn": "xxx-xx-xxxx",
    "date_of_birth": "1990-01-01",
    "address": {...}
  }
}
```

### 4. Federal Forms

#### I-9 Form Submission
```http
POST /api/onboarding/i9-section1
Authorization: Bearer <onboarding_token>

{
  "citizenship_status": "us_citizen",
  "ssn": "xxx-xx-xxxx",
  "signature": "base64_image_data",
  "signed_at": "2024-01-26T10:00:00Z"
}
```

#### W-4 Form Submission
```http
POST /api/onboarding/w4-form
Authorization: Bearer <onboarding_token>

{
  "filing_status": "single",
  "exemptions": 1,
  "additional_withholding": 0,
  "signature": "base64_image_data"
}
```

## Manager Endpoints

### Dashboard Statistics
```http
GET /api/manager/dashboard-stats
Authorization: Bearer <manager_token>

Response:
{
  "success": true,
  "data": {
    "total_applications": 15,
    "pending_applications": 5,
    "employees_active": 42,
    "onboarding_in_progress": 3
  },
  "meta": {
    "cache_status": "HIT",
    "generated_at": "2024-01-26T10:00:00Z"
  }
}
```

### Get Applications
```http
GET /api/manager/applications?status=pending&property_id=uuid
Authorization: Bearer <manager_token>

Query Parameters:
- status: pending|approved|rejected
- department: string
- position: string
- date_from: ISO date
- date_to: ISO date
- search: string
- limit: number
```

### Approve Application
```http
POST /api/applications/{id}/approve
Authorization: Bearer <manager_token>

{
  "start_date": "2024-02-01",
  "comments": "Great candidate",
  "send_onboarding_email": true
}
```

### I-9 Section 2 (Manager Verification)
```http
POST /api/onboarding/i9-section2/{employee_id}
Authorization: Bearer <manager_token>

{
  "document_type": "drivers_license",
  "document_number": "D123456",
  "issuing_authority": "State of Texas",
  "expiration_date": "2026-01-01",
  "employer_signature": "base64_image_data"
}
```

## HR Endpoints

### Properties Management
```http
GET /api/hr/properties
POST /api/hr/properties
PUT /api/hr/properties/{id}
DELETE /api/hr/properties/{id}
```

### Manager Assignment
```http
POST /api/hr/properties/{id}/managers
{
  "manager_email": "manager@hotel.com",
  "first_name": "John",
  "last_name": "Manager"
}
```

### System-wide Statistics
```http
GET /api/hr/dashboard-stats

Response includes:
- Total properties
- Total managers
- Total employees
- Application pipeline metrics
- Compliance status overview
```

### Compliance Reports
```http
GET /api/hr/compliance/i9-status
GET /api/hr/compliance/missing-documents
GET /api/hr/compliance/expiring-documents?days=30
```

## WebSocket Events

### Connection
```javascript
ws://localhost:8000/ws/{client_id}?token={jwt_token}
```

### Event Types

#### New Application
```json
{
  "type": "new_application",
  "data": {
    "id": "uuid",
    "applicant_name": "Jane Smith",
    "position": "Receptionist",
    "property_id": "uuid",
    "applied_at": "2024-01-26T10:00:00Z"
  },
  "timestamp": "2024-01-26T10:00:00Z",
  "priority": "high"
}
```

#### Status Change
```json
{
  "type": "status_change",
  "data": {
    "application_id": "uuid",
    "old_status": "pending",
    "new_status": "approved",
    "changed_by": "manager@hotel.com"
  }
}
```

#### Onboarding Progress
```json
{
  "type": "onboarding_progress",
  "data": {
    "employee_id": "uuid",
    "step_completed": "i9_section1",
    "progress_percentage": 75,
    "next_step": "direct_deposit"
  }
}
```

## Error Responses

All errors follow this format:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "User-friendly error message",
    "detail": "Technical details (optional)",
    "error_id": "ERR-ABC12345",
    "field_errors": {
      "email": ["Invalid email format"]
    }
  }
}
```

### Error Codes
- `VALIDATION_ERROR` (400)
- `AUTHENTICATION_ERROR` (401)
- `AUTHORIZATION_ERROR` (403)
- `RESOURCE_NOT_FOUND` (404)
- `RESOURCE_CONFLICT` (409)
- `DATABASE_ERROR` (500)
- `EXTERNAL_SERVICE_ERROR` (503)
- `COMPLIANCE_ERROR` (422)

## Cache Strategy

### Cached Data (5-10 min TTL)
- Dashboard statistics
- Property lists
- User permissions
- Aggregate counts
- Department/position lists

### Never Cached (Real-time)
- Individual applications
- WebSocket messages
- New application notifications
- Status changes
- Compliance data (I-9, W-4)
- Signatures
- Audit logs

### Cache Headers
```http
X-Cache: HIT|MISS|BYPASS-REALTIME
X-Cache-Stats: H:100 M:20 B:5
Cache-Control: no-cache (for real-time endpoints)
```

## Rate Limiting

- Authentication: 5 requests per minute
- API endpoints: 100 requests per minute
- WebSocket messages: 10 per second

## Federal Compliance Notes

### I-9 Requirements
- Section 1 must be completed by/before first day of work
- Section 2 must be completed within 3 business days
- Documents must be retained for 3 years after hire or 1 year after termination

### W-4 Requirements
- Must use current year IRS form
- Updates allowed at any time per employee request
- Version history must be maintained

### Digital Signatures
All digital signatures capture:
- Timestamp
- IP address
- User agent
- Consent acknowledgment
- Base64 image data

## Property-Based Access Control

Managers can only access data for properties they're assigned to:
```http
GET /api/manager/applications
# Automatically filtered to manager's properties

GET /api/manager/employees  
# Only shows employees in manager's properties
```

HR users have full system access:
```http
GET /api/hr/applications
# Shows all applications across all properties

GET /api/hr/applications?property_id=uuid
# Can filter by specific property
```