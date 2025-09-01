/**
 * Health Insurance Context Provider
 * Centralized state management for the Health Insurance module
 */

import React, { createContext, useContext, useReducer, useEffect, useCallback, useMemo } from 'react'
import { 
  HealthInsuranceState, 
  HealthInsuranceAction,
  HealthInsuranceStep,
  PersonalInfo,
  SignatureData,
  createInitialHealthInsuranceState,
  healthInsuranceSelectors
} from '../types/healthInsuranceState'
import { healthInsuranceReducer, healthInsuranceActions } from '../reducers/healthInsuranceReducer'
import { healthInsuranceErrorHandler } from '../services/HealthInsuranceErrorHandler'
import { HealthInsuranceErrorType, ErrorSeverity } from '../types/healthInsuranceErrors'
import { validateHealthInsuranceForm } from '../utils/healthInsuranceValidation'
import { getApiUrl } from '../config/api'

// Storage keys
const STORAGE_KEY = 'health_insurance_form_data'
const AUTO_SAVE_INTERVAL = 30000 // 30 seconds

interface HealthInsuranceContextValue {
  // State
  state: HealthInsuranceState
  
  // Selectors (memoized for performance)
  selectors: typeof healthInsuranceSelectors
  
  // Form Actions
  updateFormData: (data: Partial<any>) => void
  setPersonalInfo: (info: PersonalInfo) => void
  validateForm: (fields?: string[]) => void
  resetForm: () => void
  
  // Navigation Actions
  goToStep: (step: HealthInsuranceStep) => void
  nextStep: () => void
  previousStep: () => void
  
  // PDF Actions
  generatePDF: () => Promise<string | null>
  generateSignedPDF: () => Promise<string | null>
  clearPDF: () => void
  
  // Signature Actions
  captureSignature: (signature: SignatureData) => void
  clearSignature: () => void
  
  // Persistence Actions
  saveProgress: () => Promise<void>
  loadProgress: () => void
  enableAutoSave: (enabled: boolean) => void
  
  // Error Handling
  handleError: (error: any, context?: any) => void
  clearError: (key: string) => void
  clearAllErrors: () => void
  
  // Utility Actions
  setLanguage: (language: 'en' | 'es') => void
  markCompleted: () => void
}

const HealthInsuranceContext = createContext<HealthInsuranceContextValue | null>(null)

interface HealthInsuranceProviderProps {
  children: React.ReactNode
  employeeId?: string
  language?: 'en' | 'es'
  onComplete?: (data: any) => void
  onError?: (error: any) => void
}

