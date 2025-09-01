/**
 * Health Insurance Error Types and Interfaces
 * Comprehensive error handling system for the Health Insurance module
 */

export enum HealthInsuranceErrorType {
  // Network & API Errors
  NETWORK_TIMEOUT = 'NETWORK_TIMEOUT',
  API_SERVER_ERROR = 'API_SERVER_ERROR',
  PDF_GENERATION_FAILED = 'PDF_GENERATION_FAILED',
  SIGNATURE_PROCESSING_FAILED = 'SIGNATURE_PROCESSING_FAILED',
  
  // Data Validation Errors
  INVALID_FORM_DATA = 'INVALID_FORM_DATA',
  MISSING_PERSONAL_INFO = 'MISSING_PERSONAL_INFO',
  INVALID_COVERAGE_SELECTION = 'INVALID_COVERAGE_SELECTION',
  MISSING_REQUIRED_FIELDS = 'MISSING_REQUIRED_FIELDS',
  
  // Document Processing Errors
  PDF_DISPLAY_ERROR = 'PDF_DISPLAY_ERROR',
  SIGNATURE_CAPTURE_ERROR = 'SIGNATURE_CAPTURE_ERROR',
  DOCUMENT_SAVE_ERROR = 'DOCUMENT_SAVE_ERROR',
  PDF_LOADING_TIMEOUT = 'PDF_LOADING_TIMEOUT',
  
  // System Errors
  SESSION_EXPIRED = 'SESSION_EXPIRED',
  BROWSER_COMPATIBILITY = 'BROWSER_COMPATIBILITY',
  STORAGE_QUOTA_EXCEEDED = 'STORAGE_QUOTA_EXCEEDED',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

export enum ErrorSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export interface HealthInsuranceError {
  id: string
  type: HealthInsuranceErrorType
  severity: ErrorSeverity
  message: string
  details?: string
  timestamp: Date
  context?: {
    formData?: any
    step?: string
    userAgent?: string
    url?: string
    employeeId?: string
  }
  stack?: string
  recoverable: boolean
}

export interface ErrorRecoveryAction {
  label: string
  action: string
  primary?: boolean
  icon?: string
}

export interface UserFeedbackPattern {
  title: string
  message: string
  actions: ErrorRecoveryAction[]
  recovery?: string
  showDetails?: boolean
  autoRetry?: boolean
  retryDelay?: number
}

export interface ErrorResolution {
  success: boolean
  data?: any
  error?: HealthInsuranceError
  recoveryAttempted?: boolean
  userNotified?: boolean
}

export interface ErrorLoggingConfig {
  logLevel: 'debug' | 'info' | 'warn' | 'error'
  includeStack: boolean
  includeContext: boolean
  sendToAnalytics: boolean
  alertThreshold?: number
}

export interface FallbackStrategy {
  type: 'retry' | 'alternative' | 'graceful_degradation' | 'offline_mode'
  config: any
  condition?: (error: HealthInsuranceError) => boolean
}

export interface ErrorHandlingStrategy {
  detection: string[]
  recovery: string[]
  userFeedback: UserFeedbackPattern
  logging: ErrorLoggingConfig
  fallbacks: FallbackStrategy[]
  maxRetries?: number
  retryDelay?: number
}

// Error message templates for different languages
export interface ErrorMessages {
  en: Record<HealthInsuranceErrorType, UserFeedbackPattern>
  es: Record<HealthInsuranceErrorType, UserFeedbackPattern>
}

// Error context for better debugging
export interface ErrorContext {
  component: string
  operation: string
  formData?: any
  step?: string
  timestamp: Date
  userAgent: string
  url: string
  employeeId?: string
  sessionId?: string
}

// Error analytics data
export interface ErrorAnalytics {
  errorId: string
  type: HealthInsuranceErrorType
  severity: ErrorSeverity
  timestamp: Date
  resolved: boolean
  resolutionTime?: number
  userAction?: string
  context: ErrorContext
}
