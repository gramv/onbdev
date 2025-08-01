# Comprehensive Field Validation Test Cases

Generated: 2025-07-30 15:23:50

## Test Instructions

1. Open the job application form at http://localhost:3001
2. For each field, test with the provided test cases
3. Record the behavior in the checklist
4. Note any unexpected behaviors or security concerns

## Personal Information Step

### First Name Field

#### Empty Values
- [ ] Input: `''` - Expected: Show 'First name is required' error
- [ ] Input: `' '` - Expected: Show 'First name is required' error
- [ ] Input: `'  '` - Expected: Show 'First name is required' error
- [ ] Input: `'\t'` - Expected: Show 'First name is required' error
- [ ] Input: `'\n'` - Expected: Show 'First name is required' error
- [ ] Input: `'\r\n'` - Expected: Show 'First name is required' error

#### Special Characters
- [ ] Input: `<>` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `&%$#` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `@!` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `'"` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `\` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `/` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `|` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `{}` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `[]` - Expected: Either sanitize or show 'Invalid characters' error
- [ ] Input: `()` - Expected: Either sanitize or show 'Invalid characters' error

#### SQL Injection
- [ ] Input: `'; DROP TABLE users; --` - Expected: Sanitize/escape or reject with error
- [ ] Input: `1' OR '1'='1` - Expected: Sanitize/escape or reject with error
- [ ] Input: `admin'--` - Expected: Sanitize/escape or reject with error
- [ ] Input: `' UNION SELECT * FROM users --` - Expected: Sanitize/escape or reject with error
- [ ] Input: `1; DELETE FROM applications WHERE 1=1; --` - Expected: Sanitize/escape or reject with error

#### XSS Attempts
- [ ] Input: `<script>alert('xss')</script>` - Expected: Sanitize HTML tags or reject
- [ ] Input: `<img src=x onerror=alert('xss')>` - Expected: Sanitize HTML tags or reject
- [ ] Input: `<iframe src='javascript:alert(1)'></iframe>` - Expected: Sanitize HTML tags or reject
- [ ] Input: `javascript:alert('xss')` - Expected: Sanitize HTML tags or reject
- [ ] Input: `<svg onload=alert('xss')>` - Expected: Sanitize HTML tags or reject
- [ ] Input: `<<SCRIPT>alert('XSS');//<</SCRIPT>` - Expected: Sanitize HTML tags or reject
- [ ] Input: `<body onload=alert('xss')>` - Expected: Sanitize HTML tags or reject

#### Very Long Input
- [ ] Input: `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` - Expected: Accept or show max length error
- [ ] Input: `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` - Expected: Enforce max length limit

### Email Field

#### Invalid Formats
- [ ] Input: `test..user@domain.com` - Expected: Show 'Invalid email format' error
- [ ] Input: `.test@domain.com` - Expected: Show 'Invalid email format' error
- [ ] Input: `test.@domain.com` - Expected: Show 'Invalid email format' error
- [ ] Input: `test user@domain.com` - Expected: Show 'Invalid email format' error
- [ ] Input: `test@domain..com` - Expected: Show 'Invalid email format' error
- [ ] Input: `test@domain .com` - Expected: Show 'Invalid email format' error
- [ ] Input: `test@ domain.com` - Expected: Show 'Invalid email format' error

#### Missing @ Symbol
- [ ] Input: `testuser.com` - Expected: Show 'Invalid email format' error
- [ ] Input: `test.user.com` - Expected: Show 'Invalid email format' error
- [ ] Input: `test@` - Expected: Show 'Invalid email format' error
- [ ] Input: `@domain.com` - Expected: Show 'Invalid email format' error

#### Multiple @ Symbols
- [ ] Input: `test@@domain.com` - Expected: Show 'Invalid email format' error
- [ ] Input: `test@user@domain.com` - Expected: Show 'Invalid email format' error
- [ ] Input: `@test@domain.com` - Expected: Show 'Invalid email format' error

### Phone Field

#### Invalid Formats
- [ ] Input: `123` - Expected: Show 'Invalid phone number' error or format correctly
- [ ] Input: `12345` - Expected: Show 'Invalid phone number' error or format correctly
- [ ] Input: `123456789012345` - Expected: Show 'Invalid phone number' error or format correctly
- [ ] Input: `abcdefghij` - Expected: Show 'Invalid phone number' error or format correctly
- [ ] Input: `123-abc-4567` - Expected: Show 'Invalid phone number' error or format correctly
- [ ] Input: `phone number` - Expected: Show 'Invalid phone number' error or format correctly
- [ ] Input: `555-CALL-NOW` - Expected: Show 'Invalid phone number' error or format correctly
- [ ] Input: `1234567890123456789012345` - Expected: Show 'Invalid phone number' error or format correctly

#### International Formats
- [ ] Input: `+1 (555) 123-4567` - Expected: Accept or format to standard format
- [ ] Input: `+44 20 7946 0958` - Expected: Accept or format to standard format
- [ ] Input: `+86 138 0013 8000` - Expected: Accept or format to standard format
- [ ] Input: `001-555-123-4567` - Expected: Accept or format to standard format
- [ ] Input: `+1-555-123-4567` - Expected: Accept or format to standard format
- [ ] Input: `011-44-20-7946-0958` - Expected: Accept or format to standard format

