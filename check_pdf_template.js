// PDF TEMPLATE VERIFICATION
// Copy this into browser console to check if PDF template is accessible

async function checkPdfTemplate() {
  console.log('🔍 PDF TEMPLATE VERIFICATION');
  console.log('=' .repeat(50));

  try {
    // Try to access the PDF template
    const templateUrl = '/static/direct-deposit-template.pdf';

    console.log('📄 Checking template URL:', templateUrl);

    const response = await fetch(templateUrl);

    if (response.ok) {
      console.log('✅ Template accessible');

      const arrayBuffer = await response.arrayBuffer();
      const pdfBytes = new Uint8Array(arrayBuffer);

      console.log('📏 Template size:', pdfBytes.length, 'bytes');

      const header = String.fromCharCode(...pdfBytes.slice(0, 4));
      console.log('📄 Template header:', header);
      console.log('✅ Is valid PDF:', header === '%PDF');

      // Try to analyze template fields (if possible)
      const templateText = new TextDecoder().decode(pdfBytes);

      // Look for AcroForm fields
      const hasAcroForm = templateText.includes('/AcroForm');
      const hasFields = templateText.includes('/FT');

      console.log('Template Analysis:');
      console.log('  - Has AcroForm:', hasAcroForm);
      console.log('  - Has form fields:', hasFields);

      // Check for specific field names
      const employeeNameField = templateText.includes('employee_name');
      const ssnField = templateText.includes('social_security_number');
      const bankField = templateText.includes('bank1_name');

      console.log('Field Names Found:');
      console.log('  - employee_name:', employeeNameField);
      console.log('  - social_security_number:', ssnField);
      console.log('  - bank1_name:', bankField);

      if (employeeNameField && ssnField && bankField) {
        console.log('✅ All required fields found in template');
      } else {
        console.log('⚠️  Some fields missing from template');
      }

    } else {
      console.log('❌ Template not accessible:', response.status);
    }

  } catch (error) {
    console.log('❌ Error checking template:', error.message);
  }
}

checkPdfTemplate();
