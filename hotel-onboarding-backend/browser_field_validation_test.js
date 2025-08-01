/**
 * Browser-based Field Validation Testing Script
 * Run this in the browser console while on the job application form
 * 
 * Instructions:
 * 1. Navigate to http://localhost:3001/apply/{property_id}
 * 2. Open browser console (F12)
 * 3. Copy and paste this entire script
 * 4. View results in console
 */

const FieldValidationTester = {
  results: [],
  
  // Test data sets
  testData: {
    textFields: {
      empty: ["", " ", "  ", "\t", "\n"],
      sql: ["'; DROP TABLE users; --", "1' OR '1'='1", "admin'--"],
      xss: ["<script>alert('xss')</script>", "<img src=x onerror=alert('xss')>", "javascript:alert('xss')"],
      special: ["<>", "&%$#", "@!", "'\"", "\\", "/", "|", "{}", "[]", "()"],
      unicode: ["😀😃😄", "é à ñ ü", "™ ® ©", "中文测试"],
      long: ["A".repeat(500), "Test ".repeat(200)]
    },
    emails: {
      invalid: ["test", "test@", "@test.com", "test@@test.com", "test..user@test.com", "test user@test.com"],
      valid: ["test@example.com", "test.user@example.com", "test+tag@example.com"]
    },
    phones: {
      invalid: ["123", "abcdef", "123-abc-4567", "12345678901234567890"],
      valid: ["(555) 123-4567", "555-123-4567", "5551234567"]
    },
    ssns: {
      invalid: ["123456789", "123-45-678", "000-00-0000", "666-12-3456", "abc-de-fghi"],
      valid: ["123-45-6789"]
    },
    dates: {
      invalid: ["02/30/2024", "13/01/2024", "00/01/2024", "2030-01-01"],
      valid: ["01/01/2000", "12/31/1999"]
    },
    zips: {
      invalid: ["1234", "123456", "ABCDE", "12345-", "12345-123"],
      valid: ["12345", "12345-6789"]
    }
  },

  // Log test result
  logResult(field, testType, input, expected, actual, status) {
    const result = {
      timestamp: new Date().toISOString(),
      field,
      testType,
      input,
      expected,
      actual,
      status // "PASS", "FAIL", "WARNING"
    };
    this.results.push(result);
    
    console.log(`${status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⚠️'} ${field} - ${testType}: ${status}`);
    if (status !== 'PASS') {
      console.log(`   Input: ${JSON.stringify(input)}`);
      console.log(`   Expected: ${expected}`);
      console.log(`   Actual: ${actual}`);
    }
  },

  // Test a specific input field
  async testField(selector, testValues, fieldName, testType) {
    const field = document.querySelector(selector);
    if (!field) {
      console.error(`Field not found: ${selector}`);
      return;
    }

    for (const value of testValues) {
      // Set value
      field.value = value;
      field.dispatchEvent(new Event('input', { bubbles: true }));
      field.dispatchEvent(new Event('change', { bubbles: true }));
      field.dispatchEvent(new Event('blur', { bubbles: true }));
      
      // Wait for validation
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Check for error messages
      const errorElement = field.closest('.field-wrapper')?.querySelector('.error-message') ||
                          field.parentElement?.querySelector('.text-red-500') ||
                          document.querySelector(`[data-error-for="${field.name}"]`);
      
      const hasError = errorElement && errorElement.textContent.trim().length > 0;
      const errorMessage = hasError ? errorElement.textContent.trim() : 'No error';
      
      // Determine if test passed
      let status = 'PASS';
      let expected = '';
      let actual = errorMessage;
      
      if (testType === 'empty' && !hasError) {
        status = 'FAIL';
        expected = 'Should show required field error';
        actual = 'No error shown';
      } else if ((testType === 'sql' || testType === 'xss') && !hasError) {
        status = 'WARNING';
        expected = 'Should sanitize or reject dangerous input';
        actual = 'Input accepted without sanitization';
      } else if (testType === 'invalid' && !hasError) {
        status = 'FAIL';
        expected = 'Should show validation error';
        actual = 'Invalid input accepted';
      }
      
      this.logResult(fieldName, testType, value, expected, actual, status);
    }
  },

  // Run all tests
  async runAllTests() {
    console.log('🚀 Starting Field Validation Tests');
    console.log('=' . repeat(60));
    
    // Test Personal Information Fields
    console.log('\n📋 Testing Personal Information Fields\n');
    
    // First Name
    await this.testField('input[name="first_name"]', this.testData.textFields.empty, 'first_name', 'empty');
    await this.testField('input[name="first_name"]', this.testData.textFields.sql, 'first_name', 'sql');
    await this.testField('input[name="first_name"]', this.testData.textFields.xss, 'first_name', 'xss');
    await this.testField('input[name="first_name"]', this.testData.textFields.special, 'first_name', 'special');
    
    // Email
    await this.testField('input[name="email"]', this.testData.emails.invalid, 'email', 'invalid');
    
    // Phone
    await this.testField('input[name="phone"]', this.testData.phones.invalid, 'phone', 'invalid');
    
    // ZIP Code
    await this.testField('input[name="zip_code"]', this.testData.zips.invalid, 'zip_code', 'invalid');
    
    // Generate summary
    this.generateSummary();
  },

  // Generate test summary
  generateSummary() {
    console.log('\n' + '=' . repeat(60));
    console.log('📊 Test Summary');
    console.log('=' . repeat(60));
    
    const total = this.results.length;
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => r.status === 'FAIL').length;
    const warnings = this.results.filter(r => r.status === 'WARNING').length;
    
    console.log(`Total Tests: ${total}`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`⚠️ Warnings: ${warnings}`);
    
    // List critical failures
    const criticalFailures = this.results.filter(r => 
      r.status === 'FAIL' && (r.testType === 'sql' || r.testType === 'xss' || r.testType === 'empty')
    );
    
    if (criticalFailures.length > 0) {
      console.log('\n🚨 Critical Issues:');
      criticalFailures.forEach(f => {
        console.log(`- ${f.field}: ${f.expected}`);
      });
    }
    
    // Export results
    console.log('\n💾 To export full results, run:');
    console.log('copy(JSON.stringify(FieldValidationTester.results, null, 2))');
  },

  // Test cross-field validation
  async testCrossFieldValidation() {
    console.log('\n🔗 Testing Cross-Field Validation\n');
    
    // Test email confirmation if exists
    const email = document.querySelector('input[name="email"]');
    const emailConfirm = document.querySelector('input[name="email_confirm"]');
    
    if (email && emailConfirm) {
      email.value = 'test@example.com';
      emailConfirm.value = 'different@example.com';
      
      email.dispatchEvent(new Event('blur', { bubbles: true }));
      emailConfirm.dispatchEvent(new Event('blur', { bubbles: true }));
      
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const errorElement = emailConfirm.parentElement?.querySelector('.text-red-500');
      if (!errorElement) {
        this.logResult('email_confirmation', 'cross_field', 
          'different emails', 
          'Should show mismatch error', 
          'No error shown', 
          'FAIL'
        );
      } else {
        this.logResult('email_confirmation', 'cross_field',
          'different emails',
          'Should show mismatch error',
          errorElement.textContent,
          'PASS'
        );
      }
    }
  }
};

// Auto-run tests when script loads
console.log('Field Validation Tester loaded. Running tests...');
FieldValidationTester.runAllTests().then(() => {
  console.log('\n✅ Testing complete!');
});