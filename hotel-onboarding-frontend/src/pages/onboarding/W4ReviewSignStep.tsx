import React, { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import W4ReviewAndSign from '@/components/W4ReviewAndSign'
import PDFDocumentViewer from '@/components/ui/pdf-document-viewer'
import DigitalSignatureCapture from '@/components/DigitalSignatureCapture'
import { CheckCircle, CreditCard, AlertTriangle, DollarSign, Eye } from 'lucide-react'

interface OnboardingContext {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: () => void
  language: 'en' | 'es'
}

export default function W4ReviewSignStep() {
  const { currentStep, progress, markStepComplete, saveProgress, language = 'en' } = useOutletContext<OnboardingContext>()
  
  const [isComplete, setIsComplete] = useState(false)
  const [reviewData, setReviewData] = useState(null)

  // Load existing data from progress
  useEffect(() => {
    const existingData = progress.stepData?.['w4_review_sign']
    if (existingData) {
      setReviewData(existingData.reviewData)
      setIsComplete(existingData.completed || false)
    }
  }, [progress])

  // Get W-4 data from previous step
  const w4FormData = progress.stepData?.['w4_form']?.formData

  const handleComplete = (data: any) => {
    setReviewData(data)
    setIsComplete(true)
    const stepData = {
      reviewData: data,
      completed: true,
      completedAt: new Date().toISOString(),
      irsCompliant: true,
      legallyBinding: true
    }
    markStepComplete('w4_review_sign', stepData)
    saveProgress()
  }

  const handleBack = () => {
    // Navigate back to previous step logic
    console.log('Navigate back to W-4 form step')
  }

  const translations = {
    en: {
      title: 'Review & Sign Form W-4',
      subtitle: 'Employee\'s Withholding Certificate - Final Review',
      description: 'Review your tax withholding information and provide your digital signature to complete the IRS requirement.',
      irsRequirement: 'IRS Requirement',
      irsNotice: 'Form W-4 completion is required by the Internal Revenue Service (IRS) to determine the correct amount of federal income tax to withhold from your pay.',
      completedNotice: 'W-4 form review and signature completed successfully. Your tax withholding is now configured.',
      instructions: 'Important Tax Information',
      instructionsList: [
        'Review all withholding information for accuracy',
        'This determines how much tax is withheld from your pay',
        'You can submit a new W-4 anytime your situation changes',
        'Your signature certifies the information under penalties of perjury'
      ],
      missingData: 'Missing Required Data',
      missingDataDesc: 'Please complete the W-4 tax form before proceeding to review and signature.',
      estimatedTime: 'Estimated time: 3-4 minutes'
    },
    es: {
      title: 'Revisar y Firmar Formulario W-4',
      subtitle: 'Certificado de Retención del Empleado - Revisión Final',
      description: 'Revise su información de retención de impuestos y proporcione su firma digital para completar el requisito del IRS.',
      irsRequirement: 'Requisito del IRS',
      irsNotice: 'La completación del Formulario W-4 es requerida por el Servicio de Impuestos Internos (IRS) para determinar la cantidad correcta de impuesto federal sobre la renta a retener de su salario.',
      completedNotice: 'Revisión y firma del formulario W-4 completada exitosamente. Su retención de impuestos ya está configurada.',
      instructions: 'Información Importante de Impuestos',
      instructionsList: [
        'Revise toda la información de retención para verificar su precisión',
        'Esto determina cuánto impuesto se retiene de su salario',
        'Puede enviar un nuevo W-4 en cualquier momento que cambie su situación',
        'Su firma certifica la información bajo pena de perjurio'
      ],
      missingData: 'Faltan Datos Requeridos',
      missingDataDesc: 'Por favor complete el formulario de impuestos W-4 antes de proceder a la revisión y firma.',
      estimatedTime: 'Tiempo estimado: 3-4 minutos'
    }
  }

  const t = translations[language]

  // Check if required W-4 data exists
  if (!w4FormData) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <AlertTriangle className="h-6 w-6 text-red-600" />
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          </div>
          <p className="text-gray-600 max-w-3xl mx-auto">
            {t.description}
          </p>
        </div>

        <Alert className="bg-red-50 border-red-200">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>{t.missingData}:</strong> {t.missingDataDesc}
          </AlertDescription>
        </Alert>

        <div className="text-center text-sm text-gray-500">
          <p>{t.estimatedTime}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Step Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <DollarSign className="h-6 w-6 text-green-600" />
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          {t.description}
        </p>
      </div>

      {/* IRS Compliance Notice */}
      <Alert className="bg-blue-50 border-blue-200">
        <CreditCard className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>{t.irsRequirement}:</strong> {t.irsNotice}
        </AlertDescription>
      </Alert>

      {/* Progress Indicator */}
      {isComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            {t.completedNotice}
          </AlertDescription>
        </Alert>
      )}

      {/* Important Tax Information */}
      <Card className="border-orange-200 bg-orange-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center space-x-2 text-orange-800">
            <AlertTriangle className="h-5 w-5" />
            <span>{t.instructions}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-orange-800">
          <ul className="space-y-2 text-sm">
            {t.instructionsList.map((instruction, index) => (
              <li key={index}>• {instruction}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* W-4 Review and Sign Component */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="h-5 w-5 text-green-600" />
            <span>{t.subtitle}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <W4ReviewAndSign
            w4FormData={w4FormData}
            language={language}
            onComplete={handleComplete}
            onBack={handleBack}
          />
        </CardContent>
      </Card>

      {/* Completion Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-3">W-4 Review Requirements</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Review tax withholding information</span>
            <div className="flex items-center space-x-2">
              {isComplete ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
              )}
              <span className="text-sm font-medium">
                {isComplete ? 'Reviewed' : 'Required'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Digital signature certification</span>
            <div className="flex items-center space-x-2">
              {isComplete ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
              )}
              <span className="text-sm font-medium">
                {isComplete ? 'Signed' : 'Required'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* IRS Notice */}
      <div className="text-xs text-gray-500 border-t pt-4">
        <p className="mb-2"><strong>IRS Notice:</strong> This form determines your federal income tax withholding.</p>
        <p>Under penalties of perjury, the information provided must be true, correct, and complete.</p>
      </div>

      {/* Estimated Time */}
      <div className="text-center text-sm text-gray-500">
        <p>{t.estimatedTime}</p>
      </div>
    </div>
  )
}