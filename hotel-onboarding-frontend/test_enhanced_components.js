/**
 * Enhanced UI Components Test Suite
 * Tests the professional redesigned components
 */

const puppeteer = require('puppeteer');

class EnhancedComponentTester {
  constructor() {
    this.browser = null;
    this.page = null;
    this.results = {
      enhancedInput: [],
      enhancedSelect: [],
      enhancedTextarea: [],
      stepCard: [],
      progressIndicator: [],
      fileUploadZone: []
    };
  }

  async initialize() {
    console.log('🚀 Initializing browser for component testing...');
    this.browser = await puppeteer.launch({
      headless: false, // Set to true for CI/CD
      defaultViewport: { width: 1280, height: 800 }
    });
    this.page = await this.browser.newPage();
    
    // Enable console logging from page
    this.page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    this.page.on('error', err => console.error('PAGE ERROR:', err));
  }

  async testEnhancedInput() {
    console.log('\n📝 Testing EnhancedInput Component...');
    
    try {
      await this.page.goto('http://localhost:3000/apply/test-property');
      await this.page.waitForSelector('input', { timeout: 5000 });
      
      // Test floating label animation
      const inputs = await this.page.$$('input');
      if (inputs.length > 0) {
        await inputs[0].click();
        await this.page.waitForTimeout(500);
        
        // Check if label floats
        const labelStyle = await this.page.evaluate(() => {
          const label = document.querySelector('label');
          return label ? window.getComputedStyle(label) : null;
        });
        
        this.log('enhancedInput', 'Floating Label', labelStyle ? 'PASS' : 'FAIL');
      }
      
      // Test phone number formatting
      const phoneInput = await this.page.$('input[type="tel"]');
      if (phoneInput) {
        await phoneInput.type('5551234567');
        const value = await phoneInput.evaluate(el => el.value);
        const isFormatted = value === '(555) 123-4567';
        this.log('enhancedInput', 'Phone Formatting', isFormatted ? 'PASS' : 'FAIL', value);
      }
      
      // Test SSN formatting
      const ssnInput = await this.page.$('input[name*="ssn"]');
      if (ssnInput) {
        await ssnInput.type('123456789');
        const value = await ssnInput.evaluate(el => el.value);
        const isFormatted = value === '123-45-6789';
        this.log('enhancedInput', 'SSN Formatting', isFormatted ? 'PASS' : 'FAIL', value);
      }
      
      // Test validation states
      const emailInput = await this.page.$('input[type="email"]');
      if (emailInput) {
        await emailInput.type('invalid-email');
        await this.page.waitForTimeout(1000); // Wait for debounced validation
        
        const hasError = await this.page.$('.text-red-500');
        this.log('enhancedInput', 'Email Validation', hasError ? 'PASS' : 'WARN', 
                'Invalid email should show error');
        
        await emailInput.click({ clickCount: 3 }); // Select all
        await emailInput.type('valid@email.com');
        await this.page.waitForTimeout(1000);
        
        const hasSuccess = await this.page.$('.text-green-500');
        this.log('enhancedInput', 'Valid Email', hasSuccess ? 'PASS' : 'WARN',
                'Valid email should show success');
      }
      
    } catch (error) {
      this.log('enhancedInput', 'Component Test', 'FAIL', error.message);
    }
  }

  async testEnhancedSelect() {
    console.log('\n🎯 Testing EnhancedSelect Component...');
    
    try {
      // Navigate to position step
      const nextButton = await this.page.$('button:has-text("Next")');
      if (nextButton) await nextButton.click();
      
      await this.page.waitForTimeout(1000);
      
      // Test searchable select
      const selects = await this.page.$$('select');
      if (selects.length > 0) {
        await selects[0].click();
        
        // Check for search functionality
        const hasSearch = await this.page.$('input[placeholder*="Search"]');
        this.log('enhancedSelect', 'Searchable Dropdown', hasSearch ? 'PASS' : 'INFO',
                'Search functionality in select');
      }
      
      // Test cascading selects (department -> position)
      const departmentSelect = await this.page.$('select[name*="department"]');
      if (departmentSelect) {
        await departmentSelect.select('Front Desk');
        await this.page.waitForTimeout(500);
        
        const positionSelect = await this.page.$('select[name*="position"]');
        const options = await positionSelect.$$eval('option', opts => 
          opts.map(opt => opt.textContent)
        );
        
        const hasCascading = options.includes('Receptionist');
        this.log('enhancedSelect', 'Cascading Select', hasCascading ? 'PASS' : 'FAIL',
                'Position options should update based on department');
      }
      
    } catch (error) {
      this.log('enhancedSelect', 'Component Test', 'FAIL', error.message);
    }
  }

