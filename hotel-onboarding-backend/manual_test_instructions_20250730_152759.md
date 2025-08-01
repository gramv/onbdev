
# Manual Field Validation Testing Instructions

## Setup
1. Open browser to http://localhost:3001
2. Navigate to job application form
3. Open browser developer console (F12)

## Test Each Field

### Personal Information Fields

#### First Name
1. Leave empty and tab out → Should show "First name is required"
2. Enter `<script>alert('xss')</script>` → Should sanitize or reject
3. Enter `'; DROP TABLE users; --` → Should sanitize or reject
4. Enter 500 A's → Should enforce max length
5. Enter `😀😃😄` → Should accept or show clear error
6. Enter `José` → Should accept accented characters

#### Email
1. Enter `notanemail` → Should show "Invalid email format"
2. Enter `test@` → Should show error
3. Enter `test@@test.com` → Should show error
4. Enter `test..user@test.com` → Should show error
5. Enter `test user@test.com` → Should show error

#### Phone
1. Enter `123` → Should show "Invalid phone number"
2. Enter `abcdefghij` → Should show error
3. Enter `123-abc-4567` → Should show error
4. Enter `(555) 123-4567` → Should accept and format

#### ZIP Code
1. Enter `1234` → Should show "Invalid ZIP code"
2. Enter `ABCDE` → Should show error
3. Enter `12345-` → Should show error or autocomplete
4. Enter `12345` → Should accept
5. Enter `12345-6789` → Should accept

### Cross-Field Validation

1. If email confirmation exists:
   - Enter different emails → Should show mismatch error
   
2. Navigation validation:
   - Leave required fields empty
   - Click Next → Should prevent navigation

### Security Testing

1. Open Network tab in dev tools
2. Submit form with XSS payload
3. Check if payload is sanitized in request
4. Check response for any reflected input

## What to Look For

✅ Good:
- Clear, immediate error messages
- Prevents navigation with invalid data
- Sanitizes dangerous input
- Consistent validation across fields

❌ Bad:
- No validation on required fields
- Accepts SQL/XSS without sanitization
- Allows navigation with invalid data
- Stores dangerous input as-is
