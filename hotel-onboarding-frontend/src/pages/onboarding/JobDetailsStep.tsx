import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { CheckCircle, Briefcase, Calendar, DollarSign, Building } from 'lucide-react'

interface StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function JobDetailsStep(props: StepProps) {
  const { 
    currentStep, 
    progress, 
    markStepComplete, 
    saveProgress, 
    language = 'en',
    employee,
    property
  } = props
  
  const [isComplete, setIsComplete] = useState(false)
  const [jobDetails, setJobDetails] = useState({
    position: employee?.position || '',
    department: employee?.department || '',
    startDate: employee?.hire_date || '',
    payRate: employee?.pay_rate || '',
    employmentType: employee?.employment_type || 'full-time',
    supervisor: employee?.supervisor || '',
    workLocation: property?.address || '',
    scheduleConfirmed: false,
    jobDescriptionReviewed: false,
    compensationConfirmed: false
  })

  // Load existing data from progress
  useEffect(() => {
    const existingData = progress.stepData?.['job_details']
    if (existingData) {
      setJobDetails({ ...jobDetails, ...existingData.jobDetails })
      setIsComplete(existingData.completed || false)
    }
  }, [progress])

  const handleInputChange = (field: string, value: any) => {
    setJobDetails(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = () => {
    if (!jobDetails.scheduleConfirmed || !jobDetails.jobDescriptionReviewed || !jobDetails.compensationConfirmed) {
      alert('Please confirm all job details before proceeding.')
      return
    }

    setIsComplete(true)
    const stepData = {
      jobDetails,
      completed: true,
      completedAt: new Date().toISOString()
    }
    markStepComplete('job_details', stepData)
    saveProgress()
  }

  const translations = {
    en: {
      title: 'Confirm Your Job Details',
      subtitle: 'Verify Your Employment Information',
      description: 'Please review and confirm the details of your new position.',
      completedNotice: 'Job details confirmed successfully!',
      positionInfo: 'Position Information',
      position: 'Job Title',
      department: 'Department',
      supervisor: 'Direct Supervisor',
      employmentDetails: 'Employment Details',
      startDate: 'Start Date',
      payRate: 'Pay Rate',
      employmentType: 'Employment Type',
      workLocation: 'Work Location',
      confirmations: 'Required Confirmations',
      scheduleConfirmed: 'I confirm that I understand my work schedule and have discussed any questions with my supervisor',
      jobDescriptionReviewed: 'I have reviewed my job description and understand my responsibilities',
      compensationConfirmed: 'I confirm that my compensation and benefits have been clearly explained',
      continueButton: 'Confirm Job Details',
      estimatedTime: 'Estimated time: 3 minutes'
    },
    es: {
      title: 'Confirme los Detalles de Su Trabajo',
      subtitle: 'Verifique Su Información de Empleo',
      description: 'Por favor revise y confirme los detalles de su nueva posición.',
      completedNotice: '¡Detalles del trabajo confirmados exitosamente!',
      positionInfo: 'Información de la Posición',
      position: 'Título del Trabajo',
      department: 'Departamento',
      supervisor: 'Supervisor Directo',
      employmentDetails: 'Detalles del Empleo',
      startDate: 'Fecha de Inicio',
      payRate: 'Tarifa de Pago',
      employmentType: 'Tipo de Empleo',
      workLocation: 'Ubicación de Trabajo',
      confirmations: 'Confirmaciones Requeridas',
      scheduleConfirmed: 'Confirmo que entiendo mi horario de trabajo y he discutido cualquier pregunta con mi supervisor',
      jobDescriptionReviewed: 'He revisado mi descripción de trabajo y entiendo mis responsabilidades',
      compensationConfirmed: 'Confirmo que mi compensación y beneficios han sido claramente explicados',
      continueButton: 'Confirmar Detalles del Trabajo',
      estimatedTime: 'Tiempo estimado: 3 minutos'
    }
  }

  const t = translations[language]

  return (
    <div className="space-y-6">
      {/* Step Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Briefcase className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">{t.title}</h1>
        </div>
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

      {/* Position Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Briefcase className="h-5 w-5 text-blue-600" />
            <span>{t.positionInfo}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="position">{t.position}</Label>
            <Input
              id="position"
              value={jobDetails.position}
              onChange={(e) => handleInputChange('position', e.target.value)}
              className="bg-gray-50"
              readOnly
            />
          </div>
          <div>
            <Label htmlFor="department">{t.department}</Label>
            <Input
              id="department"
              value={jobDetails.department}
              onChange={(e) => handleInputChange('department', e.target.value)}
              className="bg-gray-50"
              readOnly
            />
          </div>
          <div>
            <Label htmlFor="supervisor">{t.supervisor}</Label>
            <Input
              id="supervisor"
              value={jobDetails.supervisor}
              onChange={(e) => handleInputChange('supervisor', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Employment Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-green-600" />
            <span>{t.employmentDetails}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="startDate">{t.startDate}</Label>
            <Input
              id="startDate"
              type="date"
              value={jobDetails.startDate}
              onChange={(e) => handleInputChange('startDate', e.target.value)}
              className="bg-gray-50"
              readOnly
            />
          </div>
          <div>
            <Label htmlFor="payRate">{t.payRate}</Label>
            <Input
              id="payRate"
              value={jobDetails.payRate}
              onChange={(e) => handleInputChange('payRate', e.target.value)}
              className="bg-gray-50"
              readOnly
            />
          </div>
          <div>
            <Label htmlFor="employmentType">{t.employmentType}</Label>
            <Input
              id="employmentType"
              value={jobDetails.employmentType}
              onChange={(e) => handleInputChange('employmentType', e.target.value)}
              className="bg-gray-50"
              readOnly
            />
          </div>
          <div>
            <Label htmlFor="workLocation">{t.workLocation}</Label>
            <Input
              id="workLocation"
              value={jobDetails.workLocation}
              onChange={(e) => handleInputChange('workLocation', e.target.value)}
              className="bg-gray-50"
              readOnly
            />
          </div>
        </CardContent>
      </Card>

      {/* Required Confirmations */}
      <Card className="border-orange-200 bg-orange-50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center space-x-2 text-orange-800">
            <CheckCircle className="h-5 w-5" />
            <span>{t.confirmations}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start space-x-3">
            <Checkbox
              id="scheduleConfirmed"
              checked={jobDetails.scheduleConfirmed}
              onCheckedChange={(checked) => handleInputChange('scheduleConfirmed', checked)}
              className="mt-1"
            />
            <label
              htmlFor="scheduleConfirmed"
              className="text-sm text-orange-800 leading-relaxed cursor-pointer"
            >
              {t.scheduleConfirmed}
            </label>
          </div>
          
          <div className="flex items-start space-x-3">
            <Checkbox
              id="jobDescriptionReviewed"
              checked={jobDetails.jobDescriptionReviewed}
              onCheckedChange={(checked) => handleInputChange('jobDescriptionReviewed', checked)}
              className="mt-1"
            />
            <label
              htmlFor="jobDescriptionReviewed"
              className="text-sm text-orange-800 leading-relaxed cursor-pointer"
            >
              {t.jobDescriptionReviewed}
            </label>
          </div>
          
          <div className="flex items-start space-x-3">
            <Checkbox
              id="compensationConfirmed"
              checked={jobDetails.compensationConfirmed}
              onCheckedChange={(checked) => handleInputChange('compensationConfirmed', checked)}
              className="mt-1"
            />
            <label
              htmlFor="compensationConfirmed"
              className="text-sm text-orange-800 leading-relaxed cursor-pointer"
            >
              {t.compensationConfirmed}
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-center">
        <Button
          onClick={handleSubmit}
          disabled={!jobDetails.scheduleConfirmed || !jobDetails.jobDescriptionReviewed || !jobDetails.compensationConfirmed || isComplete}
          size="lg"
          className="px-8 py-3 text-lg font-semibold"
        >
          {isComplete ? (
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5" />
              <span>Details Confirmed</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Briefcase className="h-5 w-5" />
              <span>{t.continueButton}</span>
            </div>
          )}
        </Button>
      </div>

      {/* Estimated Time */}
      <div className="text-center text-sm text-gray-500">
        <p>{t.estimatedTime}</p>
      </div>
    </div>
  )
}