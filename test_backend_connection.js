// Test backend connection and health insurance endpoint
// Run this in browser console

async function testBackendConnection() {
  console.log("=== TESTING BACKEND CONNECTION ===");
  
  try {
    // Test 1: Check if backend is responding
    console.log("\n1. Testing backend health check...");
    const healthResponse = await fetch('/api/health', {
      method: 'GET'
    });
    
    if (healthResponse.ok) {
      console.log("✅ Backend is responding");
    } else {
      console.log("❌ Backend health check failed:", healthResponse.status);
    }
    
    // Test 2: Check health insurance endpoint with minimal data
    console.log("\n2. Testing health insurance endpoint...");
    const testPayload = {
      personalInfo: {
        firstName: "Test",
        lastName: "User", 
        gender: "male",
        ssn: "123-45-6789"
      },
      dentalCoverage: true,
      dentalEnrolled: true,
      dentalTier: "employee",
      dentalWaived: false,
      section125Acknowledged: true
    };
    
    console.log("📤 Sending test payload:", testPayload);
    
    const pdfResponse = await fetch('/api/generate-health-insurance-pdf/test-employee', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload)
    });
    
    console.log("📡 Response status:", pdfResponse.status);
    console.log("📡 Response headers:", Object.fromEntries(pdfResponse.headers.entries()));
    
    if (pdfResponse.ok) {
      const result = await pdfResponse.json();
      console.log("✅ Health insurance endpoint responding");
      console.log("📄 Response:", result);
      
      if (result.success) {
        console.log("🎉 PDF generation successful!");
        console.log("💡 Now check your backend console/logs for detailed processing info");
        console.log("   Look for lines starting with:");
        console.log("   - '===================================================='");
        console.log("   - 'HEALTH INSURANCE PDF GENERATION STARTED'");
        console.log("   - 'Gender Processing:'");
        console.log("   - 'Dental coverage data received:'");
      } else {
        console.log("❌ PDF generation failed:", result.message);
      }
    } else {
      const errorText = await pdfResponse.text();
      console.log("❌ Health insurance endpoint failed");
      console.log("Error response:", errorText);
    }
    
  } catch (error) {
    console.error("❌ Backend connection test failed:", error);
    console.log("\n🔧 Possible issues:");
    console.log("   - Backend server not running");
    console.log("   - Wrong backend URL/port");
    console.log("   - CORS issues");
    console.log("   - Network connectivity problems");
  }
}

// Test with actual session data
async function testWithSessionData() {
  console.log("\n=== TESTING WITH ACTUAL SESSION DATA ===");
  
  const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data');
  const healthData = sessionStorage.getItem('onboarding_health-insurance_data');
  
  if (!personalInfoData || !healthData) {
    console.log("❌ No session data found. Complete the forms first.");
    return;
  }
  
  try {
    const personalInfo = JSON.parse(personalInfoData);
    const healthInsurance = JSON.parse(healthData);
    
    const payload = {
      ...healthInsurance.formData,
      personalInfo: personalInfo.personalInfo,
      section125Acknowledged: true
    };
    
    console.log("📤 Sending actual session data...");
    console.log("Personal info gender:", payload.personalInfo?.gender);
    console.log("Dental coverage:", payload.dentalCoverage);
    console.log("Dental enrolled:", payload.dentalEnrolled);
    
    const response = await fetch('/api/generate-health-insurance-pdf/test-employee', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log("✅ Session data test successful!");
      console.log("📄 Check backend logs for processing details");
    } else {
      console.log("❌ Session data test failed:", response.status);
    }
    
  } catch (error) {
    console.error("❌ Session data test error:", error);
  }
}

// Check what backend URL is being used
function checkBackendUrl() {
  console.log("\n=== BACKEND URL CHECK ===");
  console.log("Current origin:", window.location.origin);
  console.log("Expected backend URL:", window.location.origin + '/api/');
  
  // Check if there's any API configuration
  if (window.API_BASE_URL) {
    console.log("API_BASE_URL configured:", window.API_BASE_URL);
  }
}

// Run all tests
checkBackendUrl();
testBackendConnection();

// Also provide manual test function
console.log("\n🧪 Available test functions:");
console.log("  - testBackendConnection() - Test basic backend connectivity");
console.log("  - testWithSessionData() - Test with your actual form data");
console.log("  - checkBackendUrl() - Check backend URL configuration");
