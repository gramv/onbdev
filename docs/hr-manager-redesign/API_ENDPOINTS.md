# API Endpoints Documentation
## Hotel Employee Onboarding System - Complete API Reference

### Document Version
- **Version**: 1.0
- **Date**: January 2025
- **Base URL**: `https://api.hotel-onboarding.com/api`
- **Related**: PRD.md, TECHNICAL_SPEC.md, DATABASE_SCHEMA.md

---

## 1. Authentication Endpoints

### 1.1 Login
**POST** `/auth/login`

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "role": "hr|manager",
      "first_name": "John",
      "last_name": "Doe",
      "properties": ["property_id_1", "property_id_2"]
    }
  }
}
```

**Error Responses:**
- `401`: Invalid credentials
- `403`: Account deactivated
- `429`: Too many attempts

---

### 1.2 Logout
**POST** `/auth/logout`

Invalidate current session.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 1.3 Refresh Token
**POST** `/auth/refresh`

Get new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400
  }
}
```

---

### 1.4 Get Current User
**GET** `/auth/me`

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "hr",
    "first_name": "John",
    "last_name": "Doe",
    "properties": [],
    "last_login": "2025-01-14T10:00:00Z"
  }
}
```

---

### 1.5 Change Password
**PUT** `/auth/change-password`

Change user's password.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!",
  "confirm_password": "NewPassword456!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## 2. Setup Endpoints

### 2.1 Create First HR Admin
**POST** `/setup/hr-admin`

One-time setup to create the first HR admin account.

**Request Body:**
```json
{
  "secret_key": "ENV_SECRET_KEY_VALUE",
  "email": "hr@hotel-chain.com",
  "password": "SecurePassword123!",
  "first_name": "Admin",
  "last_name": "User"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "hr@hotel-chain.com",
    "message": "HR admin account created successfully"
  }
}
```

**Error Responses:**
- `400`: Invalid secret key
- `409`: HR admin already exists

---

## 3. HR Admin Endpoints

### 3.1 Properties Management

#### 3.1.1 List All Properties
**GET** `/hr/properties`

Get all properties in the system.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `search` (string): Search by name or city
- `state` (string): Filter by state

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": "uuid",
        "name": "Grand Hotel Downtown",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "phone": "212-555-0100",
        "manager_count": 3,
        "employee_count": 45,
        "is_active": true,
        "created_at": "2025-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "pages": 1
    }
  }
}
```

---

#### 3.1.2 Create Property
**POST** `/hr/properties`

Create a new hotel property.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Grand Hotel Downtown",
  "code": "GHD001",
  "address": "123 Main St",
  "address_line2": "Suite 100",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "phone": "212-555-0100",
  "email": "info@grandhotel.com",
  "website": "https://grandhotel.com"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Grand Hotel Downtown",
    "message": "Property created successfully"
  }
}
```

---

#### 3.1.3 Update Property
**PUT** `/hr/properties/{property_id}`

Update property information.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Grand Hotel Downtown - Updated",
  "phone": "212-555-0200"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Property updated successfully"
}
```

---

#### 3.1.4 Delete Property
**DELETE** `/hr/properties/{property_id}`

Soft delete a property.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Property deactivated successfully"
}
```

---

### 3.2 Manager Management

#### 3.2.1 List All Managers
**GET** `/hr/managers`

Get all managers in the system.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `property_id` (uuid): Filter by property
- `is_active` (boolean): Filter by active status

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "managers": [
      {
        "id": "uuid",
        "email": "manager@hotel.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "555-0100",
        "is_active": true,
        "properties": [
          {
            "id": "uuid",
            "name": "Grand Hotel Downtown",
            "assigned_at": "2025-01-01T00:00:00Z"
          }
        ],
        "last_login": "2025-01-14T09:00:00Z"
      }
    ]
  }
}
```

---

#### 3.2.2 Create Manager Account
**POST** `/hr/managers`

Create a new manager account.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "email": "manager@hotel.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "555-0100",
  "temporary_password": "TempPass123!",
  "property_ids": ["property_uuid_1", "property_uuid_2"]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "email": "manager@hotel.com",
    "message": "Manager account created and assigned to properties"
  }
}
```

---

#### 3.2.3 Assign Manager to Property
**POST** `/hr/managers/{manager_id}/assign`

Assign manager to additional properties.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "property_ids": ["property_uuid_3", "property_uuid_4"]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Manager assigned to 2 properties"
}
```

---

#### 3.2.4 Revoke Manager Access
**DELETE** `/hr/managers/{manager_id}/properties/{property_id}`

Remove manager's access to a specific property.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Property access revoked"
}
```

---

#### 3.2.5 Deactivate Manager
**DELETE** `/hr/managers/{manager_id}`

Deactivate manager account.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Manager account deactivated"
}
```

---

### 3.3 Module Distribution

#### 3.3.1 Send Module to Employee
**POST** `/hr/modules/send`

