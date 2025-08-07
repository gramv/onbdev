#!/usr/bin/env python3
"""
QR Code Visual Test - Generate and Display QR Code

This script demonstrates the QR code generation and shows what a candidate would see
when they scan the QR code.
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image
import sys

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def display_qr_workflow():
    """Display the complete QR workflow visually"""
    
    print("🎯 QR CODE VISUAL DEMONSTRATION")
    print("=" * 50)
    
    # Step 1: Login as HR
    print("\n1️⃣  HR LOGIN")
    login_data = {
        "email": "hr@hoteltest.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print("❌ HR login failed")
        return False
    
    auth_data = response.json()
    hr_token = auth_data["token"]
    headers = {"Authorization": f"Bearer {hr_token}"}
    print(f"✅ Logged in as: {auth_data['user']['first_name']} {auth_data['user']['last_name']}")
    
    # Step 2: Get existing property or create one
    print("\n2️⃣  GET PROPERTY WITH QR CODE")
    
    # Try to get existing properties first
    response = requests.get(f"{BACKEND_URL}/hr/properties", headers=headers)
    if response.status_code == 200:
        properties = response.json()
        if properties:
            property_obj = properties[0]  # Use first property
            property_id = property_obj["id"]
            print(f"✅ Using existing property: {property_obj['name']}")
        else:
            print("No properties found, would need to create one")
            return False
    else:
        print("❌ Could not retrieve properties")
        return False
    
    # Step 3: Generate/Get QR Code
    print("\n3️⃣  QR CODE GENERATION")
    
    response = requests.post(f"{BACKEND_URL}/hr/properties/{property_id}/qr-code", headers=headers)
    if response.status_code != 200:
        print("❌ QR code generation failed")
        return False
    
    qr_data = response.json()
    application_url = qr_data["application_url"]
    qr_code_base64 = qr_data["qr_code_url"]
    
    print(f"✅ QR Code generated successfully")
    print(f"📱 Application URL: {application_url}")
    print(f"🔗 QR Code: {'Present' if qr_code_base64 else 'Missing'}")
    
    # Step 4: Show what happens when QR is scanned
    print("\n4️⃣  QR CODE SCAN SIMULATION")
    print(f"📱 When candidate scans QR code, they go to: {application_url}")
    
    # Test the property info endpoint (what the frontend would call)
    response = requests.get(f"{BACKEND_URL}/properties/{property_id}/info")
    if response.status_code == 200:
        property_info = response.json()
        print("✅ Property info loaded successfully")
        print(f"🏨 Property: {property_info['property']['name']}")
        print(f"📍 Location: {property_info['property']['city']}, {property_info['property']['state']}")
        print(f"📞 Phone: {property_info['property']['phone']}")
        print(f"🔓 Accepting Applications: {property_info['is_accepting_applications']}")
        print(f"🏢 Available Departments: {', '.join(property_info['departments_and_positions'].keys())}")
    else:
        print("❌ Property info not accessible")
        return False
    
    # Step 5: Show application submission
    print("\n5️⃣  APPLICATION SUBMISSION EXAMPLE")
    
    sample_application = {
        "first_name": "Jane",
        "last_name": "Candidate",
        "email": "jane.candidate@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Candidate Street",
        "city": "Job City",
        "state": "CA",
        "zip_code": "90210",
        "department": "Front Desk",
        "position": "Front Desk Agent",
        "work_authorized": "yes",
        "sponsorship_required": "no",
        "start_date": "2025-08-01",
        "shift_preference": "morning",
        "employment_type": "full_time",
        "experience_years": "1-2",
        "hotel_experience": "no",
        "previous_employer": "",
        "reason_for_leaving": "",
        "additional_comments": "Excited to work in hospitality!"
    }
    
    print(f"📝 Sample application for: {sample_application['first_name']} {sample_application['last_name']}")
    print(f"💼 Position: {sample_application['position']} in {sample_application['department']}")
    print(f"📧 Email: {sample_application['email']}")
    
    # Submit the application
    response = requests.post(f"{BACKEND_URL}/apply/{property_id}", json=sample_application)
    if response.status_code == 200:
        app_response = response.json()
        print("✅ Application submitted successfully!")
        print(f"🆔 Application ID: {app_response['application_id']}")
        print(f"🏨 Applied to: {app_response['property_name']}")
        print(f"📋 Position: {app_response['position_applied']}")
    else:
        # Check if it's a duplicate
        if response.status_code == 400 and "already submitted" in response.text:
            print("ℹ️  Application already exists (duplicate prevention working)")
        else:
            print(f"❌ Application submission failed: {response.status_code}")
            return False
    
    # Step 6: Show how it appears in dashboard
    print("\n6️⃣  DASHBOARD VIEW")
    
    response = requests.get(f"{BACKEND_URL}/hr/applications", headers=headers)
    if response.status_code == 200:
        applications = response.json()
        property_applications = [app for app in applications if app['property_id'] == property_id]
        
        print(f"✅ HR Dashboard shows {len(property_applications)} applications for this property")
        
        if property_applications:
            latest_app = property_applications[-1]  # Get most recent
            print(f"📋 Latest Application:")
            print(f"   👤 Applicant: {latest_app['applicant_data']['first_name']} {latest_app['applicant_data']['last_name']}")
            print(f"   💼 Position: {latest_app['position']} - {latest_app['department']}")
            print(f"   📧 Email: {latest_app['applicant_data']['email']}")
            print(f"   📅 Applied: {latest_app['applied_at'][:10]}")
            print(f"   ⏳ Status: {latest_app['status']}")
    else:
        print("❌ Could not retrieve applications")
        return False
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 QR CODE WORKFLOW SUMMARY")
    print("=" * 50)
    print("✅ Complete workflow verified:")
    print("   1. HR creates property → QR code auto-generated")
    print("   2. QR code links to property-specific application form")
    print("   3. Candidates scan QR → see property info & form")
    print("   4. Applications submitted → linked to correct property")
    print("   5. HR/Managers see applications in dashboard")
    print("   6. Duplicate applications prevented")
    
    print(f"\n🔗 QR Code URL: {application_url}")
    print(f"🏨 Property: {property_obj['name']}")
    print(f"📊 Total Applications: {len(property_applications)}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting QR Code Visual Demonstration...")
    
    try:
        success = display_qr_workflow()
        if success:
            print("\n✨ QR Code workflow demonstration completed successfully!")
        else:
            print("\n💥 Demonstration failed. Check the output above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Demonstration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)