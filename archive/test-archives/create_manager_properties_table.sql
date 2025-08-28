-- Create manager_properties table for property assignments
CREATE TABLE IF NOT EXISTS public.manager_properties (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    manager_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    property_id UUID NOT NULL REFERENCES public.properties(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES public.users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique manager-property assignments
    UNIQUE(manager_id, property_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_manager_properties_manager_id ON public.manager_properties(manager_id);
CREATE INDEX IF NOT EXISTS idx_manager_properties_property_id ON public.manager_properties(property_id);
CREATE INDEX IF NOT EXISTS idx_manager_properties_active ON public.manager_properties(is_active);

-- Enable RLS
ALTER TABLE public.manager_properties ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "HR can manage all manager property assignments" ON public.manager_properties
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'hr'
        )
    );

CREATE POLICY "Managers can view their own property assignments" ON public.manager_properties
    FOR SELECT USING (
        manager_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'hr'
        )
    );

-- Grant permissions
GRANT ALL ON public.manager_properties TO authenticated;
GRANT ALL ON public.manager_properties TO service_role;

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_manager_properties_updated_at 
    BEFORE UPDATE ON public.manager_properties 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();