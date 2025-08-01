import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import DirectDepositFormEnhanced from '@/components/DirectDepositFormEnhanced'
import ReviewAndSign from '@/components/ReviewAndSign'
import { CheckCircle, DollarSign, AlertTriangle } from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { useAutoSave } from '@/hooks/useAutoSave'
import { useStepValidation } from '@/hooks/useStepValidation'
import { directDepositValidator } from '@/utils/stepValidators'

export default function DirectDepositStep({
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
  const [isSigned, setIsSigned] = useState(false)
  const [showReview, setShowReview] = useState(false)

  // Validation hook
  const { errors, fieldErrors, validate } = useStepValidation(directDepositValidator)

  // Auto-save data
  const autoSaveData = {
    formData,
    isValid,
    isSigned,
    showReview
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

  const handleFormComplete = async (data: any) => {
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
      title: 'Payment Method Setup',
      reviewTitle: 'Review Direct Deposit',
      description: 'Choose how you want to receive your pay. Direct deposit is the fastest and most secure way to receive your paycheck.',
      completionMessage: 'Payment method configured successfully!',
      importantInfoTitle: 'Important Information',
      importantInfo: [
        'Direct deposit is available 1-2 days earlier than paper checks',
        'Changes take 1-2 pay periods to take effect',
        'You can update your payment method anytime through HR',
        'Ensure your banking information is accurate'
      ],
      formTitle: 'Direct Deposit Setup',
      acknowledgments: {
        directDeposit: 'I authorize my employer to deposit my pay electronically',
        paperCheck: 'I choose to receive paper checks and will pick them up on payday',
        understand: 'I understand changes take 1-2 pay periods to take effect',
        update: 'I can update my payment method at any time through HR'
      }
    },
    es: {
      title: 'Configuración de Método de Pago',
      reviewTitle: 'Revisar Depósito Directo',
      description: 'Elija cómo desea recibir su pago. El depósito directo es la forma más rápida y segura de recibir su salario.',
      completionMessage: '¡Método de pago configurado exitosamente!',
      importantInfoTitle: 'Información Importante',
      importantInfo: [
        'El depósito directo está disponible 1-2 días antes que los cheques en papel',
        'Los cambios tardan 1-2 períodos de pago en entrar en vigencia',
        'Puede actualizar su método de pago en cualquier momento a través de RRHH',
        'Asegúrese de que su información bancaria sea precisa'
      ],
      formTitle: 'Configuración de Depósito Directo',
      acknowledgments: {
        directDeposit: 'Autorizo a mi empleador a depositar mi pago electrónicamente',
        paperCheck: 'Elijo recibir cheques en papel y los recogeré el día de pago',
        understand: 'Entiendo que los cambios tardan 1-2 períodos de pago en entrar en vigencia',
        update: 'Puedo actualizar mi método de pago en cualquier momento a través de RRHH'
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
              <DollarSign className="h-6 w-6 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">{t.reviewTitle}</h1>
            </div>
          </div>
          
          <ReviewAndSign
            formType="direct_deposit"
            formTitle="Direct Deposit Authorization Form"
            formData={formData}
            documentName="Direct Deposit Authorization"
            signerName={employee?.firstName + ' ' + employee?.lastName || 'Employee'}
            signerTitle={employee?.position}
            onSign={handleDigitalSignature}
            onEdit={handleBackFromReview}
            acknowledgments={[
              formData.paymentMethod === 'direct_deposit' 
                ? t.acknowledgments.directDeposit
                : t.acknowledgments.paperCheck,
              t.acknowledgments.understand,
              t.acknowledgments.update
            ]}
            language={language}
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
            <DollarSign className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          </div>
          <p className="text-gray-600 max-w-3xl mx-auto">{t.description}</p>
        </div>

        {/* Progress Indicator */}
        {isStepComplete && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t.completionMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Important Information */}
        <Card className="border-amber-200 bg-amber-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center space-x-2 text-amber-800">
              <AlertTriangle className="h-5 w-5" />
              <span>{t.importantInfoTitle}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-amber-800">
            <ul className="space-y-2 text-sm">
              {t.importantInfo.map((info, index) => (
                <li key={index}>• {info}</li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Direct Deposit Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5 text-blue-600" />
              <span>{t.formTitle}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <DirectDepositFormEnhanced
              initialData={formData}
              language={language}
              onComplete={handleFormComplete}
              onValidationChange={(valid: boolean, errors: Record<string, string>) => {
                setIsValid(valid)
              }}
              employeeId={employee?.id}
            />
          </CardContent>
        </Card>
      </div>
    </StepContainer>
  )
}