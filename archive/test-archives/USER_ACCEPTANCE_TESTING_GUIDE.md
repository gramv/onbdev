# User Acceptance Testing Guide

## Overview

This guide provides comprehensive test scenarios for the HR Manager Dashboard System. These tests should be performed manually to ensure the system meets all requirements and provides a good user experience.

## Prerequisites

### Backend Setup
1. Start the backend server:
   ```bash
   cd hotel-onboarding-backend
   source venv/bin/activate
   python -m app.main_enhanced
   ```

2. Verify backend is running:
   ```bash
   curl http://127.0.0.1:8000/healthz
   ```

### Frontend Setup
1. Start the frontend development server:
   ```bash
   cd hotel-onboarding-frontend
   npm run dev
   ```

2. Open browser to: http://localhost:5173

### Test Accounts
- **HR Account**: hr@hoteltest.com / admin123
- **Manager Account**: manager@hoteltest.com / manager123

## Test Scenarios

### 1. HR Complete Workflow Testing

#### 1.1 HR Authentication
**Objective**: Verify HR login and authentication flow

**Steps**:
1. Navigate to http://localhost:5173
2. Enter HR credentials: hr@hoteltest.com / admin123
3. Click "Sign In"

**Expected Results**:
- ✅ Login successful
- ✅ Redirected to HR Dashboard
- ✅ Welcome message shows "Welcome, hr@hoteltest.com"
- ✅ Dashboard shows statistics cards (Properties, Managers, Employees, Applications)

**Test Status**: [ ] Pass [ ] Fail

---

#### 1.2 HR Dashboard Overview
**Objective**: Verify HR dashboard displays correct information

**Steps**:
1. After successful login, observe the dashboard
2. Check all statistics cards
3. Verify tab navigation is present

**Expected Results**:
- ✅ Statistics cards show numerical values
- ✅ Five tabs visible: Properties, Managers, Employees, Applications, Analytics
- ✅ Professional, clean design
- ✅ Responsive layout

**Test Status**: [ ] Pass [ ] Fail

---

#### 1.3 Properties Management
**Objective**: Test property creation, editing, and management

**Steps**:
1. Click on "Properties" tab
2. Click "Create Property" button
3. Fill in property details:
   - Name: "Test Hotel UAT"
   - Address: "123 Test Street"
   - City: "Test City"
   - State: "CA"
   - ZIP: "90210"
   - Phone: "(555) 123-4567"
4. Submit the form
5. Verify property appears in the list
6. Click on the property to view details
7. Edit the property (change phone number)
8. Save changes

**Expected Results**:
- ✅ Property creation form works correctly
- ✅ Form validation works (required fields)
- ✅ Property appears in list after creation
- ✅ Property details can be viewed
- ✅ Property can be edited successfully
- ✅ QR code is generated for the property

**Test Status**: [ ] Pass [ ] Fail

---

#### 1.4 Manager Management
**Objective**: Test manager creation and assignment

**Steps**:
1. Click on "Managers" tab
2. Click "Create Manager" button
3. Fill in manager details:
   - Email: "testmanager@test.com"
   - First Name: "Test"
   - Last Name: "Manager"
   - Password: "password123"
4. Submit the form
5. Assign manager to a property
6. Verify manager appears in the list

**Expected Results**:
- ✅ Manager creation form works correctly
- ✅ Manager can be assigned to properties
- ✅ Manager list displays correctly
- ✅ Manager details can be viewed

**Test Status**: [ ] Pass [ ] Fail

---

#### 1.5 Employee Directory
**Objective**: Test employee management and filtering

**Steps**:
1. Click on "Employees" tab
2. Observe the employee list
3. Use search functionality to find specific employees
4. Filter by property (if multiple properties exist)
5. Filter by department
6. Filter by employment status
7. Click on an employee to view details

**Expected Results**:
- ✅ Employee list displays correctly
- ✅ Search functionality works
- ✅ Property filter works
- ✅ Department filter works
- ✅ Status filter works
- ✅ Employee details modal works
- ✅ Pagination works for large lists

**Test Status**: [ ] Pass [ ] Fail

---

#### 1.6 Applications Management
**Objective**: Test job application review and management

**Steps**:
1. Click on "Applications" tab
2. Observe the applications list
3. Filter applications by status (pending, approved, rejected)
4. Filter by property
5. Click on an application to view details
6. Review applicant information
7. Use search to find specific applications

**Expected Results**:
- ✅ Applications list displays correctly
- ✅ Status filtering works
- ✅ Property filtering works
- ✅ Application details modal shows complete information
- ✅ Search functionality works
- ✅ Applications are sortable by date, status, etc.

**Test Status**: [ ] Pass [ ] Fail

---

