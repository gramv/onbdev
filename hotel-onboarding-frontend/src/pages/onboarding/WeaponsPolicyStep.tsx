import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import WeaponsPolicyAcknowledgment from '@/components/WeaponsPolicyAcknowledgment'
import { CheckCircle, Shield, AlertTriangle } from 'lucide-react'
import { StepProps } from '../../controllers/OnboardingFlowController'
import { StepContainer } from '@/components/onboarding/StepContainer'
import { StepContentWrapper } from '@/components/onboarding/StepContentWrapper'
import { useAutoSave } from '@/hooks/useAutoSave'

export default function WeaponsPolicyStep({
  currentStep,
  progress,
  markStepComplete,
  saveProgress,
  language = 'en',
  employee,
  property
}: StepProps) {
  
  const [acknowledged, setAcknowledged] = useState(false)
  const [signatureData, setSignatureData] = useState(null)

  // Auto-save data
  const autoSaveData = {
    acknowledged,
    signatureData
  }

  // Auto-save hook
  const { saveStatus } = useAutoSave(autoSaveData, {
    onSave: async (data) => {
    await saveProgress(currentStep.id, data)
    }
  })

  // Load existing data
  useEffect(() => {
    if (progress.completedSteps.includes(currentStep.id)) {
      setAcknowledged(true)
    }
  }, [currentStep.id, progress.completedSteps])

  const handleAcknowledgment = async (data: any) => {
    setAcknowledged(true)
    setSignatureData(data)
    
    const stepData = {
      acknowledged: true,
      signature: data,
      completedAt: new Date().toISOString()
    }
    await markStepComplete(currentStep.id, stepData)
  }

  const translations = {
    en: {
      title: 'Weapons Policy Acknowledgment',
      description: 'Please review and acknowledge our workplace weapons policy. This policy ensures the safety and security of all employees, guests, and visitors.',
      zeroTolerance: 'Zero Tolerance:',
      zeroToleranceNotice: 'Our company maintains a strict no-weapons policy for all employees, contractors, and visitors on company property.',
      completionMessage: 'Weapons policy acknowledged and signed successfully.',
      policyTitle: 'Weapons Policy',
      estimatedTime: 'Estimated time: 2-3 minutes'
    },
    es: {
      title: 'Reconocimiento de Política de Armas',
      description: 'Por favor revise y reconozca nuestra política de armas en el lugar de trabajo. Esta política garantiza la seguridad de todos los empleados, huéspedes y visitantes.',
      zeroTolerance: 'Cero Tolerancia:',
      zeroToleranceNotice: 'Nuestra empresa mantiene una política estricta de no armas para todos los empleados, contratistas y visitantes en la propiedad de la empresa.',
      completionMessage: 'Política de armas reconocida y firmada exitosamente.',
      policyTitle: 'Política de Armas',
      estimatedTime: 'Tiempo estimado: 2-3 minutos'
    }
  }

  const t = translations[language]

  return (
    <StepContainer saveStatus={saveStatus}>
      <StepContentWrapper>
        <div className="space-y-6">
        {/* Step Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Shield className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
          </div>
          <p className="text-gray-600 max-w-3xl mx-auto">{t.description}</p>
        </div>

        {/* Zero Tolerance Notice */}
        <Alert className="bg-red-50 border-red-200">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>{t.zeroTolerance}</strong> {t.zeroToleranceNotice}
          </AlertDescription>
        </Alert>

        {/* Completion Status */}
        {acknowledged && (
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {t.completionMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Policy Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span>{t.policyTitle}</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <WeaponsPolicyAcknowledgment
              onAcknowledgment={handleAcknowledgment}
              language={language}
            />
          </CardContent>
        </Card>

        {/* Time Estimate */}
        <div className="text-center text-sm text-gray-500">
          <p>{t.estimatedTime}</p>
        </div>
        </div>
      </StepContentWrapper>
    </StepContainer>
  )
}