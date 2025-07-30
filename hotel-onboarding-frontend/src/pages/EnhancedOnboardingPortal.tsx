import React, { useState, useEffect } from 'react'
import { useSearchParams, useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CheckCircle, Clock, AlertCircle, Globe, Users, RefreshCw, Info, AlertTriangle, Shield } from 'lucide-react'
import axios from 'axios'

// Import enhanced services
import { GovernmentFormMappingService } from '@/utils/governmentFormMapping'
import { OfficialPacketMappingService, ONBOARDING_WORKFLOW_STEPS } from '@/utils/officialPacketMapping'
import { autoFillManager } from '@/utils/autoFillManager'
import { ONBOARDING_STEPS as UNIFIED_STEPS, normalizeStepId } from '@/config/onboardingSteps.config'

// Import form components
import PersonalInformationForm from '../components/PersonalInformationForm'
import I9Section1Form from '../components/I9Section1Form'
import I9SupplementA from '../components/I9SupplementA'
import I9SupplementB from '../components/I9SupplementB'
import I9ReviewAndSign from '../components/I9ReviewAndSign'
import W4Form from '../components/W4Form'
import W4ReviewAndSign from '../components/W4ReviewAndSign'
import DirectDepositForm from '../components/DirectDepositForm'
import EmergencyContactsForm from '../components/EmergencyContactsForm'
import HealthInsuranceForm from '../components/HealthInsuranceForm'
import WeaponsPolicyAcknowledgment from '../components/WeaponsPolicyAcknowledgment'
import HumanTraffickingAwareness from '../components/HumanTraffickingAwareness'

// Import onboarding step components
import WelcomeStep from './onboarding/WelcomeStep'
import JobDetailsStep from './onboarding/JobDetailsStep'
import PersonalInfoStep from './onboarding/PersonalInfoStep'
import I9Section1Step from './onboarding/I9Section1Step'
import I9ReviewSignStep from './onboarding/I9ReviewSignStep'
import W4FormStep from './onboarding/W4FormStep'
import W4ReviewSignStep from './onboarding/W4ReviewSignStep'
import DirectDepositStep from './onboarding/DirectDepositStep'
import HealthInsuranceStep from './onboarding/HealthInsuranceStep'
import EmergencyContactsStep from './onboarding/EmergencyContactsStep'
import CompanyPoliciesStep from './onboarding/CompanyPoliciesStep'
import TraffickingAwarenessStep from './onboarding/TrafficakingAwarenessStep'
import WeaponsPolicyStep from './onboarding/WeaponsPolicyStep'
import FinalReviewStep from './onboarding/FinalReviewStep'
import I9SupplementsStep from './onboarding/I9SupplementsStep'

// Import enhanced PDF viewer
import PDFDocumentViewer from '@/components/ui/pdf-document-viewer'

// Use the unified onboarding steps configuration
const ONBOARDING_STEPS = UNIFIED_STEPS

interface OnboardingSession {
  id: string
  status: string
  current_step: string
  progress_percentage: number
  language_preference: string
  expires_at: string
}

interface Employee {
  id: string
  name: string
  email: string
  position: string
  department: string
  hire_date: string
  personal_info: any
}

interface Property {
  name: string
  address: string
}

interface OnboardingData {
  session: OnboardingSession
  employee: Employee
  property: Property
  onboarding_steps: string[]
}

