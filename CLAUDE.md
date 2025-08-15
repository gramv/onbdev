# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hotel Employee Onboarding System - A comprehensive digital onboarding platform for hospitality industry with federal compliance (I-9, W-4) built using FastAPI backend and React/TypeScript frontend.

## Quick Start Commands

### Backend
```bash
cd hotel-onboarding-backend

# Setup and run (preferred method - no Poetry)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install poetry  # Temporary for export
poetry export -f requirements.txt --output requirements.txt
pip install -r requirements.txt
python3 -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8000 --reload

# Testing
python3 -m pytest tests/ -v  # Run all tests with verbose output
python3 -m pytest tests/test_authentication.py::test_login  # Run specific test
python3 -m pytest --cov=app --cov-report=term-missing  # With coverage

# Code quality
python3 -m black app/  # Format code
python3 -m mypy app/  # Type checking
python3 -m ruff check app/  # Linting
```

### Frontend
```bash
cd hotel-onboarding-frontend

npm install
npm run dev  # Starts on http://localhost:3000
npm run build  # Production build
npm run test  # Run Jest tests
npm run test:watch  # Watch mode
npm run lint  # ESLint

# Run specific test
npm test -- PersonalInfoStep
npm test -- --coverage
```

### Quick Database Debugging
```bash
# Backend directory
python3 check_test_db_schema.py  # Verify database schema
python3 create_test_data.py  # Create test data
python3 debug_auth.py  # Debug authentication issues
```

## High-Level Architecture

### Three-Phase Workflow
1. **Employee Phase**: Job application → Manager approval → Onboarding completion
2. **Manager Phase**: Review submissions → I-9 Section 2 → Approve/correct
3. **HR Phase**: Final compliance review → System integration

### Authentication Model
- **Managers/HR**: Persistent accounts with role-based access (JWT auth)
- **Employees**: Stateless 7-day JWT tokens, no accounts
- **Property Isolation**: Managers only see their property's data

### Critical Files & Their Purpose

#### Backend Core Files
- `app/main_enhanced.py` - Main API entry point, all endpoints
- `app/supabase_service_enhanced.py` - Database abstraction layer
- `app/auth.py` - JWT authentication middleware
- `app/property_access_control.py` - Property-based access enforcement
- `app/websocket_manager.py` - Real-time WebSocket connections
- `app/pdf_forms.py` - Federal form PDF generation

#### Frontend Core Files
- `src/App.tsx` - Main app with routing
- `src/contexts/AuthContext.tsx` - Global auth state
- `src/pages/OnboardingFlowPortal.tsx` - Employee onboarding flow
- `src/pages/ManagerDashboard.tsx` - Manager interface
- `src/pages/HRDashboard.tsx` - HR oversight interface

### Database Connection
- **Provider**: Supabase (PostgreSQL)
- **Connection**: Through `SupabaseServiceEnhanced` class
- **RLS**: Row Level Security enforced at service layer
- **Property Filtering**: All queries must filter by property_id

## Critical Implementation Rules

### 1. Brick-by-Brick Methodology
**NEVER build everything at once**. Always:
1. Build one component/endpoint completely
2. Test in isolation
3. Connect to next component
4. Verify integration
5. Move to next component

### 2. Property Access Control
```python
# CORRECT - Always filter by property
employees = await supabase.get_employees_by_property(property_id)

# WRONG - Never global queries
employees = await supabase.get_all_employees()  # Security violation!
```

### 3. Step Component Pattern
All onboarding steps MUST follow:
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

// NEVER use useOutletContext() - always direct props
```

### 4. Federal Compliance Requirements
- **I-9 Section 1**: By first day of work
- **I-9 Section 2**: Within 3 business days
- **Signature Coordinates**: Must match exactly between frontend/backend
- **Audit Trail**: Required for all form modifications

### 5. PDF Signature Positioning
```typescript
// Frontend (pdf-lib) - bottom-left origin
{ x: 150, y: 142, width: 200, height: 50 }

// Backend (PyMuPDF) - bottom-left origin  
{ x: 150, y: 650, width: 200, height: 50 }
```

## Agent OS Integration

### Commands for Development
- `/create-spec` - Create feature specification before implementation
- `/execute-tasks` - Implement features from spec with agents
- `/analyze-product` - Assess progress and technical debt

### Available Specialized Agents
When using `/execute-tasks` with complex features:
- `backend-api-builder` - Backend endpoints and services
- `frontend-component-fixer` - React component fixes
- `onboarding-form-builder` - Form components with compliance
- `test-automation-engineer` - Comprehensive testing
- `compliance-validator` - Federal compliance verification
- `task-orchestrator` - Complex multi-part features

### Current Active Specs
- **HR Manager System Consolidation**: `.agent-os/specs/2025-08-06-hr-manager-system-consolidation/`
- **MVP Test Database Setup**: `.agent-os/specs/2025-08-09-mvp-test-database-setup/`

## Testing Approach

### Backend Testing
```bash
# Unit tests for specific modules
python3 -m pytest tests/test_authentication.py -v

# Integration tests  
python3 -m pytest tests/test_integration.py -v

# Property access control tests
python3 test_property_access_control_comprehensive.py

# WebSocket functionality
python3 test_websocket_basic.py
```

### Frontend Testing
```bash
# Component tests
npm test -- components/

# Integration tests
npm test -- integration/

# E2E tests
npm test -- e2e/

# Compliance tests
npm test -- compliance/
```

### Key Test Routes
- `/test-steps` - Test individual components in isolation
- `/onboard` - Main employee onboarding flow
- `/manager` - Manager dashboard
- `/hr` - HR dashboard

## Performance & Scalability

### System Capacity Design
- **15-20 HR users** with full access
- **200+ Managers** with property-specific access  
- **Unlimited employees** (stateless sessions)

### Production Optimizations
```python
# Connection pooling
max_connections = 50
min_connections = 10

# Caching frequently accessed data
@lru_cache(maxsize=128)
async def get_cached_properties():
    return await supabase.get_all_properties()
```

### Database Indexes (Run once in production)
```sql
CREATE INDEX idx_employees_property_id ON employees(property_id);
CREATE INDEX idx_applications_property_status ON job_applications(property_id, status);
CREATE INDEX idx_managers_property ON property_managers(property_id);
```

## Common Issues & Solutions

### Authentication Issues
```bash
python3 debug_auth.py  # Check auth flow
python3 check_test_db_schema.py  # Verify user tables
```

### Property Access Issues
```bash
python3 check_property_assignment.py  # Verify manager assignments
python3 test_property_access_control_comprehensive.py  # Test isolation
```

### Frontend State Issues
- Check session storage for onboarding progress
- Verify JWT token in localStorage
- Check WebSocket connection status in console

## Development Workflow

1. **New Feature**: Run `/create-spec` first
2. **Implementation**: Use `/execute-tasks` with appropriate agents
3. **Testing**: Run comprehensive test suite
4. **Property Isolation**: Verify all queries filter by property_id
5. **Compliance**: Ensure federal requirements met
6. **Performance**: Check response times < 200ms

## NO MOCK DATA Policy

This is a **production system**. Never use mock/hardcoded data for:
- OCR document processing (use Groq API)
- Authentication flows
- Database operations
- PDF generation

## Important Constraints

- **Python Version**: 3.12+ required
- **Node Version**: 20 LTS required
- **Database**: Supabase (PostgreSQL) only
- **No Poetry in production**: Use pip and requirements.txt
- **Property Isolation**: Every query must respect property boundaries
- **Federal Compliance**: I-9/W-4 requirements are non-negotiable