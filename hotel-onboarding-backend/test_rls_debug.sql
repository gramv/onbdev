-- Debug RLS Issues
-- Run these queries in Supabase SQL Editor to diagnose the problem

-- 1. Check if RLS is enabled on properties table
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename = 'properties';

-- 2. Check what policies exist on properties table
SELECT 
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'properties';

-- 3. Check if the is_hr_user function exists
SELECT 
    proname,
    prosecdef,
    provolatile
FROM pg_proc 
WHERE proname = 'is_hr_user';

-- 4. Test the is_hr_user function directly
-- (This will show NULL if not authenticated via Supabase)
SELECT is_hr_user();

-- 5. Check current user's auth.uid()
-- (This will show NULL if not authenticated via Supabase)
SELECT auth.uid();

-- 6. Check if users table has HR users
SELECT id, email, role 
FROM users 
WHERE role = 'hr'
LIMIT 5;

-- 7. TEMPORARY FIX - Disable RLS for testing
-- ONLY run this if you want to test without RLS temporarily
-- ALTER TABLE properties DISABLE ROW LEVEL SECURITY;

-- 8. Alternative: Create a simpler policy that allows all authenticated users
-- This is less secure but good for testing
-- DROP POLICY IF EXISTS "HR can create properties" ON properties;
-- CREATE POLICY "Allow authenticated insert" 
-- ON properties 
-- FOR INSERT 
-- TO authenticated 
-- WITH CHECK (true);