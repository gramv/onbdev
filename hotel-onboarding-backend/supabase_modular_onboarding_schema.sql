-- =====================================================
-- MODULAR EMPLOYEE ONBOARDING SYSTEM - DATABASE SCHEMA
-- Enhanced schema with form update sessions and audit trails
-- Federal compliance and modular architecture support
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =====================================================
-- ENHANCED ONBOARDING SESSIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL,
    application_id UUID,
    property_id UUID NOT NULL,
    manager_id UUID NOT NULL,
    
    -- Session management
    token VARCHAR UNIQUE NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'not_started' 
        CHECK (status IN ('not_started', 'in_progress', 'employee_completed', 'manager_review', 'hr_approval', 'approved', 'rejected', 'expired')),
    current_step VARCHAR DEFAULT 'welcome',
    phase VARCHAR DEFAULT 'employee' CHECK (phase IN ('employee', 'manager', 'hr')),
    language_preference VARCHAR DEFAULT 'en',
    
    -- Progress tracking
    steps_completed JSONB DEFAULT '[]'::jsonb,
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    total_steps INTEGER DEFAULT 18,
    
    -- Form completion tracking
    completed_forms JSONB DEFAULT '{}'::jsonb,
    required_signatures JSONB DEFAULT '{}'::jsonb,
    uploaded_documents JSONB DEFAULT '{}'::jsonb,
    
    -- Workflow timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    employee_completed_at TIMESTAMP WITH TIME ZONE,
    manager_review_started_at TIMESTAMP WITH TIME ZONE,
    hr_review_started_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Review and approval
    reviewed_by UUID, -- Manager ID
    hr_reviewed_by UUID, -- HR ID
    manager_comments TEXT,
    hr_comments TEXT,
    rejection_reason TEXT,
    
    -- Notifications and communication
    notifications_sent JSONB DEFAULT '[]'::jsonb,
    last_reminder_sent TIMESTAMP WITH TIME ZONE,
    
    -- Compliance tracking
    federal_compliance_checks JSONB DEFAULT '{}'::jsonb,
    audit_trail JSONB DEFAULT '[]'::jsonb,
    
    -- Security and access
    ip_address INET,
    user_agent TEXT,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Audit fields
    created_by UUID,
    updated_by UUID
);

-- =====================================================
-- FORM UPDATE SESSIONS TABLE (NEW)
-- =====================================================

CREATE TABLE IF NOT EXISTS form_update_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL,
    form_type VARCHAR NOT NULL 
        CHECK (form_type IN ('personal_info', 'w4_form', 'i9_section1', 'direct_deposit', 'emergency_contacts', 'health_insurance')),
    update_token VARCHAR UNIQUE NOT NULL,
    
    -- Request details
    requested_by UUID NOT NULL, -- HR user ID
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Form data
    current_data JSONB DEFAULT '{}'::jsonb,
    updated_data JSONB,
    change_reason TEXT NOT NULL,
    change_summary TEXT,
    
    -- Status and workflow
    status VARCHAR DEFAULT 'pending' 
        CHECK (status IN ('pending', 'in_progress', 'completed', 'expired', 'cancelled')),
    requires_manager_approval BOOLEAN DEFAULT false,
    requires_hr_approval BOOLEAN DEFAULT true,
    
    -- Approval tracking
    manager_approved_at TIMESTAMP WITH TIME ZONE,
    manager_approved_by UUID,
    hr_approved_at TIMESTAMP WITH TIME ZONE,
    hr_approved_by UUID,
    
    -- Notifications
    employee_notified_at TIMESTAMP WITH TIME ZONE,
    completion_notified_at TIMESTAMP WITH TIME ZONE,
    
    -- Security and audit
    ip_address INET,
    user_agent TEXT,
    audit_trail JSONB DEFAULT '[]'::jsonb,
    
    -- Compliance
    requires_signature BOOLEAN DEFAULT true,
    signature_captured BOOLEAN DEFAULT false,
    signature_data TEXT,
    
    -- Audit fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- =====================================================
