import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  CheckCircle, 
  Users, 
  FileText, 
  Shield, 
  Heart, 
  Briefcase,
  ArrowRight,
  ArrowLeft,
  Home
} from 'lucide-react'

// Import our fixed step components
import WelcomeStep from './onboarding/WelcomeStep'
import PersonalInfoStep from './onboarding/PersonalInfoStep'
import I9Section1Step from './onboarding/I9Section1Step'
import JobDetailsStep from './onboarding/JobDetailsStep'

interface StepData {
  [key: string]: {
    completed: boolean
    data?: any
    completedAt?: string
  }
}

interface OnboardingStep {
  id: string
  title: string
  component: React.ComponentType<any>
  icon: React.ComponentType<any>
  required: boolean
  federalCompliance: boolean
  estimatedTime: number
}

const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 'welcome',
    title: 'Welcome & Language',
    component: WelcomeStep,
    icon: Users,
    required: true,
    federalCompliance: false,
    estimatedTime: 2
  },
  {
    id: 'job_details',
    title: 'Job Details',
    component: JobDetailsStep,
    icon: Briefcase,
    required: true,
    federalCompliance: false,
    estimatedTime: 3
  },
  {
    id: 'personal_info',
    title: 'Personal Information',
    component: PersonalInfoStep,
    icon: Users,
    required: true,
    federalCompliance: false,
    estimatedTime: 8
  },
  {
    id: 'i9_section1',
    title: 'I-9 Section 1',
    component: I9Section1Step,
    icon: Shield,
    required: true,
    federalCompliance: true,
    estimatedTime: 10
  }
]

export default function TestOnboardingFlow() {
  const navigate = useNavigate()
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [stepData, setStepData] = useState<StepData>({})
  const [language, setLanguage] = useState<'en' | 'es'>('en')

  // Mock employee and property data for testing
  const mockEmployee = {
    id: 'test-employee-1',
    name: 'John Doe',
    email: 'john.doe@email.com',
    position: 'Front Desk Agent',
    department: 'Guest Services',
    hire_date: '2024-02-01',
    pay_rate: '$18.00/hour',
    employment_type: 'full-time',
    supervisor: 'Jane Smith'
  }

  const mockProperty = {
    id: 'test-property-1',
    name: 'Grand Vista Hotel',
    address: '123 Main St, City, State 12345'
  }

  const currentStep = ONBOARDING_STEPS[currentStepIndex]
  const progress = {
    stepData,
    currentStepIndex,
    totalSteps: ONBOARDING_STEPS.length,
    completedSteps: Object.values(stepData).filter(step => step.completed).length
  }

  const markStepComplete = (stepId: string, data?: any) => {
    console.log('Marking step complete:', stepId, data)
    setStepData(prev => ({
      ...prev,
      [stepId]: {
        completed: true,
        data,
        completedAt: new Date().toISOString()
      }
    }))
  }

  const saveProgress = (stepId: string, data?: any) => {
    console.log('Saving progress:', stepId, data)
    setStepData(prev => ({
      ...prev,
      [stepId]: {
        completed: prev[stepId]?.completed || false,
        data,
        completedAt: prev[stepId]?.completedAt
      }
    }))
  }

  const goToNextStep = () => {
    if (currentStepIndex < ONBOARDING_STEPS.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1)
    }
  }

  const goToPreviousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1)
    }
  }

  const goToStep = (stepIndex: number) => {
    setCurrentStepIndex(stepIndex)
  }

  const renderCurrentStep = () => {
    const StepComponent = currentStep.component
    const commonProps = {
      currentStep: {
        id: currentStep.id,
        title: currentStep.title
      },
      progress,
      markStepComplete,
      saveProgress,
      language,
      employee: mockEmployee,
      property: mockProperty
    }

    return <StepComponent {...commonProps} />
  }

  const calculateOverallProgress = () => {
    return Math.round((progress.completedSteps / progress.totalSteps) * 100)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/')}
              >
                <Home className="h-4 w-4 mr-2" />
                Home
              </Button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Onboarding Flow Test</h1>
                <p className="text-sm text-gray-600">{mockProperty.name}</p>
              </div>
            </div>
            
            {/* Language Toggle */}
            <div className="flex items-center space-x-2">
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value as 'en' | 'es')}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="en">English</option>
                <option value="es">Español</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Progress Overview */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Onboarding Progress</span>
              <Badge variant="outline">
                {progress.completedSteps} of {progress.totalSteps} completed
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Overall Progress</span>
                <span>{calculateOverallProgress()}%</span>
              </div>
              <Progress value={calculateOverallProgress()} className="h-2" />
            </div>
            
            {/* Step Navigation */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {ONBOARDING_STEPS.map((step, index) => {
                const IconComponent = step.icon
                const isCompleted = stepData[step.id]?.completed
                const isCurrent = index === currentStepIndex
                const isAccessible = index <= currentStepIndex || isCompleted
                
                return (
                  <button
                    key={step.id}
                    onClick={() => isAccessible && goToStep(index)}
                    disabled={!isAccessible}
                    className={`p-4 rounded-lg border-2 transition-all text-left ${
                      isCurrent
                        ? 'border-blue-500 bg-blue-50 shadow-md'
                        : isCompleted
                        ? 'border-green-500 bg-green-50 hover:bg-green-100'
                        : isAccessible
                        ? 'border-gray-200 bg-white hover:border-gray-300'
                        : 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`rounded-full p-2 ${
                        isCompleted
                          ? 'bg-green-100 text-green-600'
                          : isCurrent
                          ? 'bg-blue-100 text-blue-600'
                          : 'bg-gray-100 text-gray-400'
                      }`}>
                        {isCompleted ? (
                          <CheckCircle className="h-4 w-4" />
                        ) : (
                          <IconComponent className="h-4 w-4" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className={`font-medium ${
                          isCurrent ? 'text-blue-900' : isCompleted ? 'text-green-900' : 'text-gray-600'
                        }`}>
                          {step.title}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-xs text-gray-500">{step.estimatedTime} min</span>
                          {step.federalCompliance && (
                            <Badge variant="secondary" className="text-xs">Federal</Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Current Step */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <currentStep.icon className="h-5 w-5 text-blue-600" />
              <span>Step {currentStepIndex + 1}: {currentStep.title}</span>
              {currentStep.federalCompliance && (
                <Badge variant="outline" className="bg-blue-50 text-blue-700">
                  Federal Compliance Required
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {renderCurrentStep()}
          </CardContent>
        </Card>

        {/* Navigation Controls */}
        <div className="flex justify-between items-center">
          <Button
            variant="outline"
            onClick={goToPreviousStep}
            disabled={currentStepIndex === 0}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous Step
          </Button>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Step {currentStepIndex + 1} of {ONBOARDING_STEPS.length}
            </p>
          </div>

          <Button
            onClick={goToNextStep}
            disabled={currentStepIndex === ONBOARDING_STEPS.length - 1}
          >
            Next Step
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </div>

        {/* Debug Info */}
        <Card className="mt-8 bg-gray-50">
          <CardHeader>
            <CardTitle className="text-sm">Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs space-y-2">
              <div><strong>Current Step Index:</strong> {currentStepIndex}</div>
              <div><strong>Current Step ID:</strong> {currentStep.id}</div>
              <div><strong>Language:</strong> {language}</div>
              <div><strong>Completed Steps:</strong> {Object.keys(stepData).filter(key => stepData[key].completed).join(', ') || 'None'}</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}