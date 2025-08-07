#!/usr/bin/env python3
"""
Create the onboarding_form_data table for testing
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# For now, let's just print the SQL that needs to be run
print("""
Please run this SQL in your Supabase SQL Editor:

-- Create the onboarding_form_data table
CREATE TABLE IF NOT EXISTS onboarding_form_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR NOT NULL,
    employee_id VARCHAR NOT NULL,
    step_id VARCHAR NOT NULL,
    form_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(token, step_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_form_data_token ON onboarding_form_data(token);
CREATE INDEX IF NOT EXISTS idx_onboarding_form_data_employee ON onboarding_form_data(employee_id);

-- Enable RLS (but allow all access for testing)
ALTER TABLE onboarding_form_data ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (for testing)
CREATE POLICY "Allow all operations" ON onboarding_form_data
FOR ALL USING (true) WITH CHECK (true);
""")