### Address Fields

#### ZIP Code
- [ ] Input: `1234` - Expected: Show 'Invalid ZIP code' error
- [ ] Input: `123456` - Expected: Show 'Invalid ZIP code' error
- [ ] Input: `ABCDE` - Expected: Show 'Invalid ZIP code' error
- [ ] Input: `12345-` - Expected: Show 'Invalid ZIP code' error
- [ ] Input: `12345-123` - Expected: Show 'Invalid ZIP code' error
- [ ] Input: `12345-ABCD` - Expected: Show 'Invalid ZIP code' error
- [ ] Input: `00000` - Expected: Show 'Invalid ZIP code' error
- [ ] Input: `99999` - Expected: Show 'Invalid ZIP code' error
- [ ] Input: `12345-0000` - Expected: Show 'Invalid ZIP code' error

#### State
- [ ] Input: `XX` - Expected: Show 'Invalid state' error or convert to valid state code
- [ ] Input: `California` - Expected: Show 'Invalid state' error or convert to valid state code
- [ ] Input: `ca` - Expected: Show 'Invalid state' error or convert to valid state code
- [ ] Input: `C` - Expected: Show 'Invalid state' error or convert to valid state code
- [ ] Input: `CAL` - Expected: Show 'Invalid state' error or convert to valid state code
- [ ] Input: `US` - Expected: Show 'Invalid state' error or convert to valid state code
- [ ] Input: `123` - Expected: Show 'Invalid state' error or convert to valid state code
- [ ] Input: `` - Expected: Show 'Invalid state' error or convert to valid state code

### SSN Field
- [ ] Input: `12345678` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `1234567890` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `123-45-678` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `12-345-6789` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `abc-de-fghi` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `000-00-0000` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `666-12-3456` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `123-00-4567` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `123-45-0000` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `999-99-9999` - Expected: Show 'Invalid SSN format' error
- [ ] Input: `078-05-1120` - Expected: Show 'Invalid SSN format' error

### Date of Birth Field

#### Invalid Dates
- [ ] Input: `02/30/2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `04/31/2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `13/01/2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `00/01/2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `01/00/2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `01/32/2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `2024/01/01` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `01-01-2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `Jan 1, 2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `01/2024` - Expected: Show 'Invalid date' error or prevent selection
- [ ] Input: `99/99/9999` - Expected: Show 'Invalid date' error or prevent selection

#### Future Dates
- [ ] Input: `01/01/2030` - Expected: Show 'Birth date cannot be in the future' error
- [ ] Input: Today's date - Expected: Show error or warning for unlikely birth date

## Cross-Field Validation Tests

### Email Confirmation
- [ ] Different emails in 'Email' and 'Confirm Email' - Expected: Show 'Emails do not match' error
- [ ] Copy-paste same email - Expected: Accept

### Phone Number Consistency
- [ ] Enter phone in different formats across forms - Expected: Store in consistent format

### SSN Consistency
- [ ] Enter different SSN in I-9 vs W-4 forms - Expected: Flag inconsistency or use single source

## Security Tests

### Form Submission
- [ ] Submit form with browser dev tools network throttling - Expected: Handle timeout gracefully
- [ ] Submit form multiple times rapidly - Expected: Prevent duplicate submissions
- [ ] Modify hidden fields via browser dev tools - Expected: Validate on server side
- [ ] Submit form with very large payload - Expected: Reject oversized requests

## File Upload Tests

### Invalid File Types
- [ ] Upload: `test.exe` - Expected: Show 'Invalid file type' error
- [ ] Upload: `test.bat` - Expected: Show 'Invalid file type' error
- [ ] Upload: `test.sh` - Expected: Show 'Invalid file type' error
- [ ] Upload: `test.js` - Expected: Show 'Invalid file type' error
- [ ] Upload: `test.html` - Expected: Show 'Invalid file type' error
- [ ] Upload: `very_large_file_100MB.pdf` - Expected: Show 'Invalid file type' error
- [ ] Upload: `corrupted_file.pdf` - Expected: Show 'Invalid file type' error
- [ ] Upload: `empty_file.pdf` - Expected: Show 'Invalid file type' error
- [ ] Upload: `file_without_extension` - Expected: Show 'Invalid file type' error
- [ ] Upload: `.hidden_file` - Expected: Show 'Invalid file type' error

### File Size
- [ ] Upload 50MB file - Expected: Show 'File too large' error
- [ ] Upload 0 byte file - Expected: Show 'File is empty' error

## Test Results Summary

### Issues Found

#### Critical (Security)
1. [Field Name] - [Issue description]
   - Input: `[test input]`
   - Expected: [expected behavior]
   - Actual: [actual behavior]
   - Impact: [security/data integrity impact]
   - Fix: [recommended fix]

#### High (Data Integrity)
1. [Field Name] - [Issue description]

#### Medium (User Experience)
1. [Field Name] - [Issue description]

#### Low (Enhancement)
1. [Field Name] - [Issue description]