-- Create an RPC function to bypass RLS for property creation
-- This function should be created in your Supabase SQL editor

CREATE OR REPLACE FUNCTION create_property_bypass_rls(property_data jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER -- This allows the function to bypass RLS
AS $$
DECLARE
    new_property jsonb;
BEGIN
    -- Insert the property
    INSERT INTO properties (
        id,
        name,
        address,
        city,
        state,
        zip_code,
        phone,
        is_active,
        created_at
    )
    VALUES (
        (property_data->>'id')::uuid,
        property_data->>'name',
        property_data->>'address',
        property_data->>'city',
        property_data->>'state',
        property_data->>'zip_code',
        property_data->>'phone',
        COALESCE((property_data->>'is_active')::boolean, true),
        COALESCE((property_data->>'created_at')::timestamptz, NOW())
    )
    RETURNING to_jsonb(properties.*) INTO new_property;
    
    RETURN new_property;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION create_property_bypass_rls(jsonb) TO authenticated;

-- Alternative: Temporarily disable RLS for properties table (NOT RECOMMENDED for production)
-- ALTER TABLE properties DISABLE ROW LEVEL SECURITY;

-- Or create a more permissive RLS policy for HR users
-- CREATE POLICY "HR can create properties" ON properties
-- FOR INSERT TO authenticated
-- WITH CHECK (
--     EXISTS (
--         SELECT 1 FROM users
--         WHERE users.id = auth.uid()
--         AND users.role = 'hr'
--     )
-- );