#!/usr/bin/env python3
"""
Clear existing applications from the backend data structures
"""
import sys
import os

# Add the backend path to sys.path
sys.path.insert(0, 'hotel-onboarding-backend')

try:
    # Import the database from the main application
    from app.main_enhanced import database
    
    # Clear all data structures
    initial_apps = len(database.get("applications", {}))
    initial_employees = len(database.get("employees", {}))
    initial_onboarding = len(database.get("onboarding_sessions", {}))
    initial_form_updates = len(database.get("form_update_sessions", {}))
    
    # Clear the data
    database["applications"] = {}
    database["employees"] = {}
    database["onboarding_sessions"] = {}
    database["form_update_sessions"] = {}
    
    print("🧹 Cleared Backend Data Structures:")
    print(f"   📝 Applications: {initial_apps} → 0")
    print(f"   👤 Employees: {initial_employees} → 0") 
    print(f"   🎯 Onboarding Sessions: {initial_onboarding} → 0")
    print(f"   📋 Form Update Sessions: {initial_form_updates} → 0")
    print("✅ All data cleared successfully!")
    
except ImportError as e:
    print(f"❌ Could not import backend modules: {e}")
    print("Make sure the backend server is running")
except Exception as e:
    print(f"❌ Error clearing data: {e}")