#### 1.7 Analytics Dashboard
**Objective**: Test analytics and reporting features

**Steps**:
1. Click on "Analytics" tab
2. Observe system metrics
3. Check property performance charts
4. Review employee statistics
5. Test data export functionality (if available)

**Expected Results**:
- ✅ Analytics tab loads correctly
- ✅ System metrics are displayed
- ✅ Charts and graphs render properly
- ✅ Data appears accurate and up-to-date
- ✅ Export functionality works (if implemented)

**Test Status**: [ ] Pass [ ] Fail

---

### 2. Manager Complete Workflow Testing

#### 2.1 Manager Authentication
**Objective**: Verify manager login and authentication flow

**Steps**:
1. Logout from HR account (if logged in)
2. Navigate to login page
3. Enter Manager credentials: manager@hoteltest.com / manager123
4. Click "Sign In"

**Expected Results**:
- ✅ Login successful
- ✅ Redirected to Manager Dashboard
- ✅ Welcome message shows manager name
- ✅ Dashboard shows property-specific information

**Test Status**: [ ] Pass [ ] Fail

---

#### 2.2 Manager Dashboard Overview
**Objective**: Verify manager dashboard shows property-specific data

**Steps**:
1. After successful login, observe the dashboard
2. Check property information display
3. Verify statistics are property-specific
4. Check tab navigation

**Expected Results**:
- ✅ Property name and details displayed
- ✅ Statistics show property-specific numbers
- ✅ Three tabs visible: Applications, Employees, Analytics
- ✅ No access to Properties or Managers tabs (HR-only)

**Test Status**: [ ] Pass [ ] Fail

---

#### 2.3 Manager Application Review
**Objective**: Test application review and approval workflow

**Steps**:
1. Click on "Applications" tab (should be default)
2. Observe applications for the manager's property
3. Click on a pending application
4. Review applicant details
5. Click "Approve" on an application
6. Fill in job offer details:
   - Job Title: "Front Desk Agent"
   - Start Date: Future date
   - Start Time: "09:00"
   - Pay Rate: "18.50"
   - Pay Frequency: "hourly"
   - Benefits Eligible: "Yes"
   - Supervisor: "Test Supervisor"
7. Submit approval
8. Verify application status changes

**Expected Results**:
- ✅ Only property-specific applications shown
- ✅ Application details display correctly
- ✅ Approval workflow works
- ✅ Job offer form validates correctly
- ✅ Application status updates after approval
- ✅ Success notification appears

**Test Status**: [ ] Pass [ ] Fail

---

#### 2.4 Manager Employee Management
**Objective**: Test employee directory for property

**Steps**:
1. Click on "Employees" tab
2. Observe employee list for the property
3. Filter by department
4. Search for specific employees
5. Click on an employee to view details
6. Check employee onboarding status

**Expected Results**:
- ✅ Only property-specific employees shown
- ✅ Department filtering works
- ✅ Search functionality works
- ✅ Employee details display correctly
- ✅ Onboarding status is visible

**Test Status**: [ ] Pass [ ] Fail

---

#### 2.5 Manager Analytics
**Objective**: Test property-specific analytics

**Steps**:
1. Click on "Analytics" tab
2. Observe property-specific metrics
3. Check employee performance data
4. Review application statistics

**Expected Results**:
- ✅ Analytics show property-specific data only
- ✅ Metrics are relevant to the property
- ✅ Charts and graphs render correctly
- ✅ Data appears accurate

**Test Status**: [ ] Pass [ ] Fail

---

### 3. Cross-Browser Compatibility Testing

#### 3.1 Chrome Testing
**Objective**: Verify functionality in Google Chrome

**Steps**:
1. Open Google Chrome
2. Navigate to the application
3. Perform key workflows (login, navigation, forms)
4. Check responsive design

**Expected Results**:
- ✅ All functionality works correctly
- ✅ UI renders properly
- ✅ No console errors
- ✅ Responsive design works

**Test Status**: [ ] Pass [ ] Fail

---

#### 3.2 Firefox Testing
**Objective**: Verify functionality in Mozilla Firefox

**Steps**:
1. Open Mozilla Firefox
2. Navigate to the application
3. Perform key workflows (login, navigation, forms)
4. Check responsive design

**Expected Results**:
- ✅ All functionality works correctly
- ✅ UI renders properly
- ✅ No console errors
- ✅ Responsive design works

**Test Status**: [ ] Pass [ ] Fail

---

#### 3.3 Safari Testing (macOS)
**Objective**: Verify functionality in Safari

**Steps**:
1. Open Safari
2. Navigate to the application
3. Perform key workflows (login, navigation, forms)
4. Check responsive design

**Expected Results**:
- ✅ All functionality works correctly
- ✅ UI renders properly
- ✅ No console errors
- ✅ Responsive design works

