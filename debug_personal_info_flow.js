// Debug script to understand personal info data flow
// Run this in browser console on the health insurance step

console.log("=== PERSONAL INFO DATA FLOW DEBUG ===");

// 1. Check what's in session storage for personal-info step
const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data');
console.log("\n1. Raw personal-info session data:");
console.log(personalInfoData);

if (personalInfoData) {
  try {
    const parsed = JSON.parse(personalInfoData);
    console.log("\n2. Parsed personal-info data structure:");
    console.log(parsed);
    
    console.log("\n3. Personal info object:");
    console.log(parsed.personalInfo);
    
    if (parsed.personalInfo) {
      console.log("\n4. Personal info fields:");
      Object.keys(parsed.personalInfo).forEach(key => {
        console.log(`  ${key}: ${parsed.personalInfo[key]}`);
      });
    }
  } catch (e) {
    console.error("Failed to parse personal info data:", e);
  }
}

// 2. Check what's in session storage for health-insurance step
const healthInsuranceData = sessionStorage.getItem('onboarding_health-insurance_data');
console.log("\n5. Raw health-insurance session data:");
console.log(healthInsuranceData);

if (healthInsuranceData) {
  try {
    const parsed = JSON.parse(healthInsuranceData);
    console.log("\n6. Parsed health-insurance data structure:");
    console.log(parsed);
    
    if (parsed.personalInfo) {
      console.log("\n7. Health insurance personal info:");
      console.log(parsed.personalInfo);
    }
  } catch (e) {
    console.error("Failed to parse health insurance data:", e);
  }
}

// 3. Check what React state might have
console.log("\n8. Checking React DevTools (if available):");
if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
  console.log("React DevTools detected - check Components tab for HealthInsuranceStep state");
} else {
  console.log("React DevTools not available");
}

// 4. Field name mapping analysis
console.log("\n9. Field name analysis:");
console.log("Frontend PersonalInformationData interface uses:");
console.log("  firstName, lastName, middleInitial, dateOfBirth, ssn, phone, email");
console.log("  address, aptNumber, city, state, zipCode, gender, maritalStatus");

console.log("\nBackend health_insurance_overlay.py expects:");
console.log("  firstName/first_name, lastName/last_name, middleInitial/middle_initial");
console.log("  dateOfBirth/date_of_birth, ssn, phone/phoneNumber, email/emailAddress");
console.log("  address, city, state, zip/zipCode/zip_code, gender");

console.log("\n=== END DEBUG ===");
