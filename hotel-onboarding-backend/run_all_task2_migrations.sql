-- Combined Task 2 Migrations
-- Run this in Supabase SQL Editor

-- 003_create_audit_logs_table.sql
-- =====================================================
-- Migration 003: Create Audit Logs Table
-- HR Manager System Consolidation - Task 2.2
-- =====================================================

-- Description: Create comprehensive audit logging table for tracking all system actions
-- Created: 2025-08-06
-- Version: 1.0.0

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- CREATE AUDIT_LOGS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- User context - who performed the action
    user_id UUID,
    user_type VARCHAR(20) CHECK (user_type IN ('hr', 'manager', 'employee', 'system')),
    user_email VARCHAR(255), -- Store email for reference even if user is deleted
    
    -- Action details - what was done
    action VARCHAR(50) NOT NULL CHECK (action IN (
        'create', 'update', 'delete', 'view', 'approve', 'reject', 
        'login', 'logout', 'export', 'import', 'send_notification',
        'bulk_approve', 'bulk_reject', 'generate_report'
    )),
    
    -- Entity details - what was affected
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN (
        'application', 'employee', 'property', 'manager', 'user',
        'notification', 'report', 'onboarding_session', 'document'
    )),
    entity_id UUID,
    entity_name VARCHAR(255), -- Human readable identifier
    
    -- Property scope - for property-based access control
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    
    -- Detailed tracking
    details JSONB DEFAULT '{}'::jsonb,
    old_values JSONB, -- Before state for updates/deletes
    new_values JSONB, -- After state for creates/updates
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255), -- For tracing across services
    
    -- Compliance and retention
    compliance_event BOOLEAN DEFAULT false,
    retention_required_until DATE,
    risk_level VARCHAR(20) DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_entity_reference CHECK (
        (entity_type = 'application' AND entity_id IS NOT NULL) OR
        (entity_type = 'employee' AND entity_id IS NOT NULL) OR
        (entity_type = 'property' AND entity_id IS NOT NULL) OR
        entity_id IS NULL
    )
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_type ON audit_logs(user_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- Entity-based queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id) WHERE entity_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type);

-- Property-scoped queries (for managers)
CREATE INDEX IF NOT EXISTS idx_audit_logs_property_id ON audit_logs(property_id) WHERE property_id IS NOT NULL;

-- Time-based queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_date_range ON audit_logs(created_at, property_id);

-- Compliance and risk queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_compliance ON audit_logs(compliance_event, risk_level) WHERE compliance_event = true;
CREATE INDEX IF NOT EXISTS idx_audit_logs_retention ON audit_logs(retention_required_until) WHERE retention_required_until IS NOT NULL;

-- Full-text search on details (for advanced searching)
CREATE INDEX IF NOT EXISTS idx_audit_logs_details_gin ON audit_logs USING GIN(details);

-- Composite index for common dashboard queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_dashboard ON audit_logs(property_id, created_at, action) WHERE property_id IS NOT NULL;

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- HR can see all audit logs
CREATE POLICY "audit_logs_hr_full_access" ON audit_logs
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- Managers can see audit logs for their properties only
CREATE POLICY "audit_logs_manager_property_access" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = audit_logs.property_id
        )
    );

-- System can insert audit logs (for automated logging)
CREATE POLICY "audit_logs_system_insert" ON audit_logs
    FOR INSERT WITH CHECK (true);

-- Users can only see audit logs related to their own actions (limited scope)
CREATE POLICY "audit_logs_user_own_actions" ON audit_logs
    FOR SELECT USING (
        user_id::text = auth.uid()::text AND 
        entity_type IN ('onboarding_session', 'document') -- Only onboarding-related logs
    );

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to create audit log entries
CREATE OR REPLACE FUNCTION create_audit_log(
    p_user_id UUID,
    p_user_type VARCHAR,
    p_user_email VARCHAR,
    p_action VARCHAR,
    p_entity_type VARCHAR,
    p_entity_id UUID,
    p_entity_name VARCHAR DEFAULT NULL,
    p_property_id UUID DEFAULT NULL,
    p_details JSONB DEFAULT '{}'::jsonb,
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_session_id VARCHAR DEFAULT NULL,
    p_request_id VARCHAR DEFAULT NULL,
    p_compliance_event BOOLEAN DEFAULT false,
    p_risk_level VARCHAR DEFAULT 'low'
)
RETURNS UUID AS $$
DECLARE
    audit_id UUID;
BEGIN
    INSERT INTO audit_logs (
        user_id, user_type, user_email, action, entity_type, entity_id,
        entity_name, property_id, details, old_values, new_values,
        ip_address, user_agent, session_id, request_id,
        compliance_event, risk_level
    ) VALUES (
        p_user_id, p_user_type, p_user_email, p_action, p_entity_type, p_entity_id,
        p_entity_name, p_property_id, p_details, p_old_values, p_new_values,
        p_ip_address, p_user_agent, p_session_id, p_request_id,
        p_compliance_event, p_risk_level
    ) RETURNING id INTO audit_id;
    
    RETURN audit_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get audit trail for an entity
