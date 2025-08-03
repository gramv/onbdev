#!/usr/bin/env python3
"""
Check which fields are on which pages of the I-9 PDF
"""

import PyPDF2
from pathlib import Path

def check_field_pages(pdf_path):
    """Check which fields appear on which pages"""
    
    print(f"Analyzing PDF: {pdf_path}\n")
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        if '/AcroForm' not in pdf_reader.trailer['/Root']:
            print("No AcroForm found in PDF")
            return
            
        # Get all fields
        fields = pdf_reader.get_fields()
        if not fields:
            print("No form fields found")
            return
        
        # Group fields by page
        fields_by_page = {}
        duplicate_fields = {}
        
        for field_name, field_obj in fields.items():
            # Try to determine which page this field is on
            # This is tricky in PyPDF2, so we'll look for common patterns
            
            # Check if field name contains hints about its section
            field_lower = field_name.lower()
            
            # Supplement A typically has preparer/translator fields
            if any(term in field_lower for term in ['preparer', 'translator', 'supplement']):
                page_hint = "Supplement A (Page 2 or 3)"
            # Section 2 fields
            elif any(term in field_lower for term in ['section 2', 'list a', 'list b', 'list c', 'document title', 'issuing authority']):
                page_hint = "Section 2 (Page 2)"
            # Section 1 fields
            else:
                page_hint = "Section 1 (Page 1)"
            
            if field_name not in fields_by_page:
                fields_by_page[field_name] = []
            fields_by_page[field_name].append(page_hint)
            
            # Track duplicates
            if field_name in duplicate_fields:
                duplicate_fields[field_name] += 1
            else:
                duplicate_fields[field_name] = 1
        
        # Report findings
        print("=== FIELDS THAT APPEAR MULTIPLE TIMES ===")
        for field_name, count in sorted(duplicate_fields.items()):
            if "Last Name" in field_name or "First Name" in field_name or "Middle" in field_name:
                print(f"\n'{field_name}':")
                print(f"  Likely appears in: {fields_by_page[field_name]}")
                print(f"  WARNING: When filled, ALL instances will be filled!")
        
        print("\n\n=== ALL FIELDS BY SECTION ===")
        
        # Section 1 fields
        print("\nSECTION 1 FIELDS (Employee):")
        section1_fields = []
        for field_name in sorted(fields.keys()):
            field_lower = field_name.lower()
            if not any(term in field_lower for term in ['section 2', 'list a', 'list b', 'list c', 'preparer', 'translator', 'supplement']):
                section1_fields.append(field_name)
        
        for field in section1_fields[:20]:  # First 20 fields
            print(f"  - {field}")
        
        # Section 2 fields
        print("\n\nSECTION 2 FIELDS (Employer):")
        section2_fields = []
        for field_name in sorted(fields.keys()):
            field_lower = field_name.lower()
            if any(term in field_lower for term in ['section 2', 'list a', 'list b', 'list c', 'document title', 'issuing authority']):
                section2_fields.append(field_name)
        
        for field in section2_fields[:20]:  # First 20 fields
            print(f"  - {field}")
        
        # Supplement A fields
        print("\n\nSUPPLEMENT A FIELDS (Preparer/Translator):")
        supp_a_fields = []
        for field_name in sorted(fields.keys()):
            field_lower = field_name.lower()
            if any(term in field_lower for term in ['preparer', 'translator']):
                supp_a_fields.append(field_name)
        
        for field in supp_a_fields[:20]:  # First 20 fields
            print(f"  - {field}")
        
        # Check for the specific fields we're filling
        print("\n\n=== CHECKING OUR FILLED FIELDS ===")
        our_fields = [
            'Last Name (Family Name)',
            'First Name Given Name', 
            'Employee Middle Initial (if any)',
            'Date of Birth mmddyyyy',
            'Address Street Number and Name'
        ]
        
        for field_name in our_fields:
            if field_name in fields:
                print(f"\n'{field_name}':")
                print(f"  Found in PDF: YES")
                # Check if similar field names exist
                similar = [f for f in fields.keys() if field_name.split()[0] in f and f != field_name]
                if similar:
                    print(f"  Similar fields found:")
                    for sim in similar:
                        print(f"    - {sim}")

if __name__ == "__main__":
    pdf_path = "/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-frontend/public/i9-form-template.pdf"
    
    if Path(pdf_path).exists():
        check_field_pages(pdf_path)
    else:
        print(f"PDF file not found: {pdf_path}")