Send a specific form/module to an employee.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "employee_id": "employee_uuid",
  "module_type": "w4_update",
  "reason": "Annual tax form update required",
  "expires_in_days": 7,
  "initial_data": {
    "prefilled_field": "value"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "module_id": "uuid",
    "token": "module_token_xyz",
    "access_url": "https://onboarding.hotel.com/module/module_token_xyz",
    "expires_at": "2025-01-21T00:00:00Z",
    "email_sent": true
  }
}
```

---

#### 3.3.2 Bulk Send Modules
**POST** `/hr/modules/bulk-send`

Send modules to multiple employees.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "employee_ids": ["emp_uuid_1", "emp_uuid_2", "emp_uuid_3"],
  "module_type": "trafficking_training",
  "reason": "Annual human trafficking awareness training",
  "expires_in_days": 30
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sent_count": 3,
    "failed_count": 0,
    "modules": [
      {
        "employee_id": "emp_uuid_1",
        "module_id": "mod_uuid_1",
        "status": "sent"
      }
    ]
  }
}
```

---

#### 3.3.3 Get Module Status
**GET** `/hr/modules/status`

Track module completion status.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `property_id` (uuid): Filter by property
- `module_type` (string): Filter by module type
- `status` (string): pending|completed|expired

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "modules": [
      {
        "id": "uuid",
        "employee": {
          "id": "emp_uuid",
          "first_name": "John",
          "last_name": "Doe",
          "email": "john.doe@email.com"
        },
        "module_type": "w4_update",
        "status": "pending",
        "created_at": "2025-01-14T00:00:00Z",
        "expires_at": "2025-01-21T00:00:00Z",
        "completed_at": null,
        "reminder_count": 1,
        "last_reminder_at": "2025-01-17T00:00:00Z"
      }
    ]
  }
}
```

---

#### 3.3.4 Send Reminder
**POST** `/hr/modules/{module_id}/remind`

Send reminder email for pending module.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Reminder sent successfully"
}
```

---

### 3.4 Analytics & Reporting

#### 3.4.1 Dashboard Statistics
**GET** `/hr/dashboard-stats`

Get system-wide statistics.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "properties": {
      "total": 10,
      "active": 9
    },
    "managers": {
      "total": 25,
      "active": 23
    },
    "employees": {
      "total": 450,
      "active": 420,
      "onboarding": 15
    },
    "applications": {
      "pending": 8,
      "this_week": 12,
      "this_month": 45
    },
    "compliance": {
      "upcoming_deadlines": 3,
      "overdue": 0
    },
    "modules": {
      "pending": 25,
      "completed_today": 5
    }
  }
}
```

---

#### 3.4.2 Compliance Report
**GET** `/hr/reports/compliance`

Get compliance status report.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `property_id` (uuid): Filter by property
- `date_from` (date): Start date
- `date_to` (date): End date

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "i9_compliance": {
      "compliant": 445,
      "pending_section1": 3,
      "pending_section2": 2,
      "expired": 0
    },
    "w4_status": {
      "current_year": 440,
      "needs_update": 10
    },
    "training": {
      "trafficking_complete": 430,
      "trafficking_pending": 20
    }
  }
}
```

---

## 4. Manager Endpoints

### 4.1 Dashboard
**GET** `/manager/dashboard`

Get manager's property-specific dashboard.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "property": {
      "id": "uuid",
      "name": "Grand Hotel Downtown"
    },
    "statistics": {
      "applications_pending": 3,
      "onboarding_active": 2,
      "employees_total": 45,
      "compliance_alerts": 1
    },
    "recent_applications": [
      {
        "id": "app_uuid",
        "applicant_name": "Jane Doe",
        "position": "Front Desk",
        "applied_at": "2025-01-13T00:00:00Z"
      }
    ],
    "upcoming_deadlines": [
      {
        "employee": "John Smith",
        "requirement": "I-9 Section 2",
        "due_date": "2025-01-16T00:00:00Z"
      }
    ]
  }
}
```

---

### 4.2 Application Management

#### 4.2.1 Get Applications
**GET** `/manager/applications`

Get job applications for manager's property.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `property_id` (uuid): Required - Property ID
- `status` (string): pending|approved|rejected

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "applications": [
      {
        "id": "app_uuid",
        "property_id": "prop_uuid",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@email.com",
        "phone": "555-0100",
        "position": "Front Desk",
        "department": "Guest Services",
        "status": "pending",
        "applied_at": "2025-01-13T00:00:00Z",
        "resume_url": "https://storage.url/resume.pdf"
      }
    ]
  }
}
```

---

#### 4.2.2 Approve Application
**POST** `/manager/applications/{application_id}/approve`

Approve application and generate onboarding token.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "start_date": "2025-01-20",
  "pay_rate": 15.50,
  "employment_type": "full_time",
  "notes": "Strong candidate, bilingual"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "employee_id": "emp_uuid",
    "onboarding_token": "onb_token_xyz",
    "onboarding_url": "https://onboarding.hotel.com/onboard?token=onb_token_xyz",
    "expires_at": "2025-01-21T00:00:00Z",
    "email_sent": true
  }
}
```

---

#### 4.2.3 Reject Application
**POST** `/manager/applications/{application_id}/reject`

Reject application with option for talent pool.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "reason": "Position filled",
  "add_to_talent_pool": true,
  "talent_pool_notes": "Consider for future openings"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Application rejected and added to talent pool"
}
```

