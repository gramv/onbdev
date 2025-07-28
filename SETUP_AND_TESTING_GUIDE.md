# Hotel Onboarding System - Setup and Testing Guide

This guide provides step-by-step instructions for setting up and running the Hotel Onboarding System in new environments.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.12+ (required for backend)
- **Node.js**: 18+ (required for frontend)
- **npm**: 9+ (comes with Node.js)
- **Poetry**: Latest version (for Python dependency management)

### Installation Commands
```bash
# Install Python (macOS with Homebrew)
brew install python@3.12

# Install Node.js (macOS with Homebrew)
brew install node

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Verify installations
python3 --version  # Should be 3.12+
node --version     # Should be 18+
npm --version      # Should be 9+
poetry --version   # Should be latest
```

## 🔧 Backend Setup

### 1. Navigate to Backend Directory
```bash
cd hotel-onboarding-backend
```

### 2. Install Dependencies
```bash
# Using Poetry (recommended)
poetry install

# OR using pip with virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # If requirements.txt exists
```

### 3. Environment Configuration
The `.env` file is already configured with default values:

```env
# Groq API Configuration
GROQ_API_KEY=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
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=4000
GROQ_TEMPERATURE=0.1

# JWT Configuration
JWT_SECRET_KEY=hotel-onboarding-super-secret-key-2025
JWT_ACCESS_TOKEN_EXPIRE_HOURS=72

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Development Settings
DEBUG=true
```

**⚠️ Important**: For production, change the `JWT_SECRET_KEY` to a secure random string.

### 4. Install Additional Dependencies (if needed)
```bash
# If you encounter bcrypt errors
pip install bcrypt

# If you encounter other missing dependencies
poetry add <package-name>
# OR
pip install <package-name>
```

### 5. Start Backend Server
```bash
# Using Poetry
poetry run uvicorn app.main_enhanced:app --reload --port 8000

# OR using virtual environment
source venv/bin/activate
uvicorn app.main_enhanced:app --reload --port 8000

# OR using Python directly
python -m uvicorn app.main_enhanced:app --reload --port 8000
```

### 6. Verify Backend is Running
```bash
# Test health endpoint
curl http://localhost:8000/

# Should return FastAPI welcome message
```

## 🎨 Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd hotel-onboarding-frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start Frontend Development Server
```bash
npm run dev
```

### 4. Verify Frontend is Running
- Open browser to `http://localhost:5173`
- You should see the login page

## 🧪 Test Accounts and Data

The system automatically initializes with test data when the backend starts. Here are the pre-configured accounts:

### HR Account
- **Email**: `hr@hoteltest.com`
- **Password**: `admin123`
- **Role**: HR Administrator
- **Access**: Full system access across all properties

### Manager Account
- **Email**: `manager@hoteltest.com`
- **Password**: `manager123`
- **Role**: Property Manager
- **Access**: Limited to assigned property only

### Test Property
- **Name**: Grand Plaza Hotel
- **Address**: 123 Main Street, Downtown, CA 90210
- **Manager**: Mike Wilson (manager@hoteltest.com)

### Test Employees
The system includes 5 test employees with different statuses:
1. **Alice Smith** - Front Desk Agent (Active, Onboarding Approved)
2. **Bob Johnson** - Housekeeper (Active, Onboarding In Progress)
3. **Carol Davis** - Server (Active, Employee Completed)
4. **David Wilson** - Maintenance Technician (On Leave, Approved)
5. **Emma Brown** - Night Auditor (Active, Not Started)

## 🔐 Authentication and Tokens

### Login Process
1. Navigate to `http://localhost:5173`
2. Use test credentials above
3. System returns JWT token valid for 72 hours
4. Token is automatically stored in browser context

### Manual Token Testing
```bash
# Login and get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "hr@hoteltest.com", "password": "admin123"}'

# Use token in subsequent requests
curl -X GET "http://localhost:8000/api/employees" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Token Structure
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "hr_test_001",
    "email": "hr@hoteltest.com",
    "role": "hr",
    "first_name": "Sarah",
    "last_name": "Johnson"
  },
  "expires_at": "2025-07-27T16:28:59.301867+00:00"
}
```

## 🚀 Quick Start Commands

### Start Both Servers (Recommended)
```bash
# Terminal 1 - Backend
cd hotel-onboarding-backend
poetry run uvicorn app.main_enhanced:app --reload --port 8000

# Terminal 2 - Frontend
cd hotel-onboarding-frontend
npm run dev
```