-- ENHANCED EMPLOYEES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS employees_enhanced (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    employee_number VARCHAR UNIQUE,
    application_id UUID,
    property_id UUID NOT NULL,
    manager_id UUID NOT NULL,
    
    -- Employment information
    department VARCHAR NOT NULL,
    position VARCHAR NOT NULL,
    job_level VARCHAR,
    hire_date DATE NOT NULL,
    start_date DATE,
    probation_end_date DATE,
    
    -- Compensation
    pay_rate DECIMAL(10,2),
    pay_frequency VARCHAR DEFAULT 'biweekly',
    employment_type VARCHAR DEFAULT 'full_time',
    
    -- Personal information (encrypted in production)
    personal_info JSONB DEFAULT '{}'::jsonb,
    personal_info_encrypted JSONB, -- For PII encryption
    emergency_contacts JSONB DEFAULT '[]'::jsonb,
    
    -- Government forms data
    i9_data JSONB,
    w4_data JSONB,
    
    -- Benefits and policies
    health_insurance JSONB,
    direct_deposit JSONB,
    policy_acknowledgments JSONB DEFAULT '{}'::jsonb,
    
    -- Training and compliance
    trafficking_awareness_completed BOOLEAN DEFAULT false,
    trafficking_awareness_completed_at TIMESTAMP WITH TIME ZONE,
    background_check_authorized BOOLEAN DEFAULT false,
    background_check_authorized_at TIMESTAMP WITH TIME ZONE,
    weapons_policy_acknowledged BOOLEAN DEFAULT false,
    weapons_policy_acknowledged_at TIMESTAMP WITH TIME ZONE,
    
    -- Status tracking
    employment_status VARCHAR DEFAULT 'active' 
        CHECK (employment_status IN ('active', 'inactive', 'terminated', 'on_leave')),
    onboarding_status VARCHAR DEFAULT 'not_started'
        CHECK (onboarding_status IN ('not_started', 'in_progress', 'employee_completed', 'manager_review', 'hr_approval', 'approved', 'rejected', 'expired')),
    onboarding_session_id UUID,
    
    -- Benefits eligibility
    benefits_eligible BOOLEAN DEFAULT true,
    health_insurance_eligible BOOLEAN DEFAULT true,
    pto_eligible BOOLEAN DEFAULT true,
    
    -- Compliance status
    i9_completed BOOLEAN DEFAULT false,
    w4_completed BOOLEAN DEFAULT false,
    background_check_status VARCHAR DEFAULT 'pending',
    
    -- Document management
    uploaded_documents JSONB DEFAULT '{}'::jsonb,
    signatures JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    onboarding_completed_at TIMESTAMP WITH TIME ZONE,
    hired_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit and compliance
    compliance_audit_trail JSONB DEFAULT '[]'::jsonb,
    form_update_history JSONB DEFAULT '[]'::jsonb, -- Form update session IDs
    
    -- Audit fields
    created_by UUID,
    updated_by UUID
);

-- =====================================================
-- ONBOARDING DOCUMENTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS onboarding_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    employee_id UUID NOT NULL,
    document_type VARCHAR NOT NULL 
        CHECK (document_type IN ('i9_form', 'w4_form', 'direct_deposit_form', 'emergency_contacts', 'health_insurance', 'company_policies', 'background_check', 'photo_id', 'work_authorization', 'voided_check')),
    document_category VARCHAR, -- federal_form, company_policy, etc.
    
    -- File information
    file_name VARCHAR,
    file_path VARCHAR,
    file_size INTEGER,
    mime_type VARCHAR,
    
    -- Processing and OCR
    ocr_data JSONB DEFAULT '{}'::jsonb,
    processing_status VARCHAR DEFAULT 'pending',
    
    -- Form data for digital forms
    form_data JSONB DEFAULT '{}'::jsonb,
    form_data_encrypted JSONB, -- For sensitive data
    
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
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- DIGITAL SIGNATURES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS digital_signatures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES onboarding_sessions(id),
    employee_id UUID NOT NULL,
    document_id UUID REFERENCES onboarding_documents(id),
    
    -- Signature details
    signature_type VARCHAR NOT NULL 
        CHECK (signature_type IN ('employee_i9', 'employee_w4', 'employee_policies', 'employee_final', 'manager_i9', 'manager_approval', 'hr_approval')),
    signature_data TEXT NOT NULL, -- SVG or base64 image data
    signature_hash VARCHAR NOT NULL, -- For integrity verification
    
    -- Signer information
    signed_by UUID NOT NULL,
    signed_by_name VARCHAR NOT NULL,
    signed_by_role VARCHAR NOT NULL CHECK (signed_by_role IN ('hr', 'manager', 'employee')),
    
    -- Legal compliance metadata
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Verification
    is_verified BOOLEAN DEFAULT false,
    verification_method VARCHAR,
    verification_data JSONB,
    
    -- Legal attestation
    legal_attestation TEXT,
    witness_signature VARCHAR,
    witness_name VARCHAR
);

