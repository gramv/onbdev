/**
 * CAPTURE FRONTEND DATA TOOL
 * Copy this entire script and paste it into your browser console
 * Then run: captureAndTestPdfData()
 */

function captureFrontendData() {
  console.log('🔍 CAPTURING FRONTEND DATA FOR PDF GENERATION');
  console.log('=' .repeat(60));

  // 1. Capture session storage data
  console.log('\n1️⃣ SESSION STORAGE DATA:');
  const sessionKeys = Object.keys(sessionStorage).filter(k => k.includes('onboarding'));
  sessionKeys.forEach(key => {
    try {
      const data = JSON.parse(sessionStorage.getItem(key));
      console.log(`📋 ${key}:`);
      console.log(`   Keys: ${Object.keys(data).join(', ')}`);
      console.log(`   Raw:`, data);
    } catch (e) {
      console.log(`❌ ${key}: INVALID JSON`);
    }
  });

  // 2. Check for debug payload
  console.log('\n2️⃣ DEBUG PAYLOAD FROM LOCALSTORAGE:');
  const debugPayload = localStorage.getItem('DEBUG_LAST_PDF_PAYLOAD');
  if (debugPayload) {
    const payload = JSON.parse(debugPayload);
    console.log('✅ Found debug payload:');
    console.log('Keys:', Object.keys(payload));
    console.log('Has SSN:', !!payload.ssn);
    console.log('Has primaryAccount:', !!payload.primaryAccount);
    console.log('Full payload:', payload);
    return payload;
  } else {
    console.log('❌ No debug payload found - try generating a PDF first');
    return null;
  }
}

async function testCapturedData() {
  const payload = captureFrontendData();

  if (!payload) {
    console.log('❌ No payload to test');
    return;
  }

  console.log('\n3️⃣ TESTING PAYLOAD WITH BACKEND:');

  try {
    const response = await fetch('/api/onboarding/test-employee/direct-deposit/generate-pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ employee_data: payload })
    });

    console.log(`Response status: ${response.status}`);

    if (response.ok) {
      const result = await response.json();
      console.log('✅ BACKEND RESPONSE:');
      console.log('Has PDF data:', !!result.data?.pdf);
      if (result.data?.pdf) {
        console.log('PDF size:', result.data.pdf.length, 'characters');
        console.log('📄 PDF generation successful!');

        // Try to decode and check if it's actually a valid PDF
        try {
          const pdfBytes = Uint8Array.from(atob(result.data.pdf), c => c.charCodeAt(0));
          console.log('PDF decoded successfully, size:', pdfBytes.length, 'bytes');

          // Check if it starts with PDF header
          const header = String.fromCharCode(...pdfBytes.slice(0, 4));
          console.log('PDF header:', header);
          if (header === '%PDF') {
            console.log('✅ Valid PDF format detected!');
          } else {
            console.log('⚠️  PDF header not detected, might be corrupted');
          }
        } catch (e) {
          console.log('❌ Error decoding PDF:', e.message);
        }

      } else {
        console.log('❌ No PDF data in response');
        console.log('Full response:', result);
      }
    } else {
      const errorText = await response.text();
      console.log('❌ BACKEND ERROR:', response.status, errorText);
    }
  } catch (error) {
    console.log('❌ NETWORK ERROR:', error.message);
  }
}

function analyzePdfTemplate() {
  console.log('\n4️⃣ ANALYZING PDF TEMPLATE:');

  // This would need to be run on the backend, but let's check what we can
  console.log('Template analysis needs to be run on backend:');
  console.log('Run: python3 diagnose_direct_deposit_issue.py');
}

function generateTestData() {
  console.log('\n5️⃣ GENERATING TEST DATA:');

  const testPayload = {
    "firstName": "Test",
    "lastName": "User",
    "email": "test@example.com",
    "ssn": "123-45-6789",
    "paymentMethod": "direct_deposit",
    "depositType": "full",
    "primaryAccount": {
      "bankName": "Test Bank",
      "routingNumber": "123456789",
      "accountNumber": "9876543210",
      "accountType": "checking",
      "depositAmount": "",
      "percentage": 100
    },
    "additionalAccounts": [],
    "voidedCheckUploaded": false,
    "bankLetterUploaded": false,
    "totalPercentage": 100,
    "authorizeDeposit": true,
    "employeeSignature": "",
    "dateOfAuth": "2025-01-27"
  };

  localStorage.setItem('DEBUG_TEST_PAYLOAD', JSON.stringify(testPayload));
  console.log('✅ Test payload saved to localStorage as DEBUG_TEST_PAYLOAD');
  console.log('Test payload:', testPayload);

  return testPayload;
}

async function testWithGeneratedData() {
  const testPayload = generateTestData();

  console.log('\n6️⃣ TESTING WITH GENERATED DATA:');

  try {
    const response = await fetch('/api/onboarding/test-employee/direct-deposit/generate-pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ employee_data: testPayload })
    });

    console.log(`Response status: ${response.status}`);

    if (response.ok) {
      const result = await response.json();
      console.log('✅ Generated data test successful!');
      console.log('Has PDF:', !!result.data?.pdf);
      if (result.data?.pdf) {
        console.log('PDF size:', result.data.pdf.length);

        // Decode and check
        try {
          const pdfBytes = Uint8Array.from(atob(result.data.pdf), c => c.charCodeAt(0));
          const header = String.fromCharCode(...pdfBytes.slice(0, 4));
          console.log('PDF header:', header);
          console.log('Valid PDF:', header === '%PDF');
        } catch (e) {
          console.log('❌ Decode error:', e.message);
        }
      }
    } else {
      const errorText = await response.text();
      console.log('❌ Error with test data:', response.status, errorText);
    }
  } catch (error) {
    console.log('❌ Network error:', error.message);
  }
}

// Main function to run all tests
async function captureAndTestPdfData() {
  console.log('🚀 COMPREHENSIVE PDF DATA CAPTURE AND TEST');
  console.log('=' .repeat(60));

  captureFrontendData();
  await testCapturedData();
  analyzePdfTemplate();
  await testWithGeneratedData();

  console.log('\n📋 SUMMARY:');
  console.log('=' .repeat(30));
  console.log('1. Check if your real data matches the test data structure');
  console.log('2. Compare SSN and primaryAccount fields');
  console.log('3. If test data works but real data doesn\'t, there\'s a data structure issue');
  console.log('4. If test data also fails, there\'s a backend issue');
  console.log('\n🔧 Next steps: Share the output above for detailed analysis');
}

// Make functions globally available
if (typeof window !== 'undefined') {
  window.captureFrontendData = captureFrontendData;
  window.testCapturedData = testCapturedData;
  window.captureAndTestPdfData = captureAndTestPdfData;
  window.generateTestData = generateTestData;
  window.testWithGeneratedData = testWithGeneratedData;

  console.log('🔧 Functions loaded! Run: captureAndTestPdfData()');
}
