import React, { useState, useEffect } from 'react'
import I9Section1FormClean from '@/components/I9Section1FormClean'
import ReviewAndSign from '@/components/ReviewAndSign'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, FileText } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { useAutoSave } from '@/hooks/useAutoSave'
import { useStepValidation } from '@/hooks/useStepValidation'
import { i9Section1Validator } from '@/utils/stepValidators'

export default function I9Section1Step({
  currentStep,
  progress,
  markStepComplete,
  saveProgress,
  language = 'en',
  employee,
  property
}: StepProps) {
  
  const [formData, setFormData] = useState<any>({})
  const [activeTab, setActiveTab] = useState('form')
  const [formValid, setFormValid] = useState(false)
  const [isSigned, setIsSigned] = useState(false)

  // Validation hook
  const { errors, fieldErrors, validate } = useStepValidation(i9Section1Validator)

  // Auto-save data
  const autoSaveData = {
    formData,
    activeTab,
    formValid,
    isSigned
  }

  // Auto-save hook
  const { saveStatus } = useAutoSave(autoSaveData, {
    onSave: async (data) => {
    await saveProgress(currentStep.id, data)
    }
  })

  // Load existing data and auto-fill from personal info
  useEffect(() => {
    // Check if this step is already completed
    if (progress.completedSteps.includes(currentStep.id)) {
      setIsSigned(true)
      setFormValid(true)
      setActiveTab('review')
      
      // Load saved I9 data if exists
      const savedI9Data = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
      if (savedI9Data) {
        try {
          const parsed = JSON.parse(savedI9Data)
          if (parsed.formData) {
            setFormData(parsed.formData)
          }
        } catch (e) {
          console.error('Failed to parse saved I9 data:', e)
        }
      }
      return
    }
    
    // Try to auto-fill from personal info step data if not completed
    const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data')
    console.log('Personal info data from storage:', personalInfoData)
    
    if (personalInfoData) {
      try {
        const parsedData = JSON.parse(personalInfoData)
        console.log('Parsed personal info:', parsedData)
        const personalInfo = parsedData.personalInfo || parsedData || {}
        
        // Map personal info fields to I-9 fields
        const mappedData = {
          last_name: personalInfo.lastName || '',
          first_name: personalInfo.firstName || '',
          middle_initial: personalInfo.middleInitial || '',
          date_of_birth: personalInfo.dateOfBirth || '',
          ssn: personalInfo.ssn || '',
          email: personalInfo.email || '',
          phone: personalInfo.phone || '',
          address: personalInfo.address || '',
          apt_number: personalInfo.aptNumber || personalInfo.apartment || '',
          city: personalInfo.city || '',
          state: personalInfo.state || '',
          zip_code: personalInfo.zipCode || ''
        }
        
        console.log('Mapped I9 data:', mappedData)
        setFormData(mappedData)
      } catch (e) {
        console.error('Failed to parse personal info data:', e)
      }
    }
  }, [currentStep.id, progress.completedSteps])

  const handleFormComplete = async (data: any) => {
    console.log('Form completed with data:', data)
    
    // Save the form data
    setFormData(data)
    setFormValid(true)
    
    // Save to session storage
    await saveProgress(currentStep.id, { formData: data, formValid: true })
    
    // Switch to review tab
    setActiveTab('review')
  }

  const handleSign = async (signatureData: any) => {
    const completeData = {
      formData,
      signed: true,
      signatureData,
      completedAt: new Date().toISOString()
    }
    
    setIsSigned(true)
    await markStepComplete(currentStep.id, completeData)
  }

  const renderFormPreview = (data: any) => {
    if (!data || Object.keys(data).length === 0) return <div>No form data available</div>
    
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-600">Last Name</label>
            <p className="text-gray-900">{data.last_name || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">First Name</label>
            <p className="text-gray-900">{data.first_name || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Middle Initial</label>
            <p className="text-gray-900">{data.middle_initial || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Date of Birth</label>
            <p className="text-gray-900">{data.date_of_birth || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Social Security Number</label>
            <p className="text-gray-900">{data.ssn ? '***-**-' + data.ssn.slice(-4) : 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Employee Address</label>
            <p className="text-gray-900">{data.address || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Citizenship Status</label>
            <p className="text-gray-900">{data.citizenship_status || 'Not provided'}</p>
          </div>
        </div>
      </div>
    )
  }

  const translations = {
    en: {
      title: 'Employment Eligibility Verification',
      description: 'Complete Form I-9 Section 1 to verify your eligibility to work in the United States',
      completionMessage: 'Form I-9 Section 1 has been completed and digitally signed.',
      fillFormTab: 'Fill Form',
      reviewTab: 'Preview & Sign',
      reviewTitle: 'Review I-9 Section 1',
      reviewDescription: 'Please review your employment eligibility information and sign electronically',
      agreementText: 'I attest, under penalty of perjury, that I am (check one of the following boxes):'
    },
    es: {
      title: 'Verificación de Elegibilidad de Empleo',
      description: 'Complete el Formulario I-9 Sección 1 para verificar su elegibilidad para trabajar en los Estados Unidos',
      completionMessage: 'El Formulario I-9 Sección 1 ha sido completado y firmado digitalmente.',
      fillFormTab: 'Llenar Formulario',
      reviewTab: 'Revisar y Firmar',
      reviewTitle: 'Revisar I-9 Sección 1',
      reviewDescription: 'Por favor revise su información de elegibilidad de empleo y firme electrónicamente',
      agreementText: 'Atestiguo, bajo pena de perjurio, que soy (marque una de las siguientes casillas):'
    }
  }

  const t = translations[language]

  return (
    <StepContainer errors={errors} fieldErrors={fieldErrors} saveStatus={saveStatus}>
      <div className="space-y-6">
        {/* Step Header */}
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          <p className="text-gray-600 mt-2">{t.description}</p>
        </div>

        {/* Completion Status */}
        {isSigned && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t.completionMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Tabbed Interface */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="form" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>{t.fillFormTab}</span>
              {formValid && <CheckCircle className="h-3 w-3 text-green-600" />}
            </TabsTrigger>
            <TabsTrigger value="review" disabled={!formValid} className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4" />
              <span>{t.reviewTab}</span>
              {isSigned && <CheckCircle className="h-3 w-3 text-green-600" />}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="form" className="space-y-6">
            <I9Section1FormClean
              onComplete={handleFormComplete}
              initialData={formData}
              language={language}
              employeeId={employee?.id}
            />
          </TabsContent>

          <TabsContent value="review" className="space-y-6">
            {formData && (
              <ReviewAndSign
                formType="i9-section1"
                formData={formData}
                title={t.reviewTitle}
                description={t.reviewDescription}
                language={language}
                onSign={handleSign}
                onBack={() => setActiveTab('form')}
                renderPreview={renderFormPreview}
                usePDFPreview={true}
                pdfEndpoint={`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/api/onboarding/${employee?.id}/i9-section1/generate-pdf`}
                federalCompliance={{
                  formName: 'Form I-9, Employment Eligibility Verification',
                  retentionPeriod: '3 years after hire or 1 year after termination (whichever is later)',
                  requiresWitness: false
                }}
                agreementText={t.agreementText}
              />
            )}
          </TabsContent>
        </Tabs>
      </div>
    </StepContainer>
  )
}