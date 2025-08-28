# Component Testing Checklist

## Pre-Test Setup
- [ ] Frontend server running on http://localhost:5173/
- [ ] Backend server running on http://localhost:8000/ (optional)
- [ ] Browser developer tools open for console monitoring

## Test 1: Simple Test Dashboard
**URL**: http://localhost:5173/simple-test

### Visual Verification
- [ ] Page loads without errors
- [ ] All 3 component cards display correctly
- [ ] Status indicators show green checkmarks
- [ ] Compliance section shows correct status
- [ ] Test buttons are clickable

### Functionality Test
- [ ] Click "Test Component" buttons - should show alerts
- [ ] Verify component status descriptions are accurate
- [ ] Check that all implemented features are listed

**Expected Result**: Clean dashboard showing implementation status

---

## Test 2: Human Trafficking Awareness Module
**URL**: http://localhost:5173/test → Click "Human Trafficking"

### Section 1: What is Human Trafficking?
- [ ] Content displays with Users icon
- [ ] All 4 bullet points show correctly
- [ ] "Continue" button works
- [ ] Progress bar updates to ~25%

### Section 2: Types of Human Trafficking
- [ ] Content displays with AlertTriangle icon
- [ ] Sex trafficking and labor trafficking info shows
- [ ] Industry examples listed correctly
- [ ] Progress bar updates to ~50%

### Section 3: Warning Signs
- [ ] Content displays with Shield icon
- [ ] All 7 warning signs listed
- [ ] Employee behavior indicators clear
- [ ] Progress bar updates to ~75%

### Section 4: Reporting Information
- [ ] Content displays with Phone icon
- [ ] National Hotline number: 1-888-373-7888
- [ ] Text number: 233733 (BEFREE)
- [ ] Website: humantraffickinghotline.org
- [ ] 911 for emergencies mentioned

### Knowledge Quiz
- [ ] All 4 questions display
- [ ] True/False buttons work
- [ ] Immediate feedback shows for each answer
- [ ] Correct answers: False, True, False, True
- [ ] Explanations appear after each answer
- [ ] Cannot continue until all questions answered

### Acknowledgment Section
- [ ] 4 acknowledgment statements display
- [ ] Emergency contact information section shows
- [ ] "I Acknowledge Completion" button appears
- [ ] Clicking button shows completion message
- [ ] Green checkmark and success message display

**Expected Result**: Complete training flow with quiz and certification

---

## Test 3: Weapons Policy Acknowledgment
**URL**: http://localhost:5173/test → Click "Weapons Policy"

### Policy Reading Section
- [ ] Policy title displays with Shield icon
- [ ] 4 main sections show:
  - [ ] Prohibited Items (with red AlertTriangle icon)
  - [ ] Workplace Violence Prevention (with blue Shield icon)
  - [ ] Enforcement and Consequences (with orange FileText icon)
  - [ ] Reporting Procedures (with green Users icon)
- [ ] Each section has bullet points
- [ ] Limited Exceptions section shows in yellow box
- [ ] "I have read and understand" checkbox appears
- [ ] Must check box before acknowledgments appear

### Acknowledgments Section
- [ ] 6 acknowledgment checkboxes display
- [ ] Each acknowledgment text is clear and readable
- [ ] Cannot proceed without checking all boxes
- [ ] Checkboxes work properly

### Signature Section
- [ ] Appears only after policy read and acknowledgments checked
- [ ] Employee Acknowledgment title shows
- [ ] Legal statement displays in gray box
- [ ] Digital signature component loads
- [ ] Can test both draw and type signature methods

### Completion
- [ ] "Submit Policy Acknowledgment" button appears when ready
- [ ] Progress indicators show completion status
- [ ] Clicking submit shows success message
- [ ] Completion data logged (check console)

**Expected Result**: Complete policy acknowledgment with digital signature

---

## Test 4: I-9 Section 1 Form
**URL**: http://localhost:5173/test → Click "I-9 Section 1"

### Step 1: Personal Information
- [ ] Form title shows: "Form I-9, Section 1: Employee Information and Attestation"
- [ ] Progress bar shows Step 1 of 4
- [ ] Blue info box displays with instructions
- [ ] Required fields: First Name, Last Name (marked with *)
- [ ] Optional fields: Middle Initial, Other Last Names
- [ ] Validation works - cannot proceed without required fields
- [ ] "Next" button advances to step 2

