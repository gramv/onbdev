#!/usr/bin/env python3
"""
Script to extract all checkbox field names from the health insurance PDF template
"""

import fitz  # PyMuPDF
import json

def extract_checkbox_names():
    """Extract all checkbox field names from the PDF template"""
    
    template_path = "hotel-onboarding-backend/static/HI Form_final3.pdf"
    
    try:
        # Open the PDF template
        doc = fitz.open(template_path)
        print(f"📄 Analyzing PDF template: {template_path}")
        print(f"📄 Number of pages: {len(doc)}")
        print("=" * 80)
        
        all_checkboxes = {}
        
        # Analyze each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n📋 PAGE {page_num + 1} CHECKBOXES:")
            print("-" * 50)
            
            page_checkboxes = []
            
            for widget in page.widgets():
                if widget.field_type_string == "CheckBox":
                    field_name = widget.field_name
                    field_value = widget.field_value
                    
                    # Get the checkbox position
                    rect = widget.rect
                    position = [rect.x0, rect.y0, rect.x1, rect.y1]
                    
                    checkbox_info = {
                        "name": field_name,
                        "current_value": field_value,
                        "position": position,
                        "page": page_num + 1
                    }
                    
                    page_checkboxes.append(checkbox_info)
                    print(f"  📋 '{field_name}' | Value: '{field_value}' | Pos: {position}")
            
            all_checkboxes[f"page_{page_num + 1}"] = page_checkboxes
            print(f"\n📊 Page {page_num + 1}: {len(page_checkboxes)} checkboxes found")
        
        # Categorize checkboxes by likely purpose
        print("\n" + "=" * 80)
        print("🔍 CHECKBOX CATEGORIZATION")
        print("=" * 80)
        
        dental_checkboxes = []
        vision_checkboxes = []
        medical_checkboxes = []
        other_checkboxes = []
        
        for page_key, checkboxes in all_checkboxes.items():
            for cb in checkboxes:
                name = cb["name"].lower()
                
                if any(keyword in name for keyword in ["dental", "employee only_6", "employee  spouse_7", "employee  children_8", "employee  family_8"]):
                    dental_checkboxes.append(cb)
                elif any(keyword in name for keyword in ["vision", "decline vision"]):
                    vision_checkboxes.append(cb)
                elif any(keyword in name for keyword in ["medical", "employee only_5", "employee  spouse", "employee  children", "employee  family"]) and "dental" not in name and "vision" not in name:
                    medical_checkboxes.append(cb)
                else:
                    other_checkboxes.append(cb)
        
        print(f"\n🦷 DENTAL-RELATED CHECKBOXES ({len(dental_checkboxes)} found):")
        for cb in dental_checkboxes:
            print(f"  📋 '{cb['name']}' | Page: {cb['page']} | Pos: {cb['position']}")
        
        print(f"\n👁️ VISION-RELATED CHECKBOXES ({len(vision_checkboxes)} found):")
        for cb in vision_checkboxes:
            print(f"  📋 '{cb['name']}' | Page: {cb['page']} | Pos: {cb['position']}")
        
        print(f"\n🏥 MEDICAL-RELATED CHECKBOXES ({len(medical_checkboxes)} found):")
        for cb in medical_checkboxes:
            print(f"  📋 '{cb['name']}' | Page: {cb['page']} | Pos: {cb['position']}")
        
        print(f"\n📋 OTHER CHECKBOXES ({len(other_checkboxes)} found):")
        for cb in other_checkboxes:
            print(f"  📋 '{cb['name']}' | Page: {cb['page']} | Pos: {cb['position']}")
        
        # Generate mapping suggestions
        print("\n" + "=" * 80)
        print("💡 SUGGESTED CHECKBOX MAPPINGS")
        print("=" * 80)
        
        # Look for employee-only patterns
        employee_only_checkboxes = [cb for cb in dental_checkboxes + medical_checkboxes + vision_checkboxes 
                                   if "employee only" in cb["name"].lower()]
        
        print(f"\n📋 EMPLOYEE ONLY CHECKBOXES:")
        for cb in employee_only_checkboxes:
            print(f"  '{cb['name']}' | Page: {cb['page']}")
        
        # Save detailed mapping to JSON
        mapping_output = {
            "dental_checkboxes": dental_checkboxes,
            "vision_checkboxes": vision_checkboxes,
            "medical_checkboxes": medical_checkboxes,
            "other_checkboxes": other_checkboxes,
            "all_checkboxes": all_checkboxes
        }
        
        with open("checkbox_mapping_analysis.json", "w") as f:
            json.dump(mapping_output, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to: checkbox_mapping_analysis.json")
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return False

def main():
    print("🔍 EXTRACTING CHECKBOX FIELD NAMES FROM HEALTH INSURANCE PDF")
    print("=" * 80)
    extract_checkbox_names()

if __name__ == "__main__":
    main()
