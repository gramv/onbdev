-- Combined Migration Script for Task 2
-- Run this in Supabase SQL Editor
-- ==================================================

-- From: supabase/migrations/008_create_user_preferences_table.sql
-- --------------------------------------------------
-- Migration: Create user_preferences table for personalization settings
-- Date: 2025-08-07
-- Description: Stores user-specific preferences for dashboard customization and notifications

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Dashboard preferences
    dashboard_layout TEXT DEFAULT 'default', -- 'default', 'compact', 'expanded'
    theme TEXT DEFAULT 'light', -- 'light', 'dark', 'auto'
    language TEXT DEFAULT 'en', -- 'en', 'es'
    timezone TEXT DEFAULT 'America/New_York',
    date_format TEXT DEFAULT 'MM/DD/YYYY',
    items_per_page INTEGER DEFAULT 20,
    
    -- Notification preferences
    email_notifications BOOLEAN DEFAULT true,
    sms_notifications BOOLEAN DEFAULT false,
    push_notifications BOOLEAN DEFAULT false,
    in_app_notifications BOOLEAN DEFAULT true,
    
    -- Notification types to receive
    notification_types JSONB DEFAULT '{"application_submitted": true, "application_approved": true, "deadline_reminder": true, "system_updates": false}'::jsonb,
    
    -- Email frequency
    email_frequency TEXT DEFAULT 'immediate', -- 'immediate', 'daily', 'weekly', 'never'
    daily_digest_time TIME DEFAULT '09:00:00',
    
    -- Dashboard widgets configuration
    dashboard_widgets JSONB DEFAULT '{"stats": true, "recent_applications": true, "pending_tasks": true, "notifications": true, "analytics": true}'::jsonb,
    widget_order TEXT[] DEFAULT ARRAY['stats', 'pending_tasks', 'recent_applications', 'notifications', 'analytics'],
    
    -- Saved filters and searches
    saved_filters JSONB DEFAULT '[]'::jsonb,
    saved_searches JSONB DEFAULT '[]'::jsonb,
    recent_searches TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Quick actions
    quick_actions JSONB DEFAULT '[]'::jsonb,
    pinned_properties UUID[] DEFAULT ARRAY[]::UUID[],
    
    -- Accessibility settings
    high_contrast BOOLEAN DEFAULT false,
    font_size TEXT DEFAULT 'medium', -- 'small', 'medium', 'large', 'extra-large'
    reduce_motion BOOLEAN DEFAULT false,
    screen_reader_mode BOOLEAN DEFAULT false,
    
    -- Advanced preferences
    auto_refresh_interval INTEGER DEFAULT 30, -- seconds, 0 = disabled
    show_tooltips BOOLEAN DEFAULT true,
    enable_shortcuts BOOLEAN DEFAULT true,
    sound_notifications BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified_by UUID REFERENCES users(id),
    
    CONSTRAINT unique_user_preferences UNIQUE(user_id)
);

-- Create indexes for performance
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_theme ON user_preferences(theme);
CREATE INDEX idx_user_preferences_language ON user_preferences(language);

-- Create trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_user_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER user_preferences_updated_at_trigger
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_user_preferences_updated_at();

-- Row Level Security (RLS)
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view and update their own preferences
CREATE POLICY user_preferences_own_access ON user_preferences
    FOR ALL
    USING (auth.uid()::uuid = user_id)
    WITH CHECK (auth.uid()::uuid = user_id);

-- Policy: HR users can view all preferences (for support)
CREATE POLICY user_preferences_hr_read ON user_preferences
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()::uuid
            AND role = 'hr'
        )
    );

-- Insert default preferences for existing users
INSERT INTO user_preferences (user_id)
SELECT id FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM user_preferences WHERE user_preferences.user_id = users.id
)
ON CONFLICT (user_id) DO NOTHING;

-- Add comment for documentation
COMMENT ON TABLE user_preferences IS 'Stores user-specific preferences for dashboard customization, notifications, and accessibility settings';
COMMENT ON COLUMN user_preferences.dashboard_widgets IS 'JSON configuration for which dashboard widgets to display';
COMMENT ON COLUMN user_preferences.saved_filters IS 'Array of saved filter configurations for quick access';
COMMENT ON COLUMN user_preferences.notification_types IS 'JSON object defining which types of notifications the user wants to receive';

