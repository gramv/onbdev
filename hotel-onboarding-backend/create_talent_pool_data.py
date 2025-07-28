#!/usr/bin/env python3
"""
Script to create talent pool test data by manually updating application statuses
"""
import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000"
HR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiaHJfdGVzdF8wMDEiLCJyb2xlIjoiaHIiLCJ0b2tlbl90eXBlIjoiaHJfYXV0aCIsImlhdCI6MTc1MzY1MDAxOCwiZXhwIjoxNzUzNzM2NDE4LCJqdGkiOiI2MGNhZmY2Yi0yMDI0LTQxOWUtOGZiMi04NjBhMmZmNjUyYzAifQ.zqCGeKJeH2tsB-ipgSol5TZiGOkbObUL0menQjXpWwk"

def get_applications():
    """Get all applications"""
    headers = {"Authorization": f"Bearer {HR_TOKEN}"}
    response = requests.get(f"{BASE_URL}/hr/applications", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get applications: {response.text}")
        return []

def update_application_to_talent_pool(app_id):
    """Update application status to talent_pool via direct database manipulation"""
    # Since there's no direct endpoint to move to talent pool as HR,
    # we'll use the internal database structure
    print(f"Would update application {app_id} to talent_pool status")
    # This would require direct database access which we don't have in this setup
    return False

def main():
    print("🔄 Creating talent pool test data...")
    
    # Get all applications
    applications = get_applications()
    print(f"Found {len(applications)} applications")
    
    # Find some applications to move to talent pool
    # Let's move Emily Davis and Michael Brown applications to talent pool
    talent_pool_candidates = []
    for app in applications:
        if app['applicant_name'] in ['Emily Davis', 'Michael Brown'] and len(talent_pool_candidates) < 6:
            talent_pool_candidates.append(app)
    
    print(f"Selected {len(talent_pool_candidates)} candidates for talent pool:")
    for candidate in talent_pool_candidates:
        print(f"  - {candidate['applicant_name']} - {candidate['position']} at {candidate['property_name']}")
    
    # Since we can't directly update the database, let's just show what we would do
    print("\n⚠️  Note: Direct database manipulation would be needed to create talent pool data")
    print("For demo purposes, the frontend will work with the existing talent pool endpoint")

if __name__ == "__main__":
    main()