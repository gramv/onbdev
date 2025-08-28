# System Applications UI Test Guide

## Test Setup
1. Backend is running on http://localhost:8000
2. Frontend is running on http://localhost:3000

## Test Credentials
- **HR User**: hr@test.com / test123

## Test Steps

### 1. Login as HR
1. Navigate to http://localhost:3000
2. Click "Login" 
3. Enter credentials:
   - Email: hr@test.com
   - Password: test123
4. Click "Login" button

### 2. Navigate to System Applications
1. Once logged in, you should see the HR Dashboard
2. Look for the "System Applications" tab in the navigation
3. Click on "System Applications"

### 3. Verify Functionality
The System Applications tab should display:
- ✅ **All applications across all properties** (30 total based on test data)
- ✅ **Property filter dropdown** - shows which property each application belongs to
- ✅ **Status filter** - filter by pending/approved/rejected/talent_pool
- ✅ **Department and Position filters**
- ✅ **Search functionality** - search by applicant name/email
- ✅ **Property information** - shows property name, city, state for each application
- ✅ **Action buttons** - Approve/Reject for pending applications
- ✅ **Pagination** - if more than 50 applications

### 4. Test Filters
1. **Property Filter**: Select a specific property from dropdown
   - Should only show applications for that property
2. **Status Filter**: Select "Pending"
   - Should show only pending applications (9 based on test data)
3. **Search**: Type an applicant name
   - Should filter results in real-time

### 5. Test Actions (Optional)
1. Find a pending application
2. Click the green checkmark to approve
3. Fill in the job offer details:
   - Start date
   - Pay rate
   - Employment type
4. Click "Approve & Send Offer"

## Expected Results
- ✅ System Applications tab is visible in HR navigation
- ✅ All applications from all properties are displayed
- ✅ Each application shows its property information
- ✅ Filters work correctly
- ✅ Pagination works for large datasets
- ✅ Approve/Reject functionality works for pending applications

## API Endpoint Used
- `GET /api/hr/applications/all` - Returns all applications across all properties with filters

## Component Location
- Frontend: `/src/components/dashboard/SystemApplicationsTab.tsx`
- Backend: `/app/main_enhanced.py` (line 2249)