-- --------------------------------------------------

-- From: supabase/migrations/009_create_bulk_operations_table.sql
-- --------------------------------------------------
-- Migration: Create bulk_operations table for tracking batch processes
-- Date: 2025-08-07
-- Description: Tracks bulk operations like mass approvals, batch communications, and bulk data updates

-- Create enum for bulk operation types
CREATE TYPE bulk_operation_type AS ENUM (
    'application_approval',
    'application_rejection', 
    'employee_onboarding',
    'employee_termination',
    'document_request',
    'notification_broadcast',
    'data_export',
    'data_import',
    'property_assignment',
    'role_change',
    'password_reset',
    'email_campaign',
    'compliance_check',
    'form_distribution'
);

-- Create enum for bulk operation status
CREATE TYPE bulk_operation_status AS ENUM (
    'pending',
    'queued',
    'processing',
    'completed',
    'failed',
    'cancelled',
    'partial_success'
);

-- Create bulk_operations table
CREATE TABLE IF NOT EXISTS bulk_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Operation details
    operation_type bulk_operation_type NOT NULL,
    operation_name TEXT NOT NULL,
    description TEXT,
    
    -- User and scope
    initiated_by UUID NOT NULL REFERENCES users(id),
    property_id UUID REFERENCES properties(id), -- NULL for global operations
    
    -- Target entities
    target_entity_type TEXT NOT NULL, -- 'applications', 'employees', 'users', etc.
    target_count INTEGER NOT NULL DEFAULT 0,
    target_ids UUID[] DEFAULT ARRAY[]::UUID[], -- IDs of entities being processed
    
    -- Filters and criteria used
    filter_criteria JSONB DEFAULT '{}'::jsonb, -- Store the filters used to select targets
    
    -- Processing details
    status bulk_operation_status NOT NULL DEFAULT 'pending',
    total_items INTEGER NOT NULL DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    successful_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    skipped_items INTEGER DEFAULT 0,
    
    -- Progress tracking
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    estimated_completion_time TIMESTAMP WITH TIME ZONE,
    actual_completion_time TIMESTAMP WITH TIME ZONE,
    
    -- Processing results
    results JSONB DEFAULT '{}'::jsonb, -- Detailed results for each item
    error_log JSONB DEFAULT '[]'::jsonb, -- Array of errors encountered
    warning_log JSONB DEFAULT '[]'::jsonb, -- Array of warnings
    
    -- Operation configuration
    configuration JSONB DEFAULT '{}'::jsonb, -- Operation-specific settings
    retry_failed BOOLEAN DEFAULT false,
    max_retries INTEGER DEFAULT 3,
    retry_count INTEGER DEFAULT 0,
    
    -- Scheduling
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    
    -- Performance metrics
    processing_time_ms INTEGER, -- Total processing time in milliseconds
    avg_item_time_ms INTEGER, -- Average time per item in milliseconds
    
    -- Cancellation
    cancelled_by UUID REFERENCES users(id),
    cancellation_reason TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Audit trail
    approval_required BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Rollback capability
    is_reversible BOOLEAN DEFAULT false,
    rollback_operation_id UUID REFERENCES bulk_operations(id),
    rolled_back BOOLEAN DEFAULT false,
    rolled_back_at TIMESTAMP WITH TIME ZONE,
    rolled_back_by UUID REFERENCES users(id)
);

-- Create indexes for performance
CREATE INDEX idx_bulk_operations_initiated_by ON bulk_operations(initiated_by);
CREATE INDEX idx_bulk_operations_property_id ON bulk_operations(property_id);
CREATE INDEX idx_bulk_operations_status ON bulk_operations(status);
CREATE INDEX idx_bulk_operations_operation_type ON bulk_operations(operation_type);
CREATE INDEX idx_bulk_operations_created_at ON bulk_operations(created_at DESC);
CREATE INDEX idx_bulk_operations_scheduled_at ON bulk_operations(scheduled_at) WHERE scheduled_at IS NOT NULL;
CREATE INDEX idx_bulk_operations_status_processing ON bulk_operations(status) WHERE status IN ('pending', 'queued', 'processing');

