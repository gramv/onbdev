import axios from 'axios'
import bankDatabase from '@/data/us-banks-routing.json'
import { getApiUrl } from '@/config/api'

export interface BankInfo {
  routing: string
  bank_name: string
  short_name: string
  ach_supported: boolean
  wire_supported: boolean
  state: string
  verified: boolean
}

export interface ValidationResult {
  valid: boolean
  bank?: BankInfo
  error?: string
  source?: 'local' | 'api' | 'cache'
}

class RoutingValidationService {
  private bankMap: Map<string, BankInfo>
  private validationCache: Map<string, ValidationResult>
  private pendingValidations: Map<string, Promise<ValidationResult>>
  private apiUrl: string

  constructor() {
    // Initialize bank map from local database
    this.bankMap = new Map()
    bankDatabase.banks.forEach((bank) => {
      this.bankMap.set(bank.routing, bank)
    })

    // Initialize caches
    this.validationCache = new Map()
    this.pendingValidations = new Map()
    
    // Use centralized API configuration
    this.apiUrl = getApiUrl()

    // Load cached validations from localStorage
    this.loadCachedValidations()
  }

  /**
   * Validate ABA routing number checksum
   * Uses the standard ABA checksum algorithm
   */
  validateABAChecksum(routing: string): boolean {
    // Must be exactly 9 digits
    if (!/^\d{9}$/.test(routing)) {
      return false
    }

    // ABA checksum algorithm
    const weights = [3, 7, 1, 3, 7, 1, 3, 7, 1]
    let sum = 0
    for (let i = 0; i < 9; i++) {
      sum += parseInt(routing[i]) * weights[i]
    }
    return sum % 10 === 0
  }

  /**
   * Main validation method - validates routing number and returns bank info
   */
  async validateRouting(routingNumber: string): Promise<ValidationResult> {
    // Clean input
    const cleaned = routingNumber.replace(/\D/g, '')

    // Check basic format
    if (cleaned.length !== 9) {
      return {
        valid: false,
        error: 'Routing number must be 9 digits'
      }
    }

    // Validate checksum
    if (!this.validateABAChecksum(cleaned)) {
      return {
        valid: false,
        error: 'Invalid routing number (checksum failed)'
      }
    }

    // Check if we have a pending validation for this number
    const pending = this.pendingValidations.get(cleaned)
    if (pending) {
      return pending
    }

    // Check memory cache
    const cached = this.validationCache.get(cleaned)
    if (cached) {
      return { ...cached, source: 'cache' }
    }

    // Check local database
    const localBank = this.bankMap.get(cleaned)
    if (localBank) {
      const result: ValidationResult = {
        valid: true,
        bank: localBank,
        source: 'local'
      }
      this.validationCache.set(cleaned, result)
      this.saveCachedValidations()
      return result
    }

    // If not found locally, call backend API
    const validationPromise = this.validateWithAPI(cleaned)
    this.pendingValidations.set(cleaned, validationPromise)
    
    try {
      const result = await validationPromise
      this.pendingValidations.delete(cleaned)
      return result
    } catch (error) {
      this.pendingValidations.delete(cleaned)
      throw error
    }
  }

  /**
   * Validate routing number via backend API
   */
  private async validateWithAPI(routingNumber: string): Promise<ValidationResult> {
    try {
      const response = await axios.post(
        `${this.apiUrl}/validate/routing-number`,
        { routing_number: routingNumber },
        { timeout: 5000 }
      )

      if (response.data.valid) {
        const result: ValidationResult = {
          valid: true,
          bank: response.data.bank,
          source: 'api'
        }
        
        // Cache the result
        this.validationCache.set(routingNumber, result)
        this.saveCachedValidations()
        
        return result
      } else {
        return {
          valid: false,
          error: response.data.error || 'Routing number not found',
          source: 'api'
        }
      }
    } catch (error) {
      console.error('API validation error:', error)
      
      // Fallback to basic validation only
      return {
        valid: true, // Checksum passed, so we'll allow it
        bank: {
          routing: routingNumber,
          bank_name: 'Bank (Unable to verify)',
          short_name: 'Unknown',
          ach_supported: true,
          wire_supported: false,
          state: '',
          verified: false
        },
        error: 'Unable to verify bank details at this time',
        source: 'cache'
      }
    }
  }

