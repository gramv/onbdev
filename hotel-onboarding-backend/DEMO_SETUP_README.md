# Demo Test Data Setup

This document explains how to set up comprehensive demo data for the QR Job Application Workflow.

## Quick Start

1. **Start the backend server:**
   ```bash
   cd hotel-onboarding-backend
   python -m uvicorn app.main_enhanced:app --reload
   ```

2. **Run the demo setup script:**
   ```bash
   python demo_test_data_setup.py
   ```

3. **Start the frontend (optional):**
   ```bash
   cd hotel-onboarding-frontend
   npm run dev
   ```

## What Gets Created

### Properties (4)
- **Grand Plaza Hotel** - Downtown, CA
- **Seaside Resort & Spa** - Coastal City, FL  
- **Mountain View Lodge** - Mountain Town, CO
- **City Center Business Hotel** - Metro City, NY

Each property includes:
- QR code for job applications
- Assigned manager
- Application URL for public access

### Applications (24 total)
For each property, the following applications are created:

**Pending Applications (3 per property):**
- John Doe - Front Desk Agent
- Maria Garcia - Housekeeper  
- Sarah Johnson - Server

**Talent Pool Candidates (2 per property):**
- Michael Brown - Front Desk Agent
- Emily Davis - Front Desk Agent

**Approved Applications (1 per property):**
- Robert Wilson - Maintenance Technician

### User Accounts

**HR Account:**
- Email: `hr@hoteltest.com`
- Password: `admin123`
- Access: All properties and applications

**Manager Accounts:**
- `manager1@hoteltest.com` - Grand Plaza Hotel (Mike Wilson)
- `manager2@hoteltest.com` - Seaside Resort & Spa (Sarah Davis)
- `manager3@hoteltest.com` - Mountain View Lodge (John Smith)
- `manager4@hoteltest.com` - City Center Business Hotel (Lisa Brown)
- Password: `manager123` (all managers)
- Access: Property-specific applications only

## Demo Scenarios

### 1. QR Code Generation
- All properties have QR codes generated
- QR codes link to public application forms
- Managers can regenerate QR codes for their properties

### 2. Public Application Submission
- Visit any application URL (shown in setup output)
- Fill out job application form
- No authentication required
- Applications appear immediately in manager dashboard

### 3. Application Review Workflow
- Login as manager to see property-specific applications
- Applications grouped by department and position
- View applicant details and qualifications

### 4. Approval Process
- Managers can approve applications with job offer details
- Approved applications create employee records
- Other applications for same position move to talent pool

### 5. Talent Pool Management
- Multiple candidates for same position automatically go to talent pool
- HR can view all talent pool candidates across properties
- Candidates can be contacted for future openings

### 6. Multi-Property Management
- HR sees all properties and applications
- Managers only see their assigned property
- Different properties have different managers

## API Endpoints for Testing

### Public Endpoints (No Auth Required)
```bash
# Get property info for application form
GET /properties/{property_id}/info

# Submit job application
POST /apply/{property_id}
```

### Manager Endpoints (Manager Token Required)
```bash
# Get applications for manager's property
GET /applications

# Approve application
POST /applications/{application_id}/approve
```

### HR Endpoints (HR Token Required)
```bash
# Get all properties
GET /hr/properties

# Get all applications
GET /hr/applications

# Generate QR code for property
POST /hr/properties/{property_id}/qr-code
```

## Troubleshooting

### Backend Not Running
If you get connection errors, make sure the backend is running:
```bash
cd hotel-onboarding-backend
python -m uvicorn app.main_enhanced:app --reload
```

### Script Fails
The script handles most common issues:
- Existing accounts are reused
- Duplicate data is avoided
- Validation errors are reported

### Reset Demo Data
To start fresh, restart the backend server (data is in-memory).

## Testing the Complete Workflow

1. **As HR:**
   - Login to see all properties
   - View QR codes and application URLs
   - See applications across all properties

2. **As Manager:**
   - Login to see property-specific view
   - Review pending applications
   - Approve candidates and see talent pool formation

3. **As Applicant:**
   - Visit application URL from QR code
   - Fill out and submit application
   - See confirmation message

4. **End-to-End:**
   - Submit application → Manager reviews → Approve/Reject → Talent pool management

## Demo Data Summary

After running the setup, you'll have:
- ✅ 4 Properties with QR codes
- ✅ 5 User accounts (1 HR + 4 Managers)  
- ✅ 24 Applications in various states
- ✅ 8 Talent pool candidates
- ✅ Working end-to-end workflow
- ✅ All demo scenarios ready

The setup provides a comprehensive demonstration of the QR job application workflow with realistic data across multiple properties and application states.