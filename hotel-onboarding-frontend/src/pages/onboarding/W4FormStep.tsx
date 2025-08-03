import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import W4FormClean from '@/components/W4FormClean'
import ReviewAndSign from '@/components/ReviewAndSign'
import { CheckCircle, CreditCard, FileText, AlertTriangle } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FormSection } from '@/components/ui/form-section'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { StepContentWrapper } from '@/components/onboarding/StepContentWrapper'
import { useAutoSave } from '@/hooks/useAutoSave'
import { useStepValidation } from '@/hooks/useStepValidation'
import { w4FormValidator } from '@/utils/stepValidators'

interface W4Translations {
  title: string
  description: string
  federalNotice: string
  completionMessage: string
  importantInfoTitle: string
  importantInfo: string[]
  fillFormTab: string
  reviewTab: string
  formTitle: string
  reviewTitle: string
  reviewDescription: string
  agreementText: string
}

export default function W4FormStep({
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
  const { errors, fieldErrors, validate } = useStepValidation(w4FormValidator)

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

  // Load existing data
  useEffect(() => {
    if (progress.completedSteps.includes(currentStep.id)) {
      setIsSigned(true)
      setFormValid(true)
      setActiveTab('review')
    }
  }, [currentStep.id, progress.completedSteps])

  const handleFormComplete = async (data: any) => {
    // Validate the form data
    const validation = await validate(data)
    
    if (validation.valid) {
      setFormData(data)
      setFormValid(true)
      setActiveTab('review')
    }
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
    if (!data) return <div>No form data available</div>
    
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-600">First Name</label>
            <p className="text-gray-900">{data.first_name || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Middle Initial</label>
            <p className="text-gray-900">{data.middle_initial || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Last Name</label>
            <p className="text-gray-900">{data.last_name || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Social Security Number</label>
            <p className="text-gray-900">{data.ssn ? '***-**-' + data.ssn.slice(-4) : 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Address</label>
            <p className="text-gray-900">{data.address || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">City, State, ZIP</label>
            <p className="text-gray-900">
              {[data.city, data.state, data.zip_code].filter(Boolean).join(', ') || 'Not provided'}
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Filing Status</label>
            <p className="text-gray-900">{data.filing_status || 'Not provided'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Multiple Jobs or Spouse Works</label>
            <p className="text-gray-900">{data.multiple_jobs ? 'Yes' : 'No'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Dependents Amount</label>
            <p className="text-gray-900">${data.dependents_amount || '0'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Extra Withholding</label>
            <p className="text-gray-900">${data.extra_withholding || '0'}</p>
          </div>
        </div>
      </div>
    )
  }

  const translations: Record<'en' | 'es', W4Translations> = {
    en: {
      title: 'W-4 Tax Withholding',
      description: 'Complete Form W-4 to determine the correct amount of federal income tax to withhold from your pay.',
      federalNotice: 'Form W-4 is required by the Internal Revenue Service (IRS) for all employees to determine federal income tax withholding.',
      completionMessage: 'W-4 form completed successfully with digital signature.',
      importantInfoTitle: 'Important Tax Information',
      importantInfo: [
        'Complete this form based on your current tax situation',
        'You can submit a new W-4 anytime your situation changes',
        'Consider using the IRS Tax Withholding Estimator for accuracy',
        'Consult a tax professional if you have complex tax situations'
      ],
      fillFormTab: 'Fill Form',
      reviewTab: 'Preview & Sign',
      formTitle: 'Form W-4: Employee\'s Withholding Certificate',
      reviewTitle: 'Review W-4 Form',
      reviewDescription: 'Please review your tax withholding information and sign electronically',
      agreementText: 'Under penalties of perjury, I declare that this certificate, to the best of my knowledge and belief, is true, correct, and complete.'
    },
    es: {
      title: 'Retención de Impuestos W-4',
      description: 'Complete el Formulario W-4 para determinar la cantidad correcta de impuesto federal sobre la renta a retener de su pago.',
      federalNotice: 'El Formulario W-4 es requerido por el Servicio de Impuestos Internos (IRS) para todos los empleados.',
      completionMessage: 'Formulario W-4 completado exitosamente con firma digital.',
      importantInfoTitle: 'Información Fiscal Importante',
      importantInfo: [
        'Complete este formulario basado en su situación fiscal actual',
        'Puede enviar un nuevo W-4 cuando cambie su situación',
        'Considere usar el Estimador de Retención del IRS',
        'Consulte a un profesional de impuestos si tiene situaciones complejas'
      ],
      fillFormTab: 'Llenar Formulario',
      reviewTab: 'Revisar y Firmar',
      formTitle: 'Formulario W-4: Certificado de Retención del Empleado',
      reviewTitle: 'Revisar Formulario W-4',
      reviewDescription: 'Por favor revise su información de retención de impuestos y firme electrónicamente',
      agreementText: 'Bajo pena de perjurio, declaro que este certificado, a mi leal saber y entender, es verdadero, correcto y completo.'
    }
  }

  const t = translations[language]

  return (
    <StepContainer errors={errors} fieldErrors={fieldErrors} saveStatus={saveStatus}>
      <StepContentWrapper>
        <div className="space-y-6">
        {/* Step Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <CreditCard className="h-6 w-6 text-blue-600" />
            <h1 className="text-heading-secondary">{t.title}</h1>
          </div>
          <p className="text-gray-600 max-w-3xl mx-auto">{t.description}</p>
        </div>

        {/* Federal Compliance Notice */}
        <Alert className="bg-blue-50 border-blue-200">
          <CreditCard className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">
            <strong>{language === 'es' ? 'Requisito Federal:' : 'Federal Requirement:'}</strong> {t.federalNotice}
          </AlertDescription>
        </Alert>

        {/* Progress Indicator */}
        {isSigned && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t.completionMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Important Tax Information */}
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center space-x-2 text-orange-800">
              <AlertTriangle className="h-5 w-5" />
              <span>{t.importantInfoTitle}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="text-orange-800">
            <ul className="space-y-2 text-sm">
              {t.importantInfo.map((info, index) => (
                <li key={index}>• {info}</li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Form Section */}
        <FormSection
          title={String(t.title || 'W-4 Tax Withholding')}
          description={String(t.description || '')}
          icon={<FileText />}
          completed={isSigned}
          required={true}
        >
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
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <span>{t.formTitle}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <W4FormClean
                    initialData={formData}
                    language={language}
                    employeeId={employee?.id}
                    onComplete={handleFormComplete}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="review" className="space-y-6">
              {formData && (
                <ReviewAndSign
                  formType="w4-form"
                  formData={formData}
                  title={t.reviewTitle}
                  description={t.reviewDescription}
                  language={language}
                  onSign={handleSign}
                  onBack={() => setActiveTab('form')}
                  renderPreview={renderFormPreview}
                  usePDFPreview={true}
                  pdfEndpoint={`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/api/onboarding/${employee?.id}/w4-form/generate-pdf`}
                  federalCompliance={{
                    formName: 'Form W-4, Employee\'s Withholding Certificate',
                    retentionPeriod: 'For 4 years after the date the last tax return using the information was filed',
                    requiresWitness: false
                  }}
                  agreementText={t.agreementText}
                />
              )}
            </TabsContent>
          </Tabs>
        </FormSection>
        </div>
      </StepContentWrapper>
    </StepContainer>
  )
}