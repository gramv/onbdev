#!/usr/bin/env python3
"""
Script to clean up duplicate imports added by the bash script
"""

import os
import re

# List of files to clean
files = [
    "src/pages/onboarding/I9Section1Step.tsx",
    "src/pages/onboarding/W4FormStep.tsx",
    "src/pages/onboarding/TraffickingAwarenessStep.tsx",
    "src/pages/onboarding/I9Section2Step.tsx",
    "src/pages/onboarding/I9CompleteStep.tsx",
    "src/pages/onboarding/HealthInsuranceStep.tsx",
    "src/pages/onboarding/CompanyPoliciesStep.tsx",
    "src/pages/onboarding/DirectDepositStep.tsx",
    "src/pages/onboarding/WeaponsPolicyStep.tsx"
]

def clean_duplicate_imports(filepath):
    """Remove duplicate imports from a file"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        seen_imports = set()
        cleaned_lines = []
        
        for line in lines:
            # Check if this is the API config import
            if "import { getApiUrl, getLegacyBaseUrl } from '@/config/api'" in line:
                if line.strip() not in seen_imports:
                    cleaned_lines.append(line)
                    seen_imports.add(line.strip())
                # Skip duplicate imports
            else:
                cleaned_lines.append(line)
        
        # Write back the cleaned content
        with open(filepath, 'w') as f:
            f.writelines(cleaned_lines)
        
        print(f"✓ Cleaned {filepath}")
        
    except Exception as e:
        print(f"✗ Error cleaning {filepath}: {e}")

# Process all files
print("Cleaning duplicate imports from onboarding components...")
for file in files:
    if os.path.exists(file):
        clean_duplicate_imports(file)
    else:
        print(f"⚠ File not found: {file}")

print("\nAll files have been cleaned!")