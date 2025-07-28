import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import PersonalInformationForm from '@/components/PersonalInformationForm'
import EmergencyContactsForm from '@/components/EmergencyContactsForm'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, User, Phone } from 'lucide-react'

interface PersonalInfoStepProps {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: (stepId: string, data?: any) => void
  language: 'en' | 'es'
  employee?: any
  property?: any
}

export default function PersonalInfoStep({
  currentStep,
  progress,
  markStepComplete,
  saveProgress,
  language = 'en',
  employee,
  property
}: PersonalInfoStepProps) {
  
  const [personalInfoData, setPersonalInfoData] = useState(null)
  const [emergencyContactsData, setEmergencyContactsData] = useState(null)
  const [personalInfoValid, setPersonalInfoValid] = useState(false)
  const [emergencyContactsValid, setEmergencyContactsValid] = useState(false)
  const [activeTab, setActiveTab] = useState('personal')

  // Load existing data from progress
  useEffect(() => {
    const existingData = progress.stepData?.['personal-info']
    if (existingData) {
      setPersonalInfoData(existingData.personalInfo)
      setEmergencyContactsData(existingData.emergencyContacts)
    }
  }, [progress])

  const handlePersonalInfoSave = (data: any) => {
    setPersonalInfoData(data)
    saveStepData({ personalInfo: data, emergencyContacts: emergencyContactsData })
  }

  const handleEmergencyContactsSave = (data: any) => {
    setEmergencyContactsData(data)
    saveStepData({ personalInfo: personalInfoData, emergencyContacts: data })
  }

  const saveStepData = (data: any) => {
    markStepComplete('personal-info', data)
    saveProgress('personal-info', data)
  }

  const handleContinue = () => {
    if (personalInfoValid && emergencyContactsValid) {
      // Both forms are complete, mark step as complete and save
      const stepData = {
        personalInfo: personalInfoData,
        emergencyContacts: emergencyContactsData
      }
      markStepComplete('personal-info', stepData)
      saveProgress('personal-info', stepData)
    }
  }

  const isStepComplete = personalInfoValid && emergencyContactsValid

  return (
    <div className="space-y-6">
      {/* Step Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <User className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Personal Information</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Please provide your personal information and emergency contacts. This information will be kept confidential 
          and used only for employment and emergency purposes.
        </p>
      </div>

      {/* Progress Indicator */}
      {isStepComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Personal information section completed successfully. You can proceed to the next step.
          </AlertDescription>
        </Alert>
      )}

      {/* Tabbed Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="personal" className="flex items-center space-x-2">
            <User className="h-4 w-4" />
            <span>Personal Details</span>
            {personalInfoValid && <CheckCircle className="h-3 w-3 text-green-600" />}
          </TabsTrigger>
          <TabsTrigger value="emergency" className="flex items-center space-x-2">
            <Phone className="h-4 w-4" />
            <span>Emergency Contacts</span>
            {emergencyContactsValid && <CheckCircle className="h-3 w-3 text-green-600" />}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="personal" className="space-y-6">
          <PersonalInformationForm
            initialData={personalInfoData || {}}
            language={language}
            onSave={handlePersonalInfoSave}
            onNext={() => setActiveTab('emergency')}
            onValidationChange={(isValid) => setPersonalInfoValid(isValid)}
          />
        </TabsContent>

        <TabsContent value="emergency" className="space-y-6">
          <EmergencyContactsForm
            initialData={emergencyContactsData || {}}
            language={language}
            onSave={handleEmergencyContactsSave}
            onNext={handleContinue}
            onBack={() => setActiveTab('personal')}
            onValidationChange={(isValid) => setEmergencyContactsValid(isValid)}
          />
        </TabsContent>
      </Tabs>

      {/* Form Validation Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-3">Section Progress</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Personal Details</span>
            <div className="flex items-center space-x-2">
              {personalInfoValid ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
              )}
              <span className="text-sm font-medium">
                {personalInfoValid ? 'Complete' : 'Required'}
              </span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Emergency Contacts</span>
            <div className="flex items-center space-x-2">
              {emergencyContactsValid ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <div className="h-4 w-4 rounded-full border-2 border-gray-300" />
              )}
              <span className="text-sm font-medium">
                {emergencyContactsValid ? 'Complete' : 'Required'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Estimated Time */}
      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 5-7 minutes</p>
      </div>
    </div>
  )
}