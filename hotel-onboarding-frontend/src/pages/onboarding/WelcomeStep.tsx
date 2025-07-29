import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent } from '@/components/ui/card'
import { CheckCircle, Clock, FileText, Globe } from 'lucide-react'

interface WelcomeStepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function WelcomeStep({
  currentStep, 
  progress, 
  markStepComplete, 
  saveProgress, 
  language = 'en', 
  employee,
  property
}: WelcomeStepProps) {
  
  const [isComplete, setIsComplete] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'es'>(language)

  // Load existing data from progress
  useEffect(() => {
    const existingData = progress.stepData?.['welcome'] || progress.stepData?.['language_welcome']
    if (existingData) {
      setIsComplete(existingData.completed || false)
      setSelectedLanguage(existingData.selectedLanguage || language)
    }
  }, [progress, language])

  const handleLanguageToggle = () => {
    const newLanguage = selectedLanguage === 'en' ? 'es' : 'en'
    setSelectedLanguage(newLanguage)
  }

  const handleContinue = () => {
    setIsComplete(true)
    const stepData = {
      completed: true,
      selectedLanguage,
      completedAt: new Date().toISOString(),
      welcomeAcknowledged: true
    }
    markStepComplete('welcome', stepData)
    saveProgress('welcome', stepData)
  }

  const translations = {
    en: {
      greeting: employee?.name ? `Welcome, ${employee.name}!` : 'Welcome!',
      propertyInfo: property?.name || 'Our Company',
      title: 'Let\'s get you started',
      description: 'Complete your onboarding in about 45 minutes',
      whatYouNeed: 'What you\'ll need:',
      requirements: [
        'Government ID (Driver\'s License or Passport)',
        'Social Security Card',
        'Bank account information',
        'Emergency contact details'
      ],
      estimatedTime: 'Estimated time: 45-60 minutes',
      languageToggle: 'Español',
      continueButton: 'Start Onboarding',
      completedButton: 'Welcome Completed'
    },
    es: {
      greeting: employee?.name ? `¡Bienvenido, ${employee.name}!` : '¡Bienvenido!',
      propertyInfo: property?.name || 'Nuestra Empresa',
      title: 'Comencemos',
      description: 'Complete su incorporación en aproximadamente 45 minutos',
      whatYouNeed: 'Lo que necesitará:',
      requirements: [
        'Identificación del gobierno (Licencia o Pasaporte)',
        'Tarjeta de Seguro Social',
        'Información bancaria',
        'Datos de contacto de emergencia'
      ],
      estimatedTime: 'Tiempo estimado: 45-60 minutos',
      languageToggle: 'English',
      continueButton: 'Comenzar Incorporación',
      completedButton: 'Bienvenida Completada'
    }
  }

  const t = translations[selectedLanguage]

  return (
    <div className="flex-container-adaptive">
      {/* Clean Header */}
      <div className="text-center space-y-2">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{t.greeting}</h1>
        <p className="text-lg text-blue-600 font-medium">{t.propertyInfo}</p>
        <p className="text-base text-gray-600">{t.title}</p>
      </div>

      {/* Completion Alert */}
      {isComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Welcome step completed! You can proceed to the next step.
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Card */}
      <Card className="flex-1">
        <CardContent className="pt-6 space-y-4">
          {/* Time Estimate */}
          <div className="flex items-center justify-center space-x-2 text-blue-600 bg-blue-50 rounded-lg p-3">
            <Clock className="h-5 w-5" />
            <span className="font-medium">{t.estimatedTime}</span>
          </div>

          {/* Requirements List */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
              <FileText className="h-4 w-4 mr-2" />
              {t.whatYouNeed}
            </h3>
            <ul className="space-y-2">
              {t.requirements.map((req, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span className="text-gray-700">{req}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* Language Toggle & Continue Button */}
      <div className="space-y-3">
        {/* Language Toggle */}
        <div className="flex justify-center">
          <Button
            variant="outline"
            size="sm"
            onClick={handleLanguageToggle}
            className="flex items-center space-x-2"
          >
            <Globe className="h-4 w-4" />
            <span>{t.languageToggle}</span>
          </Button>
        </div>

        {/* Continue Button */}
        <Button
          onClick={handleContinue}
          size="lg"
          className="w-full"
          disabled={isComplete}
        >
          {isComplete ? (
            <div className="flex items-center justify-center space-x-2">
              <CheckCircle className="h-5 w-5" />
              <span>{t.completedButton}</span>
            </div>
          ) : (
            <span>{t.continueButton}</span>
          )}
        </Button>
      </div>
    </div>
  )
}