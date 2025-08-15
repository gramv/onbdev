# 🔍 QR Code Link Issue - Root Cause Analysis

## **PROBLEM IDENTIFIED**

The QR code links are not working because of a **PORT MISMATCH**:

### **Current Situation:**
- **QR Code Service** generates links with: `http://localhost:3000/apply/{propertyId}`
- **Frontend Server** actually runs on: `http://localhost:5174/apply/{propertyId}`
- **Result**: QR codes point to wrong port, links don't work

## **ROOT CAUSE**

1. **Vite Default Port Change**: Vite now defaults to port 5174 instead of 3000
2. **QR Service Hardcoded Port**: QR service still uses old port 3000
3. **No Port Synchronization**: Backend and frontend ports not coordinated

## **IMMEDIATE FIX**

### **Option 1: Update QR Service (DONE)**
```python
# In hotel-onboarding-backend/app/qr_service.py
def __init__(self):
    self.base_url = "http://localhost:5174"  # Updated to correct port
```

### **Option 2: Force Frontend to Port 3000**
```json
// In hotel-onboarding-frontend/package.json
"scripts": {
    "dev": "vite --port 3000"
}
```

## **SYSTEM PERFORMANCE ISSUE**

The application is slow because:
1. **Multiple Server Instances**: Multiple npm/python processes running
2. **Resource Contention**: System overloaded with duplicate processes
3. **Port Conflicts**: Processes competing for same ports

## **CLEAN SOLUTION**

### **Step 1: Clean Environment**
```bash
# Kill all processes
pkill -f "npm|node|python|uvicorn"

# Clear ports
lsof -ti:3000,5174,8000 | xargs kill -9
```

### **Step 2: Start Single Backend**
```bash
cd hotel-onboarding-backend
python3 -m app.main_enhanced
```

### **Step 3: Start Single Frontend on Port 3000**
```bash
cd hotel-onboarding-frontend
npm run dev -- --port 3000
```

## **VERIFICATION STEPS**

1. **Backend Health**: `curl http://127.0.0.1:8000/health`
2. **Frontend Access**: `curl http://localhost:3000`
3. **QR Code Test**: `curl http://localhost:3000/apply/prop_test_001`
4. **Generate QR**: Test QR generation endpoint

## **PERMANENT FIX**

### **Environment Configuration**
```bash
# .env file for backend
FRONTEND_URL=http://localhost:3000

# .env file for frontend  
VITE_BACKEND_URL=http://localhost:8000
```

### **Dynamic Port Configuration**
```python
# In qr_service.py
import os
self.base_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
```

## **TESTING WORKFLOW**

1. **Generate QR Code**: Call backend QR endpoint
2. **Scan QR Code**: Should point to `http://localhost:3000/apply/{propertyId}`
3. **Load Application**: Frontend should load job application form
4. **Verify Property**: Form should show correct property information

## **SYSTEM RULES ADDITION**

**NEW RULE**: Never start multiple server instances. Always:
1. Check if servers are running first
2. Kill existing processes before starting new ones
3. Use consistent ports (3000 for frontend, 8000 for backend)
4. Verify server health before proceeding with tests

---

**NEXT ACTION**: Clean restart with correct ports and test QR functionality once.