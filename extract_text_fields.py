#!/usr/bin/env python3
"""
Script to extract all text field names from the health insurance PDF template
"""

import fitz  # PyMuPDF
import json

def extract_text_fields():
    """Extract all text field names from the PDF template"""
    
    template_path = "hotel-onboarding-backend/static/HI Form_final3.pdf"
    
    try:
        # Open the PDF template
        doc = fitz.open(template_path)
        print(f"📄 Analyzing PDF template: {template_path}")
        print(f"📄 Number of pages: {len(doc)}")
        print("=" * 80)
        
        all_text_fields = {}
        
        # Analyze each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n📋 PAGE {page_num + 1} TEXT FIELDS:")
            print("-" * 50)
            
            page_text_fields = []
            
            for widget in page.widgets():
                if widget.field_type_string == "Text":
                    field_name = widget.field_name
                    field_value = widget.field_value
                    
                    # Get the text field position
                    rect = widget.rect
                    position = [rect.x0, rect.y0, rect.x1, rect.y1]
                    
                    text_info = {
                        "name": field_name,
                        "current_value": field_value,
                        "position": position,
                        "page": page_num + 1,
                        "width": rect.x1 - rect.x0,
                        "height": rect.y1 - rect.y0
                    }
                    
                    page_text_fields.append(text_info)
                    print(f"  📝 '{field_name}' | Value: '{field_value}' | Pos: {position} | Size: {rect.x1-rect.x0:.1f}x{rect.y1-rect.y0:.1f}")
            
            all_text_fields[f"page_{page_num + 1}"] = page_text_fields
            print(f"\n📊 Page {page_num + 1}: {len(page_text_fields)} text fields found")
        
        # Look specifically for dependent-related fields on page 2
        print("\n" + "=" * 80)
        print("🔍 DEPENDENT-RELATED TEXT FIELDS (PAGE 2)")
        print("=" * 80)
        
        if "page_2" in all_text_fields:
            page2_fields = all_text_fields["page_2"]
            
            # Group fields by likely purpose
            name_fields = []
            dob_fields = []
            ssn_fields = []
            gender_fields = []
            other_fields = []
            
            for field in page2_fields:
                name = field["name"].lower()
                
                if "last name" in name or "first" in name:
                    name_fields.append(field)
                elif "date of birth" in name or "birth" in name:
                    dob_fields.append(field)
                elif "ssn" in name:
                    ssn_fields.append(field)
                elif "gender" in name or "sex" in name:
                    gender_fields.append(field)
                else:
                    other_fields.append(field)
            
            print(f"\n👥 NAME FIELDS ({len(name_fields)} found):")
            for field in name_fields:
                print(f"  📝 '{field['name']}' | Pos: {field['position']} | Size: {field['width']:.1f}x{field['height']:.1f}")
            
            print(f"\n📅 DATE OF BIRTH FIELDS ({len(dob_fields)} found):")
            for field in dob_fields:
                print(f"  📝 '{field['name']}' | Pos: {field['position']} | Size: {field['width']:.1f}x{field['height']:.1f}")
            
            print(f"\n🔢 SSN FIELDS ({len(ssn_fields)} found):")
            for field in ssn_fields:
                print(f"  📝 '{field['name']}' | Pos: {field['position']} | Size: {field['width']:.1f}x{field['height']:.1f}")
            
            print(f"\n👤 GENDER FIELDS ({len(gender_fields)} found):")
            for field in gender_fields:
                print(f"  📝 '{field['name']}' | Pos: {field['position']} | Size: {field['width']:.1f}x{field['height']:.1f}")
            
            print(f"\n📋 OTHER FIELDS ({len(other_fields)} found):")
            for field in other_fields:
                print(f"  📝 '{field['name']}' | Pos: {field['position']} | Size: {field['width']:.1f}x{field['height']:.1f}")
            
            # Suggest gender overlay positions
            print(f"\n💡 SUGGESTED GENDER OVERLAY POSITIONS:")
            print("-" * 50)
            
            # For each dependent row, suggest where to place gender
            dependent_rows = []
            
            # Group fields by Y position (rows)
            y_positions = {}
            for field in page2_fields:
                y = round(field['position'][1], 0)  # Round Y position
                if y not in y_positions:
                    y_positions[y] = []
                y_positions[y].append(field)
            
            # Sort by Y position (top to bottom)
            sorted_rows = sorted(y_positions.items(), key=lambda x: -x[0])  # Negative for top-to-bottom
            
            dependent_count = 0
            for y, fields in sorted_rows:
                # Check if this row has dependent-related fields
                has_name = any("last name" in f["name"].lower() or "first" in f["name"].lower() for f in fields)
                has_dob = any("date of birth" in f["name"].lower() for f in fields)
                has_ssn = any("ssn" in f["name"].lower() for f in fields)
                
                if has_name or has_dob or has_ssn:
                    dependent_count += 1
                    print(f"\n  👥 DEPENDENT {dependent_count} ROW (Y={y}):")
                    
                    # Find rightmost field to place gender after
                    rightmost_x = max(f['position'][2] for f in fields)  # x1 coordinate
                    
                    # Suggest gender position
                    gender_x = rightmost_x + 10  # 10 points to the right
                    gender_rect = [gender_x, y, gender_x + 30, y + 12]  # 30 wide, 12 tall
                    
                    print(f"    📍 Suggested gender position: {gender_rect}")
                    print(f"    📝 Fields in this row:")
                    for f in fields:
                        print(f"      - {f['name']}: {f['position']}")
        
        # Save detailed mapping to JSON
        mapping_output = {
            "all_text_fields": all_text_fields,
            "analysis_timestamp": "2025-08-31"
        }
        
        with open("text_field_mapping_analysis.json", "w") as f:
            json.dump(mapping_output, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to: text_field_mapping_analysis.json")
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return False

def main():
    print("🔍 EXTRACTING TEXT FIELD NAMES FROM HEALTH INSURANCE PDF")
    print("=" * 80)
    extract_text_fields()

if __name__ == "__main__":
    main()
