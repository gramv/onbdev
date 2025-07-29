
-- Create RPC function to bypass RLS for property creation
CREATE OR REPLACE FUNCTION create_property_bypass_rls(property_data jsonb)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER  -- This runs with creator's privileges, bypassing RLS
AS $$
DECLARE
    result json;
    new_property record;
BEGIN
    -- Insert the property data
    INSERT INTO properties (
        id, name, address, city, state, zip_code, phone, is_active, created_at
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
    RETURNING * INTO new_property;
    
    -- Return the created property as JSON
    SELECT row_to_json(new_property) INTO result;
    
    RETURN result;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION create_property_bypass_rls(jsonb) TO authenticated;
GRANT EXECUTE ON FUNCTION create_property_bypass_rls(jsonb) TO anon;
