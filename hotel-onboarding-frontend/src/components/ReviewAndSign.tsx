import React, { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, FileText, Pen, AlertCircle, Eye, Loader2 } from 'lucide-react'
import SignatureCanvas from 'react-signature-canvas'
import { format } from 'date-fns'
import PDFViewer from './PDFViewer'
import axios from 'axios'

interface ReviewAndSignProps {
  formType: string
  formData: any
  title: string
  description?: string
  language: 'en' | 'es'
  onSign: (signatureData: SignatureData) => void
  onBack?: () => void
  renderPreview?: (data: any) => React.ReactNode
  signatureLabel?: string
  agreementText?: string
  federalCompliance?: {
    formName: string
    requiresWitness?: boolean
    retentionPeriod?: string
  }
  pdfEndpoint?: string // Optional endpoint to generate PDF
  usePDFPreview?: boolean // Whether to show PDF preview instead of HTML
  pdfUrl?: string | null // Direct PDF URL to display
}

export interface SignatureData {
  signature: string
  signedAt: string
  ipAddress?: string
  userAgent?: string
  formType: string
  formData: any
  certificationStatement: string
  federalCompliance?: any
}

export default function ReviewAndSign({
  formType,
  formData,
  title,
  description,
  language = 'en',
  onSign,
  onBack,
  renderPreview,
  signatureLabel,
  agreementText,
  federalCompliance,
  pdfEndpoint,
  usePDFPreview = false,
  pdfUrl
}: ReviewAndSignProps) {
  const [showSignature, setShowSignature] = useState(false)
  const [hasAgreed, setHasAgreed] = useState(false)
  const [signatureError, setSignatureError] = useState('')
  const [isSigned, setIsSigned] = useState(false)
  const [pdfData, setPdfData] = useState<string | null>(null)
  const [loadingPDF, setLoadingPDF] = useState(false)
  const [pdfError, setPdfError] = useState<string | null>(null)
  const signatureRef = useRef<SignatureCanvas>(null)

  const translations = {
    en: {
      reviewTitle: 'Review Your Information',
      reviewDescription: 'Please carefully review all information before signing',
      editButton: 'Edit Information',
      proceedToSign: 'Proceed to Sign',
      signatureTitle: 'Electronic Signature',
      signatureInstructions: 'Please sign in the box below using your mouse or touch screen',
      clearSignature: 'Clear',
      cancelSignature: 'Cancel',
      submitSignature: 'Submit Signature',
      agreementLabel: 'I certify that the information provided is true and correct',
      signatureRequired: 'Please provide your signature',
      agreementRequired: 'You must agree to the certification statement',
      signedSuccessfully: 'Document signed successfully',
      signedAt: 'Signed at',
      ipAddress: 'IP Address',
      viewDocument: 'View Document',
      federalNotice: 'This is a federal form that will be retained for',
      witnessRequired: 'This form requires witness verification'
    },
    es: {
      reviewTitle: 'Revise Su Información',
      reviewDescription: 'Por favor revise cuidadosamente toda la información antes de firmar',
      editButton: 'Editar Información',
      proceedToSign: 'Proceder a Firmar',
      signatureTitle: 'Firma Electrónica',
      signatureInstructions: 'Por favor firme en el cuadro a continuación usando su mouse o pantalla táctil',
      clearSignature: 'Limpiar',
      cancelSignature: 'Cancelar',
      submitSignature: 'Enviar Firma',
      agreementLabel: 'Certifico que la información proporcionada es verdadera y correcta',
      signatureRequired: 'Por favor proporcione su firma',
      agreementRequired: 'Debe aceptar la declaración de certificación',
      signedSuccessfully: 'Documento firmado exitosamente',
      signedAt: 'Firmado en',
      ipAddress: 'Dirección IP',
      viewDocument: 'Ver Documento',
      federalNotice: 'Este es un formulario federal que se conservará durante',
      witnessRequired: 'Este formulario requiere verificación de testigo'
    }
  }

  const t = translations[language]

  useEffect(() => {
    // Get IP address and user agent for federal compliance
    if (window.navigator) {
      // In production, you'd make an API call to get the real IP
      // For now, we'll use placeholder data
    }
    
    // Load PDF if endpoint is provided and PDF preview is enabled (skip if pdfUrl already provided)
    if (usePDFPreview && pdfEndpoint && !showSignature && !pdfUrl) {
      loadPDF()
    }
  }, [usePDFPreview, pdfEndpoint, showSignature, pdfUrl])
  
  const loadPDF = async () => {
    if (!pdfEndpoint) return
    
    setLoadingPDF(true)
    setPdfError(null)
    
    try {
      const response = await axios.post(
        pdfEndpoint,
        {
          employee_data: formData
        },
        {
          responseType: 'arraybuffer',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )
      
      // Convert response to base64
      const base64 = btoa(
        new Uint8Array(response.data).reduce(
          (data, byte) => data + String.fromCharCode(byte),
          ''
        )
      )
      
      setPdfData(base64)
    } catch (error) {
      console.error('Error loading PDF:', error)
      setPdfError('Failed to load PDF preview')
    } finally {
      setLoadingPDF(false)
    }
  }

  const handleClearSignature = () => {
    signatureRef.current?.clear()
    setSignatureError('')
  }

  const handleSubmitSignature = () => {
    if (!signatureRef.current?.isEmpty() && hasAgreed) {
      const signatureData: SignatureData = {
        signature: signatureRef.current.toDataURL(),
        signedAt: new Date().toISOString(),
        ipAddress: 'xxx.xxx.xxx.xxx', // In production, get real IP
        userAgent: window.navigator.userAgent,
        formType,
        formData,
        certificationStatement: agreementText || t.agreementLabel,
        federalCompliance: federalCompliance
      }
      
      setIsSigned(true)
      onSign(signatureData)
    } else {
      if (signatureRef.current?.isEmpty()) {
        setSignatureError(t.signatureRequired)
      } else if (!hasAgreed) {
        setSignatureError(t.agreementRequired)
      }
    }
  }

  if (isSigned) {
    return (
      <div className="space-y-6">
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            {t.signedSuccessfully}
          </AlertDescription>
        </Alert>
        
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{t.signedAt}:</span>
                <span className="font-medium">{format(new Date(), 'PPpp')}</span>
              </div>
              {federalCompliance && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    {t.federalNotice} {federalCompliance.retentionPeriod}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Review Section */}
      {!showSignature && (
        <>
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
            {description && (
              <p className="text-gray-600">{description}</p>
            )}
          </div>

          {/* Show PDF Preview or HTML Preview */}
          {usePDFPreview && (pdfUrl || pdfEndpoint) ? (
            <div className="space-y-4">
              {loadingPDF ? (
                <Card>
                  <CardContent className="py-12">
                    <div className="text-center">
                      <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-2" />
                      <p className="text-gray-600">Generating PDF preview...</p>
                    </div>
                  </CardContent>
                </Card>
              ) : pdfError ? (
                <Alert className="bg-red-50 border-red-200">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    {pdfError}
                  </AlertDescription>
                </Alert>
              ) : (pdfUrl || pdfData) ? (
                <PDFViewer
                  pdfData={pdfUrl || pdfData}
                  title={`${title} Preview`}
                  height="600px"
                  showToolbar={true}
                />
              ) : null}
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Eye className="h-5 w-5" />
                  <span>{t.reviewTitle}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                  {renderPreview && renderPreview(formData)}
                </div>
              </CardContent>
            </Card>
          )}

          {federalCompliance && (
            <Alert className="bg-blue-50 border-blue-200">
              <AlertCircle className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-800">
                <div className="space-y-1">
                  <p className="font-medium">{federalCompliance.formName}</p>
                  {federalCompliance.requiresWitness && (
                    <p className="text-sm">{t.witnessRequired}</p>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          )}

          <div className="flex gap-4">
            {onBack && (
              <Button
                variant="outline"
                onClick={onBack}
                className="flex-1"
              >
                {t.editButton}
              </Button>
            )}
            <Button
              onClick={() => setShowSignature(true)}
              className="flex-1"
            >
              <Pen className="h-4 w-4 mr-2" />
              {t.proceedToSign}
            </Button>
          </div>
        </>
      )}

      {/* Signature Section */}
      {showSignature && (
        <>
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{t.signatureTitle}</h2>
            <p className="text-gray-600">{t.signatureInstructions}</p>
          </div>

          <Card>
            <CardContent className="pt-6 space-y-6">
              {/* Signature Canvas */}
              <div className="border-2 border-gray-300 rounded-lg overflow-hidden">
                <SignatureCanvas
                  ref={signatureRef}
                  canvasProps={{
                    className: 'w-full h-48 bg-white'
                  }}
                  backgroundColor="white"
                  penColor="black"
                />
              </div>

              {/* Agreement Checkbox */}
              <div className="space-y-3">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={hasAgreed}
                    onChange={(e) => {
                      setHasAgreed(e.target.checked)
                      setSignatureError('')
                    }}
                    className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    {agreementText || t.agreementLabel}
                  </span>
                </label>
              </div>

              {/* Error Message */}
              {signatureError && (
                <Alert className="bg-red-50 border-red-200">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    {signatureError}
                  </AlertDescription>
                </Alert>
              )}

              {/* Signature Label */}
              {signatureLabel && (
                <div className="text-sm text-gray-600 text-center">
                  {signatureLabel}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4">
                <Button
                  variant="outline"
                  onClick={handleClearSignature}
                  className="flex-1"
                >
                  {t.clearSignature}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowSignature(false)}
                  className="flex-1"
                >
                  {t.cancelSignature}
                </Button>
                <Button
                  onClick={handleSubmitSignature}
                  className="flex-1"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  {t.submitSignature}
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}