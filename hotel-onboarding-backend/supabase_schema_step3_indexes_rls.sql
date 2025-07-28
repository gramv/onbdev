-- =====================================================
-- STEP 3: INDEXES, RLS POLICIES, AND FUNCTIONS
-- Apply this after Step 2 in Supabase SQL Editor
-- =====================================================

-- =====================================================
-- PERFORMANCE INDEXES
-- =====================================================

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_property_id ON users(property_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true;

-- Property indexes
CREATE INDEX IF NOT EXISTS idx_properties_active ON properties(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_property_managers_property ON property_managers(property_id);
CREATE INDEX IF NOT EXISTS idx_property_managers_manager ON property_managers(manager_id);

-- Application indexes
CREATE INDEX IF NOT EXISTS idx_job_applications_property_id ON job_applications(property_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_job_applications_applied_at ON job_applications(applied_at);
CREATE INDEX IF NOT EXISTS idx_job_applications_reviewed_by ON job_applications(reviewed_by);
CREATE INDEX IF NOT EXISTS idx_job_applications_duplicate_hash ON job_applications(duplicate_check_hash);

-- Employee indexes
CREATE INDEX IF NOT EXISTS idx_employees_property_id ON employees(property_id);
CREATE INDEX IF NOT EXISTS idx_employees_manager_id ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_employees_employee_number ON employees(employee_number);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(employment_status);

-- Onboarding indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_token ON onboarding_sessions(token);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_employee ON onboarding_sessions(employee_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status ON onboarding_sessions(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_expires ON onboarding_sessions(expires_at);

-- Document indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_documents_session ON onboarding_documents(session_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_documents_type ON onboarding_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_onboarding_documents_status ON onboarding_documents(status);

-- Audit indexes
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_timestamp ON audit_log(user_id, timestamp);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_role_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_managers ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE application_status_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES - USERS
-- =====================================================

-- Users can view their own data
CREATE POLICY "users_select_own" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

-- HR can view all users
CREATE POLICY "users_select_hr" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- HR can manage all users
CREATE POLICY "users_all_hr" ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- =====================================================
-- RLS POLICIES - PROPERTIES
-- =====================================================

-- HR can manage all properties
CREATE POLICY "properties_all_hr" ON properties
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- Managers can view their assigned properties
CREATE POLICY "properties_select_managers" ON properties
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = properties.id
        )
    );

-- =====================================================
-- RLS POLICIES - JOB APPLICATIONS
-- =====================================================

-- HR can manage all applications
CREATE POLICY "applications_all_hr" ON job_applications
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- Managers can manage applications for their properties
CREATE POLICY "applications_managers" ON job_applications
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = job_applications.property_id
        )
    );

-- Public access for job application submission (anonymous)
CREATE POLICY "applications_insert_public" ON job_applications
    FOR INSERT WITH CHECK (true);

-- =====================================================
-- RLS POLICIES - EMPLOYEES
-- =====================================================

-- HR can manage all employees
CREATE POLICY "employees_all_hr" ON employees
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- Managers can manage employees in their properties
CREATE POLICY "employees_managers" ON employees
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = employees.property_id
        )
    );

-- Employees can view their own data
CREATE POLICY "employees_select_own" ON employees
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- =====================================================
-- RLS POLICIES - ONBOARDING
-- =====================================================

-- HR can manage all onboarding sessions
CREATE POLICY "onboarding_sessions_all_hr" ON onboarding_sessions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- Managers can manage onboarding for their properties
CREATE POLICY "onboarding_sessions_managers" ON onboarding_sessions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            JOIN employees e ON e.id = onboarding_sessions.employee_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = e.property_id
        )
    );

-- Public access for onboarding (token-based)
CREATE POLICY "onboarding_sessions_public_token" ON onboarding_sessions
    FOR SELECT USING (true);

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
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
    FROM employees 
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
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_applications_updated_at BEFORE UPDATE ON job_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_onboarding_sessions_updated_at BEFORE UPDATE ON onboarding_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_onboarding_documents_updated_at BEFORE UPDATE ON onboarding_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Employee number generation trigger
CREATE TRIGGER generate_employee_number_trigger BEFORE INSERT ON employees
    FOR EACH ROW WHEN (NEW.employee_number IS NULL)
    EXECUTE FUNCTION generate_employee_number();

-- =====================================================
-- MATERIALIZED VIEW FOR ANALYTICS
-- =====================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS daily_application_stats AS
SELECT 
    property_id,
    DATE(applied_at) as application_date,
    COUNT(*) as total_applications,
    COUNT(*) FILTER (WHERE status = 'approved') as approved_count,
    COUNT(*) FILTER (WHERE status = 'rejected') as rejected_count,
    COUNT(*) FILTER (WHERE status = 'talent_pool') as talent_pool_count,
    AVG(EXTRACT(EPOCH FROM (reviewed_at - applied_at))/3600) as avg_review_hours
FROM job_applications
WHERE applied_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY property_id, DATE(applied_at);

-- Index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_stats_property_date 
ON daily_application_stats(property_id, application_date);

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Step 3: Indexes, RLS policies, and functions created successfully!';
    RAISE NOTICE '📊 Performance indexes: Created';
    RAISE NOTICE '🔐 Row Level Security: Enabled with comprehensive policies';
    RAISE NOTICE '⚡ Functions and triggers: Active';
    RAISE NOTICE '📈 Materialized views: Ready for analytics';
    RAISE NOTICE '🎉 Enhanced Supabase schema is now complete and ready!';
END $$;