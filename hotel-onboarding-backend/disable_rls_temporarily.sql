-- =====================================================
-- TEMPORARILY DISABLE RLS FOR DEVELOPMENT
-- This allows the system to work while we develop proper policies
-- =====================================================

-- Disable RLS on all tables temporarily
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_role_assignments DISABLE ROW LEVEL SECURITY;
ALTER TABLE properties DISABLE ROW LEVEL SECURITY;
ALTER TABLE property_managers DISABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications DISABLE ROW LEVEL SECURITY;
ALTER TABLE application_status_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE employees DISABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_documents DISABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log DISABLE ROW LEVEL SECURITY;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '⚠️  RLS temporarily disabled for development';
    RAISE NOTICE '🔧 This allows the system to work during setup';
    RAISE NOTICE '🔐 Remember to re-enable RLS for production';
END $$;