#!/usr/bin/env python3
"""
Analyze PDF content to see what fields are actually filled
"""
import sys
import os
import fitz
import json
from pathlib import Path

def analyze_pdf_fields(pdf_path):
    """Analyze a PDF file to see what fields are filled"""
    print(f"🔍 ANALYZING PDF: {pdf_path}")
    print("=" * 50)

    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return

    try:
        doc = fitz.open(pdf_path)

        print(f"PDF has {len(doc)} pages")

        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n📄 PAGE {page_num + 1}:")

            # Get all widgets (form fields)
            widgets = list(page.widgets())
            print(f"Found {len(widgets)} form fields")

            for widget in widgets:
                field_name = widget.field_name or "unnamed"
                field_value = widget.field_value or ""
                field_type = widget.field_type

                # Check if field has content
                has_content = bool(field_value.strip())
                status = "✅ FILLED" if has_content else "❌ EMPTY"

                print(f"  {status} | {field_name} ({field_type}): '{field_value}'")

            # Also check for text that's drawn directly (not in form fields)
            print("\n📝 EXTRACTED TEXT (first 500 chars):")
            text = page.get_text()
            print(text[:500] + "..." if len(text) > 500 else text)

        doc.close()

    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()

def analyze_generated_pdf_from_payload(payload_data):
    """Generate a PDF from payload and analyze it"""
    print("🔄 GENERATING PDF FROM PAYLOAD DATA...")
    print("=" * 50)

    try:
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'hotel-onboarding-backend', 'app'))

        from app.pdf_forms import PDFFormFiller

        pdf_filler = PDFFormFiller()
        pdf_bytes = pdf_filler.fill_direct_deposit_form(payload_data)

        if pdf_bytes:
            # Save to temporary file
            temp_path = "temp_generated_pdf.pdf"
            with open(temp_path, "wb") as f:
                f.write(pdf_bytes)

            print(f"✅ PDF generated successfully ({len(pdf_bytes)} bytes)")
            print(f"📄 Saved to: {temp_path}")

            # Analyze the generated PDF
            analyze_pdf_fields(temp_path)

            return temp_path
        else:
            print("❌ PDF generation returned empty bytes")
            return None

    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_with_sample_data():
    """Test with known working data"""
    print("🧪 TESTING WITH SAMPLE DATA...")
    print("=" * 50)

    sample_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "ssn": "123-45-6789",
        "direct_deposit": {
            "bank_name": "Chase Bank",
            "routing_number": "021000021",
            "account_number": "1234567890",
            "account_type": "checking",
            "deposit_type": "full",
            "deposit_amount": ""
        },
        "property": {"name": "Test Property"}
    }

    print("Sample data:")
    print(json.dumps(sample_data, indent=2))

    return analyze_generated_pdf_from_payload(sample_data)

def test_with_frontend_structure():
    """Test with frontend-style data structure"""
    print("🔧 TESTING WITH FRONTEND DATA STRUCTURE...")
    print("=" * 50)

    frontend_data = {
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane.smith@example.com",
        "ssn": "987-65-4321",
        "paymentMethod": "direct_deposit",
        "depositType": "full",
        "primaryAccount": {
            "bankName": "Bank of America",
            "routingNumber": "121000358",
            "accountNumber": "9876543210",
            "accountType": "checking",
            "depositAmount": "",
            "percentage": 100
        }
    }

    print("Frontend-style data:")
    print(json.dumps(frontend_data, indent=2))

    return analyze_generated_pdf_from_payload(frontend_data)

def analyze_existing_pdfs():
    """Analyze any existing PDF files in the directory"""
    print("📁 ANALYZING EXISTING PDF FILES...")
    print("=" * 50)

    pdf_files = list(Path(".").glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in current directory")
        return

    print(f"Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"  📄 {pdf_file}")
        analyze_pdf_fields(str(pdf_file))
        print("-" * 30)

def main():
    print("🚀 PDF CONTENT ANALYSIS TOOL")
    print("=" * 60)

    # Test with sample data first
    test_with_sample_data()
    print("\n" + "=" * 60)

    # Test with frontend structure
    test_with_frontend_structure()
    print("\n" + "=" * 60)

    # Analyze any existing PDFs
    analyze_existing_pdfs()

    print("\n📋 ANALYSIS COMPLETE")
    print("=" * 30)
    print("If fields are showing as FILLED but PDF appears empty:")
    print("  - The fields might be filled but not visible due to PDF viewer")
    print("  - Check the extracted text to see if data is there")
    print("  - Try opening PDF in different viewer")
    print("\nIf fields are showing as EMPTY:")
    print("  - Check the payload data structure")
    print("  - Verify field names match between frontend and backend")
    print("  - Run frontend data capture tool")

if __name__ == "__main__":
    main()
