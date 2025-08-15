#!/usr/bin/env node

/**
 * Test script to verify frontend component imports and exports
 * This simulates what the frontend bundler would do
 */

const fs = require('fs');
const path = require('path');

function checkFileExists(filePath) {
  return fs.existsSync(filePath);
}

function readFileContent(filePath) {
  if (!checkFileExists(filePath)) {
    return null;
  }
  return fs.readFileSync(filePath, 'utf8');
}

function checkExports(filePath, expectedExports) {
  const content = readFileContent(filePath);
  if (!content) {
    return { exists: false, exports: [] };
  }

  const foundExports = [];
  
  // Check for named exports
  expectedExports.forEach(exportName => {
    if (content.includes(`export function ${exportName}`) || 
        content.includes(`export const ${exportName}`) ||
        content.includes(`export { ${exportName} }`)) {
      foundExports.push({ name: exportName, type: 'named' });
    }
  });

  // Check for default export
  if (content.includes('export default')) {
    foundExports.push({ name: 'default', type: 'default' });
  }

  return { exists: true, exports: foundExports, content: content.substring(0, 500) };
}

function checkImports(filePath, expectedImports) {
  const content = readFileContent(filePath);
  if (!content) {
    return { exists: false, imports: [] };
  }

  const foundImports = [];
  
  expectedImports.forEach(imp => {
    const { name, from, type } = imp;
    let importPattern;
    
    if (type === 'named') {
      importPattern = new RegExp(`import\\s*{[^}]*\\b${name}\\b[^}]*}\\s*from\\s*['"]${from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}['"]`);
    } else if (type === 'default') {
      importPattern = new RegExp(`import\\s+${name}\\s+from\\s*['"]${from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}['"]`);
    } else if (type === 'hook') {
      importPattern = new RegExp(`import\\s*{[^}]*\\b${name}\\b[^}]*}\\s*from\\s*['"]${from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}['"]`);
    }
    
    if (importPattern && importPattern.test(content)) {
      foundImports.push({ name, from, type, found: true });
    } else {
      foundImports.push({ name, from, type, found: false });
    }
  });

  return { exists: true, imports: foundImports };
}

console.log('🔍 Testing Frontend Component Imports and Exports');
console.log('='.repeat(60));

// Test component exports
const components = [
  {
    path: 'hotel-onboarding-frontend/src/components/dashboard/ApplicationsTab.tsx',
    expectedExports: ['ApplicationsTab']
  },
  {
    path: 'hotel-onboarding-frontend/src/components/dashboard/EmployeesTab.tsx',
    expectedExports: ['EmployeesTab']
  },
  {
    path: 'hotel-onboarding-frontend/src/components/dashboard/AnalyticsTab.tsx',
    expectedExports: ['AnalyticsTab']
  }
];

console.log('\n📤 Testing Component Exports:');
let exportTests = 0;
let exportPassed = 0;

components.forEach(comp => {
  const result = checkExports(comp.path, comp.expectedExports);
  exportTests++;
  
  if (result.exists) {
    const hasExpectedExports = comp.expectedExports.every(exp => 
      result.exports.some(found => found.name === exp)
    );
    
    if (hasExpectedExports) {
      console.log(`✅ ${path.basename(comp.path)}: Exports ${comp.expectedExports.join(', ')}`);
      exportPassed++;
    } else {
      console.log(`❌ ${path.basename(comp.path)}: Missing exports`);
      console.log(`   Expected: ${comp.expectedExports.join(', ')}`);
      console.log(`   Found: ${result.exports.map(e => e.name).join(', ')}`);
    }
  } else {
    console.log(`❌ ${path.basename(comp.path)}: File not found`);
  }
});

// Test imports in consuming components
const importTests = [
  {
    path: 'hotel-onboarding-frontend/src/pages/HRDashboard.tsx',
    expectedImports: [
      { name: 'ApplicationsTab', from: '@/components/dashboard/ApplicationsTab', type: 'named' },
      { name: 'EmployeesTab', from: '@/components/dashboard/EmployeesTab', type: 'named' },
      { name: 'AnalyticsTab', from: '@/components/dashboard/AnalyticsTab', type: 'named' }
    ]
  },
  {
    path: 'hotel-onboarding-frontend/src/pages/ManagerDashboard.tsx',
    expectedImports: [
      { name: 'ApplicationsTab', from: '@/components/dashboard/ApplicationsTab', type: 'named' },
      { name: 'EmployeesTab', from: '@/components/dashboard/EmployeesTab', type: 'named' },
      { name: 'AnalyticsTab', from: '@/components/dashboard/AnalyticsTab', type: 'named' },
      { name: 'useAuth', from: '@/contexts/AuthContext', type: 'hook' }
    ]
  },
  {
    path: 'hotel-onboarding-frontend/src/components/dashboard/EmployeesTab.tsx',
    expectedImports: [
      { name: 'useAuth', from: '@/contexts/AuthContext', type: 'hook' }
    ]
  }
];

console.log('\n📥 Testing Component Imports:');
let importTestCount = 0;
let importPassed = 0;

importTests.forEach(test => {
  const result = checkImports(test.path, test.expectedImports);
  importTestCount++;
  
  if (result.exists) {
    const allImportsFound = result.imports.every(imp => imp.found);
    
    if (allImportsFound) {
      console.log(`✅ ${path.basename(test.path)}: All imports correct`);
      importPassed++;
    } else {
      console.log(`❌ ${path.basename(test.path)}: Import issues`);
      result.imports.forEach(imp => {
        const status = imp.found ? '✅' : '❌';
        console.log(`   ${status} ${imp.type}: ${imp.name} from ${imp.from}`);
      });
    }
  } else {
    console.log(`❌ ${path.basename(test.path)}: File not found`);
  }
});

// Test AuthContext exports
console.log('\n🔐 Testing AuthContext:');
const authResult = checkExports('hotel-onboarding-frontend/src/contexts/AuthContext.tsx', ['useAuth', 'AuthProvider']);
if (authResult.exists) {
  const hasUseAuth = authResult.exports.some(e => e.name === 'useAuth');
  const hasAuthProvider = authResult.exports.some(e => e.name === 'AuthProvider');
  
  if (hasUseAuth && hasAuthProvider) {
    console.log('✅ AuthContext: Exports useAuth hook and AuthProvider');
  } else {
    console.log('❌ AuthContext: Missing required exports');
    console.log(`   useAuth: ${hasUseAuth ? '✅' : '❌'}`);
    console.log(`   AuthProvider: ${hasAuthProvider ? '✅' : '❌'}`);
  }
} else {
  console.log('❌ AuthContext: File not found');
}

// Summary
console.log('\n' + '='.repeat(60));
console.log('📋 TEST SUMMARY');
console.log('='.repeat(60));

const totalTests = exportTests + importTestCount + 1; // +1 for AuthContext
const totalPassed = exportPassed + importPassed + (authResult.exists ? 1 : 0);

console.log(`Component Exports: ${exportPassed}/${exportTests} passed`);
console.log(`Component Imports: ${importPassed}/${importTestCount} passed`);
console.log(`AuthContext: ${authResult.exists ? '✅' : '❌'}`);
console.log(`\nOverall: ${totalPassed}/${totalTests} tests passed`);

if (totalPassed === totalTests) {
  console.log('\n🎉 ALL IMPORT/EXPORT TESTS PASSED!');
  console.log('Frontend components should load without import errors.');
} else {
  console.log(`\n⚠️ ${totalTests - totalPassed} tests failed.`);
  console.log('Frontend may have import/export issues.');
}

process.exit(totalPassed === totalTests ? 0 : 1);