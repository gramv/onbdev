import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import PDFViewer from '@/components/PDFViewer'
import ReviewAndSign from '@/components/ReviewAndSign'

const getApiUrl = () => {
  return process.env.NODE_ENV === 'production' 
    ? 'https://your-backend-url.com/api'
    : 'http://localhost:8000/api'
}

export default function TestHealthInsurancePDF() {
  const [showPDFTest, setShowPDFTest] = useState(false)
  const [showReviewAndSign, setShowReviewAndSign] = useState(false)
  const [pdfData, setPdfData] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Test data that matches the backend expectations
  const testFormData = {
    personalInfo: {
      firstName: 'John',
      lastName: 'Doe',
      ssn: '123-45-6789',
      dateOfBirth: '1990-01-15',
      address: '123 Test St',
      city: 'Test City',
      state: 'NY',
      zipCode: '10001',
      phone: '(555) 123-4567',
      email: 'john.doe@example.com',
      gender: 'M'
    },
    medicalPlan: 'hra6k',
    medicalTier: 'employee',
    dentalCoverage: true,
    dentalEnrolled: true,
    dentalTier: 'employee',
    visionCoverage: true,
    visionEnrolled: true,
    visionTier: 'employee',
    dependents: [],
    section125Acknowledged: true,
    effectiveDate: '2025-01-01'
  }

  const testDirectPDFGeneration = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('Testing direct PDF generation...')
      
      const response = await fetch(`${getApiUrl()}/onboarding/test-employee/health-insurance/generate-pdf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employee_data: testFormData
        })
      })

      console.log('Response status:', response.status)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      console.log('Response result:', result)

      if (result.success && result.data && result.data.pdf) {
        setPdfData(result.data.pdf)
        setShowPDFTest(true)
        console.log('PDF data received, length:', result.data.pdf.length)
      } else {
        throw new Error('Invalid response format or missing PDF data')
      }
    } catch (err) {
      console.error('PDF generation failed:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const handleSignature = (signatureData: any) => {
    console.log('Signature received:', signatureData)
    alert('Signature received! Check console for details.')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Health Insurance PDF Preview Test</CardTitle>
            <p className="text-sm text-gray-600">
              Test the health insurance PDF generation and preview functionality
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <Button 
                onClick={testDirectPDFGeneration}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {loading ? 'Generating...' : 'Test Direct PDF Generation'}
              </Button>
              
              <Button 
                onClick={() => setShowReviewAndSign(true)}
                variant="outline"
              >
                Test ReviewAndSign Component
              </Button>
              
              <Button 
                onClick={() => {
                  setShowPDFTest(false)
                  setShowReviewAndSign(false)
                  setPdfData(null)
                  setError(null)
                }}
                variant="outline"
              >
                Reset
              </Button>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                <strong>Error:</strong> {error}
              </div>
            )}

            {loading && (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded">
                Generating PDF...
              </div>
            )}
          </CardContent>
        </Card>

        {/* Direct PDF Test */}
        {showPDFTest && pdfData && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Direct PDF Generation Test</CardTitle>
              <p className="text-sm text-gray-600">
                PDF generated directly from API call
              </p>
            </CardHeader>
            <CardContent>
              <div style={{ height: '600px' }}>
                <PDFViewer 
                  pdfData={`data:application/pdf;base64,${pdfData}`}
                  title="Health Insurance Form"
                  height="600px"
                />
              </div>
            </CardContent>
          </Card>
        )}

        {/* ReviewAndSign Component Test */}
        {showReviewAndSign && (
          <Card>
            <CardHeader>
              <CardTitle>ReviewAndSign Component Test</CardTitle>
              <p className="text-sm text-gray-600">
                Test the ReviewAndSign component with PDF preview
              </p>
            </CardHeader>
            <CardContent>
              <ReviewAndSign
                formType="health_insurance"
                formData={testFormData}
                title="Health Insurance Enrollment"
                description="Please review your health insurance selections before signing"
                language="en"
                onSign={handleSignature}
                usePDFPreview={true}
                pdfEndpoint={`${getApiUrl()}/onboarding/test-employee/health-insurance/generate-pdf`}
              />
            </CardContent>
          </Card>
        )}

        {/* Debug Information */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div><strong>API URL:</strong> {getApiUrl()}</div>
              <div><strong>PDF Endpoint:</strong> {getApiUrl()}/onboarding/test-employee/health-insurance/generate-pdf</div>
              <div><strong>Test Data:</strong></div>
              <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
                {JSON.stringify(testFormData, null, 2)}
              </pre>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
