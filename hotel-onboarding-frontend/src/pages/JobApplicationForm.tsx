import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'

import { Loader2, AlertCircle, CheckCircle2, Phone, Mail, MapPin } from 'lucide-react'
import axios from 'axios'
import { formValidator, ValidationRule } from '@/utils/formValidation'

interface Property {
  id: string
  name: string
  address: string
  city: string
  state: string
  zip_code: string
  phone: string
}

interface PropertyInfo {
  property: Property
  departments_and_positions: Record<string, string[]>
  application_url: string
  is_accepting_applications: boolean
}

// These will be fetched from the backend
const defaultDepartments = [
  'Front Desk',
  'Housekeeping', 
  'Food & Beverage',
  'Maintenance'
]

const defaultPositions = {
  'Front Desk': ['Front Desk Agent', 'Night Auditor', 'Guest Services Representative', 'Concierge'],
  'Housekeeping': ['Housekeeper', 'Housekeeping Supervisor', 'Laundry Attendant', 'Public Area Attendant'],
  'Food & Beverage': ['Server', 'Bartender', 'Host/Hostess', 'Kitchen Staff', 'Banquet Server'],
  'Maintenance': ['Maintenance Technician', 'Engineering Assistant', 'Groundskeeper']
}

const cities = [
  'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
  'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville'
]

const states = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