export default function EnhancedOnboardingPortal() {
  const [searchParams] = useSearchParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [onboardingData, setOnboardingData] = useState<OnboardingData | null>(null)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [language, setLanguage] = useState<'en' | 'es'>('en')
  const [formData, setFormData] = useState<Record<string, any>>({})
  const [completedSteps, setCompletedSteps] = useState<string[]>([])
  const [skipI9SupplementA, setSkipI9SupplementA] = useState(false)
  const [skipI9SupplementB, setSkipI9SupplementB] = useState(false)
  const [stepValidation, setStepValidation] = useState<Record<string, { isValid: boolean; errors: string[]; warnings: string[] }>>({})
  const [isSaving, setIsSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [showSupplementDialog, setShowSupplementDialog] = useState(false)
  const [progressSummary, setProgressSummary] = useState(OfficialPacketMappingService.getCompletionSummary([]))

  const token = searchParams.get('token')

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Allow keyboard navigation only if no input elements are focused
      if (event.target instanceof HTMLInputElement || 
          event.target instanceof HTMLTextAreaElement || 
          event.target instanceof HTMLSelectElement) {
        return
      }

      switch (event.key) {
        case 'ArrowRight':
        case 'ArrowDown':
          event.preventDefault()
          nextStep()
          break
        case 'ArrowLeft':
        case 'ArrowUp':
          event.preventDefault()
          prevStep()
          break
        case 'Escape':
          event.preventDefault()
          // Focus on the main navigation
          const mainNav = document.querySelector('#main-content')
          if (mainNav instanceof HTMLElement) {
            mainNav.focus()
          }
          break
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault()
            const stepIndex = parseInt(event.key) - 1
            if (stepIndex < ONBOARDING_STEPS.length) {
              navigateToStep(stepIndex)
            }
          }
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [currentStepIndex])

  useEffect(() => {
    // Allow access without token for demo/testing purposes
    // If no token provided, use a default test token
    const effectiveToken = token || 'demo-token'
    
    verifyToken(effectiveToken)
  }, [token])

  const verifyToken = async (tokenToVerify = token) => {
    try {
      setLoading(true)
      
      // Try to verify token with backend
      try {
        const response = await axios.get(`http://127.0.0.1:8000/onboard/verify?token=${tokenToVerify}`)
        
        if (response.data.success) {
          const onboardingData = response.data.data
          setOnboardingData(onboardingData)
          setLanguage(onboardingData.session.language_preference || 'en')
          
          // Load any saved progress from localStorage
          const savedSession = autoFillManager.getSessionData()
          if (savedSession.formData) {
            setFormData(savedSession.formData)
          }
          
          // Set current step index based on session data
          const stepIndex = ONBOARDING_STEPS.findIndex(step => step.id === onboardingData.session.current_step)
          if (stepIndex >= 0) {
            setCurrentStepIndex(stepIndex)
          }
        } else {
          setError(response.data.message || 'Invalid or expired onboarding link.')
        }
      } catch (apiError) {
        // Fallback to demo mode for testing if API fails
        if (tokenToVerify === 'test-token' || tokenToVerify === 'demo-token' || !token) {
          const mockOnboardingData = {
            valid: true,
            session: {
              id: 'test-session-1',
              status: 'in_progress',
              current_step: 'welcome',
              progress_percentage: 0,
              language_preference: 'en',
              expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
            },
            employee: {
              id: 'demo-emp-1',
              name: 'Demo Employee',
              email: 'demo.employee@hoteltest.com',
              position: 'Front Desk Agent',
              department: 'Guest Services',
              hire_date: new Date().toISOString(),
              personal_info: {}
            },
            property: {
              name: 'Grand Vista Hotel',
              address: '123 Main Street, Demo City, DC 12345'
            },
            onboarding_steps: ONBOARDING_STEPS.map(s => s.id)
          }
          
          setOnboardingData({
            session: mockOnboardingData.session,
            employee: mockOnboardingData.employee,
            property: mockOnboardingData.property,
            onboarding_steps: mockOnboardingData.onboarding_steps
          })
          setLanguage('en')
        } else {
          console.error('Token verification error:', apiError)
          setError('Unable to verify onboarding link. Please try again later.')
        }
      }
    } catch (error: any) {
      console.error('Token verification failed:', error)
      if (error.response?.status === 401) {
        setError('Your onboarding link has expired or is invalid. Please contact your manager for a new link.')
      } else {
        setError('Failed to load onboarding session. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Enhanced progress update with auto-save feedback
  const updateProgress = async (stepId: string, stepFormData: any = {}) => {
    try {
      setIsSaving(true)
      setSaveStatus('saving')
      
      // Save to localStorage for persistence during testing
      const persistedData = {
        token,
        step: stepId,
        form_data: { ...formData, ...stepFormData },
        language_preference: language,
        currentStepIndex: currentStepIndex,
        timestamp: new Date().toISOString()
      }
      localStorage.setItem(`onboarding_${token}`, JSON.stringify(persistedData))
      
      // Simulate save delay for better UX feedback
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)
      
      // For testing, bypass backend call
      console.log('Progress updated:', persistedData)
      
      // Uncomment for real backend integration:
      /*
      await axios.post('http://127.0.0.1:8000/onboard/update-progress', {
        token,
        step: stepId,
        form_data: stepFormData,
        language_preference: language
      })
      */
    } catch (error) {
      console.error('Failed to update progress:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } finally {
      setIsSaving(false)
    }
  }

  // Enhanced step completion with official packet mapping
  const markStepComplete = (stepId: string, data?: any) => {
    if (!completedSteps.includes(stepId)) {
      const newCompletedSteps = [...completedSteps, stepId]
      setCompletedSteps(newCompletedSteps)
      
      // Update progress summary
      const summary = OfficialPacketMappingService.getCompletionSummary(newCompletedSteps)
      setProgressSummary(summary)
      
      // Update form data if provided
      if (data) {
        setFormData(prev => ({
          ...prev,
          [stepId]: {
            ...prev[stepId],
            ...data,
            completed_at: new Date().toISOString(),
            completed: true
          }
        }))
      }
      
      console.log(`✅ Step completed: ${stepId}`, { 
        progress: `${summary.completed}/${summary.total}`,
        federalProgress: `${summary.federalCompleted}/${summary.federalTotal}`,
        timeRemaining: `${summary.estimatedTimeRemaining} minutes`
      })
    }
  }

  // Enhanced navigation using official packet mapping
  const getNextAvailableStep = (currentStepId: string): string | null => {
    // Find current step index
    const currentIndex = ONBOARDING_STEPS.findIndex(step => step.id === currentStepId)
    console.log('Current step ID:', currentStepId, 'Current index:', currentIndex)
    
    // If we can't find the current step or we're at the last step, return null
    if (currentIndex === -1 || currentIndex >= ONBOARDING_STEPS.length - 1) {
      return null
    }
    
    // Return the next step
    const nextStep = ONBOARDING_STEPS[currentIndex + 1]
    console.log('Found next step:', nextStep?.id)
    return nextStep?.id || null
  }

  // Validate step dependencies using official packet mapping
  const canAccessStep = (stepId: string): boolean => {
    // For now, allow access to all steps in sequence
    // In a production app, you'd check dependencies properly
    console.log('Checking if can access step:', stepId)
    const step = ONBOARDING_STEPS.find(s => s.id === stepId)
    
    // If step has no dependencies, it's accessible
    if (!step?.dependencies || step.dependencies.length === 0) {
      console.log('Step has no dependencies, allowing access')
      return true
    }
    
    // Check if all dependencies are completed
    const allDependenciesMet = step.dependencies.every(dep => completedSteps.includes(dep))
    console.log('Dependencies:', step.dependencies, 'Completed:', completedSteps, 'All met:', allDependenciesMet)
    return allDependenciesMet
  }

  // Smart step validation
  const validateCurrentStep = (): { isValid: boolean; errors: string[]; warnings: string[] } => {
    const currentStep = ONBOARDING_STEPS[currentStepIndex]
    const stepData = formData[currentStep.id] || {}
    
    let validation = { isValid: true, errors: [], warnings: [] }

    switch (currentStep.id) {
      case 'welcome':
        validation.isValid = true // Welcome step is always valid
        break
        
      case 'personal_info':
        if (!stepData.firstName) validation.errors.push('First name is required')
        if (!stepData.lastName) validation.errors.push('Last name is required')
        if (!stepData.dateOfBirth) validation.errors.push('Date of birth is required')
        if (!stepData.ssn) validation.errors.push('Social Security Number is required')
        if (!stepData.email) validation.errors.push('Email address is required')
        if (!stepData.phone) validation.errors.push('Phone number is required')
        if (!stepData.address) validation.errors.push('Address is required')
        if (!stepData.city) validation.errors.push('City is required')
        if (!stepData.state) validation.errors.push('State is required')
        if (!stepData.zipCode) validation.errors.push('ZIP code is required')
        break
        
      case 'i9_section1':
        if (!stepData.employee_first_name) validation.errors.push('Employee first name is required')
        if (!stepData.employee_last_name) validation.errors.push('Employee last name is required')
        if (!stepData.citizenship_status) validation.errors.push('Citizenship status must be selected')
        if (!stepData.section_1_completed_at) validation.errors.push('Section 1 must be completed')
        break
        
        
      case 'i9_review_sign':
        const section1Data = formData.i9_section1
        if (!section1Data || !section1Data.section_1_completed_at) {
          validation.errors.push('I-9 Section 1 must be completed first')
        }
        break
        
      case 'w4_form':
        // Check if personal info exists for auto-fill
        const personalInfo = formData.personal_info || {}
        
        if (!stepData.first_name && !personalInfo.firstName) (validation.errors as string[]).push('First name is required')
        if (!stepData.last_name && !personalInfo.lastName) (validation.errors as string[]).push('Last name is required')
        if (!stepData.ssn && !personalInfo.ssn) (validation.errors as string[]).push('Social Security Number is required')
        if (!stepData.filing_status) (validation.errors as string[]).push('Filing status must be selected')
        if (!stepData.address && !personalInfo.address) (validation.errors as string[]).push('Address is required')
        if (!stepData.city && !personalInfo.city) (validation.errors as string[]).push('City is required')
        if (!stepData.state && !personalInfo.state) (validation.errors as string[]).push('State is required')
        if (!stepData.zip_code && !personalInfo.zipCode) (validation.errors as string[]).push('ZIP code is required')
        if (!stepData.signature) (validation.errors as string[]).push('Digital signature is required')
        if (!stepData.signature_date) (validation.errors as string[]).push('Signature date is required')
        
        // Warn if personal info is missing for auto-fill
        if (!personalInfo.firstName && !personalInfo.lastName) {
          (validation.warnings as string[]).push('Complete Personal Information step first for automatic form filling')
        }
        break
        
      case 'w4_review_sign':
        const w4Data = formData.w4_form
        if (!w4Data || !w4Data.signature) {
          validation.errors.push('W-4 form must be completed first')
        }
        if (!stepData.review_acknowledgments_completed) {
          validation.errors.push('Review acknowledgments must be completed')
        }
        if (!stepData.final_signature) {
          validation.errors.push('Final digital signature is required')
        }
        break
        
      case 'direct_deposit':
        if (stepData.depositType === 'full' || stepData.depositType === 'partial') {
          if (!stepData.primaryAccount?.bankName) validation.errors.push('Bank name is required')
          if (!stepData.primaryAccount?.routingNumber) validation.errors.push('Routing number is required')
          if (!stepData.primaryAccount?.accountNumber) validation.errors.push('Account number is required')
          if (!stepData.primaryAccount?.accountType) validation.errors.push('Account type must be selected')
        }
        break
        
      case 'emergency_contacts':
        if (!stepData.primaryContact?.name) validation.errors.push('Primary emergency contact name is required')
        if (!stepData.primaryContact?.phoneNumber) validation.errors.push('Primary emergency contact phone is required')
        if (!stepData.primaryContact?.relationship) validation.errors.push('Relationship to primary contact is required')
        break
        
      case 'health_insurance':
        if (!stepData.medical_plan) validation.errors.push('Medical plan selection is required')
        if (!stepData.medical_tier) validation.errors.push('Coverage tier selection is required')
        break
        
      default:
        // For other steps, check if there's any data saved
        if (Object.keys(stepData).length === 0) {
          validation.warnings.push('This step appears to be incomplete')
        }
    }
    
    validation.isValid = validation.errors.length === 0
    
    // Update validation state
    setStepValidation(prev => ({
      ...prev,
      [currentStep.id]: validation
    }))
    
    return validation
  }

  // Enhanced next step with validation using official packet mapping
  const nextStep = async () => {
    console.log('Next button clicked, currentStepIndex:', currentStepIndex)
    const currentStep = ONBOARDING_STEPS[currentStepIndex]
    console.log('Current step:', currentStep)
    
    // Validate current step before proceeding
    const validation = validateCurrentStep()
    console.log('Validation result:', validation)
    
    if (!validation.isValid) {
      console.log('Step validation failed:', validation.errors)
      return
    }

    // Mark current step as complete if validation passes
    console.log('Marking step complete:', currentStep.id)
    markStepComplete(currentStep.id, formData[currentStep.id])

    // Use official packet mapping to get next step
    const nextStepId = getNextAvailableStep(currentStep.id)
    console.log('Next step ID:', nextStepId)
    
    if (nextStepId) {
      const nextStepIndex = ONBOARDING_STEPS.findIndex(step => step.id === nextStepId)
      console.log('Next step index:', nextStepIndex)
      
      if (nextStepIndex !== -1 && canAccessStep(nextStepId)) {
        console.log('Moving to next step')
        setCurrentStepIndex(nextStepIndex)
        await updateProgress(nextStepId, formData)
        
        // Clear validation for next step
        setStepValidation(prev => ({
          ...prev,
          [nextStepId]: { isValid: true, errors: [], warnings: [] }
        }))
      } else {
        console.warn('Cannot access next step due to unmet dependencies:', nextStepId)
      }
    } else {
      console.log('Onboarding complete - no more steps available')
    }
  }

  const shouldSkipStep = (stepId: string): boolean => {
    switch (stepId) {
      case 'i9_supplement_a':
        return skipI9SupplementA
      case 'i9_supplement_b':
        return skipI9SupplementB
      default:
        return false
    }
  }

  // Enhanced validation for government compliance using official packet mapping
  const canNavigateToStep = (stepIndex: number): boolean => {
    const step = ONBOARDING_STEPS[stepIndex]
    
    // Use official packet mapping for dependency validation
    const canAccess = canAccessStep(step.id)
    
    // Additional checks for government-required steps
    if (step.governmentRequired && !canAccess) {
      console.warn(`Cannot navigate to government-required step: ${step.id}. Missing dependencies:`, step.dependencies)
      return false
    }
    
    // Can navigate to completed steps or accessible next steps
    return canAccess || completedSteps.includes(step.id)
  }

  const prevStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1)
    }
  }

  // Navigate to specific step (for breadcrumb navigation) with compliance validation
  const navigateToStep = async (stepIndex: number) => {
    if (stepIndex < 0 || stepIndex >= ONBOARDING_STEPS.length) return
    
    // Use enhanced compliance validation
    const canNavigate = canNavigateToStep(stepIndex)
    
    if (canNavigate) {
      setCurrentStepIndex(stepIndex)
      const step = ONBOARDING_STEPS[stepIndex]
      await updateProgress(step.id, formData)
    } else {
      // Show error message for compliance violations
      const step = ONBOARDING_STEPS[stepIndex]
      if (step.governmentRequired) {
        console.warn('Cannot navigate to government-required step without completing prerequisites:', step.id)
      }
    }
  }

  const changeLanguage = async (newLanguage: 'en' | 'es') => {
    setLanguage(newLanguage)
    await updateProgress(ONBOARDING_STEPS[currentStepIndex].id, { language_preference: newLanguage })
  }

  const getStepStatus = (stepIndex: number) => {
    const step = ONBOARDING_STEPS[stepIndex]
    
    if (completedSteps.includes(step.id)) return 'completed'
    if (stepIndex === currentStepIndex) return 'current'
    if (canAccessStep(step.id)) return 'available'
    return 'locked'
  }

  const getTotalEstimatedTime = () => {
    return ONBOARDING_STEPS.reduce((total, step) => total + step.estimatedMinutes, 0)
  }

  // Handle I-9 supplement selection after Section 1 completion
  const handleSupplementSelection = (choice: 'none' | 'a' | 'b') => {
    setShowSupplementDialog(false)
    
    // Set skip flags based on choice
    if (choice === 'a') {
      setSkipI9SupplementA(false)
      setSkipI9SupplementB(true)
      // Navigate to Supplement A
      const supplementAIndex = ONBOARDING_STEPS.findIndex(step => step.id === 'i9_supplement_a')
      setCurrentStepIndex(supplementAIndex)
    } else if (choice === 'b') {
      setSkipI9SupplementA(true)
      setSkipI9SupplementB(false)
      // Navigate to Supplement B
      const supplementBIndex = ONBOARDING_STEPS.findIndex(step => step.id === 'i9_supplement_b')
      setCurrentStepIndex(supplementBIndex)
    } else {
      // choice === 'none' - skip both supplements
      setSkipI9SupplementA(true)
      setSkipI9SupplementB(true)
      // Navigate directly to I-9 review
      const reviewIndex = ONBOARDING_STEPS.findIndex(step => step.id === 'i9_review_sign')
      setCurrentStepIndex(reviewIndex)
    }

    // Save the supplement choice to formData
    setFormData(prev => ({
      ...prev,
      i9_supplement_choice: {
        supplement_a_needed: choice === 'a',
        supplement_b_needed: choice === 'b',
        supplements_completed_at: new Date().toISOString(),
        choice_made: true
      }
    }))
  }

  const t = (key: string) => {
    // Simple translation function - in production, use proper i18n library
    const translations: Record<string, Record<string, string>> = {
      en: {
        'loading': 'Loading...',
        'step_of': 'Step {current} of {total}',
        'progress': 'Progress',
        'complete': 'Complete',
        'estimated_time': 'Estimated time: {time} minutes',
        'next': 'Next',
        'previous': 'Previous',
        'save_continue': 'Save & Continue',
        'submit': 'Submit',
        'review_sign': 'Review & Sign'
      },
      es: {
        'loading': 'Cargando...',
        'step_of': 'Paso {current} de {total}',
        'progress': 'Progreso',
        'complete': 'Completar',
        'estimated_time': 'Tiempo estimado: {time} minutos',
        'next': 'Siguiente',
        'previous': 'Anterior',
        'save_continue': 'Guardar y Continuar',
        'submit': 'Enviar',
        'review_sign': 'Revisar y Firmar'
      }
    }
    return translations[language][key] || key
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <Card className="w-full max-w-sm sm:max-w-md p-4 sm:p-6 md:p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">{t('loading')}</h2>
          <p className="text-gray-600">Please wait while we prepare your onboarding experience...</p>
        </Card>
      </div>
    )
  }

  if (error || !onboardingData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-red-100 p-4">
        <Card className="w-full max-w-sm sm:max-w-md lg:max-w-lg p-4 sm:p-6 md:p-8 text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Access Denied</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Button onClick={() => window.location.href = '/apply'} variant="outline">
            Return to Job Portal
          </Button>
        </Card>
      </div>
    )
  }

  const currentStep = ONBOARDING_STEPS[currentStepIndex]
  const progressPercentage = OfficialPacketMappingService.calculateProgress(completedSteps)

  return (
    <div className="min-h-screen w-full flex flex-col bg-gradient-to-br from-hotel-neutral-50 via-white to-blue-50">
      {/* Skip Link for Accessibility */}
      <a 
        href="#main-content" 
        className="skip-link sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-hotel-primary text-white px-4 py-2 rounded-md z-50"
      >
        Skip to main content
      </a>
      
      {/* Live Region for Screen Reader Announcements */}
      <div 
        aria-live="polite" 
        aria-atomic="true" 
        className="sr-only"
        id="status-announcements"
      >
        {saveStatus === 'saving' && 'Saving your progress...'}
        {saveStatus === 'saved' && 'Progress saved successfully'}
        {saveStatus === 'error' && 'Error saving progress, please try again'}
        {stepValidation[currentStep?.id]?.errors?.length > 0 && 
          `Please fix ${stepValidation[currentStep.id].errors.length} error${stepValidation[currentStep.id].errors.length > 1 ? 's' : ''} before continuing`
        }
      </div>

      {/* Enterprise Header */}
      <header 
        className="flex-shrink-0 header-enhanced"
        role="banner"
      >
        <div className="header-content">
          <div className="flex items-center space-x-6">
            <div className="relative">
              <div className="logo-enhanced">
                <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div className="absolute -bottom-1 -right-1 h-5 w-5 bg-green-500 rounded-full border-3 border-white flex items-center justify-center shadow-lg">
                <div className="h-2 w-2 bg-white rounded-full animate-pulse-soft"></div>
              </div>
            </div>
            <div>
              <h1 className="header-title">
                Employee Onboarding
                <span className="sr-only">
                  - Step {currentStepIndex + 1} of {ONBOARDING_STEPS.length}: {language === 'es' ? currentStep.titleEs : currentStep.title}
                </span>
              </h1>
              <div className="flex items-center space-x-3 mt-2">
                <div className="inline-flex items-center px-3 py-1 rounded-full bg-hotel-primary/10 text-hotel-primary text-sm font-semibold">
                  <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  {onboardingData.property.name}
                </div>
                <span className="text-gray-400" aria-hidden="true">•</span>
                <span className="text-sm text-gray-600 font-medium">{onboardingData.employee.name}</span>
              </div>
            </div>
          </div>

          {/* Enhanced Language Selector */}
          <div className="flex items-center space-x-6">
            <div className="hidden lg:flex items-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Secure Connection</span>
              </div>
            </div>
            <fieldset className="flex items-center space-x-1 bg-gray-50/70 rounded-xl p-1 border border-gray-200/50 shadow-sm">
              <legend className="sr-only">Select Language</legend>
              <Globe className="h-4 w-4 text-gray-500 ml-3" aria-hidden="true" />
              <button
                onClick={() => changeLanguage('en')}
                aria-pressed={language === 'en'}
                aria-label="Switch to English"
                className={`px-4 py-2.5 text-sm font-semibold rounded-lg transition-all duration-300 touch-target ${
                  language === 'en' 
                    ? 'bg-white text-hotel-primary shadow-md ring-2 ring-hotel-primary/20 transform scale-105' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-white/70'
                }`}
              >
                English
              </button>
              <button
                onClick={() => changeLanguage('es')}
                aria-pressed={language === 'es'}
                aria-label="Cambiar a Español"
                className={`px-4 py-2.5 text-sm font-semibold rounded-lg transition-all duration-300 touch-target ${
                  language === 'es' 
                    ? 'bg-white text-hotel-primary shadow-md ring-2 ring-hotel-primary/20 transform scale-105' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-white/70'
                }`}
              >
                Español
              </button>
            </fieldset>
          </div>
        </div>
      </header>

      {/* Enhanced Progress Section */}
      <section 
        className="flex-shrink-0 bg-gradient-to-r from-white to-hotel-neutral-50 border-b border-gray-200"
        aria-label="Onboarding Progress"
      >
        <div className="w-full px-2 sm:px-4 md:px-6 lg:px-8 py-3 sm:py-4">
          {/* Enhanced Employee Info Card */}
          <div className="mb-4 bg-gradient-to-r from-hotel-primary/5 to-blue-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-hotel-primary/10">
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-2 sm:gap-3 md:gap-4 lg:gap-6">
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 bg-hotel-primary/10 rounded-lg flex items-center justify-center">
                  <Users className="h-5 w-5 text-hotel-primary" />
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Employee</span>
                  <p className="text-sm font-semibold text-gray-900">{onboardingData.employee.name}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 bg-hotel-secondary/10 rounded-lg flex items-center justify-center">
                  <svg className="h-5 w-5 text-hotel-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m8 6V9a2 2 0 00-2-2H10a2 2 0 00-2 2v3.1M15 13l-3-3-3 3" />
                  </svg>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Position</span>
                  <p className="text-sm font-semibold text-gray-900">{onboardingData.employee.position}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Department</span>
                  <p className="text-sm font-semibold text-gray-900">{onboardingData.employee.department}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg className="h-5 w-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 8h6m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Start Date</span>
                  <p className="text-sm font-semibold text-gray-900">
                    {new Date(onboardingData.employee.hire_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Breadcrumb Navigation */}
          <div className="mb-3">
            <nav className="flex" aria-label="Breadcrumb">
              <ol className="flex items-center space-x-2 overflow-x-auto pb-2">
                {ONBOARDING_STEPS.slice(0, Math.min(currentStepIndex + 3, ONBOARDING_STEPS.length)).map((step, index) => {
                  const status = getStepStatus(index)
                  const isClickable = canNavigateToStep(index)
                  const isLast = index === Math.min(currentStepIndex + 2, ONBOARDING_STEPS.length - 1)
                  
                  return (
                    <li key={step.id} className="flex items-center">
                      <button
                        onClick={() => isClickable && navigateToStep(index)}
                        disabled={!isClickable}
                        className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                          status === 'current'
                            ? 'bg-blue-600 text-white shadow-sm hover:bg-blue-700'
                            : status === 'completed'
                            ? 'bg-green-100 text-green-800 hover:bg-green-200'
                            : step.governmentRequired && !isClickable
                            ? 'bg-red-50 text-red-600 cursor-not-allowed border border-red-200'
                            : 'bg-gray-100 text-gray-500 cursor-not-allowed'
                        } ${isClickable && status !== 'current' ? 'hover:shadow-md' : ''}`}
                        aria-current={status === 'current' ? 'step' : undefined}
                        title={step.governmentRequired && !isClickable ? 'Complete previous government-required steps first' : ''}
                      >
                        {status === 'completed' ? (
                          <CheckCircle className="h-4 w-4" />
                        ) : step.governmentRequired && !isClickable ? (
                          <AlertTriangle className="h-4 w-4" />
                        ) : (
                          <span className={`flex items-center justify-center w-5 h-5 rounded-full text-xs font-bold ${
                          status === 'current' ? 'bg-white/20' : 'bg-current/20'
                        }`}>
                            {index + 1}
                          </span>
                        )}
                        <span className="hidden sm:inline-block">
                          {(language === 'es' ? step.titleEs : step.title).length > 20 
                            ? (language === 'es' ? step.titleEs : step.title).substring(0, 20) + '...' 
                            : (language === 'es' ? step.titleEs : step.title)}
                        </span>
                        <span className="sm:hidden">
                          {index + 1}
                        </span>
                        {step.governmentRequired && (
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 ml-1">
                            REQ
                          </span>
                        )}
                      </button>
                      {!isLast && (
                        <svg className="flex-shrink-0 w-5 h-5 text-gray-300 mx-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </li>
                  )
                })}
                {currentStepIndex + 3 < ONBOARDING_STEPS.length && (
                  <li className="flex items-center">
                    <span className="text-gray-400 text-sm px-2">
                      ... {ONBOARDING_STEPS.length - currentStepIndex - 3} more steps
                    </span>
                  </li>
                )}
              </ol>
            </nav>
          </div>

          {/* Enhanced Progress Bar */}
          <div className="mb-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h3 className="text-base font-semibold text-gray-900">Progress Overview</h3>
                <p className="text-xs text-gray-600">
                  Step {currentStepIndex + 1} of {ONBOARDING_STEPS.length} • 
                  {progressSummary.completed}/{progressSummary.total} completed
                </p>
              </div>
              <div className="flex items-center space-x-4 text-xs text-gray-600">
                <div className="flex items-center space-x-1">
                  <Shield className="h-3 w-3 text-blue-600" />
                  <span>Federal: {progressSummary.federalCompleted}/{progressSummary.federalTotal}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>~{progressSummary.estimatedTimeRemaining} min left</span>
                </div>
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-3 w-3 text-green-500" />
                  <span>{Math.round(progressPercentage)}% Complete</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <Progress value={progressPercentage} className="w-full h-3 bg-gray-200 rounded-full overflow-hidden" />
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xs font-medium text-white drop-shadow-sm">
                  {Math.round(progressPercentage)}%
                </span>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* Enhanced Main Content */}
      <main 
        id="main-content"
        className="flex-1 flex flex-col min-h-0"
        role="main"
        aria-label={`Onboarding Step ${currentStepIndex + 1}: ${language === 'es' ? currentStep.titleEs : currentStep.title}`}
      >
        <div className="flex-1 w-full px-2 sm:px-4 md:px-6 lg:px-8 py-2 sm:py-3 md:py-4 min-h-0">
        <div className="flex flex-col h-full w-full max-w-none card-elevated animate-fade-in">
          <CardHeader className="flex-shrink-0 bg-gradient-to-r from-white to-hotel-neutral-50 border-b border-gray-100 py-2 sm:py-3 md:py-4 lg:py-6 px-2 sm:px-4 md:px-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0">
              <div className="flex-1 min-w-0">
                <CardTitle className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 truncate">
                  {language === 'es' ? currentStep.titleEs : currentStep.title}
                </CardTitle>
                <CardDescription className="mt-1 text-xs sm:text-sm text-gray-600 line-clamp-2">
                  {currentStep.description}
                  {currentStep.estimatedMinutes > 0 && (
                    <span className="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-hotel-primary/10 text-hotel-primary">
                      <Clock className="h-3 w-3 mr-1" />
                      ~{currentStep.estimatedMinutes} min
                    </span>
                  )}
                </CardDescription>
              </div>
              <div className="flex items-center justify-end sm:justify-start space-x-3 flex-shrink-0">
                <Badge variant="outline" className="text-xs px-2 py-1 bg-white border-hotel-primary/20 text-hotel-primary whitespace-nowrap">
                  Step {currentStepIndex + 1} of {ONBOARDING_STEPS.length}
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex-1 p-2 sm:p-4 md:p-6 lg:p-8 overflow-auto min-h-0">
            {/* Render step content based on current step */}
            <div className="animate-slide-in-right">
              {renderStepContent()}
            </div>

            {/* Validation Errors Display */}
            {stepValidation[currentStep.id]?.errors?.length > 0 && (
              <Alert className="mt-6 border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription>
                  <div className="font-medium text-red-800 mb-2">Please fix the following issues:</div>
                  <ul className="list-disc list-inside space-y-1 text-red-700">
                    {stepValidation[currentStep.id].errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {/* Validation Warnings Display */}
            {stepValidation[currentStep.id]?.warnings?.length > 0 && (
              <Alert className="mt-6 border-amber-200 bg-amber-50">
                <AlertCircle className="h-4 w-4 text-amber-600" />
                <AlertDescription>
                  <div className="font-medium text-amber-800 mb-2">Warnings:</div>
                  <ul className="list-disc list-inside space-y-1 text-amber-700">
                    {stepValidation[currentStep.id].warnings.map((warning, index) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {/* Enhanced Navigation */}
            <div className="flex-shrink-0 flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3 sm:gap-0 mt-4 sm:mt-6 pt-4 border-t border-gray-200">
              <Button
                variant="outline"
                onClick={() => prevStep()}
                disabled={currentStepIndex === 0}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed h-10 sm:h-12 px-4 sm:px-6 text-sm sm:text-base order-2 sm:order-1"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                {t('previous')}
              </Button>
              
              {/* Hidden auto-save indicator for functionality only */}
              <div className="sr-only" aria-live="polite">
                {saveStatus === 'saving' && 'Saving your progress...'}
                {saveStatus === 'saved' && 'Progress saved successfully'}
                {saveStatus === 'error' && 'Error saving progress'}
              </div>
              
              <Button
                onClick={nextStep}
                disabled={currentStepIndex === ONBOARDING_STEPS.length - 1 || isSaving}
                className={`btn-primary disabled:opacity-50 disabled:cursor-not-allowed h-10 sm:h-12 px-6 sm:px-8 text-sm sm:text-base font-semibold transition-all duration-200 order-1 sm:order-2 ${
                  stepValidation[currentStep.id]?.errors?.length > 0 
                    ? 'bg-red-600 hover:bg-red-700 animate-pulse' 
                    : ''
                }`}
              >
                {isSaving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    {currentStepIndex === ONBOARDING_STEPS.length - 2 ? t('review_sign') : t('next')}
                    <svg className="h-4 w-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </div>
        </div>
      </main>

      {/* I-9 Supplement Selection Dialog */}
      {showSupplementDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <Info className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                I-9 Supplement Selection
              </h3>
              <p className="text-gray-600">
                Do you need to complete any I-9 supplements? This choice is final.
              </p>
            </div>

            <div className="space-y-4">
              <Card className="border-2 hover:border-green-300 transition-colors cursor-pointer" 
                    onClick={() => handleSupplementSelection('none')}>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold text-gray-900">No Supplements Needed</h4>
                      <p className="text-sm text-gray-600">
                        I completed Section 1 independently without assistance and do not need work authorization reverification
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-2 hover:border-blue-300 transition-colors cursor-pointer"
                    onClick={() => handleSupplementSelection('a')}>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <Users className="h-6 w-6 text-blue-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold text-gray-900">Need Supplement A</h4>
                      <p className="text-sm text-gray-600">
                        <strong>Required if:</strong> Someone helped me complete Section 1 or provided translation assistance
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-2 hover:border-blue-300 transition-colors cursor-pointer"
                    onClick={() => handleSupplementSelection('b')}>
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <RefreshCw className="h-6 w-6 text-blue-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold text-gray-900">Need Supplement B</h4>
                      <p className="text-sm text-gray-600">
                        <strong>Required if:</strong> My work authorization has expired and needs renewal, or I am being rehired
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Alert className="mt-6 bg-amber-50 border-amber-200">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <AlertDescription className="text-amber-800">
                <strong>Important:</strong> Most employees select "No Supplements Needed" unless they specifically received help completing Section 1 or need work authorization reverification.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      )}
    </div>
  );

  // Enhanced step content rendering using modular components
  function renderStepContent() {
    const currentStep = ONBOARDING_STEPS[currentStepIndex]
    const stepProps = {
      currentStep,
      progress: {
        stepData: formData,
        completedSteps,
        progressSummary
      },
      markStepComplete,
      saveProgress: updateProgress,
      language,
      employee: onboardingData?.employee,
      property: onboardingData?.property
    }

    switch (currentStep.id) {
      case 'language_welcome':
      case 'welcome':
        return <WelcomeStep {...stepProps} />
        
      case 'job_details_confirmation':
        return <JobDetailsStep {...stepProps} />
        
      case 'personal_information':
        return <PersonalInfoStep {...stepProps} />
        
      case 'i9_section1':
        return <I9Section1Step {...stepProps} />
        
      case 'i9_supplements':
        return <I9SupplementsStep {...stepProps} />
        
      case 'i9_review_sign':
        return <I9ReviewSignStep {...stepProps} />
        
      case 'w4_tax_withholding':
        return <W4FormStep {...stepProps} />
        
      case 'w4_review_sign':
        return <W4ReviewSignStep {...stepProps} />
        
      case 'direct_deposit':
        return <DirectDepositStep {...stepProps} />
        
      case 'health_insurance':
        return <HealthInsuranceStep {...stepProps} />
        
      case 'emergency_contacts':
        return <EmergencyContactsStep {...stepProps} />
        
      case 'background_check':
        return <BackgroundCheckStep {...stepProps} />
        
      case 'photo_capture':
        return <PhotoCaptureStep {...stepProps} />
        
      case 'company_policies':
        return renderCompanyPoliciesStep()
        
      case 'safety_training':
        return renderTrafficingAwarenessStep()
        
      case 'final_review':
        return <FinalReviewStep {...stepProps} />
        
      default:
        return renderLegacyStep(currentStep.id)
    }
  }

  // Fallback for legacy step rendering
  function renderLegacyStep(stepId: string) {
    switch (stepId) {
      case 'personal_info':
        return renderPersonalInfoStep()
      case 'document_upload':
        return renderDocumentUploadStep()
      case 'i9_supplement_a':
        return renderI9SupplementAStep()
      case 'i9_supplement_b':
        return renderI9SupplementBStep()
      case 'w4_form':
        return renderW4FormStep()
      case 'direct_deposit':
        return renderDirectDepositStep()
      case 'health_insurance':
        return renderHealthInsuranceStep()
      case 'company_policies':
        return renderCompanyPoliciesStep()
      case 'trafficking_awareness':
        return renderTrafficingAwarenessStep()
      case 'employee_signature':
        return renderEmployeeSignatureStep()
      case 'manager_review':
        return renderManagerReviewStep()
      default:
        return renderPlaceholderStep()
    }
  }


  function renderPlaceholderStep() {
    return (
      <div className="text-center py-12">
        <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <Clock className="h-12 w-12 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {language === 'es' ? currentStep.titleEs : currentStep.title}
        </h3>
        <p className="text-gray-600 max-w-md mx-auto">
          This step is being developed. In the full implementation, this would contain the complete form for {currentStep.title.toLowerCase()}.
        </p>
      </div>
    )
  }

  // Legacy render functions - DEPRECATED
  // These are replaced by the new step components that include review and sign functionality
  /*
  function renderPersonalInfoStep() { 
    return (
      <PersonalInformationForm
        initialData={formData.personal_info || {}}
        language={language}
        onSave={(data) => {
          setFormData(prev => ({ ...prev, personal_info: data }));
          // Extract and save to AutoFillManager for use in subsequent forms
          autoFillManager.updateData({
            firstName: data.firstName,
            lastName: data.lastName,
            middleInitial: data.middleInitial,
            fullName: `${data.firstName} ${data.middleInitial ? data.middleInitial + ' ' : ''}${data.lastName}`.trim(),
            dateOfBirth: data.dateOfBirth,
            ssn: data.ssn,
            email: data.email,
            phoneNumber: data.phone,
            streetAddress: data.address,
            city: data.city,
            state: data.state,
            zipCode: data.zipCode,
            maritalStatus: data.maritalStatus,
            gender: data.gender,
            preferredName: data.preferredName
          });
        }}
        onNext={nextStep}
        onBack={() => setCurrentStepIndex(Math.max(0, currentStepIndex - 1))}
      />
    )
  }
  
  function renderJobDetailsStep() { return renderPlaceholderStep() }
  function renderDocumentUploadStep() { return renderPlaceholderStep() }
  
  function renderI9Section1Step() { 
    return (
      <I9Section1Form
        initialData={formData.i9_section1 || {}}
        language={language}
        onComplete={(data) => {
          setFormData(prev => ({ ...prev, i9_section1: data }));
          // After Section 1 completion, show supplement selection dialog
          setShowSupplementDialog(true);
        }}
      />
    )
  }
  
  function renderW4FormStep() {
    // Auto-fill W-4 form with personal information data
    const personalInfo = formData.personal_info || {};
    const autoFilledW4Data = autoFillManager.autoFillForm(formData.w4_form || {}, 'w4_form');
    
    // Combine personal info with existing W-4 data and auto-fill
    const initialW4Data = {
      first_name: personalInfo.firstName || autoFilledW4Data.first_name || '',
      middle_initial: personalInfo.middleInitial || autoFilledW4Data.middle_initial || '',
      last_name: personalInfo.lastName || autoFilledW4Data.last_name || '',
      address: personalInfo.address || autoFilledW4Data.address || '',
      city: personalInfo.city || autoFilledW4Data.city || '',
      state: personalInfo.state || autoFilledW4Data.state || '',
      zip_code: personalInfo.zipCode || autoFilledW4Data.zip_code || '',
      ssn: personalInfo.ssn || autoFilledW4Data.ssn || '',
      filing_status: autoFilledW4Data.filing_status || '',
      // Preserve existing W-4 specific data if already filled
      ...autoFilledW4Data,
      // Override with any explicitly set W-4 data
      ...(formData.w4_form || {})
    };
    
    return (
      <W4Form
        ocrData={initialW4Data}
        language={language}
        onSubmit={(data: any) => {
          setFormData(prev => ({ ...prev, w4_form: data }));
          // Extract and save W-4 data to AutoFillManager
          autoFillManager.updateData({
            firstName: data.first_name,
            lastName: data.last_name,
            middleInitial: data.middle_initial,
            fullName: `${data.first_name} ${data.middle_initial ? data.middle_initial + ' ' : ''}${data.last_name}`.trim(),
            streetAddress: data.address,
            city: data.city,
            state: data.state,
            zipCode: data.zip_code,
            ssn: data.ssn,
            maritalStatus: data.filing_status?.includes('Married') ? 'married' : 'single',
            dependentCount: (data.dependents_amount || 0) / 2000
          });
          nextStep();
        }}
      />
    )
  }
  
  function renderDirectDepositStep() { 
    return (
      <DirectDepositForm
        initialData={formData.direct_deposit || {}}
        language={language}
        onSave={(data) => setFormData(prev => ({ ...prev, direct_deposit: data }))}
        onNext={nextStep}
        onBack={() => setCurrentStepIndex(Math.max(0, currentStepIndex - 1))}
      />
    )
  }
  
  function renderEmergencyContactsStep() { 
    return (
      <EmergencyContactsForm
        initialData={formData.emergency_contacts || {}}
        language={language}
        onSave={(data) => setFormData(prev => ({ ...prev, emergency_contacts: data }))}
        onNext={nextStep}
        onBack={() => setCurrentStepIndex(Math.max(0, currentStepIndex - 1))}
      />
    )
  }
  
  function renderHealthInsuranceStep() { 
    return (
      <HealthInsuranceForm
        initialData={formData.health_insurance || {}}
        language={language}
        onSave={(data) => setFormData(prev => ({ ...prev, health_insurance: data }))}
        onNext={nextStep}
        onBack={() => setCurrentStepIndex(Math.max(0, currentStepIndex - 1))}
      />
    )
  }
  
  function renderCompanyPoliciesStep() { 
    return (
      <WeaponsPolicyAcknowledgment
        language={language}
        onComplete={(data) => {
          setFormData(prev => ({ ...prev, weapons_policy: data }));
          nextStep();
        }}
      />
    )
  }
  
  function renderTrafficingAwarenessStep() { 
    return (
      <HumanTraffickingAwareness
        language={language}
        onComplete={(data) => {
          setFormData(prev => ({ ...prev, trafficking_awareness: data }));
          nextStep();
        }}
      />
    )
  }
  
  function renderI9SupplementAStep() {
    return (
      <I9SupplementA
        // FEDERAL COMPLIANCE: Do NOT pass any initialData to ensure completely blank form
        // Supplement A is for preparer/translator ONLY - never employee data
        // This prevents auto-fill contamination which would violate federal compliance
        language={language}
        onComplete={(data) => {
          setFormData(prev => ({ ...prev, i9_supplement_a: data }));
          nextStep();
        }}
        onSkip={() => {
          setSkipI9SupplementA(true);
          nextStep();
        }}
        onBack={prevStep}
      />
    )
  }
  
  function renderI9SupplementBStep() {
    return (
      <I9SupplementB
        // FEDERAL COMPLIANCE: Pass employeeData for READ-ONLY display only
        // Employee fields should NOT be editable - they come from Section 1
        // This ensures only reverification data is collected, not employee data changes
        employeeData={formData.i9_section1 || {}}
        // Do NOT pass previous supplement B data to avoid auto-fill contamination
        language={language}
        onComplete={(data) => {
          setFormData(prev => ({ ...prev, i9_supplement_b: data }));
          nextStep();
        }}
        onSkip={() => {
          setSkipI9SupplementB(true);
          nextStep();
        }}
        onBack={prevStep}
      />
    )
  }
  
  function renderI9ReviewSignStep() {
    return (
      <I9ReviewAndSign
        section1Data={formData.i9_section1 || {}}
        supplementAData={!skipI9SupplementA ? formData.i9_supplement_a : undefined}
        supplementBData={!skipI9SupplementB ? formData.i9_supplement_b : undefined}
        language={language}
        onComplete={(data) => {
          setFormData(prev => ({ ...prev, i9_review_complete: data }));
          nextStep();
        }}
        onBack={prevStep}
      />
    )
  }
  
  function renderW4ReviewSignStep() {
    return (
      <W4ReviewAndSign
        w4FormData={formData.w4_form || {}}
        language={language}
        onComplete={(data) => {
          setFormData(prev => ({ ...prev, w4_review_complete: data }));
          nextStep();
        }}
        onBack={prevStep}
      />
    )
  }
  
  function renderBackgroundCheckStep() { return renderPlaceholderStep() }
  function renderPhotoCaptureStep() { return renderPlaceholderStep() }
  function renderEmployeeSignatureStep() { return renderPlaceholderStep() }
  function renderManagerReviewStep() { return renderPlaceholderStep() }
  */

  // Render current step based on step ID
  function renderCurrentStep() {
    const currentStep = ONBOARDING_STEPS[currentStepIndex]
    const normalizedId = normalizeStepId(currentStep.id)
    
    // Map step IDs to render functions - all using new step components
    switch (normalizedId) {
      case 'welcome':
        return <WelcomeStep {...getStepProps()} />
      case 'personal-info':
        return <PersonalInfoStep {...getStepProps()} />
      case 'job-details':
        return <JobDetailsStep {...getStepProps()} />
      case 'i9-section1':
        return <I9Section1Step {...getStepProps()} />
      case 'i9-review-sign':
        return <I9ReviewSignStep {...getStepProps()} />
      case 'i9-supplements':
        return <I9SupplementsStep {...getStepProps()} />
      case 'document-upload':
        return renderPlaceholderStep()
      case 'w4-form':
        return <W4FormStep {...getStepProps()} />
      case 'w4-review-sign':
        return <W4ReviewSignStep {...getStepProps()} />
      case 'direct-deposit':
        return <DirectDepositStep {...getStepProps()} />
      case 'health-insurance':
        return <HealthInsuranceStep {...getStepProps()} />
      case 'emergency-contacts':
        return <EmergencyContactsStep {...getStepProps()} />
      case 'company-policies':
        return <CompanyPoliciesStep {...getStepProps()} />
      case 'trafficking-awareness':
        return <TraffickingAwarenessStep {...getStepProps()} />
      case 'weapons-policy':
        return <WeaponsPolicyStep {...getStepProps()} />
      case 'final-review':
        return <FinalReviewStep {...getStepProps()} />
      default:
        return renderPlaceholderStep()
    }
  }

  // Get props for step components
  function getStepProps() {
    return {
      currentStep: ONBOARDING_STEPS[currentStepIndex],
      progress: {
        currentStepIndex,
        totalSteps: ONBOARDING_STEPS.length,
        completedSteps,
        stepData: formData
      },
      markStepComplete: (stepId: string, data?: any) => {
        setCompletedSteps(prev => [...new Set([...prev, stepId])])
        if (data) {
          setFormData(prev => ({ ...prev, [stepId]: data }))
        }
      },
      saveProgress: async (stepId: string, data?: any) => {
        if (data) {
          setFormData(prev => ({ ...prev, [stepId]: data }))
        }
        await updateProgress(stepId, { ...formData, [stepId]: data })
      },
      language,
      employee: onboardingData?.employee,
      property: onboardingData?.property
    }
  }

  // Check if user can proceed to next step
  function canProceedToNextStep(): boolean {
    const currentStep = ONBOARDING_STEPS[currentStepIndex]
    // Check if current step is completed
    return completedSteps.includes(currentStep.id) || !currentStep.required
  }

  // Main render
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center space-y-4">
          <RefreshCw className="h-8 w-8 text-blue-600 animate-spin mx-auto" />
          <p className="text-gray-600">Loading onboarding session...</p>
        </div>
      </div>
    )
  }

  if (error || !onboardingData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Onboarding Error</h2>
            <p className="text-gray-600 mb-6">{error || 'Unable to load onboarding session'}</p>
            <Button
              onClick={() => window.location.reload()}
              className="w-full"
            >
              Try Again
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Employee Onboarding</h1>
              <span className="ml-4 text-sm text-gray-500">
                {onboardingData.property.name}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => changeLanguage(language === 'en' ? 'es' : 'en')}
                className="flex items-center space-x-2"
              >
                <Globe className="h-4 w-4" />
                <span>{language === 'en' ? 'Español' : 'English'}</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="bg-white border-b border-gray-200">
        <div className="px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-medium text-gray-900">
              {language === 'es' ? currentStep.titleEs : currentStep.title}
            </h2>
            <span className="text-sm text-gray-500">
              Step {currentStepIndex + 1} of {ONBOARDING_STEPS.length}
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Step Content */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            {renderCurrentStep()}
          </div>

          {/* Navigation */}
          <div className="flex justify-between mt-6">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStepIndex === 0}
              className="flex items-center space-x-2"
            >
              <span>Previous</span>
            </Button>
            <Button
              onClick={nextStep}
              disabled={!canProceedToNextStep()}
              className="flex items-center space-x-2"
            >
              <span>Next</span>
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}