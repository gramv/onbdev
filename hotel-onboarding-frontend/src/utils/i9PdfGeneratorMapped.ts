import { PDFDocument } from 'pdf-lib'

interface I9FormData {
  last_name: string
  first_name: string
  middle_initial: string
  other_names: string
  address: string
  apt_number: string
  city: string
  state: string
  zip_code: string
  date_of_birth: string
  ssn: string
  email: string
  phone: string
  citizenship_status: string
  alien_registration_number?: string
  foreign_passport_number?: string
  country_of_issuance?: string
  expiration_date?: string
}

export async function generateMappedI9Pdf(formData: I9FormData): Promise<Uint8Array> {
  console.log('generateMappedI9Pdf called with data:', formData)
  
  try {
    // Load the official I-9 form template
    const formUrl = '/i9-form-template.pdf'
    const formBytes = await fetch(formUrl).then(res => res.arrayBuffer())
    
    // Load the PDF
    const pdfDoc = await PDFDocument.load(formBytes)
    const form = pdfDoc.getForm()
    
    // Map data to exact field names from the official I-9 form
    const fieldMappings = {
      // Personal Information - Using exact field names from the form
      'Last Name (Family Name)': formData.last_name.toUpperCase(),
      'First Name Given Name': formData.first_name.toUpperCase(),
      'Employee Middle Initial (if any)': formData.middle_initial.toUpperCase(),
      'Employee Other Last Names Used (if any)': formData.other_names.toUpperCase(),
      
      // Address Information
      'Address Street Number and Name': formData.address,
      'Apt Number (if any)': formData.apt_number,
      'City or Town': formData.city,
      'ZIP Code': formData.zip_code,
      
      // Personal Details
      'Date of Birth mmddyyyy': formatDateWithSlashes(formData.date_of_birth),
      'US Social Security Number': formData.ssn.replace(/\D/g, ''),
      'Employees E-mail Address': formData.email,
      'Telephone Number': formData.phone.replace(/\D/g, ''),
      
      // Signature Date - try multiple possible field names
      "Today's Date mmddyyyy": formatDateWithSlashes(new Date().toISOString()),
      "Today's Date (mm/dd/yyyy)": formatDateWithSlashes(new Date().toISOString()),
      "Todays Date mmddyyyy": formatDateWithSlashes(new Date().toISOString()),
      "Date": formatDateWithSlashes(new Date().toISOString())
    }
    
    // Fill text fields
    for (const [fieldName, value] of Object.entries(fieldMappings)) {
      if (value) {
        try {
          const field = form.getTextField(fieldName)
          field.setText(value)
          console.log(`Filled "${fieldName}" with "${value}"`)
        } catch (e) {
          // Only log errors for fields other than date fields (which may not exist in all versions)
          if (!fieldName.toLowerCase().includes('date') && !fieldName.toLowerCase().includes('today')) {
            console.error(`Failed to fill field "${fieldName}":`, e)
          }
        }
      }
    }
    
    // Handle State dropdown separately
    try {
      const stateField = form.getDropdown('State')
      // Check if the state value exists in dropdown options
      const options = stateField.getOptions()
      if (options.includes(formData.state)) {
        stateField.select(formData.state)
        console.log(`Set state dropdown to: ${formData.state}`)
      } else {
        console.error(`State "${formData.state}" not found in dropdown options:`, options)
        // Try to set as text field instead if dropdown fails
        try {
          const stateTextField = form.getTextField('State')
          stateTextField.setText(formData.state)
          console.log(`Set state as text field: ${formData.state}`)
        } catch (textError) {
          console.error('Failed to set state as text field:', textError)
        }
      }
    } catch (e) {
      console.error('Failed to set state dropdown:', e)
      // Try alternate field name
      try {
        const stateTextField = form.getTextField('State')
        stateTextField.setText(formData.state)
        console.log(`Set state as text field: ${formData.state}`)
      } catch (textError) {
        console.error('Failed to set state as text field:', textError)
      }
    }
    
    // Handle citizenship checkboxes
    const citizenshipCheckboxes: Record<string, string> = {
      'citizen': 'CB_1',
      'national': 'CB_2', 
      'permanent_resident': 'CB_3',
      'authorized_alien': 'CB_4'
    }
    
    const checkboxName = citizenshipCheckboxes[formData.citizenship_status as keyof typeof citizenshipCheckboxes]
    if (checkboxName) {
      try {
        const checkbox = form.getCheckBox(checkboxName)
        checkbox.check()
        console.log(`Checked citizenship checkbox: ${checkboxName}`)
      } catch (e) {
        console.error(`Failed to check checkbox ${checkboxName}:`, e)
      }
    }
    
    // Handle additional fields for specific citizenship statuses
    if (formData.citizenship_status === 'permanent_resident') {
      if (formData.alien_registration_number) {
        try {
          // This field has a unique name for permanent residents
          const field = form.getTextField('3 A lawful permanent resident Enter USCIS or ANumber')
          field.setText(formData.alien_registration_number)
          console.log('Filled permanent resident USCIS number')
        } catch (e) {
          console.error('Failed to fill permanent resident USCIS number:', e)
        }
      }
      
      // Try to fill expiration date for permanent resident card
      if (formData.expiration_date) {
        try {
          const expField = form.getTextField('Card Expiration Date mmddyyyy')
          expField.setText(formatDateWithSlashes(formData.expiration_date))
          console.log('Filled permanent resident card expiration date')
        } catch (e) {
          // Try alternate field names
          try {
            const expField = form.getTextField('Expiration Date mmddyyyy')
            expField.setText(formatDateWithSlashes(formData.expiration_date))
            console.log('Filled permanent resident expiration date (alternate field)')
          } catch (e2) {
            // Suppress error - the PDF template may not have this field
            // console.error('Failed to fill permanent resident expiration date:', e2)
          }
        }
      }
    }
    
    if (formData.citizenship_status === 'authorized_alien') {
      // Additional fields for authorized aliens
      const alienFields = {
        'USCIS ANumber': formData.alien_registration_number || '',
        'Exp Date mmddyyyy': formatDateWithSlashes(formData.expiration_date || ''),
        'Foreign Passport Number and Country of IssuanceRow1': 
          formData.foreign_passport_number && formData.country_of_issuance 
            ? `${formData.foreign_passport_number} ${formData.country_of_issuance}` 
            : ''
      }
      
      for (const [fieldName, value] of Object.entries(alienFields)) {
        if (value) {
          try {
            const field = form.getTextField(fieldName)
            field.setText(value)
            console.log(`Filled alien field "${fieldName}" with "${value}"`)
          } catch (e) {
            console.error(`Failed to fill alien field "${fieldName}":`, e)
          }
        }
      }
    }
    
    // Save the filled PDF
    const pdfBytes = await pdfDoc.save()
    console.log('PDF generated successfully')
    return pdfBytes
    
  } catch (error) {
    console.error('Error in generateMappedI9Pdf:', error)
    throw error
  }
}

function formatDateWithSlashes(dateString: string): string {
  if (!dateString) return ''
  
  try {
    // Parse the date string components to avoid timezone issues
    // Expected format: YYYY-MM-DD
    const parts = dateString.split('-')
    if (parts.length !== 3) {
      console.error('Invalid date format:', dateString)
      return ''
    }
    
    const year = parseInt(parts[0])
    const month = parseInt(parts[1])
    const day = parseInt(parts[2])
    
    // Validate the parsed values
    if (isNaN(year) || isNaN(month) || isNaN(day)) {
      console.error('Invalid date components:', dateString)
      return ''
    }
    
    // Format as mm/dd/yyyy (with slashes) as required by the form
    const monthStr = String(month).padStart(2, '0')
    const dayStr = String(day).padStart(2, '0')
    const yearStr = String(year)
    
    return `${monthStr}/${dayStr}/${yearStr}`
  } catch (error) {
    console.error('Error formatting date:', error)
    return ''
  }
}