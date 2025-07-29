import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import I9SupplementA from '@/components/I9SupplementA'
import { CheckCircle, FileText, Info, Users, Globe } from 'lucide-react'

interface StepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function I9SupplementsStep(props: StepProps) {
  const { currentStep, progress, markStepComplete, saveProgress } = props
  
  const [needsSupplements, setNeedsSupplements] = useState<'none' | 'translator'>('none')
  const [supplementAData, setSupplementAData] = useState(null)
  const [isComplete, setIsComplete] = useState(false)

  // Load existing data from progress
  useEffect(() => {
    const existingData = progress.stepData?.['i9-supplements']
    if (existingData) {
      setNeedsSupplements(existingData.needsSupplements || 'none')
      setSupplementAData(existingData.supplementA)
    }
  }, [progress])

  // Check completion status
  useEffect(() => {
    let complete = false
    
    if (needsSupplements === 'none') {
      complete = true
    } else if (needsSupplements === 'translator' && supplementAData) {
      complete = true
    }
    
    setIsComplete(complete)
    
    if (complete) {
      const stepData = {
        needsSupplements,
        supplementA: supplementAData,
        federalComplianceNote: 'Supplement B is not applicable for employee - manager handles reverification',
        completedAt: new Date().toISOString()
      }
      markStepComplete('i9-supplements', stepData)
      saveProgress()
    }
  }, [needsSupplements, supplementAData])

  const handleSupplementAComplete = (data: any) => {
    setSupplementAData(data)
  }


  const handleSkipSupplements = () => {
    setNeedsSupplements('none')
  }

  return (
    <div className="space-y-6">
      {/* Step Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <FileText className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">I-9 Supplements</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          If someone assisted you in completing Section 1 of Form I-9, additional supplements may be required. 
          This includes translators or preparers who helped you understand or complete the form.
        </p>
      </div>

      {/* Information Alert */}
      <Alert className="bg-blue-50 border-blue-200">
        <Info className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>Most employees can skip this step.</strong> Supplements are only required if someone other than you 
          helped translate or prepare your I-9 Section 1 responses.
        </AlertDescription>
      </Alert>

      {/* Progress Indicator */}
      {isComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            I-9 Supplements section completed. You can proceed to document upload.
          </AlertDescription>
        </Alert>
      )}

      {/* Assessment Questions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5 text-blue-600" />
            <span>Did Anyone Assist You?</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <Label className="text-base font-medium text-gray-900 mb-4 block">
              Select which supplements are needed (if any):
            </Label>
            
            <RadioGroup 
              value={needsSupplements} 
              onValueChange={(value: any) => setNeedsSupplements(value)}
              className="space-y-4"
            >
              <div className="flex items-start space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50">
                <RadioGroupItem value="none" id="none" className="mt-1" />
                <div className="flex-1">
                  <Label htmlFor="none" className="font-medium cursor-pointer">
                    No assistance needed
                  </Label>
                  <p className="text-sm text-gray-600 mt-1">
                    I completed Section 1 myself without help from a translator or preparer.
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50">
                <RadioGroupItem value="translator" id="translator" className="mt-1" />
                <div className="flex-1">
                  <Label htmlFor="translator" className="font-medium cursor-pointer flex items-center space-x-2">
                    <Globe className="h-4 w-4" />
                    <span>Supplement A - Translator</span>
                  </Label>
                  <p className="text-sm text-gray-600 mt-1">
                    Someone translated the form or instructions for me because English is not my primary language.
                  </p>
                </div>
              </div>

            </RadioGroup>
          </div>

          {needsSupplements === 'none' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-green-800">No supplements required</span>
              </div>
              <p className="text-sm text-green-700 mt-1">
                You can proceed to the next step - document upload for I-9 verification.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Supplement A - Translator */}
      {needsSupplements === 'translator' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="h-5 w-5 text-blue-600" />
              <span>Supplement A - Translator Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <I9SupplementA
              initialData={supplementAData || {}}
              language="en"
              onComplete={handleSupplementAComplete}
              onSkip={() => setNeedsSupplements('none')}
              onBack={() => setNeedsSupplements('none')}
            />
          </CardContent>
        </Card>
      )}

      {/* Federal Compliance Notice for Supplement B */}
      <Card className="border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-blue-800">
            <FileText className="h-5 w-5" />
            <span>About Supplement B (Reverification)</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-blue-800">
          <div className="space-y-3">
            <p className="text-sm">
              <strong>Supplement B is NOT completed by employees.</strong> It is used exclusively by managers 
              for reverification scenarios such as:
            </p>
            <ul className="text-sm list-disc list-inside space-y-1 ml-4">
              <li>When an employee's work authorization expires and needs renewal</li>
              <li>When rehiring an employee within 3 years of the original I-9</li>
              <li>When an employee has a legal name change</li>
            </ul>
            <p className="text-sm">
              Your manager will complete Supplement B if any of these situations apply to you during 
              your employment. You do not need to take any action regarding Supplement B.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Completion Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-3">Supplement Requirements</h3>
        <div className="space-y-3">
          {needsSupplements === 'none' && (
            <div className="flex items-center space-x-2 text-green-700">
              <CheckCircle className="h-4 w-4" />
              <span className="text-sm font-medium">No supplements needed - Ready to continue</span>
            </div>
          )}
          
          {needsSupplements === 'translator' && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Supplement A (Translator)</span>
              <div className="flex items-center space-x-2">
                {supplementAData ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
                )}
                <span className="text-sm font-medium">
                  {supplementAData ? 'Complete' : 'Required'}
                </span>
              </div>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Supplement B (Reverification)</span>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-700">
                Manager Responsibility
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Federal Notice */}
      <div className="text-xs text-gray-500 border-t pt-4">
        <p><strong>Federal Requirement:</strong> Supplements A and B are required when a translator or preparer assists with Form I-9 completion under 8 CFR § 274a.2(b)(1)(i)(B).</p>
      </div>

      {/* Estimated Time */}
      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 2-4 minutes (if supplements needed)</p>
      </div>
    </div>
  )
}