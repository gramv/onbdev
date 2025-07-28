import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle, Users, Clock, FileText, Globe, Info } from 'lucide-react'

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
    const existingData = progress.stepData?.['language_welcome']
    if (existingData) {
      setIsComplete(existingData.completed || false)
      setSelectedLanguage(existingData.selectedLanguage || language)
    }
  }, [progress, language])

  const handleLanguageChange = (newLanguage: 'en' | 'es') => {
    setSelectedLanguage(newLanguage)
    // Note: Language change will be handled by parent component
  }

  const handleContinue = () => {
    setIsComplete(true)
    const stepData = {
      completed: true,
      selectedLanguage,
      completedAt: new Date().toISOString(),
      welcomeAcknowledged: true
    }
    markStepComplete('language_welcome', stepData)
    saveProgress('language_welcome', stepData)
  }

  const translations = {
    en: {
      title: 'Welcome to Your Onboarding Process',
      subtitle: 'Let\'s Get You Started',
      personalGreeting: employee?.name ? `Welcome, ${employee.name}!` : 'Welcome!',
      propertyInfo: property?.name ? `You're joining ${property.name}` : 'You\'re joining our team',
      description: 'We\'re excited to have you join our team. This onboarding process will help you get set up with everything you need for your new position.',
      languageSelection: 'Language Preference',
      languageDesc: 'Choose your preferred language for the onboarding process. You can change this at any time.',
      processOverview: 'What to Expect',
      overviewDesc: 'Your onboarding journey includes several important steps to ensure federal compliance and get you ready for success.',
      steps: [
        { title: 'Personal Information', desc: 'Provide your contact details and basic information', time: '5 min' },
        { title: 'Document Upload', desc: 'Upload required identification documents', time: '7 min' },
        { title: 'I-9 Employment Verification', desc: 'Complete federal employment eligibility forms', time: '10 min' },
        { title: 'Tax Information (W-4)', desc: 'Set up your tax withholding preferences', time: '8 min' },
        { title: 'Benefits & Policies', desc: 'Review health insurance, policies, and company information', time: '15 min' },
        { title: 'Final Review', desc: 'Review and sign all your information', time: '5 min' }
      ],
      totalTime: 'Total estimated time: 45-60 minutes',
      importantInfo: 'Important Information',
      requirements: [
        'Have a government-issued photo ID ready (driver\'s license, passport, etc.)',
        'Prepare your Social Security card or other work authorization documents',
        'Set aside 45-60 minutes to complete the full process',
        'Ensure you have a stable internet connection for document uploads'
      ],
      federalCompliance: 'Federal Compliance Notice',
      complianceText: 'This onboarding process includes federally required forms including I-9 Employment Eligibility Verification and W-4 tax withholding. All information must be accurate and complete.',
      privacyNotice: 'Privacy & Security',
      privacyText: 'Your personal information is encrypted and securely stored. We comply with all federal privacy requirements and will only use your information for employment purposes.',
      readyToStart: 'Ready to Start?',
      continueButton: 'Begin Onboarding',
      completedNotice: 'Welcome step completed! You can now proceed to the next step.'
    },
    es: {
      title: 'Bienvenido a Su Proceso de Incorporación',
      subtitle: 'Comencemos',
      personalGreeting: employee?.name ? `¡Bienvenido, ${employee.name}!` : '¡Bienvenido!',
      propertyInfo: property?.name ? `Se está uniendo a ${property.name}` : 'Se está uniendo a nuestro equipo',
      description: 'Estamos emocionados de tenerlo en nuestro equipo. Este proceso de incorporación lo ayudará a configurar todo lo que necesita para su nueva posición.',
      languageSelection: 'Preferencia de Idioma',
      languageDesc: 'Elija su idioma preferido para el proceso de incorporación. Puede cambiar esto en cualquier momento.',
      processOverview: 'Qué Esperar',
      overviewDesc: 'Su jornada de incorporación incluye varios pasos importantes para asegurar el cumplimiento federal y prepararlo para el éxito.',
      steps: [
        { title: 'Información Personal', desc: 'Proporcione sus datos de contacto e información básica', time: '5 min' },
        { title: 'Subir Documentos', desc: 'Suba los documentos de identificación requeridos', time: '7 min' },
        { title: 'Verificación de Empleo I-9', desc: 'Complete los formularios federales de elegibilidad de empleo', time: '10 min' },
        { title: 'Información de Impuestos (W-4)', desc: 'Configure sus preferencias de retención de impuestos', time: '8 min' },
        { title: 'Beneficios y Políticas', desc: 'Revise el seguro de salud, políticas e información de la empresa', time: '15 min' },
        { title: 'Revisión Final', desc: 'Revise y firme toda su información', time: '5 min' }
      ],
      totalTime: 'Tiempo total estimado: 45-60 minutos',
      importantInfo: 'Información Importante',
      requirements: [
        'Tenga lista una identificación con foto emitida por el gobierno (licencia de conducir, pasaporte, etc.)',
        'Prepare su tarjeta de Seguro Social u otros documentos de autorización de trabajo',
        'Reserve 45-60 minutos para completar todo el proceso',
        'Asegúrese de tener una conexión a internet estable para subir documentos'
      ],
      federalCompliance: 'Aviso de Cumplimiento Federal',
      complianceText: 'Este proceso de incorporación incluye formularios requeridos federalmente incluyendo la Verificación de Elegibilidad de Empleo I-9 y retención de impuestos W-4. Toda la información debe ser precisa y completa.',
      privacyNotice: 'Privacidad y Seguridad',
      privacyText: 'Su información personal está encriptada y almacenada de forma segura. Cumplimos con todos los requisitos federales de privacidad y solo usaremos su información para propósitos de empleo.',
      readyToStart: '¿Listo para Comenzar?',
      continueButton: 'Comenzar Incorporación',
      completedNotice: '¡Paso de bienvenida completado! Ahora puede proceder al siguiente paso.'
    }
  }

  const t = translations[selectedLanguage]

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Users className="h-8 w-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">{t.title}</h1>
        </div>
        <h2 className="text-xl text-blue-600 font-semibold mb-2">{t.personalGreeting}</h2>
        <p className="text-lg text-gray-600 mb-2">{t.propertyInfo}</p>
        <p className="text-gray-600 max-w-3xl mx-auto">
          {t.description}
        </p>
      </div>

      {/* Completion Notice */}
      {isComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            {t.completedNotice}
          </AlertDescription>
        </Alert>
      )}

      {/* Language Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Globe className="h-5 w-5 text-blue-600" />
            <span>{t.languageSelection}</span>
          </CardTitle>
          <p className="text-sm text-gray-600">{t.languageDesc}</p>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4">
            <button
              onClick={() => handleLanguageChange('en')}
              className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                selectedLanguage === 'en'
                  ? 'border-blue-500 bg-blue-50 text-blue-900'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-center">
                <div className="text-2xl mb-2">🇺🇸</div>
                <div className="font-semibold">English</div>
                <div className="text-sm text-gray-600">Complete process in English</div>
              </div>
            </button>
            <button
              onClick={() => handleLanguageChange('es')}
              className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                selectedLanguage === 'es'
                  ? 'border-blue-500 bg-blue-50 text-blue-900'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-center">
                <div className="text-2xl mb-2">🇪🇸</div>
                <div className="font-semibold">Español</div>
                <div className="text-sm text-gray-600">Completar proceso en español</div>
              </div>
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Process Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <span>{t.processOverview}</span>
          </CardTitle>
          <p className="text-sm text-gray-600">{t.overviewDesc}</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {t.steps.map((step, index) => (
              <div key={index} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{step.title}</h4>
                  <p className="text-sm text-gray-600">{step.desc}</p>
                </div>
                <Badge variant="secondary" className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>{step.time}</span>
                </Badge>
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg text-center">
            <p className="font-semibold text-blue-900">{t.totalTime}</p>
          </div>
        </CardContent>
      </Card>

      {/* Important Information */}
      <Card className="border-orange-200 bg-orange-50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center space-x-2 text-orange-800">
            <Info className="h-5 w-5" />
            <span>{t.importantInfo}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-orange-800">
          <ul className="space-y-2 text-sm">
            {t.requirements.map((requirement, index) => (
              <li key={index}>• {requirement}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Federal Compliance Notice */}
      <Alert className="bg-blue-50 border-blue-200">
        <FileText className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>{t.federalCompliance}:</strong> {t.complianceText}
        </AlertDescription>
      </Alert>

      {/* Privacy Notice */}
      <Alert className="bg-green-50 border-green-200">
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertDescription className="text-green-800">
          <strong>{t.privacyNotice}:</strong> {t.privacyText}
        </AlertDescription>
      </Alert>

      {/* Ready to Start */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardContent className="pt-6 text-center">
          <h3 className="text-xl font-bold text-blue-900 mb-4">{t.readyToStart}</h3>
          <Button
            onClick={handleContinue}
            size="lg"
            className="px-8 py-3 text-lg font-semibold"
            disabled={isComplete}
          >
            {isComplete ? (
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5" />
                <span>Welcome Completed</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>{t.continueButton}</span>
              </div>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Estimated Time */}
      <div className="text-center text-sm text-gray-500">
        <p>This step: 2 minutes</p>
      </div>
    </div>
  )
}