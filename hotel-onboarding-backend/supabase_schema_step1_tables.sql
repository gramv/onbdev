-- =====================================================
-- STEP 1: CREATE CORE TABLES (No Foreign Keys)
-- Apply this first in Supabase SQL Editor
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- CORE TABLES WITHOUT FOREIGN KEYS
-- =====================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR UNIQUE NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('hr', 'manager', 'employee')),
    property_id UUID,
    is_active BOOLEAN DEFAULT true,
    password_hash VARCHAR,
    
    -- Enhanced security fields
    last_login_at TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- User roles table for flexible RBAC
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]'::jsonb,
    is_system_role BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Properties table
CREATE TABLE IF NOT EXISTS properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    address VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    phone VARCHAR(20),
    
    -- Business details
    business_license VARCHAR,
    tax_id VARCHAR,
    property_type VARCHAR DEFAULT 'hotel',
    
    -- QR code and branding
    qr_code_url TEXT,
    logo_url TEXT,
    brand_colors JSONB,
    
    -- Status and settings
    is_active BOOLEAN DEFAULT true,
    timezone VARCHAR DEFAULT 'America/New_York',
    settings JSONB DEFAULT '{}'::jsonb,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- Job applications table
CREATE TABLE IF NOT EXISTS job_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL,
    
    -- Job details
    department VARCHAR NOT NULL,
    position VARCHAR NOT NULL,
    job_posting_id UUID,
    
    -- Applicant data (encrypted sensitive fields)
    applicant_data JSONB NOT NULL,
    applicant_data_encrypted JSONB,
    
    -- Application status and workflow
    status VARCHAR NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'approved', 'rejected', 'talent_pool', 'withdrawn', 'hired')),
    priority VARCHAR DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    
    -- Timestamps
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID,
    talent_pool_date TIMESTAMP WITH TIME ZONE,
    hired_date TIMESTAMP WITH TIME ZONE,
    
    -- Review details
    rejection_reason TEXT,
    review_notes TEXT,
    interview_scheduled_at TIMESTAMP WITH TIME ZONE,
    
    -- Compliance and tracking
    source VARCHAR DEFAULT 'qr_code',
    duplicate_check_hash VARCHAR,
    gdpr_consent BOOLEAN DEFAULT false,
    data_retention_until TIMESTAMP WITH TIME ZONE,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    application_id UUID,
    property_id UUID NOT NULL,
    manager_id UUID,
    
    -- Employee identification
    employee_number VARCHAR UNIQUE,
    badge_number VARCHAR,
    
    -- Job information
    department VARCHAR NOT NULL,
    position VARCHAR NOT NULL,
    job_level VARCHAR,
    pay_rate DECIMAL(10,2),
    pay_frequency VARCHAR DEFAULT 'biweekly',
    employment_type VARCHAR DEFAULT 'full_time',
    
    -- Dates
    hire_date DATE NOT NULL,
    start_date DATE,
    probation_end_date DATE,
    termination_date DATE,
    
    -- Personal information (encrypted)
    personal_info JSONB DEFAULT '{}'::jsonb,
    personal_info_encrypted JSONB,
    emergency_contacts JSONB DEFAULT '[]'::jsonb,
    
    -- Status tracking
    employment_status VARCHAR DEFAULT 'active' 
        CHECK (employment_status IN ('active', 'inactive', 'terminated', 'on_leave')),
    onboarding_status VARCHAR DEFAULT 'not_started'
        CHECK (onboarding_status IN ('not_started', 'in_progress', 'employee_completed', 'manager_review', 'approved', 'rejected', 'expired')),
    
    -- Benefits and compliance
    benefits_eligible BOOLEAN DEFAULT true,
    i9_completed BOOLEAN DEFAULT false,
    w4_completed BOOLEAN DEFAULT false,
    background_check_status VARCHAR DEFAULT 'pending',
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    onboarding_completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    updated_by UUID
);

