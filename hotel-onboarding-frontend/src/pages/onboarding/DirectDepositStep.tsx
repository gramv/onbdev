import React, { useState, useEffect } from 'react'
import { getApiUrl, getLegacyBaseUrl } from '@/config/api'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import DirectDepositFormEnhanced from '@/components/DirectDepositFormEnhanced'
import ReviewAndSign from '@/components/ReviewAndSign'
import PDFViewer from '@/components/PDFViewer'
import { CheckCircle, DollarSign, AlertTriangle } from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { StepContentWrapper } from '@/components/onboarding/StepContentWrapper'
import { useAutoSave } from '@/hooks/useAutoSave'
import { useStepValidation } from '@/hooks/useStepValidation'
import { directDepositValidator } from '@/utils/stepValidators'
import { ValidationSummary } from '@/components/ui/validation-summary'
import { FormSection } from '@/components/ui/form-section'
import axios from 'axios'

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
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [ssnFromI9, setSsnFromI9] = useState<string>('')

    // Try to retrieve SSN from PersonalInfoStep or I9 form data stored in session
  React.useEffect(() => {
    console.log('DirectDepositStep - Starting SSN retrieval...')
    try {
      // First try PersonalInfoStep data (where SSN is initially entered)
      const personalData = sessionStorage.getItem('onboarding_personal-info_data')
      console.log('DirectDepositStep - Personal info data exists:', !!personalData)
      if (personalData) {
        const parsed = JSON.parse(personalData)
        const ssn = parsed?.personalInfo?.ssn || parsed?.ssn || ''
        console.log('DirectDepositStep - Personal info parsed SSN:', ssn ? ssn.replace(/./g, '*').slice(-4) : 'NOT FOUND')
        if (ssn) {
          console.log('DirectDepositStep - Retrieved SSN from PersonalInfo data')
          setSsnFromI9(ssn)
          return
        }
      }

      // Fallback to I9 form data if not in PersonalInfo
      const i9Data = sessionStorage.getItem('onboarding_i9-form_data')
      console.log('DirectDepositStep - I9 form data exists:', !!i9Data)
      if (i9Data) {
        const parsed = JSON.parse(i9Data)
        const ssn = parsed?.personalInfo?.ssn || parsed?.ssn || ''
        console.log('DirectDepositStep - I9 form parsed SSN:', ssn ? ssn.replace(/./g, '*').slice(-4) : 'NOT FOUND')
        if (ssn) {
          console.log('DirectDepositStep - Retrieved SSN from I9 form data')
          setSsnFromI9(ssn)
        }
      }

      // Additional fallback: check I9 complete step data
      const i9CompleteData = sessionStorage.getItem('onboarding_i9-complete_data')
      console.log('DirectDepositStep - I9 complete data exists:', !!i9CompleteData)
      if (i9CompleteData) {
        const parsed = JSON.parse(i9CompleteData)
        const ssn = parsed?.formData?.ssn || parsed?.ssn || ''
        console.log('DirectDepositStep - I9 complete parsed SSN:', ssn ? ssn.replace(/./g, '*').slice(-4) : 'NOT FOUND')
        if (ssn) {
          console.log('DirectDepositStep - Retrieved SSN from I9 Complete data')
          setSsnFromI9(ssn)
        }
      }

      console.log('DirectDepositStep - SSN retrieval complete. Final SSN:', ssnFromI9 ? ssnFromI9.replace(/./g, '*').slice(-4) : 'NOT FOUND')
    } catch (e) {
      console.error('Failed to retrieve SSN from session data:', e)
    }
  }, [])

  // Stable extra data for PDF generation
  const extraPdfData = React.useMemo(() => ({
    firstName: employee?.firstName || (employee as any)?.first_name,
    lastName: employee?.lastName || (employee as any)?.last_name,
    email: (employee as any)?.email,
    ssn: ssnFromI9 || (formData as any)?.ssn || ''
  }), [employee?.firstName, (employee as any)?.first_name, employee?.lastName, (employee as any)?.last_name, (employee as any)?.email, ssnFromI9, (formData as any)?.ssn])

  // Validation hook
  const { errors, fieldErrors, validate } = useStepValidation(directDepositValidator)

  // Convert errors to ValidationSummary format
  const validationMessages = React.useMemo(() => {
    const messages = []
    
    // Add general errors
    if (errors && errors.length > 0) {
      messages.push(...errors.map(error => ({ message: error, type: 'error' as const })))
    }
    
    // Add field-specific errors
    if (fieldErrors) {
      Object.entries(fieldErrors).forEach(([field, message]) => {
        if (message) {
          messages.push({ field, message, type: 'error' as const })
        }
      })
    }
    
    return messages
  }, [errors, fieldErrors])

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
    console.log('DirectDepositStep - Loading data for step:', currentStep.id)
    
    // Try to load saved data from session storage
    const savedData = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        console.log('DirectDepositStep - Found saved data:', parsed)
        
        // Check for different data structures
        if (parsed.formData) {
          console.log('DirectDepositStep - Setting formData from parsed.formData')
          setFormData(parsed.formData)
        } else if (parsed.paymentMethod || parsed.primaryAccount) {
          // Direct data structure
          console.log('DirectDepositStep - Setting formData from direct structure')
          setFormData(parsed)
        }
        
        // Only set as signed if BOTH signed flag AND final PDF exist
        if ((parsed.isSigned || parsed.signed) && parsed.pdfUrl) {
          console.log('DirectDepositStep - Form was previously signed with PDF')
          setIsSigned(true)
          setIsValid(true)
          setPdfUrl(parsed.pdfUrl)
        } else if (parsed.showReview) {
          // Restore review state if it was saved but not signed
          console.log('DirectDepositStep - Restoring review state')
          setShowReview(true)
          setIsValid(parsed.isValid || false)
        }
      } catch (e) {
        console.error('Failed to parse saved direct deposit data:', e)
      }
    }
    
    // Only set as signed if step is complete AND we have a saved PDF
    if (progress.completedSteps.includes(currentStep.id)) {
      console.log('DirectDepositStep - Step marked as complete in progress')
      // Check if we have a signed PDF before marking as signed
      const savedData = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
      if (savedData) {
        const parsed = JSON.parse(savedData)
        if (parsed.pdfUrl && (parsed.isSigned || parsed.signed)) {
          setIsSigned(true)
          setIsValid(true)
        }
      }
    }
  }, [currentStep.id, progress.completedSteps])

  const handleFormComplete = async (data: any) => {
    // Transform nested data structure to flat structure for validation
    const validationData = {
      paymentMethod: data.paymentMethod,
      accountType: data.primaryAccount?.accountType,
      bankName: data.primaryAccount?.bankName,
      routingNumber: data.primaryAccount?.routingNumber,
      accountNumber: data.primaryAccount?.accountNumber,
      confirmAccountNumber: data.primaryAccount?.accountNumberConfirm,
      voidedCheckUploaded: data.voidedCheckUploaded,
      bankLetterUploaded: data.bankLetterUploaded,
      accountVerified: data.accountVerified || data.voidedCheckUploaded || data.bankLetterUploaded,
      // Include deposit type and amount for partial deposits
      depositType: data.depositType,
      depositAmount:
        data.depositType === 'partial' ? (data.primaryAccount?.depositAmount ?? '') : ''
    }
    
    // Validate the transformed data
    const validation = await validate(validationData)
    
    if (validation.valid) {
      setFormData(data)
      setIsValid(true)
      setShowReview(true)
      
      // Save to session storage (no pdfUrl until signed)
      sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify({
        formData: data,
        isValid: true,
        isSigned: false,
        showReview: true
        // Don't save pdfUrl here - only after signing
      }))
    }
  }

  const handleBackFromReview = () => {
    setShowReview(false)
    setPdfUrl(null)  // Clear any preview PDF
    
    // Update session storage to clear review state
    sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify({
      formData,
      isValid: true,
      isSigned: false,
      showReview: false
      // No pdfUrl
    }))
  }

  const handleDigitalSignature = async (signatureData: any, generatedPdfUrl?: string) => {
    console.log('DirectDepositStep - Signing with signature data')
    
    // If we have an employee ID, regenerate PDF with signature
    let finalPdfUrl = generatedPdfUrl || pdfUrl
    
    if (employee?.id && signatureData) {
      try {
        console.log('DirectDepositStep - Regenerating PDF with signature...')
        const apiUrl = getApiUrl()

        // Create payload with signature included - ensure SSN is properly included
        const pdfPayload = {
          ...formData,
          ...extraPdfData,
          signatureData: signatureData,
          // Ensure SSN is always included - try multiple sources
          ssn: ssnFromI9 || extraPdfData?.ssn || (formData as any)?.ssn || ''
        }

        // Debug logging to identify SSN sources
        console.log('DirectDepositStep - SSN Debug:')
        console.log('  - ssnFromI9:', ssnFromI9)
        console.log('  - extraPdfData.ssn:', extraPdfData?.ssn)
        console.log('  - formData.ssn:', (formData as any)?.ssn)
        console.log('  - Final SSN in payload:', pdfPayload.ssn)

        console.log('DirectDepositStep - PDF Payload being sent to backend:', JSON.stringify(pdfPayload, null, 2))

        // TEMPORARY: Save payload to localStorage for debugging
        localStorage.setItem('DEBUG_LAST_PDF_PAYLOAD', JSON.stringify(pdfPayload))
        console.log('💾 DEBUG: Payload saved to localStorage as DEBUG_LAST_PDF_PAYLOAD')
        
        // Regenerate PDF with signature
        const response = await axios.post(
          `${apiUrl}/onboarding/${employee.id}/direct-deposit/generate-pdf`,
          { employee_data: pdfPayload },
          { headers: { 'Content-Type': 'application/json' } }
        )
        
        if (response.data?.data?.pdf) {
          finalPdfUrl = response.data.data.pdf
          console.log('DirectDepositStep - PDF regenerated with signature')
        }
      } catch (error) {
        console.error('Failed to regenerate PDF with signature:', error)
        // Use preview PDF if regeneration fails
      }
    }
    
    setIsSigned(true)
    setPdfUrl(finalPdfUrl)
    
    // Create complete data with both nested and flat structure for compatibility
    const completeData = {
      // Include flattened primary account data for validator
      ...(formData.primaryAccount || {}),
      // Include all form data
      ...formData,
      // Keep nested structure too
      formData,
      signed: true,
      isSigned: true, // Include both for compatibility
      signatureData,
      pdfUrl: finalPdfUrl,
      completedAt: new Date().toISOString()
    }
    
    // Save to backend if we have an employee ID
    if (employee?.id) {
      try {
        const apiUrl = getApiUrl()
        await axios.post(`${apiUrl}/onboarding/${employee.id}/direct-deposit`, completeData)
        console.log('Direct deposit data saved to backend')
      } catch (error) {
        console.error('Failed to save direct deposit data to backend:', error)
        // Continue even if backend save fails - data is in session storage
      }
    }
    
    // Save to session storage with signed status and flat structure
    sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify({
      ...(formData.primaryAccount || {}), // Include flattened data
      ...formData,
      formData,
      isValid: true,
      isSigned: true,
      showReview: false,
      signed: true,
      signatureData,
      pdfUrl: generatedPdfUrl || pdfUrl,
      completedAt: completeData.completedAt
    }))
    
    // Save progress to update controller's step data
    await saveProgress(currentStep.id, completeData)
    
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

  // Show signed PDF if form is already signed
  if (isSigned && pdfUrl) {
    return (
      <StepContainer errors={errors} saveStatus={saveStatus}>
        <StepContentWrapper>
          <div className="space-y-6">
            {/* Completion Status */}
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                {t.completionMessage}
              </AlertDescription>
            </Alert>

            {/* Signed PDF Display */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <DollarSign className="h-5 w-5 text-green-600" />
                  <span>Signed Direct Deposit Authorization</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    Your direct deposit authorization has been completed and signed.
                  </p>
                  <div className="border rounded-lg p-4">
                    <PDFViewer pdfData={pdfUrl} height="600px" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </StepContentWrapper>
      </StepContainer>
    )
  }

  // Show review and sign if form is valid and review is requested
  if (showReview && formData) {
    const previewEmployeeId = employee?.id
    return (
      <StepContainer errors={errors} saveStatus={saveStatus}>
        <StepContentWrapper>
          <div className="space-y-6">
          {/* Validation Summary */}
          {validationMessages.length > 0 && (
            <ValidationSummary
              messages={validationMessages}
              title="Please correct the following issues"
              className="mb-6"
            />
          )}

          <FormSection
            title={t.reviewTitle}
            description="Please review your direct deposit information and sign to complete this step"
            icon={<DollarSign className="h-5 w-5" />}
            required={true}
          >
            <ReviewAndSign
              formType="direct_deposit"
              title="Direct Deposit Authorization Form"
              formData={formData}
              description={employee?.position ? `Position: ${employee.position}` : undefined}
              onSign={(signatureData: any) => handleDigitalSignature(signatureData, pdfUrl || undefined)}
              onBack={handleBackFromReview}
              language={language}
              usePDFPreview={!!previewEmployeeId}
              pdfEndpoint={previewEmployeeId ? `${getApiUrl()}/onboarding/${previewEmployeeId}/direct-deposit/generate-pdf` : undefined}
              onPdfGenerated={(pdf: string) => setPdfUrl(pdf)}
              extraPdfData={extraPdfData}
            />
          </FormSection>
          </div>
        </StepContentWrapper>
      </StepContainer>
    )
  }

  return (
    <StepContainer errors={errors} fieldErrors={fieldErrors} saveStatus={saveStatus}>
      <StepContentWrapper>
        <div className="space-y-6">
        {/* Validation Summary */}
        {validationMessages.length > 0 && (
          <ValidationSummary
            messages={validationMessages}
            title="Please correct the following issues"
            className="mb-6"
          />
        )}

        {/* Progress Indicator */}
        {isStepComplete && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t.completionMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Main Form Section */}
        <FormSection
          title={t.title}
          description={t.description}
          icon={<DollarSign className="h-5 w-5" />}
          completed={isStepComplete}
          required={true}
        >
          <div className="space-y-6">
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
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900">{t.formTitle}</h3>
              <DirectDepositFormEnhanced
                initialData={formData}
                language={language}
                onSave={handleFormComplete}
                onValidationChange={(valid: boolean) => {
                  setIsValid(valid)
                }}
                employee={employee}
                property={property}
              />
            </div>
          </div>
        </FormSection>
        </div>
      </StepContentWrapper>
    </StepContainer>
  )
}