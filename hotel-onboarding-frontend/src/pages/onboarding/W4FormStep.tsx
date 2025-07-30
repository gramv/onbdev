import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import W4Form from '@/components/W4Form'
import ReviewPlaceholder from '@/components/ReviewPlaceholder'
import { CheckCircle, CreditCard, FileText, AlertTriangle } from 'lucide-react'

interface StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function W4FormStep(props: StepProps) {
  const { currentStep, progress, markStepComplete, saveProgress } = props
  
  const [formData, setFormData] = useState(null)
  const [isValid, setIsValid] = useState(false)
  const [isSigned, setIsSigned] = useState(false)
  const [showReview, setShowReview] = useState(false)

  // Load existing data from progress
  useEffect(() => {
    const existingData = progress.stepData?.['w4-form']
    if (existingData) {
      setFormData(existingData.formData)
      setIsSigned(existingData.signed || false)
    }
  }, [progress])

  const handleFormSave = (data: any) => {
    setFormData(data)
    // Save progress but don't mark complete yet (wait for review and sign)
    const stepData = {
      formData: data,
      signed: isSigned,
      completedAt: new Date().toISOString()
    }
    // Don't mark complete until reviewed and signed
    saveProgress()
  }

  const handleProceedToReview = () => {
    if (isValid && formData) {
      setShowReview(true)
    }
  }

  const handleBackFromReview = () => {
    setShowReview(false)
  }

  const handleDigitalSignature = (signatureData: any) => {
    setIsSigned(true)
    const stepData = {
      formData,
      signed: true,
      signature: signatureData,
      completedAt: new Date().toISOString()
    }
    markStepComplete('w4-form', stepData)
    saveProgress()
    setShowReview(false)
  }

  const isStepComplete = isValid && isSigned

  // Show review placeholder if form is valid and review is requested
  if (showReview && formData) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <CreditCard className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Review W-4 Form</h1>
          </div>
        </div>
        
        <ReviewPlaceholder
          formType="w4"
          formTitle="Form W-4 Employee's Withholding Certificate"
          description="Review your tax withholding information before signing"
          isReady={isValid}
          onEdit={handleBackFromReview}
          language="en"
        />
        
        <div className="flex justify-between">
          <Button variant="outline" onClick={handleBackFromReview}>
            Back to Form
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Step Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <CreditCard className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">W-4 Tax Withholding</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Complete Form W-4 to determine the correct amount of federal income tax to withhold from your pay. 
          This form helps ensure you're paying the right amount throughout the year.
        </p>
      </div>

      {/* Federal Compliance Notice */}
      <Alert className="bg-blue-50 border-blue-200">
        <CreditCard className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>Federal Requirement:</strong> Form W-4 is required by the Internal Revenue Service (IRS) 
          for all employees to determine federal income tax withholding.
        </AlertDescription>
      </Alert>

      {/* Progress Indicator */}
      {isStepComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            W-4 form completed successfully with digital signature. Your tax withholding is now configured.
          </AlertDescription>
        </Alert>
      )}

      {/* Important Tax Information */}
      <Card className="border-orange-200 bg-orange-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center space-x-2 text-orange-800">
            <AlertTriangle className="h-5 w-5" />
            <span>Important Tax Information</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-orange-800">
          <ul className="space-y-2 text-sm">
            <li>• Complete this form based on your current tax situation</li>
            <li>• You can submit a new W-4 anytime your situation changes</li>
            <li>• Consider using the IRS Tax Withholding Estimator for accuracy</li>
            <li>• Consult a tax professional if you have complex tax situations</li>
          </ul>
        </CardContent>
      </Card>

      {/* W-4 Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <span>Form W-4: Employee's Withholding Certificate</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <W4Form
            initialData={formData || {}}
            language="en"
            onSave={handleFormSave}
            onValidationChange={setIsValid}
            onDigitalSignature={handleDigitalSignature}
          />
          
          {/* Review and Sign Button */}
          {isValid && formData && !isSigned && (
            <div className="mt-6 flex justify-end">
              <Button 
                onClick={handleProceedToReview}
                size="lg"
                className="bg-blue-600 hover:bg-blue-700"
              >
                Review and Sign Form
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Completion Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-3">W-4 Requirements</h3>
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
            <span className="text-sm text-gray-600">Digital signature certification</span>
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

      {/* Estimated Time */}
      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 4-6 minutes</p>
      </div>
    </div>
  )
}