-- Create trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_bulk_operations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    
    -- Update progress percentage
    IF NEW.total_items > 0 THEN
        NEW.progress_percentage = (NEW.processed_items::DECIMAL / NEW.total_items::DECIMAL) * 100;
    END IF;
    
    -- Set completion time when status changes to completed/failed/cancelled
    IF NEW.status IN ('completed', 'failed', 'cancelled') AND OLD.status NOT IN ('completed', 'failed', 'cancelled') THEN
        NEW.actual_completion_time = CURRENT_TIMESTAMP;
        
        -- Calculate processing time if started_at is set
        IF NEW.started_at IS NOT NULL THEN
            NEW.processing_time_ms = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - NEW.started_at)) * 1000;
            
            -- Calculate average time per item
            IF NEW.processed_items > 0 THEN
                NEW.avg_item_time_ms = NEW.processing_time_ms / NEW.processed_items;
            END IF;
        END IF;
    END IF;
    
    -- Set started_at when status changes to processing
    IF NEW.status = 'processing' AND OLD.status != 'processing' THEN
        NEW.started_at = CURRENT_TIMESTAMP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER bulk_operations_updated_at_trigger
    BEFORE UPDATE ON bulk_operations
    FOR EACH ROW
    EXECUTE FUNCTION update_bulk_operations_updated_at();

-- Row Level Security (RLS)
ALTER TABLE bulk_operations ENABLE ROW LEVEL SECURITY;

-- Policy: HR users can view and create all bulk operations
CREATE POLICY bulk_operations_hr_full_access ON bulk_operations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()::uuid
            AND role = 'hr'
        )
    );

-- Policy: Managers can view and create bulk operations for their properties
CREATE POLICY bulk_operations_manager_property_access ON bulk_operations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON pm.manager_id = u.id
            WHERE u.id = auth.uid()::uuid
            AND u.role = 'manager'
            AND (pm.property_id = bulk_operations.property_id OR bulk_operations.property_id IS NULL)
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON pm.manager_id = u.id
            WHERE u.id = auth.uid()::uuid
            AND u.role = 'manager'
            AND pm.property_id = bulk_operations.property_id
        )
    );

-- Create a table for bulk operation items (individual records within a bulk operation)
CREATE TABLE IF NOT EXISTS bulk_operation_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bulk_operation_id UUID NOT NULL REFERENCES bulk_operations(id) ON DELETE CASCADE,
    
    -- Item details
    target_id UUID NOT NULL, -- ID of the entity being processed
    target_type TEXT NOT NULL, -- Type of entity
    
    -- Processing status
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'success', 'failed', 'skipped'
    
    -- Processing details
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_ms INTEGER,
    
    -- Results
    result JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for bulk operation items
CREATE INDEX idx_bulk_operation_items_bulk_operation_id ON bulk_operation_items(bulk_operation_id);
CREATE INDEX idx_bulk_operation_items_target_id ON bulk_operation_items(target_id);
CREATE INDEX idx_bulk_operation_items_status ON bulk_operation_items(status);

-- Add comments for documentation
COMMENT ON TABLE bulk_operations IS 'Tracks bulk operations like mass approvals, batch communications, and bulk data updates';
COMMENT ON COLUMN bulk_operations.filter_criteria IS 'JSON object containing the filters used to select target entities';
COMMENT ON COLUMN bulk_operations.results IS 'Detailed results for each processed item including success/failure details';
COMMENT ON COLUMN bulk_operations.configuration IS 'Operation-specific settings like email templates, approval criteria, etc.';
COMMENT ON TABLE bulk_operation_items IS 'Individual items processed within a bulk operation for detailed tracking';

-- --------------------------------------------------

-- From: supabase/migrations/010_add_performance_tracking_columns.sql
-- --------------------------------------------------
-- Migration: Add performance tracking columns to existing tables
-- Date: 2025-08-07
-- Description: Adds performance tracking and optimization columns to existing tables

