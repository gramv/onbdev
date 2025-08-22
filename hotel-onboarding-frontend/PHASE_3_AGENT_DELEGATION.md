# Phase 3: Job Application Form Redesign - Agent Delegation Plan

## Overview
This document contains specific instructions for 7 frontend-component-fixer agents to work in parallel on redesigning the job application form steps. Each agent has an independent scope and can work simultaneously.

## Design System Resources
All agents should use:
- **Design System**: `/src/styles/design-system.ts`
- **Animations**: `/src/styles/animations.ts`
- **Form Styles**: `/src/styles/form-styles.ts`
- **Enhanced Components**: `/src/components/ui/enhanced/`
  - EnhancedInput
  - EnhancedSelect
  - EnhancedTextarea
  - StepCard
  - ProgressIndicator
  - FileUploadZone

## Common Requirements for All Agents
1. Use the enhanced components from Phase 2
2. Implement professional UX comparable to LinkedIn/Indeed
3. Ensure mobile responsiveness (test at 375px, 768px, 1024px)
4. Maintain federal compliance requirements
5. Support bilingual functionality (English/Spanish)
6. Add smooth animations and micro-interactions
7. Implement proper validation with clear error messages
8. Use the design system color palette and spacing
9. Ensure WCAG 2.1 AA accessibility compliance
10. Test thoroughly before marking complete

---

## Agent 1: Personal Information Step

### File to Redesign
`/src/components/job-application/PersonalInformationStep.tsx`

### Specific Requirements
1. **Layout**:
   - Use StepCard component with User icon
   - Group fields logically: Name, Contact, Address
   - Implement 2-column layout on desktop, single column on mobile

2. **Fields to Enhance**:
   - First Name, Middle Name, Last Name (use EnhancedInput)
   - Email (with email validation)
   - Phone (with phone mask formatting)
   - Address fields (Street, City, State ZIP)
   - Date of Birth (add date picker if not present)
   - SSN (with secure input and mask XXX-XX-XXXX)

3. **UX Improvements**:
   - Add floating labels
   - Implement auto-save every 30 seconds
   - Show completion percentage
   - Add helpful tooltips for sensitive fields (SSN)
   - Implement address auto-complete if possible

4. **Validation**:
   - Real-time validation with debouncing
   - Clear error messages below fields
   - Success checkmarks for valid fields
   - Prevent submission until all required fields valid

---

## Agent 2: Position & Availability Step

### File to Redesign
`/src/components/job-application/PositionAvailabilityStep.tsx`

### Specific Requirements
1. **Layout**:
   - Use StepCard with Briefcase icon
   - Create visual hierarchy with sections
   - Department → Position cascade selection

2. **Fields to Enhance**:
   - Department selection (EnhancedSelect with icons)
   - Position selection (dynamically filtered by department)
   - Employment type (full-time/part-time with visual badges)
   - Start date (calendar picker with minimum today)
   - Availability grid for days/shifts
   - Weekend/Holiday availability toggle switches
   - Salary expectations (optional, with range slider)

3. **UX Improvements**:
   - Visual availability scheduler (morning/afternoon/evening grid)
   - Show position descriptions on hover/click
   - Indicate which positions are urgently needed
   - Add "flexible" option for availability
   - Previous employment at property (yes/no toggle)

4. **Validation**:
   - Ensure at least some availability selected
   - Start date must be future date
   - Required fields clearly marked

---

## Agent 3: Employment History Step

### File to Redesign
`/src/components/job-application/EmploymentHistoryStep.tsx`

### Specific Requirements
1. **Layout**:
   - Use StepCard with Building icon
   - Dynamic form for multiple employers
   - Timeline visualization of work history

2. **Fields to Enhance**:
   - Employer name and location
   - Position title
   - Employment dates (with date range picker)
   - Responsibilities (rich text area)
   - Reason for leaving (select with "Other" option)
   - May we contact? (toggle with conditional fields)
   - Supervisor name and phone

3. **UX Improvements**:
   - "Add Another Employer" button with smooth animation
   - Calculate and display total years of experience
   - Auto-calculate employment duration
   - Collapsible employer cards after completion
   - Quick templates for common hospitality roles
   - Employment gap detection and explanation field

4. **Validation**:
   - Date logic (end date after start date)
   - At least one employer required
   - Phone number format validation
   - No overlapping employment dates

---

## Agent 4: Education & Skills Step

### File to Redesign
`/src/components/job-application/EducationSkillsStep.tsx`

### Specific Requirements
1. **Layout**:
   - Use StepCard with GraduationCap icon
   - Two sections: Education and Skills
   - Skills as tag selection interface

2. **Fields to Enhance**:
   - Education level (EnhancedSelect)
   - School/Institution name
   - Graduation year
   - Major/Field of study
   - Certifications (multi-add with badges)
   - Languages spoken (multi-select with proficiency)
   - Technical skills (tag cloud selection)
   - Hospitality skills (pre-defined options)

