# HR Manager Dashboard System - Testing Guide

## 🚀 Application Status: READY FOR TESTING

The HR Manager Dashboard System is fully implemented and ready for comprehensive testing. This guide covers testing the HR and Manager dashboards (onboarding functionality excluded as requested).

## 📋 Prerequisites

### Backend Requirements:
- Python 3.13+ ✅
- Virtual environment with dependencies ✅
- FastAPI backend server ✅
- Test data and accounts ✅

### Frontend Requirements:
- Node.js and npm ✅
- React 18 with TypeScript ✅
- Vite build system ✅
- Comprehensive test suite ✅

## 🏃‍♂️ Quick Start

### 1. Start the Backend Server

```bash
cd hotel-onboarding-backend

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Start the FastAPI server
python3 -m app.main_enhanced
```

The backend will be available at: `http://127.0.0.1:8000`

### 2. Start the Frontend Development Server

```bash
cd hotel-onboarding-frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## 🧪 Testing Scenarios

### HR Dashboard Testing

#### Login as HR User
1. Navigate to: `http://localhost:5173/login?role=hr`
2. Use test credentials:
   - **Email**: `hr@hoteltest.com`
   - **Password**: `password`
   - Or click "Use Test Credentials" button

#### HR Dashboard Features to Test:

**1. Dashboard Overview**
- ✅ View dashboard statistics (Properties, Managers, Employees, Pending Applications)
- ✅ Responsive layout on different screen sizes
- ✅ Navigation between tabs

**2. Properties Tab**
- ✅ View all properties in the system
- ✅ Create new properties
- ✅ Edit property details
- ✅ Generate QR codes for applications
- ✅ Activate/deactivate properties
- ✅ Search and filter properties

**3. Managers Tab**
- ✅ View all managers
- ✅ Assign managers to properties
- ✅ Create new manager accounts
- ✅ Update manager information
- ✅ Search and filter managers

**4. Employees Tab**
- ✅ View all employees across all properties
- ✅ Search and filter employees
- ✅ View employee details
- ✅ Export employee data
- ✅ Advanced filtering options

**5. Applications Tab**
- ✅ View all job applications system-wide
- ✅ Filter by status (pending, approved, rejected)
- ✅ Review application details
- ✅ Approve/reject applications
- ✅ Export application data

**6. Analytics Tab**
- ✅ System-wide analytics
- ✅ Property performance metrics
- ✅ Application processing statistics
- ✅ Employee satisfaction metrics
- ✅ Interactive charts and graphs

### Manager Dashboard Testing

#### Login as Manager User
1. Navigate to: `http://localhost:5173/login?role=manager`
2. Use test credentials:
   - **Email**: `manager@hoteltest.com`
   - **Password**: `password`
   - Or click "Use Test Credentials" button

#### Manager Dashboard Features to Test:

**1. Dashboard Overview**
- ✅ View property-specific statistics
- ✅ Property information display
- ✅ Quick stats cards
- ✅ Responsive design

**2. Applications Tab (Default)**
- ✅ View applications for assigned property only
- ✅ Review application details
- ✅ Approve/reject applications
- ✅ Filter applications by status
- ✅ Search applications
- ✅ Pending applications badge

**3. Employees Tab**
- ✅ View employees for assigned property
- ✅ Search and filter property employees
- ✅ View employee details
- ✅ Monitor employment status

**4. Analytics Tab**
- ✅ Property-specific analytics
- ✅ Application response time metrics
- ✅ Staff efficiency statistics
- ✅ Occupancy rate tracking

## 🔐 Role-Based Access Control Testing

### Test Scenarios:

**1. HR User Access**
- ✅ Can access HR dashboard
- ✅ Cannot access Manager dashboard
- ✅ Has access to all system data
- ✅ Can manage properties and managers

**2. Manager User Access**
- ✅ Can access Manager dashboard
- ✅ Cannot access HR dashboard
- ✅ Only sees data for assigned property
- ✅ Cannot access system-wide management

**3. Unauthenticated Access**
- ✅ Redirected to login page
- ✅ Cannot access protected routes
- ✅ Session management works correctly

## 📱 Responsive Design Testing

### Screen Sizes to Test:
- **Desktop**: 1920x1080, 1366x768
- **Tablet**: 768x1024, 1024x768
- **Mobile**: 375x667, 414x896

