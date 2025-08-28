# Run Supabase Migrations - CRITICAL FOR PRODUCTION

## 🚨 URGENT: Run these migrations to fix production errors

### Option 1: Via Supabase Dashboard (Recommended)

1. Go to your Supabase project: https://app.supabase.com
2. Navigate to **SQL Editor** in the left sidebar
3. Copy and paste the entire SQL below
4. Click **Run** button

### Option 2: Via psql command line

```bash
psql postgresql://[YOUR_DATABASE_URL] < hotel-onboarding-backend/migrations/create_document_tables.sql
```

### SQL Migration to Run:

```sql
-- Migration: Create document storage tables for production
-- Date: 2024-08-23
-- Purpose: Fix production issues with missing tables

-- 1. Create i9_forms table (CRITICAL - fixing production error)
CREATE TABLE IF NOT EXISTS i9_forms (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  employee_id VARCHAR(255) NOT NULL,
  section VARCHAR(50) NOT NULL,
  data JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_i9_employee ON i9_forms(employee_id);
CREATE INDEX IF NOT EXISTS idx_i9_section ON i9_forms(section);

-- 2. Create w4_forms table for W-4 document storage
CREATE TABLE IF NOT EXISTS w4_forms (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  employee_id VARCHAR(255) NOT NULL,
  data JSONB,
  pdf_url TEXT,
  signed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_w4_employee ON w4_forms(employee_id);

-- 3. Create signed_documents table for company policies and other signed docs
CREATE TABLE IF NOT EXISTS signed_documents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  employee_id VARCHAR(255) NOT NULL,
  document_type VARCHAR(100) NOT NULL,
  document_name VARCHAR(255),
  pdf_url TEXT,
  pdf_data BYTEA, -- Optional: store PDF binary
  signed_at TIMESTAMP,
  signature_data TEXT,
  property_id UUID,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_signed_docs_employee ON signed_documents(employee_id);
CREATE INDEX IF NOT EXISTS idx_signed_docs_type ON signed_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_signed_docs_property ON signed_documents(property_id);
```

## What This Fixes:

✅ **I-9 Forms Error**: Fixes "Could not find the table 'public.i9_forms'" error
✅ **Document Storage**: Enables proper storage of W-4 and company policy documents
✅ **Performance**: Adds indexes for fast queries

## After Running Migrations:

1. **Deploy Backend to Heroku**:
```bash
cd hotel-onboarding-backend
git push heroku main
```

2. **Deploy Frontend to Vercel**:
```bash
cd hotel-onboarding-frontend
vercel --prod
```

3. **Test in Production**:
- Try submitting an I-9 form
- Test document uploads
- Verify no more 500 errors

## Verification Query:

Run this to verify tables were created:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('i9_forms', 'w4_forms', 'signed_documents');
```

Should return 3 rows if successful.