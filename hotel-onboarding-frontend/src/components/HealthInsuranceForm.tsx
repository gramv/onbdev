import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  Shield, Users, DollarSign, Info, Plus, Trash2, 
  AlertCircle, CheckCircle, Calculator, GitCompare,
  Heart, Eye, Smile, ArrowRight, ChevronDown, ChevronUp, Calendar
} from 'lucide-react'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface Dependent {
  firstName: string
  lastName: string
  middleInitial: string
  relationship: string
  dateOfBirth: string
  ssn: string
  gender: 'M' | 'F' | ''
  coverageType: {
    medical: boolean
    dental: boolean
    vision: boolean
  }
}

interface HealthInsuranceData {
  // Medical Coverage
  medicalPlan: string
  medicalTier: string
  medicalCost: number
  medicalWaived: boolean
  
  // Additional Coverage
  dentalCoverage: boolean
  dentalEnrolled: boolean  // Add for backend compatibility
  dentalTier: string
  dentalCost: number
  dentalWaived: boolean
  
  visionCoverage: boolean
  visionEnrolled: boolean  // Add for backend compatibility
  visionTier: string
  visionCost: number
  visionWaived: boolean
  
  // Dependents
  dependents: Dependent[]
  hasStepchildren: boolean
  stepchildrenNames: string
  dependentsSupported: boolean
  irsDependentConfirmation: boolean
  section125Acknowledgment: boolean
  
  // Effective Date
  effectiveDate: string
  
  // Total costs
  totalBiweeklyCost: number
  totalMonthlyCost: number
  totalAnnualCost: number
  
  // Waiver
  isWaived: boolean
  waiveReason: string
  otherCoverageType: string
  otherCoverageDetails: string
}

interface HealthInsuranceFormProps {
  initialData?: Partial<HealthInsuranceData>
  personalInfo?: any
  language: 'en' | 'es'
  onSave: (data: HealthInsuranceData) => void
  onNext?: () => void
  onBack?: () => void
  onValidationChange?: (isValid: boolean) => void
}

// Medical plan options with enhanced details
const MEDICAL_PLANS = {
  'hra_6k': {
    name: 'UHC HRA $6K Plan',
    shortName: 'HRA $6K',
    description: 'High deductible plan with Health Reimbursement Account',
    deductible: 6000,
    outOfPocketMax: 12000,
    costs: {
      'employee': 59.91,
      'employee_spouse': 319.29,
      'employee_children': 264.10,
      'family': 390.25
    },
    features: ['$6,000 HRA contribution', 'Lower premiums', 'Preventive care covered 100%']
  },
  'hra_4k': {
    name: 'UHC HRA $4K Plan',
    shortName: 'HRA $4K',
    description: 'Mid-level deductible with Health Reimbursement Account',
    deductible: 4000,
    outOfPocketMax: 10000,
    costs: {
      'employee': 136.84,
      'employee_spouse': 396.21,
      'employee_children': 341.02,
      'family': 467.17
    },
    features: ['$4,000 HRA contribution', 'Balanced premiums', 'Lower out-of-pocket costs']
  },
  'hra_2k': {
    name: 'UHC HRA $2K Plan',
    shortName: 'HRA $2K',
    description: 'Low deductible plan with Health Reimbursement Account',
    deductible: 2000,
    outOfPocketMax: 8000,
    costs: {
      'employee': 213.76,
      'employee_spouse': 473.13,
      'employee_children': 417.95,
      'family': 544.09
    },
    features: ['$2,000 HRA contribution', 'Higher premiums', 'Lowest deductible']
  },
  'minimum_essential': {
    name: 'ACI Minimum Essential Coverage',
    shortName: 'MEC',
    description: 'Basic coverage meeting ACA requirements',
    deductible: 0,
    outOfPocketMax: 0,
    costs: {
      'employee': 7.77,
      'employee_spouse': 17.55,
      'employee_children': 19.03,
      'family': 27.61
    },
    features: ['Preventive care only', 'Lowest cost option', 'ACA compliant']
  },
  'indemnity': {
    name: 'ACI Indemnity Plan',
    shortName: 'Indemnity',
    description: 'Fixed benefit payments for covered services',
    deductible: 0,
    outOfPocketMax: 0,
    costs: {
      'employee': 19.61,
      'employee_spouse': 37.24,
      'employee_children': 31.45,
      'family': 49.12
    },
    features: ['Fixed cash benefits', 'No network restrictions', 'Supplements other coverage']
  },
  'minimum_indemnity': {
    name: 'MEC + Indemnity Bundle',
    shortName: 'MEC + Indemnity',
    description: 'Combined minimum essential and indemnity coverage',
    deductible: 0,
    outOfPocketMax: 0,
    costs: {
      'employee': 27.37,
      'employee_spouse': 54.79,
      'employee_children': 50.48,
      'family': 76.74
    },
    features: ['Preventive + cash benefits', 'Affordable comprehensive option', 'Best of both plans']
  }
}

const DENTAL_COSTS = {
  'employee': 13.45,
  'employee_spouse': 27.44,
  'employee_children': 31.13,
  'family': 45.63
}

const VISION_COSTS = {
  'employee': 3.04,
  'employee_spouse': 5.59,
  'employee_children': 5.86,
  'family': 8.78
}

const TIER_OPTIONS = [
  { value: 'employee', label: 'Employee Only', labelEs: 'Solo Empleado', icon: '👤' },
  { value: 'employee_spouse', label: 'Employee + Spouse', labelEs: 'Empleado + Cónyuge', icon: '👫' },
  { value: 'employee_children', label: 'Employee + Child(ren)', labelEs: 'Empleado + Hijo(s)', icon: '👨‍👧‍👦' },
  { value: 'family', label: 'Employee + Family', labelEs: 'Empleado + Familia', icon: '👨‍👩‍👧‍👦' }
]

const RELATIONSHIP_OPTIONS = [
  'Spouse', 'Child', 'Stepchild', 'Adopted Child', 'Domestic Partner', 'Other'
]

