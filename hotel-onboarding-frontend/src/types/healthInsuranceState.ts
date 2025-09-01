/**
 * Health Insurance State Management Types
 * Centralized state definitions for the Health Insurance module
 */

import { HealthInsuranceError } from './healthInsuranceErrors'

export enum HealthInsuranceStep {
  FORM = 'form',
  REVIEW = 'review',
  SIGNATURE = 'signature',
  SIGNED_PREVIEW = 'signed_preview',
  COMPLETE = 'complete'
}

export interface PersonalInfo {
  firstName: string
  lastName: string
  middleInitial?: string
  ssn: string
  dateOfBirth: string
  address: string
  city: string
  state: string
  zipCode: string
  phone: string
  email: string
  gender?: 'M' | 'F' | 'Other'
  maritalStatus?: 'Single' | 'Married' | 'Divorced' | 'Widowed'
}

export interface Dependent {
  id: string
  firstName: string
  lastName: string
  dateOfBirth: string
  gender: 'M' | 'F' | 'Other'
  relationship: 'Spouse' | 'Child' | 'Other'
  coverageType: {
    medical: boolean
    dental: boolean
    vision: boolean
  }
}

export interface HealthInsuranceFormData {
  // Medical Coverage
  medicalPlan: string
  medicalTier: 'employee' | 'employee_spouse' | 'employee_children' | 'family'
  medicalWaived: boolean
  
  // Dental Coverage
  dentalCoverage: boolean
  dentalEnrolled: boolean
  dentalTier: 'employee' | 'employee_spouse' | 'employee_children' | 'family'
  dentalWaived: boolean
  
  // Vision Coverage
  visionCoverage: boolean
  visionEnrolled: boolean
  visionTier: 'employee' | 'employee_spouse' | 'employee_children' | 'family'
  visionWaived: boolean
  
  // Dependents
  dependents: Dependent[]
  hasStepchildren: boolean
  stepchildrenNames: string
  dependentsSupported: boolean
  irsDependentConfirmation: boolean
  
  // Additional Information
  section125Acknowledged: boolean
  effectiveDate: string
  isWaived: boolean
  waiveReason: string
  otherCoverageDetails: string
  
  // Validation
  isValid: boolean
  validationErrors: Record<string, string>
}

export interface SignatureData {
  signature: string // Base64 encoded image
  signedDate: string
  ipAddress?: string
  userAgent?: string
  coordinates?: {
    x: number
    y: number
    width: number
    height: number
  }
}

export interface LoadingState {
  isLoading: boolean
  operation: string | null
  progress?: number
  message?: string
}

export interface HealthInsuranceState {
  // Form Data
  formData: HealthInsuranceFormData
  personalInfo: PersonalInfo | null
  
  // UI State
  currentStep: HealthInsuranceStep
  previousStep: HealthInsuranceStep | null
  canGoBack: boolean
  canGoForward: boolean
  
  // Loading States
  loading: LoadingState
  
  // Error State
  errors: Record<string, HealthInsuranceError>
  hasErrors: boolean
  
  // Document State
  pdfData: string | null
  signedPdfData: string | null
  pdfGenerating: boolean
  pdfError: HealthInsuranceError | null
  signatureData: SignatureData | null
  
  // Persistence State
  lastSaved: Date | null
  isDirty: boolean
  autoSaveEnabled: boolean
  
  // Metadata
  employeeId: string | null
  sessionId: string
  startedAt: Date
  completedAt: Date | null
  
  // Configuration
  language: 'en' | 'es'
  debugMode: boolean
}

export type HealthInsuranceAction = 
  // Form Data Actions
  | { type: 'UPDATE_FORM_DATA'; payload: Partial<HealthInsuranceFormData> }
  | { type: 'SET_PERSONAL_INFO'; payload: PersonalInfo }
  | { type: 'VALIDATE_FORM'; payload?: string[] } // Optional field names to validate
  | { type: 'CLEAR_VALIDATION_ERRORS' }
  
  // Navigation Actions
  | { type: 'SET_CURRENT_STEP'; payload: HealthInsuranceStep }
  | { type: 'ADVANCE_STEP' }
  | { type: 'GO_BACK' }
  | { type: 'RESET_TO_STEP'; payload: HealthInsuranceStep }
  
  // Loading Actions
  | { type: 'SET_LOADING'; payload: { operation: string; message?: string; progress?: number } }
  | { type: 'CLEAR_LOADING' }
  | { type: 'UPDATE_LOADING_PROGRESS'; payload: number }
  
  // Error Actions
  | { type: 'SET_ERROR'; payload: { key: string; error: HealthInsuranceError } }
  | { type: 'CLEAR_ERROR'; payload: string }
  | { type: 'CLEAR_ALL_ERRORS' }
  
  // PDF Actions
  | { type: 'SET_PDF_GENERATING'; payload: boolean }
  | { type: 'SET_PDF_DATA'; payload: string }
  | { type: 'SET_SIGNED_PDF_DATA'; payload: string }
  | { type: 'SET_PDF_ERROR'; payload: HealthInsuranceError | null }
  | { type: 'CLEAR_PDF_DATA' }
  
  // Signature Actions
  | { type: 'SET_SIGNATURE_DATA'; payload: SignatureData }
  | { type: 'CLEAR_SIGNATURE_DATA' }
  
  // Persistence Actions
  | { type: 'MARK_DIRTY' }
  | { type: 'MARK_SAVED'; payload?: Date }
  | { type: 'SET_AUTO_SAVE'; payload: boolean }
  | { type: 'RESTORE_FROM_STORAGE'; payload: Partial<HealthInsuranceState> }
  
  // Metadata Actions
  | { type: 'SET_EMPLOYEE_ID'; payload: string }
  | { type: 'SET_LANGUAGE'; payload: 'en' | 'es' }
  | { type: 'SET_DEBUG_MODE'; payload: boolean }
  | { type: 'MARK_COMPLETED' }
  
  // Reset Actions
  | { type: 'RESET_STATE' }
  | { type: 'RESET_FORM_DATA' }

