# Setting Up I-9 Tables in Supabase

## Important: Manual Steps Required

Due to Supabase security restrictions, tables must be created via the Supabase Dashboard SQL Editor.

## Step 1: Create Tables in Supabase Dashboard

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **SQL Editor** in the left sidebar
4. Copy and paste the SQL from `create_i9_tables.sql`
5. Click **Run** to execute

## Step 2: Get Your Service Role Key

⚠️ **IMPORTANT**: The service role key bypasses all RLS policies. Keep it secure!

1. In Supabase Dashboard, go to **Settings** → **API**
2. Find the **Service Role Key** (starts with `eyJ...`)
3. Add it to your `.env` file:
   ```
   SUPABASE_SERVICE_KEY=your_service_role_key_here
   ```

## Step 3: Update Your Backend Configuration

The backend code has been updated to:
- Use the service role key when available for admin operations
- Fall back to anon key for regular operations
- Properly handle RLS policies

## Step 4: Verify Setup

Run the verification script:
```bash
python3 verify_i9_setup.py
```

## Database Tables Created

### 1. `i9_forms`
- Stores I-9 Section 1 and Section 2 data
- Includes signature data and completion status
- Links to employee records

### 2. `i9_section2_documents`
- Stores metadata for uploaded documents
- Includes OCR extracted data
- References to storage bucket

### 3. `w4_forms`
- Stores W-4 tax withholding forms
- Includes PDF URLs and signature data
- Yearly versioning support

## RLS Policies

The tables have RLS enabled with the following policies:
- Employees can view their own records
- HR users can view all records
- System (service role) can insert/update records

## Cloud Sync Implementation

The frontend has been updated to:
1. **I-9 Section 1**: Saves form data, signatures, and PDFs to cloud
2. **I-9 Section 2**: Saves document metadata and OCR results to cloud
3. **General Progress**: Uses the standard `saveProgress` mechanism for all steps

## Testing the Implementation

1. Start the backend server:
   ```bash
   python3 -m uvicorn app.main_enhanced:app --reload
   ```

2. Start the frontend:
   ```bash
   npm run dev
   ```

3. Test the I-9 flow:
   - Complete I-9 Section 1
   - Upload documents in Section 2
   - Navigate away and back to verify persistence
   - Check that data is saved in Supabase

## Troubleshooting

### "Table does not exist" Error
- Make sure you've run the SQL in Supabase Dashboard
- Tables must be created manually first time

### "RLS policy violation" Error
- Ensure you're using the service role key for backend operations
- Check that the `.env` file has `SUPABASE_SERVICE_KEY` set

### Data Not Persisting
- Verify API endpoints are being called (check browser console)
- Ensure employee ID is not a demo/test ID
- Check backend logs for errors