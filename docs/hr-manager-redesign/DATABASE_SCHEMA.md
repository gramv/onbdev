# Database Schema Design
## Hotel Employee Onboarding System - Clean Schema

### Document Version
- **Version**: 1.0
- **Date**: January 2025
- **Database**: PostgreSQL 15+ (via Supabase)
- **Related**: PRD.md, TECHNICAL_SPEC.md

---

## 1. Schema Overview

### 1.1 Design Principles
- **Normalization**: 3NF for transactional data
- **Audit Trail**: All tables include created_at, updated_at
- **Soft Deletes**: Use is_active flags instead of hard deletes
- **UUID Keys**: Use UUIDs for all primary keys
- **RLS**: Row Level Security on all tables
- **Indexes**: Strategic indexes for query performance

### 1.2 Table Categories

| Category | Tables | Purpose |
|----------|--------|---------|
| **Core** | users, properties, property_managers | Basic system entities |
| **Applications** | job_applications, job_positions | Job application flow |
| **Employees** | employees, employee_documents | Employee records |
| **Modules** | employee_modules, module_templates | Form distribution |
| **Compliance** | compliance_deadlines, audit_logs | Federal requirements |
| **Onboarding** | onboarding_sessions, onboarding_progress | Onboarding tracking |

---

## 2. Core Tables

### 2.1 Users Table
Primary table for all system users (HR, Managers, temporary employee access)

```sql
CREATE TABLE users (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- User Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    
    -- Role & Access
    role VARCHAR(20) NOT NULL CHECK (role IN ('hr', 'manager', 'employee')),
    is_active BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_by UUID REFERENCES users(id),
    deactivated_at TIMESTAMP WITH TIME ZONE,
    deactivated_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_email_active ON users(email, is_active);

-- Comments
COMMENT ON TABLE users IS 'System users including HR, Managers, and temporary employee access';
COMMENT ON COLUMN users.role IS 'User role: hr (system-wide), manager (property-specific), employee (temporary)';
```

### 2.2 Properties Table
Hotel properties managed by the system

```sql
CREATE TABLE properties (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Property Information
    name VARCHAR(255) NOT NULL,
    code VARCHAR(20) UNIQUE, -- Optional property code
    
    -- Address
    address VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    country VARCHAR(2) DEFAULT 'US',
    
    -- Contact
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    website VARCHAR(255),
    
    -- Settings
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    is_active BOOLEAN DEFAULT true,
    
    -- Statistics (denormalized for performance)
    employee_count INTEGER DEFAULT 0,
    manager_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_by UUID REFERENCES users(id),
    deactivated_at TIMESTAMP WITH TIME ZONE,
    deactivated_by UUID REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_properties_active ON properties(is_active);
CREATE INDEX idx_properties_state ON properties(state);
CREATE INDEX idx_properties_name ON properties(name);

-- Comments
COMMENT ON TABLE properties IS 'Hotel properties in the system';
COMMENT ON COLUMN properties.code IS 'Optional property code for integration with other systems';
```

### 2.3 Property Managers Table
Many-to-many relationship between managers and properties

```sql
CREATE TABLE property_managers (
    -- Composite Primary Key
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Assignment Information
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    
    -- Permissions (future expansion)
    can_approve_applications BOOLEAN DEFAULT true,
    can_complete_i9 BOOLEAN DEFAULT true,
    can_view_reports BOOLEAN DEFAULT true,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    deactivated_at TIMESTAMP WITH TIME ZONE,
    deactivated_by UUID REFERENCES users(id),
    
    PRIMARY KEY (property_id, user_id)
);

-- Indexes
CREATE INDEX idx_property_managers_user ON property_managers(user_id);
CREATE INDEX idx_property_managers_active ON property_managers(user_id, is_active);

-- Comments
COMMENT ON TABLE property_managers IS 'Links managers to properties they can access';
```

---

## 3. Application Tables

