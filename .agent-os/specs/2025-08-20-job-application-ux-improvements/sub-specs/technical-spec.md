# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-20-job-application-ux-improvements/spec.md

## Technical Requirements

### Responsive Design Implementation

- **Breakpoint System**: Implement Tailwind CSS responsive utilities
  - Mobile: Default to 640px (sm:)
  - Tablet: 768px (md:)
  - Desktop: 1024px (lg:)
  - Wide: 1280px (xl:)

- **Mobile-First Grid Layouts**:
  ```css
  /* Personal Info Section */
  grid-cols-1 sm:grid-cols-2 md:grid-cols-3
  
  /* Contact Fields */
  grid-cols-1 md:grid-cols-2
  
  /* Address Fields */
  grid-cols-1 md:grid-cols-3
  ```

- **Touch Target Optimization**:
  - Minimum button height: `h-12` (48px)
  - Input field height: `h-11` (44px)
  - Clickable area padding: `p-3` minimum
  - Radio/Checkbox touch area: 44x44px with larger hit zones

### Visual Design System

- **Card-Based Layout**:
  - Section wrapper: `Card` component with `CardHeader` and `CardContent`
  - Spacing: `space-y-6` between sections, `space-y-4` within sections
  - Mobile padding: `p-4`, Desktop: `p-6`
  - Border radius: `rounded-lg`

- **Section Icons**:
  ```typescript
  const sectionIcons = {
    personalInfo: User,
    positionAvailability: Briefcase,
    employmentHistory: Building2,
    educationSkills: GraduationCap,
    additionalInfo: FileText,
    voluntaryIdentification: Users,
    reviewConsent: CheckCircle2
  }
  ```

- **Color System for States**:
  - Focus: `focus:border-blue-500 focus:ring-2 focus:ring-blue-200`
  - Error: `border-red-500 bg-red-50`
  - Success: `border-green-500` with checkmark icon
  - Disabled: `opacity-50 cursor-not-allowed`

### Form Validation System

- **Real-Time Validation Trigger**: On field blur event
- **Validation Display**:
  ```typescript
  interface FieldValidation {
    isValid: boolean
    isTouched: boolean
    errorMessage?: string
    showSuccess: boolean
  }
  ```

- **Error Message Component**:
  ```tsx
  <div className="mt-1 flex items-start space-x-1">
    <AlertCircle className="h-4 w-4 text-red-500 mt-0.5" />
    <p className="text-sm text-red-600">{errorMessage}</p>
  </div>
  ```

- **Success Indicator**:
  ```tsx
  {isValid && isTouched && (
    <CheckCircle2 className="absolute right-3 top-3 h-5 w-5 text-green-500" />
  )}
  ```

### Auto-Save Implementation

- **Save Trigger**: Every 30 seconds or on step navigation
- **Storage Structure**:
  ```typescript
  interface SavedApplication {
    applicationId: string // Generated UUID
    propertyId: string
    formData: ApplicationFormData
    currentStep: number
    stepCompletionStatus: Record<string, boolean>
    lastSaved: string // ISO timestamp
    version: number // For migration compatibility
  }
  ```

- **Recovery Flow**:
  1. Check localStorage for saved application
  2. If found, prompt user to continue or start fresh
  3. Display "Saved X minutes ago" indicator
  4. Provide application ID for recovery

### Enhanced Progress Tracking

- **Progress Bar Component**:
  ```tsx
  <div className="sticky top-0 z-10 bg-white shadow-sm p-4">
    <Progress value={calculateProgress()} className="h-3" />
    <div className="flex justify-between mt-2">
      {steps.map((step, index) => (
        <StepIndicator 
          key={step.id}
          step={step}
          index={index}
          isComplete={stepCompletionStatus[step.id]}
          isCurrent={currentStep === index}
        />
      ))}
    </div>
  </div>
  ```

### Mobile-Specific Optimizations

- **Sticky Navigation Bar**:
  ```tsx
  <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-4 md:relative md:border-0">
    <div className="flex justify-between">
      <Button>Previous</Button>
      <Button>Save</Button>
      <Button>Next</Button>
    </div>
  </div>
  ```

- **Mobile Select Enhancement**:
  - Use native select on mobile for better UX
  - Custom styled select on desktop
  - Detect via `window.matchMedia('(max-width: 768px)')`

- **Date Picker Mobile Optimization**:
  - Use native date input on mobile: `type="date"`
  - Custom date picker on desktop

### Smart Input Formatting

- **Phone Number Formatter**:
  ```typescript
  const formatPhone = (value: string): string => {
    const numbers = value.replace(/\D/g, '')
    if (numbers.length <= 3) return numbers
    if (numbers.length <= 6) return `(${numbers.slice(0, 3)}) ${numbers.slice(3)}`
    return `(${numbers.slice(0, 3)}) ${numbers.slice(3, 6)}-${numbers.slice(6, 10)}`
  }
  ```

- **SSN Formatter**:
  ```typescript
  const formatSSN = (value: string): string => {
    const numbers = value.replace(/\D/g, '')
    if (numbers.length <= 3) return numbers
    if (numbers.length <= 5) return `${numbers.slice(0, 3)}-${numbers.slice(3)}`
    return `${numbers.slice(0, 3)}-${numbers.slice(3, 5)}-${numbers.slice(5, 9)}`
  }
  ```

### Error Recovery System

- **Network Error Handling**:
  ```typescript
  const submitWithRetry = async (data: any, retries = 3) => {
    try {
      return await apiClient.post('/api/apply', data)
    } catch (error) {
      if (retries > 0 && isNetworkError(error)) {
        await delay(1000 * (4 - retries)) // Exponential backoff
        return submitWithRetry(data, retries - 1)
      }
      throw error
    }
  }
  ```

- **Auto-Scroll to Error**:
  ```typescript
  const scrollToError = (fieldId: string) => {
    const element = document.getElementById(fieldId)
    element?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    element?.focus()
    element?.classList.add('shake-animation')
  }
  ```

### Loading States

- **Skeleton Screens**:
  ```tsx
  {loading ? (
    <div className="space-y-4">
      <Skeleton className="h-12 w-full" />
      <Skeleton className="h-12 w-3/4" />
      <Skeleton className="h-32 w-full" />
    </div>
  ) : (
    <ActualContent />
  )}
  ```

### Accessibility Enhancements

- **ARIA Labels**: Add descriptive labels for screen readers
- **Focus Management**: Proper tab order and focus trapping in modals
- **Error Announcements**: Use `role="alert"` for error messages
- **Keyboard Navigation**: Support for Enter/Space on custom controls

## Performance Optimizations

- **Lazy Loading**: Load step components only when needed
- **Debounced Validation**: Debounce validation checks by 300ms
- **Memoization**: Use React.memo for step components
- **Virtual Scrolling**: For long lists in employment history

## Browser Compatibility

- Support modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Progressive enhancement for older browsers
- Polyfills for modern JavaScript features if needed