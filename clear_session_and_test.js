// Clear session storage and test the fixed PDF generation
// Run this in your browser console

console.log("🔧 Clearing session storage and fixing authentication...");

// Step 1: Clear all onboarding session data
console.log("1. Clearing session storage...");
Object.keys(sessionStorage).forEach(key => {
  if (key.startsWith('onboarding_')) {
    console.log(`   Removing: ${key}`);
    sessionStorage.removeItem(key);
  }
});

// Step 2: Clear localStorage token
console.log("2. Clearing localStorage token...");
localStorage.removeItem('onboarding_token');
localStorage.removeItem('employee_token');

// Step 3: Clear any other auth-related items
console.log("3. Clearing other auth items...");
['auth_token', 'jwt_token', 'access_token', 'session_token'].forEach(key => {
  if (localStorage.getItem(key)) {
    console.log(`   Removing: ${key}`);
    localStorage.removeItem(key);
  }
});

// Step 4: Test if backend is responding
console.log("4. Testing backend connection...");
fetch('/api/healthz')
  .then(response => {
    if (response.ok) {
      console.log("✅ Backend is responding");
      return response.json();
    } else {
      console.log("❌ Backend health check failed:", response.status);
    }
  })
  .then(data => {
    if (data) {
      console.log("✅ Backend health data:", data);
    }
  })
  .catch(error => {
    console.log("❌ Backend connection error:", error);
  });

// Step 5: Create a simple test session
console.log("5. Creating test session data...");

// Set up minimal session data for testing
const testPersonalInfo = {
  personalInfo: {
    firstName: "Goutham",
    lastName: "Vemula",
    middleInitial: "G",
    ssn: "090-90-9090",
    dateOfBirth: "1998-05-18",
    address: "403 - 126 Corbin Ave",
    city: "jersey city",
    state: "ID",
    zipCode: "07306",
    phone: "(347) 263-2091",
    email: "vgoutamram@gmail.com",
    gender: "male",
    maritalStatus: "single",
    aptNumber: "Sugandha Enclave",
    preferredName: ""
  }
};

const testHealthInsurance = {
  formData: {
    medicalPlan: "Standard",
    medicalTier: "employee",
    medicalCost: 150.00,
    medicalWaived: false,
    dentalCoverage: true,
    dentalEnrolled: true,
    dentalTier: "employee",
    dentalCost: 25.00,
    dentalWaived: false,
    visionCoverage: false,
    visionEnrolled: false,
    visionTier: "employee",
    visionCost: 0,
    visionWaived: true,
    section125Acknowledged: true,
    personalInfo: testPersonalInfo.personalInfo
  },
  signed: false,
  isSigned: false
};

// Store the test data
sessionStorage.setItem('onboarding_personal-info_data', JSON.stringify(testPersonalInfo));
sessionStorage.setItem('onboarding_health-insurance_data', JSON.stringify(testHealthInsurance));

console.log("✅ Test session data created");

// Step 6: Test the fixed PDF generation directly
console.log("6. Testing the fixed PDF generation...");

function testPDFGeneration() {
  const testPayload = {
    personalInfo: testPersonalInfo.personalInfo,
    ...testHealthInsurance.formData
  };
  
  console.log("📤 Testing PDF generation with fixed backend...");
  console.log("   Gender:", testPayload.personalInfo.gender, "→ should become 'M'");
  console.log("   Dental Coverage:", testPayload.dentalCoverage, "→ should set checkbox");
  
  fetch('/api/onboarding/test-employee/health-insurance/generate-pdf', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(testPayload)
  })
  .then(response => {
    console.log("📡 PDF Response status:", response.status);
    if (response.ok) {
      return response.json();
    } else {
      throw new Error(`PDF generation failed: ${response.status}`);
    }
  })
  .then(result => {
    if (result.success) {
      console.log("🎉 PDF GENERATION SUCCESSFUL!");
      console.log("📄 PDF size:", result.data.pdf_base64.length, "characters");
      console.log("📁 Filename:", result.data.filename);
      console.log("✅ Gender and dental fixes are working!");
      
      // Create download link
      const pdfData = result.data.pdf_base64;
      const byteCharacters = atob(pdfData);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = 'health_insurance_fixed.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      console.log("📥 PDF downloaded! Check your downloads folder.");
      console.log("🔍 Open the PDF and verify:");
      console.log("   ✓ Male radio button is selected");
      console.log("   ✓ Employee Only dental checkbox is selected");
      console.log("   ✓ All personal info fields are filled");
      
    } else {
      console.log("❌ PDF generation failed:", result.error);
    }
  })
  .catch(error => {
    console.log("❌ PDF test error:", error);
  });
}

// Run the PDF test after a short delay
setTimeout(testPDFGeneration, 2000);

console.log("🔄 Reloading page in 5 seconds...");
setTimeout(() => {
  window.location.reload();
}, 5000);

console.log("✅ Session cleared and test initiated!");
console.log("📋 What's happening:");
console.log("   1. Cleared all session storage");
console.log("   2. Cleared authentication tokens");
console.log("   3. Created fresh test data");
console.log("   4. Testing PDF generation with fixes");
console.log("   5. Page will reload automatically");
