# ManagersTab Component Test Guide

## Component Location
`/src/components/dashboard/ManagersTab.tsx`

## Key Features Implemented

### 1. Manager Creation with Password Display
- **Form Fields**: Email, First Name, Last Name, Property (optional), Password (optional)
- **Password Generation**: If no password provided, backend generates temporary password
- **Password Modal**: Shows temporary password after creation with:
  - Clear display of the generated password
  - Copy button with visual feedback
  - Warning that password won't be shown again
  - Instructions for first login password change

### 2. Multiple Property Assignments
- **Properties Display**: Shows all assigned properties as badges in the table
- **Assign Property Button**: Dedicated button to add properties to a manager
- **Property Assignment Dialog**: 
  - Shows currently assigned properties with remove option
  - Dropdown to select new properties
  - Filters out already assigned properties

### 3. Manager Table Updates
- **Columns**: Name, Email, Properties (multiple badges), Status, Actions
- **Active/Inactive Toggle**: Show/hide inactive managers
- **Search**: Works across name, email, and property names
- **Filter**: Filter by property or show unassigned managers

### 4. Enhanced Actions
- **Edit Button**: Edit manager details
- **Assign Property Button**: Manage property assignments
- **Deactivate/Reactivate**: Toggle manager status

## TypeScript Interfaces Updated

```typescript
interface Manager {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: 'manager';
  is_active: boolean;
  properties: Array<{
    id: string;
    name: string;
  }>;
  created_at: string;
}

interface CreateManagerResponse {
  success: boolean;
  data: {
    id: string;
    email: string;
    temporary_password: string;
    first_name: string;
    last_name: string;
    role: string;
    is_active: boolean;
  };
}
```

## API Endpoints Used
- `POST /api/hr/managers` - Create manager (returns temporary password)
- `GET /api/hr/managers` - List managers with properties
- `PUT /api/hr/managers/{id}` - Update manager
- `DELETE /api/hr/managers/{id}` - Deactivate manager
- `POST /api/hr/managers/{id}/reactivate` - Reactivate manager
- `POST /api/hr/managers/assign` - Assign property to manager
- `DELETE /api/hr/properties/{propertyId}/managers/{managerId}` - Remove property assignment

## Testing Steps

1. **Test Manager Creation**:
   - Click "Add Manager" button
   - Fill in required fields (First Name, Last Name, Email)
   - Leave password blank to test auto-generation
   - Submit form
   - Verify password modal appears with copyable password

2. **Test Property Assignment**:
   - Click the Building icon button on any manager
   - Select a property from dropdown
   - Click "Assign Property"
   - Verify property badge appears in table

3. **Test Multiple Properties**:
   - Assign multiple properties to same manager
   - Verify all properties show as badges
   - Test removing properties via the × button in assignment dialog

4. **Test Search and Filter**:
   - Search by manager name
   - Search by property name
   - Filter by specific property
   - Filter to show only unassigned managers

5. **Test Manager Status**:
   - Deactivate a manager
   - Toggle "Show Inactive Managers" 
   - Verify inactive manager appears grayed out
   - Test reactivation

## Success Criteria
✅ Manager creation shows temporary password in modal
✅ Password can be copied to clipboard
✅ Multiple properties can be assigned to each manager
✅ Properties display as badges in the table
✅ Property assignment/removal works correctly
✅ Search works across all fields including properties
✅ Active/inactive toggle functions properly
✅ All TypeScript types are properly defined
✅ No compilation errors