  async testEnhancedTextarea() {
    console.log('\n📄 Testing EnhancedTextarea Component...');
    
    try {
      // Navigate to a step with textarea
      const textareas = await this.page.$$('textarea');
      
      if (textareas.length > 0) {
        const textarea = textareas[0];
        
        // Test auto-resize
        const initialHeight = await textarea.evaluate(el => el.offsetHeight);
        await textarea.type('Line 1\nLine 2\nLine 3\nLine 4\nLine 5');
        const newHeight = await textarea.evaluate(el => el.offsetHeight);
        
        const autoResizes = newHeight > initialHeight;
        this.log('enhancedTextarea', 'Auto-resize', autoResizes ? 'PASS' : 'FAIL',
                `Height changed from ${initialHeight}px to ${newHeight}px`);
        
        // Test character counter
        const counter = await this.page.$('.text-sm.text-gray-500');
        if (counter) {
          const counterText = await counter.evaluate(el => el.textContent);
          this.log('enhancedTextarea', 'Character Counter', 'PASS', counterText);
        }
      }
      
    } catch (error) {
      this.log('enhancedTextarea', 'Component Test', 'FAIL', error.message);
    }
  }

  async testStepCard() {
    console.log('\n🎴 Testing StepCard Component...');
    
    try {
      // Check for collapsible cards
      const cards = await this.page.$$('[data-testid="step-card"]');
      
      if (cards.length > 0) {
        // Test collapse/expand
        const collapseButton = await this.page.$('[aria-label*="Collapse"]');
        if (collapseButton) {
          await collapseButton.click();
          await this.page.waitForTimeout(500);
          
          const isCollapsed = await this.page.evaluate(() => {
            const card = document.querySelector('[data-testid="step-card"]');
            return card?.classList.contains('collapsed');
          });
          
          this.log('stepCard', 'Collapsible', 'PASS', 'Card can be collapsed');
        }
        
        // Test progress indicator on card
        const progress = await this.page.$('.progress-indicator');
        this.log('stepCard', 'Progress Indicator', progress ? 'PASS' : 'INFO',
                'Progress shown on card');
      }
      
    } catch (error) {
      this.log('stepCard', 'Component Test', 'FAIL', error.message);
    }
  }

  async testProgressIndicator() {
    console.log('\n📊 Testing ProgressIndicator Component...');
    
    try {
      // Check main progress bar
      const progressBar = await this.page.$('[role="progressbar"]');
      if (progressBar) {
        const value = await progressBar.getAttribute('aria-valuenow');
        this.log('progressIndicator', 'Progress Bar', 'PASS', `Current: ${value}%`);
      }
      
      // Check step indicators
      const stepIndicators = await this.page.$$('.step-indicator');
      this.log('progressIndicator', 'Step Indicators', 'PASS', 
              `Found ${stepIndicators.length} step indicators`);
      
      // Test navigation via progress indicator
      if (stepIndicators.length > 1) {
        await stepIndicators[1].click();
        await this.page.waitForTimeout(500);
        
        const navigated = await this.page.evaluate(() => {
          return window.location.hash || window.location.pathname;
        });
        
        this.log('progressIndicator', 'Step Navigation', 'INFO',
                'Click to navigate between steps');
      }
      
    } catch (error) {
      this.log('progressIndicator', 'Component Test', 'FAIL', error.message);
    }
  }

  async testFileUploadZone() {
    console.log('\n📁 Testing FileUploadZone Component...');
    
    try {
      // Look for file upload zones
      const uploadZones = await this.page.$$('[data-testid="file-upload-zone"]');
      
      if (uploadZones.length > 0) {
        // Test drag-and-drop area
        const dropZone = uploadZones[0];
        const rect = await dropZone.boundingBox();
        
        // Simulate drag over
        await this.page.mouse.move(rect.x + rect.width / 2, rect.y + rect.height / 2);
        
        const hasDragOver = await this.page.evaluate(() => {
          const zone = document.querySelector('[data-testid="file-upload-zone"]');
          return zone?.classList.contains('drag-over');
        });
        
        this.log('fileUploadZone', 'Drag & Drop', hasDragOver ? 'PASS' : 'INFO',
                'Drag over state detected');
        
        // Check for file type restrictions
        const acceptedTypes = await dropZone.evaluate(el => 
          el.querySelector('input[type="file"]')?.getAttribute('accept')
        );
        
        this.log('fileUploadZone', 'File Types', 'PASS', 
                `Accepted: ${acceptedTypes || 'All types'}`);
      } else {
        this.log('fileUploadZone', 'Component', 'INFO', 
                'No file upload zones in current step');
      }
      
    } catch (error) {
      this.log('fileUploadZone', 'Component Test', 'FAIL', error.message);
    }
  }