  /**
   * Search for banks by name
   */
  searchBanksByName(query: string): BankInfo[] {
    if (!query || query.length < 2) return []
    
    const lowerQuery = query.toLowerCase()
    const results: BankInfo[] = []
    
    // Search through local database
    for (const bank of this.bankMap.values()) {
      if (
        bank.bank_name.toLowerCase().includes(lowerQuery) ||
        bank.short_name.toLowerCase().includes(lowerQuery)
      ) {
        results.push(bank)
        if (results.length >= 10) break // Limit results
      }
    }
    
    return results
  }

  /**
   * Get popular banks for quick selection
   */
  getPopularBanks(): BankInfo[] {
    const popularRoutings = [
      '021000021', // Chase
      '026009593', // Bank of America
      '121000248', // Wells Fargo
      '021000089', // Citibank
      '071000013', // US Bank
      '031100649', // Capital One
      '256074974', // Navy Federal
      '124303120', // Ally Bank
      '084003997', // USAA
      '271070801'  // Chime
    ]
    
    return popularRoutings
      .map(routing => this.bankMap.get(routing))
      .filter(Boolean) as BankInfo[]
  }

  /**
   * Load cached validations from localStorage
   */
  private loadCachedValidations() {
    try {
      const stored = localStorage.getItem('routing_validations')
      if (stored) {
        const data = JSON.parse(stored)
        // Only load validations from last 30 days
        const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000)
        
        Object.entries(data).forEach(([routing, result]: [string, any]) => {
          if (result.timestamp && result.timestamp > thirtyDaysAgo) {
            this.validationCache.set(routing, result)
          }
        })
      }
    } catch (error) {
      console.error('Error loading cached validations:', error)
    }
  }

  /**
   * Save validations to localStorage
   */
  private saveCachedValidations() {
    try {
      const data: Record<string, any> = {}
      
      // Only save last 100 validations
      const entries = Array.from(this.validationCache.entries()).slice(-100)
      entries.forEach(([routing, result]) => {
        data[routing] = {
          ...result,
          timestamp: Date.now()
        }
      })
      
      localStorage.setItem('routing_validations', JSON.stringify(data))
    } catch (error) {
      console.error('Error saving cached validations:', error)
    }
  }

  /**
   * Clear all caches
   */
  clearCache() {
    this.validationCache.clear()
    localStorage.removeItem('routing_validations')
  }

  /**
   * Check if bank supports ACH
   */
  supportsACH(routingNumber: string): boolean {
    const bank = this.bankMap.get(routingNumber)
    return bank?.ach_supported ?? true // Default to true if unknown
  }

  /**
   * Check if bank supports Wire transfers
   */
  supportsWire(routingNumber: string): boolean {
    const bank = this.bankMap.get(routingNumber)
    return bank?.wire_supported ?? false // Default to false if unknown
  }

  /**
   * Get warnings for specific banks (credit unions, online-only, etc.)
   */
  getBankWarnings(routingNumber: string): string[] {
    const warnings: string[] = []
    const bank = this.bankMap.get(routingNumber)
    
    if (bank) {
      // Check for credit unions
      if (bank.bank_name.toLowerCase().includes('credit union')) {
        warnings.push('Credit union detected. Some features may be limited.')
      }
      
      // Check for online-only banks
      const onlineBanks = ['Chime', 'Ally Bank', 'SoFi', 'Discover', 'Cash App', 'Venmo', 'PayPal']
      if (onlineBanks.some(name => bank.short_name.includes(name))) {
        warnings.push('Online bank detected. Ensure account supports direct deposit.')
      }
      
      // Check for payment apps
      const paymentApps = ['Cash App', 'Venmo', 'PayPal', 'Chime', 'Green Dot']
      if (paymentApps.some(name => bank.short_name.includes(name))) {
        warnings.push('Payment app detected. Verify this is a checking account.')
      }
      
      // Check for wire support
      if (!bank.wire_supported) {
        warnings.push('This bank may not support wire transfers.')
      }
    }
    
    return warnings
  }
}

// Export singleton instance
export const routingValidationService = new RoutingValidationService()
export default routingValidationService