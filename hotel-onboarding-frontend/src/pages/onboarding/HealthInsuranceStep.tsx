import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import HealthInsuranceForm from '@/components/HealthInsuranceForm'
import ReviewPlaceholder from '@/components/ReviewPlaceholder'
import { CheckCircle, Heart, Users, AlertTriangle } from 'lucide-react'

interface StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function HealthInsuranceStep(props: StepProps) {
  const { currentStep, progress, markStepComplete, saveProgress } = props
  
  const [formData, setFormData] = useState(null)
  const [isValid, setIsValid] = useState(false)
  const [showReview, setShowReview] = useState(false)

  useEffect(() => {
    const existingData = progress.stepData?.['health-insurance']
    if (existingData) {
      setFormData(existingData.formData)
    }
  }, [progress])

  const handleFormSave = (data: any) => {
    setFormData(data)
    // Save progress but don't mark complete yet (wait for review and sign)
    const stepData = {
      formData: data,
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

  const handleComplete = () => {
    const stepData = {
      formData,
      reviewed: true,
      completedAt: new Date().toISOString()
    }
    markStepComplete('health-insurance', stepData)
    saveProgress()
    setShowReview(false)
  }

  // Show review placeholder if form is valid and review is requested
  if (showReview && formData) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Heart className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Review Health Insurance</h1>
          </div>
        </div>
        
        <ReviewPlaceholder
          formType="health_insurance"
          formTitle="Health Insurance Enrollment"
          description="Review your health insurance selections and dependent information"
          isReady={isValid}
          onEdit={handleBackFromReview}
          onReview={handleComplete}
          language="en"
        />
        
        <div className="flex justify-between">
          <Button variant="outline" onClick={handleBackFromReview}>
            Back to Form
          </Button>
          <Button onClick={handleComplete} className="bg-green-600 hover:bg-green-700">
            Complete Enrollment
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Heart className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Health Insurance Enrollment</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Choose your health insurance plan and add dependents if applicable. Your coverage will begin according to your plan's effective date.
        </p>
      </div>

      <Alert className="bg-blue-50 border-blue-200">
        <Heart className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>Enrollment Period:</strong> You have 30 days from your hire date to enroll in health insurance or make changes to your coverage.
        </AlertDescription>
      </Alert>

      {formData && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Health insurance enrollment completed successfully.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-blue-600" />
            <span>Health Insurance Plan Selection</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <HealthInsuranceForm
            initialData={formData || {}}
            language="en"
            onSave={handleFormSave}
            onValidationChange={setIsValid}
          />
          
          {/* Review and Complete Button */}
          {isValid && formData && (
            <div className="mt-6 flex justify-end">
              <Button 
                onClick={handleProceedToReview}
                size="lg"
                className="bg-blue-600 hover:bg-blue-700"
              >
                Review Enrollment
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 6-8 minutes</p>
      </div>
    </div>
  )
}