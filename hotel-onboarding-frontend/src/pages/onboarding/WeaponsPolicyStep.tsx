import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import WeaponsPolicyAcknowledgment from '@/components/WeaponsPolicyAcknowledgment'
import { CheckCircle, Shield, AlertTriangle } from 'lucide-react'

interface StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function WeaponsPolicyStep(props: StepProps) {
  const { currentStep, progress, markStepComplete, saveProgress } = props
  
  const [acknowledged, setAcknowledged] = useState(false)
  const [signatureData, setSignatureData] = useState(null)

  useEffect(() => {
    const existingData = progress.stepData?.['weapons-policy']
    if (existingData) {
      setAcknowledged(existingData.acknowledged || false)
      setSignatureData(existingData.signature)
    }
  }, [progress])

  const handleAcknowledgment = (data: any) => {
    setAcknowledged(true)
    setSignatureData(data)
    
    const stepData = {
      acknowledged: true,
      signature: data,
      completedAt: new Date().toISOString()
    }
    markStepComplete('weapons-policy', stepData)
    saveProgress()
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Shield className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Weapons Policy Acknowledgment</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Please review and acknowledge our workplace weapons policy. This policy ensures the safety 
          and security of all employees, guests, and visitors.
        </p>
      </div>

      <Alert className="bg-red-50 border-red-200">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">
          <strong>Zero Tolerance:</strong> Our company maintains a strict no-weapons policy for all employees, 
          contractors, and visitors on company property.
        </AlertDescription>
      </Alert>

      {acknowledged && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Weapons policy acknowledged and signed successfully.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-blue-600" />
            <span>Weapons Policy</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <WeaponsPolicyAcknowledgment
            onAcknowledgment={handleAcknowledgment}
            language="en"
          />
        </CardContent>
      </Card>

      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 2-3 minutes</p>
      </div>
    </div>
  )
}