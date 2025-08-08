#!/usr/bin/env python3
"""
Script to fix all remaining hardcoded API URLs in the frontend
"""

import os
import re
from pathlib import Path

def fix_hardcoded_urls(file_path):
    """Replace hardcoded URLs with relative /api paths"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Replace http://127.0.0.1:8000 and http://localhost:8000 with /api
    patterns = [
        (r'http://127\.0\.0\.1:8000', '/api'),
        (r'http://localhost:8000', '/api'),
        (r'https://127\.0\.0\.1:8000', '/api'),
        (r'https://localhost:8000', '/api'),
        # Also handle axios calls with explicit URLs
        (r'axios\.(get|post|put|delete|patch)\s*\(\s*[\'"`]http://127\.0\.0\.1:8000', r'api.apiClient.\1(\'/api'),
        (r'axios\.(get|post|put|delete|patch)\s*\(\s*[\'"`]http://localhost:8000', r'api.apiClient.\1(\'/api'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Main function to process all files"""
    
    frontend_dir = Path('/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-frontend')
    
    # Files to process (based on grep results)
    files_to_fix = [
        'src/services/documentService.ts',
        'src/pages/onboarding/WeaponsPolicyStep.tsx',
        'src/pages/onboarding/W4FormStep.tsx',
        'src/pages/onboarding/PersonalInfoStep.tsx',
        'src/pages/onboarding/I9Section2Step.tsx',
        'src/pages/onboarding/I9Section1Step.tsx',
        'src/pages/onboarding/I9CompleteStep.tsx',
        'src/pages/onboarding/HealthInsuranceStep.tsx',
        'src/pages/onboarding/DocumentUploadEnhanced.tsx',
        'src/pages/onboarding/DirectDepositStep.tsx',
        'src/pages/onboarding/CompanyPoliciesStep.tsx',
        'src/pages/ManagerDashboard.tsx',
        'src/pages/HRDashboardDebug.tsx',
        'src/pages/EnhancedManagerDashboard.tsx',
        'src/hooks/useSyncStatus.ts',
        'src/controllers/OnboardingFlowController.ts',
        'src/components/layouts/ManagerDashboardLayout.tsx',
        'src/components/layouts/HRDashboardLayout.tsx',
        'src/components/dashboard/EmployeesTab.tsx',
        'src/components/dashboard/ApplicationsTab.tsx',
        'src/components/dashboard/AnalyticsTab.tsx',
        'src/components/OfficialW4Display.tsx',
        'src/components/OfficialI9Display.tsx',
        'src/services/apiClient.ts',
        'src/services/apiService.ts',
        'src/pages/JobApplicationFormV2.tsx',
    ]
    
    fixed_count = 0
    error_count = 0
    
    for file_rel in files_to_fix:
        file_path = frontend_dir / file_rel
        if file_path.exists():
            try:
                if fix_hardcoded_urls(file_path):
                    print(f"✅ Fixed: {file_rel}")
                    fixed_count += 1
                else:
                    print(f"⏭️  No changes needed: {file_rel}")
            except Exception as e:
                print(f"❌ Error fixing {file_rel}: {e}")
                error_count += 1
        else:
            print(f"⚠️  File not found: {file_rel}")
    
    print(f"\n📊 Summary:")
    print(f"   Files fixed: {fixed_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total processed: {len(files_to_fix)}")

if __name__ == "__main__":
    main()