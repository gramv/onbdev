-- Comprehensive Row Level Security (RLS) Fix for Property-Based Access Control
-- This script fixes all RLS policies to ensure managers can only access data from their assigned properties
-- while HR users can access all data

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================================================
-- STEP 1: Enable RLS on all relevant tables
-- ================================================================================

ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE managers ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_managers ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_documents ENABLE ROW LEVEL SECURITY;

-- ================================================================================
-- STEP 2: Drop all existing policies to start fresh
-- ================================================================================

-- Properties table policies
DROP POLICY IF EXISTS "properties_select_policy" ON properties;
DROP POLICY IF EXISTS "properties_insert_policy" ON properties;
DROP POLICY IF EXISTS "properties_update_policy" ON properties;
DROP POLICY IF EXISTS "properties_delete_policy" ON properties;
DROP POLICY IF EXISTS "properties_policy" ON properties;

-- Managers table policies
DROP POLICY IF EXISTS "managers_select_policy" ON managers;
DROP POLICY IF EXISTS "managers_insert_policy" ON managers;
DROP POLICY IF EXISTS "managers_update_policy" ON managers;
DROP POLICY IF EXISTS "managers_delete_policy" ON managers;
DROP POLICY IF EXISTS "managers_policy" ON managers;

-- Property managers table policies
DROP POLICY IF EXISTS "property_managers_select_policy" ON property_managers;
DROP POLICY IF EXISTS "property_managers_insert_policy" ON property_managers;
DROP POLICY IF EXISTS "property_managers_update_policy" ON property_managers;
DROP POLICY IF EXISTS "property_managers_delete_policy" ON property_managers;
DROP POLICY IF EXISTS "property_managers_policy" ON property_managers;

-- Job applications table policies
DROP POLICY IF EXISTS "job_applications_select_policy" ON job_applications;
DROP POLICY IF EXISTS "job_applications_insert_policy" ON job_applications;
DROP POLICY IF EXISTS "job_applications_update_policy" ON job_applications;
DROP POLICY IF EXISTS "job_applications_delete_policy" ON job_applications;
DROP POLICY IF EXISTS "job_applications_policy" ON job_applications;

-- Employees table policies
DROP POLICY IF EXISTS "employees_select_policy" ON employees;
DROP POLICY IF EXISTS "employees_insert_policy" ON employees;
DROP POLICY IF EXISTS "employees_update_policy" ON employees;
DROP POLICY IF EXISTS "employees_delete_policy" ON employees;
DROP POLICY IF EXISTS "employees_policy" ON employees;

-- Onboarding sessions table policies
DROP POLICY IF EXISTS "onboarding_sessions_select_policy" ON onboarding_sessions;
DROP POLICY IF EXISTS "onboarding_sessions_insert_policy" ON onboarding_sessions;
DROP POLICY IF EXISTS "onboarding_sessions_update_policy" ON onboarding_sessions;
DROP POLICY IF EXISTS "onboarding_sessions_delete_policy" ON onboarding_sessions;
DROP POLICY IF EXISTS "onboarding_sessions_policy" ON onboarding_sessions;

-- Onboarding tokens table policies
DROP POLICY IF EXISTS "onboarding_tokens_select_policy" ON onboarding_tokens;
DROP POLICY IF EXISTS "onboarding_tokens_insert_policy" ON onboarding_tokens;
DROP POLICY IF EXISTS "onboarding_tokens_update_policy" ON onboarding_tokens;
DROP POLICY IF EXISTS "onboarding_tokens_delete_policy" ON onboarding_tokens;
DROP POLICY IF EXISTS "onboarding_tokens_policy" ON onboarding_tokens;

-- Employee forms table policies
DROP POLICY IF EXISTS "employee_forms_select_policy" ON employee_forms;
DROP POLICY IF EXISTS "employee_forms_insert_policy" ON employee_forms;
DROP POLICY IF EXISTS "employee_forms_update_policy" ON employee_forms;
DROP POLICY IF EXISTS "employee_forms_delete_policy" ON employee_forms;
DROP POLICY IF EXISTS "employee_forms_policy" ON employee_forms;