-- ============================================
-- Add performance tracking to job_applications table
-- ============================================
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS time_to_hire_hours INTEGER;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS last_reviewed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS average_review_time_ms INTEGER;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS source_channel TEXT; -- 'website', 'mobile', 'kiosk', 'partner'
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS conversion_rate DECIMAL(5,2);
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS quality_score INTEGER; -- 0-100 score based on completeness

-- Calculate time_to_hire for existing records
UPDATE job_applications 
SET time_to_hire_hours = EXTRACT(EPOCH FROM (updated_at - created_at)) / 3600
WHERE status IN ('approved', 'rejected') AND time_to_hire_hours IS NULL;

-- ============================================
-- Add performance tracking to employees table
-- ============================================
ALTER TABLE employees ADD COLUMN IF NOT EXISTS onboarding_completion_time_hours INTEGER;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS forms_completion_percentage DECIMAL(5,2) DEFAULT 0.00;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS document_upload_count INTEGER DEFAULT 0;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS engagement_score INTEGER; -- 0-100 based on activity
ALTER TABLE employees ADD COLUMN IF NOT EXISTS compliance_score INTEGER; -- 0-100 based on deadline adherence
ALTER TABLE employees ADD COLUMN IF NOT EXISTS training_modules_completed INTEGER DEFAULT 0;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS average_form_completion_time_ms INTEGER;

-- ============================================
-- Add performance tracking to properties table
-- ============================================
ALTER TABLE properties ADD COLUMN IF NOT EXISTS total_employees_onboarded INTEGER DEFAULT 0;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS average_onboarding_time_hours DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS compliance_rate DECIMAL(5,2); -- Percentage of compliant onboardings
ALTER TABLE properties ADD COLUMN IF NOT EXISTS employee_retention_rate DECIMAL(5,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS last_onboarding_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS monthly_application_count INTEGER DEFAULT 0;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS conversion_rate DECIMAL(5,2); -- Applications to hires
ALTER TABLE properties ADD COLUMN IF NOT EXISTS performance_tier TEXT; -- 'platinum', 'gold', 'silver', 'bronze'

-- ============================================
-- Add performance tracking to users table (managers/HR)
-- ============================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS average_session_duration_seconds INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS tasks_completed INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS average_response_time_hours DECIMAL(10,2);
ALTER TABLE users ADD COLUMN IF NOT EXISTS approval_rate DECIMAL(5,2); -- For managers
ALTER TABLE users ADD COLUMN IF NOT EXISTS actions_per_session DECIMAL(10,2);
ALTER TABLE users ADD COLUMN IF NOT EXISTS performance_rating DECIMAL(3,2); -- 0.00 to 5.00

-- ============================================
-- Add performance tracking to notifications table
-- ============================================
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS delivery_time_ms INTEGER;
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS read_time_ms INTEGER;
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS click_through BOOLEAN DEFAULT false;
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS engagement_action TEXT; -- Action taken after reading

-- ============================================
-- Add performance tracking to audit_logs table
-- ============================================
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS execution_time_ms INTEGER;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS affected_rows INTEGER;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS query_complexity TEXT; -- 'simple', 'moderate', 'complex'

-- ============================================
-- Create indexes for performance queries
-- ============================================

-- Job applications performance indexes
CREATE INDEX IF NOT EXISTS idx_job_applications_processing_time ON job_applications(processing_time_ms) WHERE processing_time_ms IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_job_applications_time_to_hire ON job_applications(time_to_hire_hours) WHERE time_to_hire_hours IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_job_applications_source_channel ON job_applications(source_channel) WHERE source_channel IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_job_applications_quality_score ON job_applications(quality_score) WHERE quality_score IS NOT NULL;

-- Employees performance indexes
CREATE INDEX IF NOT EXISTS idx_employees_last_activity ON employees(last_activity_at DESC) WHERE last_activity_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_compliance_score ON employees(compliance_score) WHERE compliance_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_onboarding_time ON employees(onboarding_completion_time_hours) WHERE onboarding_completion_time_hours IS NOT NULL;

-- Properties performance indexes
CREATE INDEX IF NOT EXISTS idx_properties_performance_tier ON properties(performance_tier) WHERE performance_tier IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_compliance_rate ON properties(compliance_rate) WHERE compliance_rate IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_last_onboarding ON properties(last_onboarding_at DESC) WHERE last_onboarding_at IS NOT NULL;

-- Users performance indexes
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login_at DESC) WHERE last_login_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_login_count ON users(login_count) WHERE login_count > 0;
CREATE INDEX IF NOT EXISTS idx_users_performance_rating ON users(performance_rating) WHERE performance_rating IS NOT NULL;