-- =====================================================
-- COMPREHENSIVE AUDIT TRAIL TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_trail (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR NOT NULL, -- onboarding_session, employee, form_update, etc.
    entity_id UUID NOT NULL,
    action VARCHAR NOT NULL, -- create, update, delete, approve, reject, etc.
    
    -- Change tracking
    old_values JSONB,
    new_values JSONB,
    changes_summary TEXT,
    
    -- User context
    user_id UUID,
    user_email VARCHAR,
    user_role VARCHAR,
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR,
    
    -- Compliance and legal
    compliance_event BOOLEAN DEFAULT false,
    legal_requirement VARCHAR,
    retention_required_until DATE,
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- COMPLIANCE CHECKS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS compliance_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_type VARCHAR NOT NULL,
    employee_id UUID NOT NULL,
    session_id UUID,
    
    -- Validation results
    status VARCHAR NOT NULL CHECK (status IN ('compliant', 'non_compliant', 'pending_review', 'requires_correction')),
    is_compliant BOOLEAN NOT NULL,
    errors JSONB DEFAULT '[]'::jsonb,
    warnings JSONB DEFAULT '[]'::jsonb,
    
    -- Legal requirements
    federal_requirements_met JSONB DEFAULT '[]'::jsonb,
    federal_requirements_failed JSONB DEFAULT '[]'::jsonb,
    
    -- Validation metadata
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validated_by UUID, -- System or user ID
    validation_version VARCHAR DEFAULT '1.0',
    
    -- Compliance notes
    compliance_notes JSONB DEFAULT '[]'::jsonb,
    legal_citations JSONB DEFAULT '[]'::jsonb
);

-- =====================================================
-- NOTIFICATION RECORDS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS notification_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipient_email VARCHAR NOT NULL,
    recipient_name VARCHAR NOT NULL,
    notification_type VARCHAR NOT NULL, -- welcome, reminder, approval_required, etc.
    
    -- Content
    subject VARCHAR NOT NULL,
    message TEXT NOT NULL,
    template_used VARCHAR,
    
    -- Context
    session_id UUID,
    employee_id UUID,
    form_update_id UUID,
    
    -- Delivery tracking
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    clicked_at TIMESTAMP WITH TIME ZONE,
    
    -- Status
    status VARCHAR DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'failed', 'bounced')),
    error_message TEXT
);

