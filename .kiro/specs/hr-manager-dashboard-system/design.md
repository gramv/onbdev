# Design Document

## Overview

The HR and Manager Dashboard System provides a professional, role-based administrative interface for managing hotel properties, staff, and applications. The system uses a clean, modern design with React/TypeScript frontend and FastAPI backend, leveraging existing UI components for consistency.

## Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript and Vite
- **UI Library**: Existing shadcn/ui components (Card, Button, Input, Tabs, etc.)
- **State Management**: React hooks with Context API for authentication
- **Routing**: React Router for navigation
- **HTTP Client**: Axios for API communication
- **Styling**: Tailwind CSS with existing design system

### Backend Architecture
- **Framework**: FastAPI with Python 3.12+
- **Authentication**: JWT tokens with role-based access control
- **Database**: In-memory storage (existing structure)
- **API Design**: RESTful endpoints with proper HTTP status codes
- **Validation**: Pydantic models for request/response validation

### Design Principles
- **Consistency**: Use existing UI components and patterns
- **Simplicity**: Clean, professional interface without clutter
- **Responsiveness**: Mobile-friendly design
- **Performance**: Efficient data loading and updates
- **Accessibility**: Proper labels, focus management, keyboard navigation

## Components and Interfaces

### 1. Authentication System

#### Login Page Component
```typescript
interface LoginPageProps {
  role?: 'hr' | 'manager'
}

interface LoginFormData {
  email: string
  password: string
}
```

**Features:**
- Clean login form with email/password fields
- Role-specific branding (HR Portal vs Manager Portal)
- Form validation with error display
- Loading states during authentication
- Redirect to appropriate dashboard after login

#### Authentication Context
```typescript
interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
}
```

### 2. HR Dashboard Components

#### Main HR Dashboard Layout
```typescript
interface HRDashboardProps {
  user: User
}

interface DashboardTab {
  id: string
  label: string
  component: React.ComponentType
}
```

**Tab Structure:**
- Properties: Property management interface
- Managers: Manager assignment and oversight
- Employees: Employee directory and management
- Applications: Job application review system
- Analytics: System metrics and reporting

#### Property Management Component
```typescript
interface Property {
  id: string
  name: string
  address: string
  city: string
  state: string
  zip_code: string
  phone: string
  manager_ids: string[]
  qr_code_url: string
  created_at: string
}

interface PropertyFormData {
  name: string
  address: string
  city: string
  state: string
  zip_code: string
  phone: string
}
```

**Features:**
- Property creation form with validation
- Property list with edit/delete actions
- QR code generation for applications
- Manager assignment interface
- Search and filter capabilities

#### Manager Management Component
```typescript
interface Manager {
  id: string
  email: string
  first_name: string
  last_name: string
  property_id: string
  created_at: string
}

interface ManagerFormData {
  email: string
  first_name: string
  last_name: string
  property_id: string
  password: string
}
```

**Features:**
- Manager creation and assignment
- Property assignment management
- Manager performance overview
- Contact information management

#### Employee Directory Component
```typescript
interface Employee {
  id: string
  first_name: string
  last_name: string
  email: string
  property_id: string
  department: string
  position: string
  hire_date: string
  status: string
}

interface EmployeeFilters {
  property_id?: string
  department?: string
  status?: string
  search?: string
}
```

**Features:**
- Comprehensive employee listing
- Multi-property filtering
- Department and status filters
- Search by name or email
- Employee detail modal
- Status management

### 3. Manager Dashboard Components

#### Manager Dashboard Layout
```typescript
interface ManagerDashboardProps {
  user: User
  property: Property
}
```

**Tab Structure:**
- Applications: Job applications for their property
- Employees: Property-specific employee management
- Analytics: Property performance metrics

#### Application Management Component
```typescript
interface JobApplication {
  id: string
  property_id: string
  department: string
  position: string
  applicant_data: ApplicantData
  status: 'pending' | 'approved' | 'rejected'
  applied_at: string
}

interface ApplicantData {
  first_name: string
  last_name: string
  email: string
  phone: string
  address: string
  experience_years: string
  availability: string
}

interface JobOfferData {
  job_title: string
  start_date: string
  start_time: string
  pay_rate: number
  pay_frequency: string
  benefits_eligible: boolean
  supervisor: string
}
```

**Features:**
- Application review interface
- Detailed applicant information display
- Approve/reject workflow
- Job offer creation form
- Application status tracking

### 4. Shared Components

#### Data Table Component
```typescript
interface DataTableProps<T> {
  data: T[]
  columns: ColumnDefinition<T>[]
  searchable?: boolean
  filterable?: boolean
  sortable?: boolean
  pagination?: boolean
}

interface ColumnDefinition<T> {
  key: keyof T
  label: string
  sortable?: boolean
  render?: (value: any, row: T) => React.ReactNode
}
```

#### Search and Filter Bar
```typescript
interface SearchFilterProps {
  onSearch: (query: string) => void
  onFilter: (filters: Record<string, any>) => void
  filterOptions: FilterOption[]
}

interface FilterOption {
  key: string
  label: string
  type: 'select' | 'text' | 'date'
  options?: { value: string; label: string }[]
}
```

#### Modal Components
```typescript
interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
}
```

## Data Models

### User Model
```typescript
interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
  role: 'hr' | 'manager' | 'employee'
  property_id?: string
  is_active: boolean
  created_at: string
}
```

### Property Model
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

### Application Model
```typescript
interface JobApplication {
  id: string
  property_id: string
  department: string
  position: string
  applicant_data: Record<string, any>
  status: 'pending' | 'approved' | 'rejected'
  applied_at: string
  reviewed_by?: string
  reviewed_at?: string
  rejection_reason?: string
}
```

## Error Handling

### Frontend Error Handling
- Form validation with real-time feedback
- API error display with user-friendly messages
- Loading states for all async operations
- Retry mechanisms for failed requests
- Graceful degradation for network issues

### Backend Error Handling
- Proper HTTP status codes
- Structured error responses
- Input validation with detailed messages
- Authentication and authorization errors
- Database operation error handling

## Testing Strategy

### Frontend Testing
- Component unit tests with React Testing Library
- Integration tests for user workflows
- Form validation testing
- Authentication flow testing
- Responsive design testing

### Backend Testing
- API endpoint testing with pytest
- Authentication and authorization testing
- Data validation testing
- Error handling verification
- Role-based access control testing

### User Acceptance Testing
- HR workflow testing
- Manager workflow testing
- Cross-browser compatibility
- Mobile responsiveness
- Performance testing

## Performance Considerations

### Frontend Optimization
- Component lazy loading
- Efficient re-rendering with React.memo
- Debounced search inputs
- Pagination for large datasets
- Image optimization for QR codes

### Backend Optimization
- Efficient database queries
- Response caching where appropriate
- Pagination for large result sets
- Proper indexing for search operations
- Rate limiting for API endpoints

## Security Considerations

### Authentication Security
- JWT token expiration handling
- Secure token storage
- Role-based route protection
- Session timeout management
- Password security requirements

### Data Security
- Input sanitization
- SQL injection prevention
- XSS protection
- CORS configuration
- Audit logging for sensitive operations