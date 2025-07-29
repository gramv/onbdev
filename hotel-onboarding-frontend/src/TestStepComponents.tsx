import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import WelcomeStep from './pages/onboarding/WelcomeStep'
import PersonalInfoStep from './pages/onboarding/PersonalInfoStep'
import I9Section1Step from './pages/onboarding/I9Section1Step'
import JobDetailsStep from './pages/onboarding/JobDetailsStep'
import DocumentUploadStep from './pages/onboarding/DocumentUploadStep'
import W4FormStep from './pages/onboarding/W4FormStep'
import DirectDepositStep from './pages/onboarding/DirectDepositStep'
import HealthInsuranceStep from './pages/onboarding/HealthInsuranceStep'
import EmergencyContactsStep from './pages/onboarding/EmergencyContactsStep'
import CompanyPoliciesStep from './pages/onboarding/CompanyPoliciesStep'
import BackgroundCheckStep from './pages/onboarding/BackgroundCheckStep'
import PhotoCaptureStep from './pages/onboarding/PhotoCaptureStep'
import I9SupplementsStep from './pages/onboarding/I9SupplementsStep'
import TraffickingAwarenessStep from './pages/onboarding/TrafficakingAwarenessStep'
import WeaponsPolicyStep from './pages/onboarding/WeaponsPolicyStep'
import FinalReviewStep from './pages/onboarding/FinalReviewStep'
import W4ReviewSignStep from './pages/onboarding/W4ReviewSignStep'
import I9ReviewSignStep from './pages/onboarding/I9ReviewSignStep'
import EmployeeReviewStep from './pages/onboarding/EmployeeReviewStep'

interface TestStepData {
  [key: string]: {
    completed: boolean
    data?: any
  }
}

export default function TestStepComponents() {
  const [currentStep, setCurrentStep] = useState('welcome')
  const [progress, setProgress] = useState<TestStepData>({})
  const [language, setLanguage] = useState<'en' | 'es'>('en')

  const mockEmployee = {
    name: 'John Doe',
    position: 'Front Desk Agent',
    department: 'Guest Services',
    hire_date: '2024-01-15',
    pay_rate: '$18.00/hour',
    employment_type: 'full-time',
    supervisor: 'Jane Smith'
  }

  const mockProperty = {
    name: 'Grand Vista Hotel',
    address: '123 Main St, City, State 12345'
  }

  const mockCurrentStep = {
    id: currentStep,
    title: 'Current Step'
  }

  const mockProgress = {
    stepData: progress,
    completedSteps: Object.keys(progress).filter(key => progress[key]?.completed)
  }

  const markStepComplete = (stepId: string, data?: any) => {
    console.log('Step completed:', stepId, data)
    setProgress(prev => ({
      ...prev,
      [stepId]: {
        completed: true,
        data
      }
    }))
  }

  const saveProgress = (stepId: string, data?: any) => {
    console.log('Progress saved:', stepId, data)
    setProgress(prev => ({
      ...prev,
      [stepId]: {
        completed: prev[stepId]?.completed || false,
        data
      }
    }))
  }

  const steps = [
    { id: 'welcome', title: 'Welcome & Language' },
    { id: 'job_details', title: 'Job Details' },
    { id: 'personal-info', title: 'Personal Info' },
    { id: 'i9-section1', title: 'I-9 Section 1' },
    { id: 'i9-supplements', title: 'I-9 Supplements' },
    { id: 'document-upload', title: 'Document Upload' },
    { id: 'w4-form', title: 'W-4 Tax Form' },
    { id: 'direct-deposit', title: 'Direct Deposit' },
    { id: 'health-insurance', title: 'Health Insurance' },
    { id: 'emergency-contacts', title: 'Emergency Contacts' },
    { id: 'company-policies', title: 'Company Policies' },
    { id: 'trafficking-awareness', title: 'Human Trafficking Awareness' },
    { id: 'weapons-policy', title: 'Weapons Policy' },
    { id: 'background-check', title: 'Background Check' },
    { id: 'photo-capture', title: 'Photo Capture' },
    { id: 'final-review', title: 'Final Review' },
    { id: 'w4-review-sign', title: 'W-4 Review & Sign' },
    { id: 'i9-review-sign', title: 'I-9 Review & Sign' },
    { id: 'employee-review', title: 'Employee Review' }
  ]

  const renderCurrentStep = () => {
    const commonProps = {
      currentStep: mockCurrentStep,
      progress: mockProgress,
      markStepComplete,
      saveProgress,
      language,
      employee: mockEmployee,
      property: mockProperty
    }

    switch (currentStep) {
      case 'welcome':
        return <WelcomeStep {...commonProps} />
      case 'job_details':
        return <JobDetailsStep {...commonProps} />
      case 'personal-info':
        return <PersonalInfoStep {...commonProps} />
      case 'i9-section1':
        return <I9Section1Step {...commonProps} />
      case 'i9-supplements':
        return <I9SupplementsStep {...commonProps} />
      case 'document-upload':
        return <DocumentUploadStep {...commonProps} />
      case 'w4-form':
        return <W4FormStep {...commonProps} />
      case 'direct-deposit':
        return <DirectDepositStep {...commonProps} />
      case 'health-insurance':
        return <HealthInsuranceStep {...commonProps} />
      case 'emergency-contacts':
        return <EmergencyContactsStep {...commonProps} />
      case 'company-policies':
        return <CompanyPoliciesStep {...commonProps} />
      case 'trafficking-awareness':
        return <TraffickingAwarenessStep {...commonProps} />
      case 'weapons-policy':
        return <WeaponsPolicyStep {...commonProps} />
      case 'background-check':
        return <BackgroundCheckStep {...commonProps} />
      case 'photo-capture':
        return <PhotoCaptureStep {...commonProps} />
      case 'final-review':
        return <FinalReviewStep {...commonProps} />
      case 'w4-review-sign':
        return <W4ReviewSignStep {...commonProps} />
      case 'i9-review-sign':
        return <I9ReviewSignStep {...commonProps} />
      case 'employee-review':
        return <EmployeeReviewStep {...commonProps} ONBOARDING_STEPS={steps} />
      default:
        return <div>Unknown step: {currentStep}</div>
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Step Component Test</h1>
          <p className="text-gray-600">Testing the fixed onboarding step components</p>
        </div>

        {/* Step Navigation */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Step Navigation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-4">
              {steps.map(step => (
                <Button
                  key={step.id}
                  variant={currentStep === step.id ? 'default' : 'outline'}
                  onClick={() => setCurrentStep(step.id)}
                  className="flex items-center space-x-2"
                >
                  <span>{step.title}</span>
                  {progress[step.id]?.completed && (
                    <Badge variant="secondary" className="ml-2">✓</Badge>
                  )}
                </Button>
              ))}
            </div>
            
            {/* Language Toggle */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Language:</span>
              <Button
                variant={language === 'en' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setLanguage('en')}
              >
                English
              </Button>
              <Button
                variant={language === 'es' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setLanguage('es')}
              >
                Español
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Current Step Content */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>Current Step: {steps.find(s => s.id === currentStep)?.title}</span>
              <Badge variant="outline">{currentStep}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {renderCurrentStep()}
          </CardContent>
        </Card>

        {/* Debug Info */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Debug Info</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto">
              {JSON.stringify({ currentStep, progress, language }, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}