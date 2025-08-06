-- Create tables for I-9 forms if they don't exist
-- This script adds proper cloud sync support for I-9 Section 1 and Section 2

-- I-9 Forms table (if not exists)
CREATE TABLE IF NOT EXISTS i9_forms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
  section VARCHAR(20) NOT NULL, -- 'section1', 'section2', 'section3'
  form_data JSONB,
  signed BOOLEAN DEFAULT false,
  signature_data TEXT,
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(employee_id, section)
);

-- I-9 Section 2 Documents metadata table
CREATE TABLE IF NOT EXISTS i9_section2_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
  document_id VARCHAR(255) UNIQUE NOT NULL, -- Frontend generated ID
  document_type VARCHAR(50), -- 'list_a', 'list_b', 'list_c'
  document_name VARCHAR(255), -- 'US Passport', 'Driver's License', etc.
  file_name VARCHAR(255),
  file_size INTEGER,
  storage_path TEXT, -- Path in Supabase storage
  uploaded_at TIMESTAMP WITH TIME ZONE,
  ocr_data JSONB, -- OCR extracted data
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  INDEX idx_i9_docs_employee (employee_id),
  INDEX idx_i9_docs_type (document_type)
);

-- W-4 Forms table (if not exists)
CREATE TABLE IF NOT EXISTS w4_forms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_id UUID REFERENCES employees(id) ON DELETE CASCADE,
  tax_year INTEGER NOT NULL,
  form_data JSONB,
  signed BOOLEAN DEFAULT false,
  signature_data TEXT,
  pdf_url TEXT, -- Stored PDF URL
  completed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(employee_id, tax_year)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_i9_employee_section ON i9_forms(employee_id, section);
CREATE INDEX IF NOT EXISTS idx_w4_employee_year ON w4_forms(employee_id, tax_year);

-- Add RLS policies for security
ALTER TABLE i9_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE i9_section2_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE w4_forms ENABLE ROW LEVEL SECURITY;

-- Policies for i9_forms
CREATE POLICY "Employees can view their own I-9 forms" ON i9_forms
  FOR SELECT USING (auth.uid()::text = employee_id::text);

CREATE POLICY "HR can view all I-9 forms" ON i9_forms
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE users.id = auth.uid() 
      AND users.role IN ('hr', 'admin')
    )
  );

CREATE POLICY "System can insert I-9 forms" ON i9_forms
  FOR INSERT WITH CHECK (true);

CREATE POLICY "System can update I-9 forms" ON i9_forms
  FOR UPDATE USING (true);

-- Policies for i9_section2_documents
CREATE POLICY "Employees can view their own documents" ON i9_section2_documents
  FOR SELECT USING (auth.uid()::text = employee_id::text);

CREATE POLICY "HR can view all documents" ON i9_section2_documents
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE users.id = auth.uid() 
      AND users.role IN ('hr', 'admin')
    )
  );

CREATE POLICY "System can insert documents" ON i9_section2_documents
  FOR INSERT WITH CHECK (true);

-- Policies for w4_forms
CREATE POLICY "Employees can view their own W-4 forms" ON w4_forms
  FOR SELECT USING (auth.uid()::text = employee_id::text);

CREATE POLICY "HR can view all W-4 forms" ON w4_forms
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users 
      WHERE users.id = auth.uid() 
      AND users.role IN ('hr', 'admin')
    )
  );

CREATE POLICY "System can insert W-4 forms" ON w4_forms
  FOR INSERT WITH CHECK (true);

CREATE POLICY "System can update W-4 forms" ON w4_forms
  FOR UPDATE USING (true);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_i9_forms_updated_at BEFORE UPDATE ON i9_forms
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_w4_forms_updated_at BEFORE UPDATE ON w4_forms
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE i9_forms IS 'Stores I-9 Employment Eligibility Verification forms for all sections';
COMMENT ON TABLE i9_section2_documents IS 'Stores metadata for documents uploaded in I-9 Section 2 verification';
COMMENT ON TABLE w4_forms IS 'Stores W-4 Employee Withholding Certificate forms';