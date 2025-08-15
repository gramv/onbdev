# Migration Plan
## Hotel Employee Onboarding System - From Legacy to Clean Architecture

### Document Version
- **Version**: 1.0
- **Date**: January 2025
- **Duration**: 7 weeks estimated
- **Related**: PRD.md, TECHNICAL_SPEC.md, DATABASE_SCHEMA.md, API_ENDPOINTS.md

---

## 1. Migration Overview

### 1.1 Current State Assessment

#### What We're Migrating From:
- **50+ duplicate API endpoints** spread across main_enhanced.py
- **7 duplicate dashboard components** (HRDashboard, HRDashboardV2, EnhancedManagerDashboard, etc.)
- **Inconsistent authentication** with broken property access control
- **Scattered database operations** without proper service layer
- **No module distribution system** for targeted form updates

#### What We're Preserving:
- ✅ Job Application System (`/apply/:propertyId`)
- ✅ Employee Onboarding Portal (`/onboard?token={token}`)
- ✅ All 14 onboarding step components
- ✅ Existing job_applications table and data
- ✅ Token-based employee access pattern

#### What We're Creating:
- Clean API structure with ~20 well-organized endpoints
- Single dashboard per role (HR, Manager)
- Module distribution system for form updates
- Proper authentication with secret key HR setup
- Complete audit trail and compliance tracking

---

## 2. Pre-Migration Checklist

### 2.1 Preparation Tasks
- [ ] **Full database backup** including all tables
- [ ] **Code repository backup** with tagged version
- [ ] **Document current endpoints** that are actually in use
- [ ] **Identify active users** and their roles
- [ ] **Export production data** for testing
- [ ] **Set up staging environment** for testing migration
- [ ] **Create rollback plan** with recovery procedures

### 2.2 Dependencies Check
```bash
# Backend dependencies to add
pip install bcrypt
pip install slowapi  # for rate limiting
pip install python-multipart
pip install email-validator

# Frontend dependencies to add
npm install @tanstack/react-query
npm install @hookform/resolvers
npm install date-fns
```

---

## 3. Phase 1: Foundation (Week 1)

### Day 1-2: Database Migration

#### Step 1.1: Backup Existing Database
```bash
# Create complete backup
pg_dump -h $DB_HOST -U $DB_USER -d hotel_onboarding > backup_$(date +%Y%m%d).sql

# Verify backup
pg_restore --list backup_$(date +%Y%m%d).sql
```

#### Step 1.2: Create New Tables
```sql
-- Run the schema from DATABASE_SCHEMA.md
-- Start with core tables
CREATE TABLE users (...);
CREATE TABLE properties (...);
CREATE TABLE property_managers (...);

-- Add module tables
CREATE TABLE module_templates (...);
CREATE TABLE employee_modules (...);

-- Add compliance tables
CREATE TABLE compliance_deadlines (...);
CREATE TABLE audit_logs (...);
```

#### Step 1.3: Migrate Existing Data
```sql
-- Migrate existing properties (if any exist)
INSERT INTO properties (name, address, city, state, zip_code, phone)
SELECT DISTINCT property_name, address, city, state, zip, phone
FROM existing_property_table
WHERE property_name IS NOT NULL;

-- Keep job_applications table as-is
-- Just add property_id column if missing
ALTER TABLE job_applications 
ADD COLUMN IF NOT EXISTS property_id UUID REFERENCES properties(id);

-- Create employee records from approved applications
INSERT INTO employees (
    application_id, 
    property_id,
    first_name, 
    last_name, 
    email,
    phone,
    position,
    hire_date,
    onboarding_status
)
SELECT 
    id,
    property_id,
    first_name,
    last_name,
    email,
    phone,
    position,
    approved_date,
    CASE 
        WHEN onboarding_completed THEN 'completed'
        ELSE 'in_progress'
    END
FROM job_applications
WHERE status = 'approved';
```

### Day 3-4: Clean Up Backend Structure

