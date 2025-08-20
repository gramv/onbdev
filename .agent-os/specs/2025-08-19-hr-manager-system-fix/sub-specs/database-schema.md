# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-08-19-hr-manager-system-fix/spec.md

## Schema Modifications

### Fix property_managers Junction Table

```sql
-- Drop existing incorrect constraints
ALTER TABLE property_managers 
DROP CONSTRAINT IF EXISTS property_managers_user_id_fkey;

-- Add correct foreign key relationships
ALTER TABLE property_managers
ADD CONSTRAINT property_managers_user_id_fkey 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE property_managers
ADD CONSTRAINT property_managers_property_id_fkey
FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE;

-- Add unique constraint to prevent duplicate assignments
ALTER TABLE property_managers
ADD CONSTRAINT unique_user_property 
UNIQUE (user_id, property_id);

-- Add created_at timestamp
ALTER TABLE property_managers
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
```

### Add I-9 Section 2 Storage

```sql
-- Create table for I-9 Section 2 data
CREATE TABLE IF NOT EXISTS i9_section2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    manager_id UUID NOT NULL REFERENCES users(id),
    
    -- Document verification
    document_type VARCHAR(100) NOT NULL,
    document_number VARCHAR(100),
    document_expiry DATE,
    issuing_authority VARCHAR(200),
    
    -- Additional document (if List B + C)
    additional_document_type VARCHAR(100),
    additional_document_number VARCHAR(100),
    additional_document_expiry DATE,
    
    -- Employer information
    employer_name VARCHAR(200) NOT NULL,
    employer_title VARCHAR(100) NOT NULL,
    employer_signature TEXT NOT NULL,
    signature_date DATE NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure one Section 2 per employee
    CONSTRAINT unique_employee_section2 UNIQUE (employee_id)
);

-- Index for performance
CREATE INDEX idx_i9_section2_employee ON i9_section2(employee_id);
CREATE INDEX idx_i9_section2_manager ON i9_section2(manager_id);
```

### Add Manager Review Tracking

```sql
-- Create table for application reviews
CREATE TABLE IF NOT EXISTS application_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id),
    
    -- Review details
    action VARCHAR(20) NOT NULL CHECK (action IN ('approved', 'rejected', 'request_info')),
    comments TEXT,
    
    -- Approval details (if approved)
    pay_rate DECIMAL(10,2),
    pay_frequency VARCHAR(20),
    start_date DATE,
    start_time TIME,
    supervisor_name VARCHAR(200),
    special_instructions TEXT,
    
    -- Timestamps
    reviewed_at TIMESTAMP DEFAULT NOW(),
    
    -- Prevent duplicate reviews
    CONSTRAINT unique_application_review UNIQUE (application_id)
);

-- Index for performance
CREATE INDEX idx_reviews_application ON application_reviews(application_id);
CREATE INDEX idx_reviews_reviewer ON application_reviews(reviewer_id);
CREATE INDEX idx_reviews_action ON application_reviews(action);
```

### Fix Users Table Password Field

```sql
-- Ensure password_hash column exists and is used correctly
ALTER TABLE users
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Migrate any existing password data (if needed)
UPDATE users 
SET password_hash = password 
WHERE password_hash IS NULL AND password IS NOT NULL;

-- Drop old password column if it exists
ALTER TABLE users
DROP COLUMN IF EXISTS password;

-- Add is_active flag for manager deactivation
ALTER TABLE users
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Add password reset tracking
ALTER TABLE users
ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255),
ADD COLUMN IF NOT EXISTS password_reset_expires TIMESTAMP,
ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT false;
```

### Add Indexes for Performance

```sql
-- Optimize common queries
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_properties_active ON properties(is_active);
CREATE INDEX IF NOT EXISTS idx_applications_property_status ON job_applications(property_id, status);
CREATE INDEX IF NOT EXISTS idx_employees_property ON employees(property_id);
```

## Migration Notes

1. Run schema updates in transaction to ensure atomicity
2. Backup database before applying changes
3. Test foreign key constraints with sample data
4. Verify indexes improve query performance
5. Update Supabase RLS policies if needed