CREATE OR REPLACE FUNCTION get_audit_trail(
    p_entity_type VARCHAR,
    p_entity_id UUID,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    id UUID,
    action VARCHAR,
    user_email VARCHAR,
    user_type VARCHAR,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.id,
        al.action,
        al.user_email,
        al.user_type,
        al.details,
        al.created_at
    FROM audit_logs al
    WHERE al.entity_type = p_entity_type
    AND al.entity_id = p_entity_id
    ORDER BY al.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up old audit logs (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(
    p_retention_days INTEGER DEFAULT 2555 -- 7 years default
)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Only delete non-compliance logs past retention period
    DELETE FROM audit_logs 
    WHERE created_at < NOW() - (p_retention_days || ' days')::INTERVAL
    AND compliance_event = false
    AND (retention_required_until IS NULL OR retention_required_until < CURRENT_DATE);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup action
    INSERT INTO audit_logs (
        user_type, action, entity_type, entity_name,
        details, compliance_event, risk_level
    ) VALUES (
        'system', 'delete', 'audit_logs', 'cleanup_operation',
        jsonb_build_object('deleted_count', deleted_count, 'retention_days', p_retention_days),
        true, 'low'
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- TRIGGERS FOR AUTOMATIC AUDIT LOGGING
-- =====================================================

-- Enhanced trigger function for audit logging
CREATE OR REPLACE FUNCTION enhanced_audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    audit_user_id UUID;
    audit_user_type VARCHAR;
    audit_user_email VARCHAR;
    audit_property_id UUID;
BEGIN
    -- Get user context from auth or trigger context
    audit_user_id := COALESCE(
        (auth.jwt() ->> 'user_id')::UUID,
        auth.uid()::UUID,
        CASE 
            WHEN TG_OP = 'DELETE' THEN OLD.updated_by 
            ELSE NEW.updated_by 
        END
    );
    
    audit_user_type := COALESCE(
        auth.jwt() ->> 'user_type',
        'system'
    );
    
    audit_user_email := COALESCE(
        auth.jwt() ->> 'email',
        auth.email()
    );
    
    -- Get property context if available
    audit_property_id := CASE
        WHEN TG_TABLE_NAME = 'job_applications' THEN
            CASE WHEN TG_OP = 'DELETE' THEN OLD.property_id ELSE NEW.property_id END
        WHEN TG_TABLE_NAME = 'employees' THEN
            CASE WHEN TG_OP = 'DELETE' THEN OLD.property_id ELSE NEW.property_id END
        ELSE NULL
    END;
    
    -- Create audit log entry
    IF TG_OP = 'DELETE' THEN
        PERFORM create_audit_log(
            audit_user_id, audit_user_type, audit_user_email,
            'delete', TG_TABLE_NAME, OLD.id,
            COALESCE(OLD.name, OLD.first_name || ' ' || OLD.last_name, OLD.id::text),
            audit_property_id,
            jsonb_build_object('table', TG_TABLE_NAME),
            row_to_json(OLD)::jsonb,
            NULL,
            inet_client_addr(),
            current_setting('request.headers', true)::jsonb ->> 'user-agent',
            current_setting('request.jwt.claims', true)::jsonb ->> 'session_id'
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        PERFORM create_audit_log(
            audit_user_id, audit_user_type, audit_user_email,
            'update', TG_TABLE_NAME, NEW.id,
            COALESCE(NEW.name, NEW.first_name || ' ' || NEW.last_name, NEW.id::text),
            audit_property_id,
            jsonb_build_object('table', TG_TABLE_NAME),
            row_to_json(OLD)::jsonb,
            row_to_json(NEW)::jsonb,
            inet_client_addr(),
            current_setting('request.headers', true)::jsonb ->> 'user-agent',
            current_setting('request.jwt.claims', true)::jsonb ->> 'session_id'
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        PERFORM create_audit_log(
            audit_user_id, audit_user_type, audit_user_email,
            'create', TG_TABLE_NAME, NEW.id,
            COALESCE(NEW.name, NEW.first_name || ' ' || NEW.last_name, NEW.id::text),
            audit_property_id,
            jsonb_build_object('table', TG_TABLE_NAME),
            NULL,
            row_to_json(NEW)::jsonb,
            inet_client_addr(),
            current_setting('request.headers', true)::jsonb ->> 'user-agent',
            current_setting('request.jwt.claims', true)::jsonb ->> 'session_id'
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply audit triggers to key tables (if they exist)
DO $$ 
BEGIN
    -- Only create triggers if tables exist
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'job_applications') THEN
        DROP TRIGGER IF EXISTS audit_job_applications_trigger ON job_applications;
        CREATE TRIGGER audit_job_applications_trigger
            AFTER INSERT OR UPDATE OR DELETE ON job_applications
            FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger_function();
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employees') THEN
        DROP TRIGGER IF EXISTS audit_employees_trigger ON employees;
        CREATE TRIGGER audit_employees_trigger
            AFTER INSERT OR UPDATE OR DELETE ON employees
            FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger_function();
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'properties') THEN
        DROP TRIGGER IF EXISTS audit_properties_trigger ON properties;
        CREATE TRIGGER audit_properties_trigger
            AFTER INSERT OR UPDATE OR DELETE ON properties
            FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger_function();
    END IF;
    
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        DROP TRIGGER IF EXISTS audit_users_trigger ON users;
        CREATE TRIGGER audit_users_trigger
            AFTER INSERT OR UPDATE OR DELETE ON users
            FOR EACH ROW EXECUTE FUNCTION enhanced_audit_trigger_function();
    END IF;
END $$;

-- =====================================================
-- INITIAL DATA AND VERIFICATION
-- =====================================================

-- Insert initial audit log entry to mark migration completion
INSERT INTO audit_logs (
    user_type, action, entity_type, entity_name,
    details, compliance_event, risk_level
) VALUES (
    'system', 'create', 'audit_logs', 'table_migration',
    jsonb_build_object(
        'migration', '003_create_audit_logs_table',
        'version', '1.0.0',
        'tables_created', 1,
        'indexes_created', 9,
        'functions_created', 3,
        'triggers_created', 4
    ),
    true, 'low'
);

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 003 completed successfully!';
    RAISE NOTICE '📊 Audit logs table created with comprehensive tracking';
    RAISE NOTICE '🔐 Row Level Security policies applied';
    RAISE NOTICE '⚡ Performance indexes created';
    RAISE NOTICE '🔧 Helper functions and triggers installed';
    RAISE NOTICE '📝 Ready for audit logging across all system operations';
END $$;

-- 004_create_notifications_table.sql
-- =====================================================
-- Migration 004: Create Notifications Table
-- HR Manager System Consolidation - Task 2.3
-- =====================================================

-- Description: Create notifications table with multi-channel support
-- Created: 2025-08-06
-- Version: 1.0.0

-- =====================================================
-- CREATE NOTIFICATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS notifications (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Recipient details
    user_id UUID,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('hr', 'manager', 'employee')),
    user_email VARCHAR(255), -- Store email for delivery even if user is deleted
    
    -- Notification content
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'new_application', 'application_approved', 'application_rejected',
        'onboarding_reminder', 'deadline_reminder', 'document_uploaded',
        'system_alert', 'maintenance_notice', 'policy_update',
        'bulk_operation_complete', 'report_ready', 'compliance_alert'
    )),
    title VARCHAR(255) NOT NULL,
    message TEXT,
    
    -- Additional data and context
    data JSONB DEFAULT '{}'::jsonb,
    action_url TEXT, -- Deep link for notification actions
    
    -- Multi-channel delivery
    channels JSONB NOT NULL DEFAULT '["in_app"]'::jsonb CHECK (
        channels::jsonb ?| array['in_app', 'email', 'sms', 'webhook']
    ),
    delivery_status JSONB DEFAULT '{}'::jsonb,
    
    -- Scoping and filtering
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    entity_type VARCHAR(50), -- Related entity type for context
    entity_id UUID, -- Related entity ID
    
    -- Priority and urgency
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    urgency VARCHAR(20) DEFAULT 'normal' CHECK (urgency IN ('low', 'normal', 'high', 'critical')),
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN (
        'pending', 'sent', 'delivered', 'failed', 'cancelled'
    )),
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    
    -- Delivery tracking
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    
    -- Scheduling and expiration
    scheduled_for TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Batch and campaign tracking
    batch_id UUID, -- For grouping related notifications
    campaign_id VARCHAR(100), -- For marketing/announcement campaigns
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_scheduling CHECK (
        scheduled_for IS NULL OR scheduled_for >= created_at
    ),
    CONSTRAINT valid_expiration CHECK (
        expires_at IS NULL OR expires_at > created_at
    ),
    CONSTRAINT valid_read_timestamp CHECK (
        read_at IS NULL OR (is_read = true AND read_at >= created_at)
    )
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- User-focused queries (primary dashboard use case)
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, user_type, is_read, created_at) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, created_at) WHERE is_read = false AND user_id IS NOT NULL;

-- Property-scoped queries (for managers)
CREATE INDEX IF NOT EXISTS idx_notifications_property_id ON notifications(property_id, created_at) WHERE property_id IS NOT NULL;

-- Type-based filtering
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority, urgency, created_at);

-- Status and delivery tracking
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_delivery ON notifications(status, sent_at, retry_count) WHERE status IN ('pending', 'failed');

-- Scheduling queries
CREATE INDEX IF NOT EXISTS idx_notifications_scheduled ON notifications(scheduled_for) WHERE scheduled_for IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_expiring ON notifications(expires_at) WHERE expires_at IS NOT NULL;

-- Batch operations
CREATE INDEX IF NOT EXISTS idx_notifications_batch ON notifications(batch_id) WHERE batch_id IS NOT NULL;

-- Entity relationship queries
CREATE INDEX IF NOT EXISTS idx_notifications_entity ON notifications(entity_type, entity_id) WHERE entity_id IS NOT NULL;

-- Full-text search on content
CREATE INDEX IF NOT EXISTS idx_notifications_content_search ON notifications USING GIN(to_tsvector('english', title || ' ' || COALESCE(message, '')));

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_notifications_dashboard ON notifications(user_id, property_id, is_read, priority, created_at);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES  
-- =====================================================

-- Enable RLS
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Users can only see their own notifications
CREATE POLICY "notifications_user_own" ON notifications
    FOR SELECT USING (user_id::text = auth.uid()::text);

-- Users can mark their own notifications as read
CREATE POLICY "notifications_user_update_own" ON notifications
    FOR UPDATE USING (user_id::text = auth.uid()::text)
    WITH CHECK (user_id::text = auth.uid()::text);

-- HR can see all notifications
CREATE POLICY "notifications_hr_full_access" ON notifications
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- Managers can see notifications for their properties
CREATE POLICY "notifications_manager_property_access" ON notifications
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = notifications.property_id
        )
    );