### Features to Verify:
- ✅ Navigation adapts to screen size
- ✅ Data tables become scrollable/card view
- ✅ Forms remain usable
- ✅ Charts and graphs scale properly

## 🌐 Cross-Browser Testing

### Browsers to Test:
- ✅ Chrome/Chromium (primary)
- ✅ Firefox
- ✅ Safari (macOS)
- ✅ Edge

## 🔧 API Integration Testing

### Backend Endpoints to Test:

**Authentication:**
- `POST /auth/login` - User login
- Token validation and expiration

**HR Endpoints:**
- `GET /hr/dashboard-stats` - Dashboard statistics
- `GET /hr/properties` - Properties list
- `POST /hr/properties` - Create property
- `GET /hr/managers` - Managers list
- `GET /hr/applications` - All applications

**Manager Endpoints:**
- Property-specific data filtering
- Application management for assigned property

## 🧪 Automated Testing

### Run Unit Tests:
```bash
cd hotel-onboarding-frontend
npm test
```

### Run Integration Tests:
```bash
npm test -- --testPathPatterns=integration
```

### Run Specific Test Suites:
```bash
# Dashboard tests
npm test -- --testPathPatterns=Dashboard

# Authentication tests
npm test -- --testPathPatterns=Auth

# Form validation tests
npm test -- --testPathPatterns=formValidation
```

## 🐛 Common Issues & Troubleshooting

### Backend Issues:
1. **Port 8000 already in use**: Kill existing processes or change port
2. **Database connection**: Ensure test data is loaded
3. **CORS errors**: Backend should handle CORS for localhost:5173

### Frontend Issues:
1. **API connection**: Ensure backend is running on port 8000
2. **Authentication**: Clear localStorage if login issues persist
3. **Build errors**: Run `npm install` to ensure dependencies

### Test Issues:
1. **Jest configuration**: Types should be properly configured
2. **Mock issues**: Clear mocks between tests
3. **Async testing**: Use waitFor for async operations

## 📊 Test Data

### Pre-loaded Test Data:
- **Properties**: 3-5 test properties
- **Managers**: 2-3 test managers
- **Employees**: 10-15 test employees
- **Applications**: 5-10 test applications

### Creating Additional Test Data:
```bash
cd hotel-onboarding-backend
python3 create_test_data.py
```

## ✅ Testing Checklist

### HR Dashboard:
- [ ] Login successful
- [ ] Dashboard loads with statistics
- [ ] All tabs accessible
- [ ] Properties management works
- [ ] Manager assignment works
- [ ] Application review works
- [ ] Analytics display correctly
- [ ] Search/filter functionality
- [ ] Data export works
- [ ] Logout works

### Manager Dashboard:
- [ ] Login successful
- [ ] Property information displays
- [ ] Statistics are property-specific
- [ ] Applications tab works
- [ ] Employee management works
- [ ] Analytics are property-specific
- [ ] Cannot access HR features
- [ ] Logout works

### General:
- [ ] Responsive design works
- [ ] Cross-browser compatibility
- [ ] Error handling works
- [ ] Loading states display
- [ ] API integration stable
- [ ] Role-based access enforced

## 🎯 Performance Testing

### Metrics to Monitor:
- Page load times < 2 seconds
- API response times < 500ms
- Smooth navigation between tabs
- Efficient data loading
- Memory usage optimization

## 📝 Bug Reporting

When reporting bugs, include:
1. **Steps to reproduce**
2. **Expected behavior**
3. **Actual behavior**
4. **Browser and version**
5. **Screen size (if relevant)**
6. **Console errors (if any)**

## 🚀 Production Readiness

The application includes:
- ✅ Comprehensive error handling
- ✅ Loading states and skeletons
- ✅ Responsive design
- ✅ Role-based security
- ✅ API integration
- ✅ Form validation
- ✅ Data export functionality
- ✅ Analytics and reporting
- ✅ Cross-browser compatibility
- ✅ Automated testing suite

## 📞 Support

For testing support or issues:
1. Check console for errors
2. Verify backend is running
3. Clear browser cache/localStorage
4. Restart development servers
5. Check network connectivity

---

**Status**: ✅ READY FOR COMPREHENSIVE TESTING
**Last Updated**: July 26, 2025
**Version**: 1.0.0