#### Step 1.4: Create New Folder Structure
```bash
hotel-onboarding-backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── hr.py            # HR endpoints
│   │   ├── manager.py       # Manager endpoints
│   │   ├── employee.py      # Employee endpoints
│   │   └── public.py        # Public endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── property_service.py
│   │   ├── manager_service.py
│   │   ├── module_service.py
│   │   └── compliance_service.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── rate_limit.py
│   │   └── property_access.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_models.py
│   │   ├── property_models.py
│   │   └── module_models.py
│   └── main.py              # New clean entry point
```

#### Step 1.5: Archive Old Files
```bash
# Create archive of old files
mkdir -p app/archive/old_system
mv app/main_enhanced.py app/archive/old_system/
mv app/main_enhanced_backup_*.py app/archive/old_system/

# Keep these files active during migration
# app/supabase_service_enhanced.py (needed for database)
# app/models.py (needed for existing endpoints)
```

### Day 5: Frontend Cleanup

#### Step 1.6: Archive Duplicate Components
```bash
# Create archive folder
mkdir -p src/archive/old_components

# Move duplicate dashboards
mv src/pages/HRDashboardV2.tsx src/archive/old_components/
mv src/pages/HRDashboardDebug.tsx src/archive/old_components/
mv src/pages/EnhancedManagerDashboard.tsx src/archive/old_components/
mv src/pages/EnhancedManagerDashboardV2.tsx src/archive/old_components/
mv src/pages/ManagerDashboardDebug.tsx src/archive/old_components/

# Keep for reference during migration
# src/pages/HRDashboard.tsx
# src/pages/ManagerDashboard.tsx
```

---

## 4. Phase 2: Authentication System (Week 2)

### Day 1-2: Implement New Auth System

#### Step 2.1: Create Auth Service
```python
# app/services/auth_service.py
class AuthService:
    def create_hr_admin(self, secret_key: str, user_data: dict):
        # Verify secret key from environment
        # Create first HR admin account
        # Return success/error
    
    def login(self, email: str, password: str):
        # Verify credentials
        # Generate JWT tokens
        # Log login attempt
    
    def verify_token(self, token: str):
        # Decode and validate JWT
        # Check user still active
        # Return user data
```

#### Step 2.2: Create Setup Endpoint
```python
# app/api/auth.py
@router.post("/setup/hr-admin")
async def setup_hr_admin(data: HRSetupRequest):
    """One-time setup for first HR admin"""
    # Check if HR admin already exists
    # Verify secret key
    # Create admin account
    # Return credentials
```

### Day 3: Implement Role Middleware

#### Step 2.3: Create Role-Based Middleware
```python
# app/middleware/auth_middleware.py
def require_hr():
    """Require HR role"""
    async def verify(token: str = Depends(oauth2_scheme)):
        user = verify_token(token)
        if user.role != 'hr':
            raise HTTPException(403, "HR access required")
        return user
    return verify

def require_manager():
    """Require Manager role"""
    # Similar implementation

def require_property_access(property_id: str):
    """Verify property access for managers"""
    # Check if user has access to property
```

### Day 4-5: Test Authentication

#### Step 2.4: Create Test Script
```python
# tests/test_auth_migration.py
def test_hr_setup():
    # Test secret key validation
    # Test first admin creation
    # Test duplicate prevention

def test_role_access():
    # Test HR can access all
    # Test Manager property isolation
    # Test unauthorized access blocked
```

---

## 5. Phase 3: HR Features (Week 3)

### Day 1-2: Property Management

#### Step 3.1: Implement Property CRUD
```python
# app/api/hr.py
@router.get("/properties")
@require_hr()
async def get_properties():
    # Return all properties with stats

@router.post("/properties")
@require_hr()
async def create_property(data: PropertyCreate):
    # Create new property
    # Log creation in audit trail
```

### Day 3-4: Manager Management

#### Step 3.2: Implement Manager Operations
```python
@router.post("/managers")
@require_hr()
async def create_manager(data: ManagerCreate):
    # Create manager account
    # Send welcome email
    # Assign to properties
```

### Day 5: Testing

#### Step 3.3: Integration Tests
```bash
# Test property operations
pytest tests/test_property_crud.py

# Test manager assignment
pytest tests/test_manager_assignment.py
```

