#!/usr/bin/env python3
"""
Analyze Direct Deposit PDF to extract field names, types, and positions
"""

import fitz  # PyMuPDF
import json
from pathlib import Path
import sys

def analyze_pdf_fields(pdf_path):
    """Extract all field information from a PDF"""
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        # Get the first page
        page = doc[0]
        
        print(f"\n{'='*60}")
        print(f"PDF Analysis: {pdf_path}")
        print(f"{'='*60}")
        print(f"Page size: {page.rect.width} x {page.rect.height}")
        print(f"Page rotation: {page.rotation}")
        
        # Check for form fields
        widgets = page.widgets()
        field_data = {}
        
        if widgets:
            print(f"\n📋 Found {len(list(page.widgets()))} form fields:")
            print("-" * 50)
            
            for widget in page.widgets():
                field_name = widget.field_name
                field_type = widget.field_type
                field_type_str = {
                    0: "Button",
                    1: "CheckBox", 
                    2: "RadioButton",
                    3: "Text",
                    4: "RichText",
                    5: "List",
                    6: "ComboBox",
                    7: "Signature"
                }.get(field_type, f"Unknown ({field_type})")
                
                rect = widget.rect
                field_value = widget.field_value
                field_flags = widget.field_flags
                
                print(f"\n  Field: {field_name}")
                print(f"    Type: {field_type_str}")
                print(f"    Position: x={rect.x0:.2f}, y={rect.y0:.2f}")
                print(f"    Size: {rect.width:.2f} x {rect.height:.2f}")
                print(f"    Current Value: {field_value}")
                print(f"    Flags: {field_flags}")
                
                # Store field data
                field_data[field_name] = {
                    "type": field_type_str,
                    "type_code": field_type,
                    "x": rect.x0,
                    "y": rect.y0,
                    "width": rect.width,
                    "height": rect.height,
                    "value": field_value,
                    "flags": field_flags
                }
        else:
            print("\n⚠️  No form fields found - this PDF is not fillable")
            print("    You'll need to use coordinate-based overlay instead")
        
        # Extract text and positions for reference
        print(f"\n📄 Text elements on page (for coordinate reference):")
        print("-" * 50)
        
        # Get all text with positions
        text_instances = page.get_text("dict")
        
        # Look for key labels
        key_labels = [
            "Employee Name", "Social Security", "Email", 
            "Bank Name", "Routing Number", "Account Number",
            "Amount", "Checking", "Savings", "entire net amount",
            "Employee Signature", "Date"
        ]
        
        for block in text_instances["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        # Check if this text matches any key labels
                        for label in key_labels:
                            if label.lower() in text.lower():
                                bbox = span["bbox"]
                                print(f"\n  Found label: '{text}'")
                                print(f"    Position: x={bbox[0]:.2f}, y={bbox[1]:.2f}")
                                print(f"    Size: {bbox[2]-bbox[0]:.2f} x {bbox[3]-bbox[1]:.2f}")
                                
                                # Estimate field position (usually to the right or below)
                                print(f"    Estimated field position: x={bbox[2]+10:.2f}, y={bbox[1]:.2f}")
        
        # Save field data to JSON
        output_file = pdf_path.replace('.pdf', '_fields.json')
        with open(output_file, 'w') as f:
            json.dump(field_data, f, indent=2)
        print(f"\n✅ Field data saved to: {output_file}")
        
        # Generate field mapping code
        print(f"\n🔧 Suggested field mapping code:")
        print("-" * 50)
        print("field_mappings = {")
        for field_name, field_info in field_data.items():
            if field_info["type"] == "Text":
                # Suggest mapping based on field name
                suggested_var = field_name.lower().replace(" ", "_").replace("-", "_")
                print(f"    '{field_name}': employee_data.get('{suggested_var}', ''),")
            elif field_info["type"] == "CheckBox":
                print(f"    '{field_name}': employee_data.get('{field_name.lower()}', False),")
        print("}")
        
        doc.close()
        
        return field_data
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return {}

def main():
    # Check for Direct Deposit PDF in static folder
    backend_path = Path("/Users/gouthamvemula/onbclaude/onbdev-demo/hotel-onboarding-backend")
    pdf_paths = [
        backend_path / "static" / "direct-deposit.pdf",
        backend_path / "static" / "Direct Deposit Printable Form.pdf",
        backend_path / "static" / "forms" / "direct-deposit.pdf",
    ]
    
    pdf_found = False
    for pdf_path in pdf_paths:
        if pdf_path.exists():
            print(f"Found PDF: {pdf_path}")
            analyze_pdf_fields(str(pdf_path))
            pdf_found = True
            break
    
    if not pdf_found:
        print("❌ No Direct Deposit PDF found in expected locations:")
        for path in pdf_paths:
            print(f"  - {path}")
        print("\nSearching for any PDF files in static folder...")
        
        # Search for any PDFs
        static_folder = backend_path / "static"
        pdfs = list(static_folder.glob("**/*.pdf"))
        if pdfs:
            print(f"Found {len(pdfs)} PDF files:")
            for pdf in pdfs[:5]:  # Show first 5
                print(f"  - {pdf.relative_to(backend_path)}")
                if "direct" in pdf.name.lower() or "deposit" in pdf.name.lower():
                    print(f"    📋 Analyzing this file...")
                    analyze_pdf_fields(str(pdf))

if __name__ == "__main__":
    main()