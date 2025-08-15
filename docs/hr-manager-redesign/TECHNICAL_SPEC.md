# Technical Specification
## Hotel Employee Onboarding System - HR & Manager Module Redesign

### Document Version
- **Version**: 1.0
- **Date**: January 2025
- **Status**: Technical Design
- **Related**: PRD.md

---

## 1. Technology Stack

### 1.1 Backend
- **Framework**: FastAPI 0.100+
- **Language**: Python 3.12+
- **Database**: Supabase (PostgreSQL 15+)
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio
- **Documentation**: OpenAPI/Swagger

### 1.2 Frontend
- **Framework**: React 18+
- **Language**: TypeScript 5.x
- **Build Tool**: Vite 5.x
- **State Management**: React Context + React Query
- **UI Components**: shadcn/ui + Radix UI
- **Forms**: React Hook Form + Zod
- **Styling**: Tailwind CSS 3.x
- **Testing**: Jest + React Testing Library

### 1.3 Infrastructure
- **Hosting**: TBD (Docker-ready)
- **Database**: Supabase Cloud
- **File Storage**: Supabase Storage
- **Email**: SendGrid/Resend
- **Monitoring**: TBD
- **CI/CD**: GitHub Actions

---

## 2. System Architecture

### 2.1 Architecture Pattern
```
┌─────────────────────────────────────────────────────┐
│                   Frontend Layer                     │
├─────────────────┬──────────────┬───────────────────┤
│   HR Dashboard  │Manager Dashboard│ Employee Portal │
│   /hr/*        │  /manager/*     │  /onboard       │
└─────────────────┴──────────────┴───────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  API Gateway                         │
│               FastAPI Application                    │
├─────────────────────────────────────────────────────┤
│  Authentication │  Authorization │  Rate Limiting   │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                 Service Layer                        │
├──────────────┬──────────────┬──────────────────────┤
│  HR Service  │Manager Service│ Employee Service    │
└──────────────┴──────────────┴──────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                 Data Access Layer                    │
│              Supabase Service Client                 │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  Database Layer                      │
│            PostgreSQL with Row Level Security        │
└─────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant S as Service
    participant D as Database
    
    U->>F: Login Request
    F->>A: POST /api/auth/login
    A->>S: Validate Credentials
    S->>D: Query User
    D-->>S: User Data
    S-->>A: Generate JWT
    A-->>F: JWT Token
    F-->>U: Dashboard Access
```

---

## 3. Authentication & Authorization

### 3.1 Authentication Flow

#### 3.1.1 JWT Token Structure
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "hr|manager|employee",
  "properties": ["property_id_1", "property_id_2"],
  "exp": 1234567890,
  "iat": 1234567890,
  "jti": "unique_token_id"
}
```

#### 3.1.2 Token Management
```python
class TokenManager:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS = 24
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    @staticmethod
    def create_access_token(user_data: dict) -> str:
        expires = datetime.utcnow() + timedelta(hours=24)
        payload = {
            **user_data,
            "exp": expires,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4())
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

### 3.2 Authorization Middleware

#### 3.2.1 Role-Based Access Control
```python
def require_role(allowed_roles: List[str]):
    async def verify(token: str = Depends(oauth2_scheme)):
        payload = verify_token(token)
        if payload.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return payload
    return verify

# Usage
@app.get("/api/hr/properties")
async def get_properties(user=Depends(require_role(["hr"]))):
    pass
```

#### 3.2.2 Property Access Control
```python
def require_property_access(property_id: str):
    async def verify(user=Depends(get_current_user)):
        if user.role == "hr":
            return True  # HR has access to all properties
        if property_id not in user.properties:
            raise HTTPException(status_code=403, detail="Property access denied")
        return True
    return verify
```

---

## 4. API Design

### 4.1 API Structure
```
/api
├── /auth
│   ├── POST   /login
│   ├── POST   /logout
│   ├── POST   /refresh
│   └── GET    /me
├── /setup
│   └── POST   /hr-admin
├── /hr
│   ├── /properties
│   │   ├── GET    /
│   │   ├── POST   /
│   │   ├── PUT    /{id}
│   │   └── DELETE /{id}
│   ├── /managers
│   │   ├── GET    /
│   │   ├── POST   /
│   │   ├── PUT    /{id}
│   │   └── DELETE /{id}
│   └── /modules
│       ├── POST   /send
│       ├── GET    /status
│       └── POST   /bulk-send
├── /manager
│   ├── GET    /dashboard
│   ├── GET    /applications
│   ├── POST   /applications/{id}/approve
│   └── POST   /i9-section2/{id}
└── /employee
    └── GET    /module/{token}
```

