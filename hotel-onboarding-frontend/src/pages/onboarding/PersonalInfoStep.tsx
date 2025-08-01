import React, { useState, useEffect, useCallback } from 'react'
import PersonalInformationForm from '@/components/PersonalInformationForm'
import EmergencyContactsForm from '@/components/EmergencyContactsForm'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, User, Phone } from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { useAutoSave } from '@/hooks/useAutoSave'

export default function PersonalInfoStep({
  currentStep,
  progress,
  markStepComplete,
  saveProgress,
  language = 'en',
  employee,
  property
}: StepProps) {
  
  const [personalInfoData, setPersonalInfoData] = useState<any>({})
  const [emergencyContactsData, setEmergencyContactsData] = useState<any>({})
  const [personalInfoValid, setPersonalInfoValid] = useState(false)
  const [emergencyContactsValid, setEmergencyContactsValid] = useState(false)
  const [activeTab, setActiveTab] = useState('personal')
  const [dataLoaded, setDataLoaded] = useState(false)
  
  // Combine form data for saving
  const formData = {
    personalInfo: personalInfoData,
    emergencyContacts: emergencyContactsData,
    activeTab
  }

  // For this step, we rely on the form components' own validation
  // since they handle it internally
  const errors: string[] = []
  const fieldErrors: Record<string, string> = {}

  // Auto-save hook
  const { saveStatus } = useAutoSave(formData, {
    onSave: async (data) => {
      // First save to progress/controller
      await saveProgress(currentStep.id, data)
      // Store in session storage as backup
      sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify(data))
    }
  })

  // Load existing data on mount
  useEffect(() => {
    const loadExistingData = async () => {
      try {
        // Try to load from session storage first
        const savedData = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
        console.log('Loading saved data:', savedData)
        if (savedData) {
          const parsed = JSON.parse(savedData)
          console.log('Parsed data:', parsed)
          if (parsed.personalInfo) {
            setPersonalInfoData(parsed.personalInfo)
          }
          if (parsed.emergencyContacts) {
            setEmergencyContactsData(parsed.emergencyContacts)
          }
          if (parsed.activeTab) {
            setActiveTab(parsed.activeTab)
          }
        }
        
        // Check if step is already completed
        if (progress.completedSteps.includes(currentStep.id)) {
          setPersonalInfoValid(true)
          setEmergencyContactsValid(true)
        }
        
        setDataLoaded(true)
      } catch (error) {
        console.error('Failed to load existing data:', error)
        setDataLoaded(true)
      }
    }
    loadExistingData()
  }, [currentStep.id, progress.completedSteps])

  // Check completion status
  const isStepComplete = personalInfoValid && emergencyContactsValid

  // Auto-mark complete when both forms are valid
  useEffect(() => {
    if (isStepComplete && !progress.completedSteps.includes(currentStep.id)) {
      markStepComplete(currentStep.id, formData)
    }
  }, [isStepComplete, currentStep.id, formData, markStepComplete, progress.completedSteps])

  const handlePersonalInfoSave = useCallback((data: any) => {
    console.log('Saving personal info:', data)
    setPersonalInfoData(data)
    // Immediately save to session storage
    const updatedFormData = {
      personalInfo: data,
      emergencyContacts: emergencyContactsData,
      activeTab
    }
    sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify(updatedFormData))
  }, [emergencyContactsData, activeTab, currentStep.id])

  const handleEmergencyContactsSave = useCallback((data: any) => {
    console.log('Saving emergency contacts:', data)
    setEmergencyContactsData(data)
    // Immediately save to session storage
    const updatedFormData = {
      personalInfo: personalInfoData,
      emergencyContacts: data,
      activeTab
    }
    sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify(updatedFormData))
  }, [personalInfoData, activeTab, currentStep.id])

  const handlePersonalInfoValidationChange = useCallback((isValid: boolean) => {
    setPersonalInfoValid(isValid)
  }, [])

  const handleEmergencyContactsValidationChange = useCallback((isValid: boolean) => {
    setEmergencyContactsValid(isValid)
  }, [])

  const translations = {
    en: {
      title: 'Personal Information',
      description: 'Please provide your personal information and emergency contacts. This information will be kept confidential.',
      personalTab: 'Personal Details',
      emergencyTab: 'Emergency Contacts',
      sectionProgress: 'Section Progress',
      complete: 'Complete',
      required: 'Required',
      completionMessage: 'Personal information section completed successfully.'
    },
    es: {
      title: 'Información Personal',
      description: 'Por favor proporcione su información personal y contactos de emergencia. Esta información se mantendrá confidencial.',
      personalTab: 'Detalles Personales',
      emergencyTab: 'Contactos de Emergencia',
      sectionProgress: 'Progreso de la Sección',
      complete: 'Completo',
      required: 'Requerido',
      completionMessage: 'Sección de información personal completada exitosamente.'
    }
  }

  const t = translations[language]

  return (
    <StepContainer errors={errors} fieldErrors={fieldErrors} saveStatus={saveStatus}>
      <div className="space-y-6">
        {/* Step Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <User className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">{t.description}</p>
        </div>

        {/* Completion Alert */}
        {isStepComplete && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t.completionMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Tabbed Interface */}
        <Tabs value={activeTab} onValueChange={(value) => {
          setActiveTab(value)
          // Save tab state
          const updatedFormData = {
            personalInfo: personalInfoData,
            emergencyContacts: emergencyContactsData,
            activeTab: value
          }
          sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify(updatedFormData))
        }} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="personal" className="flex items-center space-x-2">
              <User className="h-4 w-4" />
              <span>{t.personalTab}</span>
              {personalInfoValid && <CheckCircle className="h-3 w-3 text-green-600" />}
            </TabsTrigger>
            <TabsTrigger value="emergency" className="flex items-center space-x-2">
              <Phone className="h-4 w-4" />
              <span>{t.emergencyTab}</span>
              {emergencyContactsValid && <CheckCircle className="h-3 w-3 text-green-600" />}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="personal" className="space-y-6">
            {dataLoaded && (
              <PersonalInformationForm
                key="personal-form"
                initialData={personalInfoData}
                language={language}
                onSave={handlePersonalInfoSave}
                onNext={() => setActiveTab('emergency')}
                onValidationChange={handlePersonalInfoValidationChange}
                useMainNavigation={true}
              />
            )}
          </TabsContent>

          <TabsContent value="emergency" className="space-y-6">
            {dataLoaded && (
              <EmergencyContactsForm
                key="emergency-form"
                initialData={emergencyContactsData}
                language={language}
                onSave={handleEmergencyContactsSave}
                onNext={() => {}} // Portal handles navigation
                onBack={() => setActiveTab('personal')}
                onValidationChange={handleEmergencyContactsValidationChange}
                useMainNavigation={true}
              />
            )}
          </TabsContent>
        </Tabs>

        {/* Progress Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-3">{t.sectionProgress}</h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{t.personalTab}</span>
              <div className="flex items-center space-x-2">
                {personalInfoValid ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
                )}
                <span className="text-sm font-medium">
                  {personalInfoValid ? t.complete : t.required}
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{t.emergencyTab}</span>
              <div className="flex items-center space-x-2">
                {emergencyContactsValid ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
                )}
                <span className="text-sm font-medium">
                  {emergencyContactsValid ? t.complete : t.required}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Debug section - temporary */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-4 p-4 bg-gray-100 rounded">
            <button 
              onClick={() => {
                const data = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
                console.log('Session storage data:', data)
                if (data) {
                  const parsed = JSON.parse(data)
                  console.log('Parsed data structure:', parsed)
                  console.log('Personal info valid:', personalInfoValid)
                  console.log('Emergency contacts valid:', emergencyContactsValid)
                  console.log('Is step complete:', isStepComplete)
                }
              }}
              className="bg-blue-500 text-white px-4 py-2 rounded text-sm mr-2"
            >
              Debug: Check Session Storage
            </button>
            <span className="text-sm text-gray-600">
              Personal: {personalInfoValid ? '✓' : '✗'} | 
              Emergency: {emergencyContactsValid ? '✓' : '✗'} | 
              Complete: {isStepComplete ? '✓' : '✗'}
            </span>
          </div>
        )}
      </div>
    </StepContainer>
  )
}