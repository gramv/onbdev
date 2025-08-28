#!/usr/bin/env python3

import os
import re
from pathlib import Path

def focused_inmemory_audit():
    """Focused audit on application code only"""
    
    print("🔍 FOCUSED IN-MEMORY DATABASE AUDIT - APPLICATION CODE ONLY")
    print("=" * 70)
    
    # Patterns that indicate in-memory database usage
    inmemory_patterns = [
        # Dictionary-based storage
        r'applications\s*=\s*\{',
        r'users\s*=\s*\{',
        r'properties\s*=\s*\{',
        r'employees\s*=\s*\{',
        r'managers\s*=\s*\{',
        r'talent_pool\s*=\s*\{',
        r'onboarding_sessions\s*=\s*\{',
        
        # List-based storage
        r'applications\s*=\s*\[',
        r'users\s*=\s*\[',
        r'properties\s*=\s*\[',
        r'employees\s*=\s*\[',
        
        # Global variables
        r'global\s+applications',
        r'global\s+users',
        r'global\s+properties',
        r'global\s+employees',
        
        # Direct dictionary access patterns
        r'applications\[.*\]\s*=',
        r'users\[.*\]\s*=',
        r'properties\[.*\]\s*=',
        r'employees\[.*\]\s*=',
        
        # Dictionary methods on data structures
        r'applications\.get\(',
        r'applications\.pop\(',
        r'applications\.update\(',
        r'applications\.setdefault\(',
        r'users\.get\(',
        r'users\.pop\(',
        r'properties\.get\(',
        r'employees\.get\(',
        
        # List operations on data structures
        r'applications\.append\(',
        r'applications\.remove\(',
        r'users\.append\(',
        r'properties\.append\(',
        
        # Dictionary comprehensions
        r'\{.*for.*in\s+applications',
        r'\{.*for.*in\s+users',
        r'\{.*for.*in\s+properties',
        
        # Specific problematic patterns
        r'\.values\(\).*applications',
        r'\.keys\(\).*applications',
        r'\.items\(\).*applications',
        r'len\(applications\)',
        r'len\(users\)',
        r'len\(properties\)',
        
        # Variable assignments that suggest in-memory
        r'app_data\s*=\s*applications',
        r'user_data\s*=\s*users',
        r'prop_data\s*=\s*properties',
    ]
    
    # Application files to check (exclude third-party libraries)
    app_files = []
    
    # Backend application files only
    backend_app_path = Path("hotel-onboarding-backend/app")
    if backend_app_path.exists():
        for file_path in backend_app_path.rglob("*.py"):
            if not any(skip in str(file_path) for skip in ['__pycache__', '.pyc', 'venv', 'site-packages']):
                app_files.append(file_path)
    
    # Root level backend files
    backend_root = Path("hotel-onboarding-backend")
    if backend_root.exists():
        for file_path in backend_root.glob("*.py"):
            if not any(skip in str(file_path) for skip in ['venv', 'site-packages', '__pycache__']):
                app_files.append(file_path)
    
    # Frontend application files
    frontend_src_path = Path("hotel-onboarding-frontend/src")
    if frontend_src_path.exists():
        for file_path in frontend_src_path.rglob("*.ts*"):
            if not any(skip in str(file_path) for skip in ['node_modules', '.test.', '__tests__', 'venv']):
                app_files.append(file_path)
        for file_path in frontend_src_path.rglob("*.js*"):
            if not any(skip in str(file_path) for skip in ['node_modules', '.test.', '__tests__', 'venv']):
                app_files.append(file_path)
    
    total_issues = 0
    
    print(f"\n📁 Checking {len(app_files)} application files...")
    
    # Check application files
    print(f"\n🔍 APPLICATION FILES AUDIT:")
    print("-" * 50)
    
    for file_path in app_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_issues = []
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in inmemory_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Skip comments and documentation
                        if line.strip().startswith('#') or line.strip().startswith('//') or line.strip().startswith('*'):
                            continue
                        file_issues.append((i, line.strip(), pattern))
            
            if file_issues:
                print(f"\n❌ {file_path}")
                for line_num, line_content, pattern in file_issues:
                    print(f"   Line {line_num}: {line_content[:100]}...")
                    print(f"   Pattern: {pattern}")
                total_issues += len(file_issues)
            else:
                print(f"✅ {file_path}")
                
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    # Check specific critical files for Supabase usage
    print(f"\n🔍 SUPABASE USAGE VERIFICATION:")
    print("-" * 50)
    
    critical_files = [
        "hotel-onboarding-backend/app/main_enhanced.py",
        "hotel-onboarding-backend/app/auth.py",
        "hotel-onboarding-backend/app/supabase_service_enhanced.py",
        "hotel-onboarding-backend/app/services/onboarding_orchestrator.py",
        "hotel-onboarding-backend/app/services/form_update_service.py",
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"\n🔍 {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for Supabase usage
                supabase_usage = len(re.findall(r'supabase', content, re.IGNORECASE))
                inmemory_usage = len(re.findall(r'applications\s*=\s*\{|users\s*=\s*\{', content))
                
                print(f"   Supabase references: {supabase_usage}")
                print(f"   In-memory patterns: {inmemory_usage}")
                
                if inmemory_usage > 0:
                    print(f"   ❌ STILL HAS IN-MEMORY REFERENCES!")
                    total_issues += inmemory_usage
                elif supabase_usage > 0:
                    print(f"   ✅ Using Supabase")
                else:
                    print(f"   ⚠️  No database references found")
                    
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
        else:
            print(f"   ⚠️  File not found: {file_path}")
    
    # Summary
    print(f"\n📊 FOCUSED AUDIT SUMMARY:")
    print("=" * 50)
    print(f"Application files checked: {len(app_files)}")
    print(f"In-memory issues found: {total_issues}")
    
    if total_issues == 0:
        print(f"🎉 SUCCESS: No in-memory database references found in application code!")
        print(f"✅ All operations are using Supabase")
        return True
    else:
        print(f"❌ ISSUES FOUND: {total_issues} in-memory references in application code")
        print(f"🔧 These need to be migrated to Supabase")
        return False

if __name__ == "__main__":
    success = focused_inmemory_audit()
    exit(0 if success else 1)