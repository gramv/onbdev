-- Simple version of I-9 tables creation script
-- Run this in Supabase SQL Editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create i9_forms table
CREATE TABLE IF NOT EXISTS i9_forms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id TEXT NOT NULL,
  section VARCHAR(20) NOT NULL,
  form_data JSONB,
  signed BOOLEAN DEFAULT false,
  signature_data TEXT,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(employee_id, section)
);

-- Create i9_section2_documents table
CREATE TABLE IF NOT EXISTS i9_section2_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id TEXT NOT NULL,
  document_id VARCHAR(255) UNIQUE NOT NULL,
  document_type VARCHAR(50),
  document_name VARCHAR(255),
  file_name VARCHAR(255),
  file_size INTEGER,
  storage_path TEXT,
  uploaded_at TIMESTAMPTZ,
  ocr_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create w4_forms table
CREATE TABLE IF NOT EXISTS w4_forms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id TEXT NOT NULL,
  tax_year INTEGER NOT NULL,
  form_data JSONB,
  signed BOOLEAN DEFAULT false,
  signature_data TEXT,
  pdf_url TEXT,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(employee_id, tax_year)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_i9_employee_section ON i9_forms(employee_id, section);
CREATE INDEX IF NOT EXISTS idx_i9_docs_employee ON i9_section2_documents(employee_id);
CREATE INDEX IF NOT EXISTS idx_i9_docs_type ON i9_section2_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_w4_employee_year ON w4_forms(employee_id, tax_year);

-- Optional: Enable RLS (Row Level Security)
-- Uncomment these lines if you want to enable RLS
-- ALTER TABLE i9_forms ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE i9_section2_documents ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE w4_forms ENABLE ROW LEVEL SECURITY;

-- Simple RLS policies (optional - uncomment if needed)
-- These allow all operations when authenticated
-- CREATE POLICY "Enable all for authenticated users" ON i9_forms
--   FOR ALL USING (true) WITH CHECK (true);
-- 
-- CREATE POLICY "Enable all for authenticated users" ON i9_section2_documents
--   FOR ALL USING (true) WITH CHECK (true);
-- 
-- CREATE POLICY "Enable all for authenticated users" ON w4_forms
--   FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions to authenticated and service roles
GRANT ALL ON i9_forms TO authenticated;
GRANT ALL ON i9_section2_documents TO authenticated;
GRANT ALL ON w4_forms TO authenticated;
GRANT ALL ON i9_forms TO service_role;
GRANT ALL ON i9_section2_documents TO service_role;
GRANT ALL ON w4_forms TO service_role;