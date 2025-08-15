-- Ensure property_managers table exists
-- Run this in Supabase SQL Editor if needed

CREATE TABLE IF NOT EXISTS property_managers (
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    manager_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permissions JSONB DEFAULT '{"can_approve": true, "can_reject": true, "can_hire": true}'::jsonb,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    is_primary BOOLEAN DEFAULT false,
    PRIMARY KEY (property_id, manager_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_property_managers_property ON property_managers(property_id);
CREATE INDEX IF NOT EXISTS idx_property_managers_manager ON property_managers(manager_id);

-- Grant appropriate permissions
GRANT ALL ON property_managers TO authenticated;
GRANT SELECT ON property_managers TO anon;

-- Add RLS policies if not exists
ALTER TABLE property_managers ENABLE ROW LEVEL SECURITY;

-- Policy for HR users (can see all)
CREATE POLICY IF NOT EXISTS "HR can manage all property managers" 
ON property_managers 
FOR ALL 
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM users 
        WHERE users.id = auth.uid() 
        AND users.role = 'hr'
    )
);

-- Policy for managers (can see their own assignments)
CREATE POLICY IF NOT EXISTS "Managers can view their assignments" 
ON property_managers 
FOR SELECT
TO authenticated
USING (
    manager_id = auth.uid()
);

-- Policy for managers to see other managers in same property
CREATE POLICY IF NOT EXISTS "Managers can see co-managers" 
ON property_managers 
FOR SELECT
TO authenticated
USING (
    property_id IN (
        SELECT property_id 
        FROM property_managers pm2 
        WHERE pm2.manager_id = auth.uid()
    )
);