-- =====================================================
-- ONBOARDING ANALYTICS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS onboarding_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL,
    date_range_start DATE NOT NULL,
    date_range_end DATE NOT NULL,
    
    -- Completion metrics
    total_onboarding_sessions INTEGER DEFAULT 0,
    completed_sessions INTEGER DEFAULT 0,
    in_progress_sessions INTEGER DEFAULT 0,
    expired_sessions INTEGER DEFAULT 0,
    
    -- Time metrics
    avg_completion_time_hours DECIMAL(10,2),
    avg_employee_phase_hours DECIMAL(10,2),
    avg_manager_review_hours DECIMAL(10,2),
    avg_hr_approval_hours DECIMAL(10,2),
    
    -- Form update metrics
    total_form_updates INTEGER DEFAULT 0,
    completed_form_updates INTEGER DEFAULT 0,
    pending_form_updates INTEGER DEFAULT 0,
    
    -- Compliance metrics
    compliance_rate DECIMAL(5,2) DEFAULT 0.0,
    federal_violations INTEGER DEFAULT 0,
    
    -- Department breakdown
    department_breakdown JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- SYSTEM CONFIGURATION TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS onboarding_configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID, -- NULL for system-wide settings
    
    -- Session settings
    default_session_expiry_hours INTEGER DEFAULT 72,
    reminder_intervals_hours JSONB DEFAULT '[24, 48, 72]'::jsonb,
    
    -- Form update settings
    default_form_update_expiry_hours INTEGER DEFAULT 168, -- 7 days
    require_manager_approval_for_updates JSONB DEFAULT '[]'::jsonb,
    
    -- Notification settings
    send_welcome_notifications BOOLEAN DEFAULT true,
    send_reminder_notifications BOOLEAN DEFAULT true,
    send_completion_notifications BOOLEAN DEFAULT true,
    
    -- Compliance settings
    strict_federal_validation BOOLEAN DEFAULT true,
    require_digital_signatures BOOLEAN DEFAULT true,
    audit_all_actions BOOLEAN DEFAULT true,
    
    -- Language settings
    supported_languages JSONB DEFAULT '["en", "es"]'::jsonb,
    default_language VARCHAR DEFAULT 'en',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Onboarding sessions indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_token ON onboarding_sessions(token);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_employee ON onboarding_sessions(employee_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status ON onboarding_sessions(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_expires ON onboarding_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_property ON onboarding_sessions(property_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_manager ON onboarding_sessions(manager_id);

-- Form update sessions indexes
CREATE INDEX IF NOT EXISTS idx_form_update_sessions_token ON form_update_sessions(update_token);
CREATE INDEX IF NOT EXISTS idx_form_update_sessions_employee ON form_update_sessions(employee_id);
CREATE INDEX IF NOT EXISTS idx_form_update_sessions_status ON form_update_sessions(status);
CREATE INDEX IF NOT EXISTS idx_form_update_sessions_expires ON form_update_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_form_update_sessions_form_type ON form_update_sessions(form_type);

-- Enhanced employees indexes
CREATE INDEX IF NOT EXISTS idx_employees_enhanced_property ON employees_enhanced(property_id);
CREATE INDEX IF NOT EXISTS idx_employees_enhanced_manager ON employees_enhanced(manager_id);
CREATE INDEX IF NOT EXISTS idx_employees_enhanced_employee_number ON employees_enhanced(employee_number);
CREATE INDEX IF NOT EXISTS idx_employees_enhanced_status ON employees_enhanced(employment_status);
CREATE INDEX IF NOT EXISTS idx_employees_enhanced_onboarding_status ON employees_enhanced(onboarding_status);

-- Document indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_documents_session ON onboarding_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_documents_employee ON onboarding_documents(employee_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_documents_type ON onboarding_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_onboarding_documents_status ON onboarding_documents(status);

-- Signature indexes
CREATE INDEX IF NOT EXISTS idx_digital_signatures_session ON digital_signatures(session_id);
CREATE INDEX IF NOT EXISTS idx_digital_signatures_employee ON digital_signatures(employee_id);
CREATE INDEX IF NOT EXISTS idx_digital_signatures_type ON digital_signatures(signature_type);
CREATE INDEX IF NOT EXISTS idx_digital_signatures_signed_by ON digital_signatures(signed_by);

-- Audit trail indexes
CREATE INDEX IF NOT EXISTS idx_audit_trail_entity ON audit_trail(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_user_timestamp ON audit_trail(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_trail_compliance ON audit_trail(compliance_event) WHERE compliance_event = true;

-- Compliance checks indexes
CREATE INDEX IF NOT EXISTS idx_compliance_checks_employee ON compliance_checks(employee_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_session ON compliance_checks(session_id);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_form_type ON compliance_checks(form_type);
CREATE INDEX IF NOT EXISTS idx_compliance_checks_status ON compliance_checks(status);

-- Notification indexes
CREATE INDEX IF NOT EXISTS idx_notification_records_recipient ON notification_records(recipient_email);
CREATE INDEX IF NOT EXISTS idx_notification_records_session ON notification_records(session_id);
CREATE INDEX IF NOT EXISTS idx_notification_records_employee ON notification_records(employee_id);
CREATE INDEX IF NOT EXISTS idx_notification_records_type ON notification_records(notification_type);

-- Analytics indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_analytics_property_date ON onboarding_analytics(property_id, date_range_start, date_range_end);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to calculate onboarding progress
CREATE OR REPLACE FUNCTION calculate_onboarding_progress()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate progress percentage based on completed steps
    IF NEW.steps_completed IS NOT NULL THEN
        NEW.progress_percentage = (jsonb_array_length(NEW.steps_completed)::DECIMAL / NEW.total_steps) * 100.0;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to generate secure tokens
CREATE OR REPLACE FUNCTION generate_secure_token()
RETURNS TEXT AS $$
BEGIN
    RETURN encode(gen_random_bytes(32), 'base64');
END;
$$ language 'plpgsql';

-- Function to audit trail logging
CREATE OR REPLACE FUNCTION audit_trail_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_trail (entity_type, entity_id, action, old_values, user_id, timestamp)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, row_to_json(OLD), OLD.updated_by, NOW());
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_trail (entity_type, entity_id, action, old_values, new_values, user_id, timestamp)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(OLD), row_to_json(NEW), NEW.updated_by, NOW());
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_trail (entity_type, entity_id, action, new_values, user_id, timestamp)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(NEW), NEW.created_by, NOW());
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Function to generate employee number
CREATE OR REPLACE FUNCTION generate_employee_number()
RETURNS TRIGGER AS $$
DECLARE
    property_code VARCHAR(3);
    next_number INTEGER;
BEGIN
    -- Get property code (first 3 letters of property name)
    SELECT UPPER(LEFT(REGEXP_REPLACE(name, '[^A-Za-z]', '', 'g'), 3))
    INTO property_code
    FROM properties 
    WHERE id = NEW.property_id;
    
    -- Get next employee number for this property
    SELECT COALESCE(MAX(CAST(SUBSTRING(employee_number FROM 4) AS INTEGER)), 0) + 1
    INTO next_number
    FROM employees_enhanced 
    WHERE property_id = NEW.property_id 
    AND employee_number ~ ('^' || property_code || '[0-9]+$');
    
    -- Generate employee number
    NEW.employee_number = property_code || LPAD(next_number::text, 4, '0');
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Updated_at triggers
CREATE TRIGGER update_onboarding_sessions_updated_at 
    BEFORE UPDATE ON onboarding_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_form_update_sessions_updated_at 
    BEFORE UPDATE ON form_update_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employees_enhanced_updated_at 
    BEFORE UPDATE ON employees_enhanced
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_onboarding_documents_updated_at 
    BEFORE UPDATE ON onboarding_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Progress calculation trigger
CREATE TRIGGER calculate_progress_trigger 
    BEFORE UPDATE ON onboarding_sessions
    FOR EACH ROW EXECUTE FUNCTION calculate_onboarding_progress();

-- Employee number generation trigger
CREATE TRIGGER generate_employee_number_trigger 
    BEFORE INSERT ON employees_enhanced
    FOR EACH ROW WHEN (NEW.employee_number IS NULL)
    EXECUTE FUNCTION generate_employee_number();

-- Audit triggers
CREATE TRIGGER audit_onboarding_sessions_trigger
    AFTER INSERT OR UPDATE OR DELETE ON onboarding_sessions
    FOR EACH ROW EXECUTE FUNCTION audit_trail_trigger_function();

CREATE TRIGGER audit_form_update_sessions_trigger
    AFTER INSERT OR UPDATE OR DELETE ON form_update_sessions
    FOR EACH ROW EXECUTE FUNCTION audit_trail_trigger_function();

CREATE TRIGGER audit_employees_enhanced_trigger
    AFTER INSERT OR UPDATE OR DELETE ON employees_enhanced
    FOR EACH ROW EXECUTE FUNCTION audit_trail_trigger_function();

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- Comprehensive onboarding session view
CREATE OR REPLACE VIEW onboarding_session_summary AS
SELECT 
    os.*,
    e.employee_number,
    e.department,
    e.position,
    p.name as property_name,
    u_mgr.first_name as manager_first_name,
    u_mgr.last_name as manager_last_name,
    u_hr.first_name as hr_first_name,
    u_hr.last_name as hr_last_name,
    (os.personal_info->>'first_name') as employee_first_name,
    (os.personal_info->>'last_name') as employee_last_name
FROM onboarding_sessions os
LEFT JOIN employees_enhanced e ON e.id = os.employee_id
LEFT JOIN properties p ON p.id = os.property_id
LEFT JOIN users u_mgr ON u_mgr.id = os.manager_id
LEFT JOIN users u_hr ON u_hr.id = os.hr_reviewed_by;

-- Form update session summary view
CREATE OR REPLACE VIEW form_update_session_summary AS
SELECT 
    fus.*,
    e.employee_number,
    e.department,
    e.position,
    p.name as property_name,
    u_req.first_name as requested_by_first_name,
    u_req.last_name as requested_by_last_name,
    u_mgr.first_name as manager_first_name,
    u_mgr.last_name as manager_last_name,
    u_hr.first_name as hr_first_name,
    u_hr.last_name as hr_last_name
FROM form_update_sessions fus
LEFT JOIN employees_enhanced e ON e.id = fus.employee_id
LEFT JOIN properties p ON p.id = e.property_id
LEFT JOIN users u_req ON u_req.id = fus.requested_by
LEFT JOIN users u_mgr ON u_mgr.id = fus.manager_approved_by
LEFT JOIN users u_hr ON u_hr.id = fus.hr_approved_by;

-- =====================================================
-- INITIAL CONFIGURATION DATA
-- =====================================================

-- Insert default system configuration
INSERT INTO onboarding_configuration (
    property_id,
    default_session_expiry_hours,
    reminder_intervals_hours,
    default_form_update_expiry_hours,
    require_manager_approval_for_updates,
    send_welcome_notifications,
    send_reminder_notifications,
    send_completion_notifications,
    strict_federal_validation,
    require_digital_signatures,
    audit_all_actions,
    supported_languages,
    default_language
) VALUES (
    NULL, -- System-wide configuration
    72,
    '[24, 48, 72]'::jsonb,
    168,
    '["w4_form", "direct_deposit"]'::jsonb,
    true,
    true,
    true,
    true,
    true,
    true,
    '["en", "es"]'::jsonb,
    'en'
) ON CONFLICT DO NOTHING;

-- =====================================================
-- SECURITY AND CLEANUP
-- =====================================================

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_onboarding_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Update expired sessions
    UPDATE onboarding_sessions 
    SET status = 'expired', updated_at = NOW()
    WHERE expires_at < NOW() 
    AND status NOT IN ('approved', 'completed', 'expired');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired form update sessions
CREATE OR REPLACE FUNCTION cleanup_expired_form_update_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Update expired form update sessions
    UPDATE form_update_sessions 
    SET status = 'expired', updated_at = NOW()
    WHERE expires_at < NOW() 
    AND status NOT IN ('completed', 'expired', 'cancelled');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to archive old audit logs (for compliance)
CREATE OR REPLACE FUNCTION archive_old_audit_logs(retention_days INTEGER DEFAULT 2555) -- 7 years default
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    -- Move old audit logs to archive table (would be implemented based on requirements)
    -- For now, just count what would be archived
    SELECT COUNT(*)
    INTO archived_count
    FROM audit_trail
    WHERE timestamp < NOW() - INTERVAL '1 day' * retention_days
    AND retention_required_until IS NULL OR retention_required_until < CURRENT_DATE;
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- PERFORMANCE OPTIMIZATION
-- =====================================================

-- Materialized view for onboarding analytics (refresh daily)
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_onboarding_stats AS
SELECT 
    property_id,
    DATE(created_at) as onboarding_date,
    COUNT(*) as total_sessions,
    COUNT(*) FILTER (WHERE status = 'approved') as completed_count,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_count,
    COUNT(*) FILTER (WHERE status = 'expired') as expired_count,
    AVG(EXTRACT(EPOCH FROM (approved_at - created_at))/3600) as avg_completion_hours,
    AVG(EXTRACT(EPOCH FROM (employee_completed_at - created_at))/3600) as avg_employee_phase_hours,
    AVG(EXTRACT(EPOCH FROM (approved_at - manager_review_started_at))/3600) as avg_manager_review_hours
FROM onboarding_sessions
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY property_id, DATE(created_at);

-- Index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_onboarding_stats_property_date 
ON daily_onboarding_stats(property_id, onboarding_date);

-- =====================================================
-- COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON TABLE onboarding_sessions IS 'Enhanced onboarding sessions with comprehensive workflow tracking and federal compliance support';
COMMENT ON TABLE form_update_sessions IS 'Individual form update sessions for modular employee data updates without full re-onboarding';
COMMENT ON TABLE employees_enhanced IS 'Enhanced employee records with comprehensive onboarding data and compliance tracking';
COMMENT ON TABLE audit_trail IS 'Comprehensive audit trail for all system actions with federal compliance support';
COMMENT ON TABLE compliance_checks IS 'Federal compliance validation results for forms and processes';
COMMENT ON TABLE digital_signatures IS 'ESIGN Act compliant digital signatures with legal metadata';

-- Schema creation complete
SELECT 'Modular Employee Onboarding Schema Created Successfully' as status;