const WAIVER_REASONS = [
  { value: 'no_coverage_preference', label: 'My preference not to have coverage' },
  { value: 'spouse_coverage', label: 'Coverage under my spouse/partner plan' },
  { value: 'parent_coverage', label: 'Coverage under parent plan' },
  { value: 'medicare', label: 'Medicare coverage' },
  { value: 'medicaid', label: 'Medicaid coverage' },
  { value: 'tricare', label: 'TRICARE military coverage' },
  { value: 'other', label: 'Other coverage' }
]

export default function HealthInsuranceForm({
  initialData = {},
  personalInfo,
  language,
  onSave,
  onNext,
  onBack,
  onValidationChange
}: HealthInsuranceFormProps) {
  const [formData, setFormData] = useState<HealthInsuranceData>({
    medicalPlan: '',
    medicalTier: 'employee',
    medicalCost: 0,
    medicalWaived: false,
    dentalCoverage: false,
    dentalEnrolled: false,  // Same as dentalCoverage
    dentalTier: 'employee',
    dentalCost: 0,
    dentalWaived: false,
    visionCoverage: false,
    visionEnrolled: false,  // Same as visionCoverage
    visionTier: 'employee',
    visionCost: 0,
    visionWaived: false,
    dependents: [],
    hasStepchildren: false,
    stepchildrenNames: '',
    dependentsSupported: false,
    irsDependentConfirmation: false,
    section125Acknowledgment: false,
    effectiveDate: (() => {
      // Default to first of next month
      const today = new Date()
      const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1)
      return nextMonth.toISOString().split('T')[0]
    })(),
    totalBiweeklyCost: 0,
    totalMonthlyCost: 0,
    totalAnnualCost: 0,
    isWaived: false,
    waiveReason: '',
    otherCoverageType: '',
    otherCoverageDetails: '',
    ...initialData
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showDependentForm, setShowDependentForm] = useState(false)
  const [touchedFields, setTouchedFields] = useState<Record<string, boolean>>({})
  const [showErrors, setShowErrors] = useState(false)
  const [isValid, setIsValid] = useState(false)
  const [showPlanComparison, setShowPlanComparison] = useState(false)
  const [expandedPlan, setExpandedPlan] = useState<string | null>(null)
  const [showCostBreakdown, setShowCostBreakdown] = useState(false)

  // Enhanced translations
  const t = (key: string) => {
    const translations: Record<string, Record<string, string>> = {
      en: {
        'health_insurance': 'Health Insurance Benefits',
        'health_insurance_desc': 'Select your health coverage for 2025. Coverage begins the first of the month following your hire date.',
        'plan_year': 'Plan Year: January 1, 2025 – December 31, 2025',
        'medical_coverage': 'Medical Coverage',
        'select_plan': 'Select Medical Plan',
        'compare_plans': 'Compare Plans',
        'select_tier': 'Coverage Level',
        'biweekly_cost': 'Per Paycheck',
        'monthly_cost': 'Per Month',
        'annual_cost': 'Annual Cost',
        'additional_coverage': 'Additional Benefits',
        'dental_coverage': 'Dental Coverage',
        'vision_coverage': 'Vision Coverage',
        'dependents_info': 'Dependent Information',
        'add_dependent': 'Add Dependent',
        'dependent_required': 'Required for family coverage',
        'validation_error': 'Please correct the errors below',
        'cost_calculator': 'Cost Calculator',
        'total_coverage_cost': 'Total Coverage Cost',
        'employer_contribution': 'Employer Contribution',
        'your_cost': 'Your Cost',
        'plan_features': 'Plan Features',
        'deductible': 'Annual Deductible',
        'out_of_pocket_max': 'Out-of-Pocket Maximum',
        'section_125': 'Pre-Tax Benefits',
        'section_125_desc': 'I understand these premiums will be deducted pre-tax under Section 125',
        'special_enrollment': 'Special Enrollment Rights',
        'enrollment_notice': 'I understand I can only change coverage during open enrollment or qualifying life events',
        'save_continue': 'Save & Continue',
        'back': 'Back',
        'required_field': 'This field is required',
        'invalid_ssn': 'Please enter a valid SSN (XXX-XX-XXXX)',
        'invalid_date': 'Please enter a valid date',
        'dependent_validation': 'Please complete all dependent information',
        'confirm_waiver': 'Are you sure you want to decline all coverage?',
        'waiver_warning': 'You will not be able to enroll until the next open enrollment period unless you have a qualifying life event'
      },
      es: {
        'health_insurance': 'Beneficios de Seguro de Salud',
        'health_insurance_desc': 'Seleccione su cobertura de salud para 2025. La cobertura comienza el primero del mes siguiente a su fecha de contratación.',
        'plan_year': 'Año del Plan: 1 de enero de 2025 – 31 de diciembre de 2025',
        'medical_coverage': 'Cobertura Médica',
        'select_plan': 'Seleccionar Plan Médico',
        'compare_plans': 'Comparar Planes',
        'select_tier': 'Nivel de Cobertura',
        'biweekly_cost': 'Por Cheque',
        'monthly_cost': 'Por Mes',
        'annual_cost': 'Costo Anual',
        'additional_coverage': 'Beneficios Adicionales',
        'dental_coverage': 'Cobertura Dental',
        'vision_coverage': 'Cobertura de Visión',
        'dependents_info': 'Información de Dependientes',
        'add_dependent': 'Agregar Dependiente',
        'dependent_required': 'Requerido para cobertura familiar',
        'validation_error': 'Por favor corrija los errores a continuación',
        'cost_calculator': 'Calculadora de Costos',
        'save_continue': 'Guardar y Continuar',
        'back': 'Atrás'
      }
    }
    return translations[language][key] || translations['en'][key] || key
  }

  // Update form data when initialData changes
  useEffect(() => {
    if (initialData && Object.keys(initialData).length > 0) {
      setFormData(prevData => ({
        ...prevData,
        ...initialData,
        dependents: initialData.dependents?.map((dep: any) => ({
          ...dep,
          coverageType: dep.coverageType || {
            medical: true,
            dental: false,
            vision: false
          }
        })) || []
      }))
    }
  }, [initialData])

  // Enhanced cost calculation with monthly and annual projections
  useEffect(() => {
    calculateCosts()
  }, [
    formData.medicalPlan, 
    formData.medicalTier, 
    formData.dentalCoverage, 
    formData.dentalTier, 
    formData.visionCoverage, 
    formData.visionTier,
    formData.medicalWaived,
    formData.dentalWaived,
    formData.visionWaived
  ])

  // Enhanced validation
  useEffect(() => {
    validateForm()
  }, [
    formData.isWaived, 
    formData.medicalPlan, 
    formData.medicalWaived,
    formData.dependents, 
    formData.irsDependentConfirmation,
    formData.section125Acknowledgment,
    formData.waiveReason
  ])

  const calculateCosts = () => {
    let biweeklyCost = 0

    // Medical cost
    if (!formData.medicalWaived && formData.medicalPlan && MEDICAL_PLANS[formData.medicalPlan as keyof typeof MEDICAL_PLANS]) {
      const medicalCost = MEDICAL_PLANS[formData.medicalPlan as keyof typeof MEDICAL_PLANS].costs[formData.medicalTier as keyof typeof MEDICAL_PLANS['hra_6k']['costs']] || 0
      biweeklyCost += medicalCost
      setFormData(prev => ({ ...prev, medicalCost }))
    } else {
      setFormData(prev => ({ ...prev, medicalCost: 0 }))
    }

    // Dental cost
    if (!formData.dentalWaived && formData.dentalCoverage) {
      const dentalCost = DENTAL_COSTS[formData.dentalTier as keyof typeof DENTAL_COSTS] || 0
      biweeklyCost += dentalCost
      setFormData(prev => ({ ...prev, dentalCost }))
    } else {
      setFormData(prev => ({ ...prev, dentalCost: 0 }))
    }

    // Vision cost
    if (!formData.visionWaived && formData.visionCoverage) {
      const visionCost = VISION_COSTS[formData.visionTier as keyof typeof VISION_COSTS] || 0
      biweeklyCost += visionCost
      setFormData(prev => ({ ...prev, visionCost }))
    } else {
      setFormData(prev => ({ ...prev, visionCost: 0 }))
    }

    // Calculate monthly and annual costs
    const monthlyCost = biweeklyCost * 2.17 // Average bi-weekly periods per month
    const annualCost = biweeklyCost * 26 // 26 pay periods per year

    setFormData(prev => ({ 
      ...prev, 
      totalBiweeklyCost: biweeklyCost,
      totalMonthlyCost: monthlyCost,
      totalAnnualCost: annualCost
    }))
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    // Check if coverage is waived
    if (formData.isWaived) {
      if (!formData.waiveReason) {
        newErrors.waiveReason = t('required_field')
      }
      if (formData.waiveReason === 'other' && !formData.otherCoverageDetails) {
        newErrors.otherCoverageDetails = t('required_field')
      }
    } else {
      // Medical plan validation
      if (!formData.medicalWaived && !formData.medicalPlan) {
        newErrors.medicalPlan = t('required_field')
      }
      
      // Dependent validation
      if (requiresDependents()) {
        if (formData.dependents.length === 0) {
          newErrors.dependents = t('dependent_required')
        } else {
          // Validate each dependent
          formData.dependents.forEach((dep, index) => {
            if (!dep.firstName) newErrors[`dep_${index}_firstName`] = t('required_field')
            if (!dep.lastName) newErrors[`dep_${index}_lastName`] = t('required_field')
            if (!dep.relationship) newErrors[`dep_${index}_relationship`] = t('required_field')
            if (!dep.dateOfBirth) newErrors[`dep_${index}_dateOfBirth`] = t('required_field')
            if (!dep.ssn || !isValidSSN(dep.ssn)) newErrors[`dep_${index}_ssn`] = t('invalid_ssn')
            if (!dep.gender) newErrors[`dep_${index}_gender`] = t('required_field')
          })
        }
        
        // IRS confirmation required for dependents
        if (!formData.irsDependentConfirmation) {
          newErrors.irsDependentConfirmation = t('required_field')
        }
      }
      
      // Section 125 acknowledgment
      if (!formData.section125Acknowledgment) {
        newErrors.section125Acknowledgment = t('required_field')
      }
    }
    
    setErrors(newErrors)
    const formIsValid = Object.keys(newErrors).length === 0
    setIsValid(formIsValid)
    
    if (onValidationChange) {
      onValidationChange(formIsValid)
    }
    
    return formIsValid
  }

  const requiresDependents = () => {
    const needsForMedical = !formData.medicalWaived && (
      formData.medicalTier.includes('spouse') || 
      formData.medicalTier.includes('children') || 
      formData.medicalTier.includes('family')
    )
    
    const needsForDental = formData.dentalCoverage && !formData.dentalWaived && (
      formData.dentalTier.includes('spouse') || 
      formData.dentalTier.includes('children') || 
      formData.dentalTier.includes('family')
    )
    
    const needsForVision = formData.visionCoverage && !formData.visionWaived && (
      formData.visionTier.includes('spouse') || 
      formData.visionTier.includes('children') || 
      formData.visionTier.includes('family')
    )
    
    return needsForMedical || needsForDental || needsForVision
  }

  const isValidSSN = (ssn: string): boolean => {
    const ssnPattern = /^\d{3}-\d{2}-\d{4}$/
    return ssnPattern.test(ssn)
  }

  const formatSSN = (value: string): string => {
    const cleaned = value.replace(/\D/g, '')
    if (cleaned.length <= 3) return cleaned
    if (cleaned.length <= 5) return `${cleaned.slice(0, 3)}-${cleaned.slice(3)}`
    return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 5)}-${cleaned.slice(5, 9)}`
  }

  const handleFieldBlur = (field: string) => {
    setTouchedFields(prev => ({ ...prev, [field]: true }))
  }

  const shouldShowError = (field: string) => {
    return (showErrors || touchedFields[field]) && errors[field]
  }

  const addDependent = () => {
    const newDependent: Dependent = {
      firstName: '',
      lastName: '',
      middleInitial: '',
      relationship: '',
      dateOfBirth: '',
      ssn: '',
      gender: '',
      coverageType: {
        medical: true,
        dental: formData.dentalCoverage,
        vision: formData.visionCoverage
      }
    }
    setFormData(prev => ({
      ...prev,
      dependents: [...prev.dependents, newDependent]
    }))
    setShowDependentForm(true)
  }

  const removeDependent = (index: number) => {
    setFormData(prev => ({
      ...prev,
      dependents: prev.dependents.filter((_, i) => i !== index)
    }))
  }

  const updateDependent = (index: number, field: keyof Dependent | 'coverageType', value: any) => {
    setFormData(prev => ({
      ...prev,
      dependents: prev.dependents.map((dep, i) => {
        if (i !== index) return dep
        
        if (field === 'ssn' && typeof value === 'string') {
          return { ...dep, ssn: formatSSN(value) }
        }
        
        return { ...dep, [field]: value }
      })
    }))
    
    const fieldKey = `dep_${index}_${field}`
    setTouchedFields(prev => ({ ...prev, [fieldKey]: true }))
  }

  const handleSubmit = () => {
    setShowErrors(true)
    const isFormValid = validateForm()
    
    if (isFormValid) {
      onSave(formData)
      if (onNext) onNext()
    } else {
      // Scroll to first error
      const firstErrorField = document.querySelector('.error-field')
      firstErrorField?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }

  // Plan Comparison Component
  const PlanComparisonModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-auto">
        <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
          <h3 className="text-lg font-semibold flex items-center">
            <GitCompare className="h-5 w-5 mr-2" />
            {t('compare_plans')}
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowPlanComparison(false)}
          >
            ✕
          </Button>
        </div>
        
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(MEDICAL_PLANS).map(([key, plan]) => (
              <Card 
                key={key} 
                className={`cursor-pointer transition-all ${
                  formData.medicalPlan === key ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => {
                  setFormData(prev => ({ ...prev, medicalPlan: key, medicalWaived: false }))
                  setShowPlanComparison(false)
                }}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">{plan.shortName}</CardTitle>
                  <CardDescription className="text-xs">{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">{t('deductible')}</span>
                      <span className="font-medium">
                        {plan.deductible > 0 ? `$${plan.deductible.toLocaleString()}` : 'N/A'}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">{t('out_of_pocket_max')}</span>
                      <span className="font-medium">
                        {plan.outOfPocketMax > 0 ? `$${plan.outOfPocketMax.toLocaleString()}` : 'N/A'}
                      </span>
                    </div>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-gray-700">{t('plan_features')}:</p>
                    {plan.features.map((feature, idx) => (
                      <div key={idx} className="flex items-start text-xs">
                        <CheckCircle className="h-3 w-3 mr-1 mt-0.5 text-green-500 flex-shrink-0" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-gray-700">{t('biweekly_cost')}:</p>
                    <div className="grid grid-cols-2 gap-1 text-xs">
                      {TIER_OPTIONS.map(tier => (
                        <div key={tier.value} className="flex justify-between">
                          <span className="text-gray-600">{tier.icon}</span>
                          <span className="font-medium">
                            ${plan.costs[tier.value as keyof typeof plan.costs]}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {formData.medicalPlan === key && (
                    <Badge className="w-full justify-center">Selected</Badge>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  )

  // Cost Breakdown Component
  const CostBreakdownCard = () => (
    <Card className="bg-gradient-to-br from-blue-50 to-green-50">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-base">
          <span className="flex items-center">
            <Calculator className="h-4 w-4 mr-2" />
            {t('cost_calculator')}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowCostBreakdown(!showCostBreakdown)}
          >
            {showCostBreakdown ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </CardTitle>
      </CardHeader>
      
      {showCostBreakdown && (
        <CardContent className="space-y-3">
          <div className="space-y-2">
            {formData.medicalCost > 0 && (
              <div className="flex justify-between items-center text-sm">
                <span className="flex items-center">
                  <Heart className="h-3 w-3 mr-1 text-red-500" />
                  Medical ({MEDICAL_PLANS[formData.medicalPlan as keyof typeof MEDICAL_PLANS]?.shortName})
                </span>
                <span className="font-medium">${formData.medicalCost.toFixed(2)}</span>
              </div>
            )}
            
            {formData.dentalCost > 0 && (
              <div className="flex justify-between items-center text-sm">
                <span className="flex items-center">
                  <Smile className="h-3 w-3 mr-1 text-blue-500" />
                  Dental
                </span>
                <span className="font-medium">${formData.dentalCost.toFixed(2)}</span>
              </div>
            )}
            
            {formData.visionCost > 0 && (
              <div className="flex justify-between items-center text-sm">
                <span className="flex items-center">
                  <Eye className="h-3 w-3 mr-1 text-green-500" />
                  Vision
                </span>
                <span className="font-medium">${formData.visionCost.toFixed(2)}</span>
              </div>
            )}
          </div>
          
          <Separator />
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">{t('biweekly_cost')}</span>
              <span className="text-lg font-bold text-green-600">
                ${formData.totalBiweeklyCost.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center text-sm text-gray-600">
              <span>{t('monthly_cost')}</span>
              <span>${formData.totalMonthlyCost.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center text-sm text-gray-600">
              <span>{t('annual_cost')}</span>
              <span>${formData.totalAnnualCost.toFixed(2)}</span>
            </div>
          </div>
          
          {formData.section125Acknowledgment && (
            <Alert className="bg-green-50 border-green-200">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-xs text-green-800">
                Pre-tax deductions will save approximately ${(formData.totalAnnualCost * 0.25).toFixed(0)} annually in taxes
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      )}
    </Card>
  )

  // Waiver View
  if (formData.isWaived) {
    return (
      <div className="space-y-6">
        <div className="text-center mb-6">
          <Shield className="h-12 w-12 text-orange-500 mx-auto mb-3" />
          <h2 className="text-2xl font-bold text-gray-900">{t('health_insurance')}</h2>
          <p className="text-gray-600 mt-2">Coverage Waiver</p>
        </div>

        <Alert className="bg-orange-50 border-orange-200">
          <AlertCircle className="h-4 w-4 text-orange-600" />
          <AlertTitle className="text-orange-900">Important Notice</AlertTitle>
          <AlertDescription className="text-orange-800">
            {t('waiver_warning')}
          </AlertDescription>
        </Alert>

        <Card>
          <CardHeader>
            <CardTitle className="text-orange-600">Coverage Waiver</CardTitle>
            <CardDescription>
              Please indicate your reason for declining coverage
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Reason for declining coverage *</Label>
              <RadioGroup 
                value={formData.waiveReason} 
                onValueChange={(value) => setFormData(prev => ({ ...prev, waiveReason: value }))}
              >
                {WAIVER_REASONS.map(reason => (
                  <div key={reason.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={reason.value} id={reason.value} />
                    <Label htmlFor={reason.value} className="font-normal">
                      {reason.label}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
              {shouldShowError('waiveReason') && (
                <p className="text-xs text-red-500 mt-1">{errors.waiveReason}</p>
              )}
            </div>

            {formData.waiveReason === 'other' && (
              <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <Label>Please specify other coverage details *</Label>
                  <Input
                    value={formData.otherCoverageDetails}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      otherCoverageDetails: e.target.value 
                    }))}
                    onBlur={() => handleFieldBlur('otherCoverageDetails')}
                    placeholder="e.g., Individual policy through Blue Cross"
                    className={shouldShowError('otherCoverageDetails') ? 'error-field border-red-500' : ''}
                  />
                  {shouldShowError('otherCoverageDetails') && (
                    <p className="text-xs text-red-500 mt-1">{errors.otherCoverageDetails}</p>
                  )}
                </div>
              </div>
            )}

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                {t('special_enrollment')}
              </AlertDescription>
            </Alert>

            <Button 
              variant="outline" 
              onClick={() => setFormData(prev => ({ 
                ...prev, 
                isWaived: false,
                waiveReason: '',
                otherCoverageDetails: ''
              }))}
              className="w-full"
            >
              <ArrowRight className="h-4 w-4 mr-2" />
              Change Decision - Select Coverage
            </Button>
          </CardContent>
        </Card>

        <div className="flex justify-between items-center pt-6">
          <Button variant="outline" onClick={onBack}>
            {t('back')}
          </Button>
          <Button onClick={handleSubmit} className="px-8">
            {t('save_continue')}
          </Button>
        </div>
      </div>
    )
  }

  // Main Form View
  return (
    <div className="space-y-4">
      {showPlanComparison && <PlanComparisonModal />}
      
      <div className="text-center mb-4">
        <Shield className="h-8 w-8 text-blue-600 mx-auto mb-2" />
        <h2 className="text-xl font-bold text-gray-900">{t('health_insurance')}</h2>
        <p className="text-gray-600 text-sm mt-1">{t('health_insurance_desc')}</p>
        <Badge variant="outline" className="mt-1 text-xs">{t('plan_year')}</Badge>
      </div>

      {/* Employee Information Display (from PersonalInfoStep) */}
      {personalInfo && (
        <Card className="bg-gray-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center">
              <Users className="h-4 w-4 mr-2" />
              Employee Information
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div>
              <p className="text-xs text-gray-500">Name</p>
              <p className="font-medium">{personalInfo.firstName} {personalInfo.lastName}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">SSN</p>
              <p className="font-medium">***-**-{personalInfo.ssn?.slice(-4) || '****'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Date of Birth</p>
              <p className="font-medium">{personalInfo.dateOfBirth || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Email</p>
              <p className="font-medium truncate">{personalInfo.email || 'N/A'}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Validation Errors Summary */}
      {showErrors && Object.keys(errors).length > 0 && (
        <Alert className="bg-red-50 border-red-200">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertTitle className="text-red-900">{t('validation_error')}</AlertTitle>
          <AlertDescription className="text-red-800 text-sm">
            Please review and correct the highlighted fields below.
          </AlertDescription>
        </Alert>
      )}

      {/* Medical Coverage Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center justify-between text-lg">
            <span className="flex items-center">
              <Heart className="h-4 w-4 mr-2 text-red-500" />
              {t('medical_coverage')}
            </span>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowPlanComparison(true)}
              >
                <GitCompare className="h-3 w-3 mr-1" />
                {t('compare_plans')}
              </Button>
              <label className="flex items-center space-x-2 text-sm">
                <Checkbox
                  checked={formData.medicalWaived}
                  onCheckedChange={(checked) => setFormData(prev => ({ 
                    ...prev, 
                    medicalWaived: !!checked,
                    medicalPlan: checked ? '' : prev.medicalPlan
                  }))}
                />
                <span>Waive</span>
              </label>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <Label className="text-sm">
                {t('select_plan')} {!formData.medicalWaived && '*'}
              </Label>
              <Select 
                value={formData.medicalPlan} 
                onValueChange={(value) => setFormData(prev => ({ 
                  ...prev, 
                  medicalPlan: value,
                  medicalWaived: false
                }))}
                disabled={formData.medicalWaived}
              >
                <SelectTrigger 
                  className={`h-9 ${shouldShowError('medicalPlan') ? 'error-field border-red-500' : ''}`}
                >
                  <SelectValue placeholder="Choose a medical plan" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(MEDICAL_PLANS).map(([key, plan]) => (
                    <SelectItem key={key} value={key}>
                      <div className="flex justify-between items-center w-full">
                        <span className="text-sm">{plan.name}</span>
                        <Badge variant="outline" className="ml-2 text-xs">
                          ${plan.costs.employee}/pay
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {shouldShowError('medicalPlan') && (
                <p className="text-xs text-red-500 mt-1">{errors.medicalPlan}</p>
              )}
            </div>
            
            <div>
              <Label className="text-sm">{t('select_tier')}</Label>
              <Select 
                value={formData.medicalTier} 
                onValueChange={(value) => setFormData(prev => ({ ...prev, medicalTier: value }))}
                disabled={formData.medicalWaived || !formData.medicalPlan}
              >
                <SelectTrigger className="h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIER_OPTIONS.map(tier => (
                    <SelectItem key={tier.value} value={tier.value}>
                      <div className="flex items-center justify-between w-full">
                        <span className="flex items-center text-sm">
                          <span className="mr-2">{tier.icon}</span>
                          {language === 'es' ? tier.labelEs : tier.label}
                        </span>
                        {formData.medicalPlan && (
                          <Badge variant="outline" className="ml-2 text-xs">
                            ${MEDICAL_PLANS[formData.medicalPlan as keyof typeof MEDICAL_PLANS]?.costs[tier.value as keyof typeof MEDICAL_PLANS['hra_6k']['costs']] || 0}/pay
                          </Badge>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Plan Details Expansion */}
          {formData.medicalPlan && !formData.medicalWaived && (
            <Alert className="bg-blue-50 border-blue-200">
              <Info className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-xs">
                <strong>{MEDICAL_PLANS[formData.medicalPlan as keyof typeof MEDICAL_PLANS].name}</strong>
                <ul className="mt-1 ml-4 list-disc">
                  {MEDICAL_PLANS[formData.medicalPlan as keyof typeof MEDICAL_PLANS].features.map((feature, idx) => (
                    <li key={idx}>{feature}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Additional Coverage Section */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">{t('additional_coverage')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Dental Coverage */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Smile className="h-5 w-5 text-blue-500" />
              <div>
                <Label className="text-sm font-medium">{t('dental_coverage')}</Label>
                <p className="text-xs text-gray-600">Preventive, basic, and major services</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Select
                value={formData.dentalTier}
                onValueChange={(value) => setFormData(prev => ({ ...prev, dentalTier: value }))}
                disabled={!formData.dentalCoverage || formData.dentalWaived}
              >
                <SelectTrigger className="h-8 w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIER_OPTIONS.map(tier => (
                    <SelectItem key={tier.value} value={tier.value}>
                      <span className="text-xs">{tier.icon} ${DENTAL_COSTS[tier.value as keyof typeof DENTAL_COSTS]}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="flex items-center space-x-2">
                <label className="flex items-center space-x-1">
                  <Checkbox
                    checked={formData.dentalCoverage}
                    onCheckedChange={(checked) => setFormData(prev => ({ 
                      ...prev, 
                      dentalCoverage: !!checked,
                      dentalEnrolled: !!checked,  // Keep both in sync
                      dentalWaived: false
                    }))}
                    disabled={formData.dentalWaived}
                  />
                  <span className="text-sm">Enroll</span>
                </label>
                <label className="flex items-center space-x-1">
                  <Checkbox
                    checked={formData.dentalWaived}
                    onCheckedChange={(checked) => setFormData(prev => ({ 
                      ...prev, 
                      dentalWaived: !!checked,
                      dentalCoverage: false,
                      dentalEnrolled: false  // Keep both in sync
                    }))}
                  />
                  <span className="text-sm">Waive</span>
                </label>
              </div>
            </div>
          </div>

          {/* Vision Coverage */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Eye className="h-5 w-5 text-green-500" />
              <div>
                <Label className="text-sm font-medium">{t('vision_coverage')}</Label>
                <p className="text-xs text-gray-600">Eye exams, frames, and lenses</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Select
                value={formData.visionTier}
                onValueChange={(value) => setFormData(prev => ({ ...prev, visionTier: value }))}
                disabled={!formData.visionCoverage || formData.visionWaived}
              >
                <SelectTrigger className="h-8 w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {TIER_OPTIONS.map(tier => (
                    <SelectItem key={tier.value} value={tier.value}>
                      <span className="text-xs">{tier.icon} ${VISION_COSTS[tier.value as keyof typeof VISION_COSTS]}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="flex items-center space-x-2">
                <label className="flex items-center space-x-1">
                  <Checkbox
                    checked={formData.visionCoverage}
                    onCheckedChange={(checked) => setFormData(prev => ({ 
                      ...prev, 
                      visionCoverage: !!checked,
                      visionEnrolled: !!checked,  // Keep both in sync
                      visionWaived: false
                    }))}
                    disabled={formData.visionWaived}
                  />
                  <span className="text-sm">Enroll</span>
                </label>
                <label className="flex items-center space-x-1">
                  <Checkbox
                    checked={formData.visionWaived}
                    onCheckedChange={(checked) => setFormData(prev => ({ 
                      ...prev, 
                      visionWaived: !!checked,
                      visionCoverage: false,
                      visionEnrolled: false  // Keep both in sync
                    }))}
                  />
                  <span className="text-sm">Waive</span>
                </label>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dependent Information Section */}
      {requiresDependents() && (
        <Card className={errors.dependents ? 'border-red-500' : ''}>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between text-lg">
              <span className="flex items-center">
                <Users className="h-4 w-4 mr-2" />
                {t('dependents_info')} *
              </span>
              {errors.dependents && (
                <Badge variant="destructive" className="text-xs">
                  {errors.dependents}
                </Badge>
              )}
            </CardTitle>
            <CardDescription className="text-xs">
              {t('dependent_required')}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {formData.dependents.map((dependent, index) => (
              <div key={index} className="p-3 border rounded-lg space-y-3 bg-gray-50">
                <div className="flex justify-between items-center">
                  <h4 className="font-medium text-sm">Dependent {index + 1}</h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeDependent(index)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div>
                    <Label className="text-xs">First Name *</Label>
                    <Input
                      value={dependent.firstName}
                      onChange={(e) => updateDependent(index, 'firstName', e.target.value)}
                      onBlur={() => handleFieldBlur(`dep_${index}_firstName`)}
                      className={`h-8 ${shouldShowError(`dep_${index}_firstName`) ? 'error-field border-red-500' : ''}`}
                    />
                    {shouldShowError(`dep_${index}_firstName`) && (
                      <p className="text-xs text-red-500 mt-1">{errors[`dep_${index}_firstName`]}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label className="text-xs">Last Name *</Label>
                    <Input
                      value={dependent.lastName}
                      onChange={(e) => updateDependent(index, 'lastName', e.target.value)}
                      onBlur={() => handleFieldBlur(`dep_${index}_lastName`)}
                      className={`h-8 ${shouldShowError(`dep_${index}_lastName`) ? 'error-field border-red-500' : ''}`}
                    />
                    {shouldShowError(`dep_${index}_lastName`) && (
                      <p className="text-xs text-red-500 mt-1">{errors[`dep_${index}_lastName`]}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label className="text-xs">MI</Label>
                    <Input
                      value={dependent.middleInitial}
                      onChange={(e) => updateDependent(index, 'middleInitial', e.target.value.slice(0, 1).toUpperCase())}
                      maxLength={1}
                      className="h-8"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <div>
                    <Label className="text-xs">Relationship *</Label>
                    <Select 
                      value={dependent.relationship} 
                      onValueChange={(value) => updateDependent(index, 'relationship', value)}
                    >
                      <SelectTrigger className={`h-8 ${shouldShowError(`dep_${index}_relationship`) ? 'error-field border-red-500' : ''}`}>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        {RELATIONSHIP_OPTIONS.map(rel => (
                          <SelectItem key={rel} value={rel}>{rel}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {shouldShowError(`dep_${index}_relationship`) && (
                      <p className="text-xs text-red-500 mt-1">{errors[`dep_${index}_relationship`]}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label className="text-xs">Date of Birth *</Label>
                    <Input
                      type="date"
                      value={dependent.dateOfBirth}
                      onChange={(e) => updateDependent(index, 'dateOfBirth', e.target.value)}
                      onBlur={() => handleFieldBlur(`dep_${index}_dateOfBirth`)}
                      className={`h-8 ${shouldShowError(`dep_${index}_dateOfBirth`) ? 'error-field border-red-500' : ''}`}
                    />
                    {shouldShowError(`dep_${index}_dateOfBirth`) && (
                      <p className="text-xs text-red-500 mt-1">{errors[`dep_${index}_dateOfBirth`]}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label className="text-xs">Gender *</Label>
                    <Select 
                      value={dependent.gender} 
                      onValueChange={(value) => updateDependent(index, 'gender', value as 'M' | 'F')}
                    >
                      <SelectTrigger className={`h-8 ${shouldShowError(`dep_${index}_gender`) ? 'error-field border-red-500' : ''}`}>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="M">Male</SelectItem>
                        <SelectItem value="F">Female</SelectItem>
                      </SelectContent>
                    </Select>
                    {shouldShowError(`dep_${index}_gender`) && (
                      <p className="text-xs text-red-500 mt-1">{errors[`dep_${index}_gender`]}</p>
                    )}
                  </div>
                </div>
                
                {/* Coverage Type Selection for this Dependent */}
                <div className="space-y-2 p-2 bg-blue-50 rounded">
                  <Label className="text-xs font-medium">Coverage for this Dependent</Label>
                  <div className="flex gap-4">
                    {!formData.medicalWaived && (
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id={`dep-${index}-medical`}
                          checked={dependent.coverageType?.medical || false}
                          onCheckedChange={(checked) => {
                            updateDependent(index, 'coverageType', {
                              ...dependent.coverageType,
                              medical: checked as boolean
                            })
                          }}
                        />
                        <Label htmlFor={`dep-${index}-medical`} className="text-xs">
                          Medical
                        </Label>
                      </div>
                    )}
                    
                    {formData.dentalCoverage && !formData.dentalWaived && (
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id={`dep-${index}-dental`}
                          checked={dependent.coverageType?.dental || false}
                          onCheckedChange={(checked) => {
                            updateDependent(index, 'coverageType', {
                              ...dependent.coverageType,
                              dental: checked as boolean
                            })
                          }}
                        />
                        <Label htmlFor={`dep-${index}-dental`} className="text-xs">
                          Dental
                        </Label>
                      </div>
                    )}
                    
                    {formData.visionCoverage && !formData.visionWaived && (
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id={`dep-${index}-vision`}
                          checked={dependent.coverageType?.vision || false}
                          onCheckedChange={(checked) => {
                            updateDependent(index, 'coverageType', {
                              ...dependent.coverageType,
                              vision: checked as boolean
                            })
                          }}
                        />
                        <Label htmlFor={`dep-${index}-vision`} className="text-xs">
                          Vision
                        </Label>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <Label className="text-xs">SSN * (XXX-XX-XXXX)</Label>
                  <Input
                    value={dependent.ssn}
                    onChange={(e) => updateDependent(index, 'ssn', e.target.value)}
                    onBlur={() => handleFieldBlur(`dep_${index}_ssn`)}
                    placeholder="123-45-6789"
                    maxLength={11}
                    className={`h-8 ${shouldShowError(`dep_${index}_ssn`) ? 'error-field border-red-500' : ''}`}
                  />
                  {shouldShowError(`dep_${index}_ssn`) && (
                    <p className="text-xs text-red-500 mt-1">{errors[`dep_${index}_ssn`]}</p>
                  )}
                </div>
                
                <div>
                  <Label className="text-xs">Coverage Type</Label>
                  <div className="flex space-x-4 mt-1">
                    <label className="flex items-center space-x-1">
                      <Checkbox
                        checked={dependent.coverageType?.medical ?? true}
                        onCheckedChange={(checked) => updateDependent(index, 'coverageType', {
                          ...dependent.coverageType,
                          medical: !!checked
                        })}
                      />
                      <span className="text-xs">Medical</span>
                    </label>
                    <label className="flex items-center space-x-1">
                      <Checkbox
                        checked={dependent.coverageType?.dental ?? false}
                        onCheckedChange={(checked) => updateDependent(index, 'coverageType', {
                          ...dependent.coverageType,
                          dental: !!checked
                        })}
                        disabled={!formData.dentalCoverage}
                      />
                      <span className="text-xs">Dental</span>
                    </label>
                    <label className="flex items-center space-x-1">
                      <Checkbox
                        checked={dependent.coverageType?.vision ?? false}
                        onCheckedChange={(checked) => updateDependent(index, 'coverageType', {
                          ...dependent.coverageType,
                          vision: !!checked
                        })}
                        disabled={!formData.visionCoverage}
                      />
                      <span className="text-xs">Vision</span>
                    </label>
                  </div>
                </div>
              </div>
            ))}
            
            <Button 
              variant="outline" 
              onClick={addDependent} 
              size="sm" 
              className="w-full"
            >
              <Plus className="h-3 w-3 mr-1" />
              {t('add_dependent')}
            </Button>
            
            {/* Step Children Question */}
            {formData.dependents.some(d => d.relationship === 'Stepchild') && (
              <div className="space-y-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <div>
                  <Label className="text-sm">Do stepchildren meet IRS dependency requirements?</Label>
                  <RadioGroup
                    value={formData.hasStepchildren ? 'yes' : 'no'}
                    onValueChange={(value) => setFormData(prev => ({ 
                      ...prev, 
                      hasStepchildren: value === 'yes' 
                    }))}
                  >
                    <div className="flex space-x-4 mt-2">
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="yes" id="step-yes" />
                        <Label htmlFor="step-yes">Yes</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="no" id="step-no" />
                        <Label htmlFor="step-no">No</Label>
                      </div>
                    </div>
                  </RadioGroup>
                </div>
                
                {formData.hasStepchildren && (
                  <div>
                    <Label className="text-xs">Please list stepchildren names:</Label>
                    <Input
                      value={formData.stepchildrenNames}
                      onChange={(e) => setFormData(prev => ({ 
                        ...prev, 
                        stepchildrenNames: e.target.value 
                      }))}
                      placeholder="Enter names separated by commas"
                      className="h-8"
                    />
                  </div>
                )}
              </div>
            )}
            
            {/* IRS Confirmation */}
            <Alert className={errors.irsDependentConfirmation ? 'border-red-500' : ''}>
              <Info className="h-4 w-4" />
              <AlertDescription className="text-xs">
                <label className="flex items-start space-x-2">
                  <Checkbox
                    checked={formData.irsDependentConfirmation}
                    onCheckedChange={(checked) => setFormData(prev => ({ 
                      ...prev, 
                      irsDependentConfirmation: !!checked 
                    }))}
                    className="mt-0.5"
                  />
                  <span>
                    I affirm that all dependents listed meet the IRS Section 152 definition of 
                    "dependent" so that premiums can be paid with pre-tax dollars, if applicable. *
                  </span>
                </label>
                {shouldShowError('irsDependentConfirmation') && (
                  <p className="text-xs text-red-500 mt-1">{errors.irsDependentConfirmation}</p>
                )}
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Cost Summary */}
      <CostBreakdownCard />

      {/* Effective Date */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Coverage Effective Date
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="effective-date" className="text-sm">
              When should your coverage begin? *
            </Label>
            <Input
              id="effective-date"
              type="date"
              value={formData.effectiveDate || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, effectiveDate: e.target.value }))}
              min={new Date().toISOString().split('T')[0]}
              className="w-full md:w-auto"
            />
            <p className="text-xs text-gray-600">
              Coverage typically begins on the first of the month following your hire date
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Section 125 Acknowledgment */}
      <Card className={errors.section125Acknowledgment ? 'border-red-500' : ''}>
        <CardContent className="pt-4">
          <label className="flex items-start space-x-2">
            <Checkbox
              checked={formData.section125Acknowledgment}
              onCheckedChange={(checked) => setFormData(prev => ({ 
                ...prev, 
                section125Acknowledgment: !!checked 
              }))}
              className="mt-0.5"
            />
            <div>
              <p className="text-sm font-medium">{t('section_125')} *</p>
              <p className="text-xs text-gray-600 mt-1">
                {t('section_125_desc')}
              </p>
            </div>
          </label>
          {shouldShowError('section125Acknowledgment') && (
            <p className="text-xs text-red-500 mt-1">{errors.section125Acknowledgment}</p>
          )}
        </CardContent>
      </Card>

      {/* Enrollment Notice */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle className="text-sm">{t('special_enrollment')}</AlertTitle>
        <AlertDescription className="text-xs">
          {t('enrollment_notice')}
        </AlertDescription>
      </Alert>

      {/* Waive All Coverage Option */}
      <Card className="border-orange-200 bg-orange-50">
        <CardContent className="pt-4">
          <label className="flex items-center space-x-2">
            <Checkbox
              checked={formData.isWaived}
              onCheckedChange={(checked) => {
                if (checked && !confirm(t('confirm_waiver'))) {
                  return
                }
                setFormData(prev => ({ 
                  ...prev, 
                  isWaived: !!checked,
                  medicalWaived: false,
                  dentalWaived: false,
                  visionWaived: false
                }))
              }}
            />
            <span className="text-sm font-medium">
              I wish to decline ALL health insurance coverage
            </span>
          </label>
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center pt-6">
        <Button variant="outline" onClick={onBack}>
          {t('back')}
        </Button>
        <Button 
          onClick={handleSubmit} 
          className="px-8"
          disabled={showErrors && !isValid}
        >
          {t('save_continue')}
        </Button>
      </div>
    </div>
  )
}