/**
 * Health Insurance State Reducer
 * Manages all state transitions for the Health Insurance module
 */

import { 
  HealthInsuranceState, 
  HealthInsuranceAction, 
  HealthInsuranceStep,
  createInitialHealthInsuranceState
} from '@/types/healthInsuranceState'
import { validateHealthInsuranceForm } from '@/utils/healthInsuranceValidation'

export function healthInsuranceReducer(
  state: HealthInsuranceState, 
  action: HealthInsuranceAction
): HealthInsuranceState {
  switch (action.type) {
    // Form Data Actions
    case 'UPDATE_FORM_DATA': {
      const updatedFormData = {
        ...state.formData,
        ...action.payload
      }
      
      // Auto-validate on form data changes
      const validationResult = validateHealthInsuranceForm(updatedFormData, state.personalInfo)
      
      return {
        ...state,
        formData: {
          ...updatedFormData,
          isValid: validationResult.isValid,
          validationErrors: validationResult.errors
        },
        isDirty: true,
        canGoForward: validationResult.isValid && state.currentStep === HealthInsuranceStep.FORM
      }
    }

    case 'SET_PERSONAL_INFO': {
      return {
        ...state,
        personalInfo: action.payload,
        isDirty: true
      }
    }

    case 'VALIDATE_FORM': {
      const fieldsToValidate = action.payload
      const validationResult = validateHealthInsuranceForm(
        state.formData, 
        state.personalInfo,
        fieldsToValidate
      )
      
      return {
        ...state,
        formData: {
          ...state.formData,
          isValid: validationResult.isValid,
          validationErrors: fieldsToValidate 
            ? { ...state.formData.validationErrors, ...validationResult.errors }
            : validationResult.errors
        }
      }
    }

    case 'CLEAR_VALIDATION_ERRORS': {
      return {
        ...state,
        formData: {
          ...state.formData,
          validationErrors: {}
        }
      }
    }

    // Navigation Actions
    case 'SET_CURRENT_STEP': {
      const newStep = action.payload
      const steps = Object.values(HealthInsuranceStep)
      const currentIndex = steps.indexOf(newStep)
      
      return {
        ...state,
        previousStep: state.currentStep,
        currentStep: newStep,
        canGoBack: currentIndex > 0,
        canGoForward: currentIndex < steps.length - 1 && state.formData.isValid
      }
    }

    case 'ADVANCE_STEP': {
      const steps = Object.values(HealthInsuranceStep)
      const currentIndex = steps.indexOf(state.currentStep)
      
      if (currentIndex < steps.length - 1) {
        const nextStep = steps[currentIndex + 1]
        return healthInsuranceReducer(state, { type: 'SET_CURRENT_STEP', payload: nextStep })
      }
      
      return state
    }

    case 'GO_BACK': {
      const steps = Object.values(HealthInsuranceStep)
      const currentIndex = steps.indexOf(state.currentStep)
      
      if (currentIndex > 0) {
        const previousStep = steps[currentIndex - 1]
        return healthInsuranceReducer(state, { type: 'SET_CURRENT_STEP', payload: previousStep })
      }
      
      return state
    }

    case 'RESET_TO_STEP': {
      return healthInsuranceReducer(state, { type: 'SET_CURRENT_STEP', payload: action.payload })
    }

    // Loading Actions
    case 'SET_LOADING': {
      return {
        ...state,
        loading: {
          isLoading: true,
          operation: action.payload.operation,
          message: action.payload.message,
          progress: action.payload.progress
        }
      }
    }

    case 'CLEAR_LOADING': {
      return {
        ...state,
        loading: {
          isLoading: false,
          operation: null,
          message: undefined,
          progress: undefined
        }
      }
    }

    case 'UPDATE_LOADING_PROGRESS': {
      return {
        ...state,
        loading: {
          ...state.loading,
          progress: action.payload
        }
      }
    }

    // Error Actions
    case 'SET_ERROR': {
      const { key, error } = action.payload
      const newErrors = { ...state.errors, [key]: error }
      
      return {
        ...state,
        errors: newErrors,
        hasErrors: Object.keys(newErrors).length > 0
      }
    }

    case 'CLEAR_ERROR': {
      const newErrors = { ...state.errors }
      delete newErrors[action.payload]
      
      return {
        ...state,
        errors: newErrors,
        hasErrors: Object.keys(newErrors).length > 0
      }
    }

    case 'CLEAR_ALL_ERRORS': {
      return {
        ...state,
        errors: {},
        hasErrors: false
      }
    }

    // PDF Actions
    case 'SET_PDF_GENERATING': {
      return {
        ...state,
        pdfGenerating: action.payload,
        pdfError: action.payload ? null : state.pdfError // Clear error when starting generation
      }
    }

    case 'SET_PDF_DATA': {
      return {
        ...state,
        pdfData: action.payload,
        pdfGenerating: false,
        pdfError: null
      }
    }

    case 'SET_SIGNED_PDF_DATA': {
      return {
        ...state,
        signedPdfData: action.payload,
        pdfGenerating: false,
        pdfError: null
      }
    }

    case 'SET_PDF_ERROR': {
      return {
        ...state,
        pdfError: action.payload,
        pdfGenerating: false
      }
    }

    case 'CLEAR_PDF_DATA': {
      return {
        ...state,
        pdfData: null,
        pdfError: null,
        pdfGenerating: false
      }
    }

    // Signature Actions
    case 'SET_SIGNATURE_DATA': {
      return {
        ...state,
        signatureData: action.payload,
        isDirty: true
      }
    }

    case 'CLEAR_SIGNATURE_DATA': {
      return {
        ...state,
        signatureData: null,
        isDirty: true
      }
    }

    // Persistence Actions
    case 'MARK_DIRTY': {
      return {
        ...state,
        isDirty: true
      }
    }

    case 'MARK_SAVED': {
      return {
        ...state,
        isDirty: false,
        lastSaved: action.payload || new Date()
      }
    }

    case 'SET_AUTO_SAVE': {
      return {
        ...state,
        autoSaveEnabled: action.payload
      }
    }

    case 'RESTORE_FROM_STORAGE': {
      return {
        ...state,
        ...action.payload,
        // Ensure we don't overwrite critical runtime state
        sessionId: state.sessionId,
        startedAt: state.startedAt
      }
    }

    // Metadata Actions
    case 'SET_EMPLOYEE_ID': {
      return {
        ...state,
        employeeId: action.payload
      }
    }

    case 'SET_LANGUAGE': {
      return {
        ...state,
        language: action.payload
      }
    }

    case 'SET_DEBUG_MODE': {
      return {
        ...state,
        debugMode: action.payload
      }
    }

    case 'MARK_COMPLETED': {
      return {
        ...state,
        completedAt: new Date(),
        currentStep: HealthInsuranceStep.COMPLETE,
        isDirty: true // Mark dirty so completion is saved
      }
    }

    // Reset Actions
    case 'RESET_STATE': {
      return createInitialHealthInsuranceState(state.employeeId, state.language)
    }

    case 'RESET_FORM_DATA': {
      const initialState = createInitialHealthInsuranceState(state.employeeId, state.language)
      return {
        ...state,
        formData: initialState.formData,
        currentStep: HealthInsuranceStep.FORM,
        previousStep: null,
        canGoBack: false,
        canGoForward: false,
        pdfData: null,
        signatureData: null,
        isDirty: true
      }
    }

    default:
      return state
  }
}

