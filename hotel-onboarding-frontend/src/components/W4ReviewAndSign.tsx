import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { FileText, DollarSign, FileCheck, Calculator, Users, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import DigitalSignatureCapture from './DigitalSignatureCapture';
import OfficialW4Display from './OfficialW4Display';

interface W4ReviewData {
  w4FormData: any;
  reviewAcknowledgments: boolean[];
  finalSignature?: string;
  reviewCompletedAt?: string;
  review_acknowledgments_completed: boolean;
  final_signature: string;
}

interface W4ReviewAndSignProps {
  w4FormData: any;
  language: 'en' | 'es';
  onComplete: (data: W4ReviewData) => void;
  onBack: () => void;
}

export default function W4ReviewAndSign({
  w4FormData,
  language,
  onComplete,
  onBack
}: W4ReviewAndSignProps) {
  const [currentStep, setCurrentStep] = useState<'review' | 'official_form' | 'signature'>('review');
  const [reviewAcknowledgments, setReviewAcknowledgments] = useState<boolean[]>([false, false, false, false]);

  const t = (key: string) => {
    const translations: Record<string, Record<string, string>> = {
      en: {
        'w4_review_title': 'Review & Sign Form W-4',
        'w4_review_subtitle': 'Employee\'s Withholding Certificate - Review Required',
        'w4_review_desc': 'Please carefully review your tax withholding information before signing. This information determines how much federal income tax will be withheld from your pay.',
        'step_1_title': 'Step 1: Review Your Information',
        'step_2_title': 'Step 2: View Official Form',
        'step_3_title': 'Step 3: Digital Signature',
        'personal_info': 'Personal Information',
        'filing_status': 'Filing Status and Dependents',
        'additional_info': 'Additional Income and Deductions',
        'withholding_summary': 'Withholding Summary',
        'review_acknowledgments': 'Required Review Acknowledgments',
        'acknowledge_1': 'I have carefully reviewed all information provided in Form W-4 and certify that it is complete and accurate to the best of my knowledge, under penalties of perjury.',
        'acknowledge_2': 'I understand that this certificate is subject to review by the IRS and that I may be required to provide additional documentation. False statements may result in criminal prosecution under 26 USC 7206.',
        'acknowledge_3': 'I understand that the withholding amounts are estimates and my actual tax liability may differ. I will complete a new Form W-4 when my personal or financial situation changes.',
        'acknowledge_4': 'I certify that I am entitled to the withholding allowances and credits claimed on this certificate, and I understand that penalties for providing false information include fines up to $1,000 and/or imprisonment.',
        'all_acknowledgments_required': 'All acknowledgments must be checked before proceeding to review the official form.',
        'final_certification': 'Employee Certification',
        'final_cert_statement': 'Under penalties of perjury, I declare that I have examined this certificate and, to the best of my knowledge and belief, it is true, correct, and complete.',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'middle_initial': 'Middle Initial',
        'ssn': 'Social Security Number',
        'address': 'Address',
        'city': 'City',
        'state': 'State',
        'zip_code': 'ZIP Code',
        'filing_status_value': 'Filing Status',
        'dependents_amount': 'Child Tax Credit Amount',
        'other_credits': 'Other Credits Amount',
        'other_income': 'Other Income',
        'deductions': 'Deductions',
        'extra_withholding': 'Extra Withholding',
        'estimated_tax': 'Estimated Annual Tax',
        'estimated_withholding': 'Estimated Annual Withholding',
        'estimated_refund': 'Estimated Refund/Amount Owed',
        'irs_notice': 'IRS Notice',
        'irs_notice_text': 'This certificate is subject to review by the Internal Revenue Service. Complete a new Form W-4 when your personal or financial situation changes.',
        'back': 'Back to W-4 Form',
        'view_official_form': 'View Official W-4 Form',
        'sign_form': 'Sign Form W-4',
        'complete_review': 'Complete W-4 Review',
        'go_back_to_edit': 'Go Back to Edit',
        'continue_to_signature': 'Continue to Signature',
        'government_compliance': 'Government Compliance Requirement',
        'compliance_notice': 'This Form W-4 review process is required for tax compliance. You must review and acknowledge all information before signing.',
        'single': 'Single',
        'married_jointly': 'Married Filing Jointly',
        'married_separately': 'Married Filing Separately',
        'head_of_household': 'Head of Household'
      },
      es: {
        'w4_review_title': 'Revisar y Firmar Formulario W-4',
        'w4_review_subtitle': 'Certificado de Retención del Empleado - Revisión Requerida',
        'w4_review_desc': 'Por favor revise cuidadosamente su información de retención de impuestos antes de firmar. Esta información determina cuánto impuesto federal sobre la renta será retenido de su salario.',
        'back': 'Volver al Formulario W-4',
        'view_official_form': 'Ver Formulario Oficial W-4',
        'sign_form': 'Firmar Formulario W-4',
        'complete_review': 'Completar Revisión W-4'
      }
    };
    return translations[language][key] || key;
  };

  const getFilingStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      'Single': 'Single or Married filing separately',
      'Married filing jointly': 'Married filing jointly or Qualifying surviving spouse',
      'Head of household': 'Head of household'
    };
    return statusMap[status] || status;
  };

  const formatCurrency = (amount: number | string) => {
    const num = typeof amount === 'string' ? parseFloat(amount) || 0 : amount;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(num);
  };

  const calculateEstimatedTax = () => {
    // Simplified tax calculation for display purposes
    const income = parseFloat(w4FormData?.annual_income || '50000'); // Default estimate
    const otherIncome = parseFloat(w4FormData?.other_income || '0');
    const deductions = parseFloat(w4FormData?.deductions || '0');
    const totalIncome = income + otherIncome;
    const taxableIncome = Math.max(0, totalIncome - deductions - 13850); // 2025 standard deduction estimate
    
    // Simplified tax brackets (2025 rates for single filer)
    let tax = 0;
    if (taxableIncome > 0) {
      if (taxableIncome <= 11000) {
        tax = taxableIncome * 0.10;
      } else if (taxableIncome <= 44725) {
        tax = 1100 + (taxableIncome - 11000) * 0.12;
      } else if (taxableIncome <= 95375) {
        tax = 5147 + (taxableIncome - 44725) * 0.22;
      } else {
        tax = 16290 + (taxableIncome - 95375) * 0.24;
      }
    }
    
    return tax;
  };

  const calculateEstimatedWithholding = () => {
    const estimatedTax = calculateEstimatedTax();
    const extraWithholding = parseFloat(w4FormData?.extra_withholding || '0') * 26; // Bi-weekly to annual
    return estimatedTax + extraWithholding;
  };

  const handleAcknowledgmentChange = (index: number, checked: boolean) => {
    const newAcknowledgments = [...reviewAcknowledgments];
    newAcknowledgments[index] = checked;
    setReviewAcknowledgments(newAcknowledgments);
  };

  const canProceedToOfficialForm = () => {
    return reviewAcknowledgments.every(ack => ack);
  };

  const handleSignature = (signatureData: any) => {
    const reviewData: W4ReviewData = {
      w4FormData,
      reviewAcknowledgments,
      finalSignature: signatureData.signatureData,
      reviewCompletedAt: new Date().toISOString(),
      review_acknowledgments_completed: true,
      final_signature: signatureData.signatureData
    };
    onComplete(reviewData);
  };

  // Step 1: Information Review with Mandatory Acknowledgments
  const renderReviewStep = () => (
    <div className="space-y-8">
      {/* CRITICAL: IRS Compliance Notice */}
      <div className="bg-gradient-to-r from-red-50 to-red-100 border-2 border-red-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="h-12 w-12 bg-red-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>
          <div>
            <h3 className="text-2xl font-bold text-red-900 mb-3">🚨 CRITICAL: IRS TAX COMPLIANCE REQUIREMENT</h3>
            <div className="space-y-2 text-red-800">
              <p className="font-semibold">This Form W-4 review is MANDATORY under federal tax law.</p>
              <p>The W-4 form must generate the official IRS template to be legally compliant.</p>
              <p className="font-medium">You must review and acknowledge all information before signing.</p>
              <p className="text-sm bg-red-200 px-3 py-2 rounded font-medium">
                Reference: Internal Revenue Code Section 3402 | IRS Publication 15
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Personal Information Review */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="h-5 w-5" />
            <span>{t('personal_info')}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-600">{t('first_name')}:</span>
              <p className="mt-1 font-semibold">{w4FormData?.first_name || 'N/A'}</p>
            </div>
            <div>
              <span className="font-medium text-gray-600">{t('last_name')}:</span>
              <p className="mt-1 font-semibold">{w4FormData?.last_name || 'N/A'}</p>
            </div>
            <div>
              <span className="font-medium text-gray-600">{t('middle_initial')}:</span>
              <p className="mt-1 font-semibold">{w4FormData?.middle_initial || 'N/A'}</p>
            </div>
            <div>
              <span className="font-medium text-gray-600">{t('ssn')}:</span>
              <p className="mt-1 font-semibold">{w4FormData?.ssn ? `***-**-${w4FormData.ssn.slice(-4)}` : 'N/A'}</p>
            </div>
            <div className="md:col-span-2">
              <span className="font-medium text-gray-600">{t('address')}:</span>
              <p className="mt-1 font-semibold">
                {w4FormData?.address}<br />
                {w4FormData?.city}, {w4FormData?.state} {w4FormData?.zip_code}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Filing Status and Tax Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>{t('filing_status')}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-600">{t('filing_status_value')}:</span>
              <p className="mt-1 font-semibold">{getFilingStatusText(w4FormData?.filing_status)}</p>
            </div>
            <div>
              <span className="font-medium text-gray-600">{t('dependents_amount')}:</span>
              <p className="mt-1 font-semibold">{formatCurrency(w4FormData?.dependents_amount || 0)}</p>
            </div>
            <div>
              <span className="font-medium text-gray-600">{t('other_credits')}:</span>
              <p className="mt-1 font-semibold">{formatCurrency(w4FormData?.other_credits || 0)}</p>
            </div>
            <div>
              <span className="font-medium text-gray-600">{t('extra_withholding')}:</span>
              <p className="mt-1 font-semibold">{formatCurrency(w4FormData?.extra_withholding || 0)} per pay period</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Additional Income and Deductions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="h-5 w-5" />
            <span>{t('additional_info')}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-600">{t('other_income')}:</span>
              <p className="mt-1 font-semibold">{formatCurrency(w4FormData?.other_income || 0)}</p>
            </div>
            <div>
              <span className="font-medium text-gray-600">{t('deductions')}:</span>
              <p className="mt-1 font-semibold">{formatCurrency(w4FormData?.deductions || 0)}</p>
            </div>
            <div>
              <span className="font-medium text-gray-600">Multiple Jobs:</span>
              <p className="mt-1 font-semibold">{w4FormData?.multiple_jobs_checkbox ? 'Yes' : 'No'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tax Withholding Estimate */}
      <Card className="border-green-200 bg-green-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-green-900">
            <Calculator className="h-5 w-5" />
            <span>{t('withholding_summary')}</span>
          </CardTitle>
          <CardDescription className="text-green-700">
            Estimated annual tax calculation based on your entries
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="text-center p-4 bg-white rounded-lg">
              <p className="font-medium text-gray-600">{t('estimated_tax')}</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{formatCurrency(calculateEstimatedTax())}</p>
            </div>
            <div className="text-center p-4 bg-white rounded-lg">
              <p className="font-medium text-gray-600">Filing Status</p>
              <p className="text-lg font-bold text-gray-900 mt-2">{w4FormData?.filing_status?.replace('_', ' ') || 'Single'}</p>
            </div>
            <div className="text-center p-4 bg-white rounded-lg">
              <p className="font-medium text-gray-600">Extra Withholding</p>
              <p className="text-lg font-bold text-gray-900 mt-2">{formatCurrency(w4FormData?.extra_withholding || 0)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Mandatory Review Acknowledgments */}
      <Card className="border-amber-200 bg-amber-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-amber-900">
            <CheckCircle className="h-5 w-5" />
            <span>{t('review_acknowledgments')}</span>
          </CardTitle>
          <CardDescription className="text-amber-700">
            You must acknowledge each statement before proceeding to view the official form.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              t('acknowledge_1'),
              t('acknowledge_2'),
              t('acknowledge_3'),
              t('acknowledge_4')
            ].map((acknowledgment, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 bg-white rounded-lg border">
                <Checkbox
                  id={`acknowledgment-${index}`}
                  checked={reviewAcknowledgments[index]}
                  onCheckedChange={(checked) => handleAcknowledgmentChange(index, Boolean(checked))}
                  className="mt-1"
                />
                <label htmlFor={`acknowledgment-${index}`} className="text-sm leading-relaxed text-gray-800 cursor-pointer">
                  {acknowledgment}
                </label>
              </div>
            ))}
          </div>

          {!canProceedToOfficialForm() && (
            <Alert className="mt-6 border-red-200 bg-red-50">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription className="text-red-800">
                {t('all_acknowledgments_required')}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between items-center pt-6 border-t border-gray-200">
        <Button variant="outline" onClick={onBack}>
          {t('back')}
        </Button>
        
        <Button 
          onClick={() => setCurrentStep('official_form')}
          disabled={!canProceedToOfficialForm()}
          className={`px-8 ${!canProceedToOfficialForm() ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {t('view_official_form')}
        </Button>
      </div>
    </div>
  );

  // Step 2: Official Form Display
  const renderOfficialFormStep = () => (
    <OfficialW4Display
      employeeData={w4FormData}
      language={language}
      onSignatureComplete={(signedPdfData) => {
        const reviewData: W4ReviewData = {
          w4FormData,
          reviewAcknowledgments,
          finalSignature: signedPdfData,
          reviewCompletedAt: new Date().toISOString(),
          review_acknowledgments_completed: true,
          final_signature: signedPdfData
        };
        onComplete(reviewData);
      }}
      onBack={() => setCurrentStep('review')}
      showSignature={currentStep === 'signature'}
      setShowSignature={(show) => setCurrentStep(show ? 'signature' : 'official_form')}
    />
  );

  // Step 3: Digital Signature
  const renderSignatureStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <FileCheck className="h-12 w-12 text-green-600 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-gray-900">{t('final_certification')}</h2>
        <p className="text-gray-600 mt-2">Employee Signature Required</p>
      </div>

      <DigitalSignatureCapture
        signatureType="employee_w4"
        documentName="Form W-4 - Employee's Withholding Certificate"
        signerName={`${w4FormData?.first_name} ${w4FormData?.last_name}`}
        signerTitle="Employee"
        acknowledgments={[
          t('final_cert_statement')
        ]}
        requireIdentityVerification={true}
        language={language}
        onSignatureComplete={handleSignature}
        onCancel={() => setCurrentStep('official_form')}
      />
    </div>
  );

  // Main render based on current step
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'review':
        return renderReviewStep();
      case 'official_form':
      case 'signature':
        return renderOfficialFormStep();
      default:
        return renderReviewStep();
    }
  };

  return (
    <div className="space-y-8">
      {/* Step Progress Indicator */}
      <div className="flex items-center justify-center space-x-4 py-4">
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
          currentStep === 'review' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
            currentStep === 'review' ? 'bg-blue-600 text-white' : 'bg-gray-400 text-white'
          }`}>
            1
          </div>
          <span className="font-medium">{t('step_1_title')}</span>
        </div>
        
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
          currentStep === 'official_form' || currentStep === 'signature' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
            currentStep === 'official_form' || currentStep === 'signature' ? 'bg-blue-600 text-white' : 'bg-gray-400 text-white'
          }`}>
            2
          </div>
          <span className="font-medium">{t('step_2_title')}</span>
        </div>
        
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
          currentStep === 'signature' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
        }`}>
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
            currentStep === 'signature' ? 'bg-green-600 text-white' : 'bg-gray-400 text-white'
          }`}>
            3
          </div>
          <span className="font-medium">{t('step_3_title')}</span>
        </div>
      </div>

      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">{t('w4_review_title')}</h2>
        <p className="text-lg text-gray-600">{t('w4_review_subtitle')}</p>
        <p className="text-sm text-gray-500 mt-2">{t('w4_review_desc')}</p>
      </div>

      {/* Current Step Content */}
      {renderCurrentStep()}
    </div>
  );
}