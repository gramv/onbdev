// Simple session storage clear script
// Copy and paste this into your browser console

console.log("🧹 Clearing session storage...");

// Clear all onboarding session data
let cleared = 0;
Object.keys(sessionStorage).forEach(key => {
  if (key.startsWith('onboarding_')) {
    console.log(`   ❌ Removing: ${key}`);
    sessionStorage.removeItem(key);
    cleared++;
  }
});

// Clear localStorage tokens
const tokensToRemove = ['onboarding_token', 'employee_token', 'auth_token', 'jwt_token'];
tokensToRemove.forEach(token => {
  if (localStorage.getItem(token)) {
    console.log(`   ❌ Removing token: ${token}`);
    localStorage.removeItem(token);
    cleared++;
  }
});

console.log(`✅ Cleared ${cleared} items from storage`);
console.log("🔄 Reloading page...");

// Reload the page
window.location.reload();
