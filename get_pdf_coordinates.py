#!/usr/bin/env python3
"""
Get PDF field coordinates for text overlay
"""
import fitz
import os

def get_field_coordinates():
    """Get coordinates of all form fields in the PDF template"""
    template_path = "hotel-onboarding-backend/static/direct-deposit-template.pdf"

    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return {}

    doc = fitz.open(template_path)
    page = doc[0]

    coordinates = {}

    print("📋 PDF FIELD COORDINATES:")
    print("=" * 50)

    for widget in page.widgets():
        field_name = widget.field_name
        if field_name:
            rect = widget.rect
            # Calculate center coordinates for text placement
            center_x = (rect.x0 + rect.x1) / 2
            center_y = (rect.y0 + rect.y1) / 2

            # Adjust Y coordinate (PDF coordinate system starts from bottom)
            page_height = page.rect.height
            adjusted_y = page_height - center_y

            coordinates[field_name] = {
                'rect': rect,
                'center_x': center_x,
                'center_y': adjusted_y,
                'width': rect.width,
                'height': rect.height
            }

            print(f"📍 {field_name}:")
            print(f"   Rect: ({rect.x0:.1f}, {rect.y0:.1f}, {rect.x1:.1f}, {rect.y1:.1f})")
            print(f"   Center: ({center_x:.1f}, {adjusted_y:.1f})")
            print(f"   Size: {rect.width:.1f} x {rect.height:.1f}")
            print()

    doc.close()

    return coordinates

def generate_overlay_code(coordinates):
    """Generate Python code for text overlay"""
    print("🔧 GENERATED OVERLAY CODE:")
    print("=" * 50)
    print("# Copy this code into pdf_forms.py")
    print()

    for field_name, coords in coordinates.items():
        if field_name in ['employee_name', 'social_security_number', 'employee_email',
                         'bank1_name', 'bank1_routing_number', 'bank1_account_number']:
            print(f"# {field_name}")
            print(f"page.insert_text(")
            print(f"    ({coords['center_x']:.1f}, {coords['center_y']:.1f}),")
            print("    full_name,  # Replace with actual variable")
            print("    fontsize=10,")
            print("    color=(0, 0, 0),")
            print("    fontname='helv'")
            print(")")
            print()

    return coordinates

if __name__ == "__main__":
    coords = get_field_coordinates()
    generate_overlay_code(coords)
