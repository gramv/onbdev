-- Secure RLS Setup for Hotel Onboarding System
-- Run this in your Supabase SQL Editor

-- Step 1: Create a function to check if user is HR
CREATE OR REPLACE FUNCTION is_hr_user()
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER -- This is safe because it only checks role, doesn't bypass all security
AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 
    FROM users 
    WHERE id = auth.uid() 
    AND role = 'hr'
  );
END;
$$;

-- Step 2: Create RLS policies for properties table
-- Enable RLS if not already enabled
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;

-- Policy 1: HR users can INSERT properties
CREATE POLICY "HR can create properties"
ON properties
FOR INSERT
TO authenticated
WITH CHECK (is_hr_user());

-- Policy 2: HR users can UPDATE properties
CREATE POLICY "HR can update properties"
ON properties
FOR UPDATE
TO authenticated
USING (is_hr_user())
WITH CHECK (is_hr_user());

-- Policy 3: HR users can DELETE properties
CREATE POLICY "HR can delete properties"
ON properties
FOR DELETE
TO authenticated
USING (is_hr_user());

-- Policy 4: HR users can SELECT all properties
CREATE POLICY "HR can view all properties"
ON properties
FOR SELECT
TO authenticated
USING (is_hr_user());

-- Policy 5: Managers can SELECT their assigned properties
CREATE POLICY "Managers can view assigned properties"
ON properties
FOR SELECT
TO authenticated
USING (
  EXISTS (
    SELECT 1 
    FROM property_managers pm
    JOIN users u ON u.id = pm.manager_id
    WHERE pm.property_id = properties.id
    AND u.id = auth.uid()
    AND u.role = 'manager'
  )
);

-- Policy 6: Allow anonymous users to view properties for job applications
-- (Only basic info needed for application process)
CREATE POLICY "Public can view active properties for applications"
ON properties
FOR SELECT
TO anon
USING (is_active = true);

-- Step 3: Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON properties TO authenticated;
GRANT SELECT ON properties TO anon;

-- Step 4: Create similar policies for property_managers table
ALTER TABLE property_managers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "HR can manage property assignments"
ON property_managers
FOR ALL
TO authenticated
USING (is_hr_user())
WITH CHECK (is_hr_user());

CREATE POLICY "Managers can view their own assignments"
ON property_managers
FOR SELECT
TO authenticated
USING (manager_id = auth.uid());

-- Step 5: Verify the setup
-- Test query to check if policies are active
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
WHERE tablename IN ('properties', 'property_managers')
ORDER BY tablename, policyname;