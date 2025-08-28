import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import HumanTraffickingAwareness from '@/components/HumanTraffickingAwareness'
import PDFViewer from '@/components/PDFViewer'
import ReviewAndSign from '@/components/ReviewAndSign'
import { CheckCircle, GraduationCap, Shield, AlertTriangle } from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { StepContentWrapper } from '@/components/onboarding/StepContentWrapper'
import { useAutoSave } from '@/hooks/useAutoSave'

export default function TraffickingAwarenessStep({
  currentStep,
  progress,
  markStepComplete,
  saveProgress,
  language = 'en',
  employee,
  property
}: StepProps) {
  
  const [trainingComplete, setTrainingComplete] = useState(false)
  const [certificateData, setCertificateData] = useState(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [showReview, setShowReview] = useState(false)
  const [isSigned, setIsSigned] = useState(false)
  const [signatureData, setSignatureData] = useState<any>(null)
  const [previewPdfUrl, setPreviewPdfUrl] = useState<string | null>(null)

  // Auto-save data
  const autoSaveData = {
    trainingComplete,
    certificateData,
    pdfUrl,
    showReview,
    isSigned,
    signatureData
  }

  // Auto-save hook
  const { saveStatus } = useAutoSave(autoSaveData, {
    onSave: async (data) => {
    await saveProgress(currentStep.id, data)
    }
  })

  // Load existing data
  useEffect(() => {
    // Check if step is already completed
    if (progress.completedSteps.includes(currentStep.id)) {
      setTrainingComplete(true)
    }
    
    // Load saved data from session storage
    const savedData = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        if (parsed.trainingComplete) {
          setTrainingComplete(true)
        }
        if (parsed.certificateData) {
          setCertificateData(parsed.certificateData)
        }
        if (parsed.pdfUrl) {
          setPdfUrl(parsed.pdfUrl)
        }
        if (parsed.isSigned) {
          setIsSigned(true)
        }
        if (parsed.signatureData) {
          setSignatureData(parsed.signatureData)
        }
      } catch (e) {
        console.error('Failed to load saved trafficking awareness data:', e)
      }
    }
  }, [currentStep.id, progress.completedSteps])

  const handleTrainingComplete = async (data: any) => {
    setTrainingComplete(true)
    setCertificateData(data)
    
    // Load preview PDF before showing review
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || ''}/api/onboarding/${employee?.id}/human-trafficking/preview`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        }
      )
      
      if (response.ok) {
        const result = await response.json()
        if (result.data?.pdf) {
          setPreviewPdfUrl(result.data.pdf)
        }
      }
    } catch (error) {
      console.error('Failed to load preview:', error)
    }
    
    setShowReview(true)  // Show review screen
    
    // Save training completion data but don't mark step as complete yet
    const stepData = {
      trainingComplete: true,
      certificate: data,
      completedAt: new Date().toISOString(),
      showReview: true
    }
    
    await saveProgress(currentStep.id, stepData)
  }

  const handleSignatureComplete = async (signatureInfo: any) => {
    try {
      console.log('Generating signed Human Trafficking certificate...')
      
      // Generate final signed PDF
      const response = await fetch(
        `${import.meta.env.VITE_API_URL || ''}/api/onboarding/${employee?.id}/human-trafficking/generate-pdf`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            employee_data: {
              firstName: employee?.firstName || employee?.name?.split(' ')[0] || 'Employee',
              lastName: employee?.lastName || employee?.name?.split(' ')[1] || '',
              name: `${employee?.firstName || ''} ${employee?.lastName || ''}`.trim() || employee?.name || 'Employee',
              completionDate: new Date().toISOString(),
              ...employee
            },
            signature_data: {
              name: signatureInfo.name,
              timestamp: signatureInfo.timestamp,
              ipAddress: signatureInfo.ipAddress,
              signatureImage: signatureInfo.signatureImage,
              signatureId: `HT-${Date.now()}`
            }
          })
        }
      )
      
      if (response.ok) {
        const result = await response.json()
        console.log('Human Trafficking PDF response:', result)
        
        if (result.data?.pdf) {
          setPdfUrl(result.data.pdf)
          setIsSigned(true)
          setSignatureData(signatureInfo)
          setShowReview(false)
          
          // Now mark the step as complete
          const completeData = {
            trainingComplete: true,
            certificate: certificateData,
            pdfUrl: result.data.pdf,
            pdfFilename: result.data.filename,
            isSigned: true,
            signatureData: signatureInfo,
            completedAt: new Date().toISOString()
          }
          
          await markStepComplete(currentStep.id, completeData)
          console.log('Human Trafficking certificate signed and saved successfully')
        } else {
          console.warn('Human Trafficking PDF response missing PDF data')
        }
      } else {
        console.error('Human Trafficking PDF generation failed:', response.status, response.statusText)
      }
    } catch (error) {
      console.error('Failed to generate Human Trafficking PDF:', error)
    }
  }

  // Callback for ReviewAndSign onSign
  const handleOnSign = (signatureInfo: any) => {
    // Call our existing signature complete handler
    handleSignatureComplete({
      name: signatureInfo.formData?.name || `${employee?.firstName || ''} ${employee?.lastName || ''}`.trim() || employee?.name || 'Employee',
      timestamp: signatureInfo.signedAt,
      ipAddress: signatureInfo.ipAddress || window.location.hostname,
      signatureImage: signatureInfo.signature,
      ...signatureInfo
    })
  }

  const translations = {
    en: {
      title: 'Human Trafficking Awareness Training',
      description: 'Complete this mandatory training to learn about human trafficking awareness and your role in recognizing and reporting suspicious activities in the hospitality industry.',
      federalRequirement: 'Federal Requirement:',
      federalNotice: 'This training is mandatory for all hospitality employees under federal anti-trafficking laws and industry best practices.',
      completionMessage: 'Human trafficking awareness training completed successfully. Certificate generated.',
      trainingModule: 'Training Module',
      estimatedTime: 'Estimated time: 8-10 minutes',
      trainingCertificate: 'Training Certificate',
      certificateDescription: 'Your Human Trafficking Awareness training certificate'
    },
    es: {
      title: 'Capacitación sobre Concientización del Tráfico Humano',
      description: 'Complete esta capacitación obligatoria para aprender sobre la concientización del tráfico humano y su papel en el reconocimiento y reporte de actividades sospechosas en la industria hotelera.',
      federalRequirement: 'Requisito Federal:',
      federalNotice: 'Esta capacitación es obligatoria para todos los empleados de hospitalidad bajo las leyes federales contra el tráfico y las mejores prácticas de la industria.',
      completionMessage: 'Capacitación sobre concientización del tráfico humano completada exitosamente. Certificado generado.',
      trainingModule: 'Módulo de Capacitación',
      estimatedTime: 'Tiempo estimado: 8-10 minutos',
      trainingCertificate: 'Certificado de Capacitación',
      certificateDescription: 'Su certificado de capacitación sobre concientización del tráfico humano'
    }
  }

  const t = translations[language]

  return (
    <StepContainer saveStatus={saveStatus}>
      <StepContentWrapper>
        <div className="space-y-6">
        {/* Step Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <GraduationCap className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          </div>
          <p className="text-gray-600 max-w-3xl mx-auto">{t.description}</p>
        </div>

        {/* Federal Requirement Notice */}
        <Alert className="bg-red-50 border-red-200">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>{t.federalRequirement}</strong> {t.federalNotice}
          </AlertDescription>
        </Alert>

        {/* Completion Status */}
        {trainingComplete && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t.completionMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Show different states based on progress */}
        {isSigned && pdfUrl ? (
          /* Show signed certificate */
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span>{t.trainingCertificate}</span>
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">{t.certificateDescription}</p>
            </CardHeader>
            <CardContent>
              <PDFViewer 
                pdfData={pdfUrl} 
                height="600px" 
                title={t.trainingCertificate}
              />
            </CardContent>
          </Card>
        ) : trainingComplete && showReview ? (
          /* Review and Sign */
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-blue-600" />
                <span>Review and Sign Certificate</span>
              </CardTitle>
              <p className="text-sm text-gray-600 mt-1">Review your training certificate and provide your signature</p>
            </CardHeader>
            <CardContent>
              <ReviewAndSign
                formType="trafficking-awareness"
                formData={certificateData}
                title="Human Trafficking Awareness Certificate"
                description="Review your training certificate before signing"
                onSign={handleOnSign}
                language={language}
                usePDFPreview={true}
                pdfUrl={previewPdfUrl}
                federalCompliance={{
                  formName: 'Human Trafficking Awareness Training',
                  retentionPeriod: '1 year'
                }}
              />
            </CardContent>
          </Card>
        ) : (
          /* Training Module Card */
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5 text-blue-600" />
                <span>{t.trainingModule}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <HumanTraffickingAwareness
                onTrainingComplete={handleTrainingComplete}
                language={language}
              />
            </CardContent>
          </Card>
        )}

        {/* Time Estimate */}
        <div className="text-center text-sm text-gray-500">
          <p>{t.estimatedTime}</p>
        </div>
        </div>
      </StepContentWrapper>
    </StepContainer>
  )
}