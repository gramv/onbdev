-- Performance Optimization Indexes for Hotel Onboarding System
-- This script creates indexes on frequently queried fields to improve query performance
-- Version: 1.0.0
-- Created: 2025-08-06

-- ================================================================================
-- STEP 1: Property-Related Indexes
-- ================================================================================

-- Properties table indexes
CREATE INDEX IF NOT EXISTS idx_properties_is_active 
ON properties(is_active)
WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_properties_created_at 
ON properties(created_at DESC);

-- Property managers junction table - critical for access control
CREATE INDEX IF NOT EXISTS idx_property_managers_manager_id 
ON property_managers(manager_id);

CREATE INDEX IF NOT EXISTS idx_property_managers_property_id 
ON property_managers(property_id);

CREATE INDEX IF NOT EXISTS idx_property_managers_is_active 
ON property_managers(is_active)
WHERE is_active = true;

-- Composite index for manager property lookups (most common query)
CREATE INDEX IF NOT EXISTS idx_property_managers_composite 
ON property_managers(manager_id, property_id, is_active)
WHERE is_active = true;

-- ================================================================================
-- STEP 2: Job Applications Indexes
-- ================================================================================

-- Basic indexes
CREATE INDEX IF NOT EXISTS idx_job_applications_property_id 
ON job_applications(property_id);

CREATE INDEX IF NOT EXISTS idx_job_applications_status 
ON job_applications(status);

CREATE INDEX IF NOT EXISTS idx_job_applications_created_at 
ON job_applications(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_job_applications_property_status 
ON job_applications(property_id, status, created_at DESC);

-- Partial index for pending applications (frequently queried)
CREATE INDEX IF NOT EXISTS idx_job_applications_pending 
ON job_applications(property_id, created_at DESC)
WHERE status = 'pending';

-- Partial index for approved applications
CREATE INDEX IF NOT EXISTS idx_job_applications_approved 
ON job_applications(property_id, created_at DESC)
WHERE status = 'approved';

-- Index for talent pool queries
CREATE INDEX IF NOT EXISTS idx_job_applications_talent_pool 
ON job_applications(property_id, talent_pool_date DESC)
WHERE status = 'talent_pool';

-- Full-text search index for applicant data (JSONB)
CREATE INDEX IF NOT EXISTS idx_job_applications_applicant_search 
ON job_applications 
USING GIN(to_tsvector('english', applicant_data::text));

-- JSONB index for applicant data queries
CREATE INDEX IF NOT EXISTS idx_job_applications_applicant_data 
ON job_applications 
USING GIN(applicant_data);

-- ================================================================================
-- STEP 3: Employees Table Indexes
-- ================================================================================

-- Basic indexes
CREATE INDEX IF NOT EXISTS idx_employees_property_id 
ON employees(property_id);

CREATE INDEX IF NOT EXISTS idx_employees_status 
ON employees(status);

CREATE INDEX IF NOT EXISTS idx_employees_created_at 
ON employees(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_employees_email 
ON employees(email);

-- Composite indexes
CREATE INDEX IF NOT EXISTS idx_employees_property_status 
ON employees(property_id, status, created_at DESC);

-- Partial index for active employees
CREATE INDEX IF NOT EXISTS idx_employees_active 
ON employees(property_id, created_at DESC)
WHERE status = 'active';

-- Full-text search for employee names
CREATE INDEX IF NOT EXISTS idx_employees_name_search 
ON employees 
USING GIN(to_tsvector('english', first_name || ' ' || last_name));

-- ================================================================================
-- STEP 4: Onboarding Sessions Indexes
-- ================================================================================

-- Basic indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_property_id 
ON onboarding_sessions(property_id);

CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_employee_id 
ON onboarding_sessions(employee_id);

CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status 
ON onboarding_sessions(status);

CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_created_at 
ON onboarding_sessions(created_at DESC);

-- Composite indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_property_status 
ON onboarding_sessions(property_id, status, created_at DESC);

-- Partial index for sessions needing manager review
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_manager_review 
ON onboarding_sessions(property_id, created_at DESC)
WHERE status = 'employee_completed';

-- Partial index for sessions needing HR review
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_hr_review 
ON onboarding_sessions(created_at DESC)
WHERE status = 'manager_approved';

-- Progress tracking index
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_progress 
ON onboarding_sessions(progress_percentage, updated_at DESC);

-- ================================================================================
-- STEP 5: Onboarding Tokens Indexes
-- ================================================================================

CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_employee_id 
ON onboarding_tokens(employee_id);

CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_token 
ON onboarding_tokens(token);

CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_expires_at 
ON onboarding_tokens(expires_at);

-- Partial index for valid tokens
CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_valid 
ON onboarding_tokens(token, employee_id)
WHERE expires_at > NOW();

-- ================================================================================
-- STEP 6: Managers Table Indexes
-- ================================================================================

CREATE INDEX IF NOT EXISTS idx_managers_email 
ON managers(email);

CREATE INDEX IF NOT EXISTS idx_managers_is_active 
ON managers(is_active)
WHERE is_active = true;

-- Full-text search for manager names
CREATE INDEX IF NOT EXISTS idx_managers_name_search 
ON managers 
USING GIN(to_tsvector('english', first_name || ' ' || last_name));

-- ================================================================================
-- STEP 7: Employee Forms Indexes (if table exists)
-- ================================================================================

-- Check if table exists before creating indexes
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' 
               AND table_name = 'employee_forms') THEN
        
        CREATE INDEX IF NOT EXISTS idx_employee_forms_employee_id 
        ON employee_forms(employee_id);
        
        CREATE INDEX IF NOT EXISTS idx_employee_forms_form_type 
        ON employee_forms(form_type);
        
        CREATE INDEX IF NOT EXISTS idx_employee_forms_signed 
        ON employee_forms(signed)
        WHERE signed = true;
        
        CREATE INDEX IF NOT EXISTS idx_employee_forms_created_at 
        ON employee_forms(created_at DESC);
        
        -- Composite index for common queries
        CREATE INDEX IF NOT EXISTS idx_employee_forms_employee_type 
        ON employee_forms(employee_id, form_type, signed);
    END IF;
END $$;

-- ================================================================================
-- STEP 8: Employee Documents Indexes (if table exists)
-- ================================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' 
               AND table_name = 'employee_documents') THEN
        
        CREATE INDEX IF NOT EXISTS idx_employee_documents_employee_id 
        ON employee_documents(employee_id);
        
        CREATE INDEX IF NOT EXISTS idx_employee_documents_document_type 
        ON employee_documents(document_type);
        
        CREATE INDEX IF NOT EXISTS idx_employee_documents_created_at 
        ON employee_documents(created_at DESC);
        
        -- Composite index
        CREATE INDEX IF NOT EXISTS idx_employee_documents_employee_type 
        ON employee_documents(employee_id, document_type, created_at DESC);
    END IF;