### One-Line Setup (if dependencies are installed)
```bash
# Start backend in background
cd hotel-onboarding-backend && poetry run uvicorn app.main_enhanced:app --reload --port 8000 &

# Start frontend
cd hotel-onboarding-frontend && npm run dev
```

## 🧪 API Testing

### Key Endpoints
```bash
# Authentication
POST /auth/login
POST /auth/logout

# HR Dashboard
GET /hr/dashboard-stats
GET /api/properties
GET /api/managers
GET /api/employees
GET /api/applications

# Manager Dashboard
GET /manager/dashboard-stats
GET /manager/applications
GET /manager/employees

# Employee Management
GET /api/employees
GET /api/employees/{id}
GET /api/employees/filters/options
PUT /api/employees/{id}/status
```

### Sample API Calls
```bash
# Get all employees (HR)
curl -X GET "http://localhost:8000/api/employees" \
  -H "Authorization: Bearer YOUR_HR_TOKEN"

# Get employee details
curl -X GET "http://localhost:8000/api/employees/emp_test_001" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get filter options
curl -X GET "http://localhost:8000/api/employees/filters/options" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🐛 Common Issues and Solutions

### Backend Issues

#### 1. bcrypt Missing Error
```bash
# Error: bcrypt: no backends available
# Solution:
pip install bcrypt
# OR
poetry add bcrypt
```

#### 2. Port Already in Use
```bash
# Error: Address already in use
# Solution:
lsof -ti:8000 | xargs kill -9
# OR use different port
uvicorn app.main_enhanced:app --reload --port 8001
```

#### 3. Module Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Ensure you're in the right directory and virtual environment
cd hotel-onboarding-backend
source venv/bin/activate  # If using venv
poetry shell              # If using poetry
```

### Frontend Issues

#### 1. Node Modules Issues
```bash
# Solution: Clean install
rm -rf node_modules package-lock.json
npm install
```

#### 2. TypeScript Errors
```bash
# Ignore TypeScript errors during development
npm run dev -- --host
```

#### 3. CORS Issues
```bash
# Backend already configured for CORS
# If issues persist, check backend logs
```

## 📊 Testing Features

### HR Dashboard Testing
1. Login as HR (`hr@hoteltest.com` / `admin123`)
2. Navigate to different tabs:
   - **Properties**: View and manage properties
   - **Managers**: View and assign managers
   - **Employees**: Search, filter, and view employee details
   - **Applications**: Review job applications

### Manager Dashboard Testing
1. Login as Manager (`manager@hoteltest.com` / `manager123`)
2. View property-specific data:
   - Applications for assigned property only
   - Employees for assigned property only
   - Limited access compared to HR

### Employee Directory Testing
1. Login as HR
2. Go to Employees tab
3. Test features:
   - Search by name, email, department
   - Filter by department and status
   - View employee details in modal
   - Clear filters functionality

## 🔄 Development Workflow

### Making Changes
1. **Backend Changes**: Server auto-reloads with `--reload` flag
2. **Frontend Changes**: Vite auto-reloads in development mode
3. **Database Changes**: Restart backend to reinitialize test data

### Adding New Test Data
Edit the `initialize_test_data()` function in `hotel-onboarding-backend/app/main_enhanced.py`

### Environment Variables
- Backend: Edit `.env` file in `hotel-onboarding-backend/`
- Frontend: Environment variables can be added to `.env.local`

## 📝 Logs and Debugging

### Backend Logs
- Server logs appear in terminal where uvicorn is running
- API request logs show in real-time
- Error stack traces displayed for debugging

### Frontend Logs
- Browser console shows React errors and warnings
- Network tab shows API requests and responses
- Use React Developer Tools for component debugging

## 🚀 Production Deployment

### Backend Production
```bash
# Install production dependencies
poetry install --no-dev

# Run with production server
gunicorn app.main_enhanced:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Production
```bash
# Build for production
npm run build

# Serve built files
npm run preview
```

### Environment Security
- Change `JWT_SECRET_KEY` to secure random string
- Use environment-specific API keys
- Enable HTTPS in production
- Configure proper CORS origins

---

## 📞 Support

If you encounter issues not covered in this guide:
1. Check the terminal logs for error messages
2. Verify all dependencies are installed correctly
3. Ensure both servers are running on correct ports
4. Test API endpoints manually with curl
5. Check browser console for frontend errors

This guide should help you get the system running quickly in any new environment!