3. **UX Improvements**:
   - Skill suggestions based on position selected
   - Visual skill badges with categories
   - Certification upload option
   - Language proficiency slider (Basic/Conversational/Fluent)
   - "Add Education" for multiple degrees
   - Auto-complete for common schools/certifications

4. **Validation**:
   - Graduation year logic
   - At least education level required
   - Skills relevant to position

---

## Agent 5: Additional Information Step

### File to Redesign
`/src/components/job-application/AdditionalInformationStep.tsx`

### Specific Requirements
1. **Layout**:
   - Use StepCard with Info icon
   - Clear sections for References and Additional Questions
   - Professional reference card design

2. **Fields to Enhance**:
   - References (3 minimum):
     - Name, Title, Company
     - Phone and Email
     - Relationship and Years Known
   - Transportation availability
   - Criminal background disclosure
   - Additional comments (optional)
   - How did you hear about us?

3. **UX Improvements**:
   - Reference cards with contact badges
   - Character counter for text areas
   - Conditional fields based on answers
   - Privacy notice for background check
   - Clear explanation of why information is needed
   - Quick-add from LinkedIn connection (if feasible)

4. **Validation**:
   - Valid email and phone for references
   - Minimum 2 professional references
   - Relationship cannot be family
   - Required disclosure questions answered

---

## Agent 6: Review & Consent Step

### File to Redesign
`/src/components/job-application/ReviewConsentStep.tsx`

### Specific Requirements
1. **Layout**:
   - Use StepCard with CheckCircle icon
   - Comprehensive review in accordion sections
   - Clear consent checkboxes at bottom

2. **Sections to Display**:
   - Personal Information summary
   - Position & Availability summary
   - Employment History timeline
   - Education & Skills badges
   - References list
   - Edit buttons for each section

3. **UX Improvements**:
   - Printable view option
   - PDF preview of application
   - Progress completion badges
   - Missing information alerts
   - Quick-edit inline capability
   - One-click navigation to any section

4. **Consent Items**:
   - Background check authorization
   - Reference check permission
   - Information accuracy attestation
   - At-will employment acknowledgment
   - Electronic signature with timestamp

---

## Agent 7: Voluntary Self-Identification Step

### File to Redesign
`/src/components/job-application/VoluntarySelfIdentificationStep.tsx`

### Specific Requirements
1. **Layout**:
   - Use StepCard with Shield icon
   - Clear federal compliance notices
   - Optional section clearly marked

2. **Fields to Enhance**:
   - Veteran status (with categories)
   - Disability status (with privacy notice)
   - Race/Ethnicity (federal categories)
   - Gender (with inclusive options)
   - Clear "Prefer not to answer" for all

3. **UX Improvements**:
   - Explanation of why collected (EEOC compliance)
   - Privacy and confidentiality notices
   - Links to more information
   - Clear indication this won't affect application
   - Professional, respectful language
   - Collapsible detailed explanations

4. **Compliance Requirements**:
   - Follow exact federal EEOC language
   - Include required legal notices
   - Voluntary nature prominently displayed
   - Secure handling indication
   - Accessibility compliant

---

## Testing Requirements for All Agents

### Desktop Testing
- Chrome, Firefox, Safari latest versions
- 1920x1080, 1440x900, 1366x768 resolutions
- Keyboard navigation
- Screen reader compatibility

### Mobile Testing
- iPhone 12/13/14 (375px width)
- iPad (768px width)
- Android devices (360px width)
- Touch interactions
- Portrait and landscape

### Validation Testing
- All required fields
- Field format validation
- Edge cases (long names, special characters)
- Error recovery
- Browser autofill compatibility

### Performance Testing
- Page load under 2 seconds
- Smooth animations (60fps)
- No layout shifts
- Optimized images
- Lazy loading where appropriate

---

## Coordination Notes

### Parallel Execution
All 7 agents can work simultaneously as each step is independent. However, maintain consistency in:
- Using the same design system
- Similar animation patterns
- Consistent validation messaging
- Uniform spacing and layout principles

### Shared Components
If any agent needs a component not in the enhanced library, document it for potential shared use:
- DatePicker
- PhoneInput
- AddressAutocomplete
- SkillTagSelector
- AvailabilityGrid

### Communication
Each agent should:
1. Start by reading this document section
2. Review the design system files
3. Check the enhanced components
4. Begin implementation
5. Test thoroughly
6. Mark complete when done

## Success Criteria
- All 7 forms redesigned with enhanced components
- Professional UX matching top job platforms
- Mobile responsive design
- Federal compliance maintained
- Smooth animations and micro-interactions
- Comprehensive validation
- Accessibility compliant
- Performance optimized