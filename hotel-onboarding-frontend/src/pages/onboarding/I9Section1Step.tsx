import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import I9Section1Form from '@/components/I9Section1Form'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle, Shield, AlertTriangle, FileText } from 'lucide-react'

interface I9Section1StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function I9Section1Step({
  currentStep,
  progress,
  markStepComplete,
  saveProgress,
  language = 'en',
  employee,
  property
}: I9Section1StepProps) {
  
  const [formData, setFormData] = useState(null)
  const [isValid, setIsValid] = useState(false)
  const [isSigned, setIsSigned] = useState(false)

  // Load existing data from progress
  useEffect(() => {
    const existingData = progress.stepData?.['i9-section1']
    if (existingData) {
      setFormData(existingData.formData)
      setIsSigned(existingData.signed || false)
    }
  }, [progress])

  const handleFormSave = (data: any) => {
    setFormData(data)
    const stepData = {
      formData: data,
      signed: isSigned,
      completedAt: new Date().toISOString()
    }
    markStepComplete('i9-section1', stepData)
    saveProgress('i9-section1', stepData)
  }

  const handleDigitalSignature = (signatureData: any) => {
    setIsSigned(true)
    const stepData = {
      formData,
      signed: true,
      signature: signatureData,
      completedAt: new Date().toISOString()
    }
    markStepComplete('i9-section1', stepData)
    saveProgress('i9-section1', stepData)
  }

  const isStepComplete = isValid && isSigned

  return (
    <div className="space-y-6">
      {/* Step Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Shield className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">I-9 Employment Eligibility Verification</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Section 1 of Form I-9 must be completed by the employee on or before the first day of employment. 
          This form verifies your eligibility to work in the United States.
        </p>
      </div>

      {/* Federal Compliance Notice */}
      <Alert className="bg-blue-50 border-blue-200">
        <Shield className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>Federal Requirement:</strong> Form I-9 is required by the U.S. Citizenship and Immigration Services (USCIS) 
          for all employees. Completion is mandatory under the Immigration and Nationality Act.
        </AlertDescription>
      </Alert>

      {/* Progress Indicator */}
      {isStepComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            I-9 Section 1 completed successfully with digital signature. You can proceed to document verification.
          </AlertDescription>
        </Alert>
      )}

      {/* Important Instructions */}
      <Card className="border-orange-200 bg-orange-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center space-x-2 text-orange-800">
            <AlertTriangle className="h-5 w-5" />
            <span>Important Instructions</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-orange-800">
          <ul className="space-y-2 text-sm">
            <li>• Complete all required fields with information exactly as it appears on your documents</li>
            <li>• Do not provide false information - this is a federal offense</li>
            <li>• You must complete this section before your first day of work</li>
            <li>• Your employer will complete Section 2 within 3 business days of your start date</li>
          </ul>
        </CardContent>
      </Card>

      {/* I-9 Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <span>Form I-9, Section 1: Employee Information and Attestation</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <I9Section1Form
            initialData={formData || {}}
            language={language}
            onSave={handleFormSave}
            onValidationChange={setIsValid}
            onDigitalSignature={handleDigitalSignature}
          />
        </CardContent>
      </Card>

      {/* Completion Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-3">Section 1 Requirements</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Complete all required form fields</span>
            <div className="flex items-center space-x-2">
              {isValid ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
              )}
              <span className="text-sm font-medium">
                {isValid ? 'Complete' : 'In Progress'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Digital signature attestation</span>
            <div className="flex items-center space-x-2">
              {isSigned ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
              )}
              <span className="text-sm font-medium">
                {isSigned ? 'Signed' : 'Required'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      {isStepComplete && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <h3 className="font-medium text-green-800">Section 1 Complete</h3>
                <p className="text-sm text-green-700">
                  Next, you'll need to provide acceptable documents to verify your identity and work authorization.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Federal Notice */}
      <div className="text-xs text-gray-500 border-t pt-4">
        <p className="mb-2"><strong>Privacy Act Notice:</strong> The authority for collecting this information is the Immigration and Nationality Act.</p>
        <p>This information will be used to verify your eligibility to work in the United States. Failure to provide this information may result in denial of employment.</p>
      </div>

      {/* Estimated Time */}
      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 3-4 minutes</p>
      </div>
    </div>
  )
}