// Initial state factory
export function createInitialHealthInsuranceState(
  employeeId?: string,
  language: 'en' | 'es' = 'en'
): HealthInsuranceState {
  return {
    // Form Data
    formData: {
      medicalPlan: '',
      medicalTier: 'employee',
      medicalWaived: false,
      dentalCoverage: false,
      dentalEnrolled: false,
      dentalTier: 'employee',
      dentalWaived: false,
      visionCoverage: false,
      visionEnrolled: false,
      visionTier: 'employee',
      visionWaived: false,
      dependents: [],
      hasStepchildren: false,
      stepchildrenNames: '',
      dependentsSupported: false,
      irsDependentConfirmation: false,
      section125Acknowledged: false,
      effectiveDate: '',
      isWaived: false,
      waiveReason: '',
      otherCoverageDetails: '',
      isValid: false,
      validationErrors: {}
    },
    personalInfo: null,
    
    // UI State
    currentStep: HealthInsuranceStep.FORM,
    previousStep: null,
    canGoBack: false,
    canGoForward: false,
    
    // Loading States
    loading: {
      isLoading: false,
      operation: null
    },
    
    // Error State
    errors: {},
    hasErrors: false,
    
    // Document State
    pdfData: null,
    signedPdfData: null,
    pdfGenerating: false,
    pdfError: null,
    signatureData: null,
    
    // Persistence State
    lastSaved: null,
    isDirty: false,
    autoSaveEnabled: true,
    
    // Metadata
    employeeId: employeeId || null,
    sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    startedAt: new Date(),
    completedAt: null,
    
    // Configuration
    language,
    debugMode: process.env.NODE_ENV === 'development'
  }
}

// State selectors for easier access
export const healthInsuranceSelectors = {
  // Form selectors
  getFormData: (state: HealthInsuranceState) => state.formData,
  getPersonalInfo: (state: HealthInsuranceState) => state.personalInfo,
  getValidationErrors: (state: HealthInsuranceState) => state.formData.validationErrors,
  isFormValid: (state: HealthInsuranceState) => state.formData.isValid,
  
  // Navigation selectors
  getCurrentStep: (state: HealthInsuranceState) => state.currentStep,
  canNavigateBack: (state: HealthInsuranceState) => state.canGoBack,
  canNavigateForward: (state: HealthInsuranceState) => state.canGoForward,
  
  // Loading selectors
  isLoading: (state: HealthInsuranceState) => state.loading.isLoading,
  getLoadingOperation: (state: HealthInsuranceState) => state.loading.operation,
  getLoadingMessage: (state: HealthInsuranceState) => state.loading.message,
  
  // Error selectors
  hasErrors: (state: HealthInsuranceState) => state.hasErrors,
  getErrors: (state: HealthInsuranceState) => state.errors,
  getError: (state: HealthInsuranceState, key: string) => state.errors[key],
  
  // PDF selectors
  getPDFData: (state: HealthInsuranceState) => state.pdfData,
  isPDFGenerating: (state: HealthInsuranceState) => state.pdfGenerating,
  getPDFError: (state: HealthInsuranceState) => state.pdfError,
  
  // Signature selectors
  getSignatureData: (state: HealthInsuranceState) => state.signatureData,
  hasSignature: (state: HealthInsuranceState) => !!state.signatureData,
  
  // Persistence selectors
  isDirty: (state: HealthInsuranceState) => state.isDirty,
  getLastSaved: (state: HealthInsuranceState) => state.lastSaved,
  isAutoSaveEnabled: (state: HealthInsuranceState) => state.autoSaveEnabled,
  
  // Progress selectors
  getProgress: (state: HealthInsuranceState) => {
    const steps = Object.values(HealthInsuranceStep)
    const currentIndex = steps.indexOf(state.currentStep)
    return {
      current: currentIndex + 1,
      total: steps.length,
      percentage: ((currentIndex + 1) / steps.length) * 100
    }
  },
  
  // Completion selectors
  isCompleted: (state: HealthInsuranceState) => !!state.completedAt,
  getCompletionTime: (state: HealthInsuranceState) => {
    if (!state.completedAt) return null
    return state.completedAt.getTime() - state.startedAt.getTime()
  }
}
