import React, { useState, useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  Eye, 
  EyeOff,
  Loader2
} from 'lucide-react'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
  success?: boolean
  loading?: boolean
  helpText?: string
  icon?: React.ReactNode
  required?: boolean
  onValidate?: (value: string) => string | null
  autoFormat?: 'phone' | 'ssn' | 'zipcode'
  showPasswordToggle?: boolean
  floatingLabel?: boolean
}

export function FormInput({
  label,
  error,
  success,
  loading,
  helpText,
  icon,
  required,
  onValidate,
  autoFormat,
  showPasswordToggle,
  floatingLabel = true,
  className,
  value,
  onChange,
  onBlur,
  type = 'text',
  disabled,
  ...props
}: FormInputProps) {
  const [localValue, setLocalValue] = useState(value || '')
  const [localError, setLocalError] = useState(error)
  const [touched, setTouched] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  
  useEffect(() => {
    setLocalValue(value || '')
  }, [value])
  
  useEffect(() => {
    setLocalError(error)
  }, [error])
  
  // Auto-formatting functions
  const formatPhone = (val: string) => {
    const cleaned = val.replace(/\D/g, '')
    const match = cleaned.match(/^(\d{0,3})(\d{0,3})(\d{0,4})$/)
    if (!match) return val
    
    const parts = []
    if (match[1]) parts.push(`(${match[1]}`)
    if (match[2]) parts.push(`) ${match[2]}`)
    if (match[3]) parts.push(`-${match[3]}`)
    
    return parts.join('').replace(/\s+$/, '')
  }
  
  const formatSSN = (val: string) => {
    const cleaned = val.replace(/\D/g, '')
    const match = cleaned.match(/^(\d{0,3})(\d{0,2})(\d{0,4})$/)
    if (!match) return val
    
    const parts = []
    if (match[1]) parts.push(match[1])
    if (match[2]) parts.push(match[2])
    if (match[3]) parts.push(match[3])
    
    return parts.join('-')
  }
  
  const formatZipCode = (val: string) => {
    const cleaned = val.replace(/\D/g, '')
    if (cleaned.length <= 5) return cleaned
    return `${cleaned.slice(0, 5)}-${cleaned.slice(5, 9)}`
  }
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let newValue = e.target.value
    
    // Apply auto-formatting
    if (autoFormat === 'phone') {
      newValue = formatPhone(newValue)
    } else if (autoFormat === 'ssn') {
      newValue = formatSSN(newValue)
    } else if (autoFormat === 'zipcode') {
      newValue = formatZipCode(newValue)
    }
    
    setLocalValue(newValue)
    
    // Create synthetic event with formatted value
    const syntheticEvent = {
      ...e,
      target: {
        ...e.target,
        value: newValue
      }
    }
    
    onChange?.(syntheticEvent as React.ChangeEvent<HTMLInputElement>)
    
    // Real-time validation if touched
    if (touched && onValidate) {
      const validationError = onValidate(newValue)
      setLocalError(validationError || undefined)
    }
  }
  
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setTouched(true)
    setIsFocused(false)
    
    // Validate on blur
    if (onValidate) {
      const validationError = onValidate(e.target.value)
      setLocalError(validationError || undefined)
    }
    
    onBlur?.(e)
  }
  
  const handleFocus = () => {
    setIsFocused(true)
  }
  
  const inputType = showPassword && type === 'password' && !showPasswordToggle 
    ? 'text' 
    : type
  
  const hasValue = String(localValue).length > 0
  const showFloatingLabel = floatingLabel && (isFocused || hasValue)
  
  return (
    <div className={cn("relative space-y-2", className)}>
      {!floatingLabel && (
        <div className="flex items-center justify-between mb-2">
          <Label 
            htmlFor={props.id}
            className={cn(
              "text-sm font-medium transition-colors",
              localError && touched && "text-destructive",
              success && "text-green-600"
            )}
          >
            {label}
            {required && <span className="text-destructive ml-1">*</span>}
          </Label>
          {helpText && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="max-w-xs">{helpText}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
      )}
      
      <div className="relative">
        {/* Floating Label */}
        {floatingLabel && (
          <Label
            htmlFor={props.id}
            className={cn(
              "absolute left-3 transition-all duration-200 pointer-events-none z-10",
              showFloatingLabel ? [
                "top-0 -translate-y-1/2 text-xs px-1 bg-background",
                localError && touched && "text-destructive",
                success && "text-green-600",
                isFocused && !localError && "text-primary"
              ] : [
                "top-1/2 -translate-y-1/2 text-base text-muted-foreground"
              ]
            )}
          >
            {label}
            {required && <span className="text-destructive ml-1">*</span>}
          </Label>
        )}
        
        {/* Icon */}
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
            {icon}
          </div>
        )}
        
        {/* Input */}
        <Input
          ref={inputRef}
          type={showPassword ? 'text' : inputType}
          value={localValue}
          onChange={handleChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          disabled={disabled || loading}
          className={cn(
            "pr-10 transition-all duration-200",
            icon && "pl-10",
            floatingLabel && "pt-6 pb-2",
            // Error state
            localError && touched && [
              "border-destructive",
              "focus:border-destructive",
              "focus:ring-destructive"
            ],
            // Success state
            success && !localError && [
              "border-green-500",
              "focus:border-green-500",
              "focus:ring-green-500"
            ],
            // Focus state
            isFocused && !localError && !success && [
              "border-primary",
              "ring-2 ring-primary/20"
            ],
            // Touch target for mobile (minimum 44px height)
            "min-h-[44px] touch-manipulation"
          )}
          aria-invalid={!!localError && touched}
          aria-describedby={
            localError && touched ? `${props.id}-error` : 
            helpText ? `${props.id}-help` : undefined
          }
          {...props}
        />
        
        {/* Status Icons */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
          {loading && (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          )}
          
          {!loading && success && !localError && (
            <CheckCircle2 className="h-4 w-4 text-green-500" />
          )}
          
          {!loading && localError && touched && (
            <AlertCircle className="h-4 w-4 text-destructive" />
          )}
          
          {showPasswordToggle && type === 'password' && (
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-muted-foreground hover:text-foreground transition-colors"
              tabIndex={-1}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          )}
        </div>
      </div>
      
      {/* Error Message */}
      {localError && touched && (
        <p 
          id={`${props.id}-error`}
          className="text-sm text-destructive mt-1 animate-in slide-in-from-top-1"
        >
          {localError}
        </p>
      )}
      
      {/* Help Text (when not using tooltip) */}
      {helpText && !floatingLabel && (
        <p 
          id={`${props.id}-help`}
          className="text-sm text-muted-foreground mt-1"
        >
          {helpText}
        </p>
      )}
    </div>
  )
}