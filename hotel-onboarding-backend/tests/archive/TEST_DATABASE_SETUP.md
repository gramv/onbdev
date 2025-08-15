# Test Database Setup Instructions

## ✅ Current Status
- **Backend**: Using TEST database (kzommszdhapvqpekpvnt.supabase.co)
- **Production**: Safe and untouched (onmjxtyamdpkhnflwwmj.supabase.co)
- **Issue**: RLS policies blocking test data creation

## 🚀 Steps to Fix Test Database

### 1. Disable RLS in Supabase Dashboard

Go to your TEST Supabase dashboard:
1. Open https://supabase.com/dashboard/project/kzommszdhapvqpekpvnt
2. Go to **SQL Editor** (left sidebar)
3. Open the file `disable_test_rls.sql` and copy its contents
4. Paste and run the SQL in the Supabase SQL editor
5. You should see "Success" messages for each ALTER TABLE command

**Alternative: Using Supabase CLI**
```bash
supabase db push disable_test_rls.sql --project-ref kzommszdhapvqpekpvnt
```

### 2. Create Test Data

After disabling RLS, run the setup script:

```bash
cd hotel-onboarding-backend
python3 setup_test_database.py
```

This will create:
- **Property**: Demo Hotel (ID: a99239dd-ebde-4c69-b862-ecba9e878798)
- **Manager**: manager@demo.com / demo123
- **HR User**: hr@demo.com / hr123

### 3. Test the System

1. **Login as Manager**:
   - Go to: http://localhost:3000/manager
   - Email: `manager@demo.com`
   - Password: `demo123`
   - You should see the Demo Hotel dashboard

2. **Test Job Application**:
   - http://localhost:3000/apply/a99239dd-ebde-4c69-b862-ecba9e878798

3. **Test Employee Onboarding**:
   - Use the test token URL generated earlier
   - Or generate a new one via the manager dashboard

## 🔍 Verification

Both servers should be running:
- **Frontend**: http://localhost:3000 ✅
- **Backend**: http://localhost:8000 ✅

Test the health endpoint:
```bash
curl http://localhost:8000/healthz
```

## ⚠️ Important Notes

1. **Never run `disable_test_rls.sql` on production!**
2. The test database has RLS disabled for easier testing
3. All test data uses simple SHA256 password hashing (not for production)
4. The property ID `a99239dd-ebde-4c69-b862-ecba9e878798` is consistent across all test scripts

## 🎯 What Works After Setup

- Manager login and dashboard
- Property statistics
- Job applications
- Employee onboarding with JWT tokens
- All 7 document types (I-9, W-4, etc.)
- Manager document access
- HR oversight features

## 🔒 Production Safety

The production database remains completely untouched because:
- We switched to `.env.test` configuration
- Different Supabase project IDs
- All scripts check for test database URL
- RLS remains enabled on production