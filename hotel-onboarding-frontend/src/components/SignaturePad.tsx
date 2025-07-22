import React, { useRef, useState } from 'react'
import SignatureCanvas from 'react-signature-canvas'
import { Button } from '../components/ui/button'
import { useLanguage } from '../contexts/LanguageContext'

interface SignaturePadProps {
  onSignature: (signature: string) => void
  label: string
  required?: boolean
  className?: string
}

export default function SignaturePad({ onSignature, label, required = true, className = "" }: SignaturePadProps) {
  const { t } = useLanguage()
  const sigRef = useRef<SignatureCanvas>(null)
  const [signed, setSigned] = useState(false)

  const handleClear = () => {
    sigRef.current?.clear()
    setSigned(false)
    onSignature('')
  }

  const handleSave = () => {
    if (sigRef.current) {
      const signature = sigRef.current.toDataURL()
      onSignature(signature)
      setSigned(true)
    }
  }

  return (
    <div className={`border rounded-lg p-4 ${className}`}>
      <label className="block text-sm font-medium mb-2">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <div className="border-2 border-gray-300 rounded bg-white">
        <SignatureCanvas
          ref={sigRef}
          canvasProps={{
            width: 500,
            height: 200,
            className: 'signature-canvas w-full h-48 touch-action-none'
          }}
          onEnd={handleSave}
          backgroundColor="white"
        />
      </div>
      <div className="flex gap-2 mt-2 items-center">
        <Button variant="outline" onClick={handleClear} type="button">
          {t('signature.clear')}
        </Button>
        {signed && (
          <span className="text-green-600 text-sm flex items-center">
            ✓ {t('signature.signed')}
          </span>
        )}
      </div>
    </div>
  )
}