---

## 6. Phase 4: Manager Features (Week 4)

### Day 1-2: Manager Dashboard

#### Step 4.1: Create Clean Dashboard Component
```typescript
// src/pages/manager/ManagerDashboard.tsx
export const ManagerDashboard = () => {
  const { data: stats } = useQuery({
    queryKey: ['manager-dashboard'],
    queryFn: ManagerService.getDashboard
  });
  
  return (
    // Clean dashboard with:
    // - Pending applications
    // - Active onboardings
    // - Compliance alerts
  );
};
```

### Day 3-4: Application Review

#### Step 4.2: Implement Application Management
```python
@router.post("/applications/{id}/approve")
async def approve_application(
    id: str,
    data: ApprovalData,
    user=Depends(require_manager())
):
    # Verify property access
    # Create employee record
    # Generate onboarding token
    # Send welcome email
```

### Day 5: I-9 Section 2

#### Step 4.3: Implement I-9 Completion
```python
@router.post("/i9-section2/{employee_id}")
async def complete_i9_section2(
    employee_id: str,
    data: I9Section2Data,
    user=Depends(require_manager())
):
    # Verify 3-day deadline
    # Save verification data
    # Generate completed PDF
    # Update compliance status
```

---

## 7. Phase 5: Module Distribution (Week 5)

### Day 1-2: Token System

#### Step 5.1: Create Module Token Generator
```python
# app/services/module_service.py
class ModuleService:
    def create_module_token(
        self,
        employee_id: str,
        module_type: str,
        expires_days: int = 7
    ):
        # Generate unique token
        # Store in employee_modules table
        # Return access URL
```

### Day 3-4: Module Templates

#### Step 5.2: Seed Module Templates
```sql
-- Insert standard module templates
INSERT INTO module_templates (code, name, category, expires_in_days) VALUES
('w4_update', 'W-4 Tax Withholding Update', 'tax', 7),
('i9_reverify', 'I-9 Reverification', 'compliance', 3),
('direct_deposit', 'Direct Deposit Update', 'banking', 7),
('health_insurance', 'Health Insurance Enrollment', 'benefits', 14),
('trafficking_training', 'Human Trafficking Awareness', 'training', 30),
('policy_update', 'Company Policy Acknowledgment', 'policy', 7);
```

### Day 5: Email Integration

#### Step 5.3: Create Email Templates
```python
# app/templates/emails/module_invitation.html
"""
Subject: Action Required: {module_name}

Dear {employee_name},

You have been assigned to complete: {module_name}

Please click the link below to access the form:
{access_url}

This link expires on: {expiration_date}

Thank you,
{property_name} HR Team
"""
```

---

## 8. Phase 6: Frontend Migration (Week 6)

### Day 1-2: Create New Components

#### Step 6.1: Build HR Dashboard
```typescript
// src/pages/hr/HRDashboard.tsx
// Clean implementation with:
// - Property management
// - Manager management  
// - Module distribution
// - Analytics
```

### Day 3-4: Update Routes

#### Step 6.2: Clean Up App.tsx
```typescript
// Remove old routes
// Add new clean routes:
<Route path="/login" element={<LoginPage />} />
<Route path="/setup" element={<SetupPage />} />
<Route path="/hr/*" element={<HRLayout />} />
<Route path="/manager/*" element={<ManagerLayout />} />
```

### Day 5: Component Testing

#### Step 6.3: Test New Components
```bash
# Run component tests
npm test -- --coverage

# Test role-based access
npm test -- ProtectedRoute

# Test data fetching
npm test -- useProperties
```

---

## 9. Phase 7: Testing & Deployment (Week 7)

### Day 1-2: End-to-End Testing

#### Step 7.1: Complete Workflow Test
```python
# tests/test_complete_workflow.py
def test_complete_hiring_flow():
    # 1. Submit application
    # 2. Manager approves
    # 3. Employee completes onboarding
    # 4. Manager completes I-9
    # 5. Verify all data saved
```

### Day 3: Performance Testing

