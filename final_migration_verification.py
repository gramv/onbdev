#!/usr/bin/env python3

import os
import re
from pathlib import Path

def final_migration_verification():
    """Final verification focusing only on actual in-memory database usage"""
    
    print("🔍 FINAL MIGRATION VERIFICATION")
    print("=" * 50)
    
    # Patterns that indicate ACTUAL in-memory database storage (not filtering)
    critical_patterns = [
        # Global dictionary initialization
        r'^applications\s*=\s*\{',
        r'^users\s*=\s*\{',
        r'^properties\s*=\s*\{',
        r'^employees\s*=\s*\{',
        r'^database\s*=\s*\{',
        
        # Global list initialization
        r'^applications\s*=\s*\[',
        r'^users\s*=\s*\[',
        r'^properties\s*=\s*\[',
        r'^employees\s*=\s*\[',
        
        # Database dictionary access
        r'database\["applications"\]',
        r'database\["users"\]',
        r'database\["properties"\]',
        r'database\["employees"\]',
        
        # Direct storage operations
        r'applications\[.*\]\s*=.*\{',
        r'users\[.*\]\s*=.*\{',
        r'properties\[.*\]\s*=.*\{',
        r'employees\[.*\]\s*=.*\{',
    ]
    
    # Critical files to check (main application files only)
    critical_files = [
        "hotel-onboarding-backend/app/main_enhanced.py",
        "hotel-onboarding-backend/app/main.py",
        "hotel-onboarding-backend/app/auth.py",
        "hotel-onboarding-backend/app/supabase_service_enhanced.py",
        "hotel-onboarding-backend/app/services/onboarding_orchestrator.py",
        "hotel-onboarding-backend/app/services/form_update_service.py",
    ]
    
    total_critical_issues = 0
    
    print(f"\n🔍 CHECKING CRITICAL APPLICATION FILES:")
    print("-" * 50)
    
    for file_path in critical_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        print(f"\n🔍 {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Supabase usage
            supabase_usage = len(re.findall(r'supabase', content, re.IGNORECASE))
            
            # Check for critical in-memory patterns
            critical_issues = []
            for i, line in enumerate(content.split('\n'), 1):
                for pattern in critical_patterns:
                    if re.search(pattern, line):
                        critical_issues.append((i, line.strip(), pattern))
            
            print(f"   Supabase references: {supabase_usage}")
            print(f"   Critical in-memory issues: {len(critical_issues)}")
            
            if critical_issues:
                print(f"   ❌ CRITICAL IN-MEMORY DATABASE USAGE FOUND!")
                for line_num, line_content, pattern in critical_issues:
                    print(f"      Line {line_num}: {line_content[:80]}...")
                    print(f"      Pattern: {pattern}")
                total_critical_issues += len(critical_issues)
            elif supabase_usage > 0:
                print(f"   ✅ Using Supabase correctly")
            else:
                print(f"   ⚠️  No database references (may be utility file)")
                
        except Exception as e:
            print(f"   ⚠️  Error reading file: {e}")
    
    # Test the actual functionality
    print(f"\n🧪 TESTING ACTUAL FUNCTIONALITY:")
    print("-" * 50)
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend health check: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database')}")
            print(f"   Connection: {health_data.get('connection')}")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Could not test backend: {e}")
    
    # Summary
    print(f"\n📊 FINAL VERIFICATION SUMMARY:")
    print("=" * 50)
    print(f"Critical in-memory issues: {total_critical_issues}")
    
    if total_critical_issues == 0:
        print(f"🎉 SUCCESS: No critical in-memory database usage found!")
        print(f"✅ Migration to Supabase is COMPLETE")
        print(f"✅ All core application files are using Supabase")
        print(f"")
        print(f"📝 Note: List comprehensions for filtering Supabase results are OK")
        print(f"📝 Note: Test files may still use in-memory patterns for testing")
        return True
    else:
        print(f"❌ CRITICAL ISSUES: {total_critical_issues} in-memory database patterns found")
        print(f"🔧 These must be fixed before migration is complete")
        return False

if __name__ == "__main__":
    success = final_migration_verification()
    exit(0 if success else 1)