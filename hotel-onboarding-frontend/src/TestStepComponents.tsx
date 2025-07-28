import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import WelcomeStep from './pages/onboarding/WelcomeStep'
import PersonalInfoStep from './pages/onboarding/PersonalInfoStep'
import I9Section1Step from './pages/onboarding/I9Section1Step'
import JobDetailsStep from './pages/onboarding/JobDetailsStep'

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
    stepData: progress
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
    { id: 'i9-section1', title: 'I-9 Section 1' }
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