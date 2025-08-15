#!/usr/bin/env python3
"""
Create Test Data for Manager Document Access Testing
==================================================

This script creates test employees and documents to demonstrate the
manager document access functionality.
"""

import requests
import json
import base64
import uuid
from datetime import datetime, timedelta
import tempfile
import os

class DocumentAccessTestDataCreator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.manager_token = None
        self.property_id = "a99239dd-ebde-4c69-b862-ecba9e878798"
        
    def get_manager_token(self):
        """Get manager authentication token"""
        login_data = {"email": "manager@demo.com", "password": "demo123"}
        response = requests.post(f"{self.base_url}/auth/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                self.manager_token = result["data"]["token"]
                print("✅ Manager authenticated successfully")
                return True
        
        print(f"❌ Manager authentication failed: {response.text}")
        return False
    
    def create_sample_document_file(self, doc_type="pdf"):
        """Create a sample document file for testing"""
        if doc_type == "pdf":
            # Create a minimal PDF document
            content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test Document) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000136 00000 n 
0000000229 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
324
%%EOF"""
            return content, "application/pdf", "test_document.pdf"
        
        else:
            # Create a simple text file
            content = b"Test Document Content\nEmployee ID Verification\nDate: " + datetime.now().strftime("%Y-%m-%d").encode()
            return content, "text/plain", "test_document.txt"
    
    def create_test_employee(self, employee_data):
        """Create a test employee via API"""
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        # Create employee setup data
        setup_data = {
            "application_id": str(uuid.uuid4()),
            "employee_data": employee_data,
            "position_details": {
                "position": employee_data.get("position", "Front Desk Associate"),
                "department": "Front Office",
                "hire_date": datetime.now().strftime("%Y-%m-%d"),
                "employment_type": "full_time",
                "pay_rate": 18.00
            }
        }
        
        # Try to create employee via manager setup endpoint
        response = requests.post(
            f"{self.base_url}/api/manager/employee-setup", 
            json=setup_data, 
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                employee_info = result.get("data", {})
                print(f"✅ Created employee: {employee_data['name']}")
                return employee_info.get("employee_id")
        
        print(f"❌ Failed to create employee {employee_data['name']}: {response.text}")
        return None
    
    def upload_test_document(self, employee_id, doc_type="i9_form"):
        """Upload a test document for an employee"""
        headers = {"Authorization": f"Bearer {self.manager_token}"}
        
        # Create sample document
        doc_content, mime_type, filename = self.create_sample_document_file()
        
        # Prepare multipart form data
        files = {
            'file': (filename, doc_content, mime_type)
        }
        
        data = {
            'employee_id': employee_id,
            'document_type': doc_type,
            'description': f'Test {doc_type} document'
        }
        
        # Try document upload endpoint
        response = requests.post(
            f"{self.base_url}/api/documents/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Uploaded {doc_type} document for employee {employee_id}")
                return result.get("data", {}).get("document_id")
        
        print(f"❌ Failed to upload document: {response.text}")
        return None
    
    def create_comprehensive_test_data(self):
        """Create comprehensive test data set"""
        print("="*60)
        print("CREATING TEST DATA FOR DOCUMENT ACCESS TESTING")
        print("="*60)
        
        if not self.get_manager_token():
            return False
        
        # Test employees to create
        test_employees = [
            {
                "name": "John Smith",
                "email": "john.smith@demo.hotel",
                "phone": "(555) 123-4567",
                "position": "Front Desk Associate",
                "ssn": "123-45-6789"
            },
            {
                "name": "Maria Garcia", 
                "email": "maria.garcia@demo.hotel",
                "phone": "(555) 234-5678",
                "position": "Housekeeper",
                "ssn": "234-56-7890"
            },
            {
                "name": "David Johnson",
                "email": "david.johnson@demo.hotel", 
                "phone": "(555) 345-6789",
                "position": "Maintenance",
                "ssn": "345-67-8901"
            }
        ]
        
        created_employees = []
        
        # Create test employees
        print("\n📝 Creating test employees...")
        for employee_data in test_employees:
            employee_id = self.create_test_employee(employee_data)
            if employee_id:
                created_employees.append({
                    "id": employee_id,
                    "name": employee_data["name"],
                    "position": employee_data["position"]
                })
        
        if not created_employees:
            print("❌ No employees created - cannot proceed with document testing")
            return False
        
        # Create test documents for each employee
        print("\n📄 Creating test documents...")
        document_types = ["i9_form", "w4_form", "drivers_license", "voided_check"]
        
        for employee in created_employees:
            print(f"\n  Creating documents for {employee['name']}...")
            for doc_type in document_types:
                doc_id = self.upload_test_document(employee['id'], doc_type)
                if doc_id:
                    print(f"    ✅ {doc_type}: {doc_id}")
                else:
                    print(f"    ❌ Failed to create {doc_type}")
        
        print(f"\n🎉 Test data creation completed!")
        print(f"Created {len(created_employees)} employees with documents")
        
        return True

def main():
    creator = DocumentAccessTestDataCreator()
    
    success = creator.create_comprehensive_test_data()
    
    if success:
        print("\n✅ Test data created successfully!")
        print("You can now run the document access tests:")
        print("python3 test_manager_document_access.py")
    else:
        print("\n❌ Failed to create test data")
        print("Check the backend logs for more details")
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)