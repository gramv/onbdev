import { ValidationResult } from '@/hooks/useStepValidation'

/**
 * Validators for each onboarding step
 */

export const personalInfoValidator = (data: any): ValidationResult => {
  const errors: string[] = []
  const fieldErrors: Record<string, string> = {}

  // Handle nested structure from PersonalInfoStep
  const personalInfo = data.personalInfo || data
  const emergencyContacts = data.emergencyContacts || {}

  // Validate personal info fields
  if (!personalInfo.firstName?.trim()) {
    fieldErrors['personalInfo.firstName'] = 'First name is required'
  }
  if (!personalInfo.lastName?.trim()) {
    fieldErrors['personalInfo.lastName'] = 'Last name is required'
  }
  if (!personalInfo.email?.trim()) {
    fieldErrors['personalInfo.email'] = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(personalInfo.email)) {
    fieldErrors['personalInfo.email'] = 'Please enter a valid email address'
  }
  if (!personalInfo.phone?.trim()) {
    fieldErrors['personalInfo.phone'] = 'Phone number is required'
  }
  if (!personalInfo.address?.trim()) {
    fieldErrors['personalInfo.address'] = 'Address is required'
  }
  if (!personalInfo.city?.trim()) {
    fieldErrors['personalInfo.city'] = 'City is required'
  }
  if (!personalInfo.state?.trim()) {
    fieldErrors['personalInfo.state'] = 'State is required'
  }
  if (!personalInfo.zipCode?.trim()) {
    fieldErrors['personalInfo.zipCode'] = 'ZIP code is required'
  }

  // Validate emergency contact (primary contact required)
  const primaryContact = emergencyContacts.primaryContact || {}
  if (!primaryContact.name?.trim()) {
    fieldErrors['emergencyContacts.primaryContact.name'] = 'Primary emergency contact name is required'
  }
  if (!primaryContact.relationship?.trim()) {
    fieldErrors['emergencyContacts.primaryContact.relationship'] = 'Primary emergency contact relationship is required'
  }
  if (!primaryContact.phoneNumber?.trim()) {
    fieldErrors['emergencyContacts.primaryContact.phoneNumber'] = 'Primary emergency contact phone is required'
  }

  // Convert field errors to general errors if needed
  const personalInfoErrorCount = Object.keys(fieldErrors).filter(k => k.startsWith('personalInfo')).length
  const emergencyErrorCount = Object.keys(fieldErrors).filter(k => k.startsWith('emergencyContacts')).length
  
  if (personalInfoErrorCount > 0) {
    errors.push(`Please complete all required personal information fields (${personalInfoErrorCount} missing)`)
  }
  if (emergencyErrorCount > 0) {
    errors.push(`Please complete all required emergency contact fields (${emergencyErrorCount} missing)`)
  }

  return {
    valid: errors.length === 0 && Object.keys(fieldErrors).length === 0,
    errors,
    fieldErrors
  }
}

export const i9Section1Validator = (data: any): ValidationResult => {
  const errors: string[] = []
  const fieldErrors: Record<string, string> = {}

  // Personal Information
  if (!data.lastName?.trim()) {
    fieldErrors.lastName = 'Last name is required for I-9'
  }
  if (!data.firstName?.trim()) {
    fieldErrors.firstName = 'First name is required for I-9'
  }
  if (!data.dateOfBirth) {
    fieldErrors.dateOfBirth = 'Date of birth is required'
  }
  if (!data.ssn?.trim()) {
    fieldErrors.ssn = 'Social Security Number is required'
  }

  // Citizenship Status
  if (!data.citizenshipStatus) {
    errors.push('You must select your citizenship status')
  }

  // Alien Number/USCIS Number for non-citizens
  if (data.citizenshipStatus === 'alien_authorized' && !data.alienNumber?.trim() && !data.uscisNumber?.trim()) {
    errors.push('Alien Registration Number or USCIS Number is required for work-authorized aliens')
  }

  // Signature
  if (!data.signature || !data.signatureData) {
    errors.push('Electronic signature is required')
  }

  const fieldErrorCount = Object.keys(fieldErrors).length
  return {
    valid: errors.length === 0 && fieldErrorCount === 0,
    errors,
    fieldErrors
  }
}

export const w4FormValidator = (data: any): ValidationResult => {
  const errors: string[] = []
  const fieldErrors: Record<string, string> = {}

  // Step 1 - Personal Information
  if (!data.firstName?.trim()) {
    fieldErrors.firstName = 'First name is required'
  }
  if (!data.lastName?.trim()) {
    fieldErrors.lastName = 'Last name is required'
  }
  if (!data.ssn?.trim()) {
    fieldErrors.ssn = 'Social Security Number is required'
  }
  if (!data.address?.trim()) {
    fieldErrors.address = 'Address is required'
  }

  // Step 2 - Filing Status
  if (!data.filingStatus) {
    errors.push('You must select a filing status')
  }

  // Signature
  if (!data.signature || !data.signatureData) {
    errors.push('Electronic signature is required')
  }

  const fieldErrorCount = Object.keys(fieldErrors).length
  return {
    valid: errors.length === 0 && fieldErrorCount === 0,
    errors,
    fieldErrors
  }
}