### 3.1 Job Applications Table (Existing - Keep)
```sql
CREATE TABLE job_applications (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Application Details
    property_id UUID REFERENCES properties(id),
    position VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    
    -- Applicant Information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    
    -- Application Data
    resume_url TEXT,
    cover_letter TEXT,
    availability JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    is_talent_pool BOOLEAN DEFAULT false,
    
    -- Review Information
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_applications_property ON job_applications(property_id);
CREATE INDEX idx_applications_status ON job_applications(status);
CREATE INDEX idx_applications_email ON job_applications(email);
CREATE INDEX idx_applications_talent_pool ON job_applications(is_talent_pool);
```

---

## 4. Employee Tables

### 4.1 Employees Table
Core employee records

```sql
CREATE TABLE employees (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Links
    user_id UUID REFERENCES users(id), -- Optional, only if they have login
    application_id UUID REFERENCES job_applications(id),
    property_id UUID REFERENCES properties(id),
    
    -- Employee Information
    employee_number VARCHAR(50) UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    preferred_name VARCHAR(100),
    
    -- Contact
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    
    -- Personal Information
    ssn_encrypted VARCHAR(500), -- Encrypted SSN
    date_of_birth DATE,
    
    -- Address
    address JSONB, -- Flexible address storage
    
    -- Employment
    position VARCHAR(255),
    department VARCHAR(255),
    hire_date DATE,
    start_date DATE,
    termination_date DATE,
    
    -- Status
    employment_status VARCHAR(50) DEFAULT 'active',
    onboarding_status VARCHAR(50) DEFAULT 'pending',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_employees_property ON employees(property_id);
CREATE INDEX idx_employees_email ON employees(email);
CREATE INDEX idx_employees_status ON employees(employment_status);
CREATE INDEX idx_employees_onboarding ON employees(onboarding_status);
```

---

## 5. Module Distribution Tables

### 5.1 Module Templates Table
Templates for different form types

```sql
CREATE TABLE module_templates (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Template Information
    code VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'w4_update', 'i9_reverify'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- 'tax', 'compliance', 'benefits', 'training'
    
    -- Configuration
    form_fields JSONB, -- Field definitions
    validations JSONB, -- Validation rules
    expires_in_days INTEGER DEFAULT 7,
    
    -- Email Template
    email_subject VARCHAR(255),
    email_body TEXT,
    
    -- Settings
    is_active BOOLEAN DEFAULT true,
    requires_signature BOOLEAN DEFAULT true,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Seed Data
INSERT INTO module_templates (code, name, category) VALUES
    ('w4_update', 'W-4 Tax Withholding Update', 'tax'),
    ('i9_reverify', 'I-9 Reverification', 'compliance'),
    ('direct_deposit', 'Direct Deposit Update', 'banking'),
    ('health_insurance', 'Health Insurance Enrollment', 'benefits'),
    ('trafficking_training', 'Human Trafficking Awareness Training', 'training'),
    ('policy_update', 'Company Policy Acknowledgment', 'policy');
```

### 5.2 Employee Modules Table
Tracks individual module assignments

```sql
CREATE TABLE employee_modules (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Links
    employee_id UUID REFERENCES employees(id),
    template_id UUID REFERENCES module_templates(id),
    property_id UUID REFERENCES properties(id),
    
    -- Token & Access
    token VARCHAR(500) UNIQUE NOT NULL,
    token_type VARCHAR(50) DEFAULT 'module_update',
    
    -- Timing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Form Data
    initial_data JSONB, -- Pre-populated data
    submitted_data JSONB, -- Employee submission
    
    -- Tracking
    reminder_count INTEGER DEFAULT 0,
    last_reminder_at TIMESTAMP WITH TIME ZONE,
    accessed_at TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    user_agent TEXT,
    
    -- Assignment
    created_by UUID REFERENCES users(id),
    reason TEXT,
    notes TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' -- pending, accessed, completed, expired
);

-- Indexes
CREATE INDEX idx_employee_modules_token ON employee_modules(token);
CREATE INDEX idx_employee_modules_employee ON employee_modules(employee_id);
CREATE INDEX idx_employee_modules_status ON employee_modules(status);
CREATE INDEX idx_employee_modules_expires ON employee_modules(expires_at);
CREATE INDEX idx_employee_modules_property ON employee_modules(property_id);
```

