import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { 
  CheckCircle, 
  Upload, 
  FileText, 
  Camera, 
  Shield, 
  AlertTriangle,
  Info,
  CreditCard,
  BookOpen,
  Car,
  Loader2,
  X
} from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import axios from 'axios'

interface DocumentOption {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  category: 'listA' | 'listB' | 'listC'
  apiType: string // For backend processing
}

interface UploadedDocument {
  id: string
  file: File
  type: string
  status: 'uploading' | 'processing' | 'complete' | 'error'
  extractedData?: {
    documentNumber?: string
    expirationDate?: string
    issuingAuthority?: string
  }
  error?: string
}

const DOCUMENT_OPTIONS: DocumentOption[] = [
  // List A
  {
    id: 'us-passport',
    title: 'U.S. Passport',
    description: 'Passport or Passport Card',
    icon: <BookOpen className="h-5 w-5" />,
    category: 'listA',
    apiType: 'us_passport'
  },
  {
    id: 'green-card',
    title: 'Permanent Resident Card',
    description: 'Green Card (I-551)',
    icon: <CreditCard className="h-5 w-5" />,
    category: 'listA',
    apiType: 'permanent_resident_card'
  },
  // List B
  {
    id: 'drivers-license',
    title: "Driver's License",
    description: 'State-issued ID',
    icon: <Car className="h-5 w-5" />,
    category: 'listB',
    apiType: 'drivers_license'
  },
  // List C
  {
    id: 'ssn-card',
    title: 'Social Security Card',
    description: 'Unrestricted SSN card',
    icon: <CreditCard className="h-5 w-5" />,
    category: 'listC',
    apiType: 'social_security_card'
  }
]