export const directDepositValidator = (data: any): ValidationResult => {
  const errors: string[] = []
  const fieldErrors: Record<string, string> = {}

  if (!data.accountType) {
    errors.push('Please select an account type')
  }

  if (!data.bankName?.trim()) {
    fieldErrors.bankName = 'Bank name is required'
  }
  if (!data.routingNumber?.trim()) {
    fieldErrors.routingNumber = 'Routing number is required'
  } else if (!/^\d{9}$/.test(data.routingNumber)) {
    fieldErrors.routingNumber = 'Routing number must be 9 digits'
  }
  if (!data.accountNumber?.trim()) {
    fieldErrors.accountNumber = 'Account number is required'
  }
  if (!data.confirmAccountNumber?.trim()) {
    fieldErrors.confirmAccountNumber = 'Please confirm account number'
  } else if (data.accountNumber !== data.confirmAccountNumber) {
    fieldErrors.confirmAccountNumber = 'Account numbers do not match'
  }

  // Voided check upload
  if (!data.voidedCheckUploaded && !data.accountVerified) {
    errors.push('Please upload a voided check or verify account details')
  }

  const fieldErrorCount = Object.keys(fieldErrors).length
  return {
    valid: errors.length === 0 && fieldErrorCount === 0,
    errors,
    fieldErrors
  }
}

export const companyPoliciesValidator = (data: any): ValidationResult => {
  const errors: string[] = []

  // Check for required initials
  if (!data.sexualHarassmentInitials?.trim() || data.sexualHarassmentInitials.trim().length < 2) {
    errors.push('Sexual Harassment Policy initials are required (at least 2 characters)')
  }
  if (!data.eeoInitials?.trim() || data.eeoInitials.trim().length < 2) {
    errors.push('Equal Employment Opportunity Policy initials are required (at least 2 characters)')
  }

  // Check acknowledgment
  if (!data.acknowledgmentChecked) {
    errors.push('You must acknowledge that you have read and understood all policies')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

export const healthInsuranceValidator = (data: any): ValidationResult => {
  const errors: string[] = []
  const fieldErrors: Record<string, string> = {}

  // Check if plan selection is made
  if (!data.planType) {
    errors.push('Please select a health insurance plan or decline coverage')
  }

  // If enrolling, check for required information
  if (data.planType && data.planType !== 'decline') {
    if (!data.effectiveDate) {
      fieldErrors.effectiveDate = 'Coverage effective date is required'
    }
    
    // Check dependent information if applicable
    if (data.addDependents && data.dependents) {
      data.dependents.forEach((dep: any, index: number) => {
        if (!dep.firstName?.trim()) {
          fieldErrors[`dependent_${index}_firstName`] = 'Dependent first name is required'
        }
        if (!dep.lastName?.trim()) {
          fieldErrors[`dependent_${index}_lastName`] = 'Dependent last name is required'
        }
        if (!dep.dateOfBirth) {
          fieldErrors[`dependent_${index}_dob`] = 'Dependent date of birth is required'
        }
        if (!dep.relationship) {
          fieldErrors[`dependent_${index}_relationship`] = 'Dependent relationship is required'
        }
      })
    }
  }

  const fieldErrorCount = Object.keys(fieldErrors).length
  return {
    valid: errors.length === 0 && fieldErrorCount === 0,
    errors,
    fieldErrors
  }
}

export const documentUploadValidator = (data: any): ValidationResult => {
  const errors: string[] = []

  if (data.documentStrategy === 'listA') {
    if (!data.selectedDocuments || data.selectedDocuments.length === 0) {
      errors.push('Please select and upload one List A document')
    }
  } else if (data.documentStrategy === 'listBC') {
    const hasListB = data.selectedDocuments?.some((docId: string) => 
      docId.includes('drivers-license') || docId.includes('military-id')
    )
    const hasListC = data.selectedDocuments?.some((docId: string) => 
      docId.includes('social-security') || docId.includes('birth-certificate')
    )
    
    if (!hasListB) {
      errors.push('Please select and upload one List B document (identity)')
    }
    if (!hasListC) {
      errors.push('Please select and upload one List C document (work authorization)')
    }
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

export const finalReviewValidator = (data: any): ValidationResult => {
  const errors: string[] = []

  // Check all final acknowledgments
  if (!data.finalAcknowledgments || !data.finalAcknowledgments.every((ack: boolean) => ack)) {
    errors.push('Please check all final acknowledgments before signing')
  }

  // Check for signature
  if (!data.signature || !data.signatureData) {
    errors.push('Final employee signature is required to complete onboarding')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

// Map step IDs to validators
export const stepValidators: Record<string, (data: any) => ValidationResult> = {
  'personal-info': personalInfoValidator,
  'i9-section1': i9Section1Validator,
  'w4-form': w4FormValidator,
  'direct-deposit': directDepositValidator,
  'company-policies': companyPoliciesValidator,
  'health-insurance': healthInsuranceValidator,
  'document-upload': documentUploadValidator,
  'final-review': finalReviewValidator
}