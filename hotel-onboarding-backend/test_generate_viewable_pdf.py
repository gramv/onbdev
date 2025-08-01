#!/usr/bin/env python3
"""
Generate a viewable PDF document directly
"""
from app.policy_document_generator import PolicyDocumentGenerator
from datetime import datetime

# Create generator
generator = PolicyDocumentGenerator()

# Test data
employee_data = {
    'name': 'John Doe',
    'id': 'EMP-12345',
    'property_name': 'Grand Hotel & Resort',
    'position': 'Front Desk Agent'
}

policy_data = {
    'sexualHarassmentInitials': 'JD',
    'eeoInitials': 'JD',
    'acknowledgmentChecked': True
}

signature_data = {
    'name': 'John Doe',
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'ipAddress': '192.168.1.100',
    'signatureId': 'SIG-TEST-123'
}

# Generate PDF
pdf_bytes = generator.generate_policy_document(employee_data, policy_data, signature_data)

# Save to file (unencrypted for viewing)
with open('viewable_policy_document.pdf', 'wb') as f:
    f.write(pdf_bytes)

print("Generated viewable_policy_document.pdf")
print(f"File size: {len(pdf_bytes)} bytes")