---

## 6. Compliance Tables

### 6.1 Compliance Deadlines Table
Tracks federal compliance requirements

```sql
CREATE TABLE compliance_deadlines (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Links
    employee_id UUID REFERENCES employees(id),
    property_id UUID REFERENCES properties(id),
    
    -- Requirement
    requirement_type VARCHAR(50) NOT NULL, -- 'i9_section1', 'i9_section2', etc.
    requirement_name VARCHAR(255),
    
    -- Timing
    due_date DATE NOT NULL,
    completed_date DATE,
    
    -- Alerts
    alert_sent BOOLEAN DEFAULT false,
    alert_sent_at TIMESTAMP WITH TIME ZONE,
    escalation_sent BOOLEAN DEFAULT false,
    escalation_sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, overdue
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_compliance_employee ON compliance_deadlines(employee_id);
CREATE INDEX idx_compliance_due_date ON compliance_deadlines(due_date);
CREATE INDEX idx_compliance_status ON compliance_deadlines(status);
CREATE INDEX idx_compliance_property ON compliance_deadlines(property_id);
```

### 6.2 Audit Logs Table
Comprehensive audit trail

```sql
CREATE TABLE audit_logs (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Actor
    user_id UUID REFERENCES users(id),
    user_email VARCHAR(255),
    user_role VARCHAR(20),
    
    -- Action
    action VARCHAR(100) NOT NULL, -- 'create', 'update', 'delete', 'view', 'approve', etc.
    resource_type VARCHAR(50) NOT NULL, -- 'property', 'employee', 'application', etc.
    resource_id UUID,
    
    -- Details
    details JSONB, -- Additional context
    changes JSONB, -- Before/after for updates
    
    -- Request Information
    ip_address INET,
    user_agent TEXT,
    request_id UUID,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- Partitioning (for large-scale deployments)
-- Partition by month for easier archival
```

---

## 7. Onboarding Tables

### 7.1 Onboarding Sessions Table
Tracks active onboarding processes

```sql
CREATE TABLE onboarding_sessions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Links
    employee_id UUID REFERENCES employees(id),
    application_id UUID REFERENCES job_applications(id),
    property_id UUID REFERENCES properties(id),
    
    -- Token
    token VARCHAR(500) UNIQUE NOT NULL,
    token_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Progress
    current_step VARCHAR(50),
    completed_steps JSONB DEFAULT '[]'::jsonb,
    percent_complete INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'in_progress', -- in_progress, completed, expired
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Manager Review
    manager_review_required BOOLEAN DEFAULT true,
    manager_reviewed_by UUID REFERENCES users(id),
    manager_reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- HR Review
    hr_review_required BOOLEAN DEFAULT true,
    hr_reviewed_by UUID REFERENCES users(id),
    hr_reviewed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_onboarding_token ON onboarding_sessions(token);
CREATE INDEX idx_onboarding_employee ON onboarding_sessions(employee_id);
CREATE INDEX idx_onboarding_status ON onboarding_sessions(status);
CREATE INDEX idx_onboarding_property ON onboarding_sessions(property_id);
```

### 7.2 Onboarding Form Data Table
Stores form data for each onboarding step

```sql
CREATE TABLE onboarding_form_data (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Links
    session_id UUID REFERENCES onboarding_sessions(id),
    employee_id UUID REFERENCES employees(id),
    
    -- Form Information
    step_id VARCHAR(50) NOT NULL, -- 'personal_info', 'i9_section1', etc.
    form_data JSONB NOT NULL,
    
    -- Signature
    signature_data TEXT,
    signed_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_complete BOOLEAN DEFAULT false,
    validated BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_form_data_session ON onboarding_form_data(session_id);
CREATE INDEX idx_form_data_employee ON onboarding_form_data(employee_id);
CREATE INDEX idx_form_data_step ON onboarding_form_data(step_id);
```

