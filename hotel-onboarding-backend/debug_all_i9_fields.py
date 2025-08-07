#!/usr/bin/env python3
"""
Enhanced debug script to extract ALL field names from the I-9 PDF form.
This will help us get the exact field names for Supplements A and B.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])
    import fitz

def extract_all_pdf_fields(pdf_path):
    """Extract all field names from all pages of the PDF form."""
    try:
        doc = fitz.open(pdf_path)
        print(f"✅ Opened PDF: {pdf_path}")
        print(f"📄 Total pages: {doc.page_count}")
        print("=" * 80)
        
        all_fields_by_page = {}
        total_fields = 0
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            widgets = page.widgets()
            
            print(f"\n📋 PAGE {page_num + 1} FIELD ANALYSIS:")
            print("-" * 50)
            
            if not widgets:
                print("  ❌ No form fields found on this page")
                continue
            
            page_fields = []
            for widget_idx, widget in enumerate(widgets):
                field_info = {
                    'name': widget.field_name,
                    'type': widget.field_type_string,
                    'value': widget.field_value,
                    'rect': str(widget.rect)
                }
                page_fields.append(field_info)
                total_fields += 1
                
                print(f"  {widget_idx + 1:2d}. Field Name: '{widget.field_name}'")
                print(f"      Type: {widget.field_type_string}")
                print(f"      Current Value: '{widget.field_value}'")
                print(f"      Position: {widget.rect}")
                print()
            
            all_fields_by_page[f'page_{page_num + 1}'] = page_fields
        
        doc.close()
        
        # Create summary by page
        print("\n" + "=" * 80)
        print("📊 COMPLETE FIELD SUMMARY")
        print("=" * 80)
        print(f"Total fields found: {total_fields}")
        
        for page_key, fields in all_fields_by_page.items():
            page_num = page_key.split('_')[1]
            print(f"\n📄 PAGE {page_num} FIELDS ({len(fields)} total):")
            print("-" * 40)
            
            for i, field in enumerate(fields, 1):
                if field['name']:  # Only show fields with names
                    print(f"  {i:2d}. \"{field['name']}\" ({field['type']})")
        
        # Generate Python code for field mapping
        print("\n" + "=" * 80)
        print("🐍 PYTHON FIELD MAPPING CODE")
        print("=" * 80)
        
        for page_key, fields in all_fields_by_page.items():
            page_num = page_key.split('_')[1]
            print(f"\n# PAGE {page_num} FIELD MAPPINGS:")
            
            for field in fields:
                if field['name'] and field['type'] == 'Text':
                    safe_name = field['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
                    print(f"elif field_name == \"{field['name']}\":")
                    print(f"    field_value = data.get('{safe_name}', '')")
                elif field['name'] and field['type'] == 'CheckBox':
                    print(f"elif field_name == \"{field['name']}\":")
                    print(f"    field_value = data.get('checkbox_{field['name'].lower()}', False)")
        
        return all_fields_by_page
        
    except Exception as e:
        print(f"❌ Error processing PDF: {str(e)}")
        return None

def main():
    """Main function to run the enhanced field extraction."""
    pdf_path = "/Users/gouthamvemula/onbclaude/onbdev/official-forms/i9-form-latest.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        sys.exit(1)
    
    print("🔍 I-9 PDF COMPLETE FIELD EXTRACTOR")
    print("=" * 80)
    print(f"Analyzing: {pdf_path}")
    
    fields = extract_all_pdf_fields(pdf_path)
    
    if fields:
        print("\n" + "=" * 80)
        print("✅ Field extraction completed successfully!")
        print("Use the field names exactly as shown above in your form mapping.")
        print("Copy the Python code snippets to update your field mappings.")
    else:
        print("❌ Failed to extract fields from the PDF.")
        sys.exit(1)

if __name__ == "__main__":
    main()