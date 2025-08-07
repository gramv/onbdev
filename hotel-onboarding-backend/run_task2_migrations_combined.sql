-- Combined Task 2 Remaining Migrations Script
-- Run this directly in Supabase SQL Editor
-- Date: 2025-08-07

-- ============================================
-- MIGRATION 1: Create user_preferences table
-- ============================================

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Dashboard preferences
    dashboard_layout TEXT DEFAULT 'default',
    theme TEXT DEFAULT 'light',
    language TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'America/New_York',
    date_format TEXT DEFAULT 'MM/DD/YYYY',
    items_per_page INTEGER DEFAULT 20,
    
    -- Notification preferences
    email_notifications BOOLEAN DEFAULT true,
    sms_notifications BOOLEAN DEFAULT false,
    push_notifications BOOLEAN DEFAULT false,
    in_app_notifications BOOLEAN DEFAULT true,
    
    notification_types JSONB DEFAULT '{"application_submitted": true, "application_approved": true, "deadline_reminder": true, "system_updates": false}'::jsonb,
    email_frequency TEXT DEFAULT 'immediate',
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
    font_size TEXT DEFAULT 'medium',
    reduce_motion BOOLEAN DEFAULT false,
    screen_reader_mode BOOLEAN DEFAULT false,
    
    -- Advanced preferences
    auto_refresh_interval INTEGER DEFAULT 30,
    show_tooltips BOOLEAN DEFAULT true,
    enable_shortcuts BOOLEAN DEFAULT true,
    sound_notifications BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_modified_by UUID REFERENCES users(id),
    
    CONSTRAINT unique_user_preferences UNIQUE(user_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Enable RLS
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- ============================================
-- MIGRATION 2: Create bulk_operations tables
-- ============================================

-- Create enum types (only if they don't exist)
DO $$ BEGIN
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
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE bulk_operation_status AS ENUM (
        'pending',
        'queued',
        'processing',
        'completed',
        'failed',
        'cancelled',
        'partial_success'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create bulk_operations table
CREATE TABLE IF NOT EXISTS bulk_operations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operation_type bulk_operation_type NOT NULL,
    operation_name TEXT NOT NULL,
    description TEXT,
    initiated_by UUID NOT NULL REFERENCES users(id),
    property_id UUID REFERENCES properties(id),
    target_entity_type TEXT NOT NULL,
    target_count INTEGER NOT NULL DEFAULT 0,
    target_ids UUID[] DEFAULT ARRAY[]::UUID[],
    filter_criteria JSONB DEFAULT '{}'::jsonb,
    status bulk_operation_status NOT NULL DEFAULT 'pending',
    total_items INTEGER NOT NULL DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    successful_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    skipped_items INTEGER DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    estimated_completion_time TIMESTAMP WITH TIME ZONE,
    actual_completion_time TIMESTAMP WITH TIME ZONE,
    results JSONB DEFAULT '{}'::jsonb,
    error_log JSONB DEFAULT '[]'::jsonb,
    warning_log JSONB DEFAULT '[]'::jsonb,
    configuration JSONB DEFAULT '{}'::jsonb,
    retry_failed BOOLEAN DEFAULT false,
    max_retries INTEGER DEFAULT 3,
    retry_count INTEGER DEFAULT 0,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    processing_time_ms INTEGER,
    avg_item_time_ms INTEGER,
    cancelled_by UUID REFERENCES users(id),
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approval_required BOOLEAN DEFAULT false,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    is_reversible BOOLEAN DEFAULT false,
    rollback_operation_id UUID REFERENCES bulk_operations(id),
    rolled_back BOOLEAN DEFAULT false,
    rolled_back_at TIMESTAMP WITH TIME ZONE,
    rolled_back_by UUID REFERENCES users(id)
);

-- Create bulk_operation_items table
CREATE TABLE IF NOT EXISTS bulk_operation_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bulk_operation_id UUID NOT NULL REFERENCES bulk_operations(id) ON DELETE CASCADE,
    target_id UUID NOT NULL,
    target_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_ms INTEGER,
    result JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_bulk_operations_initiated_by ON bulk_operations(initiated_by);
CREATE INDEX IF NOT EXISTS idx_bulk_operations_status ON bulk_operations(status);
CREATE INDEX IF NOT EXISTS idx_bulk_operation_items_bulk_operation_id ON bulk_operation_items(bulk_operation_id);

-- Enable RLS
ALTER TABLE bulk_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE bulk_operation_items ENABLE ROW LEVEL SECURITY;

-- ============================================
-- MIGRATION 3: Add performance tracking columns
-- ============================================

-- Add columns to job_applications
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS time_to_hire_hours INTEGER;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS last_reviewed_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS source_channel TEXT;
ALTER TABLE job_applications ADD COLUMN IF NOT EXISTS quality_score INTEGER;

-- Add columns to employees
ALTER TABLE employees ADD COLUMN IF NOT EXISTS onboarding_completion_time_hours INTEGER;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS forms_completion_percentage DECIMAL(5,2) DEFAULT 0.00;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS compliance_score INTEGER;

-- Add columns to properties
ALTER TABLE properties ADD COLUMN IF NOT EXISTS total_employees_onboarded INTEGER DEFAULT 0;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS average_onboarding_time_hours DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS compliance_rate DECIMAL(5,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS performance_tier TEXT;

-- Add columns to users
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS performance_rating DECIMAL(3,2);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS idx_job_applications_processing_time ON job_applications(processing_time_ms) WHERE processing_time_ms IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_last_activity ON employees(last_activity_at DESC) WHERE last_activity_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_properties_performance_tier ON properties(performance_tier) WHERE performance_tier IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login_at DESC) WHERE last_login_at IS NOT NULL;

-- ============================================
-- Verification Query - Run this to check
-- ============================================
-- SELECT 'user_preferences' as table_name, EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_preferences') as exists
-- UNION ALL
-- SELECT 'bulk_operations', EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'bulk_operations')
-- UNION ALL
-- SELECT 'bulk_operation_items', EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'bulk_operation_items');