---

## 8. Row Level Security (RLS)

### 8.1 Enable RLS on All Tables
```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_managers ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_deadlines ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_form_data ENABLE ROW LEVEL SECURITY;
```

### 8.2 RLS Policies

#### HR Policies (Full Access)
```sql
-- HR can see and modify all data
CREATE POLICY hr_full_access ON users
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'hr');

CREATE POLICY hr_properties ON properties
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'hr');

CREATE POLICY hr_applications ON job_applications
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'hr');

CREATE POLICY hr_employees ON employees
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'hr');
```

#### Manager Policies (Property-Specific)
```sql
-- Managers can only see their assigned properties
CREATE POLICY manager_properties ON properties
    FOR SELECT
    USING (
        auth.jwt() ->> 'role' = 'manager' 
        AND id IN (
            SELECT property_id 
            FROM property_managers 
            WHERE user_id = (auth.jwt() ->> 'sub')::uuid
            AND is_active = true
        )
    );

-- Managers can only see applications for their properties
CREATE POLICY manager_applications ON job_applications
    FOR ALL
    USING (
        auth.jwt() ->> 'role' = 'manager'
        AND property_id IN (
            SELECT property_id 
            FROM property_managers 
            WHERE user_id = (auth.jwt() ->> 'sub')::uuid
            AND is_active = true
        )
    );

-- Managers can only see employees in their properties
CREATE POLICY manager_employees ON employees
    FOR SELECT
    USING (
        auth.jwt() ->> 'role' = 'manager'
        AND property_id IN (
            SELECT property_id 
            FROM property_managers 
            WHERE user_id = (auth.jwt() ->> 'sub')::uuid
            AND is_active = true
        )
    );
```

#### Employee Policies (Self-Access Only)
```sql
-- Employees can only see their own data
CREATE POLICY employee_self_access ON employees
    FOR SELECT
    USING (
        auth.jwt() ->> 'role' = 'employee'
        AND id = (auth.jwt() ->> 'employee_id')::uuid
    );

-- Employees can only access their own modules
CREATE POLICY employee_modules_self ON employee_modules
    FOR SELECT
    USING (
        auth.jwt() ->> 'role' = 'employee'
        AND employee_id = (auth.jwt() ->> 'employee_id')::uuid
    );

-- Employees can update their own form data
CREATE POLICY employee_form_data ON onboarding_form_data
    FOR ALL
    USING (
        auth.jwt() ->> 'role' = 'employee'
        AND employee_id = (auth.jwt() ->> 'employee_id')::uuid
    );
```

---

## 9. Functions & Triggers

### 9.1 Updated Timestamp Trigger
```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 9.2 Audit Log Function
```sql
-- Function to create audit log entries
CREATE OR REPLACE FUNCTION create_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        user_id,
        user_email,
        user_role,
        action,
        resource_type,
        resource_id,
        changes,
        ip_address
    ) VALUES (
        current_setting('app.current_user_id', true)::uuid,
        current_setting('app.current_user_email', true),
        current_setting('app.current_user_role', true),
        TG_OP,
        TG_TABLE_NAME,
        NEW.id,
        jsonb_build_object(
            'old', row_to_json(OLD),
            'new', row_to_json(NEW)
        ),
        inet_client_addr()
    );
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to sensitive tables
CREATE TRIGGER audit_employees AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();

CREATE TRIGGER audit_properties AFTER INSERT OR UPDATE OR DELETE ON properties
    FOR EACH ROW EXECUTE FUNCTION create_audit_log();
