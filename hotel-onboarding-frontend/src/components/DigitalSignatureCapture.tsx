import React, { useRef, useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { PenTool, RotateCcw, Check, Shield, Clock, User, FileText, AlertCircle } from 'lucide-react'

interface DigitalSignatureData {
  signatureType: 'employee_final' | 'employee_i9' | 'employee_w4' | 'employee_policies' | 'manager_i9' | 'manager_approval'
  signatureData: string // SVG or base64 image data
  signedByName: string
  signedByTitle?: string
  ipAddress?: string
  timestamp: string
  documentName: string
  acknowledgments: string[]
  termsAccepted: boolean
  identityVerified: boolean
}

interface DigitalSignatureCaptureProps {
  signatureType: DigitalSignatureData['signatureType']
  documentName: string
  signerName: string
  signerTitle?: string
  acknowledgments: string[]
  requireIdentityVerification?: boolean
  language: 'en' | 'es'
  onSignatureComplete: (signatureData: DigitalSignatureData) => void
  onCancel: () => void
}

export default function DigitalSignatureCapture({
  signatureType,
  documentName,
  signerName,
  signerTitle,
  acknowledgments,
  requireIdentityVerification = false,
  language,
  onSignatureComplete,
  onCancel
}: DigitalSignatureCaptureProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [signatureData, setSignatureData] = useState<string>('')
  const [typedName, setTypedName] = useState(signerName)
  const [signatureMethod, setSignatureMethod] = useState<'draw' | 'type'>('draw')
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [identityVerified, setIdentityVerified] = useState(false)
  const [acknowledgementsChecked, setAcknowledgementsChecked] = useState<boolean[]>(
    new Array(acknowledgments.length).fill(false)
  )
  const [ipAddress, setIpAddress] = useState('')
  const [canSign, setCanSign] = useState(false)

  const t = (key: string) => {
    const translations: Record<string, Record<string, string>> = {
      en: {
        'digital_signature': 'Digital Signature',
        'signature_required': 'Your signature is required to complete this document',
        'draw_signature': 'Draw Signature',
        'type_signature': 'Type Signature',
        'draw_instruction': 'Use your mouse or finger to draw your signature in the box below',
        'type_instruction': 'Type your full legal name as it appears on your identification',
        'clear': 'Clear',
        'your_name': 'Your Full Legal Name',
        'acknowledgments': 'Acknowledgments',
        'legal_notices': 'Legal Notices and Consents',
        'electronic_signature_consent': 'I consent to the use of electronic signatures and understand that they have the same legal effect as handwritten signatures.',
        'identity_verification': 'I verify that I am the person identified above and am authorized to sign this document.',
        'document_accuracy': 'I certify that all information provided in this document is true and accurate to the best of my knowledge.',
        'terms_conditions': 'I have read, understood, and agree to be bound by the terms and conditions of this agreement.',
        'sign_document': 'Sign Document',
        'cancel': 'Cancel',
        'signature_timestamp': 'Signature Timestamp',
        'signature_method': 'Signature Method: {method}',
        'ip_address': 'IP Address: {ip}',
        'legal_binding': 'This signature is legally binding',
        'esign_act_notice': 'Electronic Signature Act Notice: By signing electronically, you agree that your electronic signature has the same legal effect as a handwritten signature.',
        'document_retention': 'A copy of this signed document will be retained for legal and compliance purposes.',
        'signature_verification': 'Signature Verification',
        'all_acknowledgments_required': 'All acknowledgments must be checked to proceed.',
        'signature_required_error': 'A signature is required to complete this document.',
        'processing': 'Processing signature...'
      },
      es: {
        'digital_signature': 'Firma Digital',
        'signature_required': 'Su firma es requerida para completar este documento',
        'draw_signature': 'Dibujar Firma',
        'type_signature': 'Escribir Firma',
        'draw_instruction': 'Use su mouse o dedo para dibujar su firma en el cuadro de abajo',
        'type_instruction': 'Escriba su nombre legal completo como aparece en su identificación',
        'clear': 'Limpiar',
        'your_name': 'Su Nombre Legal Completo',
        'acknowledgments': 'Reconocimientos',
        'legal_notices': 'Avisos Legales y Consentimientos',
        'sign_document': 'Firmar Documento',
        'cancel': 'Cancelar',
        'processing': 'Procesando firma...'
      }
    }
    return translations[language][key] || key
  }

  useEffect(() => {
    // Get user's IP address for audit trail
    fetch('https://api.ipify.org?format=json')
      .then(response => response.json())
      .then(data => setIpAddress(data.ip))
      .catch(() => setIpAddress('Unknown'))
  }, [])

  useEffect(() => {
    // Check if all requirements are met
    const allAcknowledgmentsChecked = acknowledgementsChecked.every(checked => checked)
    const hasSignature = signatureMethod === 'draw' ? signatureData.length > 0 : typedName.trim().length > 0
    const identityOk = requireIdentityVerification ? identityVerified : true
    
    setCanSign(allAcknowledgmentsChecked && hasSignature && termsAccepted && identityOk)
  }, [acknowledgementsChecked, signatureData, typedName, termsAccepted, identityVerified, requireIdentityVerification, signatureMethod])

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return
    
    setIsDrawing(true)
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const ctx = canvas.getContext('2d')
    
    if (ctx) {
      ctx.strokeStyle = '#000000'
      ctx.lineWidth = 2
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      
      let x, y
      if ('touches' in e) {
        x = e.touches[0].clientX - rect.left
        y = e.touches[0].clientY - rect.top
      } else {
        x = e.clientX - rect.left
        y = e.clientY - rect.top
      }
      
      ctx.beginPath()
      ctx.moveTo(x, y)
    }
  }

  const draw = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !canvasRef.current) return
    
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const ctx = canvas.getContext('2d')
    
    if (ctx) {
      let x, y
      if ('touches' in e) {
        x = e.touches[0].clientX - rect.left
        y = e.touches[0].clientY - rect.top
      } else {
        x = e.clientX - rect.left
        y = e.clientY - rect.top
      }
      
      ctx.lineTo(x, y)
      ctx.stroke()
    }
  }

  const stopDrawing = () => {
    if (!isDrawing || !canvasRef.current) return
    
    setIsDrawing(false)
    const canvas = canvasRef.current
    const dataUrl = canvas.toDataURL('image/png')
    setSignatureData(dataUrl)
  }

  const clearSignature = () => {
    if (!canvasRef.current) return
    
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      setSignatureData('')
    }
  }

  const generateTypedSignature = (name: string): string => {
    // Create SVG signature for typed name
    const svg = `
      <svg width="300" height="80" xmlns="http://www.w3.org/2000/svg">
        <text x="10" y="50" font-family="Brush Script MT, cursive" font-size="24" fill="black">${name}</text>
      </svg>
    `
    return 'data:image/svg+xml;base64,' + btoa(svg)
  }

  const handleSubmitSignature = async () => {
    const finalSignatureData = signatureMethod === 'draw' 
      ? signatureData 
      : generateTypedSignature(typedName)

    const signatureDataToSubmit: DigitalSignatureData = {
      signatureType,
      signatureData: finalSignatureData,
      signedByName: signatureMethod === 'draw' ? signerName : typedName,
      signedByTitle: signerTitle,
      ipAddress,
      timestamp: new Date().toISOString(),
      documentName,
      acknowledgments,
      termsAccepted,
      identityVerified: requireIdentityVerification ? identityVerified : true
    }

    onSignatureComplete(signatureDataToSubmit)
  }

  const handleAcknowledgmentChange = (index: number, checked: boolean) => {
    const newChecked = [...acknowledgementsChecked]
    newChecked[index] = checked
    setAcknowledgementsChecked(newChecked)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="p-3 bg-blue-100 rounded-full">
            <PenTool className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900">{t('digital_signature')}</h2>
        <p className="text-gray-600 mt-2">{t('signature_required')}</p>
        <Badge variant="outline" className="mt-2">
          <Shield className="h-4 w-4 mr-1" />
          {t('legal_binding')}
        </Badge>
      </div>

      {/* Document Info */}
      <Card className="bg-blue-50">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-medium text-blue-900">Document: {documentName}</p>
                <p className="text-sm text-blue-700">Signer: {signerName}</p>
                {signerTitle && <p className="text-sm text-blue-700">Title: {signerTitle}</p>}
              </div>
            </div>
            <div className="text-right text-sm text-blue-700">
              <div className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                {new Date().toLocaleString()}
              </div>
              {ipAddress && <div>{t('ip_address').replace('{ip}', ipAddress)}</div>}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Acknowledgments */}
      {acknowledgments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">{t('acknowledgments')}</CardTitle>
            <CardDescription>
              Please read and acknowledge each item below
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {acknowledgments.map((acknowledgment, index) => (
              <div key={index} className="flex items-start space-x-3">
                <Checkbox
                  id={`ack-${index}`}
                  checked={acknowledgementsChecked[index]}
                  onCheckedChange={(checked) => handleAcknowledgmentChange(index, !!checked)}
                  className="mt-1"
                />
                <Label htmlFor={`ack-${index}`} className="text-sm leading-relaxed">
                  {acknowledgment}
                </Label>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Legal Notices */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t('legal_notices')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start space-x-3">
            <Checkbox
              id="esign-consent"
              checked={termsAccepted}
              onCheckedChange={(checked) => setTermsAccepted(!!checked)}
            />
            <Label htmlFor="esign-consent" className="text-sm leading-relaxed">
              {t('electronic_signature_consent')}
            </Label>
          </div>

          {requireIdentityVerification && (
            <div className="flex items-start space-x-3">
              <Checkbox
                id="identity-verify"
                checked={identityVerified}
                onCheckedChange={(checked) => setIdentityVerified(!!checked)}
              />
              <Label htmlFor="identity-verify" className="text-sm leading-relaxed">
                {t('identity_verification')}
              </Label>
            </div>
          )}

          <Alert>
            <Shield className="h-4 w-4" />
            <AlertDescription className="text-sm">
              {t('esign_act_notice')}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Signature Capture */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t('signature_verification')}</CardTitle>
          <div className="flex space-x-2">
            <Button
              variant={signatureMethod === 'draw' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSignatureMethod('draw')}
            >
              <PenTool className="h-4 w-4 mr-2" />
              {t('draw_signature')}
            </Button>
            <Button
              variant={signatureMethod === 'type' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSignatureMethod('type')}
            >
              <User className="h-4 w-4 mr-2" />
              {t('type_signature')}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {signatureMethod === 'draw' ? (
            <div>
              <p className="text-sm text-gray-600 mb-4">{t('draw_instruction')}</p>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 bg-white">
                <canvas
                  ref={canvasRef}
                  width={600}
                  height={200}
                  className="w-full h-32 border border-gray-200 rounded cursor-crosshair"
                  onMouseDown={startDrawing}
                  onMouseMove={draw}
                  onMouseUp={stopDrawing}
                  onMouseLeave={stopDrawing}
                  onTouchStart={startDrawing}
                  onTouchMove={draw}
                  onTouchEnd={stopDrawing}
                />
                <div className="flex justify-between items-center mt-3">
                  <p className="text-xs text-gray-500">Sign above</p>
                  <Button variant="outline" size="sm" onClick={clearSignature}>
                    <RotateCcw className="h-4 w-4 mr-2" />
                    {t('clear')}
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div>
              <p className="text-sm text-gray-600 mb-4">{t('type_instruction')}</p>
              <div>
                <Label htmlFor="typed-name">{t('your_name')}</Label>
                <Input
                  id="typed-name"
                  value={typedName}
                  onChange={(e) => setTypedName(e.target.value)}
                  placeholder="Enter your full legal name"
                  className="mt-2"
                />
                {typedName && (
                  <div className="mt-4 p-4 bg-gray-50 rounded border">
                    <p className="text-sm text-gray-600 mb-2">Preview:</p>
                    <div className="text-2xl font-serif italic text-center py-4 bg-white border rounded">
                      {typedName}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Legal Footer */}
      <div className="bg-gray-50 p-4 rounded-lg text-xs text-gray-600 space-y-2">
        <div className="flex items-center">
          <Shield className="h-4 w-4 mr-2" />
          <span>{t('document_retention')}</span>
        </div>
        <p>
          Signature Method: {signatureMethod === 'draw' ? 'Hand-drawn' : 'Typed'}
        </p>
        <p>Timestamp: {new Date().toLocaleString()}</p>
        {ipAddress && <p>IP Address: {ipAddress}</p>}
      </div>

      {/* Validation Messages */}
      {!canSign && (
        <Alert className="border-yellow-200 bg-yellow-50">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {acknowledgementsChecked.some(checked => !checked) && (
              <div>{t('all_acknowledgments_required')}</div>
            )}
            {(signatureMethod === 'draw' ? !signatureData : !typedName.trim()) && (
              <div>{t('signature_required_error')}</div>
            )}
          </AlertDescription>
        </Alert>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between items-center pt-6">
        <Button variant="outline" onClick={onCancel}>
          {t('cancel')}
        </Button>
        
        <Button 
          onClick={handleSubmitSignature}
          disabled={!canSign}
          size="lg"
          className="px-8"
        >
          <Check className="h-5 w-5 mr-2" />
          {t('sign_document')}
        </Button>
      </div>
    </div>
  )
}