-- Employee documents table policies
DROP POLICY IF EXISTS "employee_documents_select_policy" ON employee_documents;
DROP POLICY IF EXISTS "employee_documents_insert_policy" ON employee_documents;
DROP POLICY IF EXISTS "employee_documents_update_policy" ON employee_documents;
DROP POLICY IF EXISTS "employee_documents_delete_policy" ON employee_documents;
DROP POLICY IF EXISTS "employee_documents_policy" ON employee_documents;

-- ================================================================================
-- STEP 3: Create helper functions for access control
-- ================================================================================

-- Function to check if the current user is an HR user
CREATE OR REPLACE FUNCTION is_hr_user()
RETURNS BOOLEAN AS $$
BEGIN
  -- Check if the JWT has user_type = 'hr'
  RETURN auth.jwt() ->> 'user_type' = 'hr';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if the current user is a manager
CREATE OR REPLACE FUNCTION is_manager_user()
RETURNS BOOLEAN AS $$
BEGIN
  -- Check if the JWT has user_type = 'manager'
  RETURN auth.jwt() ->> 'user_type' = 'manager';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get the current user's manager ID
CREATE OR REPLACE FUNCTION current_manager_id()
RETURNS UUID AS $$
BEGIN
  -- Return the manager_id from JWT if user is a manager
  IF auth.jwt() ->> 'user_type' = 'manager' THEN
    RETURN (auth.jwt() ->> 'user_id')::uuid;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if a manager has access to a specific property
CREATE OR REPLACE FUNCTION manager_has_property_access(property_id_param UUID)
RETURNS BOOLEAN AS $$
BEGIN
  -- HR users have access to all properties
  IF is_hr_user() THEN
    RETURN TRUE;
  END IF;
  
  -- Check if manager is assigned to this property
  IF is_manager_user() THEN
    RETURN EXISTS (
      SELECT 1 FROM property_managers pm
      WHERE pm.manager_id = current_manager_id()
      AND pm.property_id = property_id_param
      AND pm.is_active = true
    );
  END IF;
  
  RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================================================
-- STEP 4: Create new RLS policies for each table
-- ================================================================================

-- PROPERTIES TABLE POLICIES
-- HR can see all properties, managers can only see their assigned properties
CREATE POLICY "properties_select_policy" ON properties
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM property_managers pm
      WHERE pm.property_id = properties.id
      AND pm.manager_id = current_manager_id()
      AND pm.is_active = true
    ))
  );

-- Only HR can insert properties
CREATE POLICY "properties_insert_policy" ON properties
  FOR INSERT
  WITH CHECK (is_hr_user());

-- Only HR can update properties
CREATE POLICY "properties_update_policy" ON properties
  FOR UPDATE
  USING (is_hr_user())
  WITH CHECK (is_hr_user());

-- Only HR can delete properties
CREATE POLICY "properties_delete_policy" ON properties
  FOR DELETE
  USING (is_hr_user());

-- MANAGERS TABLE POLICIES
-- HR can see all managers, managers can only see themselves
CREATE POLICY "managers_select_policy" ON managers
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND id = current_manager_id())
  );

-- Only HR can insert managers
CREATE POLICY "managers_insert_policy" ON managers
  FOR INSERT
  WITH CHECK (is_hr_user());

-- HR can update all managers, managers can update themselves
CREATE POLICY "managers_update_policy" ON managers
  FOR UPDATE
  USING (
    is_hr_user() OR 
    (is_manager_user() AND id = current_manager_id())
  )
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND id = current_manager_id())
  );

-- Only HR can delete managers
CREATE POLICY "managers_delete_policy" ON managers
  FOR DELETE
  USING (is_hr_user());

-- PROPERTY_MANAGERS TABLE POLICIES
-- HR can see all assignments, managers can see their own assignments
CREATE POLICY "property_managers_select_policy" ON property_managers
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND manager_id = current_manager_id())
  );

-- Only HR can insert property-manager assignments
CREATE POLICY "property_managers_insert_policy" ON property_managers
  FOR INSERT
  WITH CHECK (is_hr_user());

