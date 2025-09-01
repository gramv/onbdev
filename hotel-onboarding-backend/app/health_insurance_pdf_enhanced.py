"""
Enhanced Health Insurance PDF Generation
Comprehensive PDF generation with retry mechanisms, validation, and error handling
"""

import asyncio
import base64
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

from .pdf_forms import PDFFormFiller
from .supabase_service_enhanced import EnhancedSupabaseService

logger = logging.getLogger(__name__)

class PDFGenerationError(Exception):
    """Custom exception for PDF generation failures"""
    pass

class ValidationError(Exception):
    """Custom exception for data validation failures"""
    pass

class HealthInsurancePDFGenerator:
    """Enhanced PDF generator with comprehensive error handling and retry mechanisms"""
    
    def __init__(self, supabase_service: EnhancedSupabaseService):
        self.supabase_service = supabase_service
        self.pdf_filler = PDFFormFiller()
        self.max_retries = 3
        self.retry_delays = [1.0, 2.0, 4.0]  # Exponential backoff
        
    async def generate_pdf_with_retry(
        self,
        employee_data: Dict[str, Any],
        employee_id: str,
        operation_id: str,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate PDF with comprehensive retry mechanism"""
        
        max_retries = max_retries or self.max_retries
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"🔄 PDF generation attempt {attempt + 1}/{max_retries + 1} - Operation: {operation_id}")
                
                # Validate data before generation
                validation_result = self.validate_health_insurance_data(employee_data)
                if not validation_result['is_valid']:
                    raise ValidationError(f"Data validation failed: {validation_result['errors']}")
                
                # Generate PDF
                pdf_result = await self.generate_pdf_internal(
                    employee_data=employee_data,
                    employee_id=employee_id,
                    operation_id=operation_id,
                    attempt=attempt + 1
                )
                
                logger.info(f"✅ PDF generation successful on attempt {attempt + 1} - Operation: {operation_id}")
                return {
                    'success': True,
                    'pdf_data': pdf_result['pdf_data'],
                    'metadata': pdf_result['metadata'],
                    'attempts': attempt + 1
                }
                
            except ValidationError as e:
                # Don't retry validation errors
                logger.error(f"❌ Validation error (no retry) - Operation: {operation_id}: {e}")
                return {
                    'success': False,
                    'error': 'VALIDATION_ERROR',
                    'message': f"Form validation failed: {str(e)}",
                    'attempts': attempt + 1,
                    'status_code': 422  # Unprocessable Entity for validation errors
                }
                
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ PDF generation attempt {attempt + 1} failed - Operation: {operation_id}: {e}")
                
                if attempt < max_retries:
                    # Wait with exponential backoff
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    logger.info(f"⏳ Waiting {delay}s before retry - Operation: {operation_id}")
                    await asyncio.sleep(delay)
                    
                    # Try with simplified data on subsequent attempts
                    if attempt > 0:
                        employee_data = self.simplify_form_data(employee_data)
                        logger.info(f"🔧 Using simplified data for retry - Operation: {operation_id}")
        
        # All retries failed
        logger.error(f"❌ PDF generation failed after {max_retries + 1} attempts - Operation: {operation_id}")
        return {
            'success': False,
            'error': 'PDF_GENERATION_FAILED',
            'message': f"PDF generation failed after {max_retries + 1} attempts: {str(last_error)}",
            'attempts': max_retries + 1
        }
    
    async def generate_pdf_internal(
        self,
        employee_data: Dict[str, Any],
        employee_id: str,
        operation_id: str,
        attempt: int
    ) -> Dict[str, Any]:
        """Internal PDF generation logic"""
        
        start_time = time.time()
        
        try:
            # Get complete personal information
            complete_personal_info = await self.get_complete_personal_info(employee_id, employee_data)
            
            # Prepare PDF data
            pdf_data = self.prepare_pdf_data(employee_data, complete_personal_info, employee_id)
            
            # Generate PDF using form filler
            pdf_bytes = self.pdf_filler.fill_health_insurance_form(pdf_data)
            
            # Validate generated PDF
            if not self.validate_pdf_output(pdf_bytes):
                raise PDFGenerationError("Generated PDF failed validation")
            
            # Convert to base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            generation_time = time.time() - start_time
            
            # Prepare metadata
            metadata = {
                'employee_id': employee_id,
                'operation_id': operation_id,
                'generation_time': generation_time,
                'attempt': attempt,
                'pdf_size': len(pdf_bytes),
                'timestamp': datetime.now().isoformat(),
                'medical_plan': pdf_data.get('medicalPlan'),
                'dependents_count': len(pdf_data.get('dependents', [])),
                'has_signature': bool(pdf_data.get('signatureData'))
            }
            
            logger.info(f"📄 PDF generated successfully - Size: {len(pdf_bytes)} bytes, Time: {generation_time:.2f}s")
            
            return {
                'pdf_data': pdf_base64,
                'metadata': metadata
            }
            
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"❌ PDF generation internal error after {generation_time:.2f}s: {e}")
            raise PDFGenerationError(f"Internal PDF generation failed: {str(e)}")
    
    def validate_health_insurance_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate health insurance form data with comprehensive error reporting"""

        errors = []
        warnings = []
        field_errors = {}

        # Check required fields
        personal_info = employee_data.get('personalInfo', {})
        if not personal_info.get('firstName', '').strip():
            errors.append("Personal info: First name is required")
            field_errors['personalInfo.firstName'] = ['First name is required']
        if not personal_info.get('lastName', '').strip():
            errors.append("Personal info: Last name is required")
            field_errors['personalInfo.lastName'] = ['Last name is required']
        if not personal_info.get('ssn', '').strip():
            errors.append("Personal info: SSN is required")
            field_errors['personalInfo.ssn'] = ['SSN is required']

        # Check medical plan selection (only if not waived)
        medical_waived = employee_data.get('medicalWaived', False)
        if not medical_waived:
            if not employee_data.get('medicalPlan', '').strip():
                errors.append("Medical plan selection is required when not waiving coverage")
                field_errors['medicalPlan'] = ['Medical plan selection is required']
            if not employee_data.get('medicalTier', '').strip():
                errors.append("Medical tier selection is required when not waiving coverage")
                field_errors['medicalTier'] = ['Medical tier selection is required']

        # Check Section 125 acknowledgment (always required)
        if not employee_data.get('section125Acknowledged', False):
            errors.append("Section 125 plan acknowledgment is required")
            field_errors['section125Acknowledged'] = ['Section 125 acknowledgment is required']

        # Validate dependents if family coverage selected
        medical_tier = employee_data.get('medicalTier', 'employee')
        dependents = employee_data.get('dependents', [])

        if medical_tier in ['employee_spouse', 'employee_children', 'family'] and not medical_waived:
            if not dependents:
                warnings.append(f"No dependents found for {medical_tier} coverage")
            else:
                for i, dependent in enumerate(dependents):
                    if not dependent.get('firstName', '').strip():
                        errors.append(f"Dependent {i+1}: First name is required")
                        field_errors[f'dependents.{i}.firstName'] = ['First name is required']
                    if not dependent.get('lastName', '').strip():
                        errors.append(f"Dependent {i+1}: Last name is required")
                        field_errors[f'dependents.{i}.lastName'] = ['Last name is required']
                    if not dependent.get('dateOfBirth'):
                        errors.append(f"Dependent {i+1}: Date of birth is required")
                        field_errors[f'dependents.{i}.dateOfBirth'] = ['Date of birth is required']

        # Check effective date
        effective_date = employee_data.get('effectiveDate')
        if effective_date:
            try:
                date_obj = datetime.fromisoformat(effective_date.replace('Z', '+00:00'))
                if date_obj < datetime.now():
                    warnings.append("Effective date is in the past")
            except ValueError:
                errors.append("Invalid effective date format")
                field_errors['effectiveDate'] = ['Invalid date format']

        # Additional business logic validation
        if not medical_waived and not employee_data.get('medicalPlan'):
            if not employee_data.get('isWaived', False):
                errors.append("You must either select a medical plan or waive coverage")
                field_errors['coverage'] = ['Coverage selection or waiver is required']

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'field_errors': field_errors,
            'error_count': len(errors),
            'warning_count': len(warnings)
        }
    
    def prepare_pdf_data(
        self, 
        employee_data: Dict[str, Any], 
        personal_info: Dict[str, Any], 
        employee_id: str
    ) -> Dict[str, Any]:
        """Prepare data for PDF generation"""
        
        # Normalize dental and vision coverage fields
        dental_coverage = employee_data.get("dentalCoverage", False) or employee_data.get("dentalEnrolled", False)
        vision_coverage = employee_data.get("visionCoverage", False) or employee_data.get("visionEnrolled", False)
        
        return {
            "firstName": personal_info.get('firstName', ''),
            "lastName": personal_info.get('lastName', ''),
            "employee_id": employee_id,
            "medicalPlan": employee_data.get("medicalPlan", ""),
            "medicalTier": employee_data.get("medicalTier", "employee"),
            "medicalWaived": employee_data.get("medicalWaived", False),
            "dentalCoverage": dental_coverage,
            "dentalEnrolled": dental_coverage,
            "dentalTier": employee_data.get("dentalTier", "employee"),
            "dentalWaived": employee_data.get("dentalWaived", False),
            "visionCoverage": vision_coverage,
            "visionEnrolled": vision_coverage,
            "visionTier": employee_data.get("visionTier", "employee"),
            "visionWaived": employee_data.get("visionWaived", False),
            "isWaived": employee_data.get("isWaived", False),
            "waiveReason": employee_data.get("waiveReason", ""),
            "otherCoverageDetails": employee_data.get("otherCoverageDetails", ""),
            "dependents": employee_data.get("dependents", []),
            "hasStepchildren": employee_data.get("hasStepchildren", False),
            "stepchildrenNames": employee_data.get("stepchildrenNames", ""),
            "dependentsSupported": employee_data.get("dependentsSupported", False),
            "irsDependentConfirmation": employee_data.get("irsDependentConfirmation", False),
            "section125Acknowledged": employee_data.get("section125Acknowledged", False),
            "effectiveDate": employee_data.get("effectiveDate", ""),
            "signatureData": employee_data.get("signatureData"),
            "personalInfo": personal_info,
        }
    
    def simplify_form_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify form data for retry attempts"""
        
        simplified = employee_data.copy()
        
        # Remove complex nested objects that might cause issues
        simplified['dependents'] = simplified.get('dependents', [])[:3]  # Limit to 3 dependents
        
        # Simplify personal info to essential fields only
        personal_info = simplified.get('personalInfo', {})
        simplified['personalInfo'] = {
            'firstName': personal_info.get('firstName', ''),
            'lastName': personal_info.get('lastName', ''),
            'ssn': personal_info.get('ssn', ''),
            'dateOfBirth': personal_info.get('dateOfBirth', ''),
            'email': personal_info.get('email', ''),
            'phone': personal_info.get('phone', '')
        }
        
        # Remove optional fields that might cause issues
        optional_fields = [
            'totalBiweeklyCost', 'totalMonthlyCost', 'totalAnnualCost',
            'stepchildrenNames', 'otherCoverageDetails', 'waiveReason'
        ]
        
        for field in optional_fields:
            simplified.pop(field, None)
        
        return simplified
    
    def validate_pdf_output(self, pdf_bytes: bytes) -> bool:
        """Validate generated PDF output"""
        
        if not pdf_bytes:
            return False
        
        if len(pdf_bytes) < 1000:  # PDF too small
            return False
        
        if not pdf_bytes.startswith(b'%PDF'):
            return False
        
        if b'%%EOF' not in pdf_bytes:
            return False
        
        return True
    
    async def get_complete_personal_info(self, employee_id: str, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete personal information from various sources"""
        
        # Start with personal info from request
        personal_info = employee_data.get('personalInfo', {}).copy()
        
        # For test employees, use mock data
        if employee_id.startswith('test-'):
            personal_info.setdefault('firstName', 'Test')
            personal_info.setdefault('lastName', 'Employee')
            personal_info.setdefault('ssn', '123-45-6789')
            personal_info.setdefault('email', 'test@example.com')
            return personal_info
        
        try:
            # Get employee data from database
            employee = await self.supabase_service.get_employee_by_id(employee_id)
            if employee:
                personal_info.setdefault('firstName', employee.get('first_name', ''))
                personal_info.setdefault('lastName', employee.get('last_name', ''))
                personal_info.setdefault('email', employee.get('email', ''))
            
            # Try to get personal info from saved form data
            form_response = self.supabase_service.client.table('onboarding_form_data')\
                .select('form_data')\
                .eq('employee_id', employee_id)\
                .eq('step_id', 'personal-info')\
                .order('updated_at', desc=True)\
                .limit(1)\
                .execute()
            
            if form_response.data:
                saved_personal_info = form_response.data[0].get('form_data', {})
                for key, value in saved_personal_info.items():
                    if value and not personal_info.get(key):
                        personal_info[key] = value
                        
        except Exception as e:
            logger.warning(f"Could not fetch complete personal info for {employee_id}: {e}")
        
        return personal_info


