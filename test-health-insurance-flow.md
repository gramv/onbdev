# Health Insurance Step - Data Flow Test

## Changes Made

### 1. HealthInsuranceStep Component Updates

#### Personal Information Display
- Added state to track `personalInfo` from PersonalInfoStep
- Loads personal data from session storage (`onboarding_personal-info_data`)
- Falls back to `employee` prop if session data not available
- Displays readonly employee information at top of form:
  - Full Name (firstName, middleInitial, lastName)
  - SSN (masked as ***-**-XXXX)
  - Date of Birth
  - Gender
  - Full Address
  - Phone and Email

#### Section 125 Pre-Tax Acknowledgment
- Added new state `section125Acknowledged` to track acceptance
- Added Section 125 acknowledgment section before signature with:
  - Full 7-point acknowledgment text about pre-tax premium rules
  - Required checkbox to agree to terms
  - Prevents signing without acknowledgment

#### Data Flow Improvements
- Personal info now passed to backend with health insurance data
- Section 125 acknowledgment status included in saved data
- All data properly stored in session storage

### 2. HealthInsuranceForm Component Updates

#### Dependent Enhancements
- Added `gender` field with M/F radio buttons for each dependent
- Added `coverageType` object with checkboxes for:
  - Medical coverage
  - Dental coverage  
  - Vision coverage
- Updated `Dependent` interface to include new fields
- Modified `updateDependent` function to handle any value type (not just strings)

#### Props Updates
- Added `personalInfo` prop to receive employee data
- Component now accepts personal info from parent

#### Translation Updates
- Added missing English translations:
  - `select_gender`: "Select Gender"
  - `coverage_type`: "Coverage Type"
- Added complete Spanish translations for all dependent fields

### 3. Data Structure

The complete data structure now includes:

```typescript
{
  // Form data
  formData: {
    medicalPlan: string,
    dependents: [{
      firstName: string,
      lastName: string,
      gender: 'M' | 'F' | '',
      coverageType: {
        medical: boolean,
        dental: boolean,
        vision: boolean
      }
      // ... other fields
    }]
    // ... other insurance fields
  },
  
  // Personal info from PersonalInfoStep
  personalInfo: {
    firstName: string,
    lastName: string,
    ssn: string,
    dateOfBirth: string,
    address: string,
    // ... other personal fields
  },
  
  // Compliance
  section125Acknowledged: boolean,
  
  // Signature
  isSigned: boolean,
  signatureData: object
}
```

## Testing Steps

1. **Start Fresh Session**
   - Clear browser session storage
   - Navigate to `/onboard?token=test-token`

2. **Complete PersonalInfoStep**
   - Fill in all personal information
   - Save and continue to next steps

3. **Navigate to HealthInsuranceStep**
   - Verify personal info displays at top (readonly)
   - SSN should be masked
   - All fields should be populated from PersonalInfoStep

4. **Test Dependent Fields**
   - Add a dependent
   - Verify gender dropdown appears
   - Verify coverage type checkboxes work
   - Save and reload to verify data persists

5. **Test Section 125 Acknowledgment**
   - Fill in insurance selections
   - Click review
   - Try to sign without checking Section 125 acknowledgment
   - Should see alert preventing signature
   - Check acknowledgment and sign
   - Verify completion

## Backend Integration

The backend will receive:
- Complete personal info for PDF population
- All dependent details including gender and coverage types
- Section 125 acknowledgment status
- This ensures PDFs can be properly generated with all employee information

## Key Files Modified

1. `/src/pages/onboarding/HealthInsuranceStep.tsx`
   - Added personal info display
   - Added Section 125 acknowledgment
   - Enhanced data flow

2. `/src/components/HealthInsuranceForm.tsx`
   - Added dependent gender and coverage type fields
   - Updated translations
   - Enhanced data handling

## Notes

- Personal information flows correctly from PersonalInfoStep to HealthInsuranceStep
- Data is stored in session storage for persistence
- Backend receives all necessary data for PDF generation
- Federal compliance maintained with Section 125 acknowledgment
- Bilingual support fully implemented