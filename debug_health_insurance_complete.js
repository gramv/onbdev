// Complete debug script for health insurance issues
// Run this in browser console on the health insurance step

console.log("=== HEALTH INSURANCE COMPLETE DEBUG ===");

// 1. Check personal info in session storage
function checkPersonalInfo() {
  console.log("\n1. PERSONAL INFO CHECK:");
  
  const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data');
  if (personalInfoData) {
    try {
      const parsed = JSON.parse(personalInfoData);
      console.log("✅ Personal info session data found");
      console.log("Structure:", parsed);
      
      if (parsed.personalInfo) {
        console.log("\n📋 Personal info fields:");
        Object.keys(parsed.personalInfo).forEach(key => {
          const value = parsed.personalInfo[key];
          if (key === 'ssn' && value) {
            console.log(`  ${key}: ${value.substring(0, 3)}****`);
          } else {
            console.log(`  ${key}: ${value || 'EMPTY'}`);
          }
        });
        
        // Check specifically for gender
        const gender = parsed.personalInfo.gender;
        console.log(`\n🚻 Gender field: '${gender}' (${typeof gender})`);
        if (!gender) {
          console.log("❌ Gender is missing from personal info!");
        }
      } else {
        console.log("❌ No personalInfo object found in session data");
      }
    } catch (e) {
      console.error("❌ Failed to parse personal info:", e);
    }
  } else {
    console.log("❌ No personal info session data found");
  }
}

// 2. Check health insurance form data
function checkHealthInsuranceData() {
  console.log("\n2. HEALTH INSURANCE DATA CHECK:");
  
  const healthData = sessionStorage.getItem('onboarding_health-insurance_data');
  if (healthData) {
    try {
      const parsed = JSON.parse(healthData);
      console.log("✅ Health insurance session data found");
      console.log("Structure:", parsed);
      
      if (parsed.formData) {
        console.log("\n🏥 Health insurance form fields:");
        const formData = parsed.formData;
        
        // Check dental fields specifically
        console.log("Dental Coverage Fields:");
        console.log(`  dentalCoverage: ${formData.dentalCoverage} (${typeof formData.dentalCoverage})`);
        console.log(`  dentalEnrolled: ${formData.dentalEnrolled} (${typeof formData.dentalEnrolled})`);
        console.log(`  dentalTier: ${formData.dentalTier} (${typeof formData.dentalTier})`);
        console.log(`  dentalWaived: ${formData.dentalWaived} (${typeof formData.dentalWaived})`);
        
        // Check if dental is properly selected
        const hasDental = formData.dentalCoverage || formData.dentalEnrolled;
        console.log(`\n🦷 Dental Status: ${hasDental ? 'ENROLLED' : 'NOT ENROLLED'}`);
        if (!hasDental) {
          console.log("❌ Dental coverage not selected!");
        }
      }
      
      if (parsed.personalInfo) {
        console.log("\n👤 Personal info in health insurance data:");
        console.log(parsed.personalInfo);
      }
    } catch (e) {
      console.error("❌ Failed to parse health insurance data:", e);
    }
  } else {
    console.log("❌ No health insurance session data found");
  }
}

// 3. Test PDF generation with current data
function testPdfGeneration() {
  console.log("\n3. PDF GENERATION TEST:");
  
  // Get current form data
  const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data');
  const healthData = sessionStorage.getItem('onboarding_health-insurance_data');
  
  if (!personalInfoData || !healthData) {
    console.log("❌ Missing required session data for PDF generation");
    return;
  }
  
  try {
    const personalInfo = JSON.parse(personalInfoData);
    const healthInsurance = JSON.parse(healthData);
    
    // Build test payload
    const testPayload = {
      ...healthInsurance.formData,
      personalInfo: personalInfo.personalInfo,
      section125Acknowledged: true
    };
    
    console.log("🧪 Test payload for PDF generation:");
    console.log("Personal Info:", testPayload.personalInfo);
    console.log("Dental Fields:", {
      dentalCoverage: testPayload.dentalCoverage,
      dentalEnrolled: testPayload.dentalEnrolled,
      dentalTier: testPayload.dentalTier,
      dentalWaived: testPayload.dentalWaived
    });
    
    // Test the actual API call
    console.log("\n📡 Making test API call...");
    fetch('/api/generate-health-insurance-pdf/test-employee', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log("✅ PDF generation successful!");
        console.log("Check backend logs for detailed processing info");
      } else {
        console.log("❌ PDF generation failed:", data.message);
      }
    })
    .catch(error => {
      console.error("❌ API call failed:", error);
    });
    
  } catch (e) {
    console.error("❌ Failed to build test payload:", e);
  }
}