-- Only HR can update property-manager assignments
CREATE POLICY "property_managers_update_policy" ON property_managers
  FOR UPDATE
  USING (is_hr_user())
  WITH CHECK (is_hr_user());

-- Only HR can delete property-manager assignments
CREATE POLICY "property_managers_delete_policy" ON property_managers
  FOR DELETE
  USING (is_hr_user());

-- JOB_APPLICATIONS TABLE POLICIES
-- HR can see all applications, managers can only see applications for their properties
CREATE POLICY "job_applications_select_policy" ON job_applications
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  );

-- Anyone can insert job applications (public facing)
CREATE POLICY "job_applications_insert_policy" ON job_applications
  FOR INSERT
  WITH CHECK (true);

-- HR can update all applications, managers can update applications for their properties
CREATE POLICY "job_applications_update_policy" ON job_applications
  FOR UPDATE
  USING (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  )
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  );

-- Only HR can delete applications
CREATE POLICY "job_applications_delete_policy" ON job_applications
  FOR DELETE
  USING (is_hr_user());

-- EMPLOYEES TABLE POLICIES
-- HR can see all employees, managers can only see employees from their properties
CREATE POLICY "employees_select_policy" ON employees
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  );

-- HR can insert all employees, managers can insert employees for their properties
CREATE POLICY "employees_insert_policy" ON employees
  FOR INSERT
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  );

-- HR can update all employees, managers can update employees for their properties
CREATE POLICY "employees_update_policy" ON employees
  FOR UPDATE
  USING (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  )
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  );

-- Only HR can delete employees
CREATE POLICY "employees_delete_policy" ON employees
  FOR DELETE
  USING (is_hr_user());

-- ONBOARDING_SESSIONS TABLE POLICIES
-- HR can see all sessions, managers can only see sessions for their properties
CREATE POLICY "onboarding_sessions_select_policy" ON onboarding_sessions
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  );

-- HR can insert all sessions, managers can insert sessions for their properties
CREATE POLICY "onboarding_sessions_insert_policy" ON onboarding_sessions
  FOR INSERT
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  );

-- HR can update all sessions, managers can update sessions for their properties
CREATE POLICY "onboarding_sessions_update_policy" ON onboarding_sessions
  FOR UPDATE
  USING (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  )
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND manager_has_property_access(property_id))
  );

-- Only HR can delete sessions
CREATE POLICY "onboarding_sessions_delete_policy" ON onboarding_sessions
  FOR DELETE
  USING (is_hr_user());

-- ONBOARDING_TOKENS TABLE POLICIES
-- HR can see all tokens, managers can only see tokens for their properties
CREATE POLICY "onboarding_tokens_select_policy" ON onboarding_tokens
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = onboarding_tokens.employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- HR can insert all tokens, managers can insert tokens for employees in their properties
CREATE POLICY "onboarding_tokens_insert_policy" ON onboarding_tokens
  FOR INSERT
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- HR can update all tokens, managers can update tokens for employees in their properties
CREATE POLICY "onboarding_tokens_update_policy" ON onboarding_tokens
  FOR UPDATE
  USING (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = onboarding_tokens.employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  )
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- Only HR can delete tokens
CREATE POLICY "onboarding_tokens_delete_policy" ON onboarding_tokens
  FOR DELETE
  USING (is_hr_user());

-- EMPLOYEE_FORMS TABLE POLICIES (if exists)
-- HR can see all forms, managers can only see forms for employees in their properties
CREATE POLICY "employee_forms_select_policy" ON employee_forms
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_forms.employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- HR can insert all forms, managers can insert forms for employees in their properties
CREATE POLICY "employee_forms_insert_policy" ON employee_forms
  FOR INSERT
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- HR can update all forms, managers can update forms for employees in their properties
CREATE POLICY "employee_forms_update_policy" ON employee_forms
  FOR UPDATE
  USING (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_forms.employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  )
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- Only HR can delete forms
CREATE POLICY "employee_forms_delete_policy" ON employee_forms
  FOR DELETE
  USING (is_hr_user());

