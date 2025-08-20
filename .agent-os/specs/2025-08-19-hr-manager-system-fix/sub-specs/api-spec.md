# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-19-hr-manager-system-fix/spec.md

## Endpoints

### POST /api/hr/properties

**Purpose:** Create a new property
**Parameters:** 
- Body: `{ name, address, city, state, zip_code, phone }`
**Response:** 
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "string",
    "address": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "phone": "string",
    "is_active": true,
    "created_at": "timestamp"
  }
}
```
**Errors:** 400 (validation), 401 (unauthorized), 409 (duplicate)

### PUT /api/hr/properties/{id}

**Purpose:** Update an existing property
**Parameters:**
- Path: `id` (UUID)
- Body: Partial property object
**Response:** Updated property object
**Errors:** 400 (validation), 401 (unauthorized), 404 (not found)

### POST /api/hr/managers

**Purpose:** Create a new manager account
**Parameters:**
```json
{
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "property_id": "uuid",
  "send_welcome_email": true
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "string",
    "temporary_password": "string",
    "first_name": "string",
    "last_name": "string",
    "role": "manager",
    "property": {
      "id": "uuid",
      "name": "string"
    }
  }
}
```
**Errors:** 400 (validation), 401 (unauthorized), 409 (email exists)

### POST /api/hr/managers/{id}/assign-property

**Purpose:** Assign manager to additional property
**Parameters:**
- Path: `id` (manager UUID)
- Body: `{ property_id: "uuid" }`
**Response:** Updated manager with properties list
**Errors:** 400 (already assigned), 404 (not found)

### DELETE /api/hr/managers/{id}/properties/{property_id}

**Purpose:** Remove manager from property
**Parameters:**
- Path: `id` (manager UUID), `property_id` (UUID)
**Response:** 204 No Content
**Errors:** 404 (not found)

### GET /api/manager/applications

**Purpose:** Get applications for manager's properties
**Parameters:**
- Query: `status` (optional), `property_id` (optional)
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "property_id": "uuid",
      "applicant_name": "string",
      "position": "string",
      "department": "string",
      "status": "pending|approved|rejected",
      "applied_at": "timestamp"
    }
  ]
}
```
**Errors:** 401 (unauthorized)

### POST /api/manager/applications/{id}/review

**Purpose:** Review and approve/reject application
**Parameters:**
- Path: `id` (application UUID)
- Body:
```json
{
  "action": "approve|reject|request_info",
  "comments": "string",
  "approval_details": {
    "pay_rate": 25.00,
    "pay_frequency": "hourly",
    "start_date": "2025-09-01",
    "start_time": "09:00",
    "supervisor_name": "string",
    "special_instructions": "string"
  }
}
```
**Response:** 
```json
{
  "success": true,
  "data": {
    "application_id": "uuid",
    "status": "approved",
    "onboarding_token": "string",
    "onboarding_url": "string"
  }
}
```
**Errors:** 400 (validation), 401 (unauthorized), 404 (not found)

### POST /api/manager/i9/section2

**Purpose:** Complete I-9 Section 2 employer verification
**Parameters:**
```json
{
  "employee_id": "uuid",
  "document_type": "passport|drivers_license_and_ss",
  "document_number": "string",
  "document_expiry": "2026-01-01",
  "issuing_authority": "string",
  "employer_name": "string",
  "employer_title": "string",
  "signature_data": "base64_string"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "employee_id": "uuid",
    "completed_at": "timestamp",
    "pdf_url": "string"
  }
}
```
**Errors:** 400 (validation), 401 (unauthorized), 409 (already completed)

### GET /api/manager/i9/pending

**Purpose:** Get list of employees needing I-9 Section 2
**Response:** List of employees with Section 1 complete but Section 2 pending
**Errors:** 401 (unauthorized)

## Authentication

All endpoints require JWT Bearer token in Authorization header:
```
Authorization: Bearer <token>
```

HR endpoints require `role: "hr"`
Manager endpoints require `role: "manager"`

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per IP

## Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "status_code": 400,
  "timestamp": "2025-08-19T00:00:00Z",
  "details": {}
}
```