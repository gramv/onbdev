# Hotel Onboarding System - Testing Guide

## Current Status
All changes are on branch: `modular-employee-onboarding-system`

## Quick Start Testing

### 1. Start the Backend
```bash
cd hotel-onboarding-backend
python3 -m uvicorn app.main_enhanced:app --reload --port 8000
```

### 2. Start the Frontend
```bash
cd hotel-onboarding-frontend
npm run dev
```

### 3. Test Routes

#### Component Testing (Recommended First)
- **URL**: http://localhost:3000/test-steps
- **Purpose**: Test all 19 step components individually
- **Features**: 
  - Navigate between all components
  - Test language switching
  - Verify prop passing works
  - Check form validation

#### Full Onboarding Flow
- **URL**: http://localhost:3000/onboard?token=test-token
- **Purpose**: Test complete employee onboarding
- **Features**:
  - Uses demo mode (falls back if backend not running)
  - Saves progress automatically
  - Complete all 16 steps

#### Other Test Routes
- **HR Dashboard**: http://localhost:3000/hr
- **Manager Dashboard**: http://localhost:3000/manager
- **Job Application**: http://localhost:3000/apply

## What Was Fixed

1. **Frontend Components** ✅
   - All 19 components now use StepProps pattern
   - Fixed: W4ReviewSignStep, I9ReviewSignStep, EmployeeReviewStep
   - Fixed import error for TraffickingAwarenessStep

2. **Backend APIs** ✅
   - Employee onboarding endpoints implemented
   - Token verification works
   - Progress tracking implemented
   - Three-phase workflow complete

3. **Integration** ✅
   - Frontend calls backend APIs
   - Falls back to demo mode if backend unavailable
   - Progress syncs between frontend and backend

## Testing Checklist

### Frontend Component Testing
- [ ] Navigate to /test-steps
- [ ] Click through each component
- [ ] Test language toggle (EN/ES)
- [ ] Fill out sample data in forms
- [ ] Verify validation works

### Backend API Testing
- [ ] Start backend server
- [ ] Check http://localhost:8000/docs for API documentation
- [ ] Test token verification endpoint
- [ ] Test progress update endpoint

### Integration Testing
- [ ] Start both frontend and backend
- [ ] Navigate to /onboard?token=test-token
- [ ] Complete a few steps
- [ ] Check browser console for API calls
- [ ] Verify data persists on page refresh

## Common Issues

1. **Import Errors**: Fixed - TraffickingAwarenessStep spelling
2. **Port Conflicts**: Frontend runs on 3000, backend on 8000
3. **Demo Mode**: If backend not running, frontend uses demo data

## Branch Information

All work is on: `modular-employee-onboarding-system`

To switch branches:
```bash
git checkout modular-employee-onboarding-system
```

To see all branches:
```bash
git branch -a
```

## Test Data

Use these for testing:
- Token: `test-token` or `demo-token`
- Employee: Auto-populated in demo mode
- Manager login: Check backend for test accounts
- HR login: Check backend for test accounts