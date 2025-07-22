import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import axios from 'axios'

interface OnboardingInfo {
  employee_id: string
  job_details: {
    position: string
    start_date: string
    pay_rate: string
    department: string
  }
  required_documents: string[]
  current_step: number
  total_steps: number
}

const onboardingSteps = [
  'Welcome & Instructions',
  'Document Upload for I-9',
  'I-9 Form Completion',
  'Document Upload for W-4',
  'W-4 Form Completion',
  'Direct Deposit Form',
  'Emergency Contacts',
  'Company Policies',
  'Health Insurance',
  'Final Review & Signature'
]

export default function OnboardingPortal() {
  const { employeeId } = useParams()
  const [onboardingInfo, setOnboardingInfo] = useState<OnboardingInfo | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOnboardingInfo()
  }, [employeeId])

  const fetchOnboardingInfo = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/onboarding/${employeeId}`)
      setOnboardingInfo(response.data)
      setCurrentStep(response.data.current_step || 0)
    } catch (error) {
      console.error('Failed to fetch onboarding info:', error)
    } finally {
      setLoading(false)
    }
  }

  const nextStep = () => {
    if (currentStep < onboardingSteps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p>Loading onboarding information...</p>
        </div>
      </div>
    )
  }

  if (!onboardingInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-red-600">Access Denied</CardTitle>
            <CardDescription>
              Invalid onboarding link or session expired.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  const progressPercentage = ((currentStep + 1) / onboardingSteps.length) * 100

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <Card className="mb-6">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-2xl font-bold">Employee Onboarding</CardTitle>
                <CardDescription>
                  Welcome! Complete your onboarding for {onboardingInfo.job_details.position}
                </CardDescription>
              </div>
              <Badge variant="outline">
                Step {currentStep + 1} of {onboardingSteps.length}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>{Math.round(progressPercentage)}% Complete</span>
                </div>
                <Progress value={progressPercentage} className="w-full" />
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="font-semibold">Position:</span>
                  <p>{onboardingInfo.job_details.position}</p>
                </div>
                <div>
                  <span className="font-semibold">Department:</span>
                  <p>{onboardingInfo.job_details.department}</p>
                </div>
                <div>
                  <span className="font-semibold">Start Date:</span>
                  <p>{new Date(onboardingInfo.job_details.start_date).toLocaleDateString()}</p>
                </div>
                <div>
                  <span className="font-semibold">Pay Rate:</span>
                  <p>${onboardingInfo.job_details.pay_rate}/hour</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{onboardingSteps[currentStep]}</CardTitle>
            <CardDescription>
              Step {currentStep + 1} of {onboardingSteps.length}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {currentStep === 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Welcome to Your Onboarding Process!</h3>
                <p>
                  Congratulations on joining our team! This onboarding process will help you complete 
                  all necessary paperwork and get you ready for your first day.
                </p>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">What you'll need:</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Driver's License or State ID</li>
                    <li>Social Security Card or qualifying document</li>
                    <li>Bank account information for direct deposit</li>
                    <li>Emergency contact information</li>
                  </ul>
                </div>
                <p className="text-sm text-gray-600">
                  This process should take about 15-20 minutes to complete. You can save your progress 
                  and return later if needed.
                </p>
              </div>
            )}

            {currentStep === 1 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Document Upload for I-9 Verification</h3>
                <p>Please upload your identification documents for I-9 verification.</p>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <div className="space-y-4">
                    <div className="text-gray-500">
                      <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </div>
                    <div>
                      <Button>Upload Documents</Button>
                      <p className="text-sm text-gray-500 mt-2">
                        Drag and drop or click to upload your ID documents
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {currentStep > 1 && (
              <div className="text-center py-8">
                <p className="text-gray-600">
                  This step is under development. In the full implementation, this would contain:
                </p>
                <ul className="list-disc list-inside mt-4 text-left max-w-md mx-auto space-y-1">
                  <li>I-9 form with OCR pre-filling</li>
                  <li>W-4 form with OCR pre-filling</li>
                  <li>Direct deposit setup</li>
                  <li>Emergency contacts</li>
                  <li>Company policies acknowledgment</li>
                  <li>Health insurance enrollment</li>
                  <li>Digital signature collection</li>
                </ul>
              </div>
            )}

            <div className="flex justify-between mt-8">
              <Button 
                variant="outline" 
                onClick={prevStep} 
                disabled={currentStep === 0}
              >
                Previous
              </Button>
              <Button 
                onClick={nextStep} 
                disabled={currentStep === onboardingSteps.length - 1}
              >
                {currentStep === onboardingSteps.length - 1 ? 'Complete' : 'Next'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
