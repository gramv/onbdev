#!/bin/bash

# Script to fix API configuration in all onboarding components

echo "Fixing API configurations in onboarding components..."

# List of files to update
FILES=(
  "src/pages/onboarding/DocumentUploadEnhanced.tsx"
  "src/pages/onboarding/I9Section1Step.tsx"
  "src/pages/onboarding/W4FormStep.tsx"
  "src/pages/onboarding/TraffickingAwarenessStep.tsx"
  "src/pages/onboarding/I9Section2Step.tsx"
  "src/pages/onboarding/I9CompleteStep.tsx"
  "src/pages/onboarding/HealthInsuranceStep.tsx"
  "src/pages/onboarding/CompanyPoliciesStep.tsx"
  "src/pages/onboarding/DirectDepositStep.tsx"
  "src/pages/onboarding/WeaponsPolicyStep.tsx"
)

for FILE in "${FILES[@]}"; do
  echo "Processing $FILE..."
  
  # Check if file exists
  if [ ! -f "$FILE" ]; then
    echo "  File not found, skipping..."
    continue
  fi
  
  # Check if import already exists
  if grep -q "import { getApiUrl, getLegacyBaseUrl } from '@/config/api'" "$FILE"; then
    echo "  Import already exists, skipping import addition..."
  else
    # Add import after the first import statement
    sed -i '' "/^import/a\\
import { getApiUrl, getLegacyBaseUrl } from '@/config/api'
" "$FILE"
  fi
  
  # Replace inline VITE_API_URL usages with getLegacyBaseUrl()
  # Pattern 1: const apiUrl = import.meta.env.VITE_API_URL || ''
  sed -i '' "s/const apiUrl = import\.meta\.env\.VITE_API_URL || ''/const apiUrl = getLegacyBaseUrl()/g" "$FILE"
  
  # Pattern 2: const apiUrl = import.meta.env.VITE_API_URL || '\/api'
  sed -i '' "s/const apiUrl = import\.meta\.env\.VITE_API_URL || '\/api'/const apiUrl = getLegacyBaseUrl()/g" "$FILE"
  
  # Pattern 3: Direct usage in template literals
  sed -i '' "s/\${import\.meta\.env\.VITE_API_URL || ''}/\${getLegacyBaseUrl()}/g" "$FILE"
  sed -i '' "s/\${import\.meta\.env\.VITE_API_URL || '\/api'}/\${getLegacyBaseUrl()}/g" "$FILE"
  
  echo "  Done!"
done

echo "All files have been updated!"