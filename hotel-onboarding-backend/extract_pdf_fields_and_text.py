#!/usr/bin/env python3
"""
Extract all field names and visible text from I-9 PDF template
This will help us map field names to their visual labels on the form
"""

import PyPDF2
from pdfplumber import PDF
import json
from pathlib import Path

def extract_pdf_fields_and_text(pdf_path):
    """Extract both form fields and visible text with positions"""
    
    print(f"Analyzing PDF: {pdf_path}\n")
    
    # First, extract form fields using PyPDF2
    print("=== FORM FIELDS ===")
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Get form fields
        if '/AcroForm' in pdf_reader.trailer['/Root']:
            fields = pdf_reader.get_fields()
            if fields:
                field_data = []
                for field_name, field_obj in fields.items():
                    field_type = field_obj.get('/FT', 'Unknown')
                    field_info = {
                        'name': field_name,
                        'type': field_type,
                        'value': field_obj.get('/V', ''),
                        'default': field_obj.get('/DV', '')
                    }
                    field_data.append(field_info)
                    print(f"Field: {field_name}")
                    print(f"  Type: {field_type}")
                    print(f"  Current Value: {field_obj.get('/V', 'None')}")
                    print(f"  Default Value: {field_obj.get('/DV', 'None')}")
                    print()
            else:
                print("No form fields found")
        else:
            print("No AcroForm found in PDF")
    
    print("\n=== VISIBLE TEXT WITH POSITIONS ===")
    # Extract visible text with positions using pdfplumber
    with PDF.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"\n--- Page {page_num + 1} ---")
            
            # Extract text with bounding boxes
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            
            # Group text by approximate Y position (same line)
            lines = {}
            for word in words:
                y_pos = round(word['top'], 0)  # Round to nearest pixel
                if y_pos not in lines:
                    lines[y_pos] = []
                lines[y_pos].append({
                    'text': word['text'],
                    'x': word['x0'],
                    'y': word['top'],
                    'width': word['x1'] - word['x0'],
                    'height': word['bottom'] - word['top']
                })
            
            # Sort lines by Y position (top to bottom)
            sorted_lines = sorted(lines.items(), key=lambda x: x[0])
            
            # Print text organized by lines
            for y_pos, words_in_line in sorted_lines:
                # Sort words by X position (left to right)
                words_in_line.sort(key=lambda w: w['x'])
                
                # Combine words into a line of text
                line_text = ' '.join(w['text'] for w in words_in_line)
                
                # Look for signature-related text
                if any(term in line_text.lower() for term in ['signature', 'sign', 'firma']):
                    print(f">>> SIGNATURE TEXT: '{line_text}'")
                    print(f"    Position: x={words_in_line[0]['x']:.1f}, y={y_pos:.1f}")
                else:
                    print(f"Text: '{line_text}'")
                    print(f"  Pos: x={words_in_line[0]['x']:.1f}, y={y_pos:.1f}")
    
    print("\n=== MAPPING VISIBLE TEXT TO NEARBY FIELDS ===")
    # Try to map visible text labels to form fields
    with PDF.open(pdf_path) as pdf:
        page = pdf.pages[0]  # Focus on first page for now
        
        # Extract all text
        text_elements = page.extract_words(x_tolerance=3, y_tolerance=3)
        
        # Look for common label patterns near fields
        signature_labels = []
        for element in text_elements:
            text = element['text'].lower()
            if any(term in text for term in ['signature', 'employee', 'firma']):
                signature_labels.append({
                    'text': element['text'],
                    'x': element['x0'],
                    'y': element['top'],
                    'page': 1
                })
        
        print("\nSignature-related labels found:")
        for label in signature_labels:
            print(f"  '{label['text']}' at x={label['x']:.1f}, y={label['y']:.1f}")

if __name__ == "__main__":
    # Path to the I-9 form template
    pdf_path = "/Users/gouthamvemula/onbclaude/onbdev/hotel-onboarding-frontend/public/i9-form-template.pdf"
    
    if Path(pdf_path).exists():
        extract_pdf_fields_and_text(pdf_path)
    else:
        print(f"PDF file not found: {pdf_path}")
        print("Please update the path to your I-9 template PDF")