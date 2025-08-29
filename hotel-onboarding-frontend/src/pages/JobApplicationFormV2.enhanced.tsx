import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { 
  ChevronLeft, 
  ChevronRight, 
  CheckCircle2, 
  AlertCircle,
  Save,
  Phone,
  MapPin,
  Info,
  Building2,
  Send,
  PartyPopper,
  Globe,
  User,
  Briefcase,
  GraduationCap,
  FileText,
  Users,
  Clock,
  RefreshCw,
  Loader2,
  CheckCircle,
  Circle,
  ArrowLeft,
  ArrowRight
} from 'lucide-react'
import { apiClient } from '@/services/api'
import { toast } from 'sonner'

// Import step components
import PersonalInformationStep from '@/components/job-application/PersonalInformationStep.enhanced'
import PositionAvailabilityStep from '@/components/job-application/PositionAvailabilityStep'
import EmploymentHistoryStep from '@/components/job-application/EmploymentHistoryStep'
import EducationSkillsStep from '@/components/job-application/EducationSkillsStep'
import AdditionalInformationStep from '@/components/job-application/AdditionalInformationStep'
import VoluntarySelfIdentificationStep from '@/components/job-application/VoluntarySelfIdentificationStep'
import ReviewConsentStep from '@/components/job-application/ReviewConsentStep'

interface Property {
  id: string
  name: string
  address: string
  city: string
  state: string
  zip_code: string
  phone: string
}

interface PropertyInfo {
  property: Property
  departments_and_positions: Record<string, string[]>
  application_url: string
  is_accepting_applications: boolean
}

interface StepConfig {
  id: string
  title: string
  description: string
  component: React.ComponentType<any>
  required: boolean
  icon: React.ElementType
}

interface SavedApplication {
  applicationId: string
  propertyId: string
  formData: any
  currentStep: number
  stepCompletionStatus: Record<string, boolean>
  lastSaved: string
  version: number
}

const CURRENT_VERSION = 1
const AUTO_SAVE_INTERVAL = 30000 // 30 seconds

const getSteps = (t: any): StepConfig[] => [
  {
    id: 'personal-info',
    title: t('jobApplication.steps.personalInfo.title'),
    description: t('jobApplication.steps.personalInfo.description'),
    component: PersonalInformationStep,
    required: true,
    icon: User
  },
  {
    id: 'position-availability',
    title: t('jobApplication.steps.positionAvailability.title'),
    description: t('jobApplication.steps.positionAvailability.description'),
    component: PositionAvailabilityStep,
    required: true,
    icon: Briefcase
  },
  {
    id: 'employment-history',
    title: t('jobApplication.steps.employmentHistory.title'),
    description: t('jobApplication.steps.employmentHistory.description'),
    component: EmploymentHistoryStep,
    required: true,
    icon: Building2
  },
  {
    id: 'education-skills',
    title: t('jobApplication.steps.education.title'),
    description: t('jobApplication.steps.education.description'),
    component: EducationSkillsStep,
    required: true,
    icon: GraduationCap
  },
  {
    id: 'additional-info',
    title: t('jobApplication.steps.additionalInfo.title'),
    description: t('jobApplication.steps.additionalInfo.description'),
    component: AdditionalInformationStep,
    required: true,
    icon: FileText
  },
  {
    id: 'review-consent',
    title: t('jobApplication.steps.reviewConsent.title'),
    description: t('jobApplication.steps.reviewConsent.description'),
    component: ReviewConsentStep,
    required: true,
    icon: CheckCircle2
  },
  {
    id: 'voluntary-self-identification',
    title: t('jobApplication.steps.voluntarySelfIdentification.title'),
    description: t('jobApplication.steps.voluntarySelfIdentification.description'),
    component: VoluntarySelfIdentificationStep,
    required: false,
    icon: Users
  }
]

