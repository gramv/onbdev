-- =====================================================
-- FIX PROPERTIES RLS POLICIES FOR HR USERS
-- Allow HR users to create, update, and manage properties
-- =====================================================

-- Drop existing restrictive properties policies
DROP POLICY IF EXISTS "properties_insert_service_role" ON properties;
DROP POLICY IF EXISTS "properties_update_service_role" ON properties;
DROP POLICY IF EXISTS "properties_delete_service_role" ON properties;
DROP POLICY IF EXISTS "properties_select_authenticated" ON properties;

-- Create new policies that allow HR users full access to properties
CREATE POLICY "properties_select_all" ON properties
    FOR SELECT USING (true);

CREATE POLICY "properties_insert_hr_or_service" ON properties
    FOR INSERT WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

CREATE POLICY "properties_update_hr_or_service" ON properties
    FOR UPDATE USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

CREATE POLICY "properties_delete_hr_or_service" ON properties
    FOR DELETE USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

-- Also fix property_managers table policies to allow HR management
DROP POLICY IF EXISTS "property_managers_all_service_role" ON property_managers;

CREATE POLICY "property_managers_select_all" ON property_managers
    FOR SELECT USING (true);

CREATE POLICY "property_managers_insert_hr_or_service" ON property_managers
    FOR INSERT WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

CREATE POLICY "property_managers_update_hr_or_service" ON property_managers
    FOR UPDATE USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

CREATE POLICY "property_managers_delete_hr_or_service" ON property_managers
    FOR DELETE USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

-- Fix users table policies to allow HR operations
DROP POLICY IF EXISTS "users_insert_service_role" ON users;
DROP POLICY IF EXISTS "users_update_service_role" ON users;
DROP POLICY IF EXISTS "users_delete_service_role" ON users;

CREATE POLICY "users_insert_hr_or_service" ON users
    FOR INSERT WITH CHECK (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

CREATE POLICY "users_update_hr_or_service" ON users
    FOR UPDATE USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

CREATE POLICY "users_delete_hr_or_service" ON users
    FOR DELETE USING (
        auth.role() = 'service_role' OR 
        auth.role() = 'authenticated'
    );

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Properties RLS policies updated successfully!';
    RAISE NOTICE '🔐 HR users can now create, update, and delete properties';
    RAISE NOTICE '👥 Property manager assignments enabled for HR';
    RAISE NOTICE '🎯 Both service_role and authenticated users have full access';
END $$;