END $$;

-- ================================================================================
-- STEP 9: Audit Logs Indexes (if table exists)
-- ================================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' 
               AND table_name = 'audit_logs') THEN
        
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id 
        ON audit_logs(user_id);
        
        CREATE INDEX IF NOT EXISTS idx_audit_logs_entity 
        ON audit_logs(entity_type, entity_id);
        
        CREATE INDEX IF NOT EXISTS idx_audit_logs_property_id 
        ON audit_logs(property_id);
        
        CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at 
        ON audit_logs(created_at DESC);
        
        CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
        ON audit_logs(action);
        
        -- Composite index for user activity queries
        CREATE INDEX IF NOT EXISTS idx_audit_logs_user_activity 
        ON audit_logs(user_id, created_at DESC);
        
        -- Composite index for entity history queries
        CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_history 
        ON audit_logs(entity_type, entity_id, created_at DESC);
    END IF;
END $$;

-- ================================================================================
-- STEP 10: HR Users Table Indexes
-- ================================================================================

CREATE INDEX IF NOT EXISTS idx_hr_users_email 
ON hr_users(email);

CREATE INDEX IF NOT EXISTS idx_hr_users_is_active 
ON hr_users(is_active)
WHERE is_active = true;

-- ================================================================================
-- STEP 11: Analyze Tables for Query Optimization
-- ================================================================================

-- Update table statistics for query planner
ANALYZE properties;
ANALYZE property_managers;
ANALYZE job_applications;
ANALYZE employees;
ANALYZE onboarding_sessions;
ANALYZE onboarding_tokens;
ANALYZE managers;
ANALYZE hr_users;

-- Analyze conditional tables if they exist
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' 
               AND table_name = 'employee_forms') THEN
        ANALYZE employee_forms;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' 
               AND table_name = 'employee_documents') THEN
        ANALYZE employee_documents;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_schema = 'public' 
               AND table_name = 'audit_logs') THEN
        ANALYZE audit_logs;
    END IF;
END $$;

-- ================================================================================
-- STEP 12: Verify Indexes Were Created
-- ================================================================================

-- Query to list all indexes on key tables
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN (
    'properties', 'property_managers', 'job_applications', 
    'employees', 'onboarding_sessions', 'onboarding_tokens',
    'managers', 'hr_users', 'employee_forms', 'employee_documents',
    'audit_logs'
)
ORDER BY tablename, indexname;

-- ================================================================================
-- PERFORMANCE TUNING NOTES:
-- ================================================================================
-- 1. These indexes are designed to optimize the most common query patterns
-- 2. Partial indexes are used where appropriate to reduce index size
-- 3. GIN indexes are used for JSONB and full-text search
-- 4. Composite indexes are ordered by selectivity (most selective first)
-- 5. ANALYZE is run after index creation to update statistics
-- 
-- Monitor slow queries and add additional indexes as needed:
-- - Enable slow query logging in PostgreSQL
-- - Use EXPLAIN ANALYZE to identify missing indexes
-- - Consider index-only scans for frequently accessed columns
--
-- Maintenance:
-- - Run VACUUM ANALYZE regularly (daily recommended)
-- - Monitor index bloat and REINDEX if necessary
-- - Review and drop unused indexes periodically
-- ================================================================================