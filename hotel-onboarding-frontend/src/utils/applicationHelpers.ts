/**
 * Application Form Helper Functions
 * Utilities for job application form functionality
 */

export interface ValidationResult {
  isValid: boolean
  errors: Record<string, string>
}

/**
 * Format phone number for display
 */
export const formatPhoneNumber = (value: string): string => {
  const numbers = value.replace(/\D/g, '')
  if (numbers.length <= 3) return numbers
  if (numbers.length <= 6) return `(${numbers.slice(0, 3)}) ${numbers.slice(3)}`
  return `(${numbers.slice(0, 3)}) ${numbers.slice(3, 6)}-${numbers.slice(6, 10)}`
}

/**
 * Format SSN for display (with masking)
 */
export const formatSSN = (value: string, mask = false): string => {
  const numbers = value.replace(/\D/g, '')
  if (mask && numbers.length === 9) {
    return `***-**-${numbers.slice(5)}`
  }
  if (numbers.length <= 3) return numbers
  if (numbers.length <= 5) return `${numbers.slice(0, 3)}-${numbers.slice(3)}`
  return `${numbers.slice(0, 3)}-${numbers.slice(3, 5)}-${numbers.slice(5, 9)}`
}

/**
 * Format ZIP code
 */
export const formatZipCode = (value: string): string => {
  const numbers = value.replace(/\D/g, '')
  if (numbers.length <= 5) return numbers
  return `${numbers.slice(0, 5)}-${numbers.slice(5, 9)}`
}

/**
 * Validate email address
 */
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number (10 digits)
 */
export const validatePhone = (phone: string): boolean => {
  const phoneDigits = phone.replace(/\D/g, '')
  return phoneDigits.length === 10
}

/**
 * Validate ZIP code (5 or 9 digits)
 */
export const validateZipCode = (zip: string): boolean => {
  const zipDigits = zip.replace(/\D/g, '')
  return zipDigits.length === 5 || zipDigits.length === 9
}

/**
 * Calculate time since date
 */
export const getTimeSince = (date: Date): string => {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000)
  
  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`
  if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`
  
  return date.toLocaleDateString()
}

/**
 * Generate application recovery code
 */
export const generateRecoveryCode = (): string => {
  const timestamp = Date.now().toString(36)
  const random = Math.random().toString(36).substr(2, 5)
  return `${timestamp}-${random}`.toUpperCase()
}

/**
 * Debounce function for input validation
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

/**
 * Check if form section is complete
 */
export const isSectionComplete = (
  sectionData: Record<string, any>,
  requiredFields: string[]
): boolean => {
  return requiredFields.every(field => {
    const value = sectionData[field]
    if (value === undefined || value === null || value === '') return false
    if (typeof value === 'string' && value.trim() === '') return false
    if (Array.isArray(value) && value.length === 0) return false
    return true
  })
}

/**
 * Scroll to first error field
 */
export const scrollToError = (selector = '[aria-invalid="true"]'): void => {
  setTimeout(() => {
    const firstError = document.querySelector(selector)
    if (firstError) {
      firstError.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      })
      ;(firstError as HTMLElement).focus()
      
      // Add shake animation
      firstError.classList.add('animate-shake')
      setTimeout(() => {
        firstError.classList.remove('animate-shake')
      }, 500)
    }
  }, 100)
}

/**
 * Get device type for responsive behavior
 */
export const getDeviceType = (): 'mobile' | 'tablet' | 'desktop' => {
  const width = window.innerWidth
  if (width < 640) return 'mobile'
  if (width < 1024) return 'tablet'
  return 'desktop'
}

/**
 * Check if device is touch-enabled
 */
export const isTouchDevice = (): boolean => {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

/**
 * Export application data as JSON
 */
export const exportApplicationData = (data: any, applicationId: string): void => {
  const dataStr = JSON.stringify(data, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `application-${applicationId}-${Date.now()}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

/**
 * Network retry with exponential backoff
 */
export const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> => {
  let lastError: any
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error: any) {
      lastError = error
      
      if (i < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, i)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }
  
  throw lastError
}