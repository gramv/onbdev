#!/usr/bin/env node

/**
 * Comprehensive UX Testing Script
 * Tests the Job Application UX Improvements
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_URL = 'http://localhost:3000/apply/test-property-001';
const RESULTS_FILE = 'ux-test-results.json';

// Test results collector
const testResults = {
  timestamp: new Date().toISOString(),
  tests: [],
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    warnings: 0
  },
  performance: {
    pageLoadTime: 0,
    autoSaveTests: [],
    formValidationTests: []
  },
  accessibility: {
    touchTargets: [],
    keyboardNav: [],
    ariaLabels: []
  },
  responsiveness: {
    breakpoints: []
  }
};

// Helper function to add test result
function addTestResult(category, name, status, details = {}) {
  testResults.tests.push({
    category,
    name,
    status,
    details,
    timestamp: new Date().toISOString()
  });
  
  testResults.summary.total++;
  if (status === 'passed') testResults.summary.passed++;
  else if (status === 'failed') testResults.summary.failed++;
  else if (status === 'warning') testResults.summary.warnings++;
}

async function runTests() {
  console.log('🚀 Starting Comprehensive UX Tests...\n');
  
  const browser = await puppeteer.launch({
    headless: false, // Set to true for CI/CD
    defaultViewport: null,
    args: ['--window-size=1920,1080']
  });
  
  try {
    // Test 1: Page Load Performance
    console.log('📊 Testing Page Load Performance...');
    const page = await browser.newPage();
    
    const startTime = Date.now();
    await page.goto(TEST_URL, { waitUntil: 'networkidle2' });
    const loadTime = Date.now() - startTime;
    
    testResults.performance.pageLoadTime = loadTime;
    addTestResult('Performance', 'Page Load Time', 
      loadTime < 3000 ? 'passed' : 'warning',
      { loadTime: `${loadTime}ms`, threshold: '3000ms' }
    );
    
    // Test 2: FormInput Component Features
    console.log('🔤 Testing FormInput Component...');
    
    // Test floating labels
    const hasFloatingLabels = await page.evaluate(() => {
      const labels = document.querySelectorAll('label.absolute');
      return labels.length > 0;
    });
    addTestResult('Component', 'Floating Labels', 
      hasFloatingLabels ? 'passed' : 'failed',
      { found: hasFloatingLabels }
    );
    
    // Test phone formatting
    await page.type('input[name="phone"]', '5551234567');
    const phoneValue = await page.$eval('input[name="phone"]', el => el.value);
    const isPhoneFormatted = phoneValue.includes('(') || phoneValue.includes('-');
    addTestResult('Component', 'Phone Auto-Formatting', 
      isPhoneFormatted ? 'passed' : 'failed',
      { value: phoneValue, formatted: isPhoneFormatted }
    );
    
    // Test 3: Auto-Save Functionality
    console.log('💾 Testing Auto-Save...');
    
    // Fill in some data
    await page.type('input[name="first_name"]', 'Test');
    await page.type('input[name="last_name"]', 'User');
    await page.type('input[name="email"]', 'test@example.com');
    
    // Check localStorage for auto-save
    const hasSavedData = await page.evaluate(() => {
      const keys = Object.keys(localStorage);
      return keys.some(key => key.includes('jobApplication'));
    });
    addTestResult('Feature', 'Auto-Save to LocalStorage', 
      hasSavedData ? 'passed' : 'failed',
      { savedToLocalStorage: hasSavedData }
    );
    
    // Test recovery after refresh
    await page.reload({ waitUntil: 'networkidle2' });
    const recoveredFirstName = await page.$eval('input[name="first_name"]', el => el.value);
    const dataRecovered = recoveredFirstName === 'Test';
    addTestResult('Feature', 'Data Recovery After Refresh', 
      dataRecovered ? 'passed' : 'failed',
      { recoveredValue: recoveredFirstName, expected: 'Test' }
    );
    
    // Test 4: Mobile Responsiveness
    console.log('📱 Testing Mobile Responsiveness...');
    
    const breakpoints = [
      { name: 'Mobile S', width: 320, height: 568 },
      { name: 'Mobile M', width: 375, height: 667 },
      { name: 'Mobile L', width: 425, height: 812 },
      { name: 'Tablet', width: 768, height: 1024 },
      { name: 'Desktop', width: 1024, height: 768 }
    ];
    
    for (const breakpoint of breakpoints) {
      await page.setViewport({ width: breakpoint.width, height: breakpoint.height });
      await page.waitForTimeout(500);
      
      // Check for horizontal scroll
      const hasHorizontalScroll = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      
      // Check touch target sizes
      const touchTargetSizes = await page.evaluate(() => {
        const inputs = document.querySelectorAll('input, button, a');
        const sizes = [];
        inputs.forEach(el => {
          const rect = el.getBoundingClientRect();
          sizes.push({ height: rect.height, width: rect.width });
        });
        return sizes;
      });
      
      const minTouchTarget = 44;
      const adequateTouchTargets = touchTargetSizes.every(size => 
        size.height >= minTouchTarget || size.width >= minTouchTarget
      );
      
      testResults.responsiveness.breakpoints.push({
        name: breakpoint.name,
        width: breakpoint.width,
        hasHorizontalScroll,
        adequateTouchTargets,
        touchTargetCount: touchTargetSizes.length
      });
      
      addTestResult('Responsiveness', `${breakpoint.name} Layout`, 
        !hasHorizontalScroll && adequateTouchTargets ? 'passed' : 'failed',
        { 
          viewport: `${breakpoint.width}x${breakpoint.height}`,
          horizontalScroll: hasHorizontalScroll,
          touchTargets: adequateTouchTargets 
        }
      );
    }
    
    // Reset to desktop viewport
    await page.setViewport({ width: 1920, height: 1080 });
    
    // Test 5: Form Validation
    console.log('✅ Testing Form Validation...');
    
    // Clear fields and test validation
    await page.evaluate(() => {
      document.querySelectorAll('input').forEach(input => input.value = '');
    });
    
    // Try invalid email
    await page.type('input[name="email"]', 'invalid-email');
    await page.click('body'); // Trigger blur
    await page.waitForTimeout(600); // Wait for debounce
    
    const hasEmailError = await page.evaluate(() => {
      const errors = document.querySelectorAll('.text-red-500, .text-destructive');
      return Array.from(errors).some(el => 
        el.textContent.toLowerCase().includes('email') ||
        el.textContent.toLowerCase().includes('invalid')
      );
    });
    addTestResult('Validation', 'Email Validation', 
      hasEmailError ? 'passed' : 'warning',
      { errorShown: hasEmailError }
    );
    
    // Test 6: Accessibility
    console.log('♿ Testing Accessibility...');
    
    // Check ARIA attributes
    const ariaAttributes = await page.evaluate(() => {
      const inputs = document.querySelectorAll('input');
      const results = [];
      inputs.forEach(input => {
        results.push({
          name: input.name || input.id,
          hasAriaLabel: !!input.getAttribute('aria-label'),
          hasAriaDescribedBy: !!input.getAttribute('aria-describedby'),
          hasAriaInvalid: input.hasAttribute('aria-invalid')
        });
      });
      return results;
    });
    
    const hasProperAria = ariaAttributes.some(attr => 
      attr.hasAriaLabel || attr.hasAriaDescribedBy || attr.hasAriaInvalid
    );
    addTestResult('Accessibility', 'ARIA Attributes', 
      hasProperAria ? 'passed' : 'warning',
      { inputsWithAria: ariaAttributes.filter(a => a.hasAriaLabel).length }
    );
    
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    const focusedElement = await page.evaluate(() => {
      return document.activeElement ? document.activeElement.tagName : null;
    });
    addTestResult('Accessibility', 'Keyboard Navigation', 
      focusedElement ? 'passed' : 'failed',
      { focusedElement }
    );
    
    // Test 7: Visual Components
    console.log('🎨 Testing Visual Components...');
    
    // Check for icons
    const hasIcons = await page.evaluate(() => {
      return document.querySelectorAll('svg').length > 0;
    });
    addTestResult('Visual', 'Icons Present', 
      hasIcons ? 'passed' : 'warning',
      { iconsFound: hasIcons }
    );
    
    // Check card layouts
    const hasCards = await page.evaluate(() => {
      const cards = document.querySelectorAll('[class*="card"], [class*="Card"]');
      return cards.length > 0;
    });
    addTestResult('Visual', 'Card Components', 
      hasCards ? 'passed' : 'warning',
      { cardsFound: hasCards }
    );
    
    // Test 8: Progress Tracking
    console.log('📈 Testing Progress Tracking...');
    
    const hasProgressIndicator = await page.evaluate(() => {
      const progress = document.querySelector('[class*="progress"], [role="progressbar"]');
      return !!progress;
    });
    addTestResult('Feature', 'Progress Indicator', 
      hasProgressIndicator ? 'passed' : 'warning',
      { found: hasProgressIndicator }
    );
    
  } catch (error) {
    console.error('❌ Test Error:', error);
    addTestResult('System', 'Test Execution', 'failed', 
      { error: error.message }
    );
  } finally {
    await browser.close();
  }
  
  // Save results
  fs.writeFileSync(
    path.join(__dirname, RESULTS_FILE),
    JSON.stringify(testResults, null, 2)
  );
  
  // Print summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(50));
  console.log(`Total Tests: ${testResults.summary.total}`);
  console.log(`✅ Passed: ${testResults.summary.passed}`);
  console.log(`❌ Failed: ${testResults.summary.failed}`);
  console.log(`⚠️  Warnings: ${testResults.summary.warnings}`);
  console.log(`\nPage Load Time: ${testResults.performance.pageLoadTime}ms`);
  console.log(`\nDetailed results saved to: ${RESULTS_FILE}`);
  
  // Exit with appropriate code
  process.exit(testResults.summary.failed > 0 ? 1 : 0);
}

// Check if puppeteer is installed
try {
  require.resolve('puppeteer');
  runTests();
} catch (e) {
  console.log('📦 Installing puppeteer...');
  const { execSync } = require('child_process');
  execSync('npm install puppeteer', { stdio: 'inherit' });
  runTests();
}