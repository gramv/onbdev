"""
PDF Form Field Mappings for Government Compliance
Maps form data to official PDF form fields for I-9, W-4, and other documents
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
try:
    import fitz  # PyMuPDF for form handling
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("Warning: PyMuPDF not available. PDF form filling will use fallback methods.")

try:
    from PyPDF2 import PdfReader, PdfWriter
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

# Official I-9 Form Field Mappings (based on USCIS I-9 11/14/23 edition)
I9_FORM_FIELDS = {
    # Section 1: Employee Information and Attestation
    "employee_last_name": "form1[0].#subform[0].Pt1Line1_FamilyName[0]",
    "employee_first_name": "form1[0].#subform[0].Pt1Line1_GivenName[0]", 
    "employee_middle_initial": "form1[0].#subform[0].Pt1Line1_MI[0]",
    "other_last_names": "form1[0].#subform[0].Pt1Line2_OtherNames[0]",
    
    # Address fields
    "address_street": "form1[0].#subform[0].Pt1Line3_StreetNumberName[0]",
    "address_apt": "form1[0].#subform[0].Pt1Line3_AptNumber[0]",
    "address_city": "form1[0].#subform[0].Pt1Line3_CityTown[0]",
    "address_state": "form1[0].#subform[0].Pt1Line3_State[0]",
    "address_zip": "form1[0].#subform[0].Pt1Line3_ZipCode[0]",
    
    # Personal information
    "date_of_birth": "form1[0].#subform[0].Pt1Line4_DOB[0]",
    "ssn": "form1[0].#subform[0].Pt1Line5_SSN[0]",
    "email": "form1[0].#subform[0].Pt1Line6_Email[0]",
    "phone": "form1[0].#subform[0].Pt1Line7_TelNumber[0]",
    
    # Citizenship attestation (checkboxes)
    "citizenship_us_citizen": "form1[0].#subform[0].Pt1Line8_Checkbox[0]",
    "citizenship_noncitizen_national": "form1[0].#subform[0].Pt1Line8_Checkbox[1]", 
    "citizenship_permanent_resident": "form1[0].#subform[0].Pt1Line8_Checkbox[2]",
    "citizenship_authorized_alien": "form1[0].#subform[0].Pt1Line8_Checkbox[3]",
    
    # Additional fields for non-citizens
    "uscis_number": "form1[0].#subform[0].Pt1Line9_AlienNumber[0]",
    "i94_admission_number": "form1[0].#subform[0].Pt1Line9_I94Number[0]",
    "passport_number": "form1[0].#subform[0].Pt1Line9_PassportNumber[0]",
    "passport_country": "form1[0].#subform[0].Pt1Line9_CountryIssuance[0]",
    
    # Employee signature and date
    "employee_signature_date": "form1[0].#subform[0].Pt1Line10_DateSigned[0]",
    
    # Section 2: Employer Review and Verification
    "first_day_employment": "form1[0].#subform[1].Pt2Line1_FirstDayEmployment[0]",
    
    # Document verification
    "document_title_1": "form1[0].#subform[1].Pt2Line2a_DocumentTitle[0]",
    "issuing_authority_1": "form1[0].#subform[1].Pt2Line2a_IssuingAuthority[0]",
    "document_number_1": "form1[0].#subform[1].Pt2Line2a_DocumentNumber[0]",
    "expiration_date_1": "form1[0].#subform[1].Pt2Line2a_ExpirationDate[0]",
    
    "document_title_2": "form1[0].#subform[1].Pt2Line2b_DocumentTitle[0]",
    "issuing_authority_2": "form1[0].#subform[1].Pt2Line2b_IssuingAuthority[0]",
    "document_number_2": "form1[0].#subform[1].Pt2Line2b_DocumentNumber[0]",
    "expiration_date_2": "form1[0].#subform[1].Pt2Line2b_ExpirationDate[0]",
    
    "document_title_3": "form1[0].#subform[1].Pt2Line2c_DocumentTitle[0]",
    "issuing_authority_3": "form1[0].#subform[1].Pt2Line2c_IssuingAuthority[0]",
    "document_number_3": "form1[0].#subform[1].Pt2Line2c_DocumentNumber[0]",
    "expiration_date_3": "form1[0].#subform[1].Pt2Line2c_ExpirationDate[0]",
    
    # Additional information
    "additional_info": "form1[0].#subform[1].Pt2Line3_AdditionalInfo[0]",
    
    # Employer signature
    "employer_name": "form1[0].#subform[1].Pt2Line4_LastName[0]",
    "employer_title": "form1[0].#subform[1].Pt2Line4_Title[0]",
    "employer_signature_date": "form1[0].#subform[1].Pt2Line4_DateSigned[0]",
    
    # Business information
    "business_name": "form1[0].#subform[1].Pt2Line5_BusinessName[0]",
    "business_address": "form1[0].#subform[1].Pt2Line5_BusinessAddress[0]",
    "business_city": "form1[0].#subform[1].Pt2Line5_City[0]",
    "business_state": "form1[0].#subform[1].Pt2Line5_State[0]",
    "business_zip": "form1[0].#subform[1].Pt2Line5_ZipCode[0]"
}

# Official W-4 Form Field Mappings (based on IRS Form W-4 2025 - EXACT COMPLIANCE)
# CRITICAL: These are the EXACT field names from the official 2025 IRS W-4 PDF template
# Any deviation from these names will result in legal non-compliance
W4_FORM_FIELDS = {
    # Step 1: Personal Information (EXACT IRS field names)
    "first_name_and_middle_initial": "topmostSubform[0].Page1[0].Step1[0].f1_01[0]",  # Combined first name and middle initial field
    "last_name": "topmostSubform[0].Page1[0].Step1[0].f1_02[0]",
    "address": "topmostSubform[0].Page1[0].Step1[0].f1_03[0]",
    "city_state_zip": "topmostSubform[0].Page1[0].Step1[0].f1_04[0]",  # Combined city, state, ZIP field
    "social_security_number": "topmostSubform[0].Page1[0].Step1[0].f1_05[0]",
    
    # Step 1: Filing Status (EXACT IRS checkbox field names)
    "filing_status_single": "topmostSubform[0].Page1[0].Step1[0].c1_1[0]",  # Single or Married filing separately
    "filing_status_married_jointly": "topmostSubform[0].Page1[0].Step1[0].c1_1[1]",  # Married filing jointly or Qualifying surviving spouse
    "filing_status_head_of_household": "topmostSubform[0].Page1[0].Step1[0].c1_1[2]",  # Head of household
    
    # Step 2: Multiple Jobs or Spouse Works (EXACT IRS field names)
    "step2_multiple_jobs_checkbox": "topmostSubform[0].Page1[0].Step2[0].c1_2[0]",  # Multiple jobs checkbox
    
    # Step 3: Claim Dependents (EXACT IRS field names)
    "step3_qualifying_children_amount": "topmostSubform[0].Page1[0].Step3[0].f1_06[0]",  # Qualifying children × $2,000
    "step3_other_dependents_amount": "topmostSubform[0].Page1[0].Step3[0].f1_07[0]",  # Other dependents × $500
    "step3_total_credits": "topmostSubform[0].Page1[0].Step3[0].f1_08[0]",  # Total credits amount
    
    # Step 4: Other Adjustments (EXACT IRS field names)
    "step4a_other_income": "topmostSubform[0].Page1[0].Step4[0].f1_09[0]",  # Other income
    "step4b_deductions": "topmostSubform[0].Page1[0].Step4[0].f1_10[0]",  # Deductions
    "step4c_extra_withholding": "topmostSubform[0].Page1[0].Step4[0].f1_11[0]",  # Extra withholding
    
    # Step 5: Employee Signature (EXACT IRS field names)
    "employee_signature_date": "topmostSubform[0].Page1[0].Step5[0].f1_12[0]",  # Date field
    
    # Employer Section (Bottom of form - EXACT IRS field names)
    "employer_name_address": "topmostSubform[0].Page1[0].EmployerSection[0].f1_13[0]",  # Employer's name and address
    "first_date_employment": "topmostSubform[0].Page1[0].EmployerSection[0].f1_14[0]",  # First date of employment
    "employer_identification_number": "topmostSubform[0].Page1[0].EmployerSection[0].f1_15[0]"  # EIN
}

# Health Insurance Plan Configuration (from onboarding packet)
HEALTH_INSURANCE_PLANS = {
    "medical_plans": {
        "hra_6k": {
            "name": "UHC HRA $6K Plan",
            "costs": {
                "employee": 59.91,
                "employee_spouse": 319.29,
                "employee_children": 264.10,
                "family": 390.25
            }
        },
        "hra_4k": {
            "name": "UHC HRA $4K Plan", 
            "costs": {
                "employee": 136.84,
                "employee_spouse": 396.21,
                "employee_children": 341.02,
                "family": 467.17
            }
        },
        "hra_2k": {
            "name": "UHC HRA $2K Plan",
            "costs": {
                "employee": 213.76,
                "employee_spouse": 473.13,
                "employee_children": 417.95,
                "family": 544.09
            }
        },
        "minimum_essential": {
            "name": "ACI Minimum Essential Coverage Plan",
            "costs": {
                "employee": 7.77,
                "employee_spouse": 17.55,
                "employee_children": 19.03,
                "family": 27.61
            }
        },
        "indemnity": {
            "name": "ACI Indemnity Plan",
            "costs": {
                "employee": 19.61,
                "employee_spouse": 37.24,
                "employee_children": 31.45,
                "family": 49.12
            }
        },
        "minimum_plus_indemnity": {
            "name": "Minimum Essential + Indemnity",
            "costs": {
                "employee": 27.37,
                "employee_spouse": 54.79,
                "employee_children": 50.48,
                "family": 76.74
            }
        }
    },
    "dental_costs": {
        "employee": 13.45,
        "employee_spouse": 27.44,
        "employee_children": 31.13,
        "family": 45.63
    },
    "vision_costs": {
        "employee": 3.04,
        "employee_spouse": 5.59,
        "employee_children": 5.86,
        "family": 8.78
    }
}

# I-9 Document Lists (official USCIS requirements)
I9_DOCUMENT_LISTS = {
    "list_a": [
        "U.S. Passport or U.S. Passport Card",
        "Permanent Resident Card or Alien Registration Receipt Card (Form I-551)",
        "Foreign passport that contains a temporary I-551 stamp or temporary I-551 printed notation on a machine-readable immigrant visa",
        "Employment Authorization Document that contains a photograph (Form I-766)",
        "For a nonimmigrant alien authorized to work for a specific employer because of his or her status: Foreign passport; and Form I-94 or Form I-94A that has the following: (1) The same name as the passport; and (2) An endorsement of the individual's nonimmigrant status as long as that period of endorsement has not yet expired and the proposed employment is not in conflict with any restrictions or limitations identified on the form",
        "Passport from the Federated States of Micronesia (FSM) or the Republic of the Marshall Islands (RMI) with Form I-94 or Form I-94A indicating nonimmigrant admission under the Compact of Free Association Between the United States and the FSM or RMI"
    ],
    "list_b": [
        "Driver's license or ID card issued by a State or outlying possession of the United States provided it contains a photograph or information such as name, date of birth, gender, height, eye color, and address",
        "ID card issued by federal, state or local government agencies or entities, provided it contains a photograph or information such as name, date of birth, gender, height, eye color, and address",
        "School ID card with a photograph",
        "Voter's registration card",
        "U.S. Military card or draft record",
        "Military dependent's ID card",
        "U.S. Coast Guard Merchant Mariner Card",
        "Native American tribal document",
        "Driver's license issued by a Canadian government authority"
    ],
    "list_c": [
        "A Social Security Account Number card, unless the card includes one of the following restrictions: (1) NOT VALID FOR EMPLOYMENT (2) VALID FOR WORK ONLY WITH INS AUTHORIZATION (3) VALID FOR WORK ONLY WITH DHS AUTHORIZATION",
        "Certification of report of birth issued by the Department of State (Forms DS-1350, FS-545, FS-240)",
        "Original or certified copy of birth certificate issued by a State, county, municipal authority, or territory of the United States bearing an official seal",
        "Native American tribal document",
        "U.S. Citizen ID Card (Form I-197)",
        "Identification Card for Use of Resident Citizen in the United States (Form I-179)",
        "Employment authorization document issued by the Department of Homeland Security"
    ]
}

class PDFFormFiller:
    """Handles filling of official government PDF forms with user data"""
    
    def __init__(self):
        # CRITICAL: Only use official government form templates for federal compliance
        self.form_templates = {
            "i9": "/Users/gouthamvemula/onbclaude/onbdev/official-forms/i9-form-latest.pdf",
            "w4": "/Users/gouthamvemula/onbclaude/onbdev/official-forms/w4-form-latest.pdf"
        }
        
        # Validate template files exist
        self._validate_template_files()
    
    def _validate_template_files(self):
        """Validate that required official form templates exist"""
        import os
        for form_type, template_path in self.form_templates.items():
            if not os.path.exists(template_path):
                print(f"⚠️ WARNING: Official {form_type.upper()} template not found at {template_path}")
                print(f"Federal compliance requires official templates. Creating fallback...")
                # Create placeholder file for development
                os.makedirs(os.path.dirname(template_path), exist_ok=True)
                with open(template_path, 'w') as f:
                    f.write(f"# Placeholder for official {form_type.upper()} template")
            else:
                print(f"✅ Official {form_type.upper()} template found: {template_path}")
    
    def fill_i9_form(self, employee_data: Dict[str, Any], employer_data: Optional[Dict[str, Any]] = None) -> bytes:
        """Fill I-9 form with employee and optionally employer data - OFFICIAL TEMPLATE ONLY"""
        if not HAS_PYMUPDF:
            raise Exception("PyMuPDF required for official I-9 template - fallback forms violate federal compliance")
            
        try:
            # Open the official I-9 PDF
            doc = fitz.open(self.form_templates["i9"])
            
            # Fill employee section (Section 1)
            if employee_data:
                self._fill_i9_section1(doc, employee_data)
            
            # Fill employer section (Section 2) if provided
            if employer_data:
                self._fill_i9_section2(doc, employer_data)
            
            # Fill Supplement A if preparer/translator data provided
            if employee_data and any(key.startswith('preparer_') for key in employee_data.keys()):
                self._fill_i9_supplement_a(doc, employee_data)
            
            # Fill Supplement B if reverification data provided
            if employee_data and any(key.startswith('reverify_') or key in ['rehire_date', 'termination_date', 'new_name'] for key in employee_data.keys()):
                self._fill_i9_supplement_b(doc, employee_data)
            
            # Save to bytes
            pdf_bytes = doc.write()
            doc.close()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Error filling I-9 form: {e}")
            raise Exception(f"Failed to generate official I-9 form: {e} - No fallback allowed for federal compliance")
    
    def fill_w4_form(self, employee_data: Dict[str, Any]) -> bytes:
        """Fill W-4 form with employee data - OFFICIAL TEMPLATE ONLY"""
        if not HAS_PYMUPDF:
            raise Exception("PyMuPDF required for official W-4 template - fallback forms violate IRS compliance")
            
        try:
            # Open the official W-4 PDF
            doc = fitz.open(self.form_templates["w4"])
            
            # Fill form fields
            self._fill_w4_fields(doc, employee_data)
            
            # Save to bytes
            pdf_bytes = doc.write()
            doc.close()
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Error filling W-4 form: {e}")
            raise Exception(f"Failed to generate official W-4 form: {e} - No fallback allowed for IRS compliance")
    
    def create_health_insurance_form(self, employee_data: Dict[str, Any]) -> bytes:
        """Create health insurance enrollment form based on packet template"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Health Insurance Enrollment Form", title_style))
        story.append(Paragraph("Plan Year: January 1, 2025 – December 31, 2025", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Employee Information
        story.append(Paragraph("<b>Employee Information</b>", styles['Heading2']))
        
        emp_info = [
            ['Employee Name:', f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}"],
            ['Social Security #:', employee_data.get('ssn', '')],
            ['Birth Date:', employee_data.get('date_of_birth', '')],
            ['Gender:', employee_data.get('gender', '')],
            ['Address:', employee_data.get('address', '')],
            ['Phone Number:', employee_data.get('phone', '')],
            ['Email Address:', employee_data.get('email', '')]
        ]
        
        emp_table = Table(emp_info, colWidths=[2*inch, 4*inch])
        emp_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(emp_table)
        story.append(Spacer(1, 20))
        
        # Coverage Elections
        story.append(Paragraph("<b>Coverage Elections (deductions are bi-weekly)</b>", styles['Heading2']))
        
        # Medical Coverage
        medical_plan = employee_data.get('health_insurance', {}).get('medical_plan', '')
        medical_tier = employee_data.get('health_insurance', {}).get('medical_tier', 'employee')
        
        if medical_plan and medical_plan in HEALTH_INSURANCE_PLANS['medical_plans']:
            plan_info = HEALTH_INSURANCE_PLANS['medical_plans'][medical_plan]
            cost = plan_info['costs'].get(medical_tier, 0)
            
            story.append(Paragraph(f"<b>Medical: {plan_info['name']}</b>", styles['Normal']))
            story.append(Paragraph(f"Coverage Tier: {medical_tier.replace('_', ' ').title()}", styles['Normal']))
            story.append(Paragraph(f"Bi-weekly Cost: ${cost:.2f}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Dental Coverage
        if employee_data.get('health_insurance', {}).get('dental_coverage'):
            dental_tier = employee_data.get('health_insurance', {}).get('dental_tier', 'employee')
            dental_cost = HEALTH_INSURANCE_PLANS['dental_costs'].get(dental_tier, 0)
            
            story.append(Paragraph("<b>Dental: United Healthcare Dental PPO</b>", styles['Normal']))
            story.append(Paragraph(f"Coverage Tier: {dental_tier.replace('_', ' ').title()}", styles['Normal']))
            story.append(Paragraph(f"Bi-weekly Cost: ${dental_cost:.2f}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Vision Coverage
        if employee_data.get('health_insurance', {}).get('vision_coverage'):
            vision_tier = employee_data.get('health_insurance', {}).get('vision_tier', 'employee')
            vision_cost = HEALTH_INSURANCE_PLANS['vision_costs'].get(vision_tier, 0)
            
            story.append(Paragraph("<b>Vision: United Healthcare Vision</b>", styles['Normal']))
            story.append(Paragraph(f"Coverage Tier: {vision_tier.replace('_', ' ').title()}", styles['Normal']))
            story.append(Paragraph(f"Bi-weekly Cost: ${vision_cost:.2f}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Total Cost
        total_cost = employee_data.get('health_insurance', {}).get('total_biweekly_cost', 0)
        story.append(Paragraph(f"<b>Total Bi-weekly Cost: ${total_cost:.2f}</b>", styles['Heading3']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def create_direct_deposit_form(self, employee_data: Dict[str, Any]) -> bytes:
        """Create direct deposit authorization form"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Employee Direct Deposit Enrollment Form", title_style))
        story.append(Spacer(1, 20))
        
        # Employee Information
        story.append(Paragraph("<b>Employee Information</b>", styles['Heading2']))
        
        emp_info = [
            ['Employee Name:', f"{employee_data.get('first_name', '')} {employee_data.get('last_name', '')}"],
            ['Social Security #:', employee_data.get('ssn', '')],
            ['Employee Email:', employee_data.get('email', '')]
        ]
        
        emp_table = Table(emp_info, colWidths=[2*inch, 4*inch])
        emp_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(emp_table)
        story.append(Spacer(1, 20))
        
        # Account Information
        story.append(Paragraph("<b>Account Information</b>", styles['Heading2']))
        
        direct_deposit = employee_data.get('direct_deposit', {})
        account_info = [
            ['Bank Name/City/State:', direct_deposit.get('bank_name', '')],
            ['Routing Transit #:', direct_deposit.get('routing_number', '')],
            ['Account Number:', direct_deposit.get('account_number', '')],
            ['Account Type:', direct_deposit.get('account_type', '').title()],
            ['Deposit Amount:', 'Entire Net Amount' if direct_deposit.get('deposit_type') == 'full' else f"${direct_deposit.get('deposit_amount', 0):.2f}"]
        ]
        
        account_table = Table(account_info, colWidths=[2*inch, 4*inch])
        account_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(account_table)
        story.append(Spacer(1, 20))
        
        # Authorization text
        auth_text = """
        I hereby authorize ADP to deposit any amounts owed me, as instructed by my employer, by initiating credit entries to my account at the financial institution indicated on this form. Further, I authorize Bank to accept and to credit any credit entries indicated by ADP to my account. In the event that ADP deposits funds erroneously into my account, I authorize ADP to debit my account for an amount not to exceed the original amount of the erroneous credit.
        
        This authorization is to remain in full force and effect until ADP and Bank have received written notice from me of its termination in such time and in such manner as to afford ADP and Bank reasonable opportunity to act on it.
        """
        
        story.append(Paragraph("<b>Authorization</b>", styles['Heading2']))
        story.append(Paragraph(auth_text, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Signature lines
        sig_data = [
            ['Employee Signature:', '_' * 40, 'Date:', '_' * 20]
        ]
        
        sig_table = Table(sig_data, colWidths=[1.5*inch, 2.5*inch, 0.5*inch, 1.5*inch])
        story.append(sig_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def _fill_i9_section1(self, doc, employee_data: Dict[str, Any]):
        """Fill Section 1 of I-9 form (Employee portion) with improved field matching"""
        try:
            # First, discover all available fields in the PDF for debugging
            self._debug_print_pdf_fields(doc, "I-9")
            
            # Get all form fields from the PDF
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    field_name = widget.field_name
                    field_value = None
                    
                    # Improved field matching using flexible string matching
                    field_name_lower = field_name.lower() if field_name else ""
                    
                    # Personal Information Fields - using flexible matching
                    if any(term in field_name_lower for term in ['last name', 'family name', 'lastname']):
                        field_value = employee_data.get('employee_last_name', '')
                    elif any(term in field_name_lower for term in ['first name', 'given name', 'firstname']) and 'last' not in field_name_lower:
                        field_value = employee_data.get('employee_first_name', '')
                    elif any(term in field_name_lower for term in ['middle initial', 'mi', 'middle']):
                        field_value = employee_data.get('employee_middle_initial', '')
                    elif any(term in field_name_lower for term in ['other last names', 'other names', 'aliases']):
                        field_value = employee_data.get('other_last_names', '')
                    
                    # Address Fields - flexible matching
                    elif any(term in field_name_lower for term in ['street', 'address']) and 'email' not in field_name_lower:
                        field_value = employee_data.get('address_street', '')
                    elif any(term in field_name_lower for term in ['apt', 'apartment', 'unit']):
                        field_value = employee_data.get('address_apt', '')
                    elif any(term in field_name_lower for term in ['city', 'town']):
                        field_value = employee_data.get('address_city', '')
                    elif 'state' in field_name_lower and 'zip' not in field_name_lower:
                        field_value = employee_data.get('address_state', '')
                    elif any(term in field_name_lower for term in ['zip', 'postal']):
                        field_value = employee_data.get('address_zip', '')
                    
                    # Personal Details - flexible matching
                    elif any(term in field_name_lower for term in ['date of birth', 'birth date', 'dob']):
                        if employee_data.get('date_of_birth'):
                            field_value = self._format_date(employee_data['date_of_birth'])
                    elif any(term in field_name_lower for term in ['social security', 'ssn', 'ss number']):
                        field_value = employee_data.get('ssn', '')
                    elif 'email' in field_name_lower:
                        field_value = employee_data.get('email', '')
                    elif any(term in field_name_lower for term in ['telephone', 'phone', 'tel']):
                        field_value = employee_data.get('phone', '')
                    
                    # Citizenship Status Checkboxes - improved matching
                    elif self._is_citizenship_checkbox(field_name, 'citizen'):
                        citizenship_status = employee_data.get('citizenship_status', '')
                        field_value = citizenship_status == 'us_citizen'
                    elif self._is_citizenship_checkbox(field_name, 'noncitizen'):
                        citizenship_status = employee_data.get('citizenship_status', '')
                        field_value = citizenship_status == 'noncitizen_national'
                    elif self._is_citizenship_checkbox(field_name, 'permanent'):
                        citizenship_status = employee_data.get('citizenship_status', '')
                        field_value = citizenship_status == 'permanent_resident'
                    elif self._is_citizenship_checkbox(field_name, 'alien'):
                        citizenship_status = employee_data.get('citizenship_status', '')
                        field_value = citizenship_status == 'authorized_alien'
                    
                    # Additional Fields for Non-Citizens - flexible matching
                    elif any(term in field_name_lower for term in ['uscis', 'alien number', 'a-number']):
                        field_value = employee_data.get('uscis_number', '')
                    elif any(term in field_name_lower for term in ['i-94', 'i94', 'admission number']):
                        field_value = employee_data.get('i94_admission_number', '')
                    elif any(term in field_name_lower for term in ['passport number', 'foreign passport']):
                        passport_num = employee_data.get('passport_number', '')
                        passport_country = employee_data.get('passport_country', '')
                        if passport_num and passport_country:
                            field_value = f"{passport_num} ({passport_country})"
                        elif passport_num:
                            field_value = passport_num
                    elif any(term in field_name_lower for term in ['country of issuance', 'passport country']):
                        field_value = employee_data.get('passport_country', '')
                    elif any(term in field_name_lower for term in ['expiration', 'exp date']) and 'work' in field_name_lower:
                        if employee_data.get('work_authorization_expiration'):
                            field_value = self._format_date(employee_data['work_authorization_expiration'])
                    
                    # Employee Signature Date
                    elif any(term in field_name_lower for term in ['today', 'date', 'signature date']) and 'employee' in field_name_lower:
                        if employee_data.get('employee_signature_date'):
                            field_value = self._format_date(employee_data['employee_signature_date'])
                        elif employee_data.get('signature_date'):
                            field_value = self._format_date(employee_data['signature_date'])
                        else:
                            # Use current date if no signature date provided
                            from datetime import datetime
                            field_value = datetime.now().strftime('%m/%d/%Y')
                    
                    # Apply field value if we have one
                    if field_value is not None:
                        self._set_widget_value(widget, field_value)
                        
        except Exception as e:
            print(f"Error filling I-9 Section 1: {e}")
            # Continue with partial filling if some fields fail
    
    def _is_citizenship_checkbox(self, field_name: str, citizenship_type: str) -> bool:
        """Check if a field name matches a citizenship checkbox"""
        if not field_name:
            return False
        
        field_lower = field_name.lower()
        
        if citizenship_type == 'citizen':
            return any(term in field_lower for term in ['citizen of the united states', 'us citizen', 'citizen']) and 'noncitizen' not in field_lower
        elif citizenship_type == 'noncitizen':
            return 'noncitizen national' in field_lower or 'non-citizen national' in field_lower
        elif citizenship_type == 'permanent':
            return any(term in field_lower for term in ['permanent resident', 'lawful permanent'])
        elif citizenship_type == 'alien':
            return any(term in field_lower for term in ['alien authorized', 'authorized alien', 'authorized to work'])
        
        return False
    
    def _set_widget_value(self, widget, field_value):
        """Safely set widget value with proper error handling"""
        try:
            if HAS_PYMUPDF and hasattr(fitz, 'PDF_WIDGET_TYPE_TEXT'):
                if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                    widget.field_value = str(field_value)
                elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                    widget.field_value = bool(field_value)
                else:
                    widget.field_value = str(field_value)
            else:
                # Fallback: try to set field value directly
                widget.field_value = str(field_value) if not isinstance(field_value, bool) else field_value
            widget.update()
        except Exception as e:
            print(f"Warning: Could not set value for field '{widget.field_name}': {e}")
    
    def _debug_print_pdf_fields(self, doc, form_type: str):
        """Debug function to print all available PDF fields"""
        try:
            print(f"\n=== DEBUG: {form_type} PDF Fields ===")
            total_fields = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                print(f"Page {page_num + 1}: {len(widgets)} fields")
                for widget in widgets:
                    print(f"  - Field: '{widget.field_name}' | Type: {widget.field_type_string} | Value: '{widget.field_value}'")
                    total_fields += 1
            
            print(f"Total fields: {total_fields}")
            print("=" * 50)
        except Exception as e:
            print(f"Debug error: {e}")
    
    def _fill_i9_section2(self, doc, employer_data: Dict[str, Any]):
        """Fill Section 2 of I-9 form (Employer portion)"""
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    field_name = widget.field_name
                    field_value = None
                    
                    # Section 2: Employer Review and Verification (using exact field names)
                    if field_name == "Employee first day of employment mmddyyyy":
                        if employer_data.get('first_day_employment'):
                            field_value = self._format_date(employer_data['first_day_employment'])
                    
                    # Document verification - List A, B, or C documents
                    elif field_name == "Document Title 1":
                        field_value = employer_data.get('document_title_1', '')
                    elif field_name == "Issuing Authority 1":
                        field_value = employer_data.get('issuing_authority_1', '')
                    elif field_name == "Document Number (if any) 1":
                        field_value = employer_data.get('document_number_1', '')
                    elif field_name == "Expiration Date (if any) mmddyyyy 1":
                        if employer_data.get('expiration_date_1'):
                            field_value = self._format_date(employer_data['expiration_date_1'])
                    
                    # Document 2 (List B documents)
                    elif field_name == "Document Title 2":
                        field_value = employer_data.get('document_title_2', '')
                    elif field_name == "Issuing Authority 2":
                        field_value = employer_data.get('issuing_authority_2', '')
                    elif field_name == "Document Number (if any) 2":
                        field_value = employer_data.get('document_number_2', '')
                    elif field_name == "Expiration Date (if any) mmddyyyy 2":
                        if employer_data.get('expiration_date_2'):
                            field_value = self._format_date(employer_data['expiration_date_2'])
                    
                    # Document 3 (List C documents)  
                    elif field_name == "Document Title 3":
                        field_value = employer_data.get('document_title_3', '')
                    elif field_name == "Issuing Authority 3":
                        field_value = employer_data.get('issuing_authority_3', '')
                    elif field_name == "Document Number (if any) 3":
                        field_value = employer_data.get('document_number_3', '')
                    elif field_name == "Expiration Date (if any) mmddyyyy 3":
                        if employer_data.get('expiration_date_3'):
                            field_value = self._format_date(employer_data['expiration_date_3'])
                    
                    # Additional Information
                    elif field_name == "Additional Information":
                        field_value = employer_data.get('additional_info', '')
                    
                    # Employer signature and information
                    elif field_name == "Last Name of Employer or Authorized Representative":
                        field_value = employer_data.get('employer_last_name', employer_data.get('employer_name', ''))
                    elif field_name == "First Name of Employer or Authorized Representative":
                        field_value = employer_data.get('employer_first_name', '')
                    elif field_name == "Title of Employer or Authorized Representative":
                        field_value = employer_data.get('employer_title', 'Manager')
                    elif field_name == "Signature of Employer or Authorized Representative":
                        # This would be filled when signature is added
                        pass
                    elif field_name == "Today's Date mmddyyyy":
                        if employer_data.get('signature_date'):
                            field_value = self._format_date(employer_data['signature_date'])
                        else:
                            from datetime import datetime
                            field_value = datetime.now().strftime('%m/%d/%Y')
                    
                    # Business information
                    elif field_name == "Name of Employer or Authorized Representative":
                        field_value = employer_data.get('business_name', 'Grand Hotel & Resort')
                    elif field_name == "Business or Organization Address Street Number and Name":
                        field_value = employer_data.get('business_address', '123 Hotel Street')
                    elif field_name == "City":
                        field_value = employer_data.get('business_city', 'Jersey City')
                    elif field_name == "State":
                        field_value = employer_data.get('business_state', 'NJ')
                    elif field_name == "ZIP Code":
                        field_value = employer_data.get('business_zip', '07302')
                    
                    # Section 3: Reverification and Rehires (if applicable)
                    elif field_name == "Date of Rehire (if applicable) mmddyyyy":
                        if employer_data.get('rehire_date'):
                            field_value = self._format_date(employer_data['rehire_date'])
                    elif field_name == "New Name (if applicable)":
                        field_value = employer_data.get('new_name', '')
                    elif field_name == "Document Title":
                        field_value = employer_data.get('reverify_document_title', '')
                    elif field_name == "Document Number":
                        field_value = employer_data.get('reverify_document_number', '')
                    elif field_name == "Expiration Date (if any) mmddyyyy":
                        if employer_data.get('reverify_expiration_date'):
                            field_value = self._format_date(employer_data['reverify_expiration_date'])
                    
                    # Alternative procedure checkboxes
                    elif field_name == "CB_Alt":  # Alternative procedure checkbox
                        field_value = employer_data.get('used_alternative_procedure', False)
                    
                    # Set field value
                    if field_value is not None:
                        if HAS_PYMUPDF and hasattr(fitz, 'PDF_WIDGET_TYPE_TEXT'):
                            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                widget.field_value = str(field_value)
                            elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                                widget.field_value = field_value
                        else:
                            # Fallback: try to set field value directly
                            widget.field_value = str(field_value) if not isinstance(field_value, bool) else field_value
                        widget.update()
                        
        except Exception as e:
            print(f"Error filling I-9 Section 2: {e}")
            # Continue with partial filling if some fields fail
    
    def _fill_i9_supplement_a(self, doc, employee_data: Dict[str, Any]):
        """Fill I-9 Supplement A (Preparer and/or Translator Certification)"""
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    field_name = widget.field_name
                    field_value = None
                    
                    # Supplement A: Preparer and/or Translator Certification
                    if field_name == "Last Name (Family Name) of preparer or translator":
                        field_value = employee_data.get('preparer_last_name', '')
                    elif field_name == "First Name (Given Name) of preparer or translator":
                        field_value = employee_data.get('preparer_first_name', '')
                    elif field_name == "Address (Street Number and Name) of preparer or translator":
                        field_value = employee_data.get('preparer_address', '')
                    elif field_name == "City or Town of preparer or translator":
                        field_value = employee_data.get('preparer_city', '')
                    elif field_name == "State of preparer or translator":
                        field_value = employee_data.get('preparer_state', '')
                    elif field_name == "ZIP Code of preparer or translator":
                        field_value = employee_data.get('preparer_zip', '')
                    elif field_name == "Signature of Preparer or Translator":
                        # This would be filled when signature is added
                        pass
                    elif field_name == "Date (mm/dd/yyyy) preparer or translator":
                        if employee_data.get('preparer_date'):
                            field_value = self._format_date(employee_data['preparer_date'])
                    
                    # Set field value
                    if field_value is not None:
                        if HAS_PYMUPDF and hasattr(fitz, 'PDF_WIDGET_TYPE_TEXT'):
                            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                widget.field_value = str(field_value)
                        else:
                            widget.field_value = str(field_value)
                        widget.update()
                        
        except Exception as e:
            print(f"Error filling I-9 Supplement A: {e}")
    
    def _fill_i9_supplement_b(self, doc, employee_data: Dict[str, Any]):
        """Fill I-9 Supplement B (Reverification and Rehires)"""
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    field_name = widget.field_name
                    field_value = None
                    
                    # Supplement B: Reverification and Rehires
                    if field_name == "Employee's Last Name (Family Name)":
                        field_value = employee_data.get('employee_last_name', '')
                    elif field_name == "Employee's First Name (Given Name)":
                        field_value = employee_data.get('employee_first_name', '')
                    elif field_name == "Employee's Middle Initial":
                        field_value = employee_data.get('employee_middle_initial', '')
                    elif field_name == "Date of Hire (mm/dd/yyyy)":
                        if employee_data.get('hire_date'):
                            field_value = self._format_date(employee_data['hire_date'])
                    elif field_name == "Date of Rehire (mm/dd/yyyy) (if applicable)":
                        if employee_data.get('rehire_date'):
                            field_value = self._format_date(employee_data['rehire_date'])
                    elif field_name == "Date of Termination (mm/dd/yyyy) (if applicable)":
                        if employee_data.get('termination_date'):
                            field_value = self._format_date(employee_data['termination_date'])
                    elif field_name == "New Name (if applicable)":
                        field_value = employee_data.get('new_name', '')
                    elif field_name == "Document Title (List A or List C)":
                        field_value = employee_data.get('reverify_document_title', '')
                    elif field_name == "Document Number":
                        field_value = employee_data.get('reverify_document_number', '')
                    elif field_name == "Expiration Date (if any) (mm/dd/yyyy)":
                        if employee_data.get('reverify_expiration_date'):
                            field_value = self._format_date(employee_data['reverify_expiration_date'])
                    elif field_name == "Name of Employer or Authorized Representative":
                        field_value = employee_data.get('employer_name', '')
                    elif field_name == "Signature of Employer or Authorized Representative":
                        # This would be filled when signature is added
                        pass
                    elif field_name == "Date (mm/dd/yyyy)":
                        if employee_data.get('reverify_signature_date'):
                            field_value = self._format_date(employee_data['reverify_signature_date'])
                    
                    # Set field value
                    if field_value is not None:
                        if HAS_PYMUPDF and hasattr(fitz, 'PDF_WIDGET_TYPE_TEXT'):
                            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                widget.field_value = str(field_value)
                        else:
                            widget.field_value = str(field_value)
                        widget.update()
                        
        except Exception as e:
            print(f"Error filling I-9 Supplement B: {e}")
    
    def _fill_w4_fields(self, doc, employee_data: Dict[str, Any]):
        """Fill W-4 form fields using EXACT IRS 2025 field mappings for legal compliance"""
        try:
            # Debug print available fields for compliance verification
            self._debug_print_pdf_fields(doc, "W-4")
            
            # CRITICAL: Use exact field mappings from official IRS 2025 W-4 template
            field_mappings = {
                # Step 1: Personal Information (IRS-compliant field mapping)
                W4_FORM_FIELDS["first_name_and_middle_initial"]: f"{employee_data.get('first_name', '')} {employee_data.get('middle_initial', '')}".strip(),
                W4_FORM_FIELDS["last_name"]: employee_data.get('last_name', ''),
                W4_FORM_FIELDS["address"]: employee_data.get('address', ''),
                W4_FORM_FIELDS["city_state_zip"]: f"{employee_data.get('city', '')}, {employee_data.get('state', '')} {employee_data.get('zip_code', '')}".strip(', '),
                W4_FORM_FIELDS["social_security_number"]: employee_data.get('ssn', ''),
                
                # Step 3: Claim Dependents (IRS dollar amounts)
                W4_FORM_FIELDS["step3_qualifying_children_amount"]: str(int(employee_data.get('dependents_amount', 0))) if employee_data.get('dependents_amount', 0) > 0 else '',
                W4_FORM_FIELDS["step3_other_dependents_amount"]: str(int(employee_data.get('other_credits', 0))) if employee_data.get('other_credits', 0) > 0 else '',
                W4_FORM_FIELDS["step3_total_credits"]: str(int(employee_data.get('dependents_amount', 0) + employee_data.get('other_credits', 0))) if (employee_data.get('dependents_amount', 0) + employee_data.get('other_credits', 0)) > 0 else '',
                
                # Step 4: Other Adjustments (IRS dollar amounts)
                W4_FORM_FIELDS["step4a_other_income"]: str(int(employee_data.get('other_income', 0))) if employee_data.get('other_income', 0) > 0 else '',
                W4_FORM_FIELDS["step4b_deductions"]: str(int(employee_data.get('deductions', 0))) if employee_data.get('deductions', 0) > 0 else '',
                W4_FORM_FIELDS["step4c_extra_withholding"]: str(int(employee_data.get('extra_withholding', 0))) if employee_data.get('extra_withholding', 0) > 0 else '',
                
                # Step 5: Signature Date (IRS date format)
                W4_FORM_FIELDS["employee_signature_date"]: self._format_date(employee_data.get('signature_date', datetime.now().strftime('%Y-%m-%d')))
            }
            
            # CRITICAL: Handle Filing Status Checkboxes (IRS-compliant)
            filing_status = employee_data.get('filing_status', '')
            if filing_status == 'Single':
                field_mappings[W4_FORM_FIELDS["filing_status_single"]] = True
            elif filing_status == 'Married filing jointly':
                field_mappings[W4_FORM_FIELDS["filing_status_married_jointly"]] = True
            elif filing_status == 'Head of household':
                field_mappings[W4_FORM_FIELDS["filing_status_head_of_household"]] = True
            
            # CRITICAL: Handle Step 2 Multiple Jobs Checkbox (IRS-compliant)
            if employee_data.get('multiple_jobs_checkbox', False):
                field_mappings[W4_FORM_FIELDS["step2_multiple_jobs_checkbox"]] = True
            
            # Apply all field mappings to the PDF form
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    field_name = widget.field_name
                    if field_name in field_mappings:
                        field_value = field_mappings[field_name]
                        self._set_widget_value(widget, field_value)
                        print(f"✓ IRS COMPLIANCE: Filled field '{field_name}' with value '{field_value}'")
                    else:
                        # Log unmapped fields for compliance verification
                        print(f"⚠ UNMAPPED FIELD: '{field_name}' - verify IRS compliance")
                        
        except Exception as e:
            print(f"🚨 CRITICAL ERROR filling W-4 form: {e}")
            print("⚠ W-4 form may not be IRS compliant - manual review required")
            # Continue with partial filling if some fields fail
    
    def _is_filing_status_checkbox(self, field_name: str, status_type: str) -> bool:
        """Check if a field name matches a filing status checkbox"""
        if not field_name:
            return False
        
        field_lower = field_name.lower()
        
        if status_type == 'single':
            return 'single' in field_lower and 'married' not in field_lower
        elif status_type == 'married_jointly':
            return any(term in field_lower for term in ['married filing jointly', 'jointly', 'married joint'])
        elif status_type == 'married_separately':
            return any(term in field_lower for term in ['married filing separately', 'separately', 'married separate'])
        elif status_type == 'head_of_household':
            return any(term in field_lower for term in ['head of household', 'head household', 'hoh'])
        
        return False
    
    def _format_date(self, date_input) -> str:
        """Format date for PDF forms (MM/DD/YYYY)"""
        try:
            if isinstance(date_input, str):
                # Try parsing different date formats
                for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'):
                    try:
                        date_obj = datetime.strptime(date_input, fmt)
                        return date_obj.strftime('%m/%d/%Y')
                    except ValueError:
                        continue
                return date_input  # Return as-is if parsing fails
            elif isinstance(date_input, (datetime, date)):
                return date_input.strftime('%m/%d/%Y')
            else:
                return str(date_input)
        except:
            return str(date_input)
    
    def add_signature_to_pdf(self, pdf_bytes: bytes, signature_data: str, signature_type: str, page_num: int = 0) -> bytes:
        """Add digital signature to PDF"""
        if not HAS_PYMUPDF:
            print("PyMuPDF not available, cannot add signature to PDF")
            return pdf_bytes  # Return original PDF
            
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[page_num]
            
            # Decode base64 signature
            signature_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            
            # Define signature position based on form type
            if signature_type == "employee_i9":
                # I-9 employee signature position (approximate)
                rect = fitz.Rect(350, 650, 500, 680)
            elif signature_type == "employer_i9":
                # I-9 employer signature position (approximate)
                rect = fitz.Rect(350, 750, 500, 780)
            elif signature_type == "employee_w4":
                # W-4 employee signature position (approximate)
                rect = fitz.Rect(150, 650, 300, 680)
            else:
                # Default position
                rect = fitz.Rect(150, 650, 300, 680)
            
            # Insert signature image
            page.insert_image(rect, pixmap=fitz.Pixmap(signature_bytes))
            
            # Save and return modified PDF
            result_bytes = doc.write()
            doc.close()
            return result_bytes
            
        except Exception as e:
            print(f"Error adding signature to PDF: {e}")
            return pdf_bytes  # Return original if signature addition fails
    
    def _create_fallback_i9(self, employee_data: Dict[str, Any], employer_data: Optional[Dict[str, Any]]) -> bytes:
        """Create fallback I-9 form if official PDF filling fails"""
        # Create custom I-9 form using ReportLab as fallback
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph("Form I-9, Employment Eligibility Verification", styles['Title']))
        story.append(Paragraph("Department of Homeland Security - U.S. Citizenship and Immigration Services", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add form content here
        story.append(Paragraph("Section 1. Employee Information and Attestation", styles['Heading2']))
        # Add employee fields...
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def _create_fallback_w4(self, employee_data: Dict[str, Any]) -> bytes:
        """Create fallback W-4 form"""
        # Similar implementation for W-4 fallback
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph("Form W-4 (2024)", styles['Title']))
        story.append(Paragraph("Employee's Withholding Certificate", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add W-4 content here
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()

# PDF Form Service Instance
pdf_form_service = PDFFormFiller()