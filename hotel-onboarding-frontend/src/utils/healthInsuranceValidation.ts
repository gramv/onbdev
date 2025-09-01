/**
 * Health Insurance Form Validation Utilities
 * Comprehensive validation logic for health insurance enrollment
 */

import { HealthInsuranceFormData, PersonalInfo } from '../types/healthInsuranceState'

export interface ValidationResult {
  isValid: boolean
  errors: Record<string, string>
  warnings?: Record<string, string>
}

export interface ValidationRule {
  field: string
  validator: (value: any, formData: HealthInsuranceFormData, personalInfo?: PersonalInfo) => string | null
  required?: boolean
  dependsOn?: string[]
}

// Validation rules for health insurance form
const validationRules: ValidationRule[] = [
  // Medical Plan Validation
  {
    field: 'medicalPlan',
    required: true,
    validator: (value, formData) => {
      if (formData.medicalWaived) return null // Skip if waived
      if (!value || value.trim() === '') {
        return 'Please select a medical plan or choose to waive coverage'
      }
      
      const validPlans = ['hra6k', 'hra4k', 'hra2k', 'minimum_essential', 'indemnity']
      if (!validPlans.includes(value)) {
        return 'Please select a valid medical plan'
      }
      
      return null
    }
  },

  // Medical Tier Validation
  {
    field: 'medicalTier',
    required: true,
    dependsOn: ['medicalPlan'],
    validator: (value, formData) => {
      if (formData.medicalWaived) return null
      if (!formData.medicalPlan) return null // Will be caught by medicalPlan validation
      
      if (!value || value.trim() === '') {
        return 'Please select coverage tier'
      }
      
      const validTiers = ['employee', 'employee_spouse', 'employee_children', 'family']
      if (!validTiers.includes(value)) {
        return 'Please select a valid coverage tier'
      }
      
      // Validate tier matches dependents
      if (value === 'employee_spouse' || value === 'family') {
        const hasSpouse = formData.dependents.some(dep => dep.relationship === 'Spouse')
        if (!hasSpouse && value === 'employee_spouse') {
          return 'Employee + Spouse tier requires a spouse to be added as a dependent'
        }
      }
      
      if (value === 'employee_children' || value === 'family') {
        const hasChildren = formData.dependents.some(dep => dep.relationship === 'Child')
        if (!hasChildren && value === 'employee_children') {
          return 'Employee + Children tier requires children to be added as dependents'
        }
      }
      
      return null
    }
  },

  // Dental Coverage Validation
  {
    field: 'dentalCoverage',
    validator: (value, formData) => {
      if (formData.dentalWaived) return null
      
      if (formData.dentalEnrolled && !formData.dentalCoverage) {
        return 'Cannot enroll in dental without selecting dental coverage'
      }
      
      return null
    }
  },

  // Vision Coverage Validation
  {
    field: 'visionCoverage',
    validator: (value, formData) => {
      if (formData.visionWaived) return null
      
      if (formData.visionEnrolled && !formData.visionCoverage) {
        return 'Cannot enroll in vision without selecting vision coverage'
      }
      
      return null
    }
  },

  // Dependents Validation
  {
    field: 'dependents',
    validator: (value, formData) => {
      const dependents = value || []
      
      // Check if tier requires dependents
      const tierRequiresDependents = ['employee_spouse', 'employee_children', 'family'].includes(formData.medicalTier)
      
      if (tierRequiresDependents && dependents.length === 0) {
        return `${formData.medicalTier.replace('_', ' + ')} tier requires dependents to be added`
      }
      
      // Validate each dependent
      for (let i = 0; i < dependents.length; i++) {
        const dependent = dependents[i]
        
        if (!dependent.firstName || dependent.firstName.trim() === '') {
          return `Dependent ${i + 1}: First name is required`
        }
        
        if (!dependent.lastName || dependent.lastName.trim() === '') {
          return `Dependent ${i + 1}: Last name is required`
        }
        
        if (!dependent.dateOfBirth) {
          return `Dependent ${i + 1}: Date of birth is required`
        }
        
        if (!dependent.relationship) {
          return `Dependent ${i + 1}: Relationship is required`
        }
        
        // Validate age for children
        if (dependent.relationship === 'Child') {
          const birthDate = new Date(dependent.dateOfBirth)
          const today = new Date()
          const age = today.getFullYear() - birthDate.getFullYear()
          
          if (age > 26) {
            return `Dependent ${i + 1}: Children over 26 are not eligible for coverage`
          }
        }
      }
      
      // Check for duplicate dependents
      const names = dependents.map(dep => `${dep.firstName} ${dep.lastName}`.toLowerCase())
      const uniqueNames = new Set(names)
      if (names.length !== uniqueNames.size) {
        return 'Duplicate dependents are not allowed'
      }
      
      return null
    }
  },

  // IRS Dependent Confirmation
  {
    field: 'irsDependentConfirmation',
    dependsOn: ['dependents'],
    validator: (value, formData) => {
      if (formData.dependents && formData.dependents.length > 0) {
        if (!value) {
          return 'You must confirm that your dependents meet IRS requirements'
        }
      }
      return null
    }
  },

  // Section 125 Acknowledgment
  {
    field: 'section125Acknowledged',
    required: true,
    validator: (value) => {
      if (!value) {
        return 'You must acknowledge the Section 125 plan requirements'
      }
      return null
    }
  },

  // Effective Date Validation
  {
    field: 'effectiveDate',
    required: true,
    validator: (value) => {
      if (!value) {
        return 'Effective date is required'
      }
      
      const effectiveDate = new Date(value)
      const today = new Date()
      today.setHours(0, 0, 0, 0) // Reset time for date comparison
      
      if (effectiveDate < today) {
        return 'Effective date cannot be in the past'
      }
      
      // Check if effective date is too far in the future (e.g., more than 1 year)
      const oneYearFromNow = new Date()
      oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1)
      
      if (effectiveDate > oneYearFromNow) {
        return 'Effective date cannot be more than one year in the future'
      }
      
      return null
    }
  },

  // Waive Reason Validation
  {
    field: 'waiveReason',
    dependsOn: ['isWaived'],
    validator: (value, formData) => {
      if (formData.isWaived && (!value || value.trim() === '')) {
        return 'Please provide a reason for waiving coverage'
      }
      return null
    }
  }
]

