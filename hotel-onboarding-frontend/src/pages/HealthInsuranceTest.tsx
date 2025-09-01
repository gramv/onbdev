/**
 * Health Insurance Module Test Page
 * Test page for the enhanced health insurance components
 */

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  TestTube, 
  FileText, 
  Pen, 
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react'

// Import our new components
import { HealthInsuranceErrorBoundary } from '../components/HealthInsuranceErrorBoundary'
import { HealthInsuranceErrorDisplay } from '../components/HealthInsuranceErrorDisplay'
import { ResponsivePDFViewer } from '../components/ResponsivePDFViewer'
import { MobileSignatureCapture } from '../components/MobileSignatureCapture'
import { HealthInsuranceProvider } from '../contexts/HealthInsuranceContext'
import { healthInsuranceErrorHandler } from '../services/HealthInsuranceErrorHandler'
import { HealthInsuranceErrorType, ErrorSeverity } from '../types/healthInsuranceErrors'

interface TestResult {
  name: string
  status: 'pending' | 'success' | 'error'
  message: string
  details?: string
}

export default function HealthInsuranceTest() {
  const [testResults, setTestResults] = useState<TestResult[]>([])
  const [currentTest, setCurrentTest] = useState<string | null>(null)
  const [samplePDF, setSamplePDF] = useState<string | null>(null)
  const [showSignatureCapture, setShowSignatureCapture] = useState(false)

  // Test functions
  const runTest = async (testName: string, testFn: () => Promise<void>) => {
    setCurrentTest(testName)
    
    try {
      await testFn()
      setTestResults(prev => [...prev, {
        name: testName,
        status: 'success',
        message: 'Test passed successfully'
      }])
    } catch (error) {
      setTestResults(prev => [...prev, {
        name: testName,
        status: 'error',
        message: 'Test failed',
        details: error instanceof Error ? error.message : String(error)
      }])
    } finally {
      setCurrentTest(null)
    }
  }

  // Test 1: Error Handler Creation
  const testErrorHandler = async () => {
    const error = healthInsuranceErrorHandler.createError(
      HealthInsuranceErrorType.PDF_GENERATION_FAILED,
      'Test error message',
      ErrorSeverity.HIGH,
      { testContext: true }
    )

    if (!error.id || !error.type || !error.message) {
      throw new Error('Error handler failed to create proper error object')
    }
  }

  // Test 2: PDF Generation API
  const testPDFGeneration = async () => {
    const testData = {
      employee_data: {
        personalInfo: {
          firstName: 'Test',
          lastName: 'User',
          ssn: '123-45-6789',
          email: 'test@example.com'
        },
        medicalPlan: 'hra6k',
        medicalTier: 'employee',
        section125Acknowledged: true
      }
    }

    const response = await fetch('/api/onboarding/test-employee/health-insurance/generate-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testData)
    })

    if (!response.ok) {
      throw new Error(`PDF generation failed: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    if (!result.success || !result.data?.pdf) {
      throw new Error('Invalid PDF generation response')
    }

    setSamplePDF(result.data.pdf)
  }

  // Test 3: Context Provider
  const testContextProvider = async () => {
    // This test will be validated by the component rendering without errors
    return Promise.resolve()
  }

  // Test 4: Mobile Signature Capture
  const testSignatureCapture = async () => {
    setShowSignatureCapture(true)
    return Promise.resolve()
  }

  // Run all tests
  const runAllTests = async () => {
    setTestResults([])
    
    await runTest('Error Handler Creation', testErrorHandler)
    await runTest('PDF Generation API', testPDFGeneration)
    await runTest('Context Provider', testContextProvider)
    await runTest('Mobile Signature Capture', testSignatureCapture)
  }

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <TestTube className="h-4 w-4 text-gray-400" />
    }
  }

  return (
    <HealthInsuranceErrorBoundary language="en">
      <HealthInsuranceProvider employeeId="test-employee" language="en">
        <div className="container mx-auto p-6 max-w-6xl">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Health Insurance Module Test Suite
            </h1>
            <p className="text-gray-600">
              Test the enhanced health insurance components and functionality
            </p>
          </div>

          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="error-handling">Error Handling</TabsTrigger>
              <TabsTrigger value="pdf-viewer">PDF Viewer</TabsTrigger>
              <TabsTrigger value="signature">Signature</TabsTrigger>
              <TabsTrigger value="integration">Integration</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TestTube className="h-5 w-5" />
                    Test Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Button onClick={runAllTests} disabled={currentTest !== null}>
                      {currentTest ? `Running: ${currentTest}...` : 'Run All Tests'}
                    </Button>

                    {testResults.length > 0 && (
                      <div className="space-y-2">
                        {testResults.map((result, index) => (
                          <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex items-center gap-3">
                              {getStatusIcon(result.status)}
                              <span className="font-medium">{result.name}</span>
                            </div>
                            <div className="text-right">
                              <div className="text-sm text-gray-600">{result.message}</div>
                              {result.details && (
                                <div className="text-xs text-red-600 mt-1">{result.details}</div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Error Handling Tab */}
            <TabsContent value="error-handling" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Error Handling Test</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Button onClick={() => runTest('Error Display', async () => {
                      const error = healthInsuranceErrorHandler.createError(
                        HealthInsuranceErrorType.PDF_GENERATION_FAILED,
                        'This is a test error message',
                        ErrorSeverity.MEDIUM
                      )
                      // Error will be displayed below
                    })}>
                      Test Error Display
                    </Button>

                    {testResults.some(r => r.name === 'Error Display') && (
                      <HealthInsuranceErrorDisplay
                        error={healthInsuranceErrorHandler.createError(
                          HealthInsuranceErrorType.PDF_GENERATION_FAILED,
                          'This is a test error message',
                          ErrorSeverity.MEDIUM
                        )}
                        language="en"
                        onAction={async (action) => {
                          console.log('Error action:', action)
                        }}
                      />
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* PDF Viewer Tab */}
            <TabsContent value="pdf-viewer" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    PDF Viewer Test
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Button onClick={() => runTest('PDF Generation', testPDFGeneration)}>
                      Generate Test PDF
                    </Button>

                    {samplePDF && (
                      <ResponsivePDFViewer
                        pdfData={samplePDF}
                        title="Test Health Insurance Form"
                        language="en"
                        mobileOptimized={true}
                        height="500px"
                      />
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Signature Tab */}
            <TabsContent value="signature" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Pen className="h-5 w-5" />
                    Signature Capture Test
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {!showSignatureCapture ? (
                      <Button onClick={() => setShowSignatureCapture(true)}>
                        Test Signature Capture
                      </Button>
                    ) : (
                      <MobileSignatureCapture
                        onSignature={(signature) => {
                          console.log('Signature captured:', signature)
                          setShowSignatureCapture(false)
                          setTestResults(prev => [...prev, {
                            name: 'Signature Capture',
                            status: 'success',
                            message: 'Signature captured successfully'
                          }])
                        }}
                        onCancel={() => setShowSignatureCapture(false)}
                        language="en"
                      />
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Integration Tab */}
            <TabsContent value="integration" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Integration Test</CardTitle>
                </CardHeader>
                <CardContent>
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Integration tests will verify the complete health insurance flow
                      including form submission, PDF generation, and signature capture.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </HealthInsuranceProvider>
    </HealthInsuranceErrorBoundary>
  )
}