#### Step 7.2: Load Testing
```bash
# Use locust for load testing
locust -f tests/load_test.py --host=http://localhost:8000

# Test scenarios:
# - 100 concurrent users
# - 500 applications per hour
# - 50 managers accessing dashboards
```

### Day 4: Security Audit

#### Step 7.3: Security Verification
```bash
# Check for SQL injection
sqlmap -u "http://localhost:8000/api/hr/properties" --headers="Authorization: Bearer TOKEN"

# Check for XSS
# Verify JWT expiration
# Test rate limiting
```

### Day 5: Production Deployment

#### Step 7.4: Deploy to Production
```bash
# 1. Final backup
pg_dump production_db > final_backup.sql

# 2. Deploy backend
docker build -t hotel-onboarding-backend .
docker push registry/hotel-onboarding-backend

# 3. Run migrations
alembic upgrade head

# 4. Deploy frontend
npm run build
aws s3 sync dist/ s3://hotel-onboarding-frontend

# 5. Update DNS/Load balancer
# 6. Monitor for issues
```

---

## 10. Post-Migration Tasks

### 10.1 Cleanup (Week 8)
- [ ] Remove archived files after 30 days stable
- [ ] Delete old database tables
- [ ] Remove unused dependencies
- [ ] Update documentation

### 10.2 Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Configure performance monitoring
- [ ] Create automated health checks
- [ ] Set up backup automation

### 10.3 Training
- [ ] Create HR admin guide
- [ ] Create manager training videos
- [ ] Update employee instructions
- [ ] Document troubleshooting

---

## 11. Rollback Plan

### If Migration Fails:

#### Step 1: Immediate Rollback
```bash
# Restore database
psql -h $DB_HOST -U $DB_USER -d hotel_onboarding < backup_$(date +%Y%m%d).sql

# Revert code
git checkout previous-version-tag

# Restart services
docker-compose restart
```

#### Step 2: Investigate Issues
- Check error logs
- Review migration scripts
- Test in staging again
- Fix identified issues

#### Step 3: Retry Migration
- Schedule new migration window
- Communicate with stakeholders
- Apply fixes and retry

---

## 12. Success Criteria

### Migration is successful when:
- ✅ All existing applications accessible
- ✅ Onboarding flow works end-to-end
- ✅ HR can manage properties and managers
- ✅ Managers can only see their property data
- ✅ Module distribution system functional
- ✅ No data loss from migration
- ✅ Performance equal or better
- ✅ All tests passing
- ✅ Zero critical bugs in first week
- ✅ User satisfaction maintained

---

## 13. Risk Mitigation

### High-Risk Areas:
1. **Data Migration**: Test thoroughly in staging
2. **Authentication Changes**: Keep old system available for rollback
3. **Property Isolation**: Extensive testing of access control
4. **Token Compatibility**: Ensure existing tokens continue working

### Mitigation Strategies:
- Run parallel systems for 1 week
- Gradual rollout by property
- Feature flags for new functionality
- Comprehensive logging for debugging
- Daily backups during migration

---

## 14. Communication Plan

### Stakeholders:
- **HR Admins**: 2 weeks advance notice with training
- **Property Managers**: 1 week notice with video guide
- **Employees**: Email about temporary maintenance
- **IT Team**: Daily updates during migration

### Communication Timeline:
- **T-14 days**: Initial announcement
- **T-7 days**: Training materials distributed
- **T-1 day**: Final reminder
- **T-0**: Migration begins notification
- **T+1 day**: Success confirmation
- **T+7 days**: Feedback collection

---

## 15. Validation Checklist

### Pre-Production Validation:
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Security scan clean
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Training materials ready
- [ ] Rollback plan tested
- [ ] Backup verified
- [ ] Stakeholders informed
- [ ] Support team briefed

### Post-Production Validation:
- [ ] All endpoints responding
- [ ] Authentication working
- [ ] Property isolation verified
- [ ] Module distribution tested
- [ ] Email notifications working
- [ ] PDF generation functional
- [ ] Audit trail recording
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] User feedback positive

---

*End of Migration Plan Document*