# Secure Property Creation Setup

## The Problem
Properties cannot be created because Supabase Row Level Security (RLS) is blocking the operations, and the service key is not configured.

## Security Analysis of Current Approaches

### ❌ INSECURE: Using SECURITY DEFINER RPC Function
```sql
CREATE FUNCTION create_property_bypass_rls(property_data jsonb)
SECURITY DEFINER -- Runs with owner privileges, bypasses ALL security
```
**Why it's insecure:**
- Any authenticated user can call this function
- Bypasses all RLS policies completely
- No role validation at database level
- Could be exploited if someone gets a valid JWT token

### ❌ INSECURE: Disabling RLS
```sql
ALTER TABLE properties DISABLE ROW LEVEL SECURITY;
```
**Why it's insecure:**
- Makes the entire table publicly accessible
- Anyone with database access can modify any property
- No audit trail or access control

## ✅ SECURE Solution Options

### Option 1: Configure Service Key (RECOMMENDED)
1. Get your service key from Supabase Dashboard:
   - Go to Settings → API
   - Copy the `service_role` key (NOT the anon key)
   
2. Add to your `.env` file:
   ```
   SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

3. The backend will automatically use this for admin operations

**Why it's secure:**
- Service key never goes to frontend
- Backend validates user is HR before using it
- Maintains audit trail
- RLS still protects against other attacks

### Option 2: Create Proper RLS Policies
Add this to your Supabase SQL editor:

```sql
-- Allow HR users to do everything with properties
CREATE POLICY "HR full access to properties" ON properties
FOR ALL 
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'hr'
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1 FROM users
        WHERE users.id = auth.uid()
        AND users.role = 'hr'
    )
);

-- Allow managers to read their assigned properties
CREATE POLICY "Managers read assigned properties" ON properties
FOR SELECT
TO authenticated
USING (
    EXISTS (
        SELECT 1 FROM property_managers pm
        JOIN users u ON u.id = pm.manager_id
        WHERE pm.property_id = properties.id
        AND u.id = auth.uid()
        AND u.role = 'manager'
    )
);
```

**Why it's secure:**
- Uses Supabase's built-in auth system
- Role-based access control at database level
- No bypass mechanisms needed
- Audit trail maintained

### Option 3: Temporary In-Memory Storage (Development Only)
For development/testing without Supabase setup:

```python
# In supabase_service_enhanced.py
class InMemoryPropertyStore:
    _properties = {}
    
    @classmethod
    def create(cls, property_data):
        cls._properties[property_data['id']] = property_data
        return property_data
    
    @classmethod
    def get_all(cls):
        return list(cls._properties.values())
```

**Use only for development** - not for production!

## Current Backend Security Measures

The backend already has these security layers:
1. `require_hr_role` decorator ensures only HR can create properties
2. JWT token validation
3. Proper error handling
4. Input validation with Pydantic

## Recommended Action

1. **For Production**: Use Option 1 (Service Key) or Option 2 (RLS Policies)
2. **For Development**: Use Option 3 temporarily
3. **Delete the RPC function** if you created it - it's not secure

## To Test Your Setup

After configuring the service key:
```bash
# Restart the backend
cd hotel-onboarding-backend
python3 -m uvicorn app.main_enhanced:app --reload

# Test property creation
curl -X POST http://127.0.0.1:8000/hr/properties \
  -H "Authorization: Bearer YOUR_HR_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Test+Hotel&address=123+Main&city=NYC&state=NY&zip_code=10001&phone=555-1234"
```

## Security Best Practices

1. **Never expose service keys** to frontend or commit them to git
2. **Always validate roles** in the backend before database operations
3. **Use RLS policies** as additional defense layer
4. **Log all admin operations** for audit trail
5. **Rotate keys regularly** in production
6. **Use environment-specific keys** (dev/staging/prod)