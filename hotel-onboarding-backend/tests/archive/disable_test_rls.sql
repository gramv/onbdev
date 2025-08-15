-- Disable RLS for Test Database Tables
-- WARNING: Only run this on TEST database, never on production!
-- Test DB: kzommszdhapvqpekpvnt.supabase.co

-- Disable RLS on all main tables
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE properties DISABLE ROW LEVEL SECURITY;
ALTER TABLE property_managers DISABLE ROW LEVEL SECURITY;
ALTER TABLE employees DISABLE ROW LEVEL SECURITY;
ALTER TABLE job_applications DISABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_progress DISABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_tasks DISABLE ROW LEVEL SECURITY;
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;
ALTER TABLE i9_forms DISABLE ROW LEVEL SECURITY;
ALTER TABLE w4_forms DISABLE ROW LEVEL SECURITY;

-- Drop problematic policies if they exist
DROP POLICY IF EXISTS "Users can view their own profile" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Enable read access for all users" ON users;
DROP POLICY IF EXISTS "Enable insert for all users" ON users;
DROP POLICY IF EXISTS "Enable update for all users" ON users;

-- Grant necessary permissions
GRANT ALL ON users TO anon;
GRANT ALL ON properties TO anon;
GRANT ALL ON property_managers TO anon;
GRANT ALL ON employees TO anon;
GRANT ALL ON job_applications TO anon;
GRANT ALL ON onboarding_progress TO anon;
GRANT ALL ON onboarding_tasks TO anon;
GRANT ALL ON documents TO anon;
GRANT ALL ON i9_forms TO anon;
GRANT ALL ON w4_forms TO anon;

-- Verify RLS is disabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('users', 'properties', 'property_managers', 'employees', 
                    'job_applications', 'onboarding_progress', 'onboarding_tasks',
                    'documents', 'i9_forms', 'w4_forms')
ORDER BY tablename;