export function HealthInsuranceProvider({
  children,
  employeeId,
  language = 'en',
  onComplete,
  onError
}: HealthInsuranceProviderProps) {
  const [state, dispatch] = useReducer(
    healthInsuranceReducer,
    createInitialHealthInsuranceState(employeeId, language)
  )

  // Memoized selectors for performance
  const memoizedSelectors = useMemo(() => {
    const selectorResults: any = {}
    Object.entries(healthInsuranceSelectors).forEach(([key, selector]) => {
      selectorResults[key] = selector(state)
    })
    return selectorResults
  }, [state])

  // Auto-save functionality
  useEffect(() => {
    if (!state.autoSaveEnabled || !state.isDirty) return

    const autoSaveTimer = setTimeout(async () => {
      try {
        await saveProgress()
      } catch (error) {
        console.warn('Auto-save failed:', error)
      }
    }, AUTO_SAVE_INTERVAL)

    return () => clearTimeout(autoSaveTimer)
  }, [state.isDirty, state.autoSaveEnabled, state.formData])

  // Load saved progress on mount
  useEffect(() => {
    loadProgress()
  }, [])

  // Form Actions
  const updateFormData = useCallback((data: Partial<any>) => {
    dispatch(healthInsuranceActions.updateFormData(data))
  }, [])

  const setPersonalInfo = useCallback((info: PersonalInfo) => {
    dispatch(healthInsuranceActions.setPersonalInfo(info))
  }, [])

  const validateForm = useCallback((fields?: string[]) => {
    dispatch(healthInsuranceActions.validateForm(fields))
  }, [])

  const resetForm = useCallback(() => {
    dispatch({ type: 'RESET_FORM_DATA' })
  }, [])

  // Navigation Actions
  const goToStep = useCallback((step: HealthInsuranceStep) => {
    dispatch(healthInsuranceActions.goToStep(step))
  }, [])

  const nextStep = useCallback(() => {
    // Validate before advancing
    const validationResult = validateHealthInsuranceForm(state.formData, state.personalInfo)
    if (!validationResult.isValid) {
      handleError(
        healthInsuranceErrorHandler.createError(
          HealthInsuranceErrorType.INVALID_FORM_DATA,
          'Please complete all required fields before continuing',
          ErrorSeverity.MEDIUM,
          { validationErrors: validationResult.errors }
        ),
        'navigation'
      )
      return
    }
    
    dispatch(healthInsuranceActions.nextStep())
  }, [state.formData, state.personalInfo])

  const previousStep = useCallback(() => {
    dispatch(healthInsuranceActions.previousStep())
  }, [])

  // PDF Actions
  const generatePDF = useCallback(async (): Promise<string | null> => {
    try {
      dispatch(healthInsuranceActions.setPDFGenerating(true))
      dispatch(healthInsuranceActions.setLoading('pdf_generation', 'Generating your health insurance form...'))

      const response = await fetch(`${getApiUrl()}/onboarding/${state.employeeId}/health-insurance/generate-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_data: {
            personalInfo: state.personalInfo,
            ...state.formData
          }
        })
      })

      if (!response.ok) {
        throw new Error(`PDF generation failed: ${response.status} ${response.statusText}`)
      }

      const result = await response.json()

      if (!result.success || !result.data?.pdf) {
        throw new Error('Invalid PDF generation response')
      }

      dispatch(healthInsuranceActions.setPDFData(result.data.pdf))
      dispatch(healthInsuranceActions.clearLoading())
      
      return result.data.pdf

    } catch (error) {
      const healthError = healthInsuranceErrorHandler.createError(
        HealthInsuranceErrorType.PDF_GENERATION_FAILED,
        error instanceof Error ? error.message : 'PDF generation failed',
        ErrorSeverity.HIGH,
        { formData: state.formData, employeeId: state.employeeId }
      )

      dispatch({ type: 'SET_PDF_ERROR', payload: healthError })
      dispatch(healthInsuranceActions.clearLoading())
      
      // Attempt automatic recovery
      const recovery = await healthInsuranceErrorHandler.handleError(healthError, state.language)
      if (recovery.success && recovery.data) {
        dispatch(healthInsuranceActions.setPDFData(recovery.data))
        return recovery.data
      }

      handleError(healthError, 'pdf_generation')
      return null
    }
  }, [state.employeeId, state.formData, state.personalInfo, state.language])

  const clearPDF = useCallback(() => {
    dispatch({ type: 'CLEAR_PDF_DATA' })
  }, [])

  const generateSignedPDF = useCallback(async (): Promise<string | null> => {
    try {
      dispatch(healthInsuranceActions.setPDFGenerating(true))
      dispatch(healthInsuranceActions.setLoading('signed_pdf_generation', 'Generating your signed health insurance form...'))

      if (!state.signatureData) {
        throw new Error('No signature data available')
      }

      // First generate the unsigned PDF
      const unsignedResponse = await fetch(`${getApiUrl()}/onboarding/${state.employeeId}/health-insurance/generate-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          employee_data: {
            personalInfo: state.personalInfo,
            ...state.formData
          }
        })
      })

      if (!unsignedResponse.ok) {
        throw new Error(`Unsigned PDF generation failed: ${unsignedResponse.status}`)
      }

      const unsignedResult = await unsignedResponse.json()
      if (!unsignedResult.success || !unsignedResult.data?.pdf) {
        throw new Error('Invalid unsigned PDF generation response')
      }

      // Then add signature to the PDF
      const signedResponse = await fetch(`${getApiUrl()}/forms/health-insurance/add-signature`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pdf_data: unsignedResult.data.pdf,
          signature: state.signatureData.signature,
          signature_type: 'employee_health_insurance',
          page_num: 1
        })
      })

      if (!signedResponse.ok) {
        throw new Error(`Signature addition failed: ${signedResponse.status}`)
      }

      // Convert response to base64
      const signedPdfBlob = await signedResponse.blob()
      const signedPdfBase64 = await new Promise<string>((resolve) => {
        const reader = new FileReader()
        reader.onloadend = () => {
          const base64 = (reader.result as string).split(',')[1]
          resolve(base64)
        }
        reader.readAsDataURL(signedPdfBlob)
      })

      dispatch({ type: 'SET_SIGNED_PDF_DATA', payload: signedPdfBase64 })
      dispatch(healthInsuranceActions.clearLoading())

      return signedPdfBase64

    } catch (error) {
      const healthError = healthInsuranceErrorHandler.createError(
        HealthInsuranceErrorType.PDF_GENERATION_FAILED,
        error instanceof Error ? error.message : 'Signed PDF generation failed',
        ErrorSeverity.HIGH,
        { formData: state.formData, employeeId: state.employeeId, hasSignature: !!state.signatureData }
      )

      dispatch({ type: 'SET_PDF_ERROR', payload: healthError })
      dispatch(healthInsuranceActions.clearLoading())

      handleError(healthError, 'signed_pdf_generation')
      return null
    }
  }, [state.employeeId, state.formData, state.personalInfo, state.signatureData, state.language])

  // Signature Actions
  const captureSignature = useCallback((signature: SignatureData) => {
    dispatch(healthInsuranceActions.setSignature(signature))
  }, [])

  const clearSignature = useCallback(() => {
    dispatch({ type: 'CLEAR_SIGNATURE_DATA' })
  }, [])

  // Persistence Actions
  const saveProgress = useCallback(async (): Promise<void> => {
    try {
      const dataToSave = {
        formData: state.formData,
        personalInfo: state.personalInfo,
        currentStep: state.currentStep,
        signatureData: state.signatureData,
        lastSaved: new Date().toISOString()
      }

      localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave))
      dispatch(healthInsuranceActions.markSaved())

    } catch (error) {
      console.error('Failed to save progress:', error)
      
      const healthError = healthInsuranceErrorHandler.createError(
        HealthInsuranceErrorType.STORAGE_QUOTA_EXCEEDED,
        'Unable to save your progress. Please free up some storage space.',
        ErrorSeverity.MEDIUM
      )
      
      handleError(healthError, 'persistence')
    }
  }, [state.formData, state.personalInfo, state.currentStep, state.signatureData])

  const loadProgress = useCallback(() => {
    try {
      const savedData = localStorage.getItem(STORAGE_KEY)
      if (savedData) {
        const parsedData = JSON.parse(savedData)
        dispatch({ type: 'RESTORE_FROM_STORAGE', payload: parsedData })
      }
    } catch (error) {
      console.warn('Failed to load saved progress:', error)
      // Don't show error to user for loading failures
    }
  }, [])

  const enableAutoSave = useCallback((enabled: boolean) => {
    dispatch({ type: 'SET_AUTO_SAVE', payload: enabled })
  }, [])

  // Error Handling
  const handleError = useCallback((error: any, context?: any) => {
    const errorKey = context || 'general'
    dispatch(healthInsuranceActions.setError(errorKey, error))
    onError?.(error)
  }, [onError])

  const clearError = useCallback((key: string) => {
    dispatch(healthInsuranceActions.clearError(key))
  }, [])

  const clearAllErrors = useCallback(() => {
    dispatch({ type: 'CLEAR_ALL_ERRORS' })
  }, [])

  // Utility Actions
  const setLanguage = useCallback((newLanguage: 'en' | 'es') => {
    dispatch({ type: 'SET_LANGUAGE', payload: newLanguage })
  }, [])

  const markCompleted = useCallback(() => {
    dispatch(healthInsuranceActions.markCompleted())
    onComplete?.(state)
  }, [state, onComplete])

  // Context value
  const contextValue: HealthInsuranceContextValue = {
    state,
    selectors: memoizedSelectors,
    updateFormData,
    setPersonalInfo,
    validateForm,
    resetForm,
    goToStep,
    nextStep,
    previousStep,
    generatePDF,
    generateSignedPDF,
    clearPDF,
    captureSignature,
    clearSignature,
    saveProgress,
    loadProgress,
    enableAutoSave,
    handleError,
    clearError,
    clearAllErrors,
    setLanguage,
    markCompleted
  }

  return (
    <HealthInsuranceContext.Provider value={contextValue}>
      {children}
    </HealthInsuranceContext.Provider>
  )
}

