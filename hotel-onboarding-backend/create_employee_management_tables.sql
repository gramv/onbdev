-- Enhanced Employee Management Tables
-- Creates tables for employee lifecycle, performance tracking, and communication

-- Employee Goals Table
CREATE TABLE IF NOT EXISTS employee_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'general',
    target_value DECIMAL(10,2),
    current_value DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(50),
    status VARCHAR(50) DEFAULT 'not_started',
    priority VARCHAR(20) DEFAULT 'medium',
    due_date DATE NOT NULL,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Employee Reviews Table
CREATE TABLE IF NOT EXISTS employee_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id),
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    overall_rating VARCHAR(50) NOT NULL,
    goals_achievement JSONB DEFAULT '{}',
    strengths JSONB DEFAULT '[]',
    areas_for_improvement JSONB DEFAULT '[]',
    development_plan JSONB DEFAULT '{}',
    comments TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Employee Milestones Table
CREATE TABLE IF NOT EXISTS employee_milestones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    stage VARCHAR(100),
    achieved_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee Messages Table
CREATE TABLE IF NOT EXISTS employee_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES users(id),
    recipient_ids JSONB NOT NULL,
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'general',
    priority VARCHAR(20) DEFAULT 'normal',
    template_id UUID,
    status VARCHAR(50) DEFAULT 'sent',
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee Communications Table
CREATE TABLE IF NOT EXISTS employee_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    message_id UUID REFERENCES employee_messages(id),
    type VARCHAR(100) NOT NULL,
    subject VARCHAR(255),
    content TEXT,
    sender_id UUID REFERENCES users(id),
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Message Templates Table
CREATE TABLE IF NOT EXISTS message_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    template_type VARCHAR(50) DEFAULT 'general',
    variables JSONB DEFAULT '[]',
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add lifecycle_stage column to employees table if it doesn't exist
ALTER TABLE employees ADD COLUMN IF NOT EXISTS lifecycle_stage VARCHAR(50) DEFAULT 'onboarding';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_employee_goals_employee_id ON employee_goals(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_goals_status ON employee_goals(status);
CREATE INDEX IF NOT EXISTS idx_employee_goals_due_date ON employee_goals(due_date);

CREATE INDEX IF NOT EXISTS idx_employee_reviews_employee_id ON employee_reviews(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_reviews_reviewer_id ON employee_reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_employee_reviews_created_at ON employee_reviews(created_at);

CREATE INDEX IF NOT EXISTS idx_employee_milestones_employee_id ON employee_milestones(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_milestones_type ON employee_milestones(type);
CREATE INDEX IF NOT EXISTS idx_employee_milestones_achieved_at ON employee_milestones(achieved_at);

CREATE INDEX IF NOT EXISTS idx_employee_messages_sender_id ON employee_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_employee_messages_sent_at ON employee_messages(sent_at);

CREATE INDEX IF NOT EXISTS idx_employee_communications_employee_id ON employee_communications(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_communications_created_at ON employee_communications(created_at);

CREATE INDEX IF NOT EXISTS idx_message_templates_template_type ON message_templates(template_type);

-- Create RLS policies for employee management tables
ALTER TABLE employee_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE employee_communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_templates ENABLE ROW LEVEL SECURITY;

-- RLS Policies for employee_goals
CREATE POLICY "HR can manage all employee goals" ON employee_goals
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'hr'
        )
    );

CREATE POLICY "Managers can manage goals for their property employees" ON employee_goals
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users u
            JOIN managers m ON u.id = m.user_id
            JOIN employees e ON e.property_id = m.property_id
            WHERE u.id = auth.uid() 
            AND u.role = 'manager'
            AND e.id = employee_goals.employee_id
        )
    );

-- RLS Policies for employee_reviews
CREATE POLICY "HR can manage all employee reviews" ON employee_reviews
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'hr'
        )
    );

CREATE POLICY "Managers can manage reviews for their property employees" ON employee_reviews
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users u
            JOIN managers m ON u.id = m.user_id
            JOIN employees e ON e.property_id = m.property_id
            WHERE u.id = auth.uid() 
            AND u.role = 'manager'
            AND e.id = employee_reviews.employee_id
        )
    );

-- RLS Policies for employee_milestones
CREATE POLICY "HR can view all employee milestones" ON employee_milestones
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'hr'
        )
    );

CREATE POLICY "Managers can view milestones for their property employees" ON employee_milestones
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u
            JOIN managers m ON u.id = m.user_id
            JOIN employees e ON e.property_id = m.property_id
            WHERE u.id = auth.uid() 
            AND u.role = 'manager'
            AND e.id = employee_milestones.employee_id
        )
    );

-- RLS Policies for employee_messages
CREATE POLICY "HR can manage all employee messages" ON employee_messages
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'hr'
        )
    );

CREATE POLICY "Managers can send messages to their property employees" ON employee_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'manager'
            AND users.id = employee_messages.sender_id
        )
    );

-- RLS Policies for employee_communications
CREATE POLICY "HR can view all employee communications" ON employee_communications
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'hr'
        )
    );

CREATE POLICY "Managers can view communications for their property employees" ON employee_communications
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users u
            JOIN managers m ON u.id = m.user_id
            JOIN employees e ON e.property_id = m.property_id
            WHERE u.id = auth.uid() 
            AND u.role = 'manager'
            AND e.id = employee_communications.employee_id
        )
    );

-- RLS Policies for message_templates
CREATE POLICY "HR can manage all message templates" ON message_templates
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'hr'
        )
    );

CREATE POLICY "Managers can view message templates" ON message_templates
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'manager'
        )
    );

-- Insert default message templates
INSERT INTO message_templates (name, subject, content, template_type, variables, created_by) VALUES
('Welcome Message', 'Welcome to {{property_name}}!', 
'Dear {{employee_name}},

Welcome to {{property_name}}! We are excited to have you join our team as a {{position}} in the {{department}} department.

Your first day is scheduled for {{start_date}}. Please report to {{manager_name}} at {{report_time}}.

If you have any questions, please don''t hesitate to reach out.

Best regards,
{{sender_name}}', 
'onboarding', 
'["employee_name", "property_name", "position", "department", "start_date", "manager_name", "report_time", "sender_name"]',
(SELECT id FROM users WHERE role = 'hr' LIMIT 1)),

('Performance Review Reminder', 'Performance Review Scheduled', 
'Dear {{employee_name}},

This is a reminder that your performance review is scheduled for {{review_date}} at {{review_time}}.

Please prepare by reviewing your goals and accomplishments from the past review period.

Best regards,
{{reviewer_name}}', 
'performance', 
'["employee_name", "review_date", "review_time", "reviewer_name"]',
(SELECT id FROM users WHERE role = 'hr' LIMIT 1)),

('Goal Achievement', 'Congratulations on Goal Achievement!', 
'Dear {{employee_name}},

Congratulations on achieving your goal: {{goal_title}}!

Your dedication and hard work are truly appreciated. Keep up the excellent work!

Best regards,
{{sender_name}}', 
'recognition', 
'["employee_name", "goal_title", "sender_name"]',
(SELECT id FROM users WHERE role = 'hr' LIMIT 1)),

('Training Reminder', 'Training Session Reminder', 
'Dear {{employee_name}},

This is a reminder about the upcoming training session: {{training_title}}

Date: {{training_date}}
Time: {{training_time}}
Location: {{training_location}}

Please make sure to attend this important session.

Best regards,
{{sender_name}}', 
'training', 
'["employee_name", "training_title", "training_date", "training_time", "training_location", "sender_name"]',
(SELECT id FROM users WHERE role = 'hr' LIMIT 1));