### 4.2 Request/Response Models

#### 4.2.1 Authentication Models
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo

class UserInfo(BaseModel):
    id: str
    email: str
    role: str
    first_name: str
    last_name: str
    properties: List[str] = []
```

#### 4.2.2 Property Models
```python
class PropertyCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str

class PropertyResponse(BaseModel):
    id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    manager_count: int
    employee_count: int
    created_at: datetime
    updated_at: Optional[datetime]
```

### 4.3 Error Handling

#### 4.3.1 Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "PROPERTY_NOT_FOUND",
    "message": "Property with ID 'xyz' not found",
    "details": {},
    "timestamp": "2025-01-14T10:00:00Z"
  }
}
```

#### 4.3.2 Error Codes
```python
class ErrorCode(Enum):
    # Authentication Errors (401)
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    
    # Authorization Errors (403)
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    PROPERTY_ACCESS_DENIED = "PROPERTY_ACCESS_DENIED"
    
    # Resource Errors (404)
    USER_NOT_FOUND = "USER_NOT_FOUND"
    PROPERTY_NOT_FOUND = "PROPERTY_NOT_FOUND"
    
    # Validation Errors (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DUPLICATE_EMAIL = "DUPLICATE_EMAIL"
    
    # Server Errors (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
```

---

## 5. Database Design

### 5.1 Core Tables

#### 5.1.1 Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('hr', 'manager', 'employee')),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

#### 5.1.2 Properties Table
```sql
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_properties_active ON properties(is_active);
```

#### 5.1.3 Property Managers Table
```sql
CREATE TABLE property_managers (
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (property_id, user_id)
);

CREATE INDEX idx_property_managers_user ON property_managers(user_id);
```

### 5.2 Module Distribution Tables

#### 5.2.1 Employee Modules Table
```sql
CREATE TABLE employee_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL,
    module_type VARCHAR(50) NOT NULL,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason TEXT,
    form_data JSONB,
    reminder_sent_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_employee_modules_token ON employee_modules(token);
CREATE INDEX idx_employee_modules_employee ON employee_modules(employee_id);
CREATE INDEX idx_employee_modules_expires ON employee_modules(expires_at);
```

### 5.3 Row Level Security (RLS)

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_managers ENABLE ROW LEVEL SECURITY;

-- HR can see all users
CREATE POLICY hr_users_policy ON users
    FOR ALL
    TO authenticated
    USING (
        auth.jwt() ->> 'role' = 'hr'
        OR id = (auth.jwt() ->> 'sub')::uuid
    );

-- Managers can only see their property's data
CREATE POLICY manager_property_policy ON properties
    FOR SELECT
    TO authenticated
    USING (
        auth.jwt() ->> 'role' = 'hr'
        OR id IN (
            SELECT property_id FROM property_managers
            WHERE user_id = (auth.jwt() ->> 'sub')::uuid
        )
    );
```

---

## 6. Frontend Architecture

### 6.1 Folder Structure
```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── SetupForm.tsx
│   ├── common/
│   │   ├── Layout.tsx
│   │   ├── Header.tsx
│   │   └── LoadingSpinner.tsx
│   └── ui/
│       └── [shadcn components]
├── contexts/
│   ├── AuthContext.tsx
│   └── ThemeContext.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useApi.ts
│   └── usePropertyAccess.ts
├── pages/
│   ├── auth/
│   │   ├── LoginPage.tsx
│   │   └── SetupPage.tsx
│   ├── hr/
│   │   ├── HRDashboard.tsx
│   │   ├── PropertyManagement.tsx
│   │   ├── ManagerManagement.tsx
│   │   └── ModuleDistribution.tsx
│   └── manager/
│       ├── ManagerDashboard.tsx
│       ├── ApplicationReview.tsx
│       └── OnboardingTracking.tsx
├── services/
│   ├── api.ts
│   ├── auth.service.ts
│   └── storage.service.ts
├── types/
│   ├── auth.types.ts
│   ├── property.types.ts
│   └── module.types.ts
└── utils/
    ├── constants.ts
    ├── validators.ts
    └── formatters.ts
