# Backend-Frontend Integration Fix Design

## Overview

This design addresses the critical integration issues identified between the hotel onboarding system's backend API and frontend application. The solution focuses on standardizing API contracts, fixing authentication flows, ensuring data consistency, and implementing robust error handling to provide a seamless user experience for HR administrators, property managers, and job applicants.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (Supabase)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│ Email Service   │              │
                        │ (SMTP/SendGrid) │              │
                        └─────────────────┘              │
                                 │                       │
                        ┌─────────────────┐              │
                        │ Logging/Monitor │              │
                        │ (Structured)    │              │
                        └─────────────────┘              │
```

### Integration Layer Design

```
Frontend Components
├── AuthContext (Standardized)
├── API Service Layer
│   ├── BaseAPIClient
│   ├── AuthService
│   ├── HRService
│   ├── ManagerService
│   └── ApplicationService
└── Error Handling
    ├── ErrorBoundary
    ├── APIErrorHandler
    └── NotificationService

Backend API
├── Authentication Middleware
├── Authorization Middleware
├── Validation Middleware
├── Error Handling Middleware
├── Logging Middleware
└── CORS Middleware
```

## Components and Interfaces

### 1. Authentication System Redesign

#### Backend Authentication Service
```python
class AuthenticationService:
    def authenticate_user(email: str, password: str) -> AuthResult
    def generate_tokens(user: User) -> TokenPair
    def refresh_token(refresh_token: str) -> TokenPair
    def validate_token(token: str) -> TokenValidation
    def revoke_token(token: str) -> bool
```

#### Frontend Auth Context
```typescript
interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) -> Promise<void>
  logout: () -> void
  refreshToken: () -> Promise<void>
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}
```

#### Standardized Auth Response
```json
{
  "success": true,
  "token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "role": "hr|manager",
    "first_name": "John",
    "last_name": "Doe",
    "property_id": "property_id" // for managers only
  },
  "expires_at": "2024-01-01T00:00:00Z",
  "token_type": "Bearer"
}
```

### 2. API Client Standardization

#### Base API Client
```typescript
class BaseAPIClient {
  private baseURL: string
  private authToken: string | null
  
  constructor(baseURL: string)
  setAuthToken(token: string): void
  get<T>(endpoint: string, params?: object): Promise<APIResponse<T>>
  post<T>(endpoint: string, data?: object): Promise<APIResponse<T>>
  put<T>(endpoint: string, data?: object): Promise<APIResponse<T>>
  delete<T>(endpoint: string): Promise<APIResponse<T>>
  
  private handleResponse<T>(response: Response): Promise<APIResponse<T>>
  private handleError(error: any): APIError
}
```

#### Standardized API Response
```typescript
interface APIResponse<T> {
  success: boolean
  data: T
  message?: string
  errors?: ValidationError[]
  pagination?: PaginationMeta
}

interface APIError {
  success: false
  error: string
  error_code: string
  details?: object
  status_code: number
}
```

### 3. Endpoint Standardization

#### URL Pattern Consistency
```
Current Issues:
- Frontend: /applications/${id}/approve
- Backend: /applications/{application_id}/approve

Standardized Pattern:
- All endpoints use {id} format
- Frontend uses template literals: `/applications/${id}/approve`
- Backend uses FastAPI path parameters: /applications/{id}/approve
```

#### Required Endpoint Mappings
```python
# Authentication Endpoints
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /auth/me

# HR Endpoints
GET  /hr/dashboard-stats
GET  /hr/properties
POST /hr/properties
PUT  /hr/properties/{id}
DELETE /hr/properties/{id}
GET  /hr/applications
GET  /hr/applications/{id}/history
GET  /hr/managers
POST /hr/managers
PUT  /hr/managers/{id}
DELETE /hr/managers/{id}

# Manager Endpoints
GET  /manager/property
GET  /manager/applications
GET  /manager/dashboard-stats

# Application Endpoints
GET  /properties/{id}/info
POST /apply/{property_id}
POST /applications/{id}/approve
POST /applications/{id}/reject
GET  /applications/{id}/history

# Bulk Operations
POST /hr/applications/bulk-action
POST /hr/applications/bulk-status-update
POST /hr/applications/bulk-reactivate
```

### 4. Data Models Standardization

#### User Model
```typescript
interface User {
  id: string
  email: string
  role: 'hr' | 'manager'
  first_name: string
  last_name: string
  is_active: boolean
  created_at: string
  property_id?: string // for managers
}
```

#### Property Model
```typescript
interface Property {
  id: string
  name: string
  address: string
  city: string
  state: string
  zip_code: string
  phone?: string
  manager_ids: string[]
  qr_code_url: string
  is_active: boolean
  created_at: string
}
```

#### Application Model
```typescript
interface JobApplication {
  id: string
  property_id: string
  property_name?: string
  department: string
  position: string
  applicant_data: {
    first_name: string
    last_name: string
    email: string
    phone: string
    [key: string]: any
  }
  status: 'pending' | 'approved' | 'rejected' | 'talent_pool'
  applied_at: string
  reviewed_by?: string
  reviewed_at?: string
  rejection_reason?: string
}
```

### 5. Error Handling System

#### Backend Error Middleware
```python
class ErrorHandlingMiddleware:
    def handle_validation_error(self, exc: ValidationException) -> JSONResponse
    def handle_authentication_error(self, exc: AuthException) -> JSONResponse
    def handle_authorization_error(self, exc: AuthzException) -> JSONResponse
    def handle_not_found_error(self, exc: NotFoundException) -> JSONResponse
    def handle_server_error(self, exc: Exception) -> JSONResponse
