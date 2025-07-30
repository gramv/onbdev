import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import DirectDepositForm from '@/components/DirectDepositForm'
import ReviewPlaceholder from '@/components/ReviewPlaceholder'
import { CheckCircle, CreditCard, DollarSign, AlertTriangle } from 'lucide-react'

interface StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function DirectDepositStep(props: StepProps) {
  const { currentStep, progress, markStepComplete, saveProgress } = props
  
  const [formData, setFormData] = useState(null)
  const [isValid, setIsValid] = useState(false)
  const [isSigned, setIsSigned] = useState(false)
  const [showReview, setShowReview] = useState(false)

  // Load existing data from progress
  useEffect(() => {
    const existingData = progress.stepData?.['direct-deposit']
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
    markStepComplete('direct-deposit', stepData)
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
            <DollarSign className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Review Direct Deposit</h1>
          </div>
        </div>
        
        <ReviewPlaceholder
          formType="direct_deposit"
          formTitle="Direct Deposit Authorization"
          description="Review your banking information before signing"
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
          <DollarSign className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Direct Deposit Setup</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Set up direct deposit to receive your paychecks electronically. This is the fastest and most secure way 
          to receive your pay, with funds typically available on payday.
        </p>
      </div>

      {/* Benefits Alert */}
      <Alert className="bg-green-50 border-green-200">
        <DollarSign className="h-4 w-4 text-green-600" />
        <AlertDescription className="text-green-800">
          <strong>Benefits of Direct Deposit:</strong> Faster access to funds, no lost checks, automatic deposits even when you're away, 
          and enhanced security for your earnings.
        </AlertDescription>
      </Alert>

      {/* Progress Indicator */}
      {isStepComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Direct deposit setup completed successfully. Your paychecks will be deposited automatically starting with your first pay period.
          </AlertDescription>
        </Alert>
      )}

      {/* Security Notice */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center space-x-2 text-blue-800">
            <CreditCard className="h-5 w-5" />
            <span>Banking Information Security</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-blue-800">
          <ul className="space-y-2 text-sm">
            <li>• Your banking information is encrypted and stored securely</li>
            <li>• Only authorized payroll personnel have access to this data</li>
            <li>• You can update your information anytime through HR</li>
            <li>• All transactions are processed through secure banking networks</li>
          </ul>
        </CardContent>
      </Card>

      {/* Direct Deposit Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="h-5 w-5 text-blue-600" />
            <span>Direct Deposit Authorization</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <DirectDepositForm
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

      {/* Important Banking Information */}
      <Card className="border-orange-200 bg-orange-50">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center space-x-2 text-orange-800">
            <AlertTriangle className="h-5 w-5" />
            <span>Banking Information Guidelines</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-orange-800">
          <ul className="space-y-2 text-sm">
            <li>• Double-check your routing and account numbers for accuracy</li>
            <li>• Use a checking account for direct deposit (savings accounts may have limitations)</li>
            <li>• Ensure your account is active and in good standing</li>
            <li>• Consider uploading a voided check for verification</li>
          </ul>
        </CardContent>
      </Card>

      {/* Completion Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-3">Direct Deposit Requirements</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Complete banking information</span>
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
            <span className="text-sm text-gray-600">Authorization signature</span>
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

      {/* Payroll Timeline */}
      {isStepComplete && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <DollarSign className="h-5 w-5 text-blue-600" />
              <div>
                <h3 className="font-medium text-blue-800">Direct Deposit Active</h3>
                <p className="text-sm text-blue-700">
                  Your direct deposit will begin with your first paycheck. If you start mid-pay period, 
                  your first partial check may be issued by paper check.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Estimated Time */}
      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 3-4 minutes</p>
      </div>
    </div>
  )
}