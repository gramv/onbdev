-- Check if properties were actually created
SELECT id, name, city, state, created_at 
FROM properties
ORDER BY created_at DESC
LIMIT 10;

-- Check if there's any RLS on SELECT
SELECT 
    schemaname,
    tablename,
    policyname,
    cmd
FROM pg_policies 
WHERE tablename = 'properties' AND cmd = 'SELECT';

-- Direct count
SELECT COUNT(*) as total_properties FROM properties;