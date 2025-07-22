import React, { useState } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { RadioGroup, RadioGroupItem } from './ui/radio-group'
import SignaturePad from './SignaturePad'
import { useLanguage } from '../contexts/LanguageContext'

interface I9FormProps {
  onSubmit: (formData: any) => void
  ocrData?: any
}

export default function I9Form({ onSubmit, ocrData = {} }: I9FormProps) {
  const { t } = useLanguage()
  const [formData, setFormData] = useState({
    last_name: ocrData.last_name || '',
    first_name: ocrData.first_name || '',
    middle_initial: ocrData.middle_initial || '',
    other_last_names: ocrData.other_last_names || '',
    address: ocrData.address || '',
    apt_number: ocrData.apt_number || '',
    city: ocrData.city || '',
    state: ocrData.state || '',
    zip_code: ocrData.zip_code || '',
    date_of_birth: ocrData.date_of_birth || '',
    ssn: ocrData.ssn || '',
    email: ocrData.email || '',
    phone: ocrData.phone || '',
    citizenship_status: '',
    uscis_number: '',
    i94_number: '',
    passport_info: '',
    signature: '',
    signature_date: new Date().toISOString().split('T')[0]
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.signature || !formData.citizenship_status) {
      alert('Please complete all required fields including signature')
      return
    }
    onSubmit(formData)
  }

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-4xl mx-auto p-6">
      {/* Official I-9 Header */}
      <div className="bg-blue-50 p-4 rounded-lg border">
        <h2 className="font-bold text-xl text-center mb-2">
          Employment Eligibility Verification
        </h2>
        <h3 className="font-bold text-lg">{t('i9.section1.title')}</h3>
        <p className="text-sm text-gray-700 mt-2">
          {t('i9.section1.instructions')}
        </p>
      </div>

      {/* Personal Information */}
      <div className="space-y-4">
        <h4 className="font-semibold text-lg">Personal Information</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
        </div>

        <div>
          <Label htmlFor="other_last_names">Other Last Names Used (if any)</Label>
          <Input
            id="other_last_names"
            value={formData.other_last_names}
            onChange={(e) => updateField('other_last_names', e.target.value)}
            className="border-2"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
          <div>
            <Label htmlFor="apt_number">Apt. Number</Label>
            <Input
              id="apt_number"
              value={formData.apt_number}
              onChange={(e) => updateField('apt_number', e.target.value)}
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

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="date_of_birth">{t('form.dateOfBirth')} *</Label>
            <Input
              id="date_of_birth"
              type="date"
              value={formData.date_of_birth}
              onChange={(e) => updateField('date_of_birth', e.target.value)}
              required
              className="border-2"
            />
          </div>
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
            <Label htmlFor="email">{t('form.email')} *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => updateField('email', e.target.value)}
              required
              className="border-2"
            />
          </div>
        </div>

        <div>
          <Label htmlFor="phone">{t('form.phone')} *</Label>
          <Input
            id="phone"
            value={formData.phone}
            onChange={(e) => updateField('phone', e.target.value)}
            required
            className="border-2"
            placeholder="(XXX) XXX-XXXX"
          />
        </div>
      </div>

      {/* Citizenship Status */}
      <div className="space-y-4">
        <h4 className="font-semibold text-lg">Citizenship or Immigration Status *</h4>
        <p className="text-sm text-gray-600">
          I am aware that federal law provides for imprisonment and/or fines for false statements or the use of false documents in connection with the completion of this form. I attest, under penalty of perjury, that I am (check one of the following boxes):
        </p>
        
        <RadioGroup 
          value={formData.citizenship_status} 
          onValueChange={(value) => updateField('citizenship_status', value)}
          className="space-y-3"
        >
          <div className="flex items-start space-x-3 p-3 border rounded">
            <RadioGroupItem value="1" id="citizen" className="mt-1" />
            <Label htmlFor="citizen" className="text-sm leading-relaxed">
              <strong>1.</strong> {t('i9.citizenship.1')}
            </Label>
          </div>
          
          <div className="flex items-start space-x-3 p-3 border rounded">
            <RadioGroupItem value="2" id="noncitizen" className="mt-1" />
            <Label htmlFor="noncitizen" className="text-sm leading-relaxed">
              <strong>2.</strong> {t('i9.citizenship.2')}
            </Label>
          </div>
          
          <div className="flex items-start space-x-3 p-3 border rounded">
            <RadioGroupItem value="3" id="permanent" className="mt-1" />
            <div className="flex-1">
              <Label htmlFor="permanent" className="text-sm leading-relaxed">
                <strong>3.</strong> {t('i9.citizenship.3')} (Alien Registration Number/USCIS Number):
              </Label>
              <Input
                value={formData.uscis_number}
                onChange={(e) => updateField('uscis_number', e.target.value)}
                className="mt-2 border-2"
                placeholder="Enter USCIS Number"
                disabled={formData.citizenship_status !== '3'}
              />
            </div>
          </div>
          
          <div className="flex items-start space-x-3 p-3 border rounded">
            <RadioGroupItem value="4" id="authorized" className="mt-1" />
            <div className="flex-1">
              <Label htmlFor="authorized" className="text-sm leading-relaxed">
                <strong>4.</strong> {t('i9.citizenship.4')} until (expiration date, if applicable):
              </Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                <Input
                  value={formData.i94_number}
                  onChange={(e) => updateField('i94_number', e.target.value)}
                  className="border-2"
                  placeholder="I-94 Admission Number"
                  disabled={formData.citizenship_status !== '4'}
                />
                <Input
                  value={formData.passport_info}
                  onChange={(e) => updateField('passport_info', e.target.value)}
                  className="border-2"
                  placeholder="Foreign Passport Number and Country"
                  disabled={formData.citizenship_status !== '4'}
                />
              </div>
            </div>
          </div>
        </RadioGroup>
      </div>

      {/* Legal Attestation */}
      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
        <h4 className="font-semibold mb-2">Legal Attestation</h4>
        <p className="text-sm text-gray-700">
          I am aware that federal law provides for imprisonment and/or fines for false statements, 
          or the use of false documents, in connection with the completion of this form. I attest, 
          under penalty of perjury, that this information, including my selection of the box 
          attesting to my citizenship or immigration status, is true and correct.
        </p>
      </div>

      {/* Digital Signature */}
      <SignaturePad
        label={`${t('signature.sign')} - Employee's Signature`}
        onSignature={(sig) => updateField('signature', sig)}
        required={true}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="signature_date">Date (mm/dd/yyyy) *</Label>
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

      <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3">
        Complete I-9 Section 1
      </Button>
    </form>
  )
}
