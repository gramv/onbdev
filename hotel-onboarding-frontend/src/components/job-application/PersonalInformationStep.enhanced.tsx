import React, { useEffect, useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { FormInput } from '@/components/ui/form-input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { formValidator, ValidationRule } from '@/utils/formValidation'
import { 
  Mail, 
  Phone, 
  MapPin, 
  User, 
  Car, 
  Info,
  Building2,
  CheckCircle2,
  Briefcase,
  Home,
  Smartphone
} from 'lucide-react'

interface PersonalInformationStepProps {
  formData: any
  updateFormData: (data: any) => void
  validationErrors: Record<string, string>
  onComplete: (isComplete: boolean) => void
}

const states = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

export default function PersonalInformationStep({
  formData,
  updateFormData,
  validationErrors: externalErrors,
  onComplete
}: PersonalInformationStepProps) {
  const { t } = useTranslation()
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  // Validation rules for personal information
  const validationRules: ValidationRule[] = [
    { field: 'first_name', required: true, type: 'string', minLength: 1, maxLength: 50 },
    { field: 'last_name', required: true, type: 'string', minLength: 1, maxLength: 50 },
    { field: 'email', required: true, type: 'email' },
    { field: 'phone', required: true, type: 'phone' },
    { field: 'phone_is_cell', required: false },
    { field: 'phone_is_home', required: false },
    { field: 'address', required: true, type: 'string', minLength: 5, maxLength: 100 },
    { field: 'city', required: true, type: 'string', minLength: 2, maxLength: 50 },
    { field: 'state', required: true, type: 'string', minLength: 2, maxLength: 2 },
    { field: 'zip_code', required: true, type: 'zipCode' },
    { field: 'age_verification', required: true },
    { field: 'work_authorized', required: true, type: 'string' },
    { field: 'sponsorship_required', required: true, type: 'string' },
    { field: 'reliable_transportation', required: true, type: 'string' }
  ]

  useEffect(() => {
    validateStep()
  }, [formData])

  const validateStep = () => {
    const stepData = {
      first_name: formData.first_name,
      middle_name: formData.middle_name,
      last_name: formData.last_name,
      email: formData.email,
      phone: formData.phone,
      phone_is_cell: formData.phone_is_cell,
      phone_is_home: formData.phone_is_home,
      address: formData.address,
      apartment_unit: formData.apartment_unit,
      city: formData.city,
      state: formData.state,
      zip_code: formData.zip_code,
      age_verification: formData.age_verification,
      work_authorized: formData.work_authorized,
      sponsorship_required: formData.sponsorship_required,
      reliable_transportation: formData.reliable_transportation,
      transportation_method: formData.transportation_method,
      transportation_other: formData.transportation_other
    }

    const result = formValidator.validateForm(stepData, validationRules)
    let errors = { ...result.errors }
    
    // Additional validation for conditional fields
    if (formData.reliable_transportation === 'yes' && !formData.transportation_method) {
      errors.transportation_method = t('jobApplication.steps.personalInfo.validation.transportationMethodRequired')
    }
    if (formData.transportation_method === 'other' && !formData.transportation_other) {
      errors.transportation_other = t('jobApplication.steps.personalInfo.validation.transportationOtherRequired')
    }
    
    setLocalErrors(errors)
    
    // Check if all required fields are filled and valid
    const isComplete = result.isValid && 
      stepData.first_name && 
      stepData.last_name && 
      stepData.email && 
      stepData.phone &&
      (stepData.phone_is_cell || stepData.phone_is_home) &&
      stepData.address &&
      stepData.city &&
      stepData.state &&
      stepData.zip_code &&
      stepData.age_verification &&
      stepData.work_authorized &&
      stepData.sponsorship_required &&
      stepData.reliable_transportation &&
      (stepData.reliable_transportation === 'no' || 
        (stepData.transportation_method && 
          (stepData.transportation_method !== 'other' || stepData.transportation_other))) &&
      Object.keys(errors).length === 0

    onComplete(isComplete)
  }

  const handleInputChange = (field: string, value: any) => {
    updateFormData({ [field]: value })
    setTouched(prev => ({ ...prev, [field]: true }))
    // Also mark phone type as touched when either checkbox is changed
    if (field === 'phone_is_cell' || field === 'phone_is_home') {
      setTouched(prev => ({ ...prev, phone_is_cell: true, phone_is_home: true }))
    }
  }

  const getError = (field: string) => {
    return touched[field] ? (localErrors[field] || externalErrors[field]) : ''
  }

  // Validation functions for FormInput
  const validateEmail = useCallback((value: string) => {
    if (!value) return 'Email is required'
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) return 'Please enter a valid email address'
    return null
  }, [])

  const validatePhone = useCallback((value: string) => {
    if (!value) return 'Phone number is required'
    const phoneDigits = value.replace(/\D/g, '')
    if (phoneDigits.length !== 10) return 'Please enter a valid 10-digit phone number'
    return null
  }, [])

  const validateRequired = useCallback((fieldName: string) => (value: string) => {
    if (!value || value.trim() === '') return `${fieldName} is required`
    return null
  }, [])

  const validateZipCode = useCallback((value: string) => {
    if (!value) return 'ZIP code is required'
    const zipDigits = value.replace(/\D/g, '')
    if (zipDigits.length !== 5 && zipDigits.length !== 9) {
      return 'Please enter a valid 5 or 9 digit ZIP code'
    }
    return null
  }, [])

  return (
    <div className="space-y-6" data-testid="personal-info-step">
      {/* Personal Information Card */}
      <Card className="shadow-sm">
        <CardHeader className="pb-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
          <CardTitle className="flex items-center gap-2 text-lg">
            <User className="h-5 w-5 text-blue-600 dark:text-blue-400" data-testid="user-icon" />
            Personal Information
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4" data-testid="name-section">
            <FormInput
              id="first_name"
              label={t('jobApplication.steps.personalInfo.fields.firstName')}
              required
              value={formData.first_name || ''}
              onChange={(e) => handleInputChange('first_name', e.target.value)}
              onValidate={validateRequired('First name')}
              placeholder="John"
              icon={<User className="h-4 w-4" />}
              success={!!formData.first_name && !getError('first_name')}
              error={getError('first_name')}
            />
            
            <FormInput
              id="middle_name"
              label={t('jobApplication.steps.personalInfo.fields.middleName')}
              value={formData.middle_name || ''}
              onChange={(e) => handleInputChange('middle_name', e.target.value)}
              placeholder="M"
              success={!!formData.middle_name}
            />
            
            <FormInput
              id="last_name"
              label={t('jobApplication.steps.personalInfo.fields.lastName')}
              required
              value={formData.last_name || ''}
              onChange={(e) => handleInputChange('last_name', e.target.value)}
              onValidate={validateRequired('Last name')}
              placeholder="Doe"
              success={!!formData.last_name && !getError('last_name')}
              error={getError('last_name')}
            />
          </div>
        </CardContent>
      </Card>

      {/* Contact Information Card */}
      <Card className="shadow-sm">
        <CardHeader className="pb-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Mail className="h-5 w-5 text-green-600 dark:text-green-400" data-testid="mail-icon" />
            Contact Information
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormInput
              id="email"
              type="email"
              label={t('jobApplication.steps.personalInfo.fields.email')}
              required
              value={formData.email || ''}
              onChange={(e) => handleInputChange('email', e.target.value)}
              onValidate={validateEmail}
              placeholder="john.doe@example.com"
              icon={<Mail className="h-4 w-4" />}
              success={!!formData.email && !getError('email')}
              error={getError('email')}
              helpText="We'll use this email for application updates"
            />
            
            <FormInput
              id="phone"
              type="tel"
              label={t('jobApplication.steps.personalInfo.fields.phone')}
              required
              value={formData.phone || ''}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              onValidate={validatePhone}
              autoFormat="phone"
              placeholder="(555) 123-4567"
              icon={<Phone className="h-4 w-4" />}
              success={!!formData.phone && !getError('phone')}
              error={getError('phone')}
            />
          </div>
          
          {/* Phone Type Selection */}
          <div className="flex flex-col sm:flex-row gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
            <div className="flex items-center space-x-2">
              <Checkbox 
                id="phone_is_cell"
                checked={formData.phone_is_cell || false}
                onCheckedChange={(checked) => handleInputChange('phone_is_cell', checked)}
                className="min-w-[20px] min-h-[20px]"
              />
              <Label 
                htmlFor="phone_is_cell" 
                className="flex items-center gap-2 cursor-pointer"
              >
                <Smartphone className="h-4 w-4 text-gray-500" />
                {t('jobApplication.steps.personalInfo.fields.cellPhone')}
              </Label>
            </div>
            
            <div className="flex items-center space-x-2">
              <Checkbox 
                id="phone_is_home"
                checked={formData.phone_is_home || false}
                onCheckedChange={(checked) => handleInputChange('phone_is_home', checked)}
                className="min-w-[20px] min-h-[20px]"
              />
              <Label 
                htmlFor="phone_is_home" 
                className="flex items-center gap-2 cursor-pointer"
              >
                <Home className="h-4 w-4 text-gray-500" />
                {t('jobApplication.steps.personalInfo.fields.homePhone')}
              </Label>
            </div>
          </div>
          
          {!formData.phone_is_cell && !formData.phone_is_home && touched.phone && (
            <Alert className="border-orange-200 bg-orange-50 dark:bg-orange-900/20">
              <Info className="h-4 w-4 text-orange-600" />
              <AlertDescription className="text-orange-700 dark:text-orange-300">
                Please select at least one phone type
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Address Information Card */}
      <Card className="shadow-sm">
        <CardHeader className="pb-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
          <CardTitle className="flex items-center gap-2 text-lg">
            <MapPin className="h-5 w-5 text-purple-600 dark:text-purple-400" data-testid="map-icon" />
            Address Information
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormInput
              id="address"
              label={t('jobApplication.steps.personalInfo.fields.address')}
              required
              value={formData.address || ''}
              onChange={(e) => handleInputChange('address', e.target.value)}
              onValidate={validateRequired('Address')}
              placeholder="123 Main Street"
              icon={<Building2 className="h-4 w-4" />}
              success={!!formData.address && !getError('address')}
              error={getError('address')}
            />
            
            <FormInput
              id="apartment_unit"
              label={t('jobApplication.steps.personalInfo.fields.apartmentUnit')}
              value={formData.apartment_unit || ''}
              onChange={(e) => handleInputChange('apartment_unit', e.target.value)}
              placeholder="Apt 4B"
              success={!!formData.apartment_unit}
            />
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-6 gap-4">
            <div className="sm:col-span-3">
              <FormInput
                id="city"
                label={t('jobApplication.steps.personalInfo.fields.city')}
                required
                value={formData.city || ''}
                onChange={(e) => handleInputChange('city', e.target.value)}
                onValidate={validateRequired('City')}
                placeholder="New York"
                success={!!formData.city && !getError('city')}
                error={getError('city')}
              />
            </div>
            
            <div className="sm:col-span-1">
              <Label htmlFor="state" className="block text-sm font-medium mb-2">
                {t('jobApplication.steps.personalInfo.fields.state')} *
              </Label>
              <Select 
                value={formData.state || ''} 
                onValueChange={(value) => handleInputChange('state', value)}
              >
                <SelectTrigger 
                  id="state" 
                  className={`min-h-[44px] ${getError('state') ? 'border-red-500' : ''} ${formData.state ? 'border-green-500' : ''}`}
                >
                  <SelectValue placeholder="State" />
                </SelectTrigger>
                <SelectContent>
                  {states.map(state => (
                    <SelectItem key={state} value={state}>
                      {state}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {getError('state') && (
                <p className="text-sm text-red-600 mt-1" role="alert">{getError('state')}</p>
              )}
            </div>
            
            <div className="sm:col-span-2">
              <FormInput
                id="zip_code"
                label={t('jobApplication.steps.personalInfo.fields.zipCode')}
                required
                value={formData.zip_code || ''}
                onChange={(e) => handleInputChange('zip_code', e.target.value)}
                onValidate={validateZipCode}
                autoFormat="zipcode"
                placeholder="10001"
                success={!!formData.zip_code && !getError('zip_code')}
                error={getError('zip_code')}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Eligibility Information Card */}
      <Card className="shadow-sm">
        <CardHeader className="pb-4 bg-gradient-to-r from-orange-50 to-yellow-50 dark:from-orange-900/20 dark:to-yellow-900/20">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Briefcase className="h-5 w-5 text-orange-600 dark:text-orange-400" />
            Eligibility Information
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-6">
          {/* Age Verification */}
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="flex items-center space-x-3">
              <Checkbox 
                id="age_verification"
                checked={formData.age_verification || false}
                onCheckedChange={(checked) => handleInputChange('age_verification', checked)}
                className="min-w-[20px] min-h-[20px]"
              />
              <Label 
                htmlFor="age_verification" 
                className="cursor-pointer text-sm sm:text-base"
              >
                {t('jobApplication.steps.personalInfo.fields.ageVerification')} *
              </Label>
            </div>
            {getError('age_verification') && (
              <p className="text-sm text-red-600 mt-2 ml-7" role="alert">
                {getError('age_verification')}
              </p>
            )}
          </div>

          {/* Work Authorization */}
          <div className="space-y-2">
            <Label className="text-sm sm:text-base">
              {t('jobApplication.steps.personalInfo.fields.workAuthorized')} *
            </Label>
            <RadioGroup 
              value={formData.work_authorized || ''} 
              onValueChange={(value) => handleInputChange('work_authorized', value)}
              className="flex flex-col sm:flex-row gap-4"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="yes" id="work_authorized_yes" className="min-w-[20px] min-h-[20px]" />
                <Label htmlFor="work_authorized_yes" className="cursor-pointer">Yes</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="no" id="work_authorized_no" className="min-w-[20px] min-h-[20px]" />
                <Label htmlFor="work_authorized_no" className="cursor-pointer">No</Label>
              </div>
            </RadioGroup>
            {getError('work_authorized') && (
              <p className="text-sm text-red-600" role="alert">{getError('work_authorized')}</p>
            )}
          </div>

          {/* Sponsorship Required */}
          <div className="space-y-2">
            <Label className="text-sm sm:text-base">
              {t('jobApplication.steps.personalInfo.fields.sponsorshipRequired')} *
            </Label>
            <RadioGroup 
              value={formData.sponsorship_required || ''} 
              onValueChange={(value) => handleInputChange('sponsorship_required', value)}
              className="flex flex-col sm:flex-row gap-4"
            >
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="yes" id="sponsorship_yes" className="min-w-[20px] min-h-[20px]" />
                <Label htmlFor="sponsorship_yes" className="cursor-pointer">Yes</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="no" id="sponsorship_no" className="min-w-[20px] min-h-[20px]" />
                <Label htmlFor="sponsorship_no" className="cursor-pointer">No</Label>
              </div>
            </RadioGroup>
            {getError('sponsorship_required') && (
              <p className="text-sm text-red-600" role="alert">{getError('sponsorship_required')}</p>
            )}
          </div>

          {/* Reliable Transportation */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label className="text-sm sm:text-base">
                {t('jobApplication.steps.personalInfo.fields.reliableTransportation')} *
              </Label>
              <RadioGroup 
                value={formData.reliable_transportation || ''} 
                onValueChange={(value) => handleInputChange('reliable_transportation', value)}
                className="flex flex-col sm:flex-row gap-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem 
                    value="yes" 
                    id="transportation_yes" 
                    className="min-w-[20px] min-h-[20px]" 
                  />
                  <Label htmlFor="transportation_yes" className="cursor-pointer">
                    Yes, I have reliable transportation
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem 
                    value="no" 
                    id="transportation_no" 
                    className="min-w-[20px] min-h-[20px]" 
                  />
                  <Label htmlFor="transportation_no" className="cursor-pointer">
                    No, I do not have reliable transportation
                  </Label>
                </div>
              </RadioGroup>
              {getError('reliable_transportation') && (
                <p className="text-sm text-red-600" role="alert">{getError('reliable_transportation')}</p>
              )}
            </div>

            {/* Transportation Method (Conditional) */}
            {formData.reliable_transportation === 'yes' && (
              <div className="ml-0 sm:ml-7 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg space-y-4 animate-in slide-in-from-top-2">
                <Label htmlFor="transportation_method" className="flex items-center gap-2">
                  <Car className="h-4 w-4 text-gray-500" />
                  {t('jobApplication.steps.personalInfo.fields.transportationMethod')} *
                  <span className="text-xs text-gray-500" data-testid="help-icon">
                    (How will you get to work?)
                  </span>
                </Label>
                <Select 
                  value={formData.transportation_method || ''} 
                  onValueChange={(value) => handleInputChange('transportation_method', value)}
                >
                  <SelectTrigger 
                    id="transportation_method" 
                    className={`min-h-[44px] ${getError('transportation_method') ? 'border-red-500' : ''} ${formData.transportation_method ? 'border-green-500' : ''}`}
                  >
                    <SelectValue placeholder="Select transportation method" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="car">Personal Vehicle</SelectItem>
                    <SelectItem value="public_transit">Public Transportation</SelectItem>
                    <SelectItem value="carpool">Carpool/Rideshare</SelectItem>
                    <SelectItem value="bicycle">Bicycle</SelectItem>
                    <SelectItem value="walk">Walking</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
                {getError('transportation_method') && (
                  <p className="text-sm text-red-600" role="alert">{getError('transportation_method')}</p>
                )}

                {/* Other Transportation (Conditional) */}
                {formData.transportation_method === 'other' && (
                  <FormInput
                    id="transportation_other"
                    label="Please specify"
                    required
                    value={formData.transportation_other || ''}
                    onChange={(e) => handleInputChange('transportation_other', e.target.value)}
                    onValidate={validateRequired('Transportation method')}
                    placeholder="Please describe your transportation method"
                    success={!!formData.transportation_other && !getError('transportation_other')}
                    error={getError('transportation_other')}
                  />
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Completion Status */}
      {formData.first_name && formData.last_name && formData.email && (
        <Alert className="border-green-200 bg-green-50 dark:bg-green-900/20">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700 dark:text-green-300">
            Great progress! Complete all required fields to continue.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}