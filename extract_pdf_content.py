#!/usr/bin/env python3
"""
Comprehensive script to extract all PDF content including:
- Text content with positions
- Form field names and values
- Annotations and links
- Visual structure analysis
"""

import fitz  # PyMuPDF
import json
import sys
import os
from datetime import datetime

def extract_pdf_content(pdf_path):
    """Extract comprehensive content from PDF including text and form fields"""
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        print(f"📄 Analyzing PDF: {pdf_path}")
        print(f"📄 File size: {os.path.getsize(pdf_path)} bytes")
        print(f"📄 Number of pages: {len(doc)}")
        print("=" * 80)
        
        # Store all extracted content
        pdf_content = {
            "metadata": {
                "file_path": pdf_path,
                "file_size": os.path.getsize(pdf_path),
                "page_count": len(doc),
                "extraction_time": datetime.now().isoformat()
            },
            "pages": []
        }
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n📋 PAGE {page_num + 1} CONTENT EXTRACTION:")
            print("-" * 60)
            
            page_content = {
                "page_number": page_num + 1,
                "page_size": [page.rect.width, page.rect.height],
                "text_blocks": [],
                "form_fields": [],
                "annotations": [],
                "links": []
            }
            
            # 1. Extract text blocks with positions
            print(f"📝 Extracting text blocks...")
            text_dict = page.get_text("dict")
            
            for block in text_dict["blocks"]:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_content = span["text"].strip()
                            if text_content:  # Only non-empty text
                                text_block = {
                                    "text": text_content,
                                    "bbox": span["bbox"],  # [x0, y0, x1, y1]
                                    "font": span["font"],
                                    "size": span["size"],
                                    "flags": span["flags"],
                                    "color": span["color"]
                                }
                                page_content["text_blocks"].append(text_block)
                                print(f"  📝 Text: '{text_content[:50]}...' | Pos: {span['bbox']}")
            
            # 2. Extract form fields (widgets)
            print(f"\n📋 Extracting form fields...")
            widgets = page.widgets()
            
            for widget in widgets:
                field_info = {
                    "field_name": widget.field_name,
                    "field_type": widget.field_type_string,
                    "field_value": widget.field_value,
                    "bbox": [widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1],
                    "is_filled": bool(widget.field_value) and str(widget.field_value).strip() not in ['', 'Off', 'False']
                }
                
                # Additional properties for different field types
                if hasattr(widget, 'field_label'):
                    field_info["field_label"] = widget.field_label
                
                if hasattr(widget, 'choice_values'):
                    field_info["choice_values"] = widget.choice_values
                
                page_content["form_fields"].append(field_info)
                
                status = "✅ FILLED" if field_info["is_filled"] else "❌ EMPTY"
                print(f"  {status} | {widget.field_type_string:12} | {widget.field_name:30} | {str(widget.field_value)[:30]}")
            
            # 3. Extract annotations
            print(f"\n📌 Extracting annotations...")
            annotations = page.annots()
            
            for annot in annotations:
                annot_info = {
                    "type": annot.type[1],  # Annotation type name
                    "content": annot.info.get("content", ""),
                    "bbox": [annot.rect.x0, annot.rect.y0, annot.rect.x1, annot.rect.y1],
                    "author": annot.info.get("title", ""),
                    "subject": annot.info.get("subject", "")
                }
                page_content["annotations"].append(annot_info)
                print(f"  📌 {annot.type[1]}: '{annot.info.get('content', '')[:30]}...'")
            
            # 4. Extract links
            print(f"\n🔗 Extracting links...")
            links = page.get_links()
            
            for link in links:
                link_info = {
                    "bbox": link["from"],
                    "uri": link.get("uri", ""),
                    "page": link.get("page", -1),
                    "kind": link.get("kind", "")
                }
                page_content["links"].append(link_info)
                print(f"  🔗 Link: {link.get('uri', 'Internal link')}")
            
            # 5. Find text near form fields (labels)
            print(f"\n🏷️ Mapping field labels...")
            for field in page_content["form_fields"]:
                field_bbox = field["bbox"]
                nearby_text = []
                
                # Look for text within 100 pixels of the field
                for text_block in page_content["text_blocks"]:
                    text_bbox = text_block["bbox"]
                    
                    # Calculate distance between field and text
                    field_center_x = (field_bbox[0] + field_bbox[2]) / 2
                    field_center_y = (field_bbox[1] + field_bbox[3]) / 2
                    text_center_x = (text_bbox[0] + text_bbox[2]) / 2
                    text_center_y = (text_bbox[1] + text_bbox[3]) / 2
                    
                    distance = ((field_center_x - text_center_x) ** 2 + (field_center_y - text_center_y) ** 2) ** 0.5
                    
                    if distance < 100:  # Within 100 pixels
                        nearby_text.append({
                            "text": text_block["text"],
                            "distance": distance,
                            "position": "left" if text_center_x < field_center_x else "right"
                        })
                
                # Sort by distance and add to field info
                nearby_text.sort(key=lambda x: x["distance"])
                field["nearby_labels"] = nearby_text[:3]  # Keep top 3 closest
                
                if nearby_text:
                    closest_label = nearby_text[0]["text"]
                    print(f"  🏷️ {field['field_name']} → '{closest_label[:30]}...'")
            
            pdf_content["pages"].append(page_content)
            
            # Page summary
            print(f"\n📊 Page {page_num + 1} Summary:")
            print(f"  📝 Text blocks: {len(page_content['text_blocks'])}")
            print(f"  📋 Form fields: {len(page_content['form_fields'])}")
            print(f"  📌 Annotations: {len(page_content['annotations'])}")
            print(f"  🔗 Links: {len(page_content['links'])}")
        
        # Generate comprehensive analysis
        print(f"\n" + "=" * 80)
        print("📊 COMPREHENSIVE ANALYSIS")
        print("=" * 80)
        
        # Overall statistics
        total_text_blocks = sum(len(page["text_blocks"]) for page in pdf_content["pages"])
        total_form_fields = sum(len(page["form_fields"]) for page in pdf_content["pages"])
        filled_fields = sum(sum(1 for field in page["form_fields"] if field["is_filled"]) for page in pdf_content["pages"])
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"  📝 Total text blocks: {total_text_blocks}")
        print(f"  📋 Total form fields: {total_form_fields}")
        print(f"  ✅ Filled fields: {filled_fields}")
        print(f"  ❌ Empty fields: {total_form_fields - filled_fields}")
        print(f"  📈 Fill percentage: {(filled_fields/total_form_fields*100):.1f}%" if total_form_fields > 0 else "📈 Fill percentage: 0%")
        
        # Field type analysis
        field_types = {}
        for page in pdf_content["pages"]:
            for field in page["form_fields"]:
                field_type = field["field_type"]
                if field_type not in field_types:
                    field_types[field_type] = {"total": 0, "filled": 0}
                field_types[field_type]["total"] += 1
                if field["is_filled"]:
                    field_types[field_type]["filled"] += 1
        
        print(f"\n📋 FIELD TYPE BREAKDOWN:")
        for field_type, stats in field_types.items():
            fill_rate = (stats["filled"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {field_type:15} | {stats['filled']:3}/{stats['total']:3} filled ({fill_rate:5.1f}%)")
        
        # Save detailed content to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"pdf_content_analysis_{timestamp}.json"
        
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(pdf_content, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed content saved to: {output_filename}")
        
        # Generate human-readable report
        report_filename = f"pdf_content_report_{timestamp}.txt"
        generate_readable_report(pdf_content, report_filename)
        print(f"📄 Human-readable report saved to: {report_filename}")
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_readable_report(pdf_content, filename):
    """Generate a human-readable report of the PDF content"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("PDF CONTENT ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        # Metadata
        metadata = pdf_content["metadata"]
        f.write(f"File: {metadata['file_path']}\n")
        f.write(f"Size: {metadata['file_size']} bytes\n")
        f.write(f"Pages: {metadata['page_count']}\n")
        f.write(f"Analyzed: {metadata['extraction_time']}\n\n")
        
        # Page-by-page content
        for page in pdf_content["pages"]:
            f.write(f"PAGE {page['page_number']}\n")
            f.write("-" * 30 + "\n\n")
            
            # Form fields with labels
            f.write("FORM FIELDS:\n")
            for field in page["form_fields"]:
                status = "✅ FILLED" if field["is_filled"] else "❌ EMPTY"
                f.write(f"{status} {field['field_type']:12} | {field['field_name']:30} | {str(field['field_value'])}\n")
                
                # Add nearby labels
                if field.get("nearby_labels"):
                    closest_label = field["nearby_labels"][0]["text"]
                    f.write(f"    Label: {closest_label}\n")
                f.write("\n")
            
            # Text content
            f.write("\nTEXT CONTENT:\n")
            for text_block in page["text_blocks"]:
                f.write(f"'{text_block['text']}' (Font: {text_block['font']}, Size: {text_block['size']})\n")
            
            f.write("\n" + "="*50 + "\n\n")

def main():
    # Look for the most recent health insurance test PDF
    pdf_files = [f for f in os.listdir('.') if f.startswith('health_insurance_test_') and f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No health insurance test PDF files found in current directory")
        print("💡 Available PDF files:")
        all_pdfs = [f for f in os.listdir('.') if f.endswith('.pdf')]
        for pdf in all_pdfs[:5]:  # Show first 5 PDFs
            print(f"  📄 {pdf}")
        
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            if os.path.exists(pdf_path):
                print(f"\n🔍 Using provided PDF: {pdf_path}")
                extract_pdf_content(pdf_path)
            else:
                print(f"❌ Provided PDF not found: {pdf_path}")
        return
    
    # Use the most recent file
    pdf_files.sort(reverse=True)
    latest_pdf = pdf_files[0]
    
    print(f"🔍 Found PDF file: {latest_pdf}")
    print("🚀 Starting comprehensive content extraction...")
    extract_pdf_content(latest_pdf)

if __name__ == "__main__":
    main()
