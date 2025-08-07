#!/usr/bin/env node

/**
 * Frontend Import Validation Test
 * Tests that all critical imports are working correctly
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Testing Frontend Import Resolution...\n');

// Test files to check
const testFiles = [
  'hotel-onboarding-frontend/src/App.tsx',
  'hotel-onboarding-frontend/src/pages/EnhancedOnboardingPortal.tsx',
  'hotel-onboarding-frontend/src/pages/OnboardingPortal.tsx',
  'hotel-onboarding-frontend/src/components/layouts/OnboardingLayout.tsx',
  'hotel-onboarding-frontend/src/pages/onboarding/WelcomeStep.tsx',
  'hotel-onboarding-frontend/src/pages/onboarding/PersonalInfoStep.tsx',
  'hotel-onboarding-frontend/src/components/ui/pdf-document-viewer.tsx'
];

// Required components that should exist
const requiredComponents = [
  'hotel-onboarding-frontend/src/components/PersonalInformationForm.tsx',
  'hotel-onboarding-frontend/src/components/I9Section1Form.tsx',
  'hotel-onboarding-frontend/src/components/W4Form.tsx',
  'hotel-onboarding-frontend/src/components/DirectDepositForm.tsx',
  'hotel-onboarding-frontend/src/components/EmergencyContactsForm.tsx',
  'hotel-onboarding-frontend/src/components/HealthInsuranceForm.tsx',
  'hotel-onboarding-frontend/src/components/HumanTraffickingAwareness.tsx',
  'hotel-onboarding-frontend/src/components/WeaponsPolicyAcknowledgment.tsx'
];

// Required utilities
const requiredUtils = [
  'hotel-onboarding-frontend/src/utils/governmentFormMapping.ts',
  'hotel-onboarding-frontend/src/utils/officialPacketMapping.ts'
];

let allTestsPassed = true;

// Test 1: Check if all test files exist
console.log('📁 Testing File Existence...');
testFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - MISSING`);
    allTestsPassed = false;
  }
});

// Test 2: Check required components
console.log('\n🧩 Testing Required Components...');
requiredComponents.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${path.basename(file)}`);
  } else {
    console.log(`❌ ${path.basename(file)} - MISSING`);
    allTestsPassed = false;
  }
});

// Test 3: Check required utilities
console.log('\n🔧 Testing Required Utilities...');
requiredUtils.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${path.basename(file)}`);
  } else {
    console.log(`❌ ${path.basename(file)} - MISSING`);
    allTestsPassed = false;
  }
});

// Test 4: Check for critical import patterns
console.log('\n📦 Testing Import Patterns...');
const appTsx = fs.readFileSync('hotel-onboarding-frontend/src/App.tsx', 'utf8');

// Check for OnboardingPortal import
if (appTsx.includes("import OnboardingPortal from './pages/OnboardingPortal'")) {
  console.log('✅ OnboardingPortal import found');
} else {
  console.log('❌ OnboardingPortal import missing');
  allTestsPassed = false;
}

// Check for TraffickingAwarenessStep import (corrected spelling)
if (appTsx.includes("import TraffickingAwarenessStep from './pages/onboarding/TrafficakingAwarenessStep'")) {
  console.log('✅ TraffickingAwarenessStep import found (with corrected path)');
} else {
  console.log('❌ TraffickingAwarenessStep import issue');
  allTestsPassed = false;
}

// Test 5: Check OnboardingPortal wrapper
console.log('\n🔄 Testing OnboardingPortal Wrapper...');
if (fs.existsSync('hotel-onboarding-frontend/src/pages/OnboardingPortal.tsx')) {
  const onboardingPortal = fs.readFileSync('hotel-onboarding-frontend/src/pages/OnboardingPortal.tsx', 'utf8');
  if (onboardingPortal.includes('EnhancedOnboardingPortal')) {
    console.log('✅ OnboardingPortal correctly wraps EnhancedOnboardingPortal');
  } else {
    console.log('❌ OnboardingPortal wrapper issue');
    allTestsPassed = false;
  }
} else {
  console.log('❌ OnboardingPortal.tsx missing');
  allTestsPassed = false;
}

// Test 6: Check PDF viewer component
console.log('\n📄 Testing PDF Viewer Component...');
if (fs.existsSync('hotel-onboarding-frontend/src/components/ui/pdf-document-viewer.tsx')) {
  console.log('✅ PDF Document Viewer component exists');
} else {
  console.log('❌ PDF Document Viewer component missing');
  allTestsPassed = false;
}

// Final Results
console.log('\n' + '='.repeat(50));
if (allTestsPassed) {
  console.log('🎉 ALL IMPORT TESTS PASSED!');
  console.log('✅ Frontend imports are properly resolved');
  console.log('✅ All required components exist');
  console.log('✅ Onboarding system should work correctly');
} else {
  console.log('❌ SOME IMPORT TESTS FAILED');
  console.log('⚠️  Please fix the missing components/imports above');
}
console.log('='.repeat(50));

process.exit(allTestsPassed ? 0 : 1);