-- ============================================
-- Create functions for automatic performance calculations
-- ============================================

-- Function to update employee onboarding completion time
CREATE OR REPLACE FUNCTION calculate_onboarding_completion_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.onboarding_status = 'completed' AND OLD.onboarding_status != 'completed' THEN
        NEW.onboarding_completion_time_hours := EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - NEW.created_at)) / 3600;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for employee onboarding completion
CREATE TRIGGER calculate_onboarding_time_trigger
    BEFORE UPDATE ON employees
    FOR EACH ROW
    WHEN (NEW.onboarding_status IS DISTINCT FROM OLD.onboarding_status)
    EXECUTE FUNCTION calculate_onboarding_completion_time();

-- Function to update user login statistics
CREATE OR REPLACE FUNCTION update_user_login_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- This would be called from the application layer when user logs in
    -- Placeholder for login tracking logic
    NEW.login_count := COALESCE(OLD.login_count, 0) + 1;
    NEW.last_login_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate property performance metrics
CREATE OR REPLACE FUNCTION update_property_performance_metrics()
RETURNS TRIGGER AS $$
DECLARE
    v_total_applications INTEGER;
    v_total_hires INTEGER;
BEGIN
    -- Calculate total employees onboarded
    SELECT COUNT(*) INTO NEW.total_employees_onboarded
    FROM employees
    WHERE property_id = NEW.id AND onboarding_status = 'completed';
    
    -- Calculate average onboarding time
    SELECT AVG(onboarding_completion_time_hours) INTO NEW.average_onboarding_time_hours
    FROM employees
    WHERE property_id = NEW.id AND onboarding_completion_time_hours IS NOT NULL;
    
    -- Calculate conversion rate
    SELECT COUNT(*) INTO v_total_applications
    FROM job_applications
    WHERE property_id = NEW.id;
    
    SELECT COUNT(*) INTO v_total_hires
    FROM job_applications
    WHERE property_id = NEW.id AND status = 'approved';
    
    IF v_total_applications > 0 THEN
        NEW.conversion_rate := (v_total_hires::DECIMAL / v_total_applications::DECIMAL) * 100;
    END IF;
    
    -- Determine performance tier based on metrics
    IF NEW.compliance_rate >= 95 AND NEW.conversion_rate >= 30 THEN
        NEW.performance_tier := 'platinum';
    ELSIF NEW.compliance_rate >= 85 AND NEW.conversion_rate >= 20 THEN
        NEW.performance_tier := 'gold';
    ELSIF NEW.compliance_rate >= 75 AND NEW.conversion_rate >= 10 THEN
        NEW.performance_tier := 'silver';
    ELSE
        NEW.performance_tier := 'bronze';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Add comments for documentation
-- ============================================
COMMENT ON COLUMN job_applications.processing_time_ms IS 'Time taken to process the application in milliseconds';
COMMENT ON COLUMN job_applications.time_to_hire_hours IS 'Total time from application to hire decision in hours';
COMMENT ON COLUMN job_applications.quality_score IS 'Application quality score (0-100) based on completeness and accuracy';

COMMENT ON COLUMN employees.onboarding_completion_time_hours IS 'Time taken to complete onboarding in hours';
COMMENT ON COLUMN employees.compliance_score IS 'Compliance score (0-100) based on deadline adherence and form completion';
COMMENT ON COLUMN employees.engagement_score IS 'Engagement score (0-100) based on activity and interaction';

COMMENT ON COLUMN properties.performance_tier IS 'Performance tier classification: platinum, gold, silver, or bronze';
COMMENT ON COLUMN properties.compliance_rate IS 'Percentage of compliant onboardings at this property';

COMMENT ON COLUMN users.performance_rating IS 'User performance rating from 0.00 to 5.00';
COMMENT ON COLUMN users.average_response_time_hours IS 'Average time to respond to assigned tasks in hours';

-- --------------------------------------------------
