import React, { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import HumanTraffickingAwareness from '@/components/HumanTraffickingAwareness'
import { CheckCircle, GraduationCap, Shield, AlertTriangle } from 'lucide-react'

interface OnboardingContext {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: () => void
}

export default function TraffickingAwarenessStep() {
  const { currentStep, progress, markStepComplete, saveProgress } = useOutletContext<OnboardingContext>()
  
  const [trainingComplete, setTrainingComplete] = useState(false)
  const [certificateData, setCertificateData] = useState(null)

  useEffect(() => {
    const existingData = progress.stepData?.['trafficking-awareness']
    if (existingData) {
      setTrainingComplete(existingData.trainingComplete || false)
      setCertificateData(existingData.certificate)
    }
  }, [progress])

  const handleTrainingComplete = (data: any) => {
    setTrainingComplete(true)
    setCertificateData(data)
    
    const stepData = {
      trainingComplete: true,
      certificate: data,
      completedAt: new Date().toISOString()
    }
    markStepComplete('trafficking-awareness', stepData)
    saveProgress()
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <GraduationCap className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Human Trafficking Awareness Training</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Complete this mandatory training to learn about human trafficking awareness and your role 
          in recognizing and reporting suspicious activities in the hospitality industry.
        </p>
      </div>

      <Alert className="bg-red-50 border-red-200">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">
          <strong>Federal Requirement:</strong> This training is mandatory for all hospitality employees 
          under federal anti-trafficking laws and industry best practices.
        </AlertDescription>
      </Alert>

      {trainingComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Human trafficking awareness training completed successfully. Certificate generated.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-blue-600" />
            <span>Training Module</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <HumanTraffickingAwareness
            onTrainingComplete={handleTrainingComplete}
            language="en"
          />
        </CardContent>
      </Card>

      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 8-10 minutes</p>
      </div>
    </div>
  )
}