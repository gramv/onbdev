"""
Federal Compliance Validation Service
Backend implementation of federal employment law compliance validation

CRITICAL: This module implements server-side federal employment law compliance
validations required to prevent legal liability in hotel employee onboarding.

All validations must meet federal standards exactly as specified by:
- U.S. Department of Labor (Fair Labor Standards Act)
- Internal Revenue Service (IRS)
- U.S. Citizenship and Immigration Services (USCIS)
- Equal Employment Opportunity Commission (EEOC)
"""

import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from .models import (
    FederalValidationError, FederalValidationResult, ComplianceAuditEntry,
    I9Section1Data, W4FormData, PersonalInfoValidationRequest
)

class FederalValidationService:
    """
    Central service for all federal compliance validations
    Ensures consistent validation across all backend endpoints
    """
    
    @staticmethod
    def validate_age(date_of_birth: str) -> FederalValidationResult:
        """
        Validate employee age meets federal requirements
        CRITICAL: Federal law prohibits employment of individuals under 18 in most hotel positions
        Reference: Fair Labor Standards Act (FLSA) 29 U.S.C. § 203
        """
        result = FederalValidationResult(is_valid=True)
        
        if not date_of_birth:
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='date_of_birth',
                message='Date of birth is required for federal employment eligibility verification',
                legal_code='FLSA-203',
                severity='error',
                compliance_note='Required under Fair Labor Standards Act for age verification'
            ))
            return result
        
        try:
            birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year
            
            # Adjust age if birthday hasn't occurred this year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            
            if age < 18:
                result.is_valid = False
                result.errors.append(FederalValidationError(
                    field='date_of_birth',
                    message=f'FEDERAL COMPLIANCE VIOLATION: Employee must be at least 18 years old. Current age: {age}',
                    legal_code='FLSA-203-CHILD-LABOR',
                    severity='error',
                    compliance_note='Employment of individuals under 18 in hotel positions may violate federal child labor laws. Special work permits and restricted hours may be required. Consult legal counsel immediately.'
                ))
            elif age < 21:
                result.warnings.append(FederalValidationError(
                    field='date_of_birth',
                    message=f'Employee is {age} years old. Alcohol service restrictions may apply.',
                    legal_code='FLSA-203-MINOR',
                    severity='warning',
                    compliance_note='Employees under 21 cannot serve or handle alcoholic beverages in most jurisdictions'
                ))
            
            if result.is_valid:
                result.compliance_notes.append(f'Age verification completed: {age} years old. Meets federal minimum age requirements.')
                
        except ValueError:
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='date_of_birth',
                message='Invalid date format. Date of birth must be in YYYY-MM-DD format',
                legal_code='DATE-FORMAT-ERROR',
                severity='error'
            ))
        
        return result
    
    @staticmethod
    def validate_ssn(ssn: str) -> FederalValidationResult:
        """
        Validate Social Security Number meets federal requirements
        Reference: 26 U.S.C. § 3401 (IRS), 42 U.S.C. § 405 (SSA)
        """
        result = FederalValidationResult(is_valid=True)
        
        if not ssn:
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='ssn',
                message='Social Security Number is required for federal tax withholding and employment verification',
                legal_code='IRC-3401-SSN',
                severity='error',
                compliance_note='Required under Internal Revenue Code Section 3401 for payroll tax withholding'
            ))
            return result
        
        # Remove formatting characters
        clean_ssn = ssn.replace('-', '').replace(' ', '')
        
        # Must be exactly 9 digits
        if not re.match(r'^\d{9}$', clean_ssn):
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='ssn',
                message='SSN must be exactly 9 digits in format XXX-XX-XXXX',
                legal_code='SSA-405-FORMAT',
                severity='error',
                compliance_note='Social Security Administration requires 9-digit format'
            ))
            return result
        
        # Federal prohibited SSN patterns
        area = clean_ssn[:3]
        group = clean_ssn[3:5]
        serial = clean_ssn[5:9]
        
        # Invalid area numbers (000, 666, 900-999)
        if area == '000' or area == '666' or int(area) >= 900:
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='ssn',
                message=f'Invalid SSN area number: {area}. This SSN format is not issued by the Social Security Administration',
                legal_code='SSA-405-INVALID-AREA',
                severity='error',
                compliance_note='SSN area numbers 000, 666, and 900-999 are never issued'
            ))
            return result
        
        # Invalid group number (00)
        if group == '00':
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='ssn',
                message='Invalid SSN group number: 00. Group number cannot be 00',
                legal_code='SSA-405-INVALID-GROUP',
                severity='error',
                compliance_note='SSN group number 00 is never issued'
            ))
            return result
        
        # Invalid serial number (0000)
        if serial == '0000':
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='ssn',
                message='Invalid SSN serial number: 0000. Serial number cannot be 0000',
                legal_code='SSA-405-INVALID-SERIAL',
                severity='error',
                compliance_note='SSN serial number 0000 is never issued'
            ))
            return result
        
        # Known advertising/placeholder SSNs
        known_invalid_ssns = [
            '123456789', '111111111', '222222222', '333333333', '444444444',
            '555555555', '777777777', '888888888', '999999999', '078051120',
            '219099999', '457555462'
        ]
        
        if clean_ssn in known_invalid_ssns:
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='ssn',
                message='This SSN is a known invalid/placeholder number and cannot be used for employment',
                legal_code='SSA-405-PLACEHOLDER',
                severity='error',
                compliance_note='Placeholder SSNs used in advertising or examples are not valid for employment'
            ))
            return result
        
        result.compliance_notes.append('SSN format validation passed - meets federal requirements')
        return result
    
    @staticmethod
    def validate_i9_section1(form_data: I9Section1Data) -> FederalValidationResult:
        """
        Validate I-9 Section 1 meets USCIS requirements
        Reference: 8 U.S.C. § 1324a, 8 CFR § 274a
        """
        result = FederalValidationResult(is_valid=True)
        
        # Required fields validation
        required_fields = [
            ('employee_last_name', 'Last name is required for I-9 compliance'),
            ('employee_first_name', 'First name is required for I-9 compliance'),
            ('address_street', 'Street address is required for I-9 compliance'),
            ('address_city', 'City is required for I-9 compliance'),
            ('address_state', 'State is required for I-9 compliance'),
            ('address_zip', 'ZIP code is required for I-9 compliance'),
            ('date_of_birth', 'Date of birth is required for I-9 compliance'),
            ('ssn', 'SSN is required for I-9 compliance'),
            ('email', 'Email is required for I-9 compliance'),
            ('phone', 'Phone number is required for I-9 compliance'),
            ('citizenship_status', 'Citizenship status is required for I-9 compliance')
        ]
        
        for field_name, message in required_fields:
            field_value = getattr(form_data, field_name, None)
            if not field_value or str(field_value).strip() == '':
                result.is_valid = False
                result.errors.append(FederalValidationError(
                    field=field_name,
                    message=message,
                    legal_code='INA-274A-REQUIRED',
                    severity='error',
                    compliance_note='Required under Immigration and Nationality Act Section 274A'
                ))
        
        # Citizenship status validation
        valid_citizenship_statuses = ['us_citizen', 'noncitizen_national', 'permanent_resident', 'authorized_alien']
        if form_data.citizenship_status and form_data.citizenship_status not in valid_citizenship_statuses:
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='citizenship_status',
                message='Invalid citizenship status selected',
                legal_code='INA-274A-STATUS',
                severity='error',
                compliance_note='Must select one of the four federal citizenship/work authorization categories'
            ))
        
        # Additional validation for non-citizens
        if form_data.citizenship_status == 'permanent_resident':
            if not form_data.uscis_number and not form_data.i94_admission_number:
                result.is_valid = False
                result.errors.append(FederalValidationError(
                    field='uscis_number',
                    message='USCIS Number or I-94 Admission Number is required for permanent residents',
                    legal_code='INA-274A-DOCUMENT',
                    severity='error',
                    compliance_note='Permanent residents must provide USCIS Number or I-94 Admission Number'
                ))
        
        if form_data.citizenship_status == 'authorized_alien':
            if not form_data.uscis_number and not form_data.i94_admission_number and not form_data.passport_number:
                result.is_valid = False
                result.errors.append(FederalValidationError(
                    field='uscis_number',
                    message='At least one identification number is required for authorized aliens',
                    legal_code='INA-274A-ALIEN-ID',
                    severity='error',
                    compliance_note='Must provide USCIS Number, I-94 Number, or Passport Number'
                ))
            
            if not form_data.work_authorization_expiration:
                result.is_valid = False
                result.errors.append(FederalValidationError(
                    field='work_authorization_expiration',
                    message='Work authorization expiration date is required for authorized aliens',
                    legal_code='INA-274A-EXPIRATION',
                    severity='error',
                    compliance_note='Required to verify ongoing work authorization status'
                ))
            else:
                # Check if work authorization is expired
                try:
                    exp_date = datetime.strptime(form_data.work_authorization_expiration, '%Y-%m-%d').date()
                    today = date.today()
                    
                    if exp_date <= today:
                        result.is_valid = False
                        result.errors.append(FederalValidationError(
                            field='work_authorization_expiration',
                            message='Work authorization has expired. Cannot proceed with employment',
                            legal_code='INA-274A-EXPIRED',
                            severity='error',
                            compliance_note='Expired work authorization prohibits legal employment'
                        ))
                    elif exp_date <= date.fromordinal(today.toordinal() + 30):
                        result.warnings.append(FederalValidationError(
                            field='work_authorization_expiration',
                            message='Work authorization expires within 30 days. Renewal documentation may be needed',
                            legal_code='INA-274A-EXPIRING',
                            severity='warning',
                            compliance_note='Early renewal recommended to avoid employment interruption'
                        ))
                except ValueError:
                    result.is_valid = False
                    result.errors.append(FederalValidationError(
                        field='work_authorization_expiration',
                        message='Invalid work authorization expiration date format',
                        legal_code='INA-274A-DATE-FORMAT',
                        severity='error'
                    ))
        
        # Age validation
        if form_data.date_of_birth:
            age_validation = FederalValidationService.validate_age(form_data.date_of_birth)
            result.errors.extend(age_validation.errors)
            result.warnings.extend(age_validation.warnings)
            if not age_validation.is_valid:
                result.is_valid = False
        
        # SSN validation
        if form_data.ssn:
            ssn_validation = FederalValidationService.validate_ssn(form_data.ssn)
            result.errors.extend(ssn_validation.errors)
            result.warnings.extend(ssn_validation.warnings)
            if not ssn_validation.is_valid:
                result.is_valid = False
        
        # ZIP code validation
        if form_data.address_zip and not re.match(r'^\d{5}(-\d{4})?$', form_data.address_zip):
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='address_zip',
                message='ZIP code must be in format 12345 or 12345-6789',
                legal_code='USPS-ZIP-FORMAT',
                severity='error',
                compliance_note='Must use valid US Postal Service ZIP code format'
            ))
        
        # Email validation
        if form_data.email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', form_data.email):
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='email',
                message='Valid email address is required',
                legal_code='CONTACT-EMAIL-FORMAT',
                severity='error',
                compliance_note='Required for employment communications and compliance notices'
            ))
        
        # Phone validation
        if form_data.phone:
            clean_phone = re.sub(r'\D', '', form_data.phone)
            if len(clean_phone) != 10:
                result.is_valid = False
                result.errors.append(FederalValidationError(
                    field='phone',
                    message='Phone number must be 10 digits',
                    legal_code='CONTACT-PHONE-FORMAT',
                    severity='error',
                    compliance_note='Required for employment communications and emergency contact'
                ))
        
        if result.is_valid:
            result.compliance_notes.append('I-9 Section 1 validation completed - meets federal immigration compliance requirements')
        
        return result
    
    @staticmethod
    def validate_w4_form(form_data: W4FormData) -> FederalValidationResult:
        """
        Validate W-4 form meets IRS requirements
        Reference: 26 U.S.C. § 3402, IRS Publication 15
        """
        result = FederalValidationResult(is_valid=True)
        
        # Required fields validation
        required_fields = [
            ('first_name', 'First name is required for W-4 tax withholding'),
            ('last_name', 'Last name is required for W-4 tax withholding'),
            ('address', 'Address is required for W-4 tax withholding'),
            ('city', 'City is required for W-4 tax withholding'),
            ('state', 'State is required for W-4 tax withholding'),
            ('zip_code', 'ZIP code is required for W-4 tax withholding'),
            ('ssn', 'SSN is required for W-4 tax withholding'),
            ('filing_status', 'Filing status is required for W-4 tax withholding'),
            ('signature', 'Employee signature is required for W-4 validity'),
            ('signature_date', 'Signature date is required for W-4 validity')
        ]
        
        for field_name, message in required_fields:
            field_value = getattr(form_data, field_name, None)
            if not field_value or str(field_value).strip() == '':
                result.is_valid = False
                result.errors.append(FederalValidationError(
                    field=field_name,
                    message=message,
                    legal_code='IRC-3402-REQUIRED',
                    severity='error',
                    compliance_note='Required under Internal Revenue Code Section 3402 for federal tax withholding'
                ))
        
        # Filing status validation
        valid_filing_statuses = ['Single', 'Married filing jointly', 'Head of household']
        if form_data.filing_status and form_data.filing_status not in valid_filing_statuses:
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='filing_status',
                message='Invalid filing status selected',
                legal_code='IRC-3402-FILING-STATUS',
                severity='error',
                compliance_note='Must use IRS-approved filing status categories'
            ))
        
        # SSN validation
        if form_data.ssn:
            ssn_validation = FederalValidationService.validate_ssn(form_data.ssn)
            result.errors.extend(ssn_validation.errors)
            result.warnings.extend(ssn_validation.warnings)
            if not ssn_validation.is_valid:
                result.is_valid = False
        
        # ZIP code validation
        if form_data.zip_code and not re.match(r'^\d{5}(-\d{4})?$', form_data.zip_code):
            result.is_valid = False
            result.errors.append(FederalValidationError(
                field='zip_code',
                message='ZIP code must be in format 12345 or 12345-6789',
                legal_code='USPS-ZIP-FORMAT',
                severity='error',
                compliance_note='Must use valid US Postal Service ZIP code format for tax purposes'
            ))
        
        # Numerical field validation
        numerical_fields = [
            'dependents_amount', 'other_credits', 'other_income', 'deductions', 'extra_withholding'
        ]
        
        for field_name in numerical_fields:
            field_value = getattr(form_data, field_name, None)
            if field_value is not None:
                try:
                    value = float(field_value)
                    if value < 0:
                        result.is_valid = False
                        result.errors.append(FederalValidationError(
                            field=field_name,
                            message=f'{field_name.replace("_", " ")} must be a non-negative number',
                            legal_code='IRC-3402-AMOUNT',
                            severity='error',
                            compliance_note='All monetary amounts must be valid non-negative numbers'
                        ))
                except (ValueError, TypeError):
                    result.is_valid = False
                    result.errors.append(FederalValidationError(
                        field=field_name,
                        message=f'{field_name.replace("_", " ")} must be a valid number',
                        legal_code='IRC-3402-AMOUNT',
                        severity='error',
                        compliance_note='All monetary amounts must be valid numbers'
                    ))
        
        # Signature date validation
        if form_data.signature_date:
            try:
                signature_date = datetime.strptime(form_data.signature_date, '%Y-%m-%d').date()
                today = date.today()
                
                if signature_date > today:
                    result.is_valid = False
                    result.errors.append(FederalValidationError(
                        field='signature_date',
                        message='Signature date cannot be in the future',
                        legal_code='IRC-3402-DATE-FUTURE',
                        severity='error',
                        compliance_note='W-4 signature date must be current or historical'
                    ))
                elif (today - signature_date).days > 30:
                    result.warnings.append(FederalValidationError(
                        field='signature_date',
                        message='W-4 signature date is more than 30 days old. Consider requesting updated form',
                        legal_code='IRC-3402-DATE-OLD',
                        severity='warning',
                        compliance_note='IRS recommends current W-4 forms for accurate withholding'
                    ))
            except ValueError:
                result.is_valid = False
                result.errors.append(FederalValidationError(
                    field='signature_date',
                    message='Invalid signature date format',
                    legal_code='IRC-3402-DATE-FORMAT',
                    severity='error'
                ))
        
        if result.is_valid:
            result.compliance_notes.append('W-4 validation completed - meets federal tax withholding compliance requirements')
        
        return result
    
    @staticmethod
    def generate_compliance_audit_entry(
        form_type: str,
        validation_result: FederalValidationResult,
        user_info: Dict[str, Any]
    ) -> ComplianceAuditEntry:
        """Generate compliance audit trail entry"""
        legal_codes = []
        for error in validation_result.errors + validation_result.warnings:
            legal_codes.append(error.legal_code)
        
        audit_id = f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(user_info.get('id', 'unknown')))}"[-20:]
        
        return ComplianceAuditEntry(
            timestamp=datetime.now().isoformat(),
            form_type=form_type,
            user_id=user_info.get('id', 'unknown'),
            user_email=user_info.get('email', 'unknown'),
            compliance_status='COMPLIANT' if validation_result.is_valid else 'NON_COMPLIANT',
            error_count=len(validation_result.errors),
            warning_count=len(validation_result.warnings),
            legal_codes=legal_codes,
            compliance_notes=validation_result.compliance_notes,
            audit_id=audit_id
        )