export default function JobApplicationForm() {
  const { propertyId } = useParams()
  const [propertyInfo, setPropertyInfo] = useState<PropertyInfo | null>(null)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    department: '',
    position: '',
    work_authorized: '',
    sponsorship_required: '',
    start_date: '',
    shift_preference: '',
    employment_type: '',
    experience_years: '',
    hotel_experience: '',
    previous_employer: '',
    reason_for_leaving: '',
    additional_comments: '',
    // Position-specific questions
    availability_weekends: '',
    availability_holidays: '',
    reliable_transportation: '',
    physical_requirements_acknowledged: false,
    background_check_consent: false
  })
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [isDuplicateApplication, setIsDuplicateApplication] = useState(false)
  const [isCheckingDuplicate, setIsCheckingDuplicate] = useState(false)

  // Validation rules for job application form
  const validationRules: ValidationRule[] = [
    { field: 'first_name', required: true, type: 'string', minLength: 1, maxLength: 50 },
    { field: 'last_name', required: true, type: 'string', minLength: 1, maxLength: 50 },
    { field: 'email', required: true, type: 'email' },
    { field: 'phone', required: true, type: 'phone' },
    { field: 'address', required: true, type: 'string', minLength: 5, maxLength: 100 },
    { field: 'city', required: true, type: 'string', minLength: 2, maxLength: 50 },
    { field: 'state', required: true, type: 'string', minLength: 2, maxLength: 2 },
    { field: 'zip_code', required: true, type: 'zipCode' },
    { field: 'department', required: true, type: 'string' },
    { field: 'position', required: true, type: 'string' },
    { field: 'work_authorized', required: true, type: 'string' },
    { field: 'sponsorship_required', required: true, type: 'string' },
    { field: 'start_date', required: true, type: 'date', customValidator: (value) => {
      const today = new Date()
      const startDate = new Date(value)
      if (startDate < today) {
        return 'Start date cannot be in the past'
      }
      return null
    }},
    { field: 'shift_preference', required: true, type: 'string' },
    { field: 'employment_type', required: true, type: 'string' },
    { field: 'experience_years', required: true, type: 'string' },
    { field: 'hotel_experience', required: true, type: 'string' },
    { field: 'availability_weekends', required: true, type: 'string' },
    { field: 'availability_holidays', required: true, type: 'string' },
    { field: 'reliable_transportation', required: true, type: 'string' },
    { field: 'physical_requirements_acknowledged', required: true, customValidator: (value) => {
      return value === true ? null : 'You must acknowledge the physical requirements'
    }},
    { field: 'background_check_consent', required: true, customValidator: (value) => {
      return value === true ? null : 'Consent for background check is required'
    }}
  ]

  useEffect(() => {
    fetchProperty()
  }, [propertyId])

  // Check for duplicate applications when email and position change
  useEffect(() => {
    if (formData.email && formData.position && propertyId) {
      checkDuplicateApplication()
    }
  }, [formData.email, formData.position, propertyId])

  const fetchProperty = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/properties/${propertyId}/info`)
      setPropertyInfo(response.data)
    } catch (error) {
      console.error('Failed to fetch property:', error)
      setError('Failed to load property information. Please try again.')
    }
  }

  const checkDuplicateApplication = async () => {
    if (!formData.email || !formData.position || !propertyId) return
    
    setIsCheckingDuplicate(true)
    try {
      // Check if there's already an application with this email and position
      const response = await axios.get(`http://127.0.0.1:8000/applications/check-duplicate`, {
        params: {
          property_id: propertyId,
          email: formData.email.toLowerCase(),
          position: formData.position
        }
      })
      setIsDuplicateApplication(response.data.isDuplicate)
    } catch (error) {
      // If endpoint doesn't exist, we'll handle duplicates on submission
      console.log('Duplicate check endpoint not available, will check on submission')
    } finally {
      setIsCheckingDuplicate(false)
    }
  }

  const validateForm = () => {
    const result = formValidator.validateForm(formData, validationRules)
    setValidationErrors(result.errors)
    return result.isValid
  }

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const formatPhoneNumber = (value: string) => {
    const numbers = value.replace(/\D/g, '')
    if (numbers.length <= 3) return numbers
    if (numbers.length <= 6) return `(${numbers.slice(0, 3)}) ${numbers.slice(3)}`
    return `(${numbers.slice(0, 3)}) ${numbers.slice(3, 6)}-${numbers.slice(6, 10)}`
  }

  const getPositionSpecificQuestions = () => {
    const questions = []
    
    if (formData.department === 'Front Desk') {
      questions.push({
        key: 'customer_service_experience',
        label: 'Do you have customer service experience?',
        type: 'select',
        options: ['yes', 'no'],
        required: true
      })
    }
    
    if (formData.department === 'Housekeeping') {
      questions.push({
        key: 'physical_demands_ok',
        label: 'Are you comfortable with the physical demands of housekeeping (lifting, bending, standing for long periods)?',
        type: 'select',
        options: ['yes', 'no'],
        required: true
      })
    }
    
    if (formData.department === 'Food & Beverage') {
      questions.push({
        key: 'food_safety_certification',
        label: 'Do you have food safety certification?',
        type: 'select',
        options: ['yes', 'no'],
        required: true
      })
    }
    
    if (formData.department === 'Maintenance') {
      questions.push({
        key: 'maintenance_experience',
        label: 'Do you have maintenance or technical experience?',
        type: 'select',
        options: ['yes', 'no'],
        required: true
      })
    }
    
    return questions
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    // Validate form
    if (!validateForm()) {
      setError('Please correct the errors below and try again.')
      return
    }
    
    // Check for duplicate application
    if (isDuplicateApplication) {
      setError('You have already submitted an application for this position at this property.')
      return
    }
    
    setLoading(true)

    try {
      await axios.post(`http://127.0.0.1:8000/apply/${propertyId}`, formData)
      setSubmitted(true)
    } catch (err: any) {
      if (err.response?.status === 400 && err.response?.data?.detail?.includes('already submitted')) {
        setError('You have already submitted an application for this position. Please wait for a response before applying again.')
        setIsDuplicateApplication(true)
      } else {
        setError('Failed to submit application. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto flex items-center justify-center w-12 h-12 rounded-full bg-green-100 mb-4">
              <CheckCircle2 className="w-6 h-6 text-green-600" />
            </div>
            <CardTitle className="text-2xl font-bold text-green-600">Application Submitted!</CardTitle>
            <CardDescription>
              Thank you for your interest in working at {propertyInfo?.property?.name}. 
              We will review your application and contact you soon.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-800 font-medium">
                Next Steps:
              </p>
              <p className="text-sm text-blue-700 mt-1">
                Our hiring team will review your application and contact you within 3-5 business days.
              </p>
            </div>
            <p className="text-sm text-gray-600">
              You should receive a confirmation email shortly at {formData.email}
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-4 px-4 sm:py-8 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold">Job Application</CardTitle>
            <CardDescription>
              {propertyInfo ? (
                <div className="space-y-2">
                  <p>Apply for a position at {propertyInfo.property.name}</p>
                  <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center">
                      <MapPin className="w-4 h-4 mr-1" />
                      {propertyInfo.property.city}, {propertyInfo.property.state}
                    </div>
                    <div className="flex items-center">
                      <Phone className="w-4 h-4 mr-1" />
                      {propertyInfo.property.phone}
                    </div>
                  </div>
                </div>
              ) : (
                'Loading property information...'
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {isDuplicateApplication && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    You have already submitted an application for {formData.position} at this property. 
                    Please wait for a response before applying again.
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="first_name">First Name *</Label>
                    <Input
                      id="first_name"
                      value={formData.first_name}
                      onChange={(e) => handleInputChange('first_name', e.target.value)}
                      className={validationErrors.first_name ? 'border-red-500' : ''}
                      required
                    />
                    {validationErrors.first_name && (
                      <p className="text-sm text-red-600">{validationErrors.first_name}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="last_name">Last Name *</Label>
                    <Input
                      id="last_name"
                      value={formData.last_name}
                      onChange={(e) => handleInputChange('last_name', e.target.value)}
                      className={validationErrors.last_name ? 'border-red-500' : ''}
                      required
                    />
                    {validationErrors.last_name && (
                      <p className="text-sm text-red-600">{validationErrors.last_name}</p>
                    )}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className={`pl-10 ${validationErrors.email ? 'border-red-500' : ''}`}
                        placeholder="your.email@example.com"
                        required
                      />
                    </div>
                    {validationErrors.email && (
                      <p className="text-sm text-red-600">{validationErrors.email}</p>
                    )}
                    {isCheckingDuplicate && (
                      <p className="text-sm text-blue-600 flex items-center">
                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                        Checking for duplicate applications...
                      </p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone *</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="phone"
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => {
                          const formatted = formatPhoneNumber(e.target.value)
                          handleInputChange('phone', formatted)
                        }}
                        className={`pl-10 ${validationErrors.phone ? 'border-red-500' : ''}`}
                        placeholder="(555) 123-4567"
                        maxLength={14}
                        required
                      />
                    </div>
                    {validationErrors.phone && (
                      <p className="text-sm text-red-600">{validationErrors.phone}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="address">Address *</Label>
                  <Input
                    id="address"
                    value={formData.address}
                    onChange={(e) => handleInputChange('address', e.target.value)}
                    className={validationErrors.address ? 'border-red-500' : ''}
                    placeholder="123 Main Street"
                    required
                  />
                  {validationErrors.address && (
                    <p className="text-sm text-red-600">{validationErrors.address}</p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="city">City *</Label>
                    <Select value={formData.city} onValueChange={(value) => handleInputChange('city', value)}>
                      <SelectTrigger className={validationErrors.city ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select city" />
                      </SelectTrigger>
                      <SelectContent>
                        {cities.map(city => (
                          <SelectItem key={city} value={city}>{city}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {validationErrors.city && (
                      <p className="text-sm text-red-600">{validationErrors.city}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="state">State *</Label>
                    <Select value={formData.state} onValueChange={(value) => handleInputChange('state', value)}>
                      <SelectTrigger className={validationErrors.state ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select state" />
                      </SelectTrigger>
                      <SelectContent>
                        {states.map(state => (
                          <SelectItem key={state} value={state}>{state}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {validationErrors.state && (
                      <p className="text-sm text-red-600">{validationErrors.state}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="zip_code">ZIP Code *</Label>
                    <Input
                      id="zip_code"
                      value={formData.zip_code}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, '').slice(0, 5)
                        handleInputChange('zip_code', value)
                      }}
                      className={validationErrors.zip_code ? 'border-red-500' : ''}
                      placeholder="12345"
                      maxLength={5}
                      required
                    />
                    {validationErrors.zip_code && (
                      <p className="text-sm text-red-600">{validationErrors.zip_code}</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Position Interest</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="department">Department *</Label>
                    <Select value={formData.department} onValueChange={(value) => {
                      handleInputChange('department', value)
                      handleInputChange('position', '') // Reset position when department changes
                    }}>
                      <SelectTrigger className={validationErrors.department ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select department" />
                      </SelectTrigger>
                      <SelectContent>
                        {(propertyInfo?.departments_and_positions ? Object.keys(propertyInfo.departments_and_positions) : defaultDepartments).map(dept => (
                          <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {validationErrors.department && (
                      <p className="text-sm text-red-600">{validationErrors.department}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="position">Position *</Label>
                    <Select 
                      value={formData.position} 
                      onValueChange={(value) => handleInputChange('position', value)}
                      disabled={!formData.department}
                    >
                      <SelectTrigger className={validationErrors.position ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select position" />
                      </SelectTrigger>
                      <SelectContent>
                        {formData.department && (
                          propertyInfo?.departments_and_positions?.[formData.department] || 
                          defaultPositions[formData.department as keyof typeof defaultPositions] || 
                          []
                        ).map(pos => (
                          <SelectItem key={pos} value={pos}>{pos}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {validationErrors.position && (
                      <p className="text-sm text-red-600">{validationErrors.position}</p>
                    )}
                  </div>
                </div>

                {/* Position-specific questions */}
                {formData.department && getPositionSpecificQuestions().length > 0 && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-3">Position-Specific Questions</h4>
                    <div className="space-y-3">
                      {getPositionSpecificQuestions().map((question) => (
                        <div key={question.key} className="space-y-2">
                          <Label>{question.label} *</Label>
                          <Select 
                            value={(formData as any)[question.key] || ''} 
                            onValueChange={(value) => handleInputChange(question.key, value)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select answer" />
                            </SelectTrigger>
                            <SelectContent>
                              {question.options.map(option => (
                                <SelectItem key={option} value={option}>
                                  {option.charAt(0).toUpperCase() + option.slice(1)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Work Eligibility</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="work_authorized">Authorized to work in US? *</Label>
                    <Select value={formData.work_authorized} onValueChange={(value) => setFormData({...formData, work_authorized: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="yes">Yes</SelectItem>
                        <SelectItem value="no">No</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="sponsorship_required">Require sponsorship? *</Label>
                    <Select value={formData.sponsorship_required} onValueChange={(value) => setFormData({...formData, sponsorship_required: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="yes">Yes</SelectItem>
                        <SelectItem value="no">No</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Availability</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="start_date">Available Start Date *</Label>
                    <Input
                      id="start_date"
                      type="date"
                      value={formData.start_date}
                      onChange={(e) => handleInputChange('start_date', e.target.value)}
                      className={validationErrors.start_date ? 'border-red-500' : ''}
                      min={new Date().toISOString().split('T')[0]}
                      required
                    />
                    {validationErrors.start_date && (
                      <p className="text-sm text-red-600">{validationErrors.start_date}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="shift_preference">Shift Preference *</Label>
                    <Select value={formData.shift_preference} onValueChange={(value) => handleInputChange('shift_preference', value)}>
                      <SelectTrigger className={validationErrors.shift_preference ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select shift" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="morning">Morning (6 AM - 2 PM)</SelectItem>
                        <SelectItem value="afternoon">Afternoon (2 PM - 10 PM)</SelectItem>
                        <SelectItem value="evening">Evening (10 PM - 6 AM)</SelectItem>
                        <SelectItem value="night">Night (10 PM - 6 AM)</SelectItem>
                        <SelectItem value="flexible">Flexible</SelectItem>
                      </SelectContent>
                    </Select>
                    {validationErrors.shift_preference && (
                      <p className="text-sm text-red-600">{validationErrors.shift_preference}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="employment_type">Employment Type *</Label>
                    <Select value={formData.employment_type} onValueChange={(value) => handleInputChange('employment_type', value)}>
                      <SelectTrigger className={validationErrors.employment_type ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="full_time">Full-time</SelectItem>
                        <SelectItem value="part_time">Part-time</SelectItem>
                        <SelectItem value="temporary">Temporary</SelectItem>
                      </SelectContent>
                    </Select>
                    {validationErrors.employment_type && (
                      <p className="text-sm text-red-600">{validationErrors.employment_type}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="availability_weekends">Available Weekends? *</Label>
                    <Select value={formData.availability_weekends} onValueChange={(value) => handleInputChange('availability_weekends', value)}>
                      <SelectTrigger className={validationErrors.availability_weekends ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="yes">Yes</SelectItem>
                        <SelectItem value="no">No</SelectItem>
                        <SelectItem value="sometimes">Sometimes</SelectItem>
                      </SelectContent>
                    </Select>
                    {validationErrors.availability_weekends && (
                      <p className="text-sm text-red-600">{validationErrors.availability_weekends}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="availability_holidays">Available Holidays? *</Label>
                    <Select value={formData.availability_holidays} onValueChange={(value) => handleInputChange('availability_holidays', value)}>
                      <SelectTrigger className={validationErrors.availability_holidays ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="yes">Yes</SelectItem>
                        <SelectItem value="no">No</SelectItem>
                        <SelectItem value="sometimes">Sometimes</SelectItem>
                      </SelectContent>
                    </Select>
                    {validationErrors.availability_holidays && (
                      <p className="text-sm text-red-600">{validationErrors.availability_holidays}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reliable_transportation">Reliable Transportation? *</Label>
                    <Select value={formData.reliable_transportation} onValueChange={(value) => handleInputChange('reliable_transportation', value)}>
                      <SelectTrigger className={validationErrors.reliable_transportation ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="yes">Yes</SelectItem>
                        <SelectItem value="no">No</SelectItem>
                      </SelectContent>
                    </Select>
                    {validationErrors.reliable_transportation && (
                      <p className="text-sm text-red-600">{validationErrors.reliable_transportation}</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Experience</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="experience_years">Years of Experience *</Label>
                    <Select value={formData.experience_years} onValueChange={(value) => handleInputChange('experience_years', value)}>
                      <SelectTrigger className={validationErrors.experience_years ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select experience" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0-1">0-1 years</SelectItem>
                        <SelectItem value="2-5">2-5 years</SelectItem>
                        <SelectItem value="6-10">6-10 years</SelectItem>
                        <SelectItem value="10+">10+ years</SelectItem>
                      </SelectContent>
                    </Select>
                    {validationErrors.experience_years && (
                      <p className="text-sm text-red-600">{validationErrors.experience_years}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="hotel_experience">Previous Hotel Experience *</Label>
                    <Select value={formData.hotel_experience} onValueChange={(value) => handleInputChange('hotel_experience', value)}>
                      <SelectTrigger className={validationErrors.hotel_experience ? 'border-red-500' : ''}>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="yes">Yes</SelectItem>
                        <SelectItem value="no">No</SelectItem>
                      </SelectContent>
                    </Select>
                    {validationErrors.hotel_experience && (
                      <p className="text-sm text-red-600">{validationErrors.hotel_experience}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="previous_employer">Previous Employer (Optional)</Label>
                    <Input
                      id="previous_employer"
                      value={formData.previous_employer}
                      onChange={(e) => handleInputChange('previous_employer', e.target.value)}
                      placeholder="Company name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="reason_for_leaving">Reason for Leaving (Optional)</Label>
                    <Input
                      id="reason_for_leaving"
                      value={formData.reason_for_leaving}
                      onChange={(e) => handleInputChange('reason_for_leaving', e.target.value)}
                      placeholder="Brief reason"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="additional_comments">Additional Comments (Optional)</Label>
                  <Textarea
                    id="additional_comments"
                    value={formData.additional_comments}
                    onChange={(e) => handleInputChange('additional_comments', e.target.value)}
                    placeholder="Tell us anything else you'd like us to know about your application..."
                    rows={3}
                    maxLength={500}
                  />
                  <p className="text-sm text-gray-500">
                    {formData.additional_comments.length}/500 characters
                  </p>
                </div>
              </div>

              {/* Consent and Acknowledgments */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Acknowledgments & Consent</h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="physical_requirements_acknowledged"
                      checked={formData.physical_requirements_acknowledged}
                      onCheckedChange={(checked) => handleInputChange('physical_requirements_acknowledged', checked)}
                      className={validationErrors.physical_requirements_acknowledged ? 'border-red-500' : ''}
                    />
                    <div className="space-y-1">
                      <Label htmlFor="physical_requirements_acknowledged" className="text-sm font-normal cursor-pointer">
                        I acknowledge that this position may require physical demands including but not limited to: 
                        standing for extended periods, lifting up to 50 pounds, bending, and walking. *
                      </Label>
                      {validationErrors.physical_requirements_acknowledged && (
                        <p className="text-sm text-red-600">{validationErrors.physical_requirements_acknowledged}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="background_check_consent"
                      checked={formData.background_check_consent}
                      onCheckedChange={(checked) => handleInputChange('background_check_consent', checked)}
                      className={validationErrors.background_check_consent ? 'border-red-500' : ''}
                    />
                    <div className="space-y-1">
                      <Label htmlFor="background_check_consent" className="text-sm font-normal cursor-pointer">
                        I consent to a background check and understand that employment is contingent upon 
                        satisfactory results. I certify that all information provided is true and complete. *
                      </Label>
                      {validationErrors.background_check_consent && (
                        <p className="text-sm text-red-600">{validationErrors.background_check_consent}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4">
                <Button 
                  type="submit" 
                  className="w-full" 
                  disabled={loading || isDuplicateApplication || Object.keys(validationErrors).length > 0}
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Submitting Application...
                    </>
                  ) : (
                    'Submit Application'
                  )}
                </Button>
                
                {Object.keys(validationErrors).length > 0 && (
                  <div className="mt-3 p-3 bg-red-50 rounded-lg">
                    <p className="text-sm text-red-800 font-medium">
                      Please correct the following errors:
                    </p>
                    <ul className="mt-1 text-sm text-red-700 list-disc list-inside">
                      {Object.entries(validationErrors).slice(0, 3).map(([field, error]) => (
                        <li key={field}>{error}</li>
                      ))}
                      {Object.keys(validationErrors).length > 3 && (
                        <li>And {Object.keys(validationErrors).length - 3} more...</li>
                      )}
                    </ul>
                  </div>
                )}

                <p className="mt-3 text-xs text-gray-500 text-center">
                  By submitting this application, you agree to our terms and conditions. 
                  We will contact you within 3-5 business days regarding your application status.
                </p>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
