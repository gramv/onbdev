/**
 * Enhanced Health Insurance Step Component
 * Integrates all new components with comprehensive error handling and mobile optimization
 */

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  ArrowLeft, 
  ArrowRight,
  Loader2
} from 'lucide-react'
import { cn } from '@/lib/utils'

// Import our new components
import { HealthInsuranceProvider, useHealthInsurance } from '../contexts/HealthInsuranceContext'
import { HealthInsuranceErrorBoundary } from './HealthInsuranceErrorBoundary'
import { HealthInsuranceErrorDisplay } from './HealthInsuranceErrorDisplay'
import { ResponsivePDFViewer } from './ResponsivePDFViewer'
import { MobileSignatureCapture } from './MobileSignatureCapture'
import { HealthInsuranceStep } from '../types/healthInsuranceState'
import { StepProps } from '../controllers/OnboardingFlowController'
import { StepContainer } from './onboarding/StepContainer'
import { StepContentWrapper } from './onboarding/StepContentWrapper'
import { useAutoSave } from '../hooks/useAutoSave'
import { useStepValidation } from '../hooks/useStepValidation'
import { healthInsuranceValidator } from '../utils/stepValidators'

// Step content components
function FormStepContent() {
  const { state, updateFormData, validateForm, nextStep } = useHealthInsurance()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleFormSubmit = async () => {
    setIsSubmitting(true)
    try {
      validateForm()
      if (state.formData.isValid) {
        nextStep()
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <FileText className="h-12 w-12 text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {state.language === 'es' ? 'Inscripción de Seguro de Salud' : 'Health Insurance Enrollment'}
        </h2>
        <p className="text-gray-600">
          {state.language === 'es' 
            ? 'Complete su información de seguro de salud'
            : 'Complete your health insurance information'
          }
        </p>
      </div>

      {/* Form content would go here - simplified for this example */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="text-center text-gray-500">
              {state.language === 'es' 
                ? 'Formulario de seguro de salud (implementación completa pendiente)'
                : 'Health insurance form (full implementation pending)'
              }
            </div>
            
            <Button 
              onClick={handleFormSubmit}
              disabled={isSubmitting || !state.formData.isValid}
              className="w-full"
            >
              {isSubmitting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {state.language === 'es' ? 'Continuar a Revisión' : 'Continue to Review'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function ReviewStepContent() {
  const { state, generatePDF, nextStep, previousStep } = useHealthInsurance()
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    // Auto-generate PDF when entering review step
    if (!state.pdfData && !state.pdfGenerating) {
      handleGeneratePDF()
    }
  }, [])

  const handleGeneratePDF = async () => {
    setIsGenerating(true)
    try {
      await generatePDF()
    } finally {
      setIsGenerating(false)
    }
  }

  const handleContinue = () => {
    if (state.pdfData) {
      nextStep()
    } else {
      handleGeneratePDF()
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <FileText className="h-12 w-12 text-green-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {state.language === 'es' ? 'Revisar Documento' : 'Review Document'}
        </h2>
        <p className="text-gray-600">
          {state.language === 'es' 
            ? 'Revise su formulario de seguro de salud antes de firmar'
            : 'Review your health insurance form before signing'
          }
        </p>
      </div>

      {/* PDF Viewer */}
      <Card>
        <CardContent className="p-0">
          {state.pdfGenerating || isGenerating ? (
            <div className="h-96 flex items-center justify-center">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-gray-600">
                  {state.language === 'es' ? 'Generando documento...' : 'Generating document...'}
                </p>
              </div>
            </div>
          ) : state.pdfData ? (
            <ResponsivePDFViewer
              pdfData={state.pdfData}
              title="Health Insurance Form"
              language={state.language}
              mobileOptimized={true}
            />
          ) : state.pdfError ? (
            <div className="h-96 flex items-center justify-center p-6">
              <HealthInsuranceErrorDisplay
                error={state.pdfError}
                language={state.language}
                onAction={async (action) => {
                  if (action === 'retry') {
                    await handleGeneratePDF()
                  }
                }}
              />
            </div>
          ) : (
            <div className="h-96 flex items-center justify-center">
              <Button onClick={handleGeneratePDF}>
                {state.language === 'es' ? 'Generar Documento' : 'Generate Document'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={previousStep}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          {state.language === 'es' ? 'Atrás' : 'Back'}
        </Button>
        
        <Button 
          onClick={handleContinue}
          disabled={!state.pdfData}
        >
          {state.language === 'es' ? 'Continuar a Firma' : 'Continue to Sign'}
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  )
}

function SignatureStepContent() {
  const { state, captureSignature, nextStep, previousStep } = useHealthInsurance()
  const [showSignatureCapture, setShowSignatureCapture] = useState(false)

  const handleSignature = (signatureData: any) => {
    captureSignature(signatureData)
    setShowSignatureCapture(false)
    nextStep()
  }

  const handleStartSigning = () => {
    setShowSignatureCapture(true)
  }

  if (showSignatureCapture) {
    return (
      <div className="space-y-6">
        <MobileSignatureCapture
          onSignature={handleSignature}
          onCancel={() => setShowSignatureCapture(false)}
          language={state.language}
          title={state.language === 'es' ? 'Firme su Formulario' : 'Sign Your Form'}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <FileText className="h-12 w-12 text-purple-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {state.language === 'es' ? 'Firma Digital' : 'Digital Signature'}
        </h2>
        <p className="text-gray-600">
          {state.language === 'es' 
            ? 'Firme digitalmente su formulario de seguro de salud'
            : 'Digitally sign your health insurance form'
          }
        </p>
      </div>

      {/* Signature Instructions */}
      <Card>
        <CardContent className="p-6">
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              {state.language === 'es' 
                ? 'Al firmar este documento, usted confirma que toda la información proporcionada es correcta y completa.'
                : 'By signing this document, you confirm that all information provided is accurate and complete.'
              }
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={previousStep}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          {state.language === 'es' ? 'Atrás' : 'Back'}
        </Button>
        
        <Button onClick={handleStartSigning}>
          {state.language === 'es' ? 'Firmar Documento' : 'Sign Document'}
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  )
}

function SignedPreviewStepContent() {
  const { state, generateSignedPDF, nextStep, previousStep } = useHealthInsurance()
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    // Auto-generate signed PDF when entering this step
    if (!state.signedPdfData && !state.pdfGenerating && state.signatureData) {
      handleGenerateSignedPDF()
    }
  }, [])

  const handleGenerateSignedPDF = async () => {
    setIsGenerating(true)
    try {
      await generateSignedPDF()
    } finally {
      setIsGenerating(false)
    }
  }

  const handleContinue = () => {
    nextStep()
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <FileText className="h-12 w-12 text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {state.language === 'es' ? 'Documento Firmado' : 'Signed Document'}
        </h2>
        <p className="text-gray-600">
          {state.language === 'es'
            ? 'Revise su documento firmado antes de continuar.'
            : 'Review your signed document before continuing.'
          }
        </p>
      </div>

      {/* Signed PDF Viewer */}
      <Card>
        <CardContent className="p-0">
          {state.pdfGenerating || isGenerating ? (
            <div className="h-96 flex items-center justify-center">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-gray-600">
                  {state.language === 'es' ? 'Generando documento firmado...' : 'Generating signed document...'}
                </p>
              </div>
            </div>
          ) : state.signedPdfData ? (
            <ResponsivePDFViewer
              pdfData={state.signedPdfData}
              title={state.language === 'es' ? 'Formulario de Seguro de Salud Firmado' : 'Signed Health Insurance Form'}
              language={state.language}
              mobileOptimized={true}
            />
          ) : state.pdfError ? (
            <div className="h-96 flex items-center justify-center p-6">
              <HealthInsuranceErrorDisplay
                error={state.pdfError}
                language={state.language}
                onAction={async (action) => {
                  if (action === 'retry') {
                    await handleGenerateSignedPDF()
                  }
                }}
                onDismiss={() => {
                  // Clear error and try again
                  handleGenerateSignedPDF()
                }}
              />
            </div>
          ) : (
            <div className="h-96 flex items-center justify-center p-6">
              <div className="text-center">
                <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">
                  {state.language === 'es' ? 'No se pudo cargar el documento firmado.' : 'Could not load signed document.'}
                </p>
                <Button onClick={handleGenerateSignedPDF} disabled={isGenerating}>
                  {isGenerating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      {state.language === 'es' ? 'Generando...' : 'Generating...'}
                    </>
                  ) : (
                    state.language === 'es' ? 'Reintentar' : 'Retry'
                  )}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={previousStep}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          {state.language === 'es' ? 'Volver a Firmar' : 'Back to Sign'}
        </Button>

        <Button
          onClick={handleContinue}
          disabled={!state.signedPdfData}
        >
          {state.language === 'es' ? 'Completar' : 'Complete'}
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  )
}

function CompleteStepContent() {
  const { state } = useHealthInsurance()

  return (
    <div className="space-y-6">
      <div className="text-center">
        <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {state.language === 'es' ? '¡Completado!' : 'Complete!'}
        </h2>
        <p className="text-gray-600">
          {state.language === 'es'
            ? 'Su inscripción de seguro de salud ha sido completada exitosamente.'
            : 'Your health insurance enrollment has been completed successfully.'
          }
        </p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">
                {state.language === 'es' ? 'Estado:' : 'Status:'}
              </span>
              <span className="text-green-600 font-semibold">
                {state.language === 'es' ? 'Completado' : 'Completed'}
              </span>
            </div>
            
            {state.completedAt && (
              <div className="flex items-center justify-between">
                <span className="text-gray-600">
                  {state.language === 'es' ? 'Completado el:' : 'Completed on:'}
                </span>
                <span className="text-gray-900">
                  {new Date(state.completedAt).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Main component content
function HealthInsuranceStepContent(props: StepProps) {
  const { state, selectors } = useHealthInsurance()
  const progress = selectors.getProgress

  // Use the same hooks as the original component
  const { isValid, errors } = useStepValidation(
    state.formData,
    healthInsuranceValidator,
    props.currentStep?.id || 'health-insurance'
  )

  const { saveData } = useAutoSave(
    props.currentStep?.id || 'health-insurance',
    state.formData,
    props.saveProgress,
    5000 // Auto-save every 5 seconds
  )

  // Handle step completion
  useEffect(() => {
    if (state.isCompleted && isValid) {
      props.markStepComplete(props.currentStep?.id || 'health-insurance', state.formData)
    }
  }, [state.isCompleted, isValid, props, state.formData])

  const renderStepContent = () => {
    switch (state.currentStep) {
      case HealthInsuranceStep.FORM:
        return <FormStepContent />
      case HealthInsuranceStep.REVIEW:
        return <ReviewStepContent />
      case HealthInsuranceStep.SIGNATURE:
        return <SignatureStepContent />
      case HealthInsuranceStep.SIGNED_PREVIEW:
        return <SignedPreviewStepContent />
      case HealthInsuranceStep.COMPLETE:
        return <CompleteStepContent />
      default:
        return <FormStepContent />
    }
  }

  return (
    <StepContainer>
      <StepContentWrapper>
        <div className="max-w-4xl mx-auto p-4 space-y-6">
      {/* Progress Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>
                {state.language === 'es' ? 'Progreso' : 'Progress'}
              </span>
              <span>
                {progress.current} {state.language === 'es' ? 'de' : 'of'} {progress.total}
              </span>
            </div>
            <Progress value={progress.percentage} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Step Content */}
      {renderStepContent()}

      {/* Global Error Display */}
      {state.hasErrors && (
        <div className="space-y-2">
          {Object.entries(state.errors).map(([key, error]) => (
            <HealthInsuranceErrorDisplay
              key={key}
              error={error}
              language={state.language}
              onAction={async (action) => {
                // Handle global error actions
                console.log('Global error action:', action, 'for error:', key)
              }}
              onDismiss={() => {
                // Clear specific error
                console.log('Dismiss error:', key)
              }}
            />
          ))}
        </div>
      )}
        </div>
      </StepContentWrapper>
    </StepContainer>
  )
}

// Main exported component with providers
export function HealthInsuranceStepEnhanced(props: StepProps) {
  return (
    <HealthInsuranceErrorBoundary
      language={props.language}
      onError={(error) => {
        console.error('Health Insurance Step Error:', error)
      }}
    >
      <HealthInsuranceProvider
        employeeId={props.employee?.id}
        language={props.language}
        onComplete={(data) => {
          props.markStepComplete('health-insurance', data)
        }}
        onError={(error) => {
          console.error('Health Insurance Provider Error:', error)
        }}
      >
        <HealthInsuranceStepContent {...props} />
      </HealthInsuranceProvider>
    </HealthInsuranceErrorBoundary>
  )
}