```

### 9.3 Property Statistics Update
```sql
-- Function to update property statistics
CREATE OR REPLACE FUNCTION update_property_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update employee count
    UPDATE properties 
    SET employee_count = (
        SELECT COUNT(*) 
        FROM employees 
        WHERE property_id = NEW.property_id 
        AND employment_status = 'active'
    )
    WHERE id = NEW.property_id;
    
    -- Update manager count
    UPDATE properties 
    SET manager_count = (
        SELECT COUNT(*) 
        FROM property_managers 
        WHERE property_id = NEW.property_id 
        AND is_active = true
    )
    WHERE id = NEW.property_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_property_employee_stats 
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_property_stats();

CREATE TRIGGER update_property_manager_stats 
    AFTER INSERT OR UPDATE OR DELETE ON property_managers
    FOR EACH ROW EXECUTE FUNCTION update_property_stats();
```

---

## 10. Indexes Summary

### 10.1 Performance-Critical Indexes
```sql
-- Authentication lookups
CREATE INDEX idx_users_email_password ON users(email, is_active);

-- Property access checks
CREATE INDEX idx_property_managers_user_active ON property_managers(user_id, is_active);

-- Application queries
CREATE INDEX idx_applications_property_status ON job_applications(property_id, status);

-- Employee lookups
CREATE INDEX idx_employees_property_status ON employees(property_id, employment_status);

-- Module tracking
CREATE INDEX idx_modules_employee_status ON employee_modules(employee_id, status);

-- Compliance monitoring
CREATE INDEX idx_compliance_due_status ON compliance_deadlines(due_date, status);

-- Audit trail queries
CREATE INDEX idx_audit_user_date ON audit_logs(user_id, created_at DESC);
```

---

## 11. Data Migration Notes

### 11.1 From Existing Schema
```sql
-- Migrate existing users (keep existing IDs)
INSERT INTO users (id, email, password_hash, first_name, last_name, role)
SELECT id, email, password, first_name, last_name, role
FROM old_users;

-- Migrate existing properties
INSERT INTO properties (name, address, city, state, zip_code, phone)
SELECT name, address, city, state, zip, phone
FROM old_properties;

-- Migrate job applications (preserve existing)
-- Keep as-is, already compatible

-- Create employee records from existing data
INSERT INTO employees (
    application_id, 
    property_id, 
    first_name, 
    last_name, 
    email
)
SELECT 
    ja.id,
    ja.property_id,
    ja.first_name,
    ja.last_name,
    ja.email
FROM job_applications ja
WHERE ja.status = 'approved';
```

### 11.2 Cleanup Old Tables
```sql
-- After successful migration and verification
DROP TABLE IF EXISTS old_users CASCADE;
DROP TABLE IF EXISTS old_properties CASCADE;
DROP TABLE IF EXISTS redundant_dashboard_data CASCADE;
-- etc.
```

---

## 12. Performance Considerations

### 12.1 Table Sizes & Growth
| Table | Expected Size | Growth Rate | Partitioning |
|-------|--------------|-------------|--------------|
| users | 1,000 | 50/month | No |
| properties | 100 | 5/year | No |
| employees | 10,000 | 500/month | No |
| audit_logs | 1,000,000+ | 50,000/month | Yes (monthly) |
| employee_modules | 100,000 | 5,000/month | No |

### 12.2 Query Optimization
- Use covering indexes for frequent queries
- Denormalize statistics (employee_count, manager_count)
- Implement query result caching in application layer
- Use database connection pooling (50 connections)

---

## 13. Backup & Recovery

### 13.1 Backup Strategy
```sql
-- Daily backups
pg_dump -h localhost -U postgres -d hotel_onboarding > backup_$(date +%Y%m%d).sql

-- Point-in-time recovery enabled
-- WAL archiving configured
-- Retention: 30 days
```

### 13.2 Recovery Procedures
1. Stop application servers
2. Restore from backup
3. Apply WAL logs to recovery point
4. Verify data integrity
5. Restart application servers

---

*End of Database Schema Document*