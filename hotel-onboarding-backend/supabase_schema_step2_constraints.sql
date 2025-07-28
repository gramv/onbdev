-- =====================================================
-- STEP 2: ADD FOREIGN KEYS AND CONSTRAINTS
-- Apply this after Step 1 in Supabase SQL Editor
-- =====================================================

-- =====================================================
-- ADD FOREIGN KEY CONSTRAINTS
-- =====================================================

-- Users table foreign keys
ALTER TABLE users 
ADD CONSTRAINT fk_users_property_id 
FOREIGN KEY (property_id) REFERENCES properties(id);

ALTER TABLE users 
ADD CONSTRAINT fk_users_created_by 
FOREIGN KEY (created_by) REFERENCES users(id);

ALTER TABLE users 
ADD CONSTRAINT fk_users_updated_by 
FOREIGN KEY (updated_by) REFERENCES users(id);

-- Properties table foreign keys
ALTER TABLE properties 
ADD CONSTRAINT fk_properties_created_by 
FOREIGN KEY (created_by) REFERENCES users(id);

ALTER TABLE properties 
ADD CONSTRAINT fk_properties_updated_by 
FOREIGN KEY (updated_by) REFERENCES users(id);

-- Job applications foreign keys
ALTER TABLE job_applications 
ADD CONSTRAINT fk_job_applications_property_id 
FOREIGN KEY (property_id) REFERENCES properties(id);

ALTER TABLE job_applications 
ADD CONSTRAINT fk_job_applications_reviewed_by 
FOREIGN KEY (reviewed_by) REFERENCES users(id);

ALTER TABLE job_applications 
ADD CONSTRAINT fk_job_applications_created_by 
FOREIGN KEY (created_by) REFERENCES users(id);

ALTER TABLE job_applications 
ADD CONSTRAINT fk_job_applications_updated_by 
FOREIGN KEY (updated_by) REFERENCES users(id);

-- Employees foreign keys
ALTER TABLE employees 
ADD CONSTRAINT fk_employees_user_id 
FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE employees 
ADD CONSTRAINT fk_employees_application_id 
FOREIGN KEY (application_id) REFERENCES job_applications(id);

ALTER TABLE employees 
ADD CONSTRAINT fk_employees_property_id 
FOREIGN KEY (property_id) REFERENCES properties(id);

ALTER TABLE employees 
ADD CONSTRAINT fk_employees_manager_id 
FOREIGN KEY (manager_id) REFERENCES users(id);

ALTER TABLE employees 
ADD CONSTRAINT fk_employees_created_by 
FOREIGN KEY (created_by) REFERENCES users(id);

ALTER TABLE employees 
ADD CONSTRAINT fk_employees_updated_by 
FOREIGN KEY (updated_by) REFERENCES users(id);

-- User role assignments foreign keys
ALTER TABLE user_role_assignments 
ADD CONSTRAINT fk_user_role_assignments_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE user_role_assignments 
ADD CONSTRAINT fk_user_role_assignments_role_id 
FOREIGN KEY (role_id) REFERENCES user_roles(id) ON DELETE CASCADE;

ALTER TABLE user_role_assignments 
ADD CONSTRAINT fk_user_role_assignments_assigned_by 
FOREIGN KEY (assigned_by) REFERENCES users(id);

-- Property managers foreign keys
ALTER TABLE property_managers 
ADD CONSTRAINT fk_property_managers_property_id 
FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE;

ALTER TABLE property_managers 
ADD CONSTRAINT fk_property_managers_manager_id 
FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE property_managers 
ADD CONSTRAINT fk_property_managers_assigned_by 
FOREIGN KEY (assigned_by) REFERENCES users(id);

-- Application status history foreign keys
ALTER TABLE application_status_history 
ADD CONSTRAINT fk_application_status_history_application_id 
FOREIGN KEY (application_id) REFERENCES job_applications(id) ON DELETE CASCADE;

ALTER TABLE application_status_history 
ADD CONSTRAINT fk_application_status_history_changed_by 
FOREIGN KEY (changed_by) REFERENCES users(id);

-- Onboarding sessions foreign keys
ALTER TABLE onboarding_sessions 
ADD CONSTRAINT fk_onboarding_sessions_employee_id 
FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;

ALTER TABLE onboarding_sessions 
ADD CONSTRAINT fk_onboarding_sessions_application_id 
FOREIGN KEY (application_id) REFERENCES job_applications(id);

ALTER TABLE onboarding_sessions 
ADD CONSTRAINT fk_onboarding_sessions_reviewed_by 
FOREIGN KEY (reviewed_by) REFERENCES users(id);

-- Onboarding documents foreign keys
ALTER TABLE onboarding_documents 
ADD CONSTRAINT fk_onboarding_documents_session_id 
FOREIGN KEY (session_id) REFERENCES onboarding_sessions(id) ON DELETE CASCADE;

ALTER TABLE onboarding_documents 
ADD CONSTRAINT fk_onboarding_documents_employee_id 
FOREIGN KEY (employee_id) REFERENCES employees(id);

ALTER TABLE onboarding_documents 
ADD CONSTRAINT fk_onboarding_documents_reviewed_by 
FOREIGN KEY (reviewed_by) REFERENCES users(id);

-- Audit log foreign keys
ALTER TABLE audit_log 
ADD CONSTRAINT fk_audit_log_user_id 
FOREIGN KEY (user_id) REFERENCES users(id);

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Step 2: Foreign keys and constraints added successfully!';
    RAISE NOTICE '🔗 All table relationships established';
    RAISE NOTICE '🔗 Next: Apply Step 3 (Indexes and Performance)';
END $$;