### Step 2: Address Information
- [ ] Progress bar shows Step 2 of 4
- [ ] Street Address field (required)
- [ ] Apt/Unit field (optional)
- [ ] City field (required)
- [ ] State dropdown with all states (required)
- [ ] ZIP code field with validation (required)
- [ ] ZIP validation accepts XXXXX or XXXXX-XXXX format
- [ ] Cannot proceed without all required fields
- [ ] "Previous" and "Next" buttons work

### Step 3: Contact & Personal Details
- [ ] Progress bar shows Step 3 of 4
- [ ] Date of Birth field (required, date picker)
- [ ] SSN field with auto-formatting (XXX-XX-XXXX)
- [ ] Email field with validation
- [ ] Phone field with auto-formatting ((XXX) XXX-XXXX)
- [ ] All fields required
- [ ] Formatting works as you type
- [ ] Email validation prevents invalid formats

### Step 4: Citizenship and Work Authorization
- [ ] Progress bar shows Step 4 of 4
- [ ] Yellow warning box displays
- [ ] 4 citizenship options as radio buttons:
  - [ ] US Citizen
  - [ ] Noncitizen National
  - [ ] Lawful Permanent Resident
  - [ ] Alien Authorized to Work
- [ ] Each option has description text
- [ ] Must select one option

#### Additional Fields Test
- [ ] Select "Lawful Permanent Resident" → Additional fields appear
- [ ] Select "Alien Authorized to Work" → More additional fields appear
- [ ] USCIS Number field
- [ ] I-94 Admission Number field
- [ ] For authorized alien: Passport fields and expiration date
- [ ] Work authorization expiration required for authorized aliens

### Completion
- [ ] "Complete Section 1" button appears on final step
- [ ] All validation must pass before completion
- [ ] Success message or data capture occurs

**Expected Result**: Complete 4-step I-9 Section 1 form with validation

---

## Test 5: Error Handling & Edge Cases

### Form Validation
- [ ] Try submitting forms without required fields
- [ ] Test invalid email formats
- [ ] Test invalid SSN formats
- [ ] Test invalid ZIP codes
- [ ] Verify error messages are helpful

### Navigation
- [ ] Test browser back/forward buttons
- [ ] Test page refresh during form completion
- [ ] Test switching between components

### Responsive Design
- [ ] Test on mobile screen size
- [ ] Test on tablet screen size
- [ ] Verify forms are usable on smaller screens

---

## Test 6: Data Flow & Console Logging

### Check Browser Console
- [ ] No JavaScript errors during component loading
- [ ] Form data logged correctly on completion
- [ ] Signature data captured properly
- [ ] Progress tracking works

### Network Tab (if backend running)
- [ ] API calls succeed
- [ ] JWT tokens handled correctly
- [ ] PDF generation works
- [ ] Error responses handled gracefully

---

## Test 7: Accessibility & Usability

### Keyboard Navigation
- [ ] Can tab through all form fields
- [ ] Enter key submits forms where appropriate
- [ ] Focus indicators visible

### Screen Reader Compatibility
- [ ] Form labels associated with inputs
- [ ] Error messages announced
- [ ] Progress indicators accessible

### Color Contrast
- [ ] Text readable against backgrounds
- [ ] Important information clearly visible
- [ ] Status indicators distinguishable

---

## Post-Test Verification

### Critical Functions
- [ ] Human trafficking training completes fully
- [ ] Weapons policy acknowledgment captures signature
- [ ] I-9 Section 1 captures all required data
- [ ] Digital signatures work properly

### Federal Compliance
- [ ] Human trafficking content meets requirements
- [ ] I-9 form follows USCIS specifications
- [ ] Digital signatures comply with ESIGN Act
- [ ] Audit trail data captured

### Performance
- [ ] Components load quickly
- [ ] No memory leaks during usage
- [ ] Smooth transitions between steps
- [ ] Responsive user interactions

---

## Issues to Document

### High Priority Issues
- [ ] Any component that doesn't load
- [ ] Form validation that doesn't work
- [ ] Required functionality missing

### Medium Priority Issues
- [ ] UI/UX improvements needed
- [ ] Performance optimization opportunities
- [ ] Better error messages needed

### Low Priority Issues
- [ ] Minor styling improvements
- [ ] Additional convenience features
- [ ] Enhanced user experience

---

**Testing Complete**: ✅ / ❌

**Overall Status**: [Pass/Fail with notes]

**Ready for Next Phase**: [Yes/No with requirements]