// Custom hook for using the context
export function useHealthInsurance(): HealthInsuranceContextValue {
  const context = useContext(HealthInsuranceContext)
  
  if (!context) {
    throw new Error('useHealthInsurance must be used within a HealthInsuranceProvider')
  }
  
  return context
}

// Convenience hooks for specific functionality
export function useHealthInsuranceForm() {
  const { state, updateFormData, validateForm, selectors } = useHealthInsurance()
  
  return {
    formData: state.formData,
    personalInfo: state.personalInfo,
    isValid: selectors.isFormValid,
    errors: selectors.getValidationErrors,
    updateFormData,
    validateForm
  }
}

export function useHealthInsuranceNavigation() {
  const { state, goToStep, nextStep, previousStep, selectors } = useHealthInsurance()
  
  return {
    currentStep: state.currentStep,
    canGoBack: selectors.canNavigateBack,
    canGoForward: selectors.canNavigateForward,
    progress: selectors.getProgress,
    goToStep,
    nextStep,
    previousStep
  }
}

export function useHealthInsurancePDF() {
  const { state, generatePDF, clearPDF, selectors } = useHealthInsurance()
  
  return {
    pdfData: selectors.getPDFData,
    isGenerating: selectors.isPDFGenerating,
    error: selectors.getPDFError,
    generatePDF,
    clearPDF
  }
}
