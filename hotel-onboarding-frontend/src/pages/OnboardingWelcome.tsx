import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { useLanguage } from '@/contexts/LanguageContext'
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
  Coffee,
  Sparkles,
  PartyPopper,
  Rocket,
  Target,
  ArrowRight,
  Phone,
  Mail,
  User,
  DollarSign
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
  const { token: urlToken } = useParams()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { language, setLanguage, t } = useLanguage()
  const [welcomeData, setWelcomeData] = useState<WelcomeData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [onboardingToken, setOnboardingToken] = useState<string | null>(null)

  useEffect(() => {
    // Get token from URL params or search params
    const token = urlToken || searchParams.get('token')
    const empId = searchParams.get('employee_id')
    
    if (token) {
      setOnboardingToken(token)
      // For Task 3, we use the token to fetch welcome data
      fetchWelcomeDataByToken(token)
    } else if (empId) {
      // Fallback for legacy routes
      fetchWelcomeData(empId, token)
    }
  }, [urlToken, searchParams])

  const fetchWelcomeDataByToken = async (token: string) => {
    try {
      setLoading(true)
      
      // First, try the new token-based endpoint
      try {
        const response = await axios.get(`/api/onboarding/welcome/${token}`)
        setWelcomeData(response.data)
        setError('')
        return
      } catch (tokenErr: any) {
        // If token endpoint fails, fall back to getting session info first
        console.log('Token endpoint not available, trying fallback approach')
      }
      
      // Fallback: Get session info to find employee_id, then use existing endpoint
      try {
        const sessionResponse = await axios.get(`/api/onboarding/session/${token}`)
        const sessionData = sessionResponse.data
        const employeeId = sessionData.employee_id
        
        if (employeeId) {
          const response = await axios.get(`/api/employees/${employeeId}/welcome-data`, {
            params: { token }
          })
          setWelcomeData(response.data)
          setError('')
          return
        }
      } catch (sessionErr: any) {
        console.log('Session endpoint also failed, showing error')
      }
      
      // If all approaches fail, show error
      setError('Unable to load your onboarding information. Please contact HR for assistance.')
      
    } catch (err: any) {
      console.error('Error fetching welcome data by token:', err)
      if (err.response?.status === 401) {
        setError('Your onboarding link has expired or is invalid. Please contact HR for a new link.')
      } else if (err.response?.status === 404) {
        setError('Invalid onboarding token. Please contact HR for assistance.')
      } else {
        setError('Unable to load your onboarding information. Please contact HR for assistance.')
      }
    } finally {
      setLoading(false)
    }
  }

  const fetchWelcomeData = async (empId: string, token?: string | null) => {
    try {
      setLoading(true)
      
      // Use token as query parameter if available, otherwise use headers for authentication
      const params = token ? { token } : {}
      const headers = !token ? {} : {} // Let axios handle authentication automatically if user is logged in
      
      const response = await axios.get(`/api/employees/${empId}/welcome-data`, { 
        params,
        headers 
      })
      
      setWelcomeData(response.data)
      setError('')
    } catch (err: any) {
      console.error('Error fetching welcome data:', err)
      if (err.response?.status === 401) {
        setError('Your onboarding link has expired or is invalid. Please contact HR for a new link.')
      } else if (err.response?.status === 404) {
        setError('Employee record not found. Please contact HR for assistance.')
      } else {
        setError('Unable to load your onboarding information. Please contact HR for assistance.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleBeginOnboarding = async () => {
    try {
      // Use the token from URL or the stored onboarding token
      const token = urlToken || onboardingToken
      const empId = welcomeData?.employee?.id || searchParams.get('employee_id')
      
      if (!token && !empId) {
        setError('Unable to start onboarding. Please contact HR for assistance.')
        return
      }
      
      // Navigate to onboarding with token or employee ID
      const navigationUrl = token 
        ? `/onboarding/personal-info?token=${token}`
        : `/onboarding/personal-info?employee_id=${empId}`
      
      navigate(navigationUrl)
    } catch (err: any) {
      console.error('Error navigating to onboarding:', err)
      setError('Unable to start onboarding. Please contact HR for assistance.')
    }
  }

  // Enhanced translations for the welcome page
  const getTranslations = () => {
    const baseTranslations = {
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
        privacyNotice: 'Your information is secure and encrypted',
        readyToBegin: 'Ready to Begin?',
        joinTeamMessage: 'Start your onboarding journey and join our amazing team!',
        contactInfo: 'Contact Information'
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
        privacyNotice: 'Tu información está segura y encriptada',
        readyToBegin: '¿Listo para Comenzar?',
        joinTeamMessage: '¡Comienza tu proceso de incorporación y únete a nuestro increíble equipo!',
        contactInfo: 'Información de Contacto'
      }
    }
    return baseTranslations[language]
  }

  const translations = getTranslations()

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <Card className="max-w-md w-full mx-4 shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
          <CardContent className="p-8 text-center">
            <div className="mb-6">
              <div className="relative">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <Sparkles className="h-6 w-6 text-blue-600 animate-pulse" />
                </div>
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Preparing Your Welcome</h3>
            <p className="text-gray-600 mb-4">Loading your onboarding information...</p>
            <div className="flex justify-center space-x-1">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 flex items-center justify-center p-6">
        <Card className="max-w-lg w-full shadow-2xl border-0 bg-white/90 backdrop-blur-sm">
          <CardContent className="p-8">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-r from-red-100 to-orange-100 mb-6">
                <svg className="h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 18.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Unable to Load Information</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">{error}</p>
              <div className="space-y-3">
                <Button 
                  onClick={() => {
                    const empId = employeeId || searchParams.get('employee_id')
                    const token = searchParams.get('token')
                    if (empId) fetchWelcomeData(empId, token)
                  }} 
                  variant="default"
                  className="w-full"
                >
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
                <p className="text-sm text-gray-500">
                  If the problem persists, please contact HR for assistance.
                </p>
              </div>
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Enhanced Header with Property Branding */}
      <div className="relative bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-700 text-white overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-black/10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>
        
        <div className="relative max-w-7xl mx-auto px-6 py-12">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
            <div className="flex items-center space-x-6">
              <div className="bg-white/20 backdrop-blur-sm rounded-2xl p-4 shadow-lg">
                <Building2 className="h-12 w-12" />
              </div>
              <div>
                <h1 className="text-3xl lg:text-4xl font-bold mb-2">{welcomeData.property.name}</h1>
                <div className="flex items-center space-x-3 text-blue-100">
                  <MapPin className="h-5 w-5" />
                  <span className="text-lg">{welcomeData.property.address}</span>
                </div>
              </div>
            </div>
            
            {/* Enhanced Language Selection */}
            <div className="flex items-center space-x-4 bg-white/10 backdrop-blur-sm rounded-xl px-6 py-3">
              <Globe className="h-5 w-5 text-blue-200" />
              <span className="text-sm font-medium">{translations.languageSelection}:</span>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value as 'en' | 'es')}
                className="bg-white/20 border border-white/30 rounded-lg px-4 py-2 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-white/50 focus:bg-white/30 transition-all"
              >
                <option value="en" className="text-gray-900">English</option>
                <option value="es" className="text-gray-900">Español</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Enhanced Welcome Section */}
        <div className="text-center mb-12">
          <div className="mb-8">
            {/* Animated Welcome Icon */}
            <div className="flex items-center justify-center space-x-3 mb-6">
              <div className="relative">
                <div className="bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500 rounded-full p-4 shadow-lg animate-pulse">
                  <PartyPopper className="h-10 w-10 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full p-1">
                  <Sparkles className="h-4 w-4 text-white animate-spin" />
                </div>
              </div>
            </div>
            
            {/* Welcome Text */}
            <div className="space-y-4">
              <h1 className="text-5xl lg:text-6xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-4">
                {translations.welcomeTitle}
              </h1>
              <h2 className="text-3xl lg:text-4xl font-semibold text-blue-600 mb-3">
                {translations.personalGreeting}
              </h2>
              <p className="text-xl lg:text-2xl text-gray-700 mb-2 font-medium">
                {translations.congratulations}
              </p>
              <p className="text-lg lg:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                {translations.propertyWelcome}
              </p>
            </div>
          </div>

          {/* Enhanced Celebration Icons */}
          <div className="flex flex-wrap justify-center gap-8 mb-12">
            <div className="text-center group">
              <div className="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-2xl p-4 mb-3 mx-auto w-fit shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                <Award className="h-8 w-8 text-yellow-600" />
              </div>
              <p className="text-sm font-semibold text-gray-700">New Team Member</p>
            </div>
            <div className="text-center group">
              <div className="bg-gradient-to-r from-blue-100 to-indigo-100 rounded-2xl p-4 mb-3 mx-auto w-fit shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                <Briefcase className="h-8 w-8 text-blue-600" />
              </div>
              <p className="text-sm font-semibold text-gray-700">Ready to Start</p>
            </div>
            <div className="text-center group">
              <div className="bg-gradient-to-r from-green-100 to-emerald-100 rounded-2xl p-4 mb-3 mx-auto w-fit shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                <Rocket className="h-8 w-8 text-green-600" />
              </div>
              <p className="text-sm font-semibold text-gray-700">Welcome Aboard</p>
            </div>
            <div className="text-center group">
              <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-2xl p-4 mb-3 mx-auto w-fit shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                <Target className="h-8 w-8 text-purple-600" />
              </div>
              <p className="text-sm font-semibold text-gray-700">Let's Begin</p>
            </div>
          </div>
        </div>

        {/* Enhanced Job Details Card */}
        <Card className="mb-12 shadow-2xl border-0 bg-white/80 backdrop-blur-sm overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white relative">
            <div className="absolute inset-0 bg-black/10"></div>
            <CardTitle className="relative flex items-center space-x-3 text-xl">
              <div className="bg-white/20 rounded-lg p-2">
                <Briefcase className="h-6 w-6" />
              </div>
              <span>{translations.jobDetailsTitle}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8">
            <div className="grid lg:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl">
                  <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-3 shadow-lg">
                    <Briefcase className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{translations.positionLabel}</p>
                    <p className="text-xl font-bold text-gray-900">{welcomeData.employee.job_details.job_title}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
                  <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-3 shadow-lg">
                    <Building2 className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{translations.departmentLabel}</p>
                    <p className="text-xl font-bold text-gray-900">{welcomeData.employee.department}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl">
                  <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-3 shadow-lg">
                    <Calendar className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{translations.startDateLabel}</p>
                    <p className="text-xl font-bold text-gray-900">
                      {new Date(welcomeData.employee.job_details.start_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl">
                  <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl p-3 shadow-lg">
                    <Clock className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{translations.startTimeLabel}</p>
                    <p className="text-xl font-bold text-gray-900">{welcomeData.employee.job_details.start_time}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl">
                  <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-xl p-3 shadow-lg">
                    <DollarSign className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{translations.payRateLabel}</p>
                    <p className="text-xl font-bold text-gray-900">
                      ${welcomeData.employee.job_details.pay_rate} {welcomeData.employee.job_details.pay_frequency}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl">
                  <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-xl p-3 shadow-lg">
                    <User className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{translations.supervisorLabel}</p>
                    <p className="text-xl font-bold text-gray-900">{welcomeData.employee.job_details.supervisor}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Information Section */}
            <div className="mt-8 pt-8 border-t border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Phone className="h-5 w-5 mr-2 text-blue-600" />
                {translations.contactInfo}
              </h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-red-50 to-pink-50 rounded-xl">
                  <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-xl p-3 shadow-lg">
                    <MapPin className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">{translations.locationLabel}</p>
                    <p className="text-lg font-bold text-gray-900">{welcomeData.property.address}</p>
                  </div>
                </div>
                
                {welcomeData.applicant_data.email && (
                  <div className="flex items-center space-x-4 p-4 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl">
                    <div className="bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-xl p-3 shadow-lg">
                      <Mail className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Email</p>
                      <p className="text-lg font-bold text-gray-900">{welcomeData.applicant_data.email}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Onboarding Steps */}
        <Card className="mb-12 shadow-2xl border-0 bg-white/80 backdrop-blur-sm overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white relative">
            <div className="absolute inset-0 bg-black/10"></div>
            <CardTitle className="relative flex items-center space-x-3 text-xl">
              <div className="bg-white/20 rounded-lg p-2">
                <FileText className="h-6 w-6" />
              </div>
              <span>{translations.onboardingTitle}</span>
            </CardTitle>
            <p className="relative text-indigo-100 text-lg mt-2">{translations.onboardingDesc}</p>
          </CardHeader>
          <CardContent className="p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">{translations.stepsTitle}</h3>
            <div className="space-y-6">
              {translations.steps.map((step, index) => {
                const IconComponent = step.icon
                const gradients = [
                  'from-blue-500 to-blue-600',
                  'from-green-500 to-green-600', 
                  'from-purple-500 to-purple-600',
                  'from-orange-500 to-orange-600',
                  'from-pink-500 to-pink-600',
                  'from-indigo-500 to-indigo-600'
                ]
                const bgGradients = [
                  'from-blue-50 to-indigo-50',
                  'from-green-50 to-emerald-50',
                  'from-purple-50 to-pink-50', 
                  'from-orange-50 to-yellow-50',
                  'from-pink-50 to-rose-50',
                  'from-indigo-50 to-blue-50'
                ]
                
                return (
                  <div key={index} className={`flex items-center space-x-6 p-6 bg-gradient-to-r ${bgGradients[index]} rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02]`}>
                    <div className="flex-shrink-0">
                      <div className={`w-14 h-14 bg-gradient-to-r ${gradients[index]} text-white rounded-full flex items-center justify-center font-bold text-lg shadow-lg`}>
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      <div className="bg-white rounded-xl p-3 shadow-md">
                        <IconComponent className="h-7 w-7 text-gray-700" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold text-gray-900 text-lg mb-1">{step.title}</h4>
                      <p className="text-gray-600 leading-relaxed">{step.desc}</p>
                    </div>
                    <Badge variant="secondary" className="flex items-center space-x-2 px-4 py-2 bg-white/80 backdrop-blur-sm shadow-md">
                      <Clock className="h-4 w-4" />
                      <span className="font-semibold">{step.time}</span>
                    </Badge>
                  </div>
                )
              })}
            </div>
            <div className="mt-8 p-6 bg-gradient-to-r from-green-100 via-emerald-100 to-teal-100 rounded-2xl text-center shadow-lg">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <Clock className="h-6 w-6 text-green-700" />
                <p className="font-bold text-green-800 text-xl">{translations.totalTime}</p>
              </div>
              <p className="text-green-700">Take your time - we're here to help every step of the way!</p>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Important Information */}
        <div className="grid lg:grid-cols-2 gap-8 mb-12">
          <Card className="border-0 bg-gradient-to-br from-orange-50 via-yellow-50 to-amber-50 shadow-2xl overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-orange-500 to-yellow-500 text-white relative">
              <div className="absolute inset-0 bg-black/10"></div>
              <CardTitle className="relative text-xl flex items-center space-x-3">
                <div className="bg-white/20 rounded-lg p-2">
                  <FileText className="h-6 w-6" />
                </div>
                <span>{translations.importantInfo}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <ul className="space-y-4">
                {translations.requirements.map((req, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mt-0.5">
                      <CheckCircle className="h-4 w-4 text-white" />
                    </div>
                    <span className="text-gray-700 leading-relaxed">{req}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="border-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 shadow-2xl overflow-hidden">
            <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-500 text-white relative">
              <div className="absolute inset-0 bg-black/10"></div>
              <CardTitle className="relative text-xl flex items-center space-x-3">
                <div className="bg-white/20 rounded-lg p-2">
                  <Users className="h-6 w-6" />
                </div>
                <span>{translations.supportInfo}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              <p className="text-gray-700 mb-6 leading-relaxed text-lg">{translations.supportText}</p>
              <div className="space-y-4">
                <div className="flex items-center space-x-4 p-4 bg-white/60 rounded-xl">
                  <div className="bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg p-2">
                    <User className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <span className="font-semibold text-gray-600 text-sm uppercase tracking-wide">Supervisor:</span>
                    <p className="font-bold text-gray-900">{welcomeData.employee.job_details.supervisor}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4 p-4 bg-white/60 rounded-xl">
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-2">
                    <Building2 className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <span className="font-semibold text-gray-600 text-sm uppercase tracking-wide">Property:</span>
                    <p className="font-bold text-gray-900">{welcomeData.property.name}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Federal Compliance Notice */}
        <Alert className="mb-12 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-0 shadow-lg rounded-2xl p-6">
          <div className="flex items-start space-x-4">
            <div className="bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl p-3 shadow-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <AlertDescription className="text-gray-800 leading-relaxed">
              <div className="mb-3">
                <strong className="text-lg text-blue-800">{translations.federalNotice}:</strong>
                <p className="mt-2 text-gray-700">{translations.federalText}</p>
              </div>
              <div className="flex items-center space-x-2 text-sm text-blue-600 bg-blue-100 rounded-lg px-3 py-2 w-fit">
                <Shield className="h-4 w-4" />
                <span className="font-semibold">{translations.privacyNotice}</span>
              </div>
            </AlertDescription>
          </div>
        </Alert>

        {/* Enhanced Begin Onboarding Section */}
        <div className="text-center">
          <Card className="bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 border-0 shadow-2xl overflow-hidden relative">
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-black/10">
              <div className="absolute inset-0" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              }} />
            </div>
            
            <CardContent className="relative p-12">
              <div className="mb-8">
                <div className="flex items-center justify-center space-x-3 mb-6">
                  <div className="bg-white/20 rounded-full p-4">
                    <Rocket className="h-12 w-12 text-white" />
                  </div>
                  <div className="bg-white/20 rounded-full p-2">
                    <Sparkles className="h-6 w-6 text-white animate-spin" />
                  </div>
                </div>
                <h3 className="text-4xl font-bold text-white mb-4">{translations.readyToBegin}</h3>
                <p className="text-xl text-green-100 mb-8 max-w-2xl mx-auto leading-relaxed">
                  {translations.joinTeamMessage}
                </p>
              </div>
              
              <Button
                onClick={handleBeginOnboarding}
                size="xl"
                className="bg-white text-green-600 hover:bg-green-50 hover:text-green-700 px-12 py-6 text-xl font-bold shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300"
              >
                <div className="flex items-center space-x-3">
                  <ArrowRight className="h-8 w-8" />
                  <span>{translations.beginButton}</span>
                </div>
              </Button>
              
              <div className="mt-8 flex items-center justify-center space-x-6 text-green-100">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5" />
                  <span>Secure & Encrypted</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>45 Minutes</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Federally Compliant</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}