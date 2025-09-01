// Test script to verify backend health insurance processing
// Run this in browser console after completing the health insurance form

async function testBackendProcessing() {
  console.log("=== TESTING BACKEND HEALTH INSURANCE PROCESSING ===");
  
  // Get current session data
  const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data');
  const healthData = sessionStorage.getItem('onboarding_health-insurance_data');
  
  if (!personalInfoData || !healthData) {
    console.log("❌ Missing session data. Complete the forms first.");
    return;
  }
  
  try {
    const personalInfo = JSON.parse(personalInfoData);
    const healthInsurance = JSON.parse(healthData);
    
    // Build test payload exactly like the frontend does
    const testPayload = {
      ...healthInsurance.formData,
      personalInfo: personalInfo.personalInfo,
      section125Acknowledged: true
    };
    
    console.log("\n📤 Sending test payload to backend:");
    console.log("Personal Info:", {
      firstName: testPayload.personalInfo?.firstName,
      lastName: testPayload.personalInfo?.lastName,
      gender: testPayload.personalInfo?.gender,
      ssn: testPayload.personalInfo?.ssn ? '***masked***' : 'missing'
    });
    console.log("Dental Fields:", {
      dentalCoverage: testPayload.dentalCoverage,
      dentalEnrolled: testPayload.dentalEnrolled,
      dentalTier: testPayload.dentalTier,
      dentalWaived: testPayload.dentalWaived
    });
    
    // Make API call
    console.log("\n📡 Making API call...");
    const response = await fetch('/api/generate-health-insurance-pdf/test-employee', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload)
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log("✅ Backend processing successful!");
      console.log("📄 PDF generated:", result.data?.filename);
      console.log("\n💡 Check backend console/logs for detailed processing info:");
      console.log("   - Look for 'HEALTH INSURANCE PDF GENERATION STARTED'");
      console.log("   - Check 'Gender Processing' logs");
      console.log("   - Check 'Dental coverage data received' logs");
      console.log("   - Look for 'Gender Radio Button Setting' logs");
      console.log("   - Look for 'Dental Coverage Decision' logs");
      console.log("   - Check 'HEALTH INSURANCE PDF GENERATION COMPLETED'");
    } else {
      console.log("❌ Backend processing failed:", result.message);
      console.log("Error details:", result);
    }
    
  } catch (error) {
    console.error("❌ Test failed:", error);
  }
}

// Also provide a function to check what the backend should receive
function showExpectedBackendData() {
  console.log("\n=== EXPECTED BACKEND DATA ===");
  
  const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data');
  const healthData = sessionStorage.getItem('onboarding_health-insurance_data');
  
  if (personalInfoData && healthData) {
    try {
      const personalInfo = JSON.parse(personalInfoData);
      const healthInsurance = JSON.parse(healthData);
      
      console.log("\n📋 Backend should receive:");
      console.log("personalInfo.gender:", personalInfo.personalInfo?.gender);
      console.log("dentalCoverage:", healthInsurance.formData?.dentalCoverage);
      console.log("dentalEnrolled:", healthInsurance.formData?.dentalEnrolled);
      console.log("dentalTier:", healthInsurance.formData?.dentalTier);
      console.log("dentalWaived:", healthInsurance.formData?.dentalWaived);
      
      console.log("\n🔄 Backend should convert:");
      console.log(`gender: "${personalInfo.personalInfo?.gender}" → "${personalInfo.personalInfo?.gender === 'male' ? 'M' : personalInfo.personalInfo?.gender === 'female' ? 'F' : '?'}"`);
      
      const hasDental = healthInsurance.formData?.dentalCoverage || healthInsurance.formData?.dentalEnrolled;
      const isWaived = healthInsurance.formData?.dentalWaived;
      console.log(`dental: ${hasDental ? 'enrolled' : 'not enrolled'}, waived: ${isWaived ? 'yes' : 'no'}`);
      console.log(`dental action: ${isWaived || !hasDental ? 'decline checkbox' : `tier checkbox (${healthInsurance.formData?.dentalTier})`}`);
      
    } catch (e) {
      console.error("Failed to parse session data:", e);
    }
  }
}

// Run the tests
showExpectedBackendData();
console.log("\n🧪 Run testBackendProcessing() to test the backend API");

// Auto-run the test
testBackendProcessing();