-- =====================================================
-- JUNCTION AND SUPPORTING TABLES
-- =====================================================

-- User role assignments (many-to-many)
CREATE TABLE IF NOT EXISTS user_role_assignments (
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    assigned_by UUID,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (user_id, role_id)
);

-- Property managers junction table with enhanced permissions
CREATE TABLE IF NOT EXISTS property_managers (
    property_id UUID NOT NULL,
    manager_id UUID NOT NULL,
    permissions JSONB DEFAULT '{"can_approve": true, "can_reject": true, "can_hire": true}'::jsonb,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID,
    is_primary BOOLEAN DEFAULT false,
    PRIMARY KEY (property_id, manager_id)
);

-- Application status history with detailed tracking
CREATE TABLE IF NOT EXISTS application_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL,
    old_status VARCHAR,
    new_status VARCHAR NOT NULL,
    changed_by UUID,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason TEXT,
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Compliance tracking
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR
);

-- Onboarding sessions with enhanced tracking
CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL,
    application_id UUID,
    
    -- Session management
    token VARCHAR UNIQUE NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'not_started'
        CHECK (status IN ('not_started', 'in_progress', 'employee_completed', 'manager_review', 'approved', 'rejected', 'expired')),
    current_step VARCHAR DEFAULT 'welcome',
    language_preference VARCHAR DEFAULT 'en',
    
    -- Progress tracking
    steps_completed JSONB DEFAULT '[]'::jsonb,
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Form data storage (encrypted for sensitive data)
    form_data JSONB DEFAULT '{}'::jsonb,
    form_data_encrypted JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    employee_completed_at TIMESTAMP WITH TIME ZONE,
    manager_review_started_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Review information
    reviewed_by UUID,
    manager_comments TEXT,
    rejection_reason TEXT,
    
    -- Security tracking
    ip_address INET,
    user_agent TEXT,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document management for onboarding
CREATE TABLE IF NOT EXISTS onboarding_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL,
    employee_id UUID,
    
    -- Document details
    document_type VARCHAR NOT NULL,
    document_category VARCHAR,
    file_name VARCHAR,
    file_path VARCHAR,
    file_size INTEGER,
    mime_type VARCHAR,
    
    -- Processing and OCR
    ocr_data JSONB DEFAULT '{}'::jsonb,
    processing_status VARCHAR DEFAULT 'pending',
    
    -- Form data for digital forms
    form_data JSONB DEFAULT '{}'::jsonb,
    form_data_encrypted JSONB,
    
    -- Status and review
    status VARCHAR DEFAULT 'pending' 
        CHECK (status IN ('pending', 'uploaded', 'processed', 'approved', 'rejected', 'needs_revision')),
    version INTEGER DEFAULT 1,
    
    -- Review information
    reviewed_by UUID,
    review_comments TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- Compliance tracking
    federal_form BOOLEAN DEFAULT false,
    retention_required_until DATE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System audit log
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR NOT NULL,
    record_id UUID,
    action VARCHAR NOT NULL,
    old_values JSONB,
    new_values JSONB,
    
    -- User context
    user_id UUID,
    user_email VARCHAR,
    user_role VARCHAR,
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR,
    
    -- Compliance
    compliance_event BOOLEAN DEFAULT false,
    retention_required_until DATE,
    
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INSERT DEFAULT ROLES
-- =====================================================

-- Insert default user roles
INSERT INTO user_roles (name, description, permissions, is_system_role) VALUES
('hr', 'Human Resources Administrator', '["all"]', true),
('manager', 'Property Manager', '["manage_property", "review_applications", "manage_employees"]', true),
('employee', 'Employee', '["view_own_data", "complete_onboarding"]', true)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Step 1: Core tables created successfully!';
    RAISE NOTICE '📊 Tables created: users, properties, job_applications, employees, and supporting tables';
    RAISE NOTICE '🔗 Next: Apply Step 2 (Foreign Keys and Constraints)';
END $$;