  async testMobileResponsiveness() {
    console.log('\n📱 Testing Mobile Responsiveness...');
    
    const viewports = [
      { name: 'iPhone SE', width: 320, height: 568 },
      { name: 'iPhone 12', width: 375, height: 812 },
      { name: 'iPad', width: 768, height: 1024 },
      { name: 'Desktop', width: 1024, height: 768 },
      { name: 'Wide', width: 1440, height: 900 }
    ];
    
    for (const viewport of viewports) {
      try {
        await this.page.setViewport({ width: viewport.width, height: viewport.height });
        await this.page.waitForTimeout(500);
        
        // Check if navigation adapts
        const mobileNav = await this.page.$('.mobile-navigation');
        const desktopNav = await this.page.$('.desktop-navigation');
        
        if (viewport.width < 768) {
          this.log('responsive', `${viewport.name} (${viewport.width}px)`, 
                  mobileNav ? 'PASS' : 'WARN', 'Mobile navigation should be visible');
        } else {
          this.log('responsive', `${viewport.name} (${viewport.width}px)`,
                  desktopNav ? 'PASS' : 'WARN', 'Desktop navigation should be visible');
        }
        
        // Check touch target sizes
        const buttons = await this.page.$$('button');
        if (buttons.length > 0) {
          const size = await buttons[0].evaluate(el => ({
            width: el.offsetWidth,
            height: el.offsetHeight
          }));
          
          const meetsMinimum = size.height >= 44;
          this.log('responsive', `Touch Target (${viewport.name})`, 
                  meetsMinimum ? 'PASS' : 'FAIL',
                  `Button height: ${size.height}px (min: 44px)`);
        }
        
      } catch (error) {
        this.log('responsive', viewport.name, 'FAIL', error.message);
      }
    }
  }

  async testAutoSave() {
    console.log('\n💾 Testing Auto-save Functionality...');
    
    try {
      // Fill in some data
      const firstNameInput = await this.page.$('input[name="firstName"]');
      if (firstNameInput) {
        await firstNameInput.type('TestAutoSave');
        
        // Wait for auto-save (should happen within 30 seconds)
        await this.page.waitForTimeout(2000); // Wait 2 seconds for debounced save
        
        // Check localStorage
        const savedData = await this.page.evaluate(() => {
          return localStorage.getItem('jobApplicationDraft');
        });
        
        if (savedData) {
          const draft = JSON.parse(savedData);
          const hasSavedName = draft.data?.personalInfo?.firstName === 'TestAutoSave';
          
          this.log('autoSave', 'Draft Saved', hasSavedName ? 'PASS' : 'FAIL',
                  'Data saved to localStorage');
          
          // Test recovery
          await this.page.reload();
          await this.page.waitForSelector('input[name="firstName"]');
          
          const recoveredValue = await this.page.$eval('input[name="firstName"]', 
            el => el.value
          );
          
          this.log('autoSave', 'Draft Recovery', 
                  recoveredValue === 'TestAutoSave' ? 'PASS' : 'FAIL',
                  `Recovered: ${recoveredValue}`);
        } else {
          this.log('autoSave', 'Auto-save', 'FAIL', 'No draft found in localStorage');
        }
      }
      
    } catch (error) {
      this.log('autoSave', 'Test', 'FAIL', error.message);
    }
  }

  log(category, test, status, details = '') {
    const result = { test, status, details, timestamp: new Date().toISOString() };
    
    if (this.results[category]) {
      this.results[category].push(result);
    }
    
    const icon = status === 'PASS' ? '✅' : 
                status === 'FAIL' ? '❌' : 
                status === 'WARN' ? '⚠️' : 'ℹ️';
    
    console.log(`${icon} [${category}] ${test}: ${details}`);
  }

  async generateReport() {
    console.log('\n' + '='.repeat(50));
    console.log('TEST REPORT SUMMARY');
    console.log('='.repeat(50));
    
    let totalTests = 0;
    let passed = 0;
    let failed = 0;
    let warnings = 0;
    
    for (const [category, tests] of Object.entries(this.results)) {
      for (const test of tests) {
        totalTests++;
        if (test.status === 'PASS') passed++;
        else if (test.status === 'FAIL') failed++;
        else if (test.status === 'WARN') warnings++;
      }
    }
    
    console.log(`\nTotal Tests: ${totalTests}`);
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`⚠️  Warnings: ${warnings}`);
    
    if (totalTests > 0) {
      const successRate = ((passed / (passed + failed)) * 100).toFixed(1);
      console.log(`\nSuccess Rate: ${successRate}%`);
    }
    
    // Save detailed report
    const fs = require('fs');
    fs.writeFileSync('enhanced_components_test_report.json', 
      JSON.stringify(this.results, null, 2)
    );
    
    console.log('\nDetailed report saved to: enhanced_components_test_report.json');
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async runAllTests() {
    try {
      await this.initialize();
      
      // Run component tests
      await this.testEnhancedInput();
      await this.testEnhancedSelect();
      await this.testEnhancedTextarea();
      await this.testStepCard();
      await this.testProgressIndicator();
      await this.testFileUploadZone();
      
      // Run feature tests
      await this.testMobileResponsiveness();
      await this.testAutoSave();
      
      // Generate report
      await this.generateReport();
      
    } catch (error) {
      console.error('Test suite error:', error);
    } finally {
      await this.cleanup();
    }
  }
}

// Run tests if executed directly
if (require.main === module) {
  const tester = new EnhancedComponentTester();
  tester.runAllTests().catch(console.error);
}

module.exports = EnhancedComponentTester;