-- EMPLOYEE_DOCUMENTS TABLE POLICIES (if exists)
-- HR can see all documents, managers can only see documents for employees in their properties
CREATE POLICY "employee_documents_select_policy" ON employee_documents
  FOR SELECT
  USING (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_documents.employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- HR can insert all documents, managers can insert documents for employees in their properties
CREATE POLICY "employee_documents_insert_policy" ON employee_documents
  FOR INSERT
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- HR can update all documents, managers can update documents for employees in their properties
CREATE POLICY "employee_documents_update_policy" ON employee_documents
  FOR UPDATE
  USING (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_documents.employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  )
  WITH CHECK (
    is_hr_user() OR 
    (is_manager_user() AND EXISTS (
      SELECT 1 FROM employees e 
      WHERE e.id = employee_id 
      AND manager_has_property_access(e.property_id)
    ))
  );

-- Only HR can delete documents
CREATE POLICY "employee_documents_delete_policy" ON employee_documents
  FOR DELETE
  USING (is_hr_user());

-- ================================================================================
-- STEP 5: Create indexes for performance optimization
-- ================================================================================

-- Create indexes for commonly queried fields
CREATE INDEX IF NOT EXISTS idx_property_managers_manager_id ON property_managers(manager_id);
CREATE INDEX IF NOT EXISTS idx_property_managers_property_id ON property_managers(property_id);
CREATE INDEX IF NOT EXISTS idx_property_managers_active ON property_managers(is_active);
CREATE INDEX IF NOT EXISTS idx_property_managers_composite ON property_managers(manager_id, property_id, is_active);

CREATE INDEX IF NOT EXISTS idx_job_applications_property_id ON job_applications(property_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status);
CREATE INDEX IF NOT EXISTS idx_job_applications_property_status ON job_applications(property_id, status);

CREATE INDEX IF NOT EXISTS idx_employees_property_id ON employees(property_id);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);
CREATE INDEX IF NOT EXISTS idx_employees_property_status ON employees(property_id, status);

CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_property_id ON onboarding_sessions(property_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_employee_id ON onboarding_sessions(employee_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status ON onboarding_sessions(status);

CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_employee_id ON onboarding_tokens(employee_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_token ON onboarding_tokens(token);
CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_expires_at ON onboarding_tokens(expires_at);

-- ================================================================================
-- STEP 6: Grant necessary permissions
-- ================================================================================

-- Grant usage on the schema to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;

-- Grant necessary permissions on tables to authenticated users
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT INSERT, UPDATE ON properties, managers, property_managers, job_applications, employees, onboarding_sessions, onboarding_tokens, employee_forms, employee_documents TO authenticated;
GRANT DELETE ON properties, managers, property_managers, job_applications, employees, onboarding_sessions, onboarding_tokens, employee_forms, employee_documents TO authenticated;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION is_hr_user() TO authenticated;
GRANT EXECUTE ON FUNCTION is_manager_user() TO authenticated;
GRANT EXECUTE ON FUNCTION current_manager_id() TO authenticated;
GRANT EXECUTE ON FUNCTION manager_has_property_access(UUID) TO authenticated;

-- ================================================================================
-- STEP 7: Verification queries
-- ================================================================================

-- Verify RLS is enabled on all tables
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
  'properties', 'managers', 'property_managers', 
  'job_applications', 'employees', 'onboarding_sessions',
  'onboarding_tokens', 'employee_forms', 'employee_documents'
)
ORDER BY tablename;

-- List all policies for verification
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- ================================================================================
-- NOTES:
-- ================================================================================
-- 1. This script assumes that auth.jwt() returns a JWT with the following structure:
--    {
--      "user_type": "hr" | "manager",
--      "user_id": "uuid-of-the-user"
--    }
--
-- 2. The script creates separate policies for SELECT, INSERT, UPDATE, and DELETE
--    operations to provide fine-grained control
--
-- 3. HR users have full access to all data
--
-- 4. Managers can only access data related to properties they are assigned to
--
-- 5. The property_managers table is the key relationship table that determines
--    which properties a manager can access
--
-- 6. All policies check the is_active flag in property_managers to ensure
--    only active assignments grant access
--
-- 7. Indexes are created on frequently queried columns to improve performance
-- ================================================================================