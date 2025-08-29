/**
 * Browser-side diagnostic tool for Direct Deposit PDF issues
 * Copy and paste this into browser console to diagnose issues
 */

// Function to check all session storage data
function checkSessionData() {
  console.log('🔍 SESSION STORAGE DIAGNOSTIC');
  console.log('=' .repeat(50));

  const keys = Object.keys(sessionStorage);
  const onboardingKeys = keys.filter(key => key.includes('onboarding'));

  console.log('All session storage keys:', keys);
  console.log('Onboarding-related keys:', onboardingKeys);

  // Check each onboarding key
  onboardingKeys.forEach(key => {
    try {
      const data = JSON.parse(sessionStorage.getItem(key));
      console.log(`\n📋 ${key}:`);
      console.log('  Keys:', Object.keys(data));
      console.log('  Raw data:', data);
    } catch (e) {
      console.log(`\n❌ ${key}: INVALID JSON`);
    }
  });

  return onboardingKeys;
}

// Function to check SSN in all possible locations
function checkSSNLocations() {
  console.log('\n🔍 SSN LOCATION CHECK');
  console.log('=' .repeat(50));

  const locations = [
    { key: 'onboarding_personal-info_data', path: 'personalInfo.ssn' },
    { key: 'onboarding_personal-info_data', path: 'ssn' },
    { key: 'onboarding_i9-form_data', path: 'personalInfo.ssn' },
    { key: 'onboarding_i9-form_data', path: 'ssn' },
    { key: 'onboarding_i9-complete_data', path: 'formData.ssn' },
    { key: 'onboarding_i9-complete_data', path: 'ssn' },
    { key: 'onboarding_direct-deposit_data', path: 'formData.ssn' },
  ];

  let foundSSN = null;
  let ssnLocation = 'NOT FOUND';

  locations.forEach(location => {
    try {
      const data = sessionStorage.getItem(location.key);
      if (data) {
        const parsed = JSON.parse(data);
        const ssn = location.path.split('.').reduce((obj, key) => obj?.[key], parsed);

        if (ssn) {
          console.log(`✅ Found SSN at ${location.key} -> ${location.path}:`, ssn.replace(/./g, '*').slice(-4));
          if (!foundSSN) {
            foundSSN = ssn;
            ssnLocation = `${location.key} -> ${location.path}`;
          }
        } else {
          console.log(`❌ No SSN at ${location.key} -> ${location.path}`);
        }
      } else {
        console.log(`❌ ${location.key} not found in session storage`);
      }
    } catch (e) {
      console.log(`❌ Error checking ${location.key}:`, e.message);
    }
  });

  console.log('\n📋 SSN SUMMARY:');
  console.log('Found SSN:', foundSSN ? foundSSN.replace(/./g, '*').slice(-4) : 'NOT FOUND');
  console.log('Location:', ssnLocation);

  return { ssn: foundSSN, location: ssnLocation };
}

// Function to check Direct Deposit data structure
function checkDirectDepositData() {
  console.log('\n🔍 DIRECT DEPOSIT DATA CHECK');
  console.log('=' .repeat(50));

  try {
    const data = sessionStorage.getItem('onboarding_direct-deposit_data');
    if (!data) {
      console.log('❌ No Direct Deposit data found');
      return null;
    }

    const parsed = JSON.parse(data);
    console.log('Direct Deposit data structure:');
    console.log(JSON.stringify(parsed, null, 2));

    const formData = parsed.formData || parsed;

    console.log('\n📋 Form Data Analysis:');
    console.log('Keys:', Object.keys(formData));

    // Check primary account
    const primaryAccount = formData.primaryAccount;
    if (primaryAccount) {
      console.log('✅ Primary Account found:');
      console.log('  Bank Name:', primaryAccount.bankName || 'MISSING');
      console.log('  Routing Number:', primaryAccount.routingNumber || 'MISSING');
      console.log('  Account Number:', primaryAccount.accountNumber ? 'PRESENT' : 'MISSING');
      console.log('  Account Type:', primaryAccount.accountType || 'MISSING');
    } else {
      console.log('❌ Primary Account NOT found');
    }

    // Check other fields
    console.log('Payment Method:', formData.paymentMethod || 'MISSING');
    console.log('Deposit Type:', formData.depositType || 'MISSING');

    return formData;
  } catch (e) {
    console.log('❌ Error parsing Direct Deposit data:', e.message);
    return null;
  }
}

