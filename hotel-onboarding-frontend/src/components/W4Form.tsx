import React, { useState } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Checkbox } from './ui/checkbox'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import SignaturePad from './SignaturePad'
import { useLanguage } from '../contexts/LanguageContext'

interface W4FormProps {
  onSubmit: (formData: any) => void
  ocrData?: any
}

export default function W4Form({ onSubmit, ocrData = {} }: W4FormProps) {
  const { t } = useLanguage()
  const [formData, setFormData] = useState({
    first_name: ocrData.first_name || '',
    middle_initial: ocrData.middle_initial || '',
    last_name: ocrData.last_name || '',
    address: ocrData.address || '',
    city: ocrData.city || '',
    state: ocrData.state || '',
    zip_code: ocrData.zip_code || '',
    ssn: ocrData.ssn || '',
    filing_status: ocrData.filing_status || '',
    
    multiple_jobs_checkbox: false,
    spouse_works_checkbox: false,
    
    dependents_amount: 0,
    other_credits: 0,
    
    other_income: 0,
    deductions: 0,
    extra_withholding: 0,
    
    signature: '',
    signature_date: new Date().toISOString().split('T')[0]
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.signature || !formData.filing_status) {
      alert('Please complete all required fields including signature')
      return
    }
    onSubmit(formData)
  }

  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8 max-w-4xl mx-auto p-6">
      {/* Official W-4 Header */}
      <div className="bg-blue-50 p-4 rounded-lg border">
        <h2 className="font-bold text-xl text-center mb-2">
          Form W-4 (2025)
        </h2>
        <h3 className="font-bold text-lg text-center">
          Employee's Withholding Certificate
        </h3>
        <p className="text-sm text-gray-700 mt-2 text-center">
          Complete Form W-4 so that your employer can withhold the correct federal income tax from your pay.
        </p>
      </div>

      {/* Step 1: Personal Information */}
      <div className="space-y-4 border rounded-lg p-6">
        <h4 className="font-semibold text-lg bg-gray-100 p-2 rounded">
          {t('w4.step1.title')}
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="first_name">{t('form.firstName')} *</Label>
            <Input
              id="first_name"
              value={formData.first_name}
              onChange={(e) => updateField('first_name', e.target.value)}
              required
              className="border-2"
            />
          </div>
          <div>
            <Label htmlFor="middle_initial">{t('form.middleInitial')}</Label>
            <Input
              id="middle_initial"
              value={formData.middle_initial}
              onChange={(e) => updateField('middle_initial', e.target.value)}
              maxLength={1}
              className="border-2"
            />
          </div>
          <div>
            <Label htmlFor="last_name">{t('form.lastName')} *</Label>
            <Input
              id="last_name"
              value={formData.last_name}
              onChange={(e) => updateField('last_name', e.target.value)}
              required
              className="border-2"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <Label htmlFor="address">{t('form.address')} *</Label>
            <Input
              id="address"
              value={formData.address}
              onChange={(e) => updateField('address', e.target.value)}
              required
              className="border-2"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="city">{t('form.city')} *</Label>
            <Input
              id="city"
              value={formData.city}
              onChange={(e) => updateField('city', e.target.value)}
              required
              className="border-2"
            />
          </div>
          <div>
            <Label htmlFor="state">{t('form.state')} *</Label>
            <Input
              id="state"
              value={formData.state}
              onChange={(e) => updateField('state', e.target.value)}
              required
              className="border-2"
            />
          </div>
          <div>
            <Label htmlFor="zip_code">{t('form.zipCode')} *</Label>
            <Input
              id="zip_code"
              value={formData.zip_code}
              onChange={(e) => updateField('zip_code', e.target.value)}
              required
              className="border-2"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="ssn">{t('form.ssn')} *</Label>
            <Input
              id="ssn"
              value={formData.ssn}
              onChange={(e) => updateField('ssn', e.target.value)}
              required
              className="border-2"
              placeholder="XXX-XX-XXXX"
            />
          </div>
          <div>
            <Label htmlFor="filing_status">Filing Status *</Label>
            <Select value={formData.filing_status} onValueChange={(value) => updateField('filing_status', value)}>
              <SelectTrigger className="border-2">
                <SelectValue placeholder="Select filing status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Single">Single or Married filing separately</SelectItem>
                <SelectItem value="Married filing jointly">Married filing jointly or Qualifying surviving spouse</SelectItem>
                <SelectItem value="Head of household">Head of household (Check only if you're unmarried and pay more than half the costs of keeping up a home for yourself and a qualifying individual)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Step 2: Multiple Jobs or Spouse Works */}
      <div className="space-y-4 border rounded-lg p-6">
        <h4 className="font-semibold text-lg bg-gray-100 p-2 rounded">
          {t('w4.step2.title')}
        </h4>
        <p className="text-sm text-gray-600">
          Complete this step if you (1) hold more than one job at a time, or (2) are married filing jointly and your spouse also works. The correct amount of withholding depends on income earned from all of these jobs.
        </p>
        
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="multiple_jobs"
              checked={formData.multiple_jobs_checkbox}
              onCheckedChange={(checked) => updateField('multiple_jobs_checkbox', checked)}
            />
            <Label htmlFor="multiple_jobs" className="text-sm">
              I have multiple jobs or my spouse works
            </Label>
          </div>
          
          {formData.multiple_jobs_checkbox && (
            <div className="bg-yellow-50 p-4 rounded border border-yellow-200">
              <p className="text-sm text-gray-700">
                <strong>Note:</strong> If you have multiple jobs or your spouse works, you may need to use the online estimator at www.irs.gov/W4App or complete the Multiple Jobs Worksheet on page 3 of Form W-4 to determine the correct withholding amount.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Step 3: Claim Dependents */}
      <div className="space-y-4 border rounded-lg p-6">
        <h4 className="font-semibold text-lg bg-gray-100 p-2 rounded">
          {t('w4.step3.title')}
        </h4>
        <p className="text-sm text-gray-600">
          If your total income will be $200,000 or less ($400,000 or less if married filing jointly):
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="dependents_amount">
              Multiply number of qualifying children under age 17 by $2,000
            </Label>
            <Input
              id="dependents_amount"
              type="number"
              value={formData.dependents_amount}
              onChange={(e) => updateField('dependents_amount', parseFloat(e.target.value) || 0)}
              className="border-2"
              placeholder="$0"
              min="0"
              step="2000"
            />
          </div>
          <div>
            <Label htmlFor="other_credits">
              Multiply number of other dependents by $500
            </Label>
            <Input
              id="other_credits"
              type="number"
              value={formData.other_credits}
              onChange={(e) => updateField('other_credits', parseFloat(e.target.value) || 0)}
              className="border-2"
              placeholder="$0"
              min="0"
              step="500"
            />
          </div>
        </div>
      </div>

      {/* Step 4: Other Adjustments (Optional) */}
      <div className="space-y-4 border rounded-lg p-6">
        <h4 className="font-semibold text-lg bg-gray-100 p-2 rounded">
          {t('w4.step4.title')}
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="other_income">
              Other income (not from jobs)
            </Label>
            <Input
              id="other_income"
              type="number"
              value={formData.other_income}
              onChange={(e) => updateField('other_income', parseFloat(e.target.value) || 0)}
              className="border-2"
              placeholder="$0"
              min="0"
            />
          </div>
          <div>
            <Label htmlFor="deductions">
              Deductions (other than standard deduction)
            </Label>
            <Input
              id="deductions"
              type="number"
              value={formData.deductions}
              onChange={(e) => updateField('deductions', parseFloat(e.target.value) || 0)}
              className="border-2"
              placeholder="$0"
              min="0"
            />
          </div>
          <div>
            <Label htmlFor="extra_withholding">
              Extra withholding
            </Label>
            <Input
              id="extra_withholding"
              type="number"
              value={formData.extra_withholding}
              onChange={(e) => updateField('extra_withholding', parseFloat(e.target.value) || 0)}
              className="border-2"
              placeholder="$0"
              min="0"
            />
          </div>
        </div>
      </div>

      {/* Step 5: Sign Here */}
      <div className="space-y-4 border rounded-lg p-6">
        <h4 className="font-semibold text-lg bg-gray-100 p-2 rounded">
          {t('w4.step5.title')}
        </h4>
        
        <div className="bg-yellow-50 p-4 rounded border border-yellow-200">
          <p className="text-sm text-gray-700">
            Under penalties of perjury, I declare that this certificate, to the best of my knowledge and belief, is true, correct, and complete.
          </p>
        </div>

        <SignaturePad
          label={`${t('signature.sign')} - Employee's Signature`}
          onSignature={(sig) => updateField('signature', sig)}
          required={true}
        />

        <div>
          <Label htmlFor="signature_date">Date *</Label>
          <Input
            id="signature_date"
            type="date"
            value={formData.signature_date}
            onChange={(e) => updateField('signature_date', e.target.value)}
            required
            className="border-2"
          />
        </div>
      </div>

      <Button type="submit" className="w-full bg-green-600 hover:bg-green-700 text-white py-3">
        Complete W-4 Form
      </Button>
    </form>
  )
}