export default function DocumentUploadEnhanced({
  onComplete,
  language = 'en'
}: {
  onComplete: (data: any) => void
  language?: 'en' | 'es'
}) {
  const [documentChoice, setDocumentChoice] = useState<'passport' | 'dl_ssn' | 'other'>('')
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  
  const translations = {
    en: {
      title: 'Upload Documents',
      subtitle: 'Upload your documents for I-9 verification',
      question: 'Which documents do you have?',
      option1: 'U.S. Passport or Green Card',
      option1Desc: 'One document establishes both identity and work authorization',
      option2: 'Driver\'s License',
      option2Desc: 'You\'ll also need to upload your Social Security card',
      option3: 'Other documents',
      option3Desc: 'See all acceptable document options',
      upload: 'Upload',
      processing: 'Processing your document...',
      extracting: 'Extracting information...',
      complete: 'Processing complete!',
      error: 'Error processing document',
      retry: 'Retry',
      remove: 'Remove',
      continue: 'Continue',
      documentNumber: 'Document Number',
      expires: 'Expires',
      issuer: 'Issuing Authority'
    },
    es: {
      title: 'Cargar Documentos',
      subtitle: 'Cargue sus documentos para verificación I-9',
      question: '¿Qué documentos tiene?',
      option1: 'Pasaporte de EE.UU. o Tarjeta Verde',
      option1Desc: 'Un documento establece identidad y autorización de trabajo',
      option2: 'Licencia de Conducir',
      option2Desc: 'También necesitará cargar su tarjeta de Seguro Social',
      option3: 'Otros documentos',
      option3Desc: 'Ver todas las opciones de documentos aceptables',
      upload: 'Cargar',
      processing: 'Procesando su documento...',
      extracting: 'Extrayendo información...',
      complete: '¡Procesamiento completo!',
      error: 'Error al procesar documento',
      retry: 'Reintentar',
      remove: 'Eliminar',
      continue: 'Continuar',
      documentNumber: 'Número de Documento',
      expires: 'Vence',
      issuer: 'Autoridad Emisora'
    }
  }
  
  const t = translations[language]
  
  // Process document with AI
  const processDocument = async (file: File, docType: string) => {
    const docId = `${docType}-${Date.now()}`
    
    // Add to uploaded documents
    setUploadedDocuments(prev => [...prev, {
      id: docId,
      file,
      type: docType,
      status: 'uploading'
    }])
    
    try {
      // Create FormData
      const formData = new FormData()
      formData.append('file', file)
      formData.append('document_type', docType)
      
      // Update status to processing
      setUploadedDocuments(prev => prev.map(doc => 
        doc.id === docId ? { ...doc, status: 'processing' } : doc
      ))
      
      // Call backend API
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await axios.post(
        `${apiUrl}/api/documents/process`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      // Update with extracted data
      setUploadedDocuments(prev => prev.map(doc => 
        doc.id === docId ? {
          ...doc,
          status: 'complete',
          extractedData: response.data
        } : doc
      ))
      
    } catch (error) {
      console.error('Document processing error:', error)
      setUploadedDocuments(prev => prev.map(doc => 
        doc.id === docId ? {
          ...doc,
          status: 'error',
          error: 'Failed to process document'
        } : doc
      ))
    }
  }
  
  // Handle file selection
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>, docType: string) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    // Validate file type
    if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
      alert('Please upload an image or PDF file')
      return
    }
    
    // Process the document
    setIsProcessing(true)
    await processDocument(file, docType)
    setIsProcessing(false)
  }
  
  // Check if ready to continue
  const isReady = () => {
    if (documentChoice === 'passport') {
      return uploadedDocuments.some(doc => 
        (doc.type === 'us_passport' || doc.type === 'permanent_resident_card') && 
        doc.status === 'complete'
      )
    } else if (documentChoice === 'dl_ssn') {
      const hasLicense = uploadedDocuments.some(doc => 
        doc.type === 'drivers_license' && doc.status === 'complete'
      )
      const hasSSN = uploadedDocuments.some(doc => 
        doc.type === 'social_security_card' && doc.status === 'complete'
      )
      return hasLicense && hasSSN
    }
    return false
  }
  
  // Handle completion
  const handleComplete = () => {
    const extractedData = uploadedDocuments
      .filter(doc => doc.status === 'complete')
      .map(doc => ({
        documentType: doc.type,
        ...doc.extractedData
      }))
    
    onComplete({ 
      uploadedDocuments: uploadedDocuments.map(doc => ({
        type: doc.type,
        fileName: doc.file.name
      })),
      extractedData 
    })
  }
  
  return (
    <div className="space-y-6">
      {/* Document Choice */}
      {!documentChoice && (
        <Card>
          <CardHeader>
            <CardTitle>{t.question}</CardTitle>
          </CardHeader>
          <CardContent>
            <RadioGroup onValueChange={(value: any) => setDocumentChoice(value)}>
              <div className="space-y-3">
                <label className="flex items-start space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <RadioGroupItem value="passport" className="mt-1" />
                  <div className="flex-1">
                    <p className="font-medium">{t.option1}</p>
                    <p className="text-sm text-gray-600">{t.option1Desc}</p>
                  </div>
                </label>
                
                <label className="flex items-start space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <RadioGroupItem value="dl_ssn" className="mt-1" />
                  <div className="flex-1">
                    <p className="font-medium">{t.option2}</p>
                    <p className="text-sm text-gray-600">{t.option2Desc}</p>
                  </div>
                </label>
                
                <label className="flex items-start space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                  <RadioGroupItem value="other" className="mt-1" />
                  <div className="flex-1">
                    <p className="font-medium">{t.option3}</p>
                    <p className="text-sm text-gray-600">{t.option3Desc}</p>
                  </div>
                </label>
              </div>
            </RadioGroup>
          </CardContent>
        </Card>
      )}
      
      {/* Document Upload */}
      {documentChoice === 'passport' && (
        <Card>
          <CardHeader>
            <CardTitle>{t.option1}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Passport Upload */}
            <div className="p-4 border-2 border-dashed rounded-lg">
              <div className="text-center">
                <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <label htmlFor="passport-upload" className="cursor-pointer">
                  <span className="text-blue-600 hover:text-blue-700 font-medium">
                    {t.upload} U.S. Passport
                  </span>
                  <input
                    id="passport-upload"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => handleFileSelect(e, 'us_passport')}
                    className="hidden"
                    disabled={isProcessing}
                  />
                </label>
              </div>
            </div>
            
            {/* Green Card Upload */}
            <div className="p-4 border-2 border-dashed rounded-lg">
              <div className="text-center">
                <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <label htmlFor="greencard-upload" className="cursor-pointer">
                  <span className="text-blue-600 hover:text-blue-700 font-medium">
                    {t.upload} Green Card
                  </span>
                  <input
                    id="greencard-upload"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => handleFileSelect(e, 'permanent_resident_card')}
                    className="hidden"
                    disabled={isProcessing}
                  />
                </label>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {documentChoice === 'dl_ssn' && (
        <div className="space-y-4">
          {/* Driver's License */}
          <Card>
            <CardHeader>
              <CardTitle>Driver's License</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-4 border-2 border-dashed rounded-lg">
                <div className="text-center">
                  <Car className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <label htmlFor="dl-upload" className="cursor-pointer">
                    <span className="text-blue-600 hover:text-blue-700 font-medium">
                      {t.upload} Driver's License
                    </span>
                    <input
                      id="dl-upload"
                      type="file"
                      accept="image/*,.pdf"
                      onChange={(e) => handleFileSelect(e, 'drivers_license')}
                      className="hidden"
                      disabled={isProcessing}
                    />
                  </label>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Social Security Card */}
          <Card>
            <CardHeader>
              <CardTitle>Social Security Card</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="p-4 border-2 border-dashed rounded-lg">
                <div className="text-center">
                  <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <label htmlFor="ssn-upload" className="cursor-pointer">
                    <span className="text-blue-600 hover:text-blue-700 font-medium">
                      {t.upload} Social Security Card
                    </span>
                    <input
                      id="ssn-upload"
                      type="file"
                      accept="image/*,.pdf"
                      onChange={(e) => handleFileSelect(e, 'social_security_card')}
                      className="hidden"
                      disabled={isProcessing}
                    />
                  </label>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* Processing Status */}
      {uploadedDocuments.map(doc => (
        <Card key={doc.id} className="relative">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileText className="h-5 w-5 text-gray-400" />
                <div>
                  <p className="font-medium">{doc.file.name}</p>
                  {doc.status === 'uploading' && (
                    <p className="text-sm text-gray-600">{t.upload}...</p>
                  )}
                  {doc.status === 'processing' && (
                    <p className="text-sm text-blue-600">{t.extracting}</p>
                  )}
                  {doc.status === 'complete' && doc.extractedData && (
                    <div className="text-sm text-green-600">
                      {doc.extractedData.documentNumber && (
                        <p>{t.documentNumber}: {doc.extractedData.documentNumber}</p>
                      )}
                      {doc.extractedData.expirationDate && (
                        <p>{t.expires}: {doc.extractedData.expirationDate}</p>
                      )}
                    </div>
                  )}
                  {doc.status === 'error' && (
                    <p className="text-sm text-red-600">{doc.error}</p>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {doc.status === 'uploading' && (
                  <Loader2 className="h-4 w-4 animate-spin text-gray-400" />
                )}
                {doc.status === 'processing' && (
                  <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                )}
                {doc.status === 'complete' && (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                )}
                {doc.status === 'error' && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setUploadedDocuments(prev => prev.filter(d => d.id !== doc.id))
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
            
            {doc.status === 'processing' && (
              <Progress value={66} className="mt-2" />
            )}
          </CardContent>
        </Card>
      ))}
      
      {/* Continue Button */}
      {documentChoice && (
        <div className="flex justify-end">
          <Button 
            onClick={handleComplete}
            disabled={!isReady() || isProcessing}
          >
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t.processing}
              </>
            ) : (
              t.continue
            )}
          </Button>
        </div>
      )}
    </div>
  )
}