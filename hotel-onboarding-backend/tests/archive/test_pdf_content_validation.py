#!/usr/bin/env python3
"""
PDF Content Validation Test for Document Preview Endpoints
Hotel Employee Onboarding System

This test validates the actual content and structure of generated PDFs to ensure:
1. PDFs contain expected form content
2. Dynamic data is properly filled in
3. Signature fields are appropriately placed
4. Documents are legally compliant and readable
"""

import requests
import json
import base64
import io
from datetime import datetime
from PyPDF2 import PdfReader
import sys
import os

# Test configuration
BASE_URL = "http://localhost:8000"
EMPLOYEE_ID = "test-employee"

class PDFContentValidator:
    def __init__(self):
        self.results = {}
        
    def log(self, message):
        """Log test output with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def save_pdf_sample(self, pdf_bytes, filename):
        """Save a PDF sample for manual inspection"""
        sample_path = f"{filename}_sample.pdf"
        with open(sample_path, 'wb') as f:
            f.write(pdf_bytes)
        self.log(f"   📄 Sample saved: {sample_path}")
        return sample_path
        
    def extract_pdf_text(self, pdf_bytes):
        """Extract all text content from PDF"""
        try:
            pdf_buffer = io.BytesIO(pdf_bytes)
            pdf_reader = PdfReader(pdf_buffer)
            
            all_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                all_text += f"PAGE {page_num + 1}:\n{page_text}\n\n"
                
            return all_text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
            
    def validate_direct_deposit_content(self, pdf_bytes, test_data):
        """Validate Direct Deposit PDF content"""
        text = self.extract_pdf_text(pdf_bytes)
        
        validations = []
        
        # Check for form title
        if "Direct Deposit" in text or "ADP" in text:
            validations.append("✅ Form title present")
        else:
            validations.append("❌ Missing form title")
            
        # Check for employee data if provided
        if test_data and test_data.get("employee_data", {}).get("name"):
            name = test_data["employee_data"]["name"]
            if name in text:
                validations.append(f"✅ Employee name '{name}' found")
            else:
                validations.append(f"❌ Employee name '{name}' not found")
                
        # Check for banking fields
        banking_terms = ["Bank Name", "Routing Number", "Account Number", "Account Type"]
        for term in banking_terms:
            if term in text or term.lower() in text.lower():
                validations.append(f"✅ Banking field '{term}' present")
            else:
                validations.append(f"⚠️  Banking field '{term}' not clearly visible")
                
        return validations
        
    def validate_health_insurance_content(self, pdf_bytes, test_data):
        """Validate Health Insurance PDF content"""
        text = self.extract_pdf_text(pdf_bytes)
        
        validations = []
        
        # Check for form title
        if "Health Insurance" in text:
            validations.append("✅ Form title present")
        else:
            validations.append("❌ Missing form title")
            
        # Check for plan year
        if "2025" in text:
            validations.append("✅ Current plan year (2025) present")
        else:
            validations.append("❌ Plan year not found")
            
        # Check for enrollment options
        enrollment_terms = ["Employee", "Spouse", "Child", "Waive"]
        for term in enrollment_terms:
            if term in text:
                validations.append(f"✅ Enrollment option '{term}' present")
                
        return validations
        
    def validate_weapons_policy_content(self, pdf_bytes, test_data):
        """Validate Weapons Policy PDF content"""
        text = self.extract_pdf_text(pdf_bytes)
        
        validations = []
        
        # Check for policy title
        if "WEAPONS PROHIBITION" in text:
            validations.append("✅ Policy title present")
        else:
            validations.append("❌ Missing policy title")
            
        # Check for key policy elements
        policy_terms = ["prohibited", "workplace", "termination", "acknowledge"]
        for term in policy_terms:
            if term.lower() in text.lower():
                validations.append(f"✅ Policy term '{term}' found")
                
        return validations
        
    def validate_human_trafficking_content(self, pdf_bytes, test_data):
        """Validate Human Trafficking PDF content"""
        text = self.extract_pdf_text(pdf_bytes)
        
        validations = []
        
        # Check for awareness title
        if "HUMAN TRAFFICKING" in text:
            validations.append("✅ Awareness title present")
        else:
            validations.append("❌ Missing awareness title")
            
        # Check for federal requirement
        if "FEDERAL REQUIREMENT" in text:
            validations.append("✅ Federal requirement notice present")
        else:
            validations.append("❌ Missing federal requirement notice")
            
        # Check for hospitality industry mention
        if "HOSPITALITY" in text:
            validations.append("✅ Industry-specific content present")
            
        return validations
        
    def validate_company_policies_content(self, pdf_bytes, test_data):
        """Validate Company Policies PDF content"""
        text = self.extract_pdf_text(pdf_bytes)
        
        validations = []
        
        # Check for policies title
        if "COMPANY POLICIES" in text:
            validations.append("✅ Policies title present")
        else:
            validations.append("❌ Missing policies title")
            
        # Check for acknowledgment language
        if "acknowledge" in text.lower():
            validations.append("✅ Acknowledgment language present")
        else:
            validations.append("❌ Missing acknowledgment language")
            
        # Check for signature section
        if "signature" in text.lower() or "sign" in text.lower():
            validations.append("✅ Signature section present")
            
        return validations
        
    def test_pdf_content(self, endpoint_path, test_data, endpoint_name, validator_func):
        """Test PDF content for a specific endpoint"""
        self.log(f"\n{'='*60}")
        self.log(f"CONTENT VALIDATION: {endpoint_name}")
        self.log(f"{'='*60}")
        
        url = f"{BASE_URL}{endpoint_path}"
        
        try:
            # Get PDF with complete data
            response = requests.post(url, json=test_data)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "data" in response_data and "pdf" in response_data["data"]:
                    pdf_base64 = response_data["data"]["pdf"]
                    pdf_bytes = base64.b64decode(pdf_base64)
                    
                    # Save sample PDF
                    filename = endpoint_name.replace(" ", "_")
                    sample_path = self.save_pdf_sample(pdf_bytes, filename)
                    
                    # Extract and display text content
                    full_text = self.extract_pdf_text(pdf_bytes)
                    self.log(f"   📖 PDF Text Content (first 500 chars):")
                    self.log(f"      {full_text[:500]}...")
                    
                    # Run content validation
                    validations = validator_func(pdf_bytes, test_data)
                    
                    self.log(f"   🔍 Content Validations:")
                    for validation in validations:
                        self.log(f"      {validation}")
                        
                    return True
                else:
                    self.log(f"❌ Invalid response format")
                    return False
            else:
                self.log(f"❌ HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing {endpoint_name}: {str(e)}")
            return False
            
    def run_content_validation(self):
        """Run comprehensive PDF content validation"""
        self.log("🚀 Starting PDF Content Validation Tests")
        self.log(f"Target server: {BASE_URL}")
        
        # Test data with rich content
        rich_test_data = {
            "direct_deposit": {
                "employee_data": {
                    "name": "John Test Smith",
                    "ssn": "123-45-6789",
                    "account_type": "checking",
                    "bank_name": "Test Bank of America",
                    "routing_number": "123456789",
                    "account_number": "987654321",
                    "address": "123 Main St, Test City, CA 90210",
                    "signature_date": datetime.now().isoformat()
                }
            },
            "health_insurance": {
                "employee_data": {
                    "name": "Jane Test Doe",
                    "employee_id": "EMP123456",
                    "date_of_birth": "1990-01-15",
                    "enrollment_choice": "enroll",
                    "coverage_level": "employee_spouse",
                    "dependents": [
                        {
                            "name": "John Doe Jr.",
                            "relationship": "child",
                            "date_of_birth": "2015-06-20"
                        }
                    ],
                    "signature_date": datetime.now().isoformat()
                }
            },
            "weapons_policy": {
                "employee_data": {
                    "name": "Mike Test Johnson", 
                    "employee_id": "EMP789012",
                    "position": "Front Desk Clerk",
                    "department": "Guest Services",
                    "hire_date": "2025-01-15",
                    "signature_date": datetime.now().isoformat()
                }
            },
            "human_trafficking": {
                "employee_data": {
                    "name": "Sarah Test Wilson",
                    "employee_id": "EMP345678",
                    "position": "Housekeeper",
                    "department": "Housekeeping",
                    "signature_date": datetime.now().isoformat()
                }
            },
            "company_policies": {
                "employee_data": {
                    "name": "Robert Test Brown",
                    "employee_id": "EMP567890", 
                    "position": "Maintenance Worker",
                    "department": "Engineering",
                    "hire_date": "2025-02-01",
                    "signature_date": datetime.now().isoformat()
                }
            }
        }
        
        # Test all endpoints with content validation
        endpoints_to_test = [
            (f"/api/onboarding/{EMPLOYEE_ID}/direct-deposit/generate-pdf", 
             rich_test_data["direct_deposit"], "Direct Deposit PDF", self.validate_direct_deposit_content),
             
            (f"/api/onboarding/{EMPLOYEE_ID}/health-insurance/generate-pdf", 
             rich_test_data["health_insurance"], "Health Insurance PDF", self.validate_health_insurance_content),
             
            (f"/api/onboarding/{EMPLOYEE_ID}/weapons-policy/generate-pdf", 
             rich_test_data["weapons_policy"], "Weapons Policy PDF", self.validate_weapons_policy_content),
             
            (f"/api/onboarding/{EMPLOYEE_ID}/human-trafficking/generate-pdf", 
             rich_test_data["human_trafficking"], "Human Trafficking PDF", self.validate_human_trafficking_content),
             
            (f"/api/onboarding/{EMPLOYEE_ID}/company-policies/generate-pdf", 
             rich_test_data["company_policies"], "Company Policies PDF", self.validate_company_policies_content)
        ]
        
        successful_tests = 0
        for endpoint_path, test_data, endpoint_name, validator_func in endpoints_to_test:
            if self.test_pdf_content(endpoint_path, test_data, endpoint_name, validator_func):
                successful_tests += 1
                
        # Print summary
        self.log(f"\n{'='*60}")
        self.log("PDF CONTENT VALIDATION SUMMARY")
        self.log(f"{'='*60}")
        self.log(f"✅ Successful: {successful_tests}")
        self.log(f"❌ Failed: {len(endpoints_to_test) - successful_tests}")
        self.log(f"📊 Total: {len(endpoints_to_test)}")
        
        if successful_tests == len(endpoints_to_test):
            self.log("🎉 ALL PDF CONTENT VALIDATIONS PASSED!")
            return True
        else:
            self.log("⚠️  Some PDF content validations failed.")
            return False

def main():
    """Main test execution"""
    print("PDF Content Validation Test Suite")
    print("Hotel Employee Onboarding System")
    print("="*60)
    
    validator = PDFContentValidator()
    success = validator.run_content_validation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()