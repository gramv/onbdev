import React, { useState, useEffect } from 'react'
import { getApiUrl, getLegacyBaseUrl } from '@/config/api'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import HealthInsuranceForm from '@/components/HealthInsuranceForm'
import ReviewAndSign from '@/components/ReviewAndSign'
import PDFViewer from '@/components/PDFViewer'
import { CheckCircle, Heart, Users, AlertTriangle } from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { StepContentWrapper } from '@/components/onboarding/StepContentWrapper'
import { useAutoSave } from '@/hooks/useAutoSave'
import { useStepValidation } from '@/hooks/useStepValidation'
import { healthInsuranceValidator } from '@/utils/stepValidators'
import axios from 'axios'

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
  const [personalInfo, setPersonalInfo] = useState<any>(null)
  const [section125Acknowledged, setSection125Acknowledged] = useState(false)
  const [signatureData, setSignatureData] = useState<any>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [showSignedPreview, setShowSignedPreview] = useState(false)

  // Validation hook
  const { errors, fieldErrors, validate } = useStepValidation(healthInsuranceValidator)

  // Auto-save data
  const autoSaveData = {
    formData,
    isValid,
    showReview,
    isSigned
  }

  // Debug state changes
  useEffect(() => {
    console.log('HealthInsuranceStep - State changed:', {
      showSignedPreview,
      isSigned,
      hasPdfUrl: !!pdfUrl,
      pdfUrlLength: pdfUrl?.length,
      showReview
    })
  }, [showSignedPreview, isSigned, pdfUrl, showReview])

  // Auto-save hook
  const { saveStatus } = useAutoSave(autoSaveData, {
    onSave: async (data) => {
      await saveProgress(currentStep.id, data)
    }
  })

  // Load personal info from session storage (only once)
  useEffect(() => {
    console.log('HealthInsuranceStep - Loading personal info from session storage')

    // Load personal information from PersonalInfoStep
    const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data')
    if (personalInfoData) {
      try {
        const parsed = JSON.parse(personalInfoData)
        console.log('HealthInsuranceStep - Found personal info data:', parsed)

        // Extract personal info from the nested structure
        if (parsed.personalInfo && typeof parsed.personalInfo === 'object' && !Array.isArray(parsed.personalInfo)) {
          // Use the nested personalInfo object directly - this should have all the data
          console.log('HealthInsuranceStep - Raw personalInfo from session:', parsed.personalInfo)

          const personalInfoObj = {
            firstName: parsed.personalInfo.firstName || '',
            lastName: parsed.personalInfo.lastName || '',
            middleInitial: parsed.personalInfo.middleInitial || '',
            ssn: parsed.personalInfo.ssn || '',
            dateOfBirth: parsed.personalInfo.dateOfBirth || '',
            address: parsed.personalInfo.address || '',
            city: parsed.personalInfo.city || '',
            state: parsed.personalInfo.state || '',
            zipCode: parsed.personalInfo.zipCode || parsed.personalInfo.zip || '',
            phone: parsed.personalInfo.phone || '',
            email: parsed.personalInfo.email || '',
            gender: parsed.personalInfo.gender || '',
            maritalStatus: parsed.personalInfo.maritalStatus || '',
            aptNumber: parsed.personalInfo.aptNumber || '',
            preferredName: parsed.personalInfo.preferredName || ''
          }

          console.log('HealthInsuranceStep - Extracted personal info object:', personalInfoObj)
          console.log('HealthInsuranceStep - Personal info fields verification:', {
            ssn: personalInfoObj.ssn || 'MISSING',
            address: personalInfoObj.address || 'MISSING',
            city: personalInfoObj.city || 'MISSING',
            state: personalInfoObj.state || 'MISSING',
            zipCode: personalInfoObj.zipCode || 'MISSING',
            phone: personalInfoObj.phone || 'MISSING',
            email: personalInfoObj.email || 'MISSING',
            gender: personalInfoObj.gender || 'MISSING',
            dateOfBirth: personalInfoObj.dateOfBirth || 'MISSING'
          })
          setPersonalInfo(personalInfoObj)
        } else if (parsed.firstName || parsed.lastName) {
          // Direct structure fallback
          const personalInfoObj = {
            firstName: parsed.firstName || '',
            lastName: parsed.lastName || '',
            middleInitial: parsed.middleInitial || '',
            ssn: parsed.ssn || '',
            dateOfBirth: parsed.dateOfBirth || '',
            address: parsed.address || '',
            city: parsed.city || '',
            state: parsed.state || '',
            zipCode: parsed.zipCode || parsed.zip || '',
            phone: parsed.phone || '',
            email: parsed.email || '',
            gender: parsed.gender || '',
            maritalStatus: parsed.maritalStatus || '',
            aptNumber: parsed.aptNumber || ''
          }
          console.log('HealthInsuranceStep - Using direct structure personal info:', personalInfoObj)
          setPersonalInfo(personalInfoObj)
        }
      } catch (e) {
        console.error('Failed to parse personal info data:', e)
      }
    }

    // Fallback to employee prop if no session data found
    if (!personalInfoData && employee) {
      const employeePersonalInfo = {
        firstName: employee.firstName || '',
        lastName: employee.lastName || '',
        middleInitial: employee.middleInitial || '',
        ssn: employee.ssn || '',
        dateOfBirth: employee.dateOfBirth || '',
        address: employee.address || '',
        city: employee.city || '',
        state: employee.state || '',
        zipCode: employee.zipCode || '',
        phone: employee.phone || '',
        email: employee.email || '',
        gender: employee.gender || '',
        maritalStatus: employee.maritalStatus || '',
        aptNumber: employee.aptNumber || ''
      }
      console.log('HealthInsuranceStep - Using employee personal info as fallback:', employeePersonalInfo)
      setPersonalInfo(employeePersonalInfo)
    }
  }, []) // Empty dependency array - only run once on mount

  // Load health insurance form data
  useEffect(() => {
    console.log('HealthInsuranceStep - Loading form data for step:', currentStep.id)

    // Try to load saved health insurance data from session storage
    const savedData = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        console.log('HealthInsuranceStep - Found saved data:', parsed)

        // Check for different data structures
        if (parsed.formData) {
          console.log('HealthInsuranceStep - Setting formData from parsed.formData')
          setFormData(parsed.formData)
        } else if (parsed.medicalPlan !== undefined || parsed.isWaived !== undefined) {
          // Direct data structure
          console.log('HealthInsuranceStep - Setting formData from direct structure')
          setFormData(parsed)
        }

        if (parsed.section125Acknowledged) {
          setSection125Acknowledged(true)
        }

        if (parsed.isSigned || parsed.signed) {
          console.log('HealthInsuranceStep - Form was previously signed')
          setIsSigned(true)
          setIsValid(true)
        }

        // Restore personal info if it was saved with the health insurance data
        if (parsed.personalInfo && !personalInfo) {
          console.log('HealthInsuranceStep - Restoring personal info from health insurance session data')
          setPersonalInfo(parsed.personalInfo)
        }
      } catch (e) {
        console.error('Failed to parse saved health insurance data:', e)
      }
    }

    if (progress.completedSteps.includes(currentStep.id)) {
      console.log('HealthInsuranceStep - Step marked as complete in progress')
      setIsSigned(true)
      setIsValid(true)
    }
  }, [currentStep.id, progress.completedSteps])

  // Preserve personal info in session storage when it's set
  useEffect(() => {
    if (personalInfo && Object.keys(personalInfo).length > 0) {
      console.log('HealthInsuranceStep - Preserving personal info in session storage')
      const currentHealthData = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
      let healthData = {}

      if (currentHealthData) {
        try {
          healthData = JSON.parse(currentHealthData)
        } catch (e) {
          console.error('Failed to parse current health data:', e)
        }
      }

      // Preserve personal info in health insurance session data
      const updatedHealthData = {
        ...healthData,
        personalInfo: personalInfo
      }

      sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify(updatedHealthData))
    }
  }, [personalInfo, currentStep.id])

  const handleFormSave = async (data: any) => {
    console.log('HealthInsuranceStep - handleFormSave called with data:', data)
    // Validate the form data
    const validation = await validate(data)
    console.log('Validation result:', validation)
    
    if (validation.valid) {
      console.log('Validation passed, saving data and showing review')
      setFormData(data)
      setIsValid(true)
      setShowReview(true)
      
      // Save to session storage with personal info preserved
      sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify({
        formData: data,
        personalInfo: personalInfo, // Preserve personal info
        isValid: true,
        isSigned: false,
        showReview: true,
        section125Acknowledged
      }))
    } else {
      console.log('Validation failed:', validation.errors)
    }
  }

  const handleBackFromReview = () => {
    setShowReview(false)
  }

  const handleDigitalSignature = async (signatureDataInput: any) => {
    // Check if Section 125 is acknowledged
    if (!section125Acknowledged) {
      alert(language === 'en'
        ? 'Please acknowledge the Section 125 terms before signing.'
        : 'Por favor, acepte los términos de la Sección 125 antes de firmar.')
      return
    }

    try {
      console.log('HealthInsuranceStep - Starting signature process')

      // Store signature data
      setSignatureData(signatureDataInput)

      // First, generate the unsigned PDF to get the base PDF data
      const pdfResponse = await fetch(`${getApiUrl()}/onboarding/${employee?.id || 'test-employee'}/health-insurance/generate-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employee_data: {
            ...formData,
            personalInfo: personalInfo,
            section125Acknowledged: section125Acknowledged
          }
        })
      })

      if (!pdfResponse.ok) {
        throw new Error('Failed to generate PDF for signing')
      }

      const pdfResult = await pdfResponse.json()
      const unsignedPdfBase64 = pdfResult.data?.pdf

      if (!unsignedPdfBase64) {
        throw new Error('No PDF data received')
      }

      // Now add signature to the PDF
      const signatureResponse = await fetch(`${getApiUrl()}/forms/health-insurance/add-signature`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pdf_data: unsignedPdfBase64,
          signature: signatureDataInput.signature,
          signature_type: 'employee_health_insurance',
          page_num: 1  // Page 2 (0-indexed)
        })
      })

      if (!signatureResponse.ok) {
        throw new Error('Failed to add signature to PDF')
      }

      // Get the signed PDF as blob and convert to data URL
      const signedPdfBlob = await signatureResponse.blob()
      const signedPdfArrayBuffer = await signedPdfBlob.arrayBuffer()

      // Convert ArrayBuffer to base64 safely (handles large files)
      const uint8Array = new Uint8Array(signedPdfArrayBuffer)
      let binaryString = ''
      const chunkSize = 8192 // Process in chunks to avoid stack overflow

      for (let i = 0; i < uint8Array.length; i += chunkSize) {
        const chunk = uint8Array.slice(i, i + chunkSize)
        binaryString += String.fromCharCode.apply(null, Array.from(chunk))
      }

      const signedPdfBase64 = btoa(binaryString)
      const signedPdfDataUrl = `data:application/pdf;base64,${signedPdfBase64}`

      // Store the signed PDF and update states
      setPdfUrl(signedPdfDataUrl)
      setIsSigned(true)
      setShowSignedPreview(true)
      setShowReview(false) // CRITICAL: Hide the review to show the signed preview

      console.log('HealthInsuranceStep - Signature process completed successfully')
      console.log('HealthInsuranceStep - State after signing:', {
        isSigned: true,
        showSignedPreview: true,
        showReview: false, // This should be false now
        hasPdfUrl: !!signedPdfDataUrl,
        pdfUrlLength: signedPdfDataUrl?.length
      })

    } catch (error) {
      console.error('HealthInsuranceStep - Signature process failed:', error)

      // Reset states on failure
      setIsSigned(false)
      setPdfUrl(null)
      setShowSignedPreview(false)

      alert(language === 'en'
        ? 'Failed to sign the document. Please try again.'
        : 'Error al firmar el documento. Por favor, inténtelo de nuevo.')
      return // Exit early on failure
    }
    
    // Create complete data with proper structure for backend
    // Ensure dental and vision coverage fields are properly normalized
    const normalizedFormData = {
      ...formData,
      // Normalize dental coverage - ensure both fields are set consistently
      dentalCoverage: formData.dentalCoverage || formData.dentalEnrolled || false,
      dentalEnrolled: formData.dentalCoverage || formData.dentalEnrolled || false,
      // Normalize vision coverage - ensure both fields are set consistently
      visionCoverage: formData.visionCoverage || formData.visionEnrolled || false,
      visionEnrolled: formData.visionCoverage || formData.visionEnrolled || false,
    }

    console.log('HealthInsuranceStep - Normalized form data for PDF:', {
      dentalCoverage: normalizedFormData.dentalCoverage,
      dentalEnrolled: normalizedFormData.dentalEnrolled,
      dentalTier: normalizedFormData.dentalTier,
      visionCoverage: normalizedFormData.visionCoverage,
      visionEnrolled: normalizedFormData.visionEnrolled,
      visionTier: normalizedFormData.visionTier,
    })

    const completeData = {
      employee_data: {
        ...normalizedFormData,
        personalInfo,  // Keep personalInfo at top level of employee_data
        dependents: normalizedFormData.dependents || [],
        hasStepchildren: normalizedFormData.hasStepchildren,
        stepchildrenNames: normalizedFormData.stepchildrenNames,
        dependentsSupported: formData.dependentsSupported,
        irsDependentConfirmation: formData.irsDependentConfirmation
      },
      signed: true,
      isSigned: true,
      section125Acknowledged,
      signatureData,
      completedAt: new Date().toISOString()
    }
    
    // Save to backend if we have an employee ID
    if (employee?.id) {
      try {
        const apiUrl = getApiUrl()
        await axios.post(`${apiUrl}/onboarding/${employee.id}/health-insurance`, completeData)
        console.log('Health insurance data saved to backend')
      } catch (error) {
        console.error('Failed to save health insurance data to backend:', error)
        // Continue even if backend save fails - data is in session storage
      }
    }
    
    // Save to session storage with signed status
    sessionStorage.setItem(`onboarding_${currentStep.id}_data`, JSON.stringify({
      ...formData, // Include flat structure in session storage too
      formData,
      personalInfo,
      isValid: true,
      isSigned: true,
      showReview: false,
      signed: true,
      section125Acknowledged,
      signatureData,
      completedAt: completeData.completedAt
    }))
    
    // Save progress to update controller's step data - this ensures data is available for validation
    await saveProgress(currentStep.id, completeData)
    
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
      section125Title: 'Premium Only IRS Code Section 125',
      section125Text: `By enrolling in the Section 125 plan, I understand that:
        • My premiums will be deducted from my paycheck on a pre-tax basis
        • This will reduce my taxable income and may result in lower taxes
        • My Social Security benefits may be slightly reduced due to lower reported wages
        • I cannot change or cancel my coverage during the plan year unless I experience a qualifying life event
        • Qualifying events include marriage, divorce, birth/adoption, death of dependent, or change in spouse's employment
        • I must notify HR within 30 days of any qualifying life event
        • Pre-tax deductions cannot be refunded once taken from my paycheck`,
      section125Checkbox: 'I understand and agree to the Section 125 terms above',
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
      section125Title: 'Sección 125 del Código IRS Solo Prima',
      section125Text: `Al inscribirme en el plan de la Sección 125, entiendo que:
        • Mis primas se deducirán de mi cheque de pago antes de impuestos
        • Esto reducirá mis ingresos gravables y puede resultar en impuestos más bajos
        • Mis beneficios del Seguro Social pueden reducirse ligeramente debido a salarios reportados más bajos
        • No puedo cambiar o cancelar mi cobertura durante el año del plan a menos que experimente un evento de vida calificado
        • Los eventos calificados incluyen matrimonio, divorcio, nacimiento/adopción, muerte de dependiente o cambio en el empleo del cónyuge
        • Debo notificar a RRHH dentro de 30 días de cualquier evento de vida calificado
        • Las deducciones antes de impuestos no pueden ser reembolsadas una vez tomadas de mi cheque de pago`,
      section125Checkbox: 'Entiendo y acepto los términos de la Sección 125 anteriores',
      acknowledgments: {
        planSelection: 'He revisado y seleccionado el plan de seguro de salud apropiado',
        dependentInfo: 'Toda la información de dependientes proporcionada es precisa y completa',
        coverage: 'Entiendo cuándo comenzará mi cobertura',
        changes: 'Entiendo que puedo hacer cambios durante la inscripción abierta o eventos de vida calificados'
      }
    }
  }

  const t = translations[language]

  // Show signed document preview
  console.log('HealthInsuranceStep - Render check:', {
    showSignedPreview,
    isSigned,
    showReview,
    hasPdfUrl: !!pdfUrl,
    pdfUrlLength: pdfUrl?.length,
    shouldShowPreview: showSignedPreview && isSigned && pdfUrl,
    renderingPath: showSignedPreview && isSigned && pdfUrl ? 'SIGNED_PREVIEW' :
                   showReview ? 'REVIEW_AND_SIGN' : 'FORM'
  })

  if (showSignedPreview && isSigned && pdfUrl) {
    return (
      <StepContainer errors={errors} saveStatus={saveStatus}>
        <StepContentWrapper>
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-green-600 mb-2">
                {language === 'en' ? '✓ Health Insurance Form Signed Successfully' : '✓ Formulario de Seguro de Salud Firmado Exitosamente'}
              </h2>
              <p className="text-gray-600">
                {language === 'en'
                  ? 'Your health insurance enrollment has been completed and signed. Please review the final document below.'
                  : 'Su inscripción al seguro de salud ha sido completada y firmada. Por favor revise el documento final a continuación.'}
              </p>
            </div>

            {/* Signature Details */}
            {signatureData && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-800 mb-2">
                  {language === 'en' ? 'Signature Details' : 'Detalles de la Firma'}
                </h3>
                <div className="text-sm text-green-700 space-y-1">
                  {signatureData.signedAt && (
                    <p>{language === 'en' ? 'Signed on:' : 'Firmado el:'} {new Date(signatureData.signedAt).toLocaleString()}</p>
                  )}
                  <p>{language === 'en' ? 'Document:' : 'Documento:'} Health Insurance Enrollment Form</p>
                  <p>{language === 'en' ? 'Signer:' : 'Firmante:'} {personalInfo ? `${personalInfo.firstName} ${personalInfo.lastName}` : 'Employee'}</p>
                </div>
              </div>
            )}

            {/* PDF Preview */}
            <div className="border rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-2 border-b">
                <h3 className="font-semibold">
                  {language === 'en' ? 'Signed Health Insurance Form' : 'Formulario de Seguro de Salud Firmado'}
                </h3>
              </div>
              <div style={{ height: '600px' }}>
                <PDFViewer pdfUrl={pdfUrl} height="600px" />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-between">
              <Button
                variant="outline"
                onClick={() => {
                  setShowSignedPreview(false)
                  setShowReview(true)
                }}
              >
                {language === 'en' ? 'Back to Review' : 'Volver a Revisar'}
              </Button>

              <Button
                onClick={() => {
                  // Mark step as complete and proceed
                  const completeData = {
                    ...formData,
                    personalInfo: personalInfo,
                    section125Acknowledged: section125Acknowledged,
                    isSigned: true,
                    signatureData: signatureData,
                    pdfUrl: pdfUrl,
                    completedAt: new Date().toISOString()
                  }

                  // Save to session storage
                  sessionStorage.setItem('healthInsuranceData', JSON.stringify(completeData))

                  // Mark step complete
                  markStepComplete(currentStep.id, completeData)
                }}
                className="bg-green-600 hover:bg-green-700"
              >
                {language === 'en' ? 'Complete Health Insurance' : 'Completar Seguro de Salud'}
              </Button>
            </div>
          </div>
        </StepContentWrapper>
      </StepContainer>
    )
  }

  // Show review and sign if form is valid and review is requested
  if (showReview && formData) {
    return (
      <StepContainer errors={errors} saveStatus={saveStatus}>
        <StepContentWrapper>
          <div className="space-y-6">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Heart className="h-6 w-6 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">{t.reviewTitle}</h1>
            </div>
          </div>
          
          {/* Section 125 Acknowledgment */}
          <Card className="bg-yellow-50 border-yellow-200">
            <CardHeader>
              <CardTitle className="text-lg">{t.section125Title}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm whitespace-pre-line">{t.section125Text}</p>
                <div className="flex items-start space-x-2">
                  <input
                    type="checkbox"
                    id="section125"
                    checked={section125Acknowledged}
                    onChange={(e) => setSection125Acknowledged(e.target.checked)}
                    className="mt-1"
                  />
                  <label htmlFor="section125" className="text-sm font-medium">
                    {t.section125Checkbox}
                  </label>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <ReviewAndSign
            formType="health_insurance"
            formTitle="Health Insurance Enrollment Form"
            formData={(() => {
              const reviewData = {...formData, personalInfo, section125Acknowledged}
              console.log('HealthInsuranceStep - Passing to ReviewAndSign:')
              console.log('  personalInfo object:', personalInfo)
              console.log('  personalInfo keys:', personalInfo ? Object.keys(personalInfo) : 'null')
              console.log('  personalInfo values check:', personalInfo ? {
                firstName: personalInfo.firstName || 'MISSING',
                lastName: personalInfo.lastName || 'MISSING',
                ssn: personalInfo.ssn ? '***masked***' : 'MISSING',
                address: personalInfo.address || 'MISSING',
                city: personalInfo.city || 'MISSING',
                state: personalInfo.state || 'MISSING',
                zipCode: personalInfo.zipCode || 'MISSING',
                phone: personalInfo.phone || 'MISSING',
                email: personalInfo.email || 'MISSING',
                gender: personalInfo.gender || 'MISSING',
                dateOfBirth: personalInfo.dateOfBirth || 'MISSING',
                maritalStatus: personalInfo.maritalStatus || 'MISSING',
                aptNumber: personalInfo.aptNumber || 'MISSING'
              } : 'null')
              return reviewData
            })()}
            documentName="Health Insurance Enrollment"
            signerName={personalInfo ? `${personalInfo.firstName} ${personalInfo.lastName}` : (employee?.firstName + ' ' + employee?.lastName || 'Employee')}
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
            usePDFPreview={true}
            pdfEndpoint={`${getApiUrl()}/onboarding/${employee?.id || 'test-employee'}/health-insurance/generate-pdf`}
          />
          </div>
        </StepContentWrapper>
      </StepContainer>
    )
  }

  return (
    <StepContainer errors={errors} fieldErrors={fieldErrors} saveStatus={saveStatus}>
      <StepContentWrapper>
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

        {/* Debug Section - Remove in production */}
        {process.env.NODE_ENV === 'development' && (
          <Alert className="bg-yellow-50 border-yellow-200">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800">
              <strong>Debug Info:</strong> showSignedPreview: {showSignedPreview.toString()}, isSigned: {isSigned.toString()}, hasPdfUrl: {(!!pdfUrl).toString()}
              {isSigned && pdfUrl && !showSignedPreview && (
                <Button
                  size="sm"
                  className="ml-2"
                  onClick={() => setShowSignedPreview(true)}
                >
                  Force Show Preview
                </Button>
              )}
            </AlertDescription>
          </Alert>
        )}

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
              personalInfo={personalInfo}
              language={language}
              onSave={handleFormSave}
              onValidationChange={(valid: boolean, errors?: Record<string, string>) => {
                console.log('HealthInsuranceStep - onValidationChange called, valid:', valid)
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
      </StepContentWrapper>
    </StepContainer>
  )
}