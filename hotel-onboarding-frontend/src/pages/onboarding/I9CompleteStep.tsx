import React, { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, FileText, Upload, Camera, Globe } from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import I9Section1FormClean from '@/components/I9Section1FormClean'
import I9SupplementA from '@/components/I9SupplementA'
import DocumentUploadEnhanced from './DocumentUploadEnhanced'
import ReviewAndSign from '@/components/ReviewAndSign'
import { useAutoSave } from '@/hooks/useAutoSave'
import { useStepValidation } from '@/hooks/useStepValidation'
import { i9Section1Validator } from '@/utils/stepValidators'
import { generateMappedI9Pdf } from '@/utils/i9PdfGeneratorMapped'
import axios from 'axios'

export default function I9CompleteStep({
  currentStep,
  progress,
  markStepComplete,
  saveProgress,
  language = 'en',
  employee,
  property
}: StepProps) {
  // State for tabs
  const [activeTab, setActiveTab] = useState('form')
  const [formData, setFormData] = useState<any>({})
  const [supplementsData, setSupplementsData] = useState<any>(null)
  const [documentsData, setDocumentsData] = useState<any>(null)
  
  // State for completion tracking
  const [formComplete, setFormComplete] = useState(false)
  const [supplementsComplete, setSupplementsComplete] = useState(false)
  const [documentsComplete, setDocumentsComplete] = useState(false)
  const [isSigned, setIsSigned] = useState(false)
  
  // State for supplements
  const [needsSupplements, setNeedsSupplements] = useState<'none' | 'translator'>('none')
  
  // State for PDF
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false)
  
  // Validation hook
  const { errors, fieldErrors, validate } = useStepValidation(i9Section1Validator)
  
  // Auto-save data
  const autoSaveData = {
    activeTab,
    formData,
    supplementsData,
    documentsData,
    formComplete,
    supplementsComplete,
    documentsComplete,
    needsSupplements,
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
    // Check if already completed
    if (progress.completedSteps.includes(currentStep.id)) {
      setIsSigned(true)
      setFormComplete(true)
      setSupplementsComplete(true)
      setDocumentsComplete(true)
      setActiveTab('preview')
    }
    
    // Load saved data
    const savedData = sessionStorage.getItem(`onboarding_${currentStep.id}_data`)
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        if (parsed.formData) setFormData(parsed.formData)
        if (parsed.supplementsData) setSupplementsData(parsed.supplementsData)
        if (parsed.documentsData) setDocumentsData(parsed.documentsData)
        if (parsed.needsSupplements) setNeedsSupplements(parsed.needsSupplements)
        if (parsed.formComplete) setFormComplete(parsed.formComplete)
        if (parsed.supplementsComplete) setSupplementsComplete(parsed.supplementsComplete)
        if (parsed.documentsComplete) setDocumentsComplete(parsed.documentsComplete)
      } catch (e) {
        console.error('Failed to parse saved data:', e)
      }
    }
    
    // Auto-fill from personal info
    const personalInfoData = sessionStorage.getItem('onboarding_personal-info_data')
    if (personalInfoData && !formData.last_name) {
      try {
        const parsedData = JSON.parse(personalInfoData)
        const personalInfo = parsedData.personalInfo || parsedData || {}
        
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
        
        setFormData(mappedData)
      } catch (e) {
        console.error('Failed to parse personal info data:', e)
      }
    }
  }, [currentStep.id, progress.completedSteps])
  
  // Tab configuration
  const tabs = [
    { 
      id: 'form', 
      label: language === 'es' ? 'Llenar Formulario' : 'Fill Form',
      icon: <FileText className="h-4 w-4" />,
      enabled: true,
      complete: formComplete
    },
    { 
      id: 'supplements', 
      label: language === 'es' ? 'Suplementos' : 'Supplements',
      icon: <Globe className="h-4 w-4" />,
      enabled: formComplete,
      complete: supplementsComplete
    },
    { 
      id: 'documents', 
      label: language === 'es' ? 'Cargar Documentos' : 'Upload Documents',
      icon: <Upload className="h-4 w-4" />,
      enabled: formComplete && supplementsComplete,
      complete: documentsComplete
    },
    { 
      id: 'preview', 
      label: language === 'es' ? 'Revisar y Firmar' : 'Preview & Sign',
      icon: <CheckCircle className="h-4 w-4" />,
      enabled: formComplete && supplementsComplete && documentsComplete,
      complete: isSigned
    }
  ]
  
  // Handlers
  const handleFormComplete = async (data: any) => {
    setFormData(data)
    setFormComplete(true)
    await saveProgress(currentStep.id, { formData: data, formComplete: true })
    setActiveTab('supplements')
  }
  
  const handleSupplementsComplete = async () => {
    setSupplementsComplete(true)
    await saveProgress(currentStep.id, { supplementsComplete: true })
    setActiveTab('documents')
  }
  
  const handleDocumentsComplete = async (data: any) => {
    setDocumentsData(data)
    setDocumentsComplete(true)
    
    // Store extracted data for Section 2
    if (data.extractedData) {
      sessionStorage.setItem('i9_section2_data', JSON.stringify(data.extractedData))
    }
    
    await saveProgress(currentStep.id, { documentsData: data, documentsComplete: true })
    
    // Generate PDF before showing preview
    await generateCompletePdf(data)
    
    setActiveTab('preview')
  }
  
  const generateCompletePdf = async (documents?: any) => {
    setIsGeneratingPdf(true)
    try {
      // Prepare complete form data including Section 2 info from documents
      const completeFormData = {
        ...formData,
        // Add Section 2 data from document extraction
        section2: documents?.extractedData ? {
          documents: documents.extractedData,
          documentVerificationDate: new Date().toISOString()
        } : null,
        // Add supplement data if applicable
        supplementA: needsSupplements === 'translator' ? supplementsData : null
      }
      
      // Generate PDF with all sections
      const pdfBase64 = await generateMappedI9Pdf(completeFormData)
      
      // Save PDF to backend if employeeId is available
      if (employee?.id) {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
          const response = await axios.post(
            `${apiUrl}/api/onboarding/${employee.id}/i9-complete/generate-pdf`,
            {
              section1Data: formData,
              supplementAData: needsSupplements === 'translator' ? supplementsData : null,
              section2Data: documents?.extractedData || null
            }
          )
          
          if (response.data.pdf_url) {
            setPdfUrl(response.data.pdf_url)
          }
        } catch (error) {
          console.error('Error saving PDF to backend:', error)
        }
      }
      
      // Convert base64 to blob URL for preview
      const base64ToBlob = (base64: string, contentType: string): Blob => {
        const byteCharacters = atob(base64)
        const byteArrays = []
        
        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
          const slice = byteCharacters.slice(offset, offset + 512)
          const byteNumbers = new Array(slice.length)
          for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i)
          }
          const byteArray = new Uint8Array(byteNumbers)
          byteArrays.push(byteArray)
        }
        
        return new Blob(byteArrays, { type: contentType })
      }
      
      const pdfBlob = base64ToBlob(pdfBase64, 'application/pdf')
      const url = URL.createObjectURL(pdfBlob)
      setPdfUrl(url)
      
    } catch (error) {
      console.error('Error generating PDF:', error)
      // Continue without PDF preview
    } finally {
      setIsGeneratingPdf(false)
    }
  }

  const handleSign = async (signatureData: any) => {
    const completeData = {
      formData,
      supplementsData,
      documentsData,
      signed: true,
      signatureData,
      completedAt: new Date().toISOString()
    }
    
    setIsSigned(true)
    await markStepComplete(currentStep.id, completeData)
  }
  
  const renderFormPreview = (data: any) => {
    return (
      <div className="space-y-6">
        {/* Section 1 Data */}
        <div>
          <h3 className="font-semibold text-lg mb-3">Section 1 - Employee Information</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Name</label>
              <p className="text-gray-900">{data.first_name} {data.middle_initial} {data.last_name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Date of Birth</label>
              <p className="text-gray-900">{data.date_of_birth}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">SSN</label>
              <p className="text-gray-900">***-**-{data.ssn?.slice(-4) || '****'}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Citizenship Status</label>
              <p className="text-gray-900">{data.citizenship_status?.replace('_', ' ')}</p>
            </div>
          </div>
        </div>
        
        {/* Supplements Data */}
        {supplementsData && needsSupplements === 'translator' && (
          <div>
            <h3 className="font-semibold text-lg mb-3">Supplement A - Preparer/Translator</h3>
            <p className="text-gray-600">A translator assisted with completing this form.</p>
          </div>
        )}
        
        {/* Section 2 Preview (AI-extracted) */}
        {documentsData?.extractedData && (
          <div>
            <h3 className="font-semibold text-lg mb-3">Section 2 - Employer Review (Preview)</h3>
            <Alert className="bg-blue-50 border-blue-200 mb-3">
              <AlertDescription className="text-blue-800">
                The following information was extracted from your documents and will be verified by your manager.
              </AlertDescription>
            </Alert>
            <div className="grid grid-cols-2 gap-4">
              {documentsData.extractedData.map((doc: any, idx: number) => (
                <div key={idx}>
                  <label className="text-sm font-medium text-gray-600">{doc.documentType}</label>
                  <p className="text-gray-900">
                    {doc.documentNumber} 
                    {doc.expirationDate && ` (Exp: ${doc.expirationDate})`}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }
  
  const translations = {
    en: {
      title: 'Employment Eligibility Verification (I-9)',
      description: 'Complete all sections of Form I-9 including document upload',
      completionMessage: 'Form I-9 has been completed and submitted for manager review.'
    },
    es: {
      title: 'Verificación de Elegibilidad de Empleo (I-9)',
      description: 'Complete todas las secciones del Formulario I-9 incluyendo carga de documentos',
      completionMessage: 'El Formulario I-9 ha sido completado y enviado para revisión del gerente.'
    }
  }
  
  const t = translations[language]
  
  return (
    <StepContainer errors={errors} fieldErrors={fieldErrors} saveStatus={saveStatus}>
      <div className="space-y-6">
        {/* Header */}
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
          <TabsList className="grid w-full grid-cols-4 mb-6">
            {tabs.map(tab => (
              <TabsTrigger 
                key={tab.id}
                value={tab.id}
                disabled={!tab.enabled}
                className="flex items-center space-x-2"
              >
                {tab.icon}
                <span className="hidden sm:inline">{tab.label}</span>
                {tab.complete && <CheckCircle className="h-3 w-3 text-green-600 ml-1" />}
              </TabsTrigger>
            ))}
          </TabsList>
          
          {/* Form Tab */}
          <TabsContent value="form" className="space-y-6">
            <I9Section1FormClean
              onComplete={handleFormComplete}
              initialData={formData}
              language={language}
              employeeId={employee?.id}
              showPreview={false}
            />
          </TabsContent>
          
          {/* Supplements Tab */}
          <TabsContent value="supplements" className="space-y-6">
            <div className="space-y-4">
              <h2 className="text-lg font-semibold">
                {language === 'es' ? '¿Necesita Suplementos?' : 'Do You Need Supplements?'}
              </h2>
              
              <Alert className="bg-blue-50 border-blue-200">
                <AlertDescription className="text-blue-800">
                  {language === 'es' 
                    ? 'La mayoría de los empleados pueden omitir esta sección. Solo es necesaria si alguien le ayudó a traducir o completar el formulario.'
                    : 'Most employees can skip this section. It\'s only needed if someone helped translate or complete your form.'}
                </AlertDescription>
              </Alert>
              
              <div className="space-y-3">
                <label className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="supplements"
                    value="none"
                    checked={needsSupplements === 'none'}
                    onChange={() => setNeedsSupplements('none')}
                    className="h-4 w-4"
                  />
                  <div>
                    <p className="font-medium">
                      {language === 'es' ? 'No necesito suplementos' : 'I don\'t need supplements'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {language === 'es' 
                        ? 'Completé el formulario yo mismo'
                        : 'I completed the form myself'}
                    </p>
                  </div>
                </label>
                
                <label className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="radio"
                    name="supplements"
                    value="translator"
                    checked={needsSupplements === 'translator'}
                    onChange={() => setNeedsSupplements('translator')}
                    className="h-4 w-4"
                  />
                  <div>
                    <p className="font-medium">
                      {language === 'es' ? 'Alguien me ayudó' : 'Someone helped me'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {language === 'es' 
                        ? 'Un traductor o preparador me ayudó'
                        : 'A translator or preparer helped me'}
                    </p>
                  </div>
                </label>
              </div>
              
              {needsSupplements === 'translator' && (
                <div className="mt-6">
                  <I9SupplementA
                    initialData={supplementsData || {}}
                    language={language}
                    onComplete={(data) => {
                      setSupplementsData(data)
                      handleSupplementsComplete()
                    }}
                    onSkip={() => {
                      setNeedsSupplements('none')
                      handleSupplementsComplete()
                    }}
                    onBack={() => setNeedsSupplements('none')}
                  />
                </div>
              )}
              
              {needsSupplements === 'none' && (
                <div className="flex justify-end mt-6">
                  <button
                    onClick={handleSupplementsComplete}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {language === 'es' ? 'Continuar' : 'Continue'}
                  </button>
                </div>
              )}
            </div>
          </TabsContent>
          
          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-6">
            <DocumentUploadEnhanced
              onComplete={handleDocumentsComplete}
              language={language}
            />
          </TabsContent>
          
          {/* Preview Tab */}
          <TabsContent value="preview" className="space-y-6">
            {isGeneratingPdf ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600">
                    {language === 'es' ? 'Generando PDF...' : 'Generating PDF...'}
                  </span>
                </div>
              </div>
            ) : (
              <ReviewAndSign
                formType="i9-complete"
                formData={{ ...formData, supplementsData, documentsData }}
                title={language === 'es' ? 'Revisar I-9 Completo' : 'Review Complete I-9'}
                description={language === 'es' 
                  ? 'Revise toda la información antes de firmar'
                  : 'Review all information before signing'}
                language={language}
                onSign={handleSign}
                onBack={() => setActiveTab('documents')}
                renderPreview={renderFormPreview}
                usePDFPreview={true}
                pdfUrl={pdfUrl}
                federalCompliance={{
                  formName: 'Form I-9, Employment Eligibility Verification',
                  retentionPeriod: '3 years after hire or 1 year after termination (whichever is later)',
                  requiresWitness: false
                }}
                agreementText={language === 'es'
                  ? 'Atestiguo, bajo pena de perjurio, que la información proporcionada es verdadera y correcta.'
                  : 'I attest, under penalty of perjury, that the information provided is true and correct.'}
              />
            )}
          </TabsContent>
        </Tabs>
      </div>
    </StepContainer>
  )
}