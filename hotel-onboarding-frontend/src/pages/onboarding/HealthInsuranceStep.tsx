import React, { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import HealthInsuranceForm from '@/components/HealthInsuranceForm'
import { CheckCircle, Heart, Users, AlertTriangle } from 'lucide-react'

interface OnboardingContext {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: () => void
}

export default function HealthInsuranceStep() {
  const { currentStep, progress, markStepComplete, saveProgress } = useOutletContext<OnboardingContext>()
  
  const [formData, setFormData] = useState(null)
  const [isValid, setIsValid] = useState(false)

  useEffect(() => {
    const existingData = progress.stepData?.['health-insurance']
    if (existingData) {
      setFormData(existingData.formData)
    }
  }, [progress])

  const handleFormSave = (data: any) => {
    setFormData(data)
    const stepData = {
      formData: data,
      completedAt: new Date().toISOString()
    }
    markStepComplete('health-insurance', stepData)
    saveProgress()
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
        </CardContent>
      </Card>

      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 6-8 minutes</p>
      </div>
    </div>
  )
}