export default function JobApplicationFormV2() {
  const { propertyId } = useParams<{ propertyId: string }>()
  const navigate = useNavigate()
  const { t, i18n } = useTranslation()
  
  const [propertyInfo, setPropertyInfo] = useState<PropertyInfo | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [stepCompletionStatus, setStepCompletionStatus] = useState<Record<string, boolean>>({})
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [autoSaving, setAutoSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [applicationSubmitted, setApplicationSubmitted] = useState(false)
  const [showEqualOpportunityModal, setShowEqualOpportunityModal] = useState(false)
  const [showRecoveryModal, setShowRecoveryModal] = useState(false)
  const [savedApplication, setSavedApplication] = useState<SavedApplication | null>(null)
  const [applicationId, setApplicationId] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null)
  const steps = useMemo(() => getSteps(t), [t])

  // Initialize formData with proper structure
  const [formData, setFormData] = useState<any>({
    // Personal Information
    first_name: '',
    middle_name: '',
    last_name: '',
    email: '',
    phone: '',
    phone_is_cell: false,
    phone_is_home: false,
    alternate_phone: '',
    alternate_phone_is_cell: false,
    alternate_phone_is_home: false,
    address: '',
    apartment_unit: '',
    city: '',
    state: '',
    zip_code: '',
    age_verification: false,
    work_authorized: '',
    sponsorship_required: '',
    reliable_transportation: '',
    transportation_method: '',
    transportation_other: '',
    
    // Position & Availability
    position_applying_for: '',
    position: '',
    department: '',
    salary_desired: '',
    how_heard_about_us: '',
    referral_source: '',
    referral_details: '',
    desired_salary: '',
    start_date: '',
    shift_preference: '',
    schedule_preference: '',
    available_weekends: '',
    available_holidays: '',
    hours_per_week: '',
    employment_type: '',
    seasonal_start_date: '',
    seasonal_end_date: '',
    
    // Previous Hotel Employment
    previous_hotel_employment: '',
    previous_hotel_details: '',
    
    // Employment History
    employment_history: Array(3).fill({
      employer_name: '',
      employer_address: '',
      job_title: '',
      start_date: '',
      end_date: '',
      is_current: false,
      starting_salary: '',
      ending_salary: '',
      reason_for_leaving: '',
      responsibilities: '',
      supervisor_name: '',
      supervisor_phone: '',
      may_contact: false
    }),
    
    // Education & Skills
    highest_education: '',
    school_name: '',
    school_location: '',
    years_attended: '',
    graduated: '',
    degree_obtained: '',
    graduation_year: '',
    skills: '',
    certifications: '',
    languages_spoken: '',
    
    // Military Service
    military_branch: '',
    military_from_date: '',
    military_to_date: '',
    military_rank: '',
    military_discharge_type: '',
    military_disabilities: '',
    
    // Additional Information
    professional_references: Array(3).fill({
      name: '',
      relationship: '',
      phone: '',
      email: '',
      years_known: ''
    }),
    has_criminal_record: '',
    criminal_record_explanation: '',
    additional_comments: '',
    
    // Experience
    experience_years: '',
    hotel_experience: '',
    
    // Voluntary Self-Identification
    gender: '',
    ethnicity: '',
    veteran_status: '',
    disability_status: '',
    decline_to_identify: false,
    race_hispanic_latino: false,
    race_white: false,
    race_black_african_american: false,
    race_native_hawaiian_pacific_islander: false,
    race_asian: false,
    race_american_indian_alaska_native: false,
    race_two_or_more: false,
    referral_source_voluntary: '',
    
    // Consent & Signature
    physical_requirements_acknowledged: false,
    background_check_consent: false,
    information_accuracy_certified: false,
    at_will_employment_acknowledged: false,
    signature: '',
    signature_date: '',
    initials_truthfulness: '',
    initials_at_will: '',
    initials_screening: ''
  })

  // Generate unique application ID
  useEffect(() => {
    if (!applicationId) {
      const id = `APP-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      setApplicationId(id)
    }
  }, [])

  // Load property information and check for saved application
  useEffect(() => {
    const init = async () => {
      setLoading(true)
      await fetchProperty()
      checkForSavedApplication()
      setLoading(false)
    }
    init()
  }, [propertyId])

  // Auto-save timer
  useEffect(() => {
    if (autoSaveTimerRef.current) {
      clearInterval(autoSaveTimerRef.current)
    }

    autoSaveTimerRef.current = setInterval(() => {
      autoSave()
    }, AUTO_SAVE_INTERVAL)

    return () => {
      if (autoSaveTimerRef.current) {
        clearInterval(autoSaveTimerRef.current)
      }
    }
  }, [formData, currentStep, stepCompletionStatus])

  // Check for equal opportunity acknowledgment
  useEffect(() => {
    const timer = setTimeout(() => {
      const storageKey = `eeo-acknowledged-${propertyId}`
      const hasAcknowledged = sessionStorage.getItem(storageKey)
      const hasSavedData = savedApplication !== null
      
      if (!hasAcknowledged && !hasSavedData && !loading) {
        setShowEqualOpportunityModal(true)
      }
    }, 500)
    
    return () => clearTimeout(timer)
  }, [propertyId, savedApplication, loading])

  const fetchProperty = async () => {
    try {
      const response = await apiClient.get(`/properties/${propertyId}/info`)
      setPropertyInfo(response.data)
      setFormData(prev => ({
        ...prev,
        property_name: response.data.property.name
      }))
    } catch (error) {
      console.error('Failed to fetch property:', error)
      setError('Failed to load property information. Please try again.')
    }
  }

  const checkForSavedApplication = () => {
    const draftKey = `job-application-draft-${propertyId}`
    const savedDraft = localStorage.getItem(draftKey)
    
    if (savedDraft) {
      try {
        const parsedDraft: SavedApplication = JSON.parse(savedDraft)
        
        // Check if draft is not too old (7 days)
        const savedDate = new Date(parsedDraft.lastSaved)
        const daysSinceSaved = (Date.now() - savedDate.getTime()) / (1000 * 60 * 60 * 24)
        
        if (daysSinceSaved <= 7) {
          setSavedApplication(parsedDraft)
          setShowRecoveryModal(true)
        } else {
          // Clear old draft
          localStorage.removeItem(draftKey)
        }
      } catch (e) {
        console.error('Failed to parse saved draft:', e)
        localStorage.removeItem(draftKey)
      }
    }
  }

  const recoverApplication = () => {
    if (savedApplication) {
      setFormData(savedApplication.formData)
      setCurrentStep(savedApplication.currentStep || 0)
      setStepCompletionStatus(savedApplication.stepCompletionStatus || {})
      setApplicationId(savedApplication.applicationId)
      setLastSaved(new Date(savedApplication.lastSaved))
      setShowRecoveryModal(false)
      toast.success('Application recovered successfully!')
    }
  }

  const startFreshApplication = () => {
    const draftKey = `job-application-draft-${propertyId}`
    localStorage.removeItem(draftKey)
    setSavedApplication(null)
    setShowRecoveryModal(false)
  }

  const autoSave = async () => {
    if (!formData.first_name && !formData.email) {
      // Don't auto-save if no data entered yet
      return
    }

    setAutoSaving(true)
    try {
      const draftKey = `job-application-draft-${propertyId}`
      const draftData: SavedApplication = {
        applicationId,
        propertyId: propertyId || '',
        formData,
        currentStep,
        stepCompletionStatus,
        lastSaved: new Date().toISOString(),
        version: CURRENT_VERSION
      }
      
      localStorage.setItem(draftKey, JSON.stringify(draftData))
      setLastSaved(new Date())
    } catch (error) {
      console.error('Failed to auto-save:', error)
    } finally {
      setAutoSaving(false)
    }
  }

  const saveDraft = async () => {
    setSaving(true)
    try {
      await autoSave()
      toast.success(`Application saved! Recovery ID: ${applicationId}`)
    } catch (error) {
      console.error('Failed to save draft:', error)
      toast.error('Failed to save application')
    } finally {
      setSaving(false)
    }
  }

  const updateFormData = (stepData: any) => {
    setFormData(prev => ({ ...prev, ...stepData }))
  }

  const markStepComplete = useCallback((stepId: string, isComplete: boolean = true) => {
    setStepCompletionStatus(prev => ({ ...prev, [stepId]: isComplete }))
  }, [])

  const handleStepComplete = useCallback((isComplete: boolean) => {
    markStepComplete(steps[currentStep].id, isComplete)
  }, [currentStep, markStepComplete, steps])

  const calculateProgress = () => {
    const totalSteps = steps.filter(s => s.required).length
    const completedSteps = steps.filter(s => s.required && stepCompletionStatus[s.id]).length
    return Math.round((completedSteps / totalSteps) * 100)
  }

  const handleNext = () => {
    setError('')
    
    const currentStepId = steps[currentStep].id
    const isStepComplete = stepCompletionStatus[currentStepId]
    
    if (!isStepComplete && steps[currentStep].required) {
      setError(`Please complete all required fields in "${steps[currentStep].title}" before proceeding.`)
      
      // Auto-scroll to first error field if exists
      setTimeout(() => {
        const firstError = document.querySelector('[aria-invalid="true"]')
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' })
          ;(firstError as HTMLElement).focus()
        }
      }, 100)
      
      return
    }
    
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
      autoSave()
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const handleStepClick = (index: number) => {
    // Allow navigation to previous steps or completed steps
    if (index < currentStep || stepCompletionStatus[steps[index].id]) {
      setCurrentStep(index)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  const compileApplicationData = (): any => {
    // Compile all data from formData state which has been updated by each step
    
    // Extract middle initial from middle_name if it exists
    const middleInitial = formData.middle_name ? (formData.middle_name as string).charAt(0).toUpperCase() : null
    
    // Parse conviction record - map from actual field names used in AdditionalInformationStep
    const convictionRecord = {
      has_conviction: formData.has_conviction === 'yes',
      explanation: formData.has_conviction === 'yes' ? (formData.conviction_explanation || null) : null
    }
    
    // Parse personal reference - map from actual field names used in AdditionalInformationStep
    const personalReference = {
      name: formData.reference_name || formData.professional_references?.[0]?.name || '',
      relationship: formData.reference_relationship || formData.professional_references?.[0]?.relationship || '',
      phone: formData.reference_phone || formData.professional_references?.[0]?.phone || '',
      email: formData.reference_email || formData.professional_references?.[0]?.email || ''
    }
    
    // Parse military service
    const militaryService = {
      served: formData.military_service === 'yes' || (formData.military_branch ? true : false),
      branch: formData.military_branch || null,
      from_date: formData.military_from_date || null,
      to_date: formData.military_to_date || null,
      rank_at_discharge: formData.military_rank || null,
      type_of_discharge: formData.military_discharge_type || null,
      disabilities_related: formData.military_disabilities || null
    }
    
    // Parse education history
    const educationHistory = []
    if (formData.school_name) {
      educationHistory.push({
        school_name: formData.school_name,
        location: formData.school_location || '',
        years_attended: formData.years_attended || formData.graduation_year || '',
        graduated: formData.graduated === 'yes' || formData.highest_education?.includes('degree'),
        degree_received: formData.degree_obtained || null
      })
    }
    
    // Parse employment history
    const employmentHistory = (formData.employment_history || []).filter((emp: any) => 
      emp.employer_name && emp.employer_name.trim() !== ''
    ).map((emp: any) => ({
      company_name: emp.employer_name || '',
      phone: emp.supervisor_phone || '',
      address: emp.employer_address || '',
      supervisor: emp.supervisor_name || '',
      job_title: emp.job_title || '',
      starting_salary: emp.starting_salary || '',
      ending_salary: emp.ending_salary || '',
      from_date: emp.start_date || '',
      to_date: emp.end_date || (emp.is_current ? 'Present' : ''),
      reason_for_leaving: emp.reason_for_leaving || '',
      may_contact: emp.may_contact || false
    }))
    
    // Parse voluntary self-identification
    const voluntarySelfIdentification = {
      gender: formData.gender || null,
      race_ethnicity: formData.ethnicity || null,
      veteran_status: formData.veteran_status || null,
      disability_status: formData.disability_status || null
    }
    
    // Build complete application data matching backend model
    const applicationData = {
      // Personal Information
      first_name: formData.first_name,
      middle_initial: middleInitial,
      last_name: formData.last_name,
      email: formData.email,
      phone: formData.phone,
      phone_is_cell: formData.phone_is_cell || false,
      phone_is_home: formData.phone_is_home || false,
      secondary_phone: formData.alternate_phone || null,
      secondary_phone_is_cell: formData.alternate_phone_is_cell || false,
      secondary_phone_is_home: formData.alternate_phone_is_home || false,
      address: formData.address,
      apartment_unit: formData.apartment_unit || null,
      city: formData.city,
      state: formData.state,
      zip_code: formData.zip_code,
      
      // Position Information
      department: formData.department || '',
      position: formData.position_applying_for || formData.position || '',
      salary_desired: formData.salary_desired || formData.desired_salary || null,
      
      // Work Authorization & Legal
      work_authorized: formData.work_authorized,
      sponsorship_required: formData.sponsorship_required,
      age_verification: formData.age_verification || false,
      conviction_record: convictionRecord,
      
      // Availability
      start_date: formData.start_date || new Date().toISOString().split('T')[0],
      shift_preference: formData.shift_preference || formData.schedule_preference || 'flexible',
      employment_type: formData.employment_type || 'full_time',
      seasonal_start_date: formData.seasonal_start_date || null,
      seasonal_end_date: formData.seasonal_end_date || null,
      
      // Previous Hotel Employment
      previous_hotel_employment: formData.previous_hotel_employment === 'yes' || false,
      previous_hotel_details: formData.previous_hotel_details || null,
      
      // How did you hear about us?
      how_heard: formData.how_heard_about_us || formData.referral_source_voluntary || '',
      how_heard_detailed: formData.referral_source || formData.referral_details || null,
      
      // References
      personal_reference: personalReference,
      
      // Military Service
      military_service: militaryService,
      
      // Education History
      education_history: educationHistory,
      
      // Employment History
      employment_history: employmentHistory,
      
      // Skills, Languages, and Certifications
      skills_languages_certifications: [
        formData.skills,
        formData.languages_spoken,
        formData.certifications
      ].filter(Boolean).join('; ') || null,
      
      // Voluntary Self-Identification
      voluntary_self_identification: voluntarySelfIdentification,
      
      // Experience
      experience_years: formData.experience_years || '0-1',
      hotel_experience: formData.hotel_experience || 'no',
      
      // Additional Information
      additional_comments: formData.additional_comments || ''
    }
    
    return applicationData
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    setError('')

    try {
      // Compile all application data
      const compiledData = compileApplicationData()
      
      // Add signature data if present
      if ((formData as any).signature) {
        (compiledData as any).signature = (formData as any).signature
      }
      if ((formData as any).signature_date) {
        (compiledData as any).signature_date = (formData as any).signature_date
      }
      if ((formData as any).initials_truthfulness) {
        (compiledData as any).initials_truthfulness = (formData as any).initials_truthfulness
      }
      if ((formData as any).initials_at_will) {
        (compiledData as any).initials_at_will = (formData as any).initials_at_will
      }
      if ((formData as any).initials_screening) {
        (compiledData as any).initials_screening = (formData as any).initials_screening
      }
      
      console.log('Submitting application data:', compiledData)
      
      // Submit to backend - note the endpoint expects property ID in URL
      const response = await apiClient.post(`/apply/${propertyId}`, compiledData)

      if (response.data.success || response.data.application_id) {
        setApplicationSubmitted(true)
        
        // Clear saved draft
        const draftKey = `job-application-draft-${propertyId}`
        localStorage.removeItem(draftKey)
        
        // Show success message
        toast.success('Application submitted successfully!')
      }
    } catch (err: any) {
      console.error('Submission error:', err)
      setError(err.response?.data?.detail || err.response?.data?.error || 'Failed to submit application. Please try again.')
      
      // Log validation errors if present
      if (err.response?.data?.detail && typeof err.response.data.detail === 'object') {
        console.error('Validation errors:', err.response.data.detail)
      }
      
      // If network error, retry with exponential backoff
      if (err.code === 'ERR_NETWORK') {
        setTimeout(() => handleSubmit(), 2000)
      }
    } finally {
      setSubmitting(false)
    }
  }

  const CurrentStepComponent = steps[currentStep].component
  const StepIcon = steps[currentStep].icon

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <div className="max-w-4xl mx-auto space-y-6">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-20 w-full" />
          <div className="space-y-4">
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
        </div>
      </div>
    )
  }

  // Success state
  if (applicationSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <PartyPopper className="h-16 w-16 mx-auto text-green-500 mb-4" />
            <CardTitle className="text-2xl">Application Submitted!</CardTitle>
            <CardDescription>
              Thank you for applying to {propertyInfo?.property.name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>
                Your application ID: <strong>{applicationId}</strong>
                <br />
                Please save this ID for future reference.
              </AlertDescription>
            </Alert>
            <p className="text-center text-sm text-gray-600">
              We'll review your application and contact you soon at the email address you provided.
            </p>
            <Button 
              onClick={() => navigate('/')} 
              className="w-full"
            >
              Return to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Progress Bar - Sticky on mobile */}
      <div className="sticky top-0 z-20 bg-white dark:bg-gray-900 shadow-sm">
        <div className="max-w-4xl mx-auto p-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Application Progress</h2>
              <span className="text-sm text-gray-500">{calculateProgress()}% Complete</span>
            </div>
            <Progress value={calculateProgress()} className="h-3" />
            
            {/* Step Indicators - Horizontal scroll on mobile */}
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {steps.map((step, index) => (
                <button
                  key={step.id}
                  onClick={() => handleStepClick(index)}
                  className={`
                    flex items-center gap-2 px-3 py-2 rounded-lg whitespace-nowrap text-sm
                    transition-all duration-200 min-w-fit
                    ${index === currentStep 
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 font-medium' 
                      : stepCompletionStatus[step.id]
                      ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 cursor-pointer hover:bg-green-200'
                      : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                    }
                    ${index < currentStep && !stepCompletionStatus[step.id] && 'cursor-pointer hover:bg-gray-200'}
                  `}
                  disabled={index > currentStep && !stepCompletionStatus[step.id]}
                >
                  {stepCompletionStatus[step.id] ? (
                    <CheckCircle className="h-4 w-4 flex-shrink-0" />
                  ) : index === currentStep ? (
                    <Circle className="h-4 w-4 flex-shrink-0 fill-current" />
                  ) : (
                    <Circle className="h-4 w-4 flex-shrink-0" />
                  )}
                  <span className="hidden sm:inline">{step.title}</span>
                  <span className="sm:hidden">{index + 1}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto p-4 pb-24 md:pb-8">
        {/* Property Header */}
        {propertyInfo && (
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Building2 className="h-6 w-6" />
                    {propertyInfo.property.name}
                  </CardTitle>
                  <CardDescription className="mt-2 space-y-1">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      {propertyInfo.property.address}, {propertyInfo.property.city}, {propertyInfo.property.state} {propertyInfo.property.zip_code}
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4" />
                      {propertyInfo.property.phone}
                    </div>
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => i18n.changeLanguage(i18n.language === 'en' ? 'es' : 'en')}
                  >
                    <Globe className="h-4 w-4 mr-1" />
                    {i18n.language === 'en' ? 'ES' : 'EN'}
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>
        )}

        {/* Auto-save indicator */}
        {lastSaved && (
          <div className="mb-4 flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-2">
              {autoSaving ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span>Saved {new Date(lastSaved).toLocaleTimeString()}</span>
                </>
              )}
            </div>
            <div className="text-xs">
              Application ID: <code className="bg-gray-100 px-1 py-0.5 rounded">{applicationId}</code>
            </div>
          </div>
        )}

        {/* Current Step */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <StepIcon className="h-5 w-5" />
              {steps[currentStep].title}
            </CardTitle>
            <CardDescription>{steps[currentStep].description}</CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <CurrentStepComponent
              formData={formData}
              updateFormData={updateFormData}
              validationErrors={validationErrors}
              onComplete={handleStepComplete}
            />
          </CardContent>
        </Card>
      </div>

      {/* Navigation - Fixed on mobile */}
      <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t p-4 md:relative md:border-0 md:bg-transparent md:dark:bg-transparent">
        <div className="max-w-4xl mx-auto flex items-center justify-between gap-2">
          <Button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            variant="outline"
            className="flex-1 md:flex-none"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            <span className="hidden sm:inline">Previous</span>
            <span className="sm:hidden">Back</span>
          </Button>

          <Button
            onClick={saveDraft}
            disabled={saving || !formData.first_name}
            variant="outline"
            className="flex-1 md:flex-none"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            <span className="hidden sm:inline">Save & Continue Later</span>
            <span className="sm:hidden">Save</span>
          </Button>

          {currentStep === steps.length - 1 ? (
            <Button
              onClick={handleSubmit}
              disabled={submitting || !stepCompletionStatus[steps[currentStep].id]}
              className="flex-1 md:flex-none"
            >
              {submitting ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Send className="h-4 w-4 mr-2" />
              )}
              <span className="hidden sm:inline">Submit Application</span>
              <span className="sm:hidden">Submit</span>
            </Button>
          ) : (
            <Button
              onClick={handleNext}
              className="flex-1 md:flex-none"
            >
              <span className="hidden sm:inline">Next</span>
              <span className="sm:hidden">Next</span>
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      </div>

      {/* Recovery Modal */}
      <Dialog open={showRecoveryModal} onOpenChange={setShowRecoveryModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <RefreshCw className="h-5 w-5" />
              Resume Previous Application?
            </DialogTitle>
            <DialogDescription>
              We found a saved application from {savedApplication && new Date(savedApplication.lastSaved).toLocaleDateString()}.
              Would you like to continue where you left off?
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Application ID: <strong>{savedApplication?.applicationId}</strong>
                <br />
                Last saved: {savedApplication && new Date(savedApplication.lastSaved).toLocaleString()}
              </AlertDescription>
            </Alert>
          </div>
          <DialogFooter className="flex-col sm:flex-row gap-2">
            <Button variant="outline" onClick={startFreshApplication}>
              Start Fresh
            </Button>
            <Button onClick={recoverApplication}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Continue Application
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Equal Opportunity Modal */}
      <Dialog open={showEqualOpportunityModal} onOpenChange={setShowEqualOpportunityModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Equal Employment Opportunity</DialogTitle>
            <DialogDescription>
              {propertyInfo?.property.name} is an Equal Opportunity Employer
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 text-sm">
            <p>
              We are committed to providing equal employment opportunities to all employees and applicants 
              without regard to race, color, religion, sex, national origin, age, disability, or genetics.
            </p>
            <p>
              In addition to federal law requirements, we comply with applicable state and local laws 
              governing nondiscrimination in employment in every location in which the company has facilities.
            </p>
            <p>
              This policy applies to all terms and conditions of employment, including recruiting, hiring, 
              placement, promotion, termination, layoff, recall, transfer, leaves of absence, compensation, 
              and training.
            </p>
          </div>
          <DialogFooter>
            <Button 
              onClick={() => {
                setShowEqualOpportunityModal(false)
                sessionStorage.setItem(`eeo-acknowledged-${propertyId}`, 'true')
              }}
            >
              I Understand
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}