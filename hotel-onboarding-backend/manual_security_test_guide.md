# Manual Security Testing Guide - Hotel Job Application Form

This guide provides step-by-step instructions for manually testing security vulnerabilities in the job application form.

## Prerequisites

1. Backend server running on http://localhost:8000
2. Frontend running on http://localhost:3000
3. Browser Developer Tools
4. API testing tool (Postman, curl, or similar)

## Test URL
```
http://localhost:3000/apply/property123
```

## Testing Methodology

### Phase 1: UI-Based Testing

#### 1. XSS (Cross-Site Scripting) Tests

**Test each text field with these payloads:**

```javascript
// Basic XSS
<script>alert('xss')</script>

// Event handler XSS
<img src=x onerror=alert(1)>
<svg onload=alert(1)>

// JavaScript URL
javascript:alert(1)

// Encoded XSS
&lt;script&gt;alert('xss')&lt;/script&gt;

// Breaking out of attributes
"><script>alert(1)</script>
'><script>alert(1)</script>
```

**Steps:**
1. Enter payload in each field
2. Submit form
3. Check if script executes
4. View page source for unescaped content
5. Check stored data display

#### 2. SQL Injection Tests

**Test each field with:**

```sql
'; DROP TABLE users; --
' OR '1'='1
' OR '1'='1' --
' OR '1'='1' /*
UNION SELECT * FROM users
admin'--
1' ORDER BY 1--+
```

**Expected:** All should be rejected with validation errors

#### 3. Format Bypass Tests

**Email field:**
```
test@test
@test.com
test@
test@@test.com
test@test..com
test@test.com<script>alert(1)</script>
test@[127.0.0.1]
```

**Phone field:**
```
1234567890
123-456-7890
(abc) def-ghij
(123) 456-<script>
```

**Zip code:**
```
1234
123456
abcde
<script>
```

### Phase 2: Browser DevTools Testing

#### 1. Remove Client-Side Validation

```javascript
// In console, remove all validation
document.querySelectorAll('input').forEach(input => {
    input.removeAttribute('required');
    input.removeAttribute('pattern');
    input.removeAttribute('maxlength');
    input.removeAttribute('minlength');
    input.removeAttribute('type');
});
```

#### 2. Modify Form Data Before Submit

```javascript
// Intercept form submission
document.querySelector('form').addEventListener('submit', (e) => {
    e.preventDefault();
    // Modify form data
    const formData = new FormData(e.target);
    formData.set('first_name', '<script>alert(1)</script>');
    // Submit modified data
});
```

### Phase 3: Direct API Testing

#### 1. Bypass Frontend Completely

```bash
# Test with curl
curl -X POST http://localhost:8000/apply/property123 \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "<script>alert(1)</script>",
    "last_name": "'; DROP TABLE users; --",
    "email": "test@test.com<script>",
    "phone": "(123) 456-7890",
    "address": "123 Main St",
    "city": "City",
    "state": "ST",
    "zip_code": "12345",
    "date_of_birth": "1990-01-01",
    "position_applied": "Position",
    "availability": {
      "monday": true,
      "tuesday": true,
      "wednesday": true,
      "thursday": true,
      "friday": true,
      "saturday": false,
      "sunday": false,
      "full_time": true,
      "part_time": false,
      "start_date": "2024-02-01"
    },
    "employment_history": [],
    "references": [],
    "emergency_contact": {
      "name": "Contact",
      "relationship": "Relation",
      "phone": "(555) 555-5555"
    },
    "legal_eligibility": {
      "authorized_to_work": true,
      "require_visa_sponsorship": false,
      "convicted_of_crime": false,
      "crime_explanation": ""
    }
  }'
```

#### 2. Test Field Length Limits

```bash
# Test with 10,000 character string
curl -X POST http://localhost:8000/apply/property123 \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "'$(python3 -c "print('A' * 10000))'",
    ...
  }'
```

### Phase 4: Special Character Testing

Test each field with:
```
< > & % $ # @ ! ' " \ / | { } [ ] ( ) = + - * _ ~ ` ^ ; : , . ?
```

### Phase 5: Unicode and Encoding Tests

```
😀🔥💀
‏מימין לשמאל‏ (Hebrew RTL)
العربية (Arabic)
中文字符 (Chinese)
\u202e\u202d\u202c (RTL override)
\u200b\u200c\u200d (Zero-width)
```

### Phase 6: Business Logic Tests

#### 1. Date Validation
- Birth date in future: 2030-01-01
- Invalid dates: 2024-02-30, 2024-13-01
- Employment end date before start date

#### 2. Cross-Field Validation
- Part-time AND full-time both selected
- No availability days selected
- Contradictory information

### Phase 7: File Upload Testing (if applicable)

```bash
# Test malicious filenames
curl -X POST http://localhost:8000/upload \
  -F "file=@test.txt;filename=../../etc/passwd"

# Test large files
dd if=/dev/zero of=large.txt bs=1M count=100
curl -X POST http://localhost:8000/upload \
  -F "file=@large.txt"
```

## Security Checklist

### Frontend Security
- [ ] XSS prevention (output encoding)
- [ ] Input validation on client
- [ ] HTTPS only
- [ ] Content Security Policy headers
- [ ] No sensitive data in JavaScript

### Backend Security
- [ ] Input validation on server
- [ ] Parameterized queries (no SQL injection)
- [ ] Rate limiting
- [ ] Authentication/authorization
- [ ] CSRF protection
- [ ] Security headers

### Data Security
- [ ] Encryption at rest
- [ ] Encryption in transit
- [ ] PII data protection
- [ ] Audit logging
- [ ] Data retention policies

## Reporting Vulnerabilities

When you find a vulnerability, document:

1. **Title**: Clear description
2. **Severity**: Critical/High/Medium/Low
3. **Steps to Reproduce**: Exact steps
4. **Proof of Concept**: Code/screenshot
5. **Impact**: What attacker could do
6. **Remediation**: How to fix

## Automated Testing

Run the automated test suite:
```bash
cd hotel-onboarding-backend
python3 security_test_job_application.py
```

This will test all fields with 150+ payloads and generate a report.