// 4. Check React component state (if available)
function checkReactState() {
  console.log("\n4. REACT STATE CHECK:");
  
  // Try to access React DevTools
  if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
    console.log("✅ React DevTools available");
    console.log("💡 Check the Components tab for HealthInsuranceStep state");
    console.log("   Look for 'personalInfo' and 'formData' in the component state");
  } else {
    console.log("❌ React DevTools not available");
    console.log("💡 Install React DevTools browser extension for component state inspection");
  }
}

// 5. Provide fix recommendations
function provideFixes() {
  console.log("\n5. FIX RECOMMENDATIONS:");
  
  const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data');
  const healthData = sessionStorage.getItem('onboarding_health-insurance_data');
  
  let hasPersonalInfo = false;
  let hasGender = false;
  let hasDental = false;
  
  if (personalInfoData) {
    try {
      const parsed = JSON.parse(personalInfoData);
      hasPersonalInfo = !!(parsed.personalInfo && Object.keys(parsed.personalInfo).length > 0);
      hasGender = !!(parsed.personalInfo && parsed.personalInfo.gender);
    } catch (e) {}
  }
  
  if (healthData) {
    try {
      const parsed = JSON.parse(healthData);
      hasDental = !!(parsed.formData && (parsed.formData.dentalCoverage || parsed.formData.dentalEnrolled));
    } catch (e) {}
  }
  
  console.log("\n📋 Issue Checklist:");
  console.log(`✅ Personal info exists: ${hasPersonalInfo}`);
  console.log(`✅ Gender field exists: ${hasGender}`);
  console.log(`✅ Dental coverage selected: ${hasDental}`);
  
  if (!hasPersonalInfo) {
    console.log("\n🔧 FIX: Complete the Personal Info step first");
    console.log("   - Navigate back to personal-info step");
    console.log("   - Fill in all required fields including gender");
    console.log("   - Save and continue");
  }
  
  if (!hasGender) {
    console.log("\n🔧 FIX: Gender field missing");
    console.log("   - Go back to personal-info step");
    console.log("   - Ensure gender is selected");
    console.log("   - Save the form");
  }
  
  if (!hasDental) {
    console.log("\n🔧 FIX: Dental coverage not selected");
    console.log("   - In health insurance form, select dental coverage");
    console.log("   - Choose a dental tier (employee, family, etc.)");
    console.log("   - Save the form");
  }
  
  console.log("\n🧪 TESTING:");
  console.log("   - After making fixes, run: testPdfGeneration()");
  console.log("   - Check browser console for detailed logs");
  console.log("   - Check backend logs for processing details");
}

// Run all checks
checkPersonalInfo();
checkHealthInsuranceData();
checkReactState();
provideFixes();

console.log("\n🔧 AVAILABLE FUNCTIONS:");
console.log("  - checkPersonalInfo() - Check personal info session data");
console.log("  - checkHealthInsuranceData() - Check health insurance form data");
console.log("  - testPdfGeneration() - Test PDF generation with current data");
console.log("  - checkReactState() - Check React component state");
console.log("  - provideFixes() - Get fix recommendations");

console.log("\n=== DEBUG COMPLETE ===");
