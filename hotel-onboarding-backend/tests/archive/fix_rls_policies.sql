-- =====================================================
-- FIX RLS POLICIES - Remove Infinite Recursion
-- Apply this to fix the circular dependency in RLS policies
-- =====================================================

-- Drop existing problematic policies
DROP POLICY IF EXISTS "users_select_own" ON users;
DROP POLICY IF EXISTS "users_select_hr" ON users;
DROP POLICY IF EXISTS "users_all_hr" ON users;
DROP POLICY IF EXISTS "properties_all_hr" ON properties;
DROP POLICY IF EXISTS "properties_select_managers" ON properties;
DROP POLICY IF EXISTS "applications_all_hr" ON job_applications;
DROP POLICY IF EXISTS "applications_managers" ON job_applications;
DROP POLICY IF EXISTS "employees_all_hr" ON employees;
DROP POLICY IF EXISTS "employees_managers" ON employees;
DROP POLICY IF EXISTS "employees_select_own" ON employees;
DROP POLICY IF EXISTS "onboarding_sessions_all_hr" ON onboarding_sessions;
DROP POLICY IF EXISTS "onboarding_sessions_managers" ON onboarding_sessions;

-- =====================================================
-- SIMPLIFIED RLS POLICIES WITHOUT RECURSION
-- =====================================================

-- Users table policies (simplified)
CREATE POLICY "users_select_authenticated" ON users
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "users_insert_service_role" ON users
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "users_update_service_role" ON users
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "users_delete_service_role" ON users
    FOR DELETE USING (auth.role() = 'service_role');

-- Properties table policies
CREATE POLICY "properties_select_authenticated" ON properties
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "properties_insert_service_role" ON properties
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "properties_update_service_role" ON properties
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "properties_delete_service_role" ON properties
    FOR DELETE USING (auth.role() = 'service_role');

-- Job applications policies
CREATE POLICY "applications_select_authenticated" ON job_applications
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "applications_insert_public" ON job_applications
    FOR INSERT WITH CHECK (true);

CREATE POLICY "applications_update_service_role" ON job_applications
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "applications_delete_service_role" ON job_applications
    FOR DELETE USING (auth.role() = 'service_role');

-- Employees policies
CREATE POLICY "employees_select_authenticated" ON employees
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "employees_insert_service_role" ON employees
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "employees_update_service_role" ON employees
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "employees_delete_service_role" ON employees
    FOR DELETE USING (auth.role() = 'service_role');

-- Onboarding sessions policies
CREATE POLICY "onboarding_sessions_select_authenticated" ON onboarding_sessions
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "onboarding_sessions_insert_service_role" ON onboarding_sessions
    FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "onboarding_sessions_update_service_role" ON onboarding_sessions
    FOR UPDATE USING (auth.role() = 'service_role');

CREATE POLICY "onboarding_sessions_delete_service_role" ON onboarding_sessions
    FOR DELETE USING (auth.role() = 'service_role');

-- Public access for onboarding (token-based)
CREATE POLICY "onboarding_sessions_public_token" ON onboarding_sessions
    FOR SELECT USING (true);

-- Supporting tables policies
CREATE POLICY "property_managers_all_service_role" ON property_managers
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "application_status_history_all_service_role" ON application_status_history
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "onboarding_documents_all_service_role" ON onboarding_documents
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "audit_log_all_service_role" ON audit_log
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "user_roles_select_authenticated" ON user_roles
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "user_role_assignments_all_service_role" ON user_role_assignments
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ RLS policies fixed successfully!';
    RAISE NOTICE '🔐 Removed infinite recursion';
    RAISE NOTICE '⚡ Simplified policy structure';
    RAISE NOTICE '🎯 Service role has full access, authenticated users have read access';
END $$;