**Test Status**: [ ] Pass [ ] Fail

---

### 4. Mobile Responsiveness Testing

#### 4.1 Mobile Phone Testing
**Objective**: Verify mobile responsiveness on phone-sized screens

**Steps**:
1. Open browser developer tools
2. Set viewport to iPhone/Android size (375x667)
3. Test login functionality
4. Navigate through dashboards
5. Test forms and modals
6. Check touch interactions

**Expected Results**:
- ✅ Layout adapts to mobile screen
- ✅ Navigation is touch-friendly
- ✅ Forms are usable on mobile
- ✅ Text is readable without zooming
- ✅ Buttons are appropriately sized

**Test Status**: [ ] Pass [ ] Fail

---

#### 4.2 Tablet Testing
**Objective**: Verify responsiveness on tablet-sized screens

**Steps**:
1. Set viewport to tablet size (768x1024)
2. Test all major functionality
3. Check layout adaptation
4. Test touch interactions

**Expected Results**:
- ✅ Layout works well on tablet
- ✅ All functionality accessible
- ✅ Good use of screen space
- ✅ Touch-friendly interface

**Test Status**: [ ] Pass [ ] Fail

---

### 5. Performance and Usability Testing

#### 5.1 Page Load Performance
**Objective**: Verify acceptable page load times

**Steps**:
1. Open browser developer tools
2. Navigate to Network tab
3. Clear cache and reload application
4. Measure load times for key pages
5. Check for unnecessary network requests

**Expected Results**:
- ✅ Initial page load < 3 seconds
- ✅ Dashboard loads < 2 seconds
- ✅ No excessive network requests
- ✅ Resources load efficiently

**Test Status**: [ ] Pass [ ] Fail

---

#### 5.2 User Experience Testing
**Objective**: Evaluate overall user experience

**Steps**:
1. Perform common user tasks
2. Evaluate ease of navigation
3. Check for intuitive workflows
4. Test error handling
5. Verify feedback mechanisms

**Expected Results**:
- ✅ Navigation is intuitive
- ✅ Common tasks are easy to complete
- ✅ Error messages are helpful
- ✅ Success feedback is clear
- ✅ Loading states are shown

**Test Status**: [ ] Pass [ ] Fail

---

### 6. Security and Access Control Testing

#### 6.1 Role-Based Access Control
**Objective**: Verify proper access restrictions

**Steps**:
1. Login as HR user
2. Verify access to all HR features
3. Logout and login as Manager
4. Verify restricted access to manager features only
5. Try to access HR-only URLs directly as manager
6. Test session timeout

**Expected Results**:
- ✅ HR has access to all features
- ✅ Manager has restricted access
- ✅ Direct URL access is properly restricted
- ✅ Session timeout works correctly
- ✅ Proper error messages for unauthorized access

**Test Status**: [ ] Pass [ ] Fail

---

#### 6.2 Data Security
**Objective**: Verify data is properly protected

**Steps**:
1. Check that sensitive data is not exposed in URLs
2. Verify API calls include proper authentication
3. Test logout functionality
4. Check for XSS vulnerabilities in forms

**Expected Results**:
- ✅ No sensitive data in URLs
- ✅ API calls are authenticated
- ✅ Logout clears session properly
- ✅ Forms handle input safely

**Test Status**: [ ] Pass [ ] Fail

---

## Test Summary

### Overall Test Results

| Test Category | Pass | Fail | Notes |
|---------------|------|------|-------|
| HR Workflow | [ ] | [ ] | |
| Manager Workflow | [ ] | [ ] | |
| Cross-Browser | [ ] | [ ] | |
| Mobile Responsive | [ ] | [ ] | |
| Performance | [ ] | [ ] | |
| Security | [ ] | [ ] | |

### Critical Issues Found
1. 
2. 
3. 

### Minor Issues Found
1. 
2. 
3. 

### Recommendations
1. 
2. 
3. 

### Sign-off

**Tester Name**: ________________  
**Date**: ________________  
**Overall Status**: [ ] Approved [ ] Needs Fixes  

**Comments**:
_________________________________________________
_________________________________________________
_________________________________________________

---

## Automated Test Verification

Before performing manual UAT, ensure all automated tests pass:

### Backend Tests
```bash
cd hotel-onboarding-backend
python3 test_backend_integration_simple.py
```

### Frontend Tests
```bash
cd hotel-onboarding-frontend
npm test
```

### Integration Tests
```bash
# Backend integration tests
cd hotel-onboarding-backend
source venv/bin/activate
python -m pytest tests/test_integration.py -v

# Frontend integration tests
cd hotel-onboarding-frontend
npm test -- --testPathPatterns="integration"
```

All automated tests should pass before beginning manual UAT.