// Function to simulate PDF payload creation
function simulatePdfPayload() {
  console.log('\n🔍 PDF PAYLOAD SIMULATION');
  console.log('=' .repeat(50));

  const ssnResult = checkSSNLocations();
  const formData = checkDirectDepositData();

  if (!formData) {
    console.log('❌ Cannot simulate payload - no form data');
    return null;
  }

  // Simulate extraPdfData
  const extraPdfData = {
    firstName: 'Test', // Would come from employee object
    lastName: 'User',  // Would come from employee object
    email: ssnResult.ssn ? 'test@example.com' : 'MISSING',
    ssn: ssnResult.ssn || 'MISSING'
  };

  // Simulate pdfPayload
  const pdfPayload = {
    ...formData,
    ...extraPdfData,
    signatureData: 'SIMULATED_SIGNATURE'
  };

  console.log('Simulated PDF Payload:');
  console.log(JSON.stringify(pdfPayload, null, 2));

  console.log('\n📋 Payload Analysis:');
  console.log('Has SSN:', !!pdfPayload.ssn);
  console.log('Has Primary Account:', !!pdfPayload.primaryAccount);
  console.log('Has Bank Name:', !!(pdfPayload.primaryAccount?.bankName));
  console.log('Has Routing Number:', !!(pdfPayload.primaryAccount?.routingNumber));

  return pdfPayload;
}

// Function to test actual PDF generation
async function testPdfGeneration() {
  console.log('\n🔍 TESTING PDF GENERATION');
  console.log('=' .repeat(50));

  const payload = simulatePdfPayload();
  if (!payload) {
    console.log('❌ Cannot test PDF generation - no payload');
    return;
  }

  try {
    console.log('Sending payload to backend...');

    const response = await fetch('/api/onboarding/test-employee/direct-deposit/generate-pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ employee_data: payload })
    });

    console.log('Response status:', response.status);

    if (response.ok) {
      const result = await response.json();
      console.log('✅ PDF generation successful!');
      console.log('Response:', result);

      if (result.data?.pdf) {
        console.log('📄 PDF data received, length:', result.data.pdf.length);
        console.log('💡 PDF generation is working! The issue might be in the frontend data flow.');
      } else {
        console.log('❌ No PDF data in response');
      }
    } else {
      const errorText = await response.text();
      console.log('❌ PDF generation failed:', response.status, errorText);
    }
  } catch (error) {
    console.log('❌ Error calling PDF endpoint:', error.message);
  }
}

// Main diagnostic function
function runFullDiagnostic() {
  console.log('🚀 RUNNING FULL DIAGNOSTIC');
  console.log('=' .repeat(60));

  checkSessionData();
  const ssnResult = checkSSNLocations();
  const formData = checkDirectDepositData();
  const payload = simulatePdfPayload();

  console.log('\n🎯 DIAGNOSTIC RESULTS:');
  console.log('=' .repeat(30));
  console.log('SSN Found:', ssnResult.ssn ? 'YES' : 'NO');
  console.log('Form Data Found:', formData ? 'YES' : 'NO');
  console.log('Primary Account Found:', formData?.primaryAccount ? 'YES' : 'NO');
  console.log('Payload Created:', payload ? 'YES' : 'NO');

  if (ssnResult.ssn && formData?.primaryAccount) {
    console.log('✅ All required data present - PDF should work!');
    console.log('💡 Try running: testPdfGeneration()');
  } else {
    console.log('❌ Missing required data:');
    if (!ssnResult.ssn) console.log('  - SSN not found');
    if (!formData?.primaryAccount) console.log('  - Primary account not found');
  }

  console.log('\n🔧 NEXT STEPS:');
  console.log('1. If SSN is missing, check if you completed the Personal Info step');
  console.log('2. If Primary Account is missing, check if you filled the Direct Deposit form');
  console.log('3. Run testPdfGeneration() to test the actual endpoint');
  console.log('4. Check browser console for detailed logging during PDF generation');
}

// Make functions available globally
if (typeof window !== 'undefined') {
  window.checkSessionData = checkSessionData;
  window.checkSSNLocations = checkSSNLocations;
  window.checkDirectDepositData = checkDirectDepositData;
  window.simulatePdfPayload = simulatePdfPayload;
  window.testPdfGeneration = testPdfGeneration;
  window.runFullDiagnostic = runFullDiagnostic;

  console.log('🔧 Diagnostic functions loaded! Run: runFullDiagnostic()');
}
