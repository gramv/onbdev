import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import HealthInsuranceForm from '@/components/HealthInsuranceForm'
import ReviewAndSign from '@/components/ReviewAndSign'
import { CheckCircle, Heart, Users, AlertTriangle } from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { useAutoSave } from '@/hooks/useAutoSave'
import { useStepValidation } from '@/hooks/useStepValidation'
import { healthInsuranceValidator } from '@/utils/stepValidators'

export default function HealthInsuranceStep({
  currentStep,
  progress,
  markStepComplete,
  saveProgress,
  language = 'en',
  employee,
  property
}: StepProps) {
  
  const [formData, setFormData] = useState<any>({})
  const [isValid, setIsValid] = useState(false)
  const [showReview, setShowReview] = useState(false)
  const [isSigned, setIsSigned] = useState(false)

  // Validation hook
  const { errors, fieldErrors, validate } = useStepValidation(healthInsuranceValidator)

  // Auto-save data
  const autoSaveData = {
    formData,
    isValid,
    showReview,
    isSigned
  }

  // Auto-save hook
  const { saveStatus } = useAutoSave(autoSaveData, {
    onSave: async (data) => {
      await saveProgress(currentStep.id, data)
    }
  })

  // Load existing data
  useEffect(() => {
    if (progress.completedSteps.includes(currentStep.id)) {
      setIsSigned(true)
      setIsValid(true)
    }
  }, [currentStep.id, progress.completedSteps])

  const handleFormSave = async (data: any) => {
    // Validate the form data
    const validation = await validate(data)
    
    if (validation.valid) {
      setFormData(data)
      setIsValid(true)
      setShowReview(true)
    }
  }

  const handleBackFromReview = () => {
    setShowReview(false)
  }

  const handleDigitalSignature = async (signatureData: any) => {
    setIsSigned(true)
    
    const completeData = {
      formData,
      signed: true,
      signatureData,
      completedAt: new Date().toISOString()
    }
    
    await markStepComplete(currentStep.id, completeData)
    setShowReview(false)
  }

  const isStepComplete = isValid && isSigned

  const translations = {
    en: {
      title: 'Health Insurance Enrollment',
      reviewTitle: 'Review Health Insurance',
      description: 'Choose your health insurance plan and add dependents if applicable. Your coverage will begin according to your plan\'s effective date.',
      enrollmentPeriod: 'Enrollment Period:',
      enrollmentNotice: 'You have 30 days from your hire date to enroll in health insurance or make changes to your coverage.',
      completionMessage: 'Health insurance enrollment completed successfully.',
      planSelectionTitle: 'Health Insurance Plan Selection',
      estimatedTime: 'Estimated time: 6-8 minutes',
      reviewDescription: 'Please review your health insurance selections and dependent information',
      acknowledgments: {
        planSelection: 'I have reviewed and selected the appropriate health insurance plan',
        dependentInfo: 'All dependent information provided is accurate and complete',
        coverage: 'I understand when my coverage will begin',
        changes: 'I understand I can make changes during open enrollment or qualifying life events'
      }
    },
    es: {
      title: 'Inscripción en Seguro de Salud',
      reviewTitle: 'Revisar Seguro de Salud',
      description: 'Elija su plan de seguro de salud y agregue dependientes si corresponde. Su cobertura comenzará según la fecha de vigencia de su plan.',
      enrollmentPeriod: 'Período de Inscripción:',
      enrollmentNotice: 'Tiene 30 días desde su fecha de contratación para inscribirse en el seguro de salud o hacer cambios en su cobertura.',
      completionMessage: 'Inscripción en seguro de salud completada exitosamente.',
      planSelectionTitle: 'Selección de Plan de Seguro de Salud',
      estimatedTime: 'Tiempo estimado: 6-8 minutos',
      reviewDescription: 'Por favor revise sus selecciones de seguro de salud e información de dependientes',
      acknowledgments: {
        planSelection: 'He revisado y seleccionado el plan de seguro de salud apropiado',
        dependentInfo: 'Toda la información de dependientes proporcionada es precisa y completa',
        coverage: 'Entiendo cuándo comenzará mi cobertura',
        changes: 'Entiendo que puedo hacer cambios durante la inscripción abierta o eventos de vida calificados'
      }
    }
  }

  const t = translations[language]

  // Show review and sign if form is valid and review is requested
  if (showReview && formData) {
    return (
      <StepContainer errors={errors} saveStatus={saveStatus}>
        <div className="space-y-6">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Heart className="h-6 w-6 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">{t.reviewTitle}</h1>
            </div>
          </div>
          
          <ReviewAndSign
            formType="health_insurance"
            formTitle="Health Insurance Enrollment Form"
            formData={formData}
            documentName="Health Insurance Enrollment"
            signerName={employee?.firstName + ' ' + employee?.lastName || 'Employee'}
            signerTitle={employee?.position}
            onSign={handleDigitalSignature}
            onEdit={handleBackFromReview}
            acknowledgments={[
              t.acknowledgments.planSelection,
              t.acknowledgments.dependentInfo,
              t.acknowledgments.coverage,
              t.acknowledgments.changes
            ]}
            language={language}
            description={t.reviewDescription}
          />
        </div>
      </StepContainer>
    )
  }

  return (
    <StepContainer errors={errors} fieldErrors={fieldErrors} saveStatus={saveStatus}>
      <div className="space-y-6">
        {/* Step Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Heart className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          </div>
          <p className="text-gray-600 max-w-3xl mx-auto">{t.description}</p>
        </div>

        {/* Enrollment Period Notice */}
        <Alert className="bg-blue-50 border-blue-200">
          <Heart className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">
            <strong>{t.enrollmentPeriod}</strong> {t.enrollmentNotice}
          </AlertDescription>
        </Alert>

        {/* Completion Status */}
        {isStepComplete && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t.completionMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Health Insurance Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5 text-blue-600" />
              <span>{t.planSelectionTitle}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <HealthInsuranceForm
              initialData={formData}
              language={language}
              onSave={handleFormSave}
              onValidationChange={(valid: boolean, errors: Record<string, string>) => {
                setIsValid(valid)
              }}
            />
          </CardContent>
        </Card>

        {/* Time Estimate */}
        <div className="text-center text-sm text-gray-500">
          <p>{t.estimatedTime}</p>
        </div>
      </div>
    </StepContainer>
  )
}