// Action creators for common operations
export const healthInsuranceActions = {
  // Form actions
  updateFormData: (data: Partial<any>) => ({ 
    type: 'UPDATE_FORM_DATA' as const, 
    payload: data 
  }),
  
  setPersonalInfo: (info: any) => ({ 
    type: 'SET_PERSONAL_INFO' as const, 
    payload: info 
  }),
  
  validateForm: (fields?: string[]) => ({ 
    type: 'VALIDATE_FORM' as const, 
    payload: fields 
  }),

  // Navigation actions
  goToStep: (step: HealthInsuranceStep) => ({ 
    type: 'SET_CURRENT_STEP' as const, 
    payload: step 
  }),
  
  nextStep: () => ({ type: 'ADVANCE_STEP' as const }),
  
  previousStep: () => ({ type: 'GO_BACK' as const }),

  // Loading actions
  setLoading: (operation: string, message?: string, progress?: number) => ({ 
    type: 'SET_LOADING' as const, 
    payload: { operation, message, progress } 
  }),
  
  clearLoading: () => ({ type: 'CLEAR_LOADING' as const }),

  // Error actions
  setError: (key: string, error: any) => ({ 
    type: 'SET_ERROR' as const, 
    payload: { key, error } 
  }),
  
  clearError: (key: string) => ({ 
    type: 'CLEAR_ERROR' as const, 
    payload: key 
  }),

  // PDF actions
  setPDFGenerating: (generating: boolean) => ({ 
    type: 'SET_PDF_GENERATING' as const, 
    payload: generating 
  }),
  
  setPDFData: (data: string) => ({ 
    type: 'SET_PDF_DATA' as const, 
    payload: data 
  }),

  // Signature actions
  setSignature: (signature: any) => ({ 
    type: 'SET_SIGNATURE_DATA' as const, 
    payload: signature 
  }),

  // Persistence actions
  markSaved: (date?: Date) => ({ 
    type: 'MARK_SAVED' as const, 
    payload: date 
  }),
  
  // Completion actions
  markCompleted: () => ({ type: 'MARK_COMPLETED' as const })
}
