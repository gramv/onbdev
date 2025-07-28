import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { 
  Building2, 
  Users, 
  Clock, 
  Globe, 
  CheckCircle, 
  Star, 
  MapPin, 
  Briefcase,
  Calendar,
  FileText,
  Shield,
  Heart,
  Award,
  Coffee
} from 'lucide-react'
import axios from 'axios'

interface Employee {
  id: string
  user_id: string
  property_id: string
  position: string
  department: string
  hire_date: string
  status: string
  job_details: {
    job_title: string
    start_date: string
    start_time: string
    pay_rate: string
    pay_frequency: string
    supervisor: string
    benefits_eligible: string
    special_instructions?: string
  }
}

interface Property {
  id: string
  name: string
  address: string
  manager_ids: string[]
}

interface WelcomeData {
  employee: Employee
  property: Property
  applicant_data: {
    first_name: string
    last_name: string
    email: string
    phone: string
  }
}

export default function OnboardingWelcome() {
  const { employeeId } = useParams()
  const navigate = useNavigate()
  const [welcomeData, setWelcomeData] = useState<WelcomeData | null>(null)
  const [language, setLanguage] = useState<'en' | 'es'>('en')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (employeeId) {
      fetchWelcomeData()
    }
  }, [employeeId])

  const fetchWelcomeData = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`/api/employees/${employeeId}/welcome-data`)
      setWelcomeData(response.data)
      setError('')
    } catch (err: any) {
      console.error('Error fetching welcome data:', err)
      setError('Unable to load your onboarding information. Please contact HR for assistance.')
    } finally {
      setLoading(false)
    }
  }

  const handleBeginOnboarding = () => {
    // Navigate to the main onboarding portal
    navigate(`/onboard/${employeeId}`)
  }

  const translations = {
    en: {
      welcomeTitle: 'Welcome to Your New Journey!',
      personalGreeting: welcomeData?.applicant_data 
        ? `Welcome, ${welcomeData.applicant_data.first_name}!` 
        : 'Welcome!',
      congratulations: 'Congratulations on joining our team',
      propertyWelcome: welcomeData?.property 
        ? `You're now part of the ${welcomeData.property.name} family` 
        : 'You\'re now part of our family',
      jobDetailsTitle: 'Your Position Details',
      positionLabel: 'Position',
      departmentLabel: 'Department', 
      startDateLabel: 'Start Date',
      startTimeLabel: 'Start Time',
      payRateLabel: 'Pay Rate',
      supervisorLabel: 'Your Supervisor',
      locationLabel: 'Work Location',
      onboardingTitle: 'Your Onboarding Journey',
      onboardingDesc: 'Complete these important steps to get ready for your first day',
      stepsTitle: 'What\'s Next?',
      steps: [
        { title: 'Personal Information', desc: 'Provide your contact details and emergency contacts', time: '5 min', icon: Users },
        { title: 'Federal Forms (I-9)', desc: 'Complete employment eligibility verification', time: '8 min', icon: Shield },
        { title: 'Tax Information (W-4)', desc: 'Set up your tax withholding preferences', time: '6 min', icon: FileText },
        { title: 'Benefits & Health Insurance', desc: 'Choose your health insurance and benefits', time: '10 min', icon: Heart },
        { title: 'Company Policies', desc: 'Review and acknowledge company policies', time: '8 min', icon: Award },
        { title: 'Final Review', desc: 'Review all information and submit for approval', time: '5 min', icon: CheckCircle }
      ],
      totalTime: 'Total estimated time: 40-45 minutes',
      beginButton: 'Begin My Onboarding',
      languageSelection: 'Choose Your Language',
      importantInfo: 'Important Information',
      requirements: [
        'Have a government-issued photo ID ready (driver\'s license, passport, etc.)',
        'Prepare your Social Security card or work authorization documents',
        'Set aside 45 minutes in a quiet environment',
        'Ensure stable internet connection for document uploads'
      ],
      supportInfo: 'Need Help?',
      supportText: 'If you have questions during the process, contact your supervisor or HR department.',
      federalNotice: 'Federal Compliance Notice',
      federalText: 'This process includes federally required forms. All information must be accurate and complete.',
      privacyNotice: 'Your information is secure and encrypted'
    },
    es: {
      welcomeTitle: '¡Bienvenido a Tu Nueva Aventura!',
      personalGreeting: welcomeData?.applicant_data 
        ? `¡Bienvenido, ${welcomeData.applicant_data.first_name}!` 
        : '¡Bienvenido!',
      congratulations: 'Felicitaciones por unirte a nuestro equipo',
      propertyWelcome: welcomeData?.property 
        ? `Ahora eres parte de la familia ${welcomeData.property.name}` 
        : 'Ahora eres parte de nuestra familia',
      jobDetailsTitle: 'Detalles de Tu Posición',
      positionLabel: 'Posición',
      departmentLabel: 'Departamento',
      startDateLabel: 'Fecha de Inicio',
      startTimeLabel: 'Hora de Inicio', 
      payRateLabel: 'Tarifa de Pago',
      supervisorLabel: 'Tu Supervisor',
      locationLabel: 'Ubicación de Trabajo',
      onboardingTitle: 'Tu Proceso de Incorporación',
      onboardingDesc: 'Completa estos pasos importantes para prepararte para tu primer día',
      stepsTitle: '¿Qué Sigue?',
      steps: [
        { title: 'Información Personal', desc: 'Proporciona tus datos de contacto y contactos de emergencia', time: '5 min', icon: Users },
        { title: 'Formularios Federales (I-9)', desc: 'Completa la verificación de elegibilidad de empleo', time: '8 min', icon: Shield },
        { title: 'Información de Impuestos (W-4)', desc: 'Configura tus preferencias de retención de impuestos', time: '6 min', icon: FileText },
        { title: 'Beneficios y Seguro de Salud', desc: 'Elige tu seguro de salud y beneficios', time: '10 min', icon: Heart },
        { title: 'Políticas de la Empresa', desc: 'Revisa y reconoce las políticas de la empresa', time: '8 min', icon: Award },
        { title: 'Revisión Final', desc: 'Revisa toda la información y envía para aprobación', time: '5 min', icon: CheckCircle }
      ],
      totalTime: 'Tiempo total estimado: 40-45 minutos',
      beginButton: 'Comenzar Mi Incorporación',
      languageSelection: 'Elige Tu Idioma',
      importantInfo: 'Información Importante',
      requirements: [
        'Ten lista una identificación con foto emitida por el gobierno (licencia de conducir, pasaporte, etc.)',
        'Prepara tu tarjeta de Seguro Social o documentos de autorización de trabajo',
        'Reserva 45 minutos en un ambiente tranquilo',
        'Asegúrate de tener conexión estable a internet para subir documentos'
      ],
      supportInfo: '¿Necesitas Ayuda?',
      supportText: 'Si tienes preguntas durante el proceso, contacta a tu supervisor o al departamento de RRHH.',
      federalNotice: 'Aviso de Cumplimiento Federal',
      federalText: 'Este proceso incluye formularios requeridos federalmente. Toda la información debe ser precisa y completa.',
      privacyNotice: 'Tu información está segura y encriptada'
    }
  }

  const t = translations[language]

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your onboarding information...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-pink-50 flex items-center justify-center p-6">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to Load Information</h3>
              <p className="text-sm text-gray-600 mb-4">{error}</p>
              <Button onClick={fetchWelcomeData} variant="outline">
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!welcomeData) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header with Property Branding */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-white/20 rounded-lg p-3">
                <Building2 className="h-8 w-8" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">{welcomeData.property.name}</h1>
                <div className="flex items-center space-x-2 text-blue-100">
                  <MapPin className="h-4 w-4" />
                  <span className="text-sm">{welcomeData.property.address}</span>
                </div>
              </div>
            </div>
            
            {/* Language Selection */}
            <div className="flex items-center space-x-2">
              <Globe className="h-4 w-4 text-blue-200" />
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value as 'en' | 'es')}
                className="bg-white/20 border border-white/30 rounded-md px-3 py-1 text-sm text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-white/50"
              >
                <option value="en">English</option>
                <option value="es">Español</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="text-center mb-8">
          <div className="mb-6">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="bg-gradient-to-r from-green-400 to-emerald-500 rounded-full p-3">
                <Star className="h-8 w-8 text-white" />
              </div>
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">{t.welcomeTitle}</h1>
            <h2 className="text-2xl font-semibold text-blue-600 mb-2">{t.personalGreeting}</h2>
            <p className="text-xl text-gray-600 mb-1">{t.congratulations}</p>
            <p className="text-lg text-gray-500">{t.propertyWelcome}</p>
          </div>

          {/* Celebration Icons */}
          <div className="flex justify-center space-x-6 mb-8">
            <div className="text-center">
              <div className="bg-yellow-100 rounded-full p-3 mb-2 mx-auto w-fit">
                <Award className="h-6 w-6 text-yellow-600" />
              </div>
              <p className="text-xs text-gray-600">New Team Member</p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 rounded-full p-3 mb-2 mx-auto w-fit">
                <Briefcase className="h-6 w-6 text-blue-600" />
              </div>
              <p className="text-xs text-gray-600">Ready to Start</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full p-3 mb-2 mx-auto w-fit">
                <Coffee className="h-6 w-6 text-green-600" />
              </div>
              <p className="text-xs text-gray-600">Welcome Aboard</p>
            </div>
          </div>
        </div>

        {/* Job Details Card */}
        <Card className="mb-8 shadow-lg border-0 bg-gradient-to-r from-white to-blue-50">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
            <CardTitle className="flex items-center space-x-2">
              <Briefcase className="h-5 w-5" />
              <span>{t.jobDetailsTitle}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="bg-blue-100 rounded-lg p-2">
                    <Briefcase className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">{t.positionLabel}</p>
                    <p className="text-lg font-semibold text-gray-900">{welcomeData.employee.job_details.job_title}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <div className="bg-green-100 rounded-lg p-2">
                    <Building2 className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">{t.departmentLabel}</p>
                    <p className="text-lg font-semibold text-gray-900">{welcomeData.employee.department}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="bg-purple-100 rounded-lg p-2">
                    <Calendar className="h-4 w-4 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">{t.startDateLabel}</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {new Date(welcomeData.employee.job_details.start_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="bg-orange-100 rounded-lg p-2">
                    <Clock className="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">{t.startTimeLabel}</p>
                    <p className="text-lg font-semibold text-gray-900">{welcomeData.employee.job_details.start_time}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="bg-emerald-100 rounded-lg p-2">
                    <span className="text-emerald-600 font-bold text-sm">$</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">{t.payRateLabel}</p>
                    <p className="text-lg font-semibold text-gray-900">
                      ${welcomeData.employee.job_details.pay_rate} {welcomeData.employee.job_details.pay_frequency}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="bg-indigo-100 rounded-lg p-2">
                    <Users className="h-4 w-4 text-indigo-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600">{t.supervisorLabel}</p>
                    <p className="text-lg font-semibold text-gray-900">{welcomeData.employee.job_details.supervisor}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="bg-red-100 rounded-lg p-2">
                  <MapPin className="h-4 w-4 text-red-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">{t.locationLabel}</p>
                  <p className="text-lg font-semibold text-gray-900">{welcomeData.property.address}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Onboarding Steps */}
        <Card className="mb-8 shadow-lg border-0">
          <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-t-lg">
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5" />
              <span>{t.onboardingTitle}</span>
            </CardTitle>
            <p className="text-indigo-100 text-sm">{t.onboardingDesc}</p>
          </CardHeader>
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t.stepsTitle}</h3>
            <div className="space-y-4">
              {t.steps.map((step, index) => {
                const IconComponent = step.icon
                return (
                  <div key={index} className="flex items-center space-x-4 p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full flex items-center justify-center font-semibold">
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      <div className="bg-white rounded-lg p-2 shadow-sm">
                        <IconComponent className="h-5 w-5 text-blue-600" />
                      </div>
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
                )
              })}
            </div>
            <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg text-center">
              <p className="font-semibold text-green-800">{t.totalTime}</p>
            </div>
          </CardContent>
        </Card>

        {/* Important Information */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-yellow-50">
            <CardHeader>
              <CardTitle className="text-orange-800 flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>{t.importantInfo}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-orange-800">
                {t.requirements.map((req, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-orange-600 font-bold">•</span>
                    <span>{req}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
            <CardHeader>
              <CardTitle className="text-blue-800 flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>{t.supportInfo}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-blue-800 mb-4">{t.supportText}</p>
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm">
                  <span className="font-medium">Supervisor:</span>
                  <span>{welcomeData.employee.job_details.supervisor}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <span className="font-medium">Property:</span>
                  <span>{welcomeData.property.name}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Federal Compliance Notice */}
        <Alert className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <Shield className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">
            <strong>{t.federalNotice}:</strong> {t.federalText}<br />
            <span className="text-sm text-blue-600">{t.privacyNotice}</span>
          </AlertDescription>
        </Alert>

        {/* Begin Onboarding Button */}
        <div className="text-center">
          <Card className="bg-gradient-to-r from-green-500 to-emerald-600 border-0 shadow-xl">
            <CardContent className="p-8">
              <h3 className="text-2xl font-bold text-white mb-4">Ready to Begin?</h3>
              <p className="text-green-100 mb-6">Start your onboarding journey and join the {welcomeData.property.name} team!</p>
              <Button
                onClick={handleBeginOnboarding}
                size="lg"
                className="bg-white text-green-600 hover:bg-green-50 px-8 py-4 text-lg font-semibold shadow-lg"
              >
                <div className="flex items-center space-x-2">
                  <Users className="h-6 w-6" />
                  <span>{t.beginButton}</span>
                </div>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}