# Utility functions for error handling
def handle_health_insurance_validation_error(error: ValidationError, operation_id: str, employee_id: str) -> Dict[str, Any]:
    """Handle validation errors"""
    logger.error(f"❌ Health insurance validation error - Operation: {operation_id}, Employee: {employee_id}: {error}")
    return {
        "success": False,
        "message": "Form data validation failed",
        "error": "VALIDATION_ERROR",
        "details": str(error),
        "operation_id": operation_id
    }

def handle_health_insurance_pdf_error(error: PDFGenerationError, operation_id: str, employee_id: str) -> Dict[str, Any]:
    """Handle PDF generation errors"""
    logger.error(f"❌ Health insurance PDF error - Operation: {operation_id}, Employee: {employee_id}: {error}")
    return {
        "success": False,
        "message": "PDF generation failed",
        "error": "PDF_GENERATION_ERROR",
        "details": str(error),
        "operation_id": operation_id
    }

def handle_health_insurance_unexpected_error(error: Exception, operation_id: str, employee_id: str) -> Dict[str, Any]:
    """Handle unexpected errors"""
    logger.error(f"❌ Health insurance unexpected error - Operation: {operation_id}, Employee: {employee_id}: {error}")
    return {
        "success": False,
        "message": "An unexpected error occurred",
        "error": "INTERNAL_SERVER_ERROR",
        "details": str(error),
        "operation_id": operation_id
    }

async def log_pdf_generation_metrics(
    operation_id: str,
    employee_id: str,
    pdf_type: str,
    duration: float,
    success: bool,
    attempts: int = 1
):
    """Log PDF generation metrics for monitoring"""
    
    metrics = {
        'operation_id': operation_id,
        'employee_id': employee_id,
        'pdf_type': pdf_type,
        'duration': duration,
        'success': success,
        'attempts': attempts,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"📊 PDF Generation Metrics: {metrics}")
    
    # In production, send to monitoring service
    # await send_to_monitoring_service(metrics)
