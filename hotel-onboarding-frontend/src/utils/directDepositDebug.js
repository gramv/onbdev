/**
 * Direct Deposit PDF Generation Debug Utility
 * Run this in the browser console to diagnose PDF generation issues
 */

export const debugDirectDepositData = () => {
  console.log('=== DIRECT DEPOSIT PDF DEBUG ===');

  // Check session storage for relevant data
  const directDepositData = sessionStorage.getItem('onboarding_direct-deposit_data');
  const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data');
  const i9FormData = sessionStorage.getItem('onboarding_i9-form_data');
  const i9CompleteData = sessionStorage.getItem('onboarding_i9-complete_data');

  console.log('Session Storage Data:');
  console.log('Direct Deposit:', directDepositData ? JSON.parse(directDepositData) : 'NOT FOUND');
  console.log('Personal Info:', personalInfoData ? JSON.parse(personalInfoData) : 'NOT FOUND');
  console.log('I9 Form:', i9FormData ? JSON.parse(i9FormData) : 'NOT FOUND');
  console.log('I9 Complete:', i9CompleteData ? JSON.parse(i9CompleteData) : 'NOT FOUND');

  // Check for SSN in different locations
  let foundSSN = null;
  let ssnSource = 'NOT FOUND';

  if (personalInfoData) {
    const parsed = JSON.parse(personalInfoData);
    if (parsed?.personalInfo?.ssn) {
      foundSSN = parsed.personalInfo.ssn;
      ssnSource = 'Personal Info (personalInfo.ssn)';
    } else if (parsed?.ssn) {
      foundSSN = parsed.ssn;
      ssnSource = 'Personal Info (ssn)';
    }
  }

  if (!foundSSN && i9CompleteData) {
    const parsed = JSON.parse(i9CompleteData);
    if (parsed?.formData?.ssn) {
      foundSSN = parsed.formData.ssn;
      ssnSource = 'I9 Complete (formData.ssn)';
    } else if (parsed?.ssn) {
      foundSSN = parsed.ssn;
      ssnSource = 'I9 Complete (ssn)';
    }
  }

  console.log('SSN Check:');
  console.log('Found SSN:', foundSSN || 'NOT FOUND');
  console.log('SSN Source:', ssnSource);

  // Check primary account data structure
  if (directDepositData) {
    const parsed = JSON.parse(directDepositData);
    const formData = parsed?.formData || parsed;

    console.log('Primary Account Check:');
    console.log('Form Data Keys:', Object.keys(formData));
    console.log('Primary Account:', formData?.primaryAccount || 'NOT FOUND');
    console.log('Deposit Type:', formData?.depositType || 'NOT FOUND');
  }

  return {
    directDepositData: directDepositData ? JSON.parse(directDepositData) : null,
    personalInfoData: personalInfoData ? JSON.parse(personalInfoData) : null,
    i9FormData: i9FormData ? JSON.parse(i9FormData) : null,
    i9CompleteData: i9CompleteData ? JSON.parse(i9CompleteData) : null,
    foundSSN,
    ssnSource
  };
};

// Enhanced debug function to test PDF generation
async function testPdfGeneration() {
  console.log('=== TESTING PDF GENERATION ===');

  const debugData = debugDirectDepositData();

  if (!debugData.directDepositData) {
    console.error('❌ No Direct Deposit data found in session storage');
    return;
  }

  // Extract form data
  const formData = debugData.directDepositData.formData || debugData.directDepositData;

  // Build the payload that would be sent to backend
  const testPayload = {
    employee_data: {
      ...formData,
      firstName: debugData.personalInfoData?.personalInfo?.firstName || 'Test',
      lastName: debugData.personalInfoData?.personalInfo?.lastName || 'User',
      email: debugData.personalInfoData?.personalInfo?.email || 'test@example.com',
      ssn: debugData.foundSSN || '123-45-6789'
    }
  };

  console.log('Payload to be sent to backend:');
  console.log(JSON.stringify(testPayload, null, 2));

  // Save for backend analysis
  localStorage.setItem('DEBUG_PDF_TEST_PAYLOAD', JSON.stringify(testPayload));

  try {
    // Try to call the backend endpoint
    const apiUrl = import.meta.env.VITE_API_URL || '/api';
    const response = await fetch(`${apiUrl}/onboarding/test-employee/direct-deposit/generate-pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload)
    });

    console.log('Response status:', response.status);

    if (response.ok) {
      const result = await response.json();
      console.log('✅ PDF generation successful!');
      console.log('Response:', result);

      if (result.data?.pdf) {
        console.log('📄 PDF data received, length:', result.data.pdf.length);

        // Save PDF data for analysis
        localStorage.setItem('DEBUG_LAST_GENERATED_PDF', result.data.pdf);

        // Try to decode and analyze
        try {
          const pdfBytes = Uint8Array.from(atob(result.data.pdf), c => c.charCodeAt(0));
          const header = String.fromCharCode(...pdfBytes.slice(0, 4));
          console.log('PDF header:', header);
          console.log('Is valid PDF:', header === '%PDF');

          // Check if PDF has content by looking for some text
          const pdfText = new TextDecoder().decode(pdfBytes);
          const hasEmployeeName = pdfText.includes('employee_name') || pdfText.includes('John') || pdfText.includes('Test');
          const hasSSN = pdfText.includes('ssn') || pdfText.includes('123-45') || pdfText.includes('6789');
          const hasBankInfo = pdfText.includes('bank') || pdfText.includes('routing') || pdfText.includes('account');

          console.log('PDF Content Check:');
          console.log('  - Contains employee name references:', hasEmployeeName);
          console.log('  - Contains SSN references:', hasSSN);
          console.log('  - Contains bank references:', hasBankInfo);

          if (hasEmployeeName || hasSSN || hasBankInfo) {
            console.log('✅ PDF appears to have form data!');
          } else {
            console.log('⚠️  PDF might be missing form data or fields are not visible');
          }

        } catch (decodeError) {
          console.log('❌ Error analyzing PDF content:', decodeError.message);
        }

        // You can open this PDF data in a new tab if needed
        // const pdfBlob = new Blob([Uint8Array.from(atob(result.data.pdf), c => c.charCodeAt(0))], {type: 'application/pdf'});
        // const pdfUrl = URL.createObjectURL(pdfBlob);
        // window.open(pdfUrl);
      } else {
        console.error('❌ No PDF data in response');
      }
    } else {
      const errorText = await response.text();
      console.error('❌ PDF generation failed:', response.status, errorText);
    }
  } catch (error) {
    console.error('❌ Error calling PDF endpoint:', error);
  }
}

// Make functions available globally for console use
if (typeof window !== 'undefined') {
  window.debugDirectDepositData = debugDirectDepositData;
  window.testPdfGeneration = testPdfGeneration;
}
