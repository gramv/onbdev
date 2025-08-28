#!/usr/bin/env python3

import os
import re
from pathlib import Path

def comprehensive_inmemory_audit():
    """Comprehensive audit to find ANY in-memory database references"""
    
    print("🔍 COMPREHENSIVE IN-MEMORY DATABASE AUDIT")
    print("=" * 60)
    
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
        
        # Dictionary methods
        r'applications\.get\(',
        r'applications\.pop\(',
        r'applications\.update\(',
        r'applications\.setdefault\(',
        r'users\.get\(',
        r'users\.pop\(',
        r'properties\.get\(',
        r'employees\.get\(',
        
        # List operations
        r'applications\.append\(',
        r'applications\.remove\(',
        r'users\.append\(',
        r'properties\.append\(',
        
        # Dictionary comprehensions
        r'\{.*for.*in\s+applications',
        r'\{.*for.*in\s+users',
        r'\{.*for.*in\s+properties',
        
        # In-memory comments
        r'#.*in.?memory',
        r'#.*dictionary',
        r'#.*local.*storage',
        
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
    
    # Files to check
    backend_files = []
    frontend_files = []
    
    # Get all Python files in backend
    backend_path = Path("hotel-onboarding-backend")
    if backend_path.exists():
        for file_path in backend_path.rglob("*.py"):
            if not any(skip in str(file_path) for skip in ['__pycache__', '.pyc', 'test_', 'debug_', 'migrate_']):
                backend_files.append(file_path)
    
    # Get all TypeScript/JavaScript files in frontend
    frontend_path = Path("hotel-onboarding-frontend/src")
    if frontend_path.exists():
        for file_path in frontend_path.rglob("*.ts*"):
            if not any(skip in str(file_path) for skip in ['node_modules', '.test.', '__tests__']):
                frontend_files.append(file_path)
        for file_path in frontend_path.rglob("*.js*"):
            if not any(skip in str(file_path) for skip in ['node_modules', '.test.', '__tests__']):
                frontend_files.append(file_path)
    
    total_issues = 0
    
    print(f"\n📁 Checking {len(backend_files)} backend files...")
    print(f"📁 Checking {len(frontend_files)} frontend files...")
    
    # Check backend files
    print(f"\n🔍 BACKEND FILES AUDIT:")
    print("-" * 40)
    
    for file_path in backend_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_issues = []
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in inmemory_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        file_issues.append((i, line.strip(), pattern))
            
            if file_issues:
                print(f"\n❌ {file_path}")
                for line_num, line_content, pattern in file_issues:
                    print(f"   Line {line_num}: {line_content[:80]}...")
                    print(f"   Pattern: {pattern}")
                total_issues += len(file_issues)
            else:
                print(f"✅ {file_path}")
                
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    # Check frontend files
    print(f"\n🔍 FRONTEND FILES AUDIT:")
    print("-" * 40)
    
    # Frontend patterns (JavaScript/TypeScript specific)
    frontend_patterns = [
        r'localStorage\.setItem.*applications',
        r'sessionStorage\.setItem.*applications',
        r'const\s+applications\s*=\s*\{',
        r'let\s+applications\s*=\s*\{',
        r'var\s+applications\s*=\s*\{',
        r'applications\s*:\s*\{',
        r'users\s*:\s*\{',
        r'properties\s*:\s*\{',
    ]
    
    for file_path in frontend_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_issues = []
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in frontend_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        file_issues.append((i, line.strip(), pattern))
            
            if file_issues:
                print(f"\n❌ {file_path}")
                for line_num, line_content, pattern in file_issues:
                    print(f"   Line {line_num}: {line_content[:80]}...")
                    print(f"   Pattern: {pattern}")
                total_issues += len(file_issues)
            else:
                print(f"✅ {file_path}")
                
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    # Check specific critical files
    print(f"\n🔍 CRITICAL FILES DEEP DIVE:")
    print("-" * 40)
    
    critical_files = [
        "hotel-onboarding-backend/app/main_enhanced.py",
        "hotel-onboarding-backend/app/main.py",
        "hotel-onboarding-backend/app/auth.py",
        "hotel-onboarding-backend/app/supabase_service_enhanced.py",
        "hotel-onboarding-backend/app/services/onboarding_orchestrator.py",
        "hotel-onboarding-backend/app/services/form_update_service.py",
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"\n🔍 Deep checking: {file_path}")
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
                else:
                    print(f"   ✅ Clean - using Supabase")
                    
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
        else:
            print(f"   ⚠️  File not found: {file_path}")
    
    # Summary
    print(f"\n📊 AUDIT SUMMARY:")
    print("=" * 40)
    print(f"Total files checked: {len(backend_files) + len(frontend_files)}")
    print(f"Total issues found: {total_issues}")
    
    if total_issues == 0:
        print(f"🎉 SUCCESS: No in-memory database references found!")
        print(f"✅ All operations should be using Supabase")
        return True
    else:
        print(f"❌ ISSUES FOUND: {total_issues} in-memory references detected")
        print(f"🔧 These need to be migrated to Supabase")
        return False

if __name__ == "__main__":
    success = comprehensive_inmemory_audit()
    exit(0 if success else 1)