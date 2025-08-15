# Backend Endpoint Fixes Required

## Issues Identified from Error Logs

### 1. ❌ Missing `/manager/property` endpoint (404 error)
**Error**: `127.0.0.1:8000/manager/property:1 Failed to load resource: the server responded with a status of 404 (Not Found)`

**Fix Applied**: Added new endpoint in `main_enhanced.py`:
```python
@app.get("/manager/property")
async def get_manager_property(current_user: User = Depends(require_manager_role)):
    """Get manager's assigned property details"""
    if not current_user.property_id:
        raise HTTPException(status_code=404, detail="Manager not assigned to any property")
    
    property_obj = database["properties"].get(current_user.property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return {
        "id": property_obj.id,
        "name": property_obj.name,
        "address": property_obj.address,
        "city": property_obj.city,
        "state": property_obj.state,
        "zip_code": property_obj.zip_code,
        "phone": property_obj.phone,
        "qr_code_url": property_obj.qr_code_url,
        "is_active": property_obj.is_active,
        "created_at": property_obj.created_at.isoformat(),
        "manager_ids": property_obj.manager_ids
    }
```

### 2. ❌ Missing `/applications/{id}/reject` endpoint (404 error)
**Error**: `127.0.0.1:8000/applications/app_test_001/reject:1 Failed to load resource: the server responded with a status of 404 (Not Found)`

**Fix Applied**: Added new manager rejection endpoint:
```python
@app.post("/applications/{application_id}/reject")
async def reject_application_manager(
    application_id: str,
    rejection_reason: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Reject application and move to talent pool (Manager only)"""
    # ... implementation moves rejected applications to talent pool
    return {
        "success": True,
        "message": "Application rejected and moved to talent pool for future opportunities",
        "status": "talent_pool",
        "talent_pool_date": application.talent_pool_date.isoformat()
    }
```

### 3. ❌ Application approval failing (422 error)
**Error**: `127.0.0.1:8000/applications/app_test_001/approve 422 (Unprocessable Content)`

**Likely Cause**: Missing required form fields in approval request.

## Frontend Issues Fixed

### 1. ✅ Manager Dashboard Layout
**Fixed**: Changed from `/hr/properties` to `/manager/property`:
```typescript
// OLD CODE:
const response = await axios.get('http://127.0.0.1:8000/hr/properties', axiosConfig)
const properties = Array.isArray(response.data) ? response.data : []
const userProperty = properties.find((p: Property) => p.id === user?.property_id)

// NEW CODE:
const response = await axios.get('http://127.0.0.1:8000/manager/property', axiosConfig)
const userProperty = response.data
```

### 2. ✅ Application Rejection Workflow
**Updated**: Applications now go to talent pool instead of being rejected:
- Status changes from `PENDING` → `TALENT_POOL` (not `REJECTED`)
- Candidates receive talent pool notification emails
- Applications can be reactivated from talent pool

## Backend Restart Required

**CRITICAL**: The backend must be restarted for these changes to take effect.

Current test results show endpoints are still missing:
```
🧪 Testing /manager/property
   Status: 404
   ❌ Error: {"detail":"Not Found"}

🧪 Testing /applications/{id}/reject
   Status: 404
   ❌ Rejection failed: {"detail":"Not Found"}
```

## Expected Behavior After Restart

### Manager Property Endpoint
```bash
GET /manager/property
Authorization: Bearer <manager_token>

Response:
{
  "id": "prop_test_001",
  "name": "Grand Plaza Hotel",
  "address": "123 Main Street",
  "city": "Downtown",
  "state": "CA",
  "qr_code_url": "data:image/png;base64,..."
}
```

### Manager Rejection Endpoint
```bash
POST /applications/{application_id}/reject
Authorization: Bearer <manager_token>
Content-Type: application/x-www-form-urlencoded

rejection_reason=Not a good fit for current position

Response:
{
  "success": true,
  "message": "Application rejected and moved to talent pool for future opportunities",
  "status": "talent_pool",
  "talent_pool_date": "2025-07-28T06:02:20.518552+00:00"
}
```

## Testing Commands

After backend restart, run these tests:

```bash
# Test manager endpoints
python3 test_endpoints.py

# Test complete rejection workflow
python3 test_rejection_to_talent_pool.py

# Test manager QR access
python3 test_manager_qr_access.py
```

## Summary of Changes Made

1. ✅ **Added `/manager/property` endpoint** - Returns manager's assigned property details
2. ✅ **Added `/applications/{id}/reject` endpoint** - Manager rejection that moves to talent pool
3. ✅ **Updated rejection logic** - Applications go to talent pool instead of rejected status
4. ✅ **Fixed frontend manager dashboard** - Uses correct manager endpoint
5. ✅ **Implemented talent pool workflow** - Rejected candidates stay in system for future opportunities

## Next Steps

1. **Restart Backend Server** - Apply all endpoint changes
2. **Test All Endpoints** - Verify manager functionality works
3. **Update Frontend** - Ensure UI reflects talent pool status correctly
4. **Verify Complete Workflow** - Test QR → Application → Review → Talent Pool flow