-- System can create and manage all notifications
CREATE POLICY "notifications_system_manage" ON notifications
    FOR ALL USING (
        auth.jwt() ->> 'user_type' = 'system' OR
        auth.role() = 'service_role'
    );

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to create notification
CREATE OR REPLACE FUNCTION create_notification(
    p_user_id UUID,
    p_user_type VARCHAR,
    p_user_email VARCHAR,
    p_type VARCHAR,
    p_title VARCHAR,
    p_message TEXT DEFAULT NULL,
    p_data JSONB DEFAULT '{}'::jsonb,
    p_action_url TEXT DEFAULT NULL,
    p_channels JSONB DEFAULT '["in_app"]'::jsonb,
    p_property_id UUID DEFAULT NULL,
    p_entity_type VARCHAR DEFAULT NULL,
    p_entity_id UUID DEFAULT NULL,
    p_priority VARCHAR DEFAULT 'normal',
    p_urgency VARCHAR DEFAULT 'normal',
    p_scheduled_for TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_batch_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    notification_id UUID;
BEGIN
    INSERT INTO notifications (
        user_id, user_type, user_email, type, title, message,
        data, action_url, channels, property_id, entity_type, entity_id,
        priority, urgency, scheduled_for, expires_at, batch_id
    ) VALUES (
        p_user_id, p_user_type, p_user_email, p_type, p_title, p_message,
        p_data, p_action_url, p_channels, p_property_id, p_entity_type, p_entity_id,
        p_priority, p_urgency, p_scheduled_for, p_expires_at, p_batch_id
    ) RETURNING id INTO notification_id;
    
    RETURN notification_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to mark notification as read
CREATE OR REPLACE FUNCTION mark_notification_read(
    p_notification_id UUID,
    p_user_id UUID DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    success BOOLEAN := false;
BEGIN
    UPDATE notifications 
    SET is_read = true, 
        read_at = NOW(),
        updated_at = NOW()
    WHERE id = p_notification_id
    AND (p_user_id IS NULL OR user_id = p_user_id)
    AND is_read = false;
    
    GET DIAGNOSTICS success = FOUND;
    RETURN success;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to mark multiple notifications as read
CREATE OR REPLACE FUNCTION mark_notifications_read_batch(
    p_notification_ids UUID[],
    p_user_id UUID DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    affected_count INTEGER;
BEGIN
    UPDATE notifications 
    SET is_read = true, 
        read_at = NOW(),
        updated_at = NOW()
    WHERE id = ANY(p_notification_ids)
    AND (p_user_id IS NULL OR user_id = p_user_id)
    AND is_read = false;
    
    GET DIAGNOSTICS affected_count = ROW_COUNT;
    RETURN affected_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get unread notification count
CREATE OR REPLACE FUNCTION get_unread_notification_count(
    p_user_id UUID,
    p_property_id UUID DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    unread_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO unread_count
    FROM notifications
    WHERE user_id = p_user_id
    AND is_read = false
    AND (expires_at IS NULL OR expires_at > NOW())
    AND (p_property_id IS NULL OR property_id = p_property_id);
    
    RETURN COALESCE(unread_count, 0);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get pending notifications for delivery
CREATE OR REPLACE FUNCTION get_pending_notifications(
    p_channel VARCHAR DEFAULT NULL,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    id UUID,
    user_email VARCHAR,
    type VARCHAR,
    title VARCHAR,
    message TEXT,
    data JSONB,
    channels JSONB,
    priority VARCHAR,
    scheduled_for TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        n.id,
        n.user_email,
        n.type,
        n.title,
        n.message,
        n.data,
        n.channels,
        n.priority,
        n.scheduled_for
    FROM notifications n
    WHERE n.status = 'pending'
    AND (n.scheduled_for IS NULL OR n.scheduled_for <= NOW())
    AND (n.expires_at IS NULL OR n.expires_at > NOW())
    AND (p_channel IS NULL OR n.channels::jsonb ? p_channel)
    ORDER BY n.priority DESC, n.created_at ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update notification delivery status
CREATE OR REPLACE FUNCTION update_notification_delivery_status(
    p_notification_id UUID,
    p_channel VARCHAR,
    p_status VARCHAR,
    p_error_message TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    current_delivery_status JSONB;
    success BOOLEAN := false;
BEGIN
    -- Get current delivery status
    SELECT delivery_status INTO current_delivery_status
    FROM notifications
    WHERE id = p_notification_id;
    
    -- Update delivery status for the specific channel
    current_delivery_status := COALESCE(current_delivery_status, '{}'::jsonb);
    current_delivery_status := jsonb_set(
        current_delivery_status,
        ARRAY[p_channel],
        jsonb_build_object(
            'status', p_status,
            'timestamp', NOW(),
            'error', p_error_message
        )
    );
    
    -- Update the notification
    UPDATE notifications
    SET delivery_status = current_delivery_status,
        status = CASE 
            WHEN p_status = 'delivered' THEN 'delivered'
            WHEN p_status = 'failed' THEN 'failed'
            ELSE status
        END,
        sent_at = CASE WHEN p_status IN ('sent', 'delivered') THEN NOW() ELSE sent_at END,
        delivered_at = CASE WHEN p_status = 'delivered' THEN NOW() ELSE delivered_at END,
        failed_at = CASE WHEN p_status = 'failed' THEN NOW() ELSE failed_at END,
        retry_count = CASE WHEN p_status = 'failed' THEN retry_count + 1 ELSE retry_count END,
        updated_at = NOW()
    WHERE id = p_notification_id;
    
    GET DIAGNOSTICS success = FOUND;
    RETURN success;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup old notifications
CREATE OR REPLACE FUNCTION cleanup_old_notifications(
    p_retention_days INTEGER DEFAULT 90
)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete old read notifications
    DELETE FROM notifications 
    WHERE is_read = true
    AND read_at < NOW() - (p_retention_days || ' days')::INTERVAL;
    
    -- Delete expired notifications
    DELETE FROM notifications
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup action in audit logs
    PERFORM create_audit_log(
        NULL, 'system', NULL,
        'delete', 'notifications', NULL,
        'cleanup_operation', NULL,
        jsonb_build_object('deleted_count', deleted_count, 'retention_days', p_retention_days),
        NULL, NULL, NULL, NULL, NULL, NULL,
        true, 'low'
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger to automatically update updated_at
CREATE OR REPLACE FUNCTION update_notifications_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_notifications_updated_at_trigger
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_notifications_updated_at();

-- Trigger for audit logging on notifications
CREATE TRIGGER audit_notifications_trigger
    AFTER INSERT OR UPDATE OR DELETE ON notifications
    FOR EACH ROW 
    EXECUTE FUNCTION enhanced_audit_trigger_function();

-- =====================================================
-- INITIAL DATA AND VERIFICATION
-- =====================================================

-- Create initial system notification types as reference
INSERT INTO notifications (
    user_type, type, title, message,
    data, priority, expires_at
) VALUES (
    'system', 'system_alert', 'Notifications System Initialized',
    'The enhanced notifications system has been successfully deployed and is ready for use.',
    jsonb_build_object(
        'migration', '004_create_notifications_table',
        'version', '1.0.0',
        'features', jsonb_build_array('multi_channel', 'scheduling', 'batching', 'rls_security')
    ),
    'low',
    NOW() + INTERVAL '30 days'
) ON CONFLICT DO NOTHING;

-- Insert audit log entry
INSERT INTO audit_logs (
    user_type, action, entity_type, entity_name,
    details, compliance_event, risk_level
) VALUES (
    'system', 'create', 'notifications', 'table_migration',
    jsonb_build_object(
        'migration', '004_create_notifications_table',
        'version', '1.0.0',
        'tables_created', 1,
        'indexes_created', 12,
        'functions_created', 7,
        'triggers_created', 2,
        'rls_policies_created', 5
    ),
    true, 'low'
);

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 004 completed successfully!';
    RAISE NOTICE '📨 Notifications table created with multi-channel support';
    RAISE NOTICE '🔐 Row Level Security policies applied';
    RAISE NOTICE '⚡ Performance indexes created for dashboard queries';
    RAISE NOTICE '📬 Delivery status tracking and scheduling enabled';
    RAISE NOTICE '🔔 Ready for real-time notifications across all channels';
END $$;

-- 005_create_analytics_events_table.sql
-- =====================================================
-- Migration 005: Create Analytics Events Table
-- HR Manager System Consolidation - Task 2.4
-- =====================================================

-- Description: Create analytics_events table for tracking user interactions
-- Created: 2025-08-06
-- Version: 1.0.0

-- =====================================================
-- CREATE ANALYTICS_EVENTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS analytics_events (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- User context
    user_id UUID,
    user_type VARCHAR(20) CHECK (user_type IN ('hr', 'manager', 'employee', 'anonymous')),
    session_id VARCHAR(255),
    
    -- Event details
    event_type VARCHAR(100) NOT NULL CHECK (event_type IN (
        -- Navigation events
        'page_view', 'dashboard_view', 'tab_change', 'navigation_click',
        -- User actions
        'button_click', 'form_submit', 'search_query', 'filter_apply',
        'bulk_action', 'export_data', 'import_data',
        -- Application workflow
        'application_view', 'application_approve', 'application_reject',
        'application_create', 'application_update',
        -- Employee management
        'employee_view', 'employee_create', 'employee_update',
        'onboarding_start', 'onboarding_complete',
        -- Reporting and analytics
        'report_generate', 'report_view', 'chart_interaction',
        -- System events
        'login', 'logout', 'error_occurred', 'performance_metric'
    )),
    event_category VARCHAR(50) NOT NULL CHECK (event_category IN (
        'navigation', 'user_action', 'workflow', 'reporting', 
        'system', 'performance', 'error', 'security'
    )),
    event_label VARCHAR(255), -- Descriptive label for the event
    
    -- Event data and context
    event_data JSONB DEFAULT '{}'::jsonb,
    page_url TEXT,
    referrer_url TEXT,
    
    -- Property and entity scoping
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    entity_type VARCHAR(50), -- Related entity (application, employee, etc.)
    entity_id UUID, -- Related entity ID
    
    -- Performance and timing
    timing_value INTEGER, -- Milliseconds for performance events
    performance_metrics JSONB, -- Detailed performance data
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(20) DEFAULT 'unknown' CHECK (device_type IN (
        'desktop', 'tablet', 'mobile', 'unknown'
    )),
    browser_name VARCHAR(50),
    browser_version VARCHAR(20),
    os_name VARCHAR(50),
    
    -- Geographic data (if available)
    country_code VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    
    -- A/B testing and experiments
    experiment_id VARCHAR(100),
    experiment_variant VARCHAR(50),
    
    -- Custom dimensions (for extensibility)
    custom_dimension_1 VARCHAR(255),
    custom_dimension_2 VARCHAR(255),
    custom_dimension_3 VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Data quality and processing
    processed_at TIMESTAMP WITH TIME ZONE,
    is_valid BOOLEAN DEFAULT true,
    validation_errors JSONB,
    
    -- Constraints
    CONSTRAINT valid_timing CHECK (timing_value IS NULL OR timing_value >= 0),
    CONSTRAINT valid_event_timestamp CHECK (event_timestamp >= created_at - INTERVAL '1 hour')
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- Time-series queries (most common for analytics)
CREATE INDEX IF NOT EXISTS idx_analytics_events_time ON analytics_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_event_time ON analytics_events(event_timestamp DESC);

-- User-based analytics
CREATE INDEX IF NOT EXISTS idx_analytics_events_user ON analytics_events(user_id, created_at) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_type ON analytics_events(user_type, created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_events_session ON analytics_events(session_id, created_at) WHERE session_id IS NOT NULL;

-- Property-scoped analytics (for managers)
CREATE INDEX IF NOT EXISTS idx_analytics_events_property ON analytics_events(property_id, created_at) WHERE property_id IS NOT NULL;

-- Event classification
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type, created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_events_category ON analytics_events(event_category, created_at);

-- Entity tracking
CREATE INDEX IF NOT EXISTS idx_analytics_events_entity ON analytics_events(entity_type, entity_id) WHERE entity_id IS NOT NULL;

-- Performance analysis
CREATE INDEX IF NOT EXISTS idx_analytics_events_performance ON analytics_events(event_type, timing_value) WHERE timing_value IS NOT NULL;

-- Device and platform analytics
CREATE INDEX IF NOT EXISTS idx_analytics_events_device ON analytics_events(device_type, browser_name, created_at);

-- Geographic analytics
CREATE INDEX IF NOT EXISTS idx_analytics_events_geo ON analytics_events(country_code, region, created_at) WHERE country_code IS NOT NULL;

-- A/B testing queries
CREATE INDEX IF NOT EXISTS idx_analytics_events_experiments ON analytics_events(experiment_id, experiment_variant, created_at) WHERE experiment_id IS NOT NULL;

-- Composite indexes for common dashboard queries
CREATE INDEX IF NOT EXISTS idx_analytics_events_dashboard ON analytics_events(property_id, event_category, created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_events_funnel ON analytics_events(user_id, event_type, created_at) WHERE user_id IS NOT NULL;

-- Full-text search on event labels and URLs
CREATE INDEX IF NOT EXISTS idx_analytics_events_search ON analytics_events USING GIN(to_tsvector('english', 
    COALESCE(event_label, '') || ' ' || COALESCE(page_url, '')
));

-- Partial index for errors and performance issues
CREATE INDEX IF NOT EXISTS idx_analytics_events_errors ON analytics_events(event_category, event_type, created_at) 
    WHERE event_category IN ('error', 'performance') OR is_valid = false;

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- HR can see all analytics events
CREATE POLICY "analytics_events_hr_full_access" ON analytics_events
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- Managers can see analytics events for their properties
CREATE POLICY "analytics_events_manager_property_access" ON analytics_events
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = analytics_events.property_id
        )
    );

-- Users can see their own analytics events (limited scope)
CREATE POLICY "analytics_events_user_own" ON analytics_events
    FOR SELECT USING (user_id::text = auth.uid()::text);

-- System and services can insert analytics events
CREATE POLICY "analytics_events_system_insert" ON analytics_events
    FOR INSERT WITH CHECK (
        auth.jwt() ->> 'user_type' = 'system' OR
        auth.role() = 'service_role' OR
        auth.role() = 'anon' -- Allow anonymous events for tracking
    );

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to track analytics event
CREATE OR REPLACE FUNCTION track_analytics_event(
    p_user_id UUID DEFAULT NULL,
    p_user_type VARCHAR DEFAULT 'anonymous',
    p_session_id VARCHAR DEFAULT NULL,
    p_event_type VARCHAR,
    p_event_category VARCHAR,
    p_event_label VARCHAR DEFAULT NULL,
    p_event_data JSONB DEFAULT '{}'::jsonb,
    p_page_url TEXT DEFAULT NULL,
    p_referrer_url TEXT DEFAULT NULL,
    p_property_id UUID DEFAULT NULL,
    p_entity_type VARCHAR DEFAULT NULL,
    p_entity_id UUID DEFAULT NULL,
    p_timing_value INTEGER DEFAULT NULL,
    p_performance_metrics JSONB DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_experiment_id VARCHAR DEFAULT NULL,
    p_experiment_variant VARCHAR DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    event_id UUID;
    parsed_user_agent JSONB;
BEGIN
    -- Parse user agent if provided
    parsed_user_agent := CASE 
        WHEN p_user_agent IS NOT NULL THEN
            jsonb_build_object(
                'device_type', CASE 
                    WHEN p_user_agent ~* 'Mobile|Android|iPhone|iPad' THEN 'mobile'
                    WHEN p_user_agent ~* 'Tablet|iPad' THEN 'tablet'
                    ELSE 'desktop'
                END,
                'browser_name', CASE
                    WHEN p_user_agent ~* 'Chrome' THEN 'Chrome'
                    WHEN p_user_agent ~* 'Firefox' THEN 'Firefox'
                    WHEN p_user_agent ~* 'Safari' THEN 'Safari'
                    WHEN p_user_agent ~* 'Edge' THEN 'Edge'
                    ELSE 'Unknown'
                END
            )
        ELSE '{}'::jsonb
    END;
    
    INSERT INTO analytics_events (
        user_id, user_type, session_id, event_type, event_category,
        event_label, event_data, page_url, referrer_url, property_id,
        entity_type, entity_id, timing_value, performance_metrics,
        ip_address, user_agent, device_type, browser_name,
        experiment_id, experiment_variant
    ) VALUES (
        p_user_id, p_user_type, p_session_id, p_event_type, p_event_category,
        p_event_label, p_event_data, p_page_url, p_referrer_url, p_property_id,
        p_entity_type, p_entity_id, p_timing_value, p_performance_metrics,
        p_ip_address, p_user_agent, 
        (parsed_user_agent ->> 'device_type')::VARCHAR,
        (parsed_user_agent ->> 'browser_name')::VARCHAR,
        p_experiment_id, p_experiment_variant
    ) RETURNING id INTO event_id;
    
    RETURN event_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get analytics summary for a date range
CREATE OR REPLACE FUNCTION get_analytics_summary(
    p_property_id UUID DEFAULT NULL,
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() - INTERVAL '30 days',
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    p_event_category VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    event_type VARCHAR,
    event_count BIGINT,
    unique_users BIGINT,
    unique_sessions BIGINT,
    avg_timing NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ae.event_type,
        COUNT(*) as event_count,
        COUNT(DISTINCT ae.user_id) as unique_users,
        COUNT(DISTINCT ae.session_id) as unique_sessions,
        AVG(ae.timing_value) as avg_timing
    FROM analytics_events ae
    WHERE ae.created_at BETWEEN p_start_date AND p_end_date
    AND (p_property_id IS NULL OR ae.property_id = p_property_id)
    AND (p_event_category IS NULL OR ae.event_category = p_event_category)
    AND ae.is_valid = true
    GROUP BY ae.event_type
    ORDER BY event_count DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user journey/funnel analysis
CREATE OR REPLACE FUNCTION get_user_journey(
    p_property_id UUID DEFAULT NULL,
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() - INTERVAL '7 days',
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    p_event_types VARCHAR[] DEFAULT ARRAY['dashboard_view', 'application_view', 'application_approve']
)
RETURNS TABLE (
    step_number INTEGER,
    event_type VARCHAR,
    user_count BIGINT,
    conversion_rate NUMERIC
) AS $$
DECLARE
    total_users BIGINT;
BEGIN
    -- Get total users who started the journey
    SELECT COUNT(DISTINCT user_id) INTO total_users
    FROM analytics_events
    WHERE created_at BETWEEN p_start_date AND p_end_date
    AND (p_property_id IS NULL OR property_id = p_property_id)
    AND event_type = p_event_types[1]
    AND user_id IS NOT NULL;
    
    RETURN QUERY
    WITH RECURSIVE funnel_steps AS (
        SELECT 
            1 as step_number,
            p_event_types[1] as event_type,
            COUNT(DISTINCT user_id) as user_count
        FROM analytics_events
        WHERE created_at BETWEEN p_start_date AND p_end_date
        AND (p_property_id IS NULL OR property_id = p_property_id)
        AND event_type = p_event_types[1]
        AND user_id IS NOT NULL
        
        UNION ALL
        
        SELECT 
            fs.step_number + 1,
            p_event_types[fs.step_number + 1],
            COUNT(DISTINCT ae.user_id)
        FROM funnel_steps fs
        CROSS JOIN analytics_events ae
        WHERE fs.step_number < array_length(p_event_types, 1)
        AND ae.created_at BETWEEN p_start_date AND p_end_date
        AND (p_property_id IS NULL OR ae.property_id = p_property_id)
        AND ae.event_type = p_event_types[fs.step_number + 1]
        AND ae.user_id IS NOT NULL
        AND EXISTS (
            SELECT 1 FROM analytics_events ae2
            WHERE ae2.user_id = ae.user_id
            AND ae2.event_type = p_event_types[fs.step_number]
            AND ae2.created_at BETWEEN p_start_date AND p_end_date
            AND ae2.created_at <= ae.created_at
        )
        GROUP BY fs.step_number
    )
    SELECT 
        fs.step_number,
        fs.event_type,
        fs.user_count,
        CASE 
            WHEN total_users > 0 THEN ROUND((fs.user_count::NUMERIC / total_users) * 100, 2)
            ELSE 0
        END as conversion_rate
    FROM funnel_steps fs
    ORDER BY fs.step_number;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get performance metrics summary
CREATE OR REPLACE FUNCTION get_performance_metrics(
    p_property_id UUID DEFAULT NULL,
    p_start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() - INTERVAL '24 hours',
    p_end_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
RETURNS TABLE (
    metric_name VARCHAR,
    avg_value NUMERIC,
    min_value INTEGER,
    max_value INTEGER,
    p95_value NUMERIC,
    sample_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ae.event_type as metric_name,
        AVG(ae.timing_value) as avg_value,
        MIN(ae.timing_value) as min_value,
        MAX(ae.timing_value) as max_value,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ae.timing_value) as p95_value,
        COUNT(*) as sample_count
    FROM analytics_events ae
    WHERE ae.created_at BETWEEN p_start_date AND p_end_date
    AND (p_property_id IS NULL OR ae.property_id = p_property_id)
    AND ae.event_category = 'performance'
    AND ae.timing_value IS NOT NULL
    AND ae.is_valid = true
    GROUP BY ae.event_type
    HAVING COUNT(*) > 5 -- Only include metrics with sufficient samples
    ORDER BY avg_value DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup old analytics events
CREATE OR REPLACE FUNCTION cleanup_old_analytics_events(
    p_retention_days INTEGER DEFAULT 365
)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Archive or delete events older than retention period
    DELETE FROM analytics_events 
    WHERE created_at < NOW() - (p_retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup action
    PERFORM track_analytics_event(
        NULL, 'system', NULL,
        'cleanup', 'system', 'analytics_events_cleanup',
        jsonb_build_object(
            'deleted_count', deleted_count,
            'retention_days', p_retention_days,
            'cleanup_date', NOW()
        )
    );
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger for automatic user agent parsing and validation
CREATE OR REPLACE FUNCTION process_analytics_event()
RETURNS TRIGGER AS $$
BEGIN
    -- Set processed timestamp
    NEW.processed_at := NOW();
    
    -- Basic validation
    IF NEW.event_type IS NULL OR NEW.event_category IS NULL THEN
        NEW.is_valid := false;
        NEW.validation_errors := jsonb_build_object('error', 'Missing required fields');
    END IF;
    
    -- Set event timestamp if not provided
    IF NEW.event_timestamp IS NULL THEN
        NEW.event_timestamp := NEW.created_at;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER process_analytics_event_trigger
    BEFORE INSERT ON analytics_events
    FOR EACH ROW
    EXECUTE FUNCTION process_analytics_event();

-- =====================================================
-- VIEWS FOR COMMON ANALYTICS QUERIES
-- =====================================================

-- Daily analytics summary view
CREATE OR REPLACE VIEW daily_analytics_summary AS
SELECT 
    DATE(created_at) as analytics_date,
    property_id,
    event_category,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions,
    AVG(timing_value) as avg_timing
FROM analytics_events
WHERE is_valid = true
AND created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(created_at), property_id, event_category;

-- User engagement metrics view
CREATE OR REPLACE VIEW user_engagement_metrics AS
SELECT 
    user_id,
    user_type,
    property_id,
    DATE(created_at) as activity_date,
    COUNT(*) as total_events,
    COUNT(DISTINCT event_type) as unique_event_types,
    MIN(created_at) as first_event,
    MAX(created_at) as last_event,
    EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at)))/60 as session_duration_minutes
FROM analytics_events
WHERE user_id IS NOT NULL
AND is_valid = true
AND created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY user_id, user_type, property_id, DATE(created_at);

-- =====================================================
-- INITIAL DATA AND VERIFICATION
-- =====================================================

-- Track the migration as an analytics event
PERFORM track_analytics_event(
    NULL, 'system', NULL,
    'migration_complete', 'system', 'analytics_events_table_created',
    jsonb_build_object(
        'migration', '005_create_analytics_events_table',
        'version', '1.0.0',
        'tables_created', 1,
        'indexes_created', 14,
        'functions_created', 5,
        'views_created', 2
    )
);

-- Insert audit log entry
INSERT INTO audit_logs (
    user_type, action, entity_type, entity_name,
    details, compliance_event, risk_level
) VALUES (
    'system', 'create', 'analytics_events', 'table_migration',
    jsonb_build_object(
        'migration', '005_create_analytics_events_table',
        'version', '1.0.0',
        'tables_created', 1,
        'indexes_created', 14,
        'functions_created', 5,
        'views_created', 2,
        'rls_policies_created', 4
    ),
    true, 'low'
);

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 005 completed successfully!';
    RAISE NOTICE '📊 Analytics events table created for user interaction tracking';
    RAISE NOTICE '🔐 Row Level Security policies applied';
    RAISE NOTICE '⚡ Performance indexes created for time-series queries';
    RAISE NOTICE '📈 Analytics functions and views available';
    RAISE NOTICE '🎯 Ready for comprehensive user behavior analytics';
END $$;

-- 006_create_report_templates_table.sql
-- =====================================================
-- Migration 006: Create Report Templates Table
-- HR Manager System Consolidation - Task 2.5
-- =====================================================

-- Description: Create report_templates table for custom report definitions
-- Created: 2025-08-06
-- Version: 1.0.0

-- =====================================================
-- CREATE REPORT_TEMPLATES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS report_templates (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Template metadata
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL CHECK (category IN (
        'applications', 'employees', 'analytics', 'compliance',
        'performance', 'custom', 'system'
    )),
    
    -- Template ownership and sharing
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    user_type VARCHAR(20) CHECK (user_type IN ('hr', 'manager', 'system')),
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    is_public BOOLEAN DEFAULT false,
    is_system_template BOOLEAN DEFAULT false,
    
    -- Template configuration
    template_config JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Example template_config structure:
    -- {
    --   "report_type": "applications_summary",
    --   "data_sources": ["job_applications", "employees"],
    --   "date_range": {"type": "relative", "value": "last_30_days"},
    --   "filters": {"status": ["pending", "approved"]},
    --   "group_by": ["department", "position"],
    --   "metrics": ["total_count", "approval_rate", "avg_review_time"],
    --   "sorting": {"field": "created_at", "order": "desc"},
    --   "charts": [{"type": "bar", "x": "department", "y": "total_count"}]
    -- }
    
    -- Output configuration
    output_format JSONB DEFAULT '["pdf", "csv"]'::jsonb CHECK (
        output_format::jsonb ?| array['pdf', 'csv', 'excel', 'json']
    ),
    layout_config JSONB DEFAULT '{}'::jsonb,
    -- Layout config for styling, headers, footers, logos, etc.
    
    -- Scheduling and automation
    is_scheduled BOOLEAN DEFAULT false,
    schedule_config JSONB,
    -- Schedule config:
    -- {
    --   "frequency": "weekly", // daily, weekly, monthly, quarterly
    --   "day_of_week": 1, // 1=Monday for weekly
    --   "day_of_month": 1, // 1st for monthly  
    --   "time": "09:00",
    --   "timezone": "America/New_York",
    --   "recipients": ["manager@hotel.com", "hr@hotel.com"]
    -- }
    
    last_generated_at TIMESTAMP WITH TIME ZONE,
    next_generation_at TIMESTAMP WITH TIME ZONE,
    
    -- Usage and performance tracking
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    avg_generation_time_ms INTEGER,
    
    -- Validation and quality
    is_active BOOLEAN DEFAULT true,
    validation_errors JSONB,
    last_validated_at TIMESTAMP WITH TIME ZONE,
    
    -- Version control
    version INTEGER DEFAULT 1,
    parent_template_id UUID REFERENCES report_templates(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_schedule CHECK (
        (is_scheduled = false) OR 
        (is_scheduled = true AND schedule_config IS NOT NULL)
    ),
    CONSTRAINT valid_next_generation CHECK (
        next_generation_at IS NULL OR next_generation_at > created_at
    ),
    CONSTRAINT unique_name_per_user UNIQUE (name, created_by, property_id)
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_report_templates_created_by ON report_templates(created_by) WHERE created_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_report_templates_property ON report_templates(property_id) WHERE property_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_report_templates_category ON report_templates(category, is_active);

-- Public and sharing queries
CREATE INDEX IF NOT EXISTS idx_report_templates_public ON report_templates(is_public, category, created_at) WHERE is_public = true;
CREATE INDEX IF NOT EXISTS idx_report_templates_system ON report_templates(is_system_template, category) WHERE is_system_template = true;

-- Scheduling queries
CREATE INDEX IF NOT EXISTS idx_report_templates_scheduled ON report_templates(is_scheduled, next_generation_at, is_active) WHERE is_scheduled = true;

-- Usage and performance tracking
CREATE INDEX IF NOT EXISTS idx_report_templates_usage ON report_templates(usage_count, last_used_at);
CREATE INDEX IF NOT EXISTS idx_report_templates_performance ON report_templates(avg_generation_time_ms, usage_count) WHERE avg_generation_time_ms IS NOT NULL;

-- Version control
CREATE INDEX IF NOT EXISTS idx_report_templates_versions ON report_templates(parent_template_id, version) WHERE parent_template_id IS NOT NULL;

-- Full-text search on name and description
CREATE INDEX IF NOT EXISTS idx_report_templates_search ON report_templates USING GIN(to_tsvector('english', 
    name || ' ' || COALESCE(description, '')
));

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_report_templates_user_active ON report_templates(created_by, is_active, last_used_at) WHERE created_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_report_templates_property_category ON report_templates(property_id, category, is_active);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS
ALTER TABLE report_templates ENABLE ROW LEVEL SECURITY;

-- Users can see their own templates
CREATE POLICY "report_templates_user_own" ON report_templates
    FOR ALL USING (created_by::text = auth.uid()::text);

-- HR can see all templates
CREATE POLICY "report_templates_hr_full_access" ON report_templates
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- Managers can see public templates and property-specific templates
CREATE POLICY "report_templates_manager_access" ON report_templates
    FOR SELECT USING (
        is_public = true OR
        is_system_template = true OR
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = report_templates.property_id
        )
    );

-- Managers can create templates for their properties
CREATE POLICY "report_templates_manager_create" ON report_templates
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND pm.property_id = report_templates.property_id
        ) OR
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- System can manage all templates (for automated processes)
CREATE POLICY "report_templates_system_manage" ON report_templates
    FOR ALL USING (
        auth.jwt() ->> 'user_type' = 'system' OR
        auth.role() = 'service_role'
    );

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to create report template
CREATE OR REPLACE FUNCTION create_report_template(
    p_name VARCHAR,
    p_description TEXT,
    p_category VARCHAR,
    p_created_by UUID,
    p_user_type VARCHAR,
    p_property_id UUID DEFAULT NULL,
    p_template_config JSONB,
    p_output_format JSONB DEFAULT '["pdf"]'::jsonb,
    p_layout_config JSONB DEFAULT '{}'::jsonb,
    p_is_public BOOLEAN DEFAULT false,
    p_is_scheduled BOOLEAN DEFAULT false,
    p_schedule_config JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    template_id UUID;
BEGIN
    INSERT INTO report_templates (
        name, description, category, created_by, user_type, property_id,
        template_config, output_format, layout_config, is_public,
        is_scheduled, schedule_config
    ) VALUES (
        p_name, p_description, p_category, p_created_by, p_user_type, p_property_id,
        p_template_config, p_output_format, p_layout_config, p_is_public,
        p_is_scheduled, p_schedule_config
    ) RETURNING id INTO template_id;
    
    -- Calculate next generation time if scheduled
    IF p_is_scheduled AND p_schedule_config IS NOT NULL THEN
        UPDATE report_templates 
        SET next_generation_at = calculate_next_generation_time(p_schedule_config)
        WHERE id = template_id;
    END IF;
    
    RETURN template_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to calculate next generation time based on schedule
CREATE OR REPLACE FUNCTION calculate_next_generation_time(
    p_schedule_config JSONB
)
RETURNS TIMESTAMP WITH TIME ZONE AS $$
DECLARE
    frequency VARCHAR;
    next_time TIMESTAMP WITH TIME ZONE;
    schedule_time TIME;
    target_day INTEGER;
BEGIN
    frequency := p_schedule_config ->> 'frequency';
    schedule_time := COALESCE((p_schedule_config ->> 'time')::TIME, '09:00'::TIME);
    
    CASE frequency
        WHEN 'daily' THEN
            next_time := (CURRENT_DATE + INTERVAL '1 day') + schedule_time;
        WHEN 'weekly' THEN
            target_day := COALESCE((p_schedule_config ->> 'day_of_week')::INTEGER, 1); -- Monday
            next_time := (
                CURRENT_DATE + 
                ((target_day - EXTRACT(DOW FROM CURRENT_DATE) + 7) % 7)::INTEGER * INTERVAL '1 day'
            ) + schedule_time;
            -- If it's already past the time today and it's the target day, schedule for next week
            IF next_time <= NOW() THEN
                next_time := next_time + INTERVAL '7 days';
            END IF;
        WHEN 'monthly' THEN
            target_day := COALESCE((p_schedule_config ->> 'day_of_month')::INTEGER, 1);
            next_time := (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month' + (target_day - 1) * INTERVAL '1 day') + schedule_time;
        WHEN 'quarterly' THEN
            next_time := (DATE_TRUNC('quarter', CURRENT_DATE) + INTERVAL '3 months') + schedule_time;
        ELSE
            next_time := NOW() + INTERVAL '1 day'; -- Default fallback
    END CASE;
    
    RETURN next_time;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get available templates for a user
CREATE OR REPLACE FUNCTION get_available_templates(
    p_user_id UUID,
    p_user_type VARCHAR,
    p_property_id UUID DEFAULT NULL,
    p_category VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    name VARCHAR,
    description TEXT,
    category VARCHAR,
    is_public BOOLEAN,
    is_system_template BOOLEAN,
    created_by UUID,
    usage_count INTEGER,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rt.id,
        rt.name,
        rt.description,
        rt.category,
        rt.is_public,
        rt.is_system_template,
        rt.created_by,
        rt.usage_count,
        rt.last_used_at,
        rt.created_at
    FROM report_templates rt
    WHERE rt.is_active = true
    AND (p_category IS NULL OR rt.category = p_category)
    AND (
        -- Own templates
        rt.created_by = p_user_id OR
        -- Public templates
        rt.is_public = true OR
        -- System templates
        rt.is_system_template = true OR
        -- HR sees all
        (p_user_type = 'hr') OR
        -- Property-specific templates for managers
        (p_user_type = 'manager' AND rt.property_id = p_property_id)
    )
    ORDER BY 
        rt.is_system_template DESC,
        rt.is_public DESC,
        rt.usage_count DESC,
        rt.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update template usage statistics
CREATE OR REPLACE FUNCTION update_template_usage(
    p_template_id UUID,
    p_generation_time_ms INTEGER DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    current_avg INTEGER;
    current_count INTEGER;
    new_avg INTEGER;
    success BOOLEAN := false;
BEGIN
    -- Get current statistics
    SELECT usage_count, avg_generation_time_ms 
    INTO current_count, current_avg
    FROM report_templates 
    WHERE id = p_template_id;
    
    -- Calculate new average generation time
    IF p_generation_time_ms IS NOT NULL THEN
        new_avg := CASE 
            WHEN current_avg IS NULL THEN p_generation_time_ms
            ELSE ((current_avg * current_count) + p_generation_time_ms) / (current_count + 1)
        END;
    ELSE
        new_avg := current_avg;
    END IF;
    
    -- Update statistics
    UPDATE report_templates
    SET usage_count = usage_count + 1,
        last_used_at = NOW(),
        last_generated_at = NOW(),
        avg_generation_time_ms = new_avg,
        updated_at = NOW()
    WHERE id = p_template_id;
    
    GET DIAGNOSTICS success = FOUND;
    RETURN success;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get scheduled templates ready for generation
CREATE OR REPLACE FUNCTION get_scheduled_templates_ready()
RETURNS TABLE (
    id UUID,
    name VARCHAR,
    property_id UUID,
    template_config JSONB,
    schedule_config JSONB,
    next_generation_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rt.id,
        rt.name,
        rt.property_id,
        rt.template_config,
        rt.schedule_config,
        rt.next_generation_at
    FROM report_templates rt
    WHERE rt.is_scheduled = true
    AND rt.is_active = true
    AND rt.next_generation_at <= NOW()
    ORDER BY rt.next_generation_at ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update next generation time after processing
CREATE OR REPLACE FUNCTION update_next_generation_time(
    p_template_id UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    schedule_config JSONB;
    success BOOLEAN := false;
BEGIN
    -- Get schedule config
    SELECT rt.schedule_config INTO schedule_config
    FROM report_templates rt
    WHERE rt.id = p_template_id;
    
    -- Update next generation time
    UPDATE report_templates
    SET next_generation_at = calculate_next_generation_time(schedule_config),
        updated_at = NOW()
    WHERE id = p_template_id;
    
    GET DIAGNOSTICS success = FOUND;
    RETURN success;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate template configuration
CREATE OR REPLACE FUNCTION validate_report_template(
    p_template_id UUID
)
RETURNS JSONB AS $$
DECLARE
    template_record RECORD;
    validation_result JSONB := '{"valid": true, "errors": []}'::jsonb;
    config_errors JSONB := '[]'::jsonb;
BEGIN
    -- Get template record
    SELECT * INTO template_record
    FROM report_templates
    WHERE id = p_template_id;
    
    IF NOT FOUND THEN
        RETURN '{"valid": false, "errors": ["Template not found"]}'::jsonb;
    END IF;
    
    -- Validate template_config
    IF template_record.template_config IS NULL OR template_record.template_config = '{}'::jsonb THEN
        config_errors := config_errors || '["Template configuration is empty"]'::jsonb;
    END IF;
    
    -- Validate required fields in template_config
    IF NOT (template_record.template_config ? 'report_type') THEN
        config_errors := config_errors || '["Missing report_type in configuration"]'::jsonb;
    END IF;
    
    IF NOT (template_record.template_config ? 'data_sources') THEN
        config_errors := config_errors || '["Missing data_sources in configuration"]'::jsonb;
    END IF;
    
    -- Validate schedule configuration if scheduled
    IF template_record.is_scheduled THEN
        IF template_record.schedule_config IS NULL THEN
            config_errors := config_errors || '["Scheduled template missing schedule_config"]'::jsonb;
        ELSIF NOT (template_record.schedule_config ? 'frequency') THEN
            config_errors := config_errors || '["Schedule configuration missing frequency"]'::jsonb;
        END IF;
    END IF;
    
    -- Build final result
    IF jsonb_array_length(config_errors) > 0 THEN
        validation_result := jsonb_build_object(
            'valid', false,
            'errors', config_errors
        );
        
        -- Update template with validation errors
        UPDATE report_templates
        SET validation_errors = config_errors,
            last_validated_at = NOW()
        WHERE id = p_template_id;
    ELSE
        -- Clear any previous validation errors
        UPDATE report_templates
        SET validation_errors = NULL,
            last_validated_at = NOW()
        WHERE id = p_template_id;
    END IF;
    
    RETURN validation_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger to automatically update updated_at
CREATE OR REPLACE FUNCTION update_report_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_report_templates_updated_at_trigger
    BEFORE UPDATE ON report_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_report_templates_updated_at();

-- Trigger for audit logging on report templates
CREATE TRIGGER audit_report_templates_trigger
    AFTER INSERT OR UPDATE OR DELETE ON report_templates
    FOR EACH ROW 
    EXECUTE FUNCTION enhanced_audit_trigger_function();

-- =====================================================
-- SYSTEM TEMPLATES
-- =====================================================

-- Insert common system templates
INSERT INTO report_templates (
    name, description, category, user_type, template_config,
    is_system_template, is_public, output_format
) VALUES 
(
    'Application Status Summary',
    'Summary of job applications by status and department',
    'applications',
    'system',
    '{
        "report_type": "applications_summary",
        "data_sources": ["job_applications"],
        "date_range": {"type": "relative", "value": "last_30_days"},
        "group_by": ["status", "department"],
        "metrics": ["total_count", "approval_rate"],
        "sorting": {"field": "total_count", "order": "desc"},
        "charts": [
            {"type": "pie", "field": "status", "title": "Applications by Status"},
            {"type": "bar", "x": "department", "y": "total_count", "title": "Applications by Department"}
        ]
    }'::jsonb,
    true,
    true,
    '["pdf", "csv"]'::jsonb
),
(
    'Employee Onboarding Progress',
    'Track employee onboarding completion rates and timelines',
    'employees',
    'system',
    '{
        "report_type": "onboarding_progress",
        "data_sources": ["employees", "onboarding_sessions"],
        "date_range": {"type": "relative", "value": "last_60_days"},
        "group_by": ["onboarding_status", "department"],
        "metrics": ["completion_rate", "avg_completion_time"],
        "charts": [
            {"type": "funnel", "stages": ["not_started", "in_progress", "employee_completed", "approved"]},
            {"type": "line", "x": "date", "y": "completion_rate", "title": "Completion Rate Trend"}
        ]
    }'::jsonb,
    true,
    true,
    '["pdf", "csv"]'::jsonb
),
(
    'Property Performance Dashboard',
    'Comprehensive performance metrics for properties',
    'analytics',
    'system',
    '{
        "report_type": "property_performance",
        "data_sources": ["properties", "job_applications", "employees"],
        "date_range": {"type": "relative", "value": "last_90_days"},
        "group_by": ["property_id"],
        "metrics": ["total_applications", "hire_rate", "avg_onboarding_time", "employee_retention"],
        "charts": [
            {"type": "scatter", "x": "total_applications", "y": "hire_rate", "title": "Applications vs Hire Rate"},
            {"type": "bar", "x": "property_name", "y": "avg_onboarding_time", "title": "Average Onboarding Time"}
        ]
    }'::jsonb,
    true,
    false, -- Only visible to HR
    '["pdf", "excel"]'::jsonb
)
ON CONFLICT (name, created_by, property_id) DO NOTHING;

-- =====================================================
-- INITIAL DATA AND VERIFICATION
-- =====================================================

-- Insert audit log entry
INSERT INTO audit_logs (
    user_type, action, entity_type, entity_name,
    details, compliance_event, risk_level
) VALUES (
    'system', 'create', 'report_templates', 'table_migration',
    jsonb_build_object(
        'migration', '006_create_report_templates_table',
        'version', '1.0.0',
        'tables_created', 1,
        'indexes_created', 9,
        'functions_created', 8,
        'system_templates_created', 3,
        'rls_policies_created', 5
    ),
    true, 'low'
);

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 006 completed successfully!';
    RAISE NOTICE '📊 Report templates table created with comprehensive configuration';
    RAISE NOTICE '🔐 Row Level Security policies applied';
    RAISE NOTICE '⚡ Performance indexes created for template queries';
    RAISE NOTICE '📈 System templates installed for common use cases';
    RAISE NOTICE '⏰ Scheduling system ready for automated report generation';
    RAISE NOTICE '🎯 Ready for custom report creation and management';
END $$;

-- 007_create_saved_filters_table.sql
-- =====================================================
-- Migration 007: Create Saved Filters Table
-- HR Manager System Consolidation - Task 2
-- =====================================================

-- Description: Create saved filters table for dashboards and lists
-- Created: 2025-08-06
-- Version: 1.0.0

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- CREATE SAVED_FILTERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS saved_filters (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Filter metadata
    name VARCHAR(255) NOT NULL,
    description TEXT,
    filter_type VARCHAR(50) NOT NULL CHECK (filter_type IN (
        'employee', 'application', 'property', 'onboarding', 
        'audit_log', 'notification', 'report', 'analytics'
    )),
    
    -- Filter configuration
    filters JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- User context
    user_id UUID NOT NULL,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    
    -- Sharing and defaults
    is_default BOOLEAN DEFAULT false,
    is_shared BOOLEAN DEFAULT false,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================

-- User queries
CREATE INDEX IF NOT EXISTS idx_saved_filters_user_id ON saved_filters(user_id);

-- Filter type queries
CREATE INDEX IF NOT EXISTS idx_saved_filters_filter_type ON saved_filters(filter_type);

-- Property-scoped queries
CREATE INDEX IF NOT EXISTS idx_saved_filters_property_id ON saved_filters(property_id) WHERE property_id IS NOT NULL;

-- Shared filters
CREATE INDEX IF NOT EXISTS idx_saved_filters_shared ON saved_filters(is_shared) WHERE is_shared = true;

-- Default filters
CREATE INDEX IF NOT EXISTS idx_saved_filters_default ON saved_filters(user_id, filter_type, is_default) WHERE is_default = true;

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_saved_filters_user_type ON saved_filters(user_id, filter_type);

-- =====================================================
-- ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS
ALTER TABLE saved_filters ENABLE ROW LEVEL SECURITY;

-- Users can manage their own filters
CREATE POLICY "saved_filters_user_own" ON saved_filters
    FOR ALL USING (
        user_id::text = auth.uid()::text
    );

-- Users can view shared filters
CREATE POLICY "saved_filters_shared_read" ON saved_filters
    FOR SELECT USING (
        is_shared = true
    );

-- Managers can only see filters for their property or shared filters
CREATE POLICY "saved_filters_manager_property" ON saved_filters
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM property_managers pm
            JOIN users u ON u.id = pm.manager_id
            WHERE u.id::text = auth.uid()::text 
            AND (pm.property_id = saved_filters.property_id OR saved_filters.is_shared = true)
        )
    );

-- HR can see all filters
CREATE POLICY "saved_filters_hr_full_access" ON saved_filters
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id::text = auth.uid()::text AND role = 'hr'
        )
    );

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to create or update a saved filter
CREATE OR REPLACE FUNCTION upsert_saved_filter(
    p_name VARCHAR,
    p_filter_type VARCHAR,
    p_filters JSONB,
    p_user_id UUID,
    p_description TEXT DEFAULT NULL,
    p_property_id UUID DEFAULT NULL,
    p_is_default BOOLEAN DEFAULT false,
    p_is_shared BOOLEAN DEFAULT false,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID AS $$
DECLARE
    filter_id UUID;
BEGIN
    -- If setting as default, unset other defaults for this user and filter type
    IF p_is_default THEN
        UPDATE saved_filters 
        SET is_default = false 
        WHERE user_id = p_user_id 
        AND filter_type = p_filter_type 
        AND is_default = true;
    END IF;
    
    -- Insert or update the filter
    INSERT INTO saved_filters (
        name, description, filter_type, filters, user_id,
        property_id, is_default, is_shared, metadata
    ) VALUES (
        p_name, p_description, p_filter_type, p_filters, p_user_id,
        p_property_id, p_is_default, p_is_shared, p_metadata
    )
    ON CONFLICT (user_id, name, filter_type) 
    DO UPDATE SET
        filters = EXCLUDED.filters,
        description = EXCLUDED.description,
        is_default = EXCLUDED.is_default,
        is_shared = EXCLUDED.is_shared,
        metadata = EXCLUDED.metadata,
        updated_at = NOW()
    RETURNING id INTO filter_id;
    
    RETURN filter_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get default filter for a user and type
CREATE OR REPLACE FUNCTION get_default_filter(
    p_user_id UUID,
    p_filter_type VARCHAR
)
RETURNS TABLE (
    id UUID,
    name VARCHAR,
    filters JSONB,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sf.id,
        sf.name,
        sf.filters,
        sf.metadata
    FROM saved_filters sf
    WHERE sf.user_id = p_user_id
    AND sf.filter_type = p_filter_type
    AND sf.is_default = true
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_saved_filters_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER saved_filters_updated_at_trigger
    BEFORE UPDATE ON saved_filters
    FOR EACH ROW
    EXECUTE FUNCTION update_saved_filters_updated_at();

-- =====================================================
-- ADD UNIQUE CONSTRAINT
-- =====================================================

-- Ensure filter names are unique per user and filter type
ALTER TABLE saved_filters 
ADD CONSTRAINT unique_filter_name_per_user_type 
UNIQUE (user_id, name, filter_type);

-- =====================================================
-- INITIAL DATA
-- =====================================================

-- Insert system notification about migration
INSERT INTO audit_logs (
    user_type, action, entity_type, entity_name,
    details, compliance_event, risk_level
) VALUES (
    'system', 'create', 'saved_filters', 'table_migration',
    jsonb_build_object(
        'migration', '007_create_saved_filters_table',
        'version', '1.0.0',
        'tables_created', 1,
        'indexes_created', 6,
        'functions_created', 2,
        'triggers_created', 1
    ),
    true, 'low'
) ON CONFLICT DO NOTHING;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Migration 007 completed successfully!';
    RAISE NOTICE '💾 Saved filters table created';
    RAISE NOTICE '🔐 Row Level Security policies applied';
    RAISE NOTICE '⚡ Performance indexes created';
    RAISE NOTICE '🔧 Helper functions installed';
    RAISE NOTICE '📝 Ready for saving user dashboard filters';
END $$;

