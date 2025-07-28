import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Building2, 
  Users, 
  Clock, 
  Globe, 
  CheckCircle, 
  Star, 
  Phone,
  Mail,
  FileText,
  Calendar,
  Award,
  Heart
} from 'lucide-react'

export default function WelcomePage() {
  const [language, setLanguage] = useState<'en' | 'es'>('en')
  const [acknowledged, setAcknowledged] = useState(false)

  const handleAcknowledge = () => {
    setAcknowledged(true)
    console.log('Welcome page acknowledged by employee')
  }

  const translations = {
    en: {
      welcomeTitle: 'Welcome to Your Onboarding Journey!',
      subtitle: 'We\'re excited to have you join our team',
      companyName: 'Grand Vista Hotel',
      introMessage: 'Congratulations on your new position! This onboarding process will help you get set up with everything you need to succeed in your new role.',
      
      timelineTitle: 'Your Onboarding Timeline',
      timelineSubtitle: 'Here\'s what to expect during your first steps with us',
      
      steps: [
        {
          title: 'Personal Information',
          description: 'Provide your contact details and emergency information',
          time: '5-7 minutes',
          icon: Users
        },
        {
          title: 'Federal Forms (I-9)',
          description: 'Complete employment eligibility verification',
          time: '8-10 minutes',
          icon: FileText
        },
        {
          title: 'Tax Information (W-4)',
          description: 'Set up your federal tax withholding',
          time: '5-8 minutes',
          icon: Calendar
        },
        {
          title: 'Health Insurance',
          description: 'Choose your health insurance plan and benefits',
          time: '10-15 minutes',
          icon: Heart
        },
        {
          title: 'Company Policies',
          description: 'Review and acknowledge company policies',
          time: '8-12 minutes',
          icon: Award
        },
        {
          title: 'Training & Safety',
          description: 'Complete required training modules',
          time: '15-20 minutes',
          icon: CheckCircle
        }
      ],
      
      totalTime: 'Total estimated time: 45-60 minutes',
      
      importantTitle: 'Important Information',
      requirements: [
        'Have a government-issued photo ID ready (driver\'s license, passport, etc.)',
        'Prepare your Social Security card or work authorization documents',
        'Have your banking information for direct deposit setup',
        'Ensure you have a quiet environment and stable internet connection'
      ],
      
      contactTitle: 'Questions or Need Help?',
      contactInfo: {
        hr: {
          title: 'HR Department',
          phone: '(555) 123-4567',
          email: 'hr@grandvista.com',
          hours: 'Monday-Friday, 8:00 AM - 5:00 PM'
        },
        support: {
          title: 'Technical Support',
          phone: '(555) 123-4568',
          email: 'support@grandvista.com',
          hours: '24/7 Available'
        }
      },
      
      acknowledgmentText: 'I acknowledge that I have read and understand the onboarding process timeline and requirements.',
      acknowledgeButton: 'I Understand - Continue',
      completedMessage: 'Welcome information acknowledged! You may now proceed with your onboarding.',
      
      languageLabel: 'Language / Idioma'
    },
    
    es: {
      welcomeTitle: '¡Bienvenido a Tu Proceso de Incorporación!',
      subtitle: 'Estamos emocionados de tenerte en nuestro equipo',
      companyName: 'Hotel Grand Vista',
      introMessage: '¡Felicitaciones por tu nueva posición! Este proceso de incorporación te ayudará a configurar todo lo que necesitas para tener éxito en tu nuevo rol.',
      
      timelineTitle: 'Tu Cronograma de Incorporación',
      timelineSubtitle: 'Esto es lo que puedes esperar durante tus primeros pasos con nosotros',
      
      steps: [
        {
          title: 'Información Personal',
          description: 'Proporciona tus datos de contacto e información de emergencia',
          time: '5-7 minutos',
          icon: Users
        },
        {
          title: 'Formularios Federales (I-9)',
          description: 'Completa la verificación de elegibilidad de empleo',
          time: '8-10 minutos',
          icon: FileText
        },
        {
          title: 'Información de Impuestos (W-4)',
          description: 'Configura tu retención de impuestos federales',
          time: '5-8 minutos',
          icon: Calendar
        },
        {
          title: 'Seguro de Salud',
          description: 'Elige tu plan de seguro de salud y beneficios',
          time: '10-15 minutos',
          icon: Heart
        },
        {
          title: 'Políticas de la Empresa',
          description: 'Revisa y reconoce las políticas de la empresa',
          time: '8-12 minutos',
          icon: Award
        },
        {
          title: 'Entrenamiento y Seguridad',
          description: 'Completa los módulos de entrenamiento requeridos',
          time: '15-20 minutos',
          icon: CheckCircle
        }
      ],
      
      totalTime: 'Tiempo total estimado: 45-60 minutos',
      
      importantTitle: 'Información Importante',
      requirements: [
        'Ten lista una identificación con foto emitida por el gobierno (licencia de conducir, pasaporte, etc.)',
        'Prepara tu tarjeta de Seguro Social o documentos de autorización de trabajo',
        'Ten tu información bancaria para la configuración de depósito directo',
        'Asegúrate de tener un ambiente tranquilo y conexión estable a internet'
      ],
      
      contactTitle: '¿Preguntas o Necesitas Ayuda?',
      contactInfo: {
        hr: {
          title: 'Departamento de RRHH',
          phone: '(555) 123-4567',
          email: 'hr@grandvista.com',
          hours: 'Lunes-Viernes, 8:00 AM - 5:00 PM'
        },
        support: {
          title: 'Soporte Técnico',
          phone: '(555) 123-4568',
          email: 'support@grandvista.com',
          hours: 'Disponible 24/7'
        }
      },
      
      acknowledgmentText: 'Reconozco que he leído y entiendo el cronograma del proceso de incorporación y los requisitos.',
      acknowledgeButton: 'Entiendo - Continuar',
      completedMessage: '¡Información de bienvenida reconocida! Ahora puedes continuar con tu incorporación.',
      
      languageLabel: 'Language / Idioma'
    }
  }

  const t = translations[language]

  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex flex-col overflow-hidden">
      {/* Header - Fixed height */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white flex-shrink-0">
        <div className="w-full px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-white/20 rounded-lg p-2">
                <Building2 className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-lg font-bold">{t.companyName}</h1>
                <p className="text-blue-100 text-sm">Employee Onboarding</p>
              </div>
            </div>
            
            {/* Language Selection */}
            <div className="flex items-center space-x-2">
              <Globe className="h-4 w-4 text-blue-200" />
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value as 'en' | 'es')}
                className="bg-white/20 border border-white/30 rounded-md px-2 py-1 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white/50"
              >
                <option value="en">English</option>
                <option value="es">Español</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Flexible height */}
      <div className="flex-1 flex flex-col lg:flex-row px-6 py-4 gap-6 min-h-0 max-w-none">
        
        {/* Left Side - Main Welcome Content */}
        <div className="flex-1 flex flex-col space-y-4 min-h-0 min-w-0">
          
          {/* Welcome Message */}
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-3">
              <div className="bg-gradient-to-r from-green-400 to-emerald-500 rounded-full p-2">
                <Star className="h-6 w-6 text-white" />
              </div>
            </div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 mb-2">{t.welcomeTitle}</h1>
            <p className="text-lg text-gray-600 mb-2">{t.subtitle}</p>
            <p className="text-gray-700 text-sm max-w-lg mx-auto">{t.introMessage}</p>
          </div>

          {/* Acknowledgment Status */}
          {acknowledged && (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800 text-sm">
                {t.completedMessage}
              </AlertDescription>
            </Alert>
          )}

          {/* Main Timeline - Takes most space */}
          <Card className="flex-1 shadow-lg border-0 flex flex-col min-h-0">
            <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-t-lg py-3 flex-shrink-0">
              <CardTitle className="flex items-center space-x-2 text-lg">
                <Calendar className="h-5 w-5" />
                <span>{t.timelineTitle}</span>
              </CardTitle>
              <p className="text-indigo-100 text-sm">{t.timelineSubtitle}</p>
            </CardHeader>
            <CardContent className="flex-1 p-4 overflow-y-auto">
              <div className="space-y-3">
                {t.steps.map((step, index) => {
                  const IconComponent = step.icon
                  return (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                          {index + 1}
                        </div>
                      </div>
                      <div className="flex-shrink-0">
                        <div className="bg-white rounded-lg p-1.5 shadow-sm">
                          <IconComponent className="h-4 w-4 text-blue-600" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-gray-900 text-sm">{step.title}</h4>
                        <p className="text-xs text-gray-600 truncate">{step.description}</p>
                      </div>
                      <Badge variant="secondary" className="flex items-center space-x-1 text-xs px-2 py-1">
                        <Clock className="h-3 w-3" />
                        <span>{step.time}</span>
                      </Badge>
                    </div>
                  )
                })}
              </div>
              <div className="mt-4 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg text-center">
                <p className="font-semibold text-green-800 text-sm">{t.totalTime}</p>
              </div>
            </CardContent>
          </Card>

          {/* Digital Acknowledgment - Bottom */}
          <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200 flex-shrink-0">
            <CardContent className="p-4 text-center">
              <h3 className="text-lg font-bold text-purple-900 mb-2">Digital Acknowledgment</h3>
              <p className="text-purple-800 mb-4 text-sm">
                {t.acknowledgmentText}
              </p>
              
              {!acknowledged ? (
                <Button
                  onClick={handleAcknowledge}
                  size="lg"
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 font-semibold"
                >
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>{t.acknowledgeButton}</span>
                  </div>
                </Button>
              ) : (
                <div className="flex items-center justify-center space-x-2 text-green-600">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-semibold">Acknowledged</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Side - Secondary Information (Fixed width) */}
        <div className="w-full lg:w-80 xl:w-96 flex flex-col space-y-2 flex-shrink-0">
          
          {/* Important Information - Compact */}
          <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-yellow-50 flex-shrink-0">
            <CardHeader className="py-1.5 pb-1">
              <CardTitle className="text-orange-800 flex items-center space-x-2 text-sm">
                <FileText className="h-4 w-4" />
                <span>{t.importantTitle}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-0 pb-2">
              <ul className="space-y-0.5 text-xs text-orange-800">
                {t.requirements.map((req, index) => (
                  <li key={index} className="flex items-start space-x-1">
                    <span className="text-orange-600 font-bold text-xs">•</span>
                    <span className="leading-tight">{req}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Contact Information - Compact */}
          <div className="space-y-1.5 flex-1">
            <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
              <CardHeader className="py-1.5 pb-1">
                <CardTitle className="text-blue-800 flex items-center space-x-2 text-sm">
                  <Users className="h-4 w-4" />
                  <span>{t.contactInfo.hr.title}</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0 pb-2 text-blue-800">
                <div className="space-y-1 text-xs">
                  <div className="flex items-center space-x-1">
                    <Phone className="h-3 w-3" />
                    <span>{t.contactInfo.hr.phone}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Mail className="h-3 w-3" />
                    <span className="truncate">{t.contactInfo.hr.email}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>{t.contactInfo.hr.hours}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
              <CardHeader className="py-1.5 pb-1">
                <CardTitle className="text-green-800 flex items-center space-x-2 text-sm">
                  <FileText className="h-4 w-4" />
                  <span>{t.contactInfo.support.title}</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0 pb-2 text-green-800">
                <div className="space-y-1 text-xs">
                  <div className="flex items-center space-x-1">
                    <Phone className="h-3 w-3" />
                    <span>{t.contactInfo.support.phone}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Mail className="h-3 w-3" />
                    <span className="truncate">{t.contactInfo.support.email}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3" />
                    <span>{t.contactInfo.support.hours}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}