---

### 4.3 Onboarding Management

#### 4.3.1 Get Onboarding Sessions
**GET** `/manager/onboarding`

Get active onboarding sessions for property.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `property_id` (uuid): Required - Property ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "session_uuid",
        "employee": {
          "id": "emp_uuid",
          "first_name": "John",
          "last_name": "Doe",
          "email": "john.doe@email.com"
        },
        "status": "in_progress",
        "percent_complete": 75,
        "current_step": "i9_section1",
        "started_at": "2025-01-14T00:00:00Z",
        "last_activity_at": "2025-01-14T10:00:00Z",
        "manager_review_required": true
      }
    ]
  }
}
```

---

#### 4.3.2 Complete I-9 Section 2
**POST** `/manager/i9-section2/{employee_id}`

Complete employer verification for I-9.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "document_title": "Driver's License",
  "issuing_authority": "State of New York",
  "document_number": "123456789",
  "expiration_date": "2028-01-01",
  "additional_document": {
    "title": "Social Security Card",
    "issuing_authority": "SSA",
    "document_number": "***-**-1234"
  },
  "attestation": {
    "employee_first_day": "2025-01-20",
    "verification_date": "2025-01-20",
    "employer_name": "Grand Hotel Downtown",
    "employer_title": "HR Manager"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "i9_completed": true,
    "pdf_url": "https://storage.url/i9_completed.pdf"
  }
}
```

---

#### 4.3.3 Request Employee Correction
**POST** `/manager/onboarding/{session_id}/request-correction`

Request employee to correct specific form.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "step_id": "personal_info",
  "reason": "Address verification needed",
  "specific_fields": ["address", "zip_code"],
  "message": "Please verify your current address matches your ID"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Correction request sent to employee"
}
```

---

## 5. Employee Endpoints

### 5.1 Onboarding Access
**GET** `/onboarding/validate-token`

Validate onboarding token and get session info.

**Query Parameters:**
- `token` (string): Onboarding token

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "employee": {
      "id": "emp_uuid",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@email.com"
    },
    "property": {
      "id": "prop_uuid",
      "name": "Grand Hotel Downtown"
    },
    "position": "Front Desk",
    "expires_at": "2025-01-21T00:00:00Z"
  }
}
```

---

### 5.2 Module Access
**GET** `/module/{token}`

Access specific module form.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "module_type": "w4_update",
    "expires_at": "2025-01-21T00:00:00Z",
    "form_data": {
      "current_values": {
        "filing_status": "single",
        "allowances": 1
      },
      "form_fields": {
        // Form configuration
      }
    }
  }
}
```

---

### 5.3 Submit Module
**POST** `/module/{token}/submit`

Submit completed module form.

**Request Body:**
```json
{
  "form_data": {
    "filing_status": "married",
    "allowances": 2,
    "additional_withholding": 50
  },
  "signature": {
    "data": "base64_signature_image",
    "timestamp": "2025-01-14T10:00:00Z",
    "ip_address": "192.168.1.1"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "completed": true,
    "pdf_url": "https://storage.url/completed_form.pdf",
    "message": "Form submitted successfully"
  }
}
```

---

## 6. Public Endpoints

### 6.1 Job Application
**POST** `/apply/{property_id}`

Submit job application (no auth required).

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@email.com",
  "phone": "555-0100",
  "position": "Front Desk",
  "availability": {
    "start_date": "2025-02-01",
    "shift_preference": "any"
  },
  "resume": "base64_encoded_file",
  "cover_letter": "I am interested in..."
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "application_id": "app_uuid",
    "message": "Application submitted successfully"
  }
}
```

---

## 7. Error Response Format

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details if applicable
    },
    "timestamp": "2025-01-14T10:00:00Z"
  }
}
```

### Common Error Codes:
- `UNAUTHORIZED`: Invalid or missing authentication
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Input validation failed
- `DUPLICATE_ENTRY`: Resource already exists
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

---

## 8. Rate Limiting

| Endpoint Type | Rate Limit | Window |
|--------------|------------|---------|
| Authentication | 5 requests | 1 minute |
| Read Operations | 100 requests | 1 minute |
| Write Operations | 30 requests | 1 minute |
| Bulk Operations | 5 requests | 5 minutes |

---

## 9. Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `sort_by` (string): Field to sort by
- `sort_order` (string): asc|desc

**Response includes:**
```json
{
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 10. API Versioning

The API uses URL versioning. Current version: v1

Future versions will be available at:
- `/api/v2/...`
- `/api/v3/...`

Deprecated endpoints will include a `Deprecation` header with sunset date.

---

*End of API Endpoints Documentation*