import React, { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import DigitalSignatureCapture from '@/components/DigitalSignatureCapture'
import ReviewPlaceholder from '@/components/ReviewPlaceholder'
import { CheckCircle, Building, FileText, Shield } from 'lucide-react'

interface OnboardingContext {
  currentStep: any
  progress: any
  markStepComplete: (stepId: string, data?: any) => void
  saveProgress: () => void
}

const COMPANY_POLICIES = [
  {
    id: 'employee-handbook',
    title: 'Employee Handbook',
    description: 'Company policies, procedures, and expectations',
    required: true
  },
  {
    id: 'code-of-conduct',
    title: 'Code of Conduct',
    description: 'Professional behavior and ethical standards',
    required: true
  },
  {
    id: 'anti-harassment',
    title: 'Anti-Harassment Policy',
    description: 'Workplace harassment prevention and reporting',
    required: true
  },
  {
    id: 'safety-policies',
    title: 'Safety Policies',
    description: 'Workplace safety procedures and protocols',
    required: true
  }
]

export default function CompanyPoliciesStep() {
  const { currentStep, progress, markStepComplete, saveProgress } = useOutletContext<OnboardingContext>()
  
  const [acknowledgedPolicies, setAcknowledgedPolicies] = useState<string[]>([])
  const [isSigned, setIsSigned] = useState(false)
  const [signatureData, setSignatureData] = useState(null)
  const [showReview, setShowReview] = useState(false)

  useEffect(() => {
    const existingData = progress.stepData?.['company-policies']
    if (existingData) {
      setAcknowledgedPolicies(existingData.acknowledgedPolicies || [])
      setIsSigned(existingData.signed || false)
      setSignatureData(existingData.signature)
    }
  }, [progress])

  const handlePolicyAcknowledgment = (policyId: string, acknowledged: boolean) => {
    if (acknowledged) {
      setAcknowledgedPolicies(prev => [...prev.filter(id => id !== policyId), policyId])
    } else {
      setAcknowledgedPolicies(prev => prev.filter(id => id !== policyId))
    }
  }

  const handleProceedToReview = () => {
    if (allPoliciesAcknowledged && !isSigned) {
      setShowReview(true)
    }
  }

  const handleBackFromReview = () => {
    setShowReview(false)
  }

  const handleSignature = (signature: any) => {
    setSignatureData(signature)
    setIsSigned(true)
    
    const stepData = {
      acknowledgedPolicies,
      signed: true,
      signature,
      completedAt: new Date().toISOString()
    }
    markStepComplete('company-policies', stepData)
    saveProgress()
    setShowReview(false)
  }

  const allPoliciesAcknowledged = COMPANY_POLICIES.every(policy => 
    acknowledgedPolicies.includes(policy.id)
  )
  const isStepComplete = allPoliciesAcknowledged && isSigned

  // Show review placeholder if all policies acknowledged and review is requested
  if (showReview && allPoliciesAcknowledged) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Building className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">Review Company Policies</h1>
          </div>
        </div>
        
        <ReviewPlaceholder
          formType="company_policies"
          formTitle="Company Policy Acknowledgments"
          description="Review your policy acknowledgments before signing"
          isReady={allPoliciesAcknowledged}
          onEdit={handleBackFromReview}
          language="en"
        />
        
        <div className="flex justify-between">
          <Button variant="outline" onClick={handleBackFromReview}>
            Back to Policies
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Building className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Company Policies</h1>
        </div>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Please review and acknowledge our company policies. These policies ensure a safe, 
          respectful, and productive work environment for all employees.
        </p>
      </div>

      {isStepComplete && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            All company policies acknowledged and signed successfully.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5 text-blue-600" />
            <span>Policy Acknowledgments</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {COMPANY_POLICIES.map(policy => (
            <div key={policy.id} className="flex items-start space-x-3 p-4 border rounded-lg">
              <Checkbox
                id={policy.id}
                checked={acknowledgedPolicies.includes(policy.id)}
                onCheckedChange={(checked) => handlePolicyAcknowledgment(policy.id, checked as boolean)}
              />
              <div className="flex-1">
                <label htmlFor={policy.id} className="font-medium cursor-pointer">
                  {policy.title}
                  {policy.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                <p className="text-sm text-gray-600 mt-1">{policy.description}</p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Review Button */}
      {allPoliciesAcknowledged && !isSigned && (
        <div className="flex justify-center">
          <Button 
            onClick={handleProceedToReview}
            size="lg"
            className="bg-blue-600 hover:bg-blue-700"
          >
            Review and Sign Policies
          </Button>
        </div>
      )}

      {allPoliciesAcknowledged && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span>Digital Signature</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <DigitalSignatureCapture
              onSignature={handleSignature}
              title="Policy Acknowledgment Signature"
              description="By signing below, I acknowledge that I have read, understood, and agree to comply with all company policies."
            />
          </CardContent>
        </Card>
      )}

      <div className="text-center text-sm text-gray-500">
        <p>Estimated time: 4-5 minutes</p>
      </div>
    </div>
  )
}