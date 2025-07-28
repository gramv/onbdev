#!/usr/bin/env python3
"""
Test script for QR code generation functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.qr_service import qr_service

def test_qr_generation():
    """Test QR code generation"""
    print("Testing QR code generation...")
    
    # Test basic QR code generation
    property_id = "test_property_123"
    
    try:
        qr_data = qr_service.generate_qr_code(property_id)
        print("✅ Basic QR code generation successful")
        print(f"   Property ID: {qr_data['property_id']}")
        print(f"   Application URL: {qr_data['application_url']}")
        print(f"   QR Code Size: {qr_data['size']}")
        print(f"   QR Code URL length: {len(qr_data['qr_code_url'])} characters")
        
        # Test printable QR code generation
        printable_data = qr_service.generate_printable_qr_code(property_id, "Test Hotel Property")
        print("✅ Printable QR code generation successful")
        print(f"   Property Name: {printable_data['property_name']}")
        print(f"   Canvas Size: {printable_data['canvas_size']}")
        print(f"   Printable QR URL length: {len(printable_data['printable_qr_url'])} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ QR code generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qr_generation()
    sys.exit(0 if success else 1)