```

### 6.2 State Management

#### 6.2.1 Auth Context
```typescript
interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider: FC<PropsWithChildren> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Implementation
};
```

#### 6.2.2 API Service with React Query
```typescript
// Custom hook for API calls
export const useProperties = () => {
  return useQuery({
    queryKey: ['properties'],
    queryFn: PropertyService.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Mutation for creating property
export const useCreateProperty = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: PropertyService.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['properties']);
    },
  });
};
```

### 6.3 Component Patterns

#### 6.3.1 Protected Route Component
```typescript
export const ProtectedRoute: FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return <LoadingSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" />;
  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" />;
  }
  
  return <>{children}</>;
};
```

#### 6.3.2 Form Component Pattern
```typescript
export const PropertyForm: FC<PropertyFormProps> = ({ 
  onSubmit, 
  initialValues 
}) => {
  const form = useForm<PropertyFormData>({
    resolver: zodResolver(propertySchema),
    defaultValues: initialValues,
  });
  
  const handleSubmit = async (data: PropertyFormData) => {
    try {
      await onSubmit(data);
      toast.success('Property saved successfully');
    } catch (error) {
      toast.error('Failed to save property');
    }
  };
  
  return (
    <Form {...form}>
      {/* Form fields */}
    </Form>
  );
};
```

---

## 7. Security Implementation

### 7.1 Security Headers
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hotel-onboarding.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["hotel-onboarding.com", "*.hotel-onboarding.com"]
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

### 7.2 Input Validation
```python
class PropertyCreateSchema(BaseModel):
    name: constr(min_length=1, max_length=255)
    address: constr(min_length=1, max_length=255)
    city: constr(min_length=1, max_length=100)
    state: constr(regex="^[A-Z]{2}$")
    zip_code: constr(regex="^\\d{5}(-\\d{4})?$")
    phone: constr(regex="^\\+?1?\\d{10,14}$")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or v.isspace():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

### 7.3 Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/auth/login")
@limiter.limit("5 per minute")
async def login(request: Request, credentials: LoginRequest):
    pass
```

---

## 8. Testing Strategy

### 8.1 Backend Testing

#### 8.1.1 Unit Tests
```python
# test_auth_service.py
import pytest
from app.services.auth_service import AuthService

@pytest.fixture
def auth_service():
    return AuthService()

def test_create_token(auth_service):
    user_data = {"id": "123", "role": "hr"}
    token = auth_service.create_token(user_data)
    assert token is not None
    assert len(token) > 0

def test_verify_token(auth_service):
    user_data = {"id": "123", "role": "hr"}
    token = auth_service.create_token(user_data)
    payload = auth_service.verify_token(token)
    assert payload["id"] == "123"
    assert payload["role"] == "hr"
```

#### 8.1.2 Integration Tests
```python
# test_api_endpoints.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    response = client.post("/api/auth/login", json={
        "email": "hr@test.com",
        "password": "Test123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_property_access_denied():
    # Login as manager
    login_response = client.post("/api/auth/login", json={
        "email": "manager@test.com",
        "password": "Test123!"
    })
    token = login_response.json()["access_token"]
    
    # Try to access other property
    response = client.get(
        "/api/manager/applications",
        headers={"Authorization": f"Bearer {token}"},
        params={"property_id": "other-property-id"}
    )
    assert response.status_code == 403
```

### 8.2 Frontend Testing

#### 8.2.1 Component Tests
```typescript
// PropertyForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { PropertyForm } from './PropertyForm';

describe('PropertyForm', () => {
  it('validates required fields', async () => {
    const onSubmit = jest.fn();
    render(<PropertyForm onSubmit={onSubmit} />);
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      expect(onSubmit).not.toHaveBeenCalled();
    });
  });
  
  it('submits valid form data', async () => {
    const onSubmit = jest.fn();
    render(<PropertyForm onSubmit={onSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: 'Test Hotel' }
    });
    // Fill other fields...
    
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Test Hotel'
        })
      );
    });
  });
});
```

---

## 9. Performance Optimization

### 9.1 Backend Optimizations
- Connection pooling with 50 max connections
- Database query optimization with proper indexes
- Async/await for all I/O operations
- Response caching for frequently accessed data
- Pagination on all list endpoints

### 9.2 Frontend Optimizations
- Code splitting with React.lazy()
- React Query for efficient data fetching and caching
- Virtual scrolling for large lists
- Image optimization with next-gen formats
- Bundle size optimization with tree shaking

---

## 10. Monitoring & Logging

### 10.1 Application Logging
```python
import logging
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Log all API requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info({
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration": duration,
        "user_id": request.state.user_id if hasattr(request.state, "user_id") else None
    })
    
    return response
```

### 10.2 Error Tracking
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development")
)
```

---

## 11. Deployment Configuration

### 11.1 Docker Configuration
```dockerfile
# Backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.2 Environment Variables
```bash
# .env.production
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=your-secret-key-here
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_KEY=xxx
FRONTEND_URL=https://hotel-onboarding.com
EMAIL_API_KEY=xxx
SENTRY_DSN=xxx
ENVIRONMENT=production
SECRET_KEY=hr-setup-secret-key
```

---

*End of Technical Specification*