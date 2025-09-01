#!/usr/bin/env python3
"""
Script to extract all radio button field names from the health insurance PDF template
"""

import fitz  # PyMuPDF
import json

def extract_radio_buttons():
    """Extract all radio button field names from the PDF template"""
    
    template_path = "hotel-onboarding-backend/static/HI Form_final3.pdf"
    
    try:
        # Open the PDF template
        doc = fitz.open(template_path)
        print(f"📄 Analyzing PDF template: {template_path}")
        print(f"📄 Number of pages: {len(doc)}")
        print("=" * 80)
        
        all_radio_buttons = {}
        
        # Analyze each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n📋 PAGE {page_num + 1} RADIO BUTTONS:")
            print("-" * 50)
            
            page_radio_buttons = []
            
            for widget in page.widgets():
                if widget.field_type_string == "RadioButton":
                    field_name = widget.field_name
                    field_value = widget.field_value
                    
                    # Get the radio button position
                    rect = widget.rect
                    position = [rect.x0, rect.y0, rect.x1, rect.y1]
                    
                    radio_info = {
                        "name": field_name,
                        "current_value": field_value,
                        "position": position,
                        "page": page_num + 1
                    }
                    
                    page_radio_buttons.append(radio_info)
                    print(f"  📻 '{field_name}' | Value: '{field_value}' | Pos: {position}")
            
            all_radio_buttons[f"page_{page_num + 1}"] = page_radio_buttons
            print(f"\n📊 Page {page_num + 1}: {len(page_radio_buttons)} radio buttons found")
        
        # Categorize radio buttons by likely purpose
        print("\n" + "=" * 80)
        print("🔍 RADIO BUTTON CATEGORIZATION")
        print("=" * 80)
        
        gender_radio_buttons = []
        irs_radio_buttons = []
        support_radio_buttons = []
        other_radio_buttons = []
        
        for page_key, radio_buttons in all_radio_buttons.items():
            for rb in radio_buttons:
                name = rb["name"].lower()
                
                if any(keyword in name for keyword in ["gender", "sex", "male", "female"]):
                    gender_radio_buttons.append(rb)
                elif any(keyword in name for keyword in ["irs", "dependent", "section 152"]):
                    irs_radio_buttons.append(rb)
                elif any(keyword in name for keyword in ["support", "maintenance"]):
                    support_radio_buttons.append(rb)
                else:
                    other_radio_buttons.append(rb)
        
        print(f"\n👤 GENDER-RELATED RADIO BUTTONS ({len(gender_radio_buttons)} found):")
        for rb in gender_radio_buttons:
            print(f"  📻 '{rb['name']}' | Page: {rb['page']} | Pos: {rb['position']}")
        
        print(f"\n📋 IRS-RELATED RADIO BUTTONS ({len(irs_radio_buttons)} found):")
        for rb in irs_radio_buttons:
            print(f"  📻 '{rb['name']}' | Page: {rb['page']} | Pos: {rb['position']}")
        
        print(f"\n🤝 SUPPORT-RELATED RADIO BUTTONS ({len(support_radio_buttons)} found):")
        for rb in support_radio_buttons:
            print(f"  📻 '{rb['name']}' | Page: {rb['page']} | Pos: {rb['position']}")
        
        print(f"\n📻 OTHER RADIO BUTTONS ({len(other_radio_buttons)} found):")
        for rb in other_radio_buttons:
            print(f"  📻 '{rb['name']}' | Page: {rb['page']} | Pos: {rb['position']}")
        
        # Save detailed mapping to JSON
        mapping_output = {
            "gender_radio_buttons": gender_radio_buttons,
            "irs_radio_buttons": irs_radio_buttons,
            "support_radio_buttons": support_radio_buttons,
            "other_radio_buttons": other_radio_buttons,
            "all_radio_buttons": all_radio_buttons
        }
        
        with open("radio_button_mapping_analysis.json", "w") as f:
            json.dump(mapping_output, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to: radio_button_mapping_analysis.json")
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return False

def main():
    print("🔍 EXTRACTING RADIO BUTTON FIELD NAMES FROM HEALTH INSURANCE PDF")
    print("=" * 80)
    extract_radio_buttons()

if __name__ == "__main__":
    main()
