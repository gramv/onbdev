# Frontend Debugging Instructions

## Added Debug Logging

I've added comprehensive console logging to the ApplicationsTab.tsx component to help debug the approval issue.

### Debug Logs Added:

#### 1. Application Fetching Debug
- Shows which endpoint is being used (HR vs Manager)
- Shows user role and token info
- Shows count of applications and pending applications

#### 2. Approval Process Debug
- Shows selected application details
- Shows job offer data being sent
- Shows user role and token
- Shows each FormData field being added
- Shows the exact API endpoint being called

#### 3. Error Handling Debug
- Shows detailed error information
- Shows response status, data, and headers
- Shows specific validation errors for 422 responses
- Logs each validation error with field and message

## How to Use the Debug Logs

1. **Open Browser Developer Tools** (F12)
2. **Go to Console tab**
3. **Try to approve an application**
4. **Look for debug messages starting with 🔍, ✅, or ❌**

## What to Look For

### Normal Flow Should Show:
```
🔍 Fetching applications: {userRole: "manager", endpoint: "http://127.0.0.1:8000/manager/applications", ...}
✅ Applications fetched: {count: X, pending: Y}
🔍 DEBUG: Starting approval process
Selected application: {id: "...", status: "pending", ...}
Job offer data: {job_title: "...", supervisor: "...", ...}
Adding to FormData: job_title = "Front Desk Agent"
Adding to FormData: supervisor = "Mike Wilson"
...
🚀 Making approval request to: http://127.0.0.1:8000/applications/[ID]/approve
✅ Approval successful: {employee_id: "...", message: "..."}
```

### Error Flow Will Show:
```
❌ Error approving application: [Error Object]
Error details: {status: 422, data: {...}, ...}
422 Validation Error Details: [Detailed error info]
Validation errors:
  - supervisor: field required (input: undefined)
```

## Common Issues to Check:

### 1. Stale Data
- Look for "Application is not pending" message
- Check if the application ID exists in the fetched applications

### 2. Missing Fields
- Check if all FormData fields are being added correctly
- Look for validation errors showing missing required fields

### 3. Wrong Endpoint
- Verify the correct endpoint is being used based on user role
- Manager should use `/manager/applications`
- HR should use `/hr/applications`

### 4. Token Issues
- Check if token is present and not truncated
- Verify token format looks correct

## Next Steps

1. **Try the approval again** with the browser console open
2. **Copy all the debug output** from the console
3. **Share the debug output** so we can see exactly what's happening
4. **Look for any red error messages** that might indicate the root cause

The backend is working perfectly (confirmed by tests), so the issue is definitely in the frontend data flow or request formatting.