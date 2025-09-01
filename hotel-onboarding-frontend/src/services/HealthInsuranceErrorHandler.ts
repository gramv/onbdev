/**
 * Health Insurance Error Handler
 * Comprehensive error handling service with automatic recovery and user-friendly messaging
 */

import { 
  HealthInsuranceError, 
  HealthInsuranceErrorType, 
  ErrorSeverity, 
  ErrorResolution,
  ErrorContext,
  ErrorAnalytics
} from '@/types/healthInsuranceErrors'
import { healthInsuranceErrorMessages } from '@/config/healthInsuranceErrorMessages'

export class HealthInsuranceErrorHandler {
  private retryAttempts = new Map<string, number>()
  private maxRetries = 3
  private retryDelays = [1000, 2000, 4000] // Exponential backoff
  private errorAnalytics: ErrorAnalytics[] = []

  /**
   * Main error handling method
   */
  async handleError(
    error: HealthInsuranceError, 
    language: 'en' | 'es' = 'en'
  ): Promise<ErrorResolution> {
    const errorId = this.generateErrorId(error)
    const attempts = this.retryAttempts.get(errorId) || 0

    // Log error with full context
    this.logError(error, attempts)

    // Track analytics
    this.trackErrorAnalytics(error)

    // Attempt automatic recovery if retries available
    if (attempts < this.maxRetries && this.isRetryable(error)) {
      this.retryAttempts.set(errorId, attempts + 1)
      
      const recoveryResult = await this.attemptRecovery(error, attempts)
      if (recoveryResult.success) {
        this.logRecoverySuccess(error, attempts + 1)
        return recoveryResult
      }
    }

    // Show user-friendly error message
    return this.showUserError(error, language)
  }

  /**
   * Attempt automatic error recovery
   */
  private async attemptRecovery(
    error: HealthInsuranceError, 
    attempt: number
  ): Promise<ErrorResolution> {
    const delay = this.retryDelays[Math.min(attempt, this.retryDelays.length - 1)]
    
    // Wait with exponential backoff
    await this.delay(delay)

    try {
      switch (error.type) {
        case HealthInsuranceErrorType.PDF_GENERATION_FAILED:
          return await this.retryPDFGeneration(error)
          
        case HealthInsuranceErrorType.NETWORK_TIMEOUT:
          return await this.retryNetworkRequest(error)
          
        case HealthInsuranceErrorType.SIGNATURE_PROCESSING_FAILED:
          return await this.recoverSignatureProcess(error)
          
        case HealthInsuranceErrorType.PDF_DISPLAY_ERROR:
          return await this.retryPDFDisplay(error)
          
        default:
          return { success: false, error }
      }
    } catch (retryError) {
      return { 
        success: false, 
        error: this.createError(
          HealthInsuranceErrorType.UNKNOWN_ERROR,
          'Recovery attempt failed',
          ErrorSeverity.HIGH,
          { originalError: error, retryError }
        )
      }
    }
  }

  /**
   * Retry PDF generation with simplified data
   */
  private async retryPDFGeneration(error: HealthInsuranceError): Promise<ErrorResolution> {
    try {
      const formData = error.context?.formData
      if (!formData) {
        throw new Error('No form data available for PDF generation retry')
      }

      // Simplify form data for retry
      const simplifiedData = this.simplifyFormData(formData)
      
      // Make API call (this would be injected in real implementation)
      const response = await fetch('/api/onboarding/health-insurance/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ employee_data: simplifiedData })
      })

      if (!response.ok) {
        throw new Error(`PDF generation failed: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success && result.data?.pdf) {
        return { 
          success: true, 
          data: result.data.pdf,
          recoveryAttempted: true 
        }
      }

      throw new Error('Invalid PDF generation response')
      
    } catch (retryError) {
      return { 
        success: false, 
        error: this.createError(
          HealthInsuranceErrorType.PDF_GENERATION_FAILED,
          `PDF generation retry failed: ${retryError}`,
          ErrorSeverity.HIGH,
          error.context
        )
      }
    }
  }

  /**
   * Retry network request with timeout handling
   */
  private async retryNetworkRequest(error: HealthInsuranceError): Promise<ErrorResolution> {
    // Implementation would depend on the specific network request
    // This is a placeholder for the retry logic
    return { success: false, error }
  }

  /**
   * Recover signature processing
   */
  private async recoverSignatureProcess(error: HealthInsuranceError): Promise<ErrorResolution> {
    // Implementation would attempt to reprocess the signature
    // This is a placeholder for the recovery logic
    return { success: false, error }
  }

  /**
   * Retry PDF display
   */
  private async retryPDFDisplay(error: HealthInsuranceError): Promise<ErrorResolution> {
    // Implementation would attempt to reload the PDF viewer
    // This is a placeholder for the retry logic
    return { success: false, error }
  }

  /**
   * Show user-friendly error message
   */
  private showUserError(
    error: HealthInsuranceError, 
    language: 'en' | 'es'
  ): ErrorResolution {
    const messages = healthInsuranceErrorMessages[language]
    const userMessage = messages[error.type]

    if (!userMessage) {
      // Fallback to unknown error message
      const fallbackMessage = messages[HealthInsuranceErrorType.UNKNOWN_ERROR]
      return {
        success: false,
        error: {
          ...error,
          message: fallbackMessage.message
        },
        userNotified: true
      }
    }

    return {
      success: false,
      error: {
        ...error,
        message: userMessage.message
      },
      userNotified: true
    }
  }

  /**
   * Utility methods
   */
  private generateErrorId(error: HealthInsuranceError): string {
    return `${error.type}_${error.context?.step || 'unknown'}_${Date.now()}`
  }

  private isRetryable(error: HealthInsuranceError): boolean {
    const retryableTypes = [
      HealthInsuranceErrorType.PDF_GENERATION_FAILED,
      HealthInsuranceErrorType.NETWORK_TIMEOUT,
      HealthInsuranceErrorType.API_SERVER_ERROR,
      HealthInsuranceErrorType.PDF_DISPLAY_ERROR,
      HealthInsuranceErrorType.SIGNATURE_PROCESSING_FAILED
    ]
    return retryableTypes.includes(error.type)
  }

  private simplifyFormData(formData: any): any {
    // Remove complex nested objects that might cause PDF generation issues
    return {
      personalInfo: formData.personalInfo || {},
      medicalPlan: formData.medicalPlan || '',
      medicalTier: formData.medicalTier || 'employee',
      dentalCoverage: Boolean(formData.dentalCoverage),
      visionCoverage: Boolean(formData.visionCoverage),
      section125Acknowledged: Boolean(formData.section125Acknowledged)
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  private logError(error: HealthInsuranceError, attempts: number): void {
    console.error('HealthInsurance Error:', {
      id: error.id,
      type: error.type,
      severity: error.severity,
      message: error.message,
      attempts,
      timestamp: error.timestamp,
      context: error.context
    })

    // In production, send to logging service
    if (process.env.NODE_ENV === 'production') {
      this.sendToLoggingService(error, attempts)
    }
  }

  private logRecoverySuccess(error: HealthInsuranceError, attempts: number): void {
    console.info('HealthInsurance Recovery Success:', {
      errorType: error.type,
      attempts,
      timestamp: new Date().toISOString()
    })
  }

  private trackErrorAnalytics(error: HealthInsuranceError): void {
    const analytics: ErrorAnalytics = {
      errorId: error.id,
      type: error.type,
      severity: error.severity,
      timestamp: error.timestamp,
      resolved: false,
      context: error.context as ErrorContext
    }

    this.errorAnalytics.push(analytics)

    // In production, send to analytics service
    if (process.env.NODE_ENV === 'production') {
      this.sendToAnalyticsService(analytics)
    }
  }

  private sendToLoggingService(error: HealthInsuranceError, attempts: number): void {
    // Implementation would send to logging service like DataDog, Sentry, etc.
  }

  private sendToAnalyticsService(analytics: ErrorAnalytics): void {
    // Implementation would send to analytics service
  }

  /**
   * Create a new error instance
   */
  createError(
    type: HealthInsuranceErrorType,
    message: string,
    severity: ErrorSeverity,
    context?: any
  ): HealthInsuranceError {
    return {
      id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      severity,
      message,
      timestamp: new Date(),
      context,
      recoverable: this.isRetryable({ type } as HealthInsuranceError)
    }
  }

  /**
   * Get error statistics for monitoring
   */
  getErrorStatistics(): {
    totalErrors: number
    errorsByType: Record<string, number>
    errorsBySeverity: Record<string, number>
    recoveryRate: number
  } {
    const total = this.errorAnalytics.length
    const resolved = this.errorAnalytics.filter(e => e.resolved).length

    const byType = this.errorAnalytics.reduce((acc, error) => {
      acc[error.type] = (acc[error.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    const bySeverity = this.errorAnalytics.reduce((acc, error) => {
      acc[error.severity] = (acc[error.severity] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      totalErrors: total,
      errorsByType: byType,
      errorsBySeverity: bySeverity,
      recoveryRate: total > 0 ? (resolved / total) * 100 : 0
    }
  }
}

// Singleton instance
export const healthInsuranceErrorHandler = new HealthInsuranceErrorHandler()
