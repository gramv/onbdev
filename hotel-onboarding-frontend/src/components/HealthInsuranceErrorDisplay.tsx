/**
 * Health Insurance Error Display Component
 * Shows user-friendly error messages with recovery actions
 */

import React, { useState, useEffect } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { 
  AlertTriangle, 
  RefreshCw, 
  Save, 
  HelpCircle, 
  Download,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react'
import { 
  HealthInsuranceError, 
  ErrorSeverity,
  ErrorRecoveryAction 
} from '@/types/healthInsuranceErrors'
import { healthInsuranceErrorMessages } from '../config/healthInsuranceErrorMessages'

interface HealthInsuranceErrorDisplayProps {
  error: HealthInsuranceError
  language?: 'en' | 'es'
  onAction?: (action: string) => void
  onDismiss?: () => void
  showDetails?: boolean
  autoRetry?: boolean
  className?: string
}

const iconMap = {
  refresh: RefreshCw,
  save: Save,
  help: HelpCircle,
  download: Download,
  'arrow-right': ArrowRight,
  'arrow-left': ArrowLeft,
  check: CheckCircle,
  alert: AlertTriangle,
  magic: CheckCircle, // Placeholder for magic wand icon
  pen: RefreshCw, // Placeholder for pen icon
  eraser: XCircle,
  edit: RefreshCw,
  user: CheckCircle, // Placeholder for user icon
  mail: RefreshCw, // Placeholder for mail icon
  offline: XCircle, // Placeholder for offline icon
  trash: XCircle
}

export function HealthInsuranceErrorDisplay({
  error,
  language = 'en',
  onAction,
  onDismiss,
  showDetails = false,
  autoRetry = false,
  className = ''
}: HealthInsuranceErrorDisplayProps) {
  const [isRetrying, setIsRetrying] = useState(false)
  const [retryCountdown, setRetryCountdown] = useState(0)

  const messages = healthInsuranceErrorMessages[language]
  const errorMessage = messages[error.type]

  // Auto-retry functionality
  useEffect(() => {
    if (autoRetry && errorMessage?.autoRetry && errorMessage.retryDelay) {
      const delay = errorMessage.retryDelay / 1000 // Convert to seconds
      setRetryCountdown(delay)

      const countdownInterval = setInterval(() => {
        setRetryCountdown(prev => {
          if (prev <= 1) {
            clearInterval(countdownInterval)
            handleAction('retry')
            return 0
          }
          return prev - 1
        })
      }, 1000)

      return () => clearInterval(countdownInterval)
    }
  }, [autoRetry, errorMessage, error.type])

  const handleAction = async (action: string) => {
    if (action === 'retry') {
      setIsRetrying(true)
    }

    try {
      await onAction?.(action)
    } finally {
      setIsRetrying(false)
    }
  }

  const getSeverityColor = (severity: ErrorSeverity) => {
    switch (severity) {
      case ErrorSeverity.LOW:
        return 'border-blue-200 bg-blue-50 text-blue-800'
      case ErrorSeverity.MEDIUM:
        return 'border-yellow-200 bg-yellow-50 text-yellow-800'
      case ErrorSeverity.HIGH:
        return 'border-orange-200 bg-orange-50 text-orange-800'
      case ErrorSeverity.CRITICAL:
        return 'border-red-200 bg-red-50 text-red-800'
      default:
        return 'border-gray-200 bg-gray-50 text-gray-800'
    }
  }

  const getSeverityIcon = (severity: ErrorSeverity) => {
    switch (severity) {
      case ErrorSeverity.LOW:
      case ErrorSeverity.MEDIUM:
        return <AlertTriangle className="h-4 w-4" />
      case ErrorSeverity.HIGH:
      case ErrorSeverity.CRITICAL:
        return <XCircle className="h-4 w-4" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  const renderActionButton = (action: ErrorRecoveryAction, index: number) => {
    const IconComponent = iconMap[action.icon as keyof typeof iconMap] || AlertTriangle
    const isRetryAction = action.action === 'retry'
    const showLoading = isRetryAction && isRetrying

    return (
      <Button
        key={index}
        variant={action.primary ? 'default' : 'outline'}
        size="sm"
        onClick={() => handleAction(action.action)}
        disabled={showLoading || (retryCountdown > 0 && isRetryAction)}
        className="flex items-center gap-2"
      >
        {showLoading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <IconComponent className="h-4 w-4" />
        )}
        
        {retryCountdown > 0 && isRetryAction ? (
          `${action.label} (${retryCountdown}s)`
        ) : (
          action.label
        )}
      </Button>
    )
  }

  if (!errorMessage) {
    // Fallback for unknown error types
    return (
      <Alert className={`${getSeverityColor(error.severity)} ${className}`}>
        {getSeverityIcon(error.severity)}
        <AlertDescription>
          <div className="space-y-3">
            <div>
              <h4 className="font-semibold">
                {language === 'es' ? 'Error Inesperado' : 'Unexpected Error'}
              </h4>
              <p className="text-sm mt-1">
                {error.message || (
                  language === 'es' 
                    ? 'Ocurrió un error inesperado. Por favor contacte a soporte.'
                    : 'An unexpected error occurred. Please contact support.'
                )}
              </p>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleAction('contact_support')}
                className="flex items-center gap-2"
              >
                <HelpCircle className="h-4 w-4" />
                {language === 'es' ? 'Contactar Soporte' : 'Contact Support'}
              </Button>
              
              {onDismiss && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onDismiss}
                >
                  {language === 'es' ? 'Cerrar' : 'Dismiss'}
                </Button>
              )}
            </div>
          </div>
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <Card className={`${className}`}>
      <CardContent className="p-4">
        <Alert className={getSeverityColor(error.severity)}>
          {getSeverityIcon(error.severity)}
          <AlertDescription>
            <div className="space-y-4">
              {/* Error Title and Message */}
              <div>
                <h4 className="font-semibold text-base mb-2">
                  {errorMessage.title}
                </h4>
                <p className="text-sm">
                  {errorMessage.message}
                </p>
              </div>

              {/* Recovery Message */}
              {errorMessage.recovery && (
                <div className="bg-white bg-opacity-50 p-3 rounded border">
                  <p className="text-sm font-medium">
                    💡 {errorMessage.recovery}
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              {errorMessage.actions && errorMessage.actions.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {errorMessage.actions.map((action, index) => 
                    renderActionButton(action, index)
                  )}
                </div>
              )}

              {/* Dismiss Button */}
              {onDismiss && (
                <div className="flex justify-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onDismiss}
                    className="text-xs"
                  >
                    {language === 'es' ? 'Cerrar' : 'Dismiss'}
                  </Button>
                </div>
              )}

              {/* Error Details (Development/Debug) */}
              {showDetails && (process.env.NODE_ENV === 'development' || showDetails) && (
                <details className="mt-4">
                  <summary className="cursor-pointer text-xs text-gray-600 hover:text-gray-800">
                    {language === 'es' ? 'Detalles Técnicos' : 'Technical Details'}
                  </summary>
                  <div className="mt-2 p-3 bg-white bg-opacity-50 rounded text-xs space-y-1">
                    <div><strong>Error ID:</strong> {error.id}</div>
                    <div><strong>Type:</strong> {error.type}</div>
                    <div><strong>Severity:</strong> {error.severity}</div>
                    <div><strong>Timestamp:</strong> {error.timestamp.toISOString()}</div>
                    {error.context && (
                      <div>
                        <strong>Context:</strong>
                        <pre className="mt-1 text-xs bg-gray-100 p-2 rounded overflow-auto">
                          {JSON.stringify(error.context, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}
            </div>
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  )
}

// Simplified error toast component for non-blocking errors
export function HealthInsuranceErrorToast({
  error,
  language = 'en',
  onAction,
  onDismiss,
  duration = 5000
}: Omit<HealthInsuranceErrorDisplayProps, 'showDetails' | 'autoRetry'> & {
  duration?: number
}) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false)
        onDismiss?.()
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [duration, onDismiss])

  if (!isVisible) return null

  const messages = healthInsuranceErrorMessages[language]
  const errorMessage = messages[error.type]

  return (
    <div className="fixed top-4 right-4 z-50 max-w-md">
      <Alert className={`${getSeverityColor(error.severity)} shadow-lg`}>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h4 className="font-semibold text-sm">
                {errorMessage?.title || 'Error'}
              </h4>
              <p className="text-xs mt-1">
                {errorMessage?.message || error.message}
              </p>
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setIsVisible(false)
                onDismiss?.()
              }}
              className="ml-2 h-6 w-6 p-0"
            >
              <XCircle className="h-4 w-4" />
            </Button>
          </div>
          
          {errorMessage?.actions && errorMessage.actions.length > 0 && (
            <div className="flex gap-1 mt-2">
              {errorMessage.actions.slice(0, 2).map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => onAction?.(action.action)}
                  className="text-xs h-6"
                >
                  {action.label}
                </Button>
              ))}
            </div>
          )}
        </AlertDescription>
      </Alert>
    </div>
  )
}

function getSeverityColor(severity: ErrorSeverity): string {
  switch (severity) {
    case ErrorSeverity.LOW:
      return 'border-blue-200 bg-blue-50 text-blue-800'
    case ErrorSeverity.MEDIUM:
      return 'border-yellow-200 bg-yellow-50 text-yellow-800'
    case ErrorSeverity.HIGH:
      return 'border-orange-200 bg-orange-50 text-orange-800'
    case ErrorSeverity.CRITICAL:
      return 'border-red-200 bg-red-50 text-red-800'
    default:
      return 'border-gray-200 bg-gray-50 text-gray-800'
  }
}
