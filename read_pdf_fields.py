#!/usr/bin/env python3
"""
Script to read and analyze PDF form fields to verify they are properly filled
"""

import fitz  # PyMuPDF
import sys
import os
from datetime import datetime

def analyze_pdf_fields(pdf_path):
    """Analyze PDF form fields and their values"""
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        print(f"📄 Analyzing PDF: {pdf_path}")
        print(f"📄 File size: {os.path.getsize(pdf_path)} bytes")
        print(f"📄 Number of pages: {len(doc)}")
        print("=" * 60)
        
        # Track important fields
        important_fields = {
            'gender': [],
            'dental': [],
            'vision': [],
            'personal_info': [],
            'checkboxes': [],
            'text_fields': []
        }
        
        total_fields = 0
        filled_fields = 0
        
        # Analyze each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n📋 PAGE {page_num + 1} ANALYSIS:")
            print("-" * 40)
            
            widgets = page.widgets()
            page_fields = 0
            page_filled = 0
            
            for widget in widgets:
                total_fields += 1
                page_fields += 1
                
                field_name = widget.field_name
                field_type = widget.field_type_string
                field_value = widget.field_value
                
                # Check if field is filled
                is_filled = False
                if field_type == "CheckBox":
                    is_filled = bool(field_value) and field_value not in ['', 'Off', False]
                elif field_type == "Text":
                    is_filled = bool(field_value) and str(field_value).strip() != ''
                elif field_type == "Button":
                    is_filled = bool(field_value) and field_value not in ['', 'Off', False]
                
                if is_filled:
                    filled_fields += 1
                    page_filled += 1
                
                # Categorize important fields
                field_name_lower = field_name.lower()
                
                if 'gender' in field_name_lower or field_name in ['Male', 'Female', 'M', 'F']:
                    important_fields['gender'].append({
                        'name': field_name,
                        'type': field_type,
                        'value': field_value,
                        'filled': is_filled
                    })
                
                elif 'dental' in field_name_lower or 'employee only_6' in field_name_lower:
                    important_fields['dental'].append({
                        'name': field_name,
                        'type': field_type,
                        'value': field_value,
                        'filled': is_filled
                    })
                
                elif 'vision' in field_name_lower or 'decline vision' in field_name_lower:
                    important_fields['vision'].append({
                        'name': field_name,
                        'type': field_type,
                        'value': field_value,
                        'filled': is_filled
                    })
                
                elif any(keyword in field_name_lower for keyword in ['name', 'address', 'phone', 'email', 'ssn']):
                    important_fields['personal_info'].append({
                        'name': field_name,
                        'type': field_type,
                        'value': field_value,
                        'filled': is_filled
                    })
                
                elif field_type == "CheckBox":
                    important_fields['checkboxes'].append({
                        'name': field_name,
                        'type': field_type,
                        'value': field_value,
                        'filled': is_filled
                    })
                
                elif field_type == "Text":
                    important_fields['text_fields'].append({
                        'name': field_name,
                        'type': field_type,
                        'value': field_value,
                        'filled': is_filled
                    })
                
                # Print field details
                status = "✅ FILLED" if is_filled else "❌ EMPTY"
                print(f"  {status} | {field_type:10} | {field_name:30} | {str(field_value)[:50]}")
            
            print(f"\n📊 Page {page_num + 1} Summary: {page_filled}/{page_fields} fields filled")
        
        # Print detailed analysis
        print("\n" + "=" * 60)
        print("🔍 DETAILED FIELD ANALYSIS")
        print("=" * 60)
        
        # Gender analysis
        print(f"\n👤 GENDER FIELDS ({len(important_fields['gender'])} found):")
        for field in important_fields['gender']:
            status = "✅" if field['filled'] else "❌"
            print(f"  {status} {field['name']} ({field['type']}): {field['value']}")
        
        # Dental analysis
        print(f"\n🦷 DENTAL FIELDS ({len(important_fields['dental'])} found):")
        for field in important_fields['dental']:
            status = "✅" if field['filled'] else "❌"
            print(f"  {status} {field['name']} ({field['type']}): {field['value']}")
        
        # Vision analysis
        print(f"\n👁️ VISION FIELDS ({len(important_fields['vision'])} found):")
        for field in important_fields['vision']:
            status = "✅" if field['filled'] else "❌"
            print(f"  {status} {field['name']} ({field['type']}): {field['value']}")
        
        # Personal info analysis
        print(f"\n📝 PERSONAL INFO FIELDS ({len(important_fields['personal_info'])} found):")
        for field in important_fields['personal_info']:
            status = "✅" if field['filled'] else "❌"
            value_display = str(field['value'])[:30] + "..." if len(str(field['value'])) > 30 else str(field['value'])
            print(f"  {status} {field['name']} ({field['type']}): {value_display}")
        
        # Overall summary
        print(f"\n" + "=" * 60)
        print("📊 OVERALL SUMMARY")
        print("=" * 60)
        print(f"📄 Total form fields: {total_fields}")
        print(f"✅ Filled fields: {filled_fields}")
        print(f"❌ Empty fields: {total_fields - filled_fields}")
        print(f"📈 Fill percentage: {(filled_fields/total_fields*100):.1f}%" if total_fields > 0 else "📈 Fill percentage: 0%")
        
        # Key findings
        print(f"\n🎯 KEY FINDINGS:")
        gender_filled = any(f['filled'] for f in important_fields['gender'])
        dental_filled = any(f['filled'] for f in important_fields['dental'])
        vision_filled = any(f['filled'] for f in important_fields['vision'])
        
        print(f"  👤 Gender selection: {'✅ WORKING' if gender_filled else '❌ NOT WORKING'}")
        print(f"  🦷 Dental coverage: {'✅ WORKING' if dental_filled else '❌ NOT WORKING'}")
        print(f"  👁️ Vision coverage: {'✅ WORKING' if vision_filled else '❌ NOT WORKING'}")
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return False

def main():
    # Look for the most recent health insurance test PDF
    pdf_files = [f for f in os.listdir('.') if f.startswith('health_insurance_test_') and f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No health insurance test PDF files found in current directory")
        print("💡 Run the test script first to generate a PDF")
        return
    
    # Use the most recent file
    pdf_files.sort(reverse=True)
    latest_pdf = pdf_files[0]
    
    print(f"🔍 Found PDF file: {latest_pdf}")
    analyze_pdf_fields(latest_pdf)

if __name__ == "__main__":
    main()