/**
 * Validate the entire health insurance form
 */
export function validateHealthInsuranceForm(
  formData: HealthInsuranceFormData,
  personalInfo?: PersonalInfo | null,
  fieldsToValidate?: string[]
): ValidationResult {
  const errors: Record<string, string> = {}
  const warnings: Record<string, string> = {}

  // Personal info validation
  if (!personalInfo) {
    errors.personalInfo = 'Personal information is required to continue'
  } else {
    // Validate required personal info fields
    if (!personalInfo.firstName?.trim()) {
      errors['personalInfo.firstName'] = 'First name is required'
    }
    if (!personalInfo.lastName?.trim()) {
      errors['personalInfo.lastName'] = 'Last name is required'
    }
    if (!personalInfo.ssn?.trim()) {
      errors['personalInfo.ssn'] = 'Social Security Number is required'
    }
    if (!personalInfo.dateOfBirth) {
      errors['personalInfo.dateOfBirth'] = 'Date of birth is required'
    }
  }

  // Apply validation rules
  const rulesToApply = fieldsToValidate 
    ? validationRules.filter(rule => fieldsToValidate.includes(rule.field))
    : validationRules

  for (const rule of rulesToApply) {
    // Check dependencies
    if (rule.dependsOn) {
      const dependenciesMet = rule.dependsOn.every(dep => {
        const depValue = (formData as any)[dep]
        return depValue !== undefined && depValue !== null && depValue !== ''
      })
      
      if (!dependenciesMet) {
        continue // Skip validation if dependencies not met
      }
    }

    const fieldValue = (formData as any)[rule.field]
    const error = rule.validator(fieldValue, formData, personalInfo || undefined)
    
    if (error) {
      errors[rule.field] = error
    }
  }

  // Additional business logic validations
  if (!fieldsToValidate || fieldsToValidate.includes('coverage')) {
    // Check if at least one coverage type is selected (unless all waived)
    const hasAnyCoverage = !formData.medicalWaived || formData.dentalCoverage || formData.visionCoverage
    if (!hasAnyCoverage) {
      warnings.coverage = 'You have not selected any coverage. Please confirm this is intentional.'
    }
  }

  // Cost validation warnings
  if (!fieldsToValidate || fieldsToValidate.includes('cost')) {
    if (formData.medicalTier === 'family' && formData.dependents.length > 3) {
      warnings.cost = 'Family coverage with many dependents may be expensive. Consider reviewing your options.'
    }
  }

  const isValid = Object.keys(errors).length === 0

  return {
    isValid,
    errors,
    warnings: Object.keys(warnings).length > 0 ? warnings : undefined
  }
}

/**
 * Validate a specific field
 */
export function validateField(
  fieldName: string,
  value: any,
  formData: HealthInsuranceFormData,
  personalInfo?: PersonalInfo | null
): string | null {
  const rule = validationRules.find(r => r.field === fieldName)
  if (!rule) return null

  // Check dependencies
  if (rule.dependsOn) {
    const dependenciesMet = rule.dependsOn.every(dep => {
      const depValue = (formData as any)[dep]
      return depValue !== undefined && depValue !== null && depValue !== ''
    })
    
    if (!dependenciesMet) {
      return null // Skip validation if dependencies not met
    }
  }

  return rule.validator(value, formData, personalInfo || undefined)
}

/**
 * Get validation summary for display
 */
export function getValidationSummary(
  formData: HealthInsuranceFormData,
  personalInfo?: PersonalInfo | null
): {
  totalFields: number
  validFields: number
  invalidFields: number
  completionPercentage: number
  nextRequiredField?: string
} {
  const result = validateHealthInsuranceForm(formData, personalInfo)
  const totalFields = validationRules.filter(rule => rule.required).length
  const invalidFields = Object.keys(result.errors).length
  const validFields = totalFields - invalidFields

  // Find next required field that needs attention
  const nextRequiredField = validationRules
    .filter(rule => rule.required)
    .find(rule => result.errors[rule.field])?.field

  return {
    totalFields,
    validFields,
    invalidFields,
    completionPercentage: (validFields / totalFields) * 100,
    nextRequiredField
  }
}