```

#### Standardized Error Responses
```json
{
  "success": false,
  "error": "Validation failed",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field_errors": {
      "email": ["Email is required"],
      "password": ["Password must be at least 8 characters"]
    }
  },
  "status_code": 422
}
```

#### Frontend Error Handler
```typescript
class APIErrorHandler {
  static handle(error: APIError): void {
    switch (error.error_code) {
      case 'VALIDATION_ERROR':
        this.handleValidationError(error)
        break
      case 'AUTHENTICATION_ERROR':
        this.handleAuthError(error)
        break
      case 'AUTHORIZATION_ERROR':
        this.handleAuthzError(error)
        break
      default:
        this.handleGenericError(error)
    }
  }
}
```

## Data Models

### Authentication Flow
```
1. User submits credentials
2. Backend validates against Supabase
3. Generate JWT with proper claims
4. Return standardized auth response
5. Frontend stores token and user data
6. Include token in all subsequent requests
7. Handle token refresh automatically
8. Proper logout and token cleanup
```

### Application Workflow
```
1. Applicant accesses property info (public endpoint)
2. Submits application with validation
3. Manager receives notification
4. Manager reviews and approves/rejects
5. System sends email notification
6. If approved: create employee record and onboarding
7. If rejected: move to talent pool
8. Update application status and notify stakeholders
```

### Data Consistency Strategy
```
1. Single source of truth in Supabase
2. Consistent data models across all endpoints
3. Proper foreign key relationships
4. Atomic transactions for related operations
5. Data validation at API boundary
6. Audit logging for all changes
```

## Error Handling

### HTTP Status Code Standards
```
200 OK - Successful GET, PUT operations
201 Created - Successful POST operations
204 No Content - Successful DELETE operations
400 Bad Request - Invalid request format
401 Unauthorized - Authentication required
403 Forbidden - Insufficient permissions
404 Not Found - Resource doesn't exist
422 Unprocessable Entity - Validation errors
429 Too Many Requests - Rate limiting
500 Internal Server Error - Server errors
```

### Error Response Format
```json
{
  "success": false,
  "error": "Human readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "details": {
    "field_errors": {},
    "context": {},
    "trace_id": "uuid"
  },
  "status_code": 422,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Frontend Error Handling Strategy
```typescript
// Global error handler
const handleAPIError = (error: APIError) => {
  // Log error for debugging
  console.error('API Error:', error)
  
  // Show user-friendly message
  switch (error.error_code) {
    case 'AUTHENTICATION_ERROR':
      // Redirect to login
      authContext.logout()
      break
    case 'VALIDATION_ERROR':
      // Show field-specific errors
      showValidationErrors(error.details.field_errors)
      break
    default:
      // Show generic error toast
      showErrorToast(error.error)
  }
}
```

## Testing Strategy

### Integration Testing
```python
class IntegrationTestSuite:
    def test_authentication_flow(self)
    def test_hr_dashboard_data(self)
    def test_manager_dashboard_data(self)
    def test_application_workflow(self)
    def test_error_handling(self)
    def test_data_consistency(self)
```

### Frontend Testing
```typescript
// API integration tests
describe('API Integration', () => {
  test('authentication flow works correctly')
  test('HR dashboard loads all required data')
  test('manager dashboard shows property-specific data')
  test('application submission and approval workflow')
  test('error handling displays appropriate messages')
})
```

### End-to-End Testing
```
1. User login flow (HR and Manager)
2. Property management (create, update, delete)
3. Manager assignment workflow
4. Application submission and processing
5. Email notification delivery
6. Error scenarios and recovery
```

## Security Considerations

### Authentication Security
- JWT tokens with appropriate expiration
- Secure token storage (httpOnly cookies recommended)
- Token refresh mechanism
- Proper logout and token cleanup
- Rate limiting on auth endpoints

### Authorization Security
- Role-based access control (RBAC)
- Property-based data isolation for managers
- API endpoint protection
- Input validation and sanitization
- SQL injection prevention

### Data Security
- HTTPS enforcement
- Sensitive data encryption
- Audit logging
- CORS configuration
- Request/response logging (excluding sensitive data)

## Performance Optimization

### Backend Optimizations
- Database query optimization
- Response caching where appropriate
- Pagination for large datasets
- Async processing for heavy operations
- Connection pooling

### Frontend Optimizations
- API response caching
- Debounced search requests
- Lazy loading of components
- Error boundary implementation
- Loading states and skeleton screens

## Monitoring and Logging

### Backend Monitoring
```python
# Structured logging
logger.info("API request", extra={
    "endpoint": "/hr/applications",
    "method": "GET",
    "user_id": user.id,
    "response_time": 0.123,
    "status_code": 200
})
```

### Health Check Endpoints
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "database": await check_database_health(),
            "email": await check_email_service_health()
        }
    }
```

### Error Tracking
- Centralized error logging
- Error rate monitoring
- Performance metrics
- User session tracking
- API usage analytics