from __future__ import annotations

import base64
import io
import os
import json
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

import fitz  # PyMuPDF
from PIL import Image, ImageOps


STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
HI_TEMPLATE_PATH = os.path.join(STATIC_DIR, "HI Form_final3.pdf")
HI_MAPPING_PATH = os.path.join(STATIC_DIR, "health_insurance_mapping.json")


def _normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes", "y"}
    return bool(value)


def _load_signature_image(signature_b64: str) -> Optional[Image.Image]:
    try:
        raw = base64.b64decode(signature_b64.split(',')[-1], validate=False)
        img = Image.open(io.BytesIO(raw)).convert("RGBA")
        # Remove near-white background for transparency
        datas = img.getdata()
        new_data = []
        for px in datas:
            r, g, b, a = px
            if r > 240 and g > 240 and b > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append((r, g, b, a))
        img.putdata(new_data)
        # Slight trim to remove empty borders
        bbox = ImageOps.invert(img.split()[3]).getbbox()  # use alpha channel
        if bbox:
            img = img.crop(bbox)
        return img
    except Exception:
        return None


class HealthInsuranceFormOverlay:
    """Overlay selections onto the official HI Form_final3.pdf template.
    
    This version properly sets widget field values instead of just drawing text.
    """

    def _mask_ssn(self, ssn: str, mask_all: bool) -> str:
        if not ssn:
            return ""
        digits = ''.join([c for c in ssn if c.isdigit()])
        if len(digits) == 9:
            formatted = f"{digits[0:3]}-{digits[3:5]}-{digits[5:9]}"
            if mask_all:
                return f"***-**-{formatted[-4:]}"
            return formatted
        return ssn

    def _fmt_date(self, date_str: Optional[str]) -> str:
        if not date_str:
            return datetime.now().strftime('%m/%d/%Y')
        try:
            # Try ISO format
            dt = datetime.fromisoformat(date_str.replace('Z','+00:00'))
            return dt.strftime('%m/%d/%Y')
        except Exception:
            # Try other common formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%m/%d/%Y')
                except:
                    continue
            # Fallback to original
            return date_str

    def _set_text_field(self, page: fitz.Page, field_name: str, value: str) -> bool:
        """Set a text field value by name."""
        if not value:
            return False
        
        for widget in page.widgets():
            if widget.field_name == field_name:
                try:
                    widget.field_value = str(value)
                    widget.update()
                    return True
                except Exception as e:
                    print(f"Error setting field {field_name}: {e}")
        return False

    def _set_checkbox(self, page: fitz.Page, field_name: str, checked: bool = True) -> bool:
        """Set a checkbox field value by name."""
        for widget in page.widgets():
            if widget.field_name == field_name:
                try:
                    widget.field_value = bool(checked)
                    widget.update()
                    return True
                except Exception as e:
                    print(f"Error setting checkbox {field_name}: {e}")
        return False

    def _set_radio_button(self, page: fitz.Page, field_name: str, checked: bool = True) -> bool:
        """Set a radio button field value by name."""
        for widget in page.widgets():
            if widget.field_name == field_name and widget.field_type_string == "RadioButton":
                try:
                    widget.field_value = bool(checked)
                    widget.update()
                    return True
                except Exception as e:
                    print(f"Error setting radio {field_name}: {e}")
        return False

    def generate(self, form_data: Dict[str, Any], employee_first: str, employee_last: str,
                 signature_b64: Optional[str] = None, signed_date: Optional[str] = None,
                 preview: bool = True, return_details: bool = False) -> Union[bytes, Tuple[bytes, List[str], List[Dict[str, Any]]]]:

        doc = fitz.open(HI_TEMPLATE_PATH)
        try:
            page1 = doc[0]
            page2 = doc[1] if doc.page_count >= 2 else None
            
            actions: List[Dict[str, Any]] = []
            warnings: List[str] = []
            
            # Read form data
            personal_info = form_data.get("personalInfo", {})
            is_waived = _normalize_bool(form_data.get("isWaived", False))
            
            # Extract personal information
            first_name = personal_info.get("firstName") or employee_first or ""
            last_name = personal_info.get("lastName") or employee_last or ""
            middle_initial = personal_info.get("middleInitial", "")
            ssn = personal_info.get("ssn", "")
            date_of_birth = personal_info.get("dateOfBirth", "")
            address = personal_info.get("address", "")
            city = personal_info.get("city", "")
            state = personal_info.get("state", "")
            zip_code = personal_info.get("zip") or personal_info.get("zipCode", "")
            phone = personal_info.get("phone", "")
            email = personal_info.get("email", "")
            gender = personal_info.get("gender", "").upper()
            
            # Extract coverage information
            medical_plan = form_data.get("medicalPlan", "")
            medical_tier = form_data.get("medicalTier", "employee").lower()
            medical_waived = _normalize_bool(form_data.get("medicalWaived", False))
            
            # Frontend sends dentalEnrolled/visionEnrolled for UI integration
            # But also dentalCoverage/visionCoverage for backwards compatibility
            dental_coverage = _normalize_bool(form_data.get("dentalEnrolled", form_data.get("dentalCoverage", False)))
            dental_tier = form_data.get("dentalTier", "employee").lower()
            dental_waived = _normalize_bool(form_data.get("dentalWaived", False))
            
            vision_coverage = _normalize_bool(form_data.get("visionEnrolled", form_data.get("visionCoverage", False)))
            vision_tier = form_data.get("visionTier", "employee").lower()
            vision_waived = _normalize_bool(form_data.get("visionWaived", False))
            
            # Extract other data
            dependents = form_data.get("dependents", [])
            effective_date = form_data.get("effectiveDate", "")
            section125_ack = _normalize_bool(form_data.get("section125Acknowledgment", False))
            irs_affirm = _normalize_bool(form_data.get("irsDependentConfirmation", False))
            has_stepchildren = _normalize_bool(form_data.get("hasStepchildren", False))
            stepchildren_names = form_data.get("stepchildrenNames", "")
            dependents_supported = _normalize_bool(form_data.get("dependentsSupported", False))
            
            # Fill Page 1 Fields
            # Personal Information
            if self._set_text_field(page1, "Employees Name Last First MI", 
                                   f"{last_name}, {first_name} {middle_initial}".strip()):
                actions.append({"field": "Employees Name", "action": "text", "pg": 1})
            
            if self._set_text_field(page1, "Social Security", self._mask_ssn(ssn, mask_all=preview)):
                actions.append({"field": "SSN", "action": "text", "pg": 1})
            
            if self._set_text_field(page1, "Birth Date", self._fmt_date(date_of_birth)):
                actions.append({"field": "Birth Date", "action": "text", "pg": 1})
            
            # Address fields
            if self._set_text_field(page1, "Employees Address", address):
                actions.append({"field": "Address", "action": "text", "pg": 1})
            
            if self._set_text_field(page1, "City", city):
                actions.append({"field": "City", "action": "text", "pg": 1})
            
            if self._set_text_field(page1, "State", state):
                actions.append({"field": "State", "action": "text", "pg": 1})
            
            if self._set_text_field(page1, "Zip", zip_code):
                actions.append({"field": "Zip", "action": "text", "pg": 1})
            
            if self._set_text_field(page1, "Phone Number", phone):
                actions.append({"field": "Phone", "action": "text", "pg": 1})
            
            if self._set_text_field(page1, "Email Address", email):
                actions.append({"field": "Email", "action": "text", "pg": 1})
            
            # Set effective date
            if self._set_text_field(page1, "Effective Date", self._fmt_date(effective_date)):
                actions.append({"field": "Effective Date", "action": "text", "pg": 1})
            
            # Set gender radio buttons
            if gender == "M":
                # First gender radio is Male
                for widget in page1.widgets():
                    if widget.field_name == "Gender" and abs(widget.rect.x0 - 523.08) < 1.0:
                        widget.field_value = True
                        widget.update()
                        actions.append({"field": "Gender", "action": "radio_M", "pg": 1})
                        break
            elif gender == "F":
                # Second gender radio is Female
                for widget in page1.widgets():
                    if widget.field_name == "Gender" and abs(widget.rect.x0 - 557.28) < 1.0:
                        widget.field_value = True
                        widget.update()
                        actions.append({"field": "Gender", "action": "radio_F", "pg": 1})
                        break
            
            # Handle Medical Coverage
            if is_waived or medical_waived:
                # Check decline boxes
                self._set_checkbox(page1, "I Decline Medical Coverage", True)
                actions.append({"field": "Medical Decline", "action": "check", "pg": 1})
            else:
                # Select medical plan tier
                medical_checkboxes = self._get_medical_tier_checkbox_name(medical_plan, medical_tier)
                for checkbox_name in medical_checkboxes:
                    if self._set_checkbox(page1, checkbox_name, True):
                        actions.append({"field": f"Medical {medical_plan} {medical_tier}", "action": "check", "pg": 1})
                        break
            
            # Handle Dental Coverage
            if dental_waived or (not dental_coverage):
                self._set_checkbox(page1, "I Decline Dental Coverage", True)
                actions.append({"field": "Dental Decline", "action": "check", "pg": 1})
            else:
                dental_checkbox = self._get_dental_tier_checkbox_name(dental_tier)
                if self._set_checkbox(page1, dental_checkbox, True):
                    actions.append({"field": f"Dental {dental_tier}", "action": "check", "pg": 1})
            
            # Handle Vision Coverage
            if vision_waived or (not vision_coverage):
                self._set_checkbox(page1, "I Decline Vision Coverage", True)
                actions.append({"field": "Vision Decline", "action": "check", "pg": 1})
            else:
                # Vision uses the same checkbox field names as dental on the PDF
                # Since we can't select both (they share field names), we prioritize dental
                # and add a text annotation for vision selection
                if not dental_coverage or dental_waived:
                    # If dental is not selected, we can use the checkboxes for vision
                    vision_checkbox = self._get_vision_tier_checkbox_name(vision_tier)
                    if self._set_checkbox(page1, vision_checkbox, True):
                        actions.append({"field": f"Vision {vision_tier}", "action": "check", "pg": 1})
                else:
                    # Both dental and vision are selected - add text note for vision
                    # This is a limitation of the PDF form structure
                    actions.append({"field": f"Vision {vision_tier}", "action": "text_note", "pg": 1})
                    warnings.append(f"Vision tier '{vision_tier}' noted but checkbox not set (conflicts with dental)")
            
            # Page 2 - Dependents
            if page2 and dependents:
                dependent_fields = [
                    ("Last Name  First  MI  Only add mailing address if different from Employee  If spouse last name differs from the Employee proof of marriage is required ie marriage license", 0),
                    ("Last Name  First  MI  Only add mailing address if different from Employee  If spouse last name differs from the Employee proof of marriage is required ie marriage licenseChild", 1),
                    ("Last Name  First  MI  Only add mailing address if different from Employee  If spouse last name differs from the Employee proof of marriage is required ie marriage licenseMedical Dental Vision", 2),
                    ("Last Name  First  MI  Only add mailing address if different from Employee  If spouse last name differs from the Employee proof of marriage is required ie marriage licenseMedical Dental Vision_2", 3)
                ]
                
                for idx, dep in enumerate(dependents[:4]):  # Max 4 dependents on form
                    if idx < len(dependent_fields):
                        field_name, _ = dependent_fields[idx]
                        dep_name = f"{dep.get('lastName', '')}, {dep.get('firstName', '')} {dep.get('middleInitial', '')}".strip()
                        if dep.get('relationship'):
                            dep_name += f" ({dep['relationship']})"
                        
                        if self._set_text_field(page2, field_name, dep_name):
                            actions.append({"field": f"Dependent{idx+1} Name", "action": "text", "pg": 2})
                        
                        # Set DOB
                        dob_field = f"Date of Birth" if idx == 0 else f"Date of Birth_{idx}"
                        if self._set_text_field(page2, dob_field, self._fmt_date(dep.get('dateOfBirth', ''))):
                            actions.append({"field": f"Dependent{idx+1} DOB", "action": "text", "pg": 2})
                        
                        # Set SSN
                        ssn_field = f"SSN required" if idx == 0 else f"SSN required_{idx}"
                        if self._set_text_field(page2, ssn_field, self._mask_ssn(dep.get('ssn', ''), mask_all=preview)):
                            actions.append({"field": f"Dependent{idx+1} SSN", "action": "text", "pg": 2})
                        
                        # Set coverage checkboxes for this dependent
                        coverage_type = dep.get('coverageType', {})
                        base_idx = idx * 3  # Each dependent has 3 checkboxes (Medical, Dental, Vision)
                        
                        medical_cb = f"Medical" if idx == 0 else f"Medical_{idx}"
                        if coverage_type.get('medical', False):
                            self._set_checkbox(page2, medical_cb, True)
                            
                        dental_cb = f"Dental" if idx == 0 else f"Dental_{idx}"
                        if coverage_type.get('dental', False):
                            self._set_checkbox(page2, dental_cb, True)
                            
                        vision_cb = f"Vision" if idx == 0 else f"Vision_{idx}"
                        if coverage_type.get('vision', False):
                            self._set_checkbox(page2, vision_cb, True)
                
                if len(dependents) > 4:
                    warnings.append(f"Form supports max 4 dependents. {len(dependents) - 4} additional dependents not shown.")
            
            # IRS Affirmations on Page 2
            if page2:
                # IRS Section 152 affirmation
                if irs_affirm:
                    # First radio button is YES
                    for widget in page2.widgets():
                        if widget.field_name == "I affirm that all dependents listed meet the IRS Section 152 definition of dependent so that premiums can be paid with pretax dollars if applicable":
                            if abs(widget.rect.x0 - 519.12) < 1.0:  # YES button
                                widget.field_value = True
                                widget.update()
                                actions.append({"field": "IRS Affirmation", "action": "radio_yes", "pg": 2})
                                break
                
                # Dependent support question
                if dependents_supported:
                    # First radio is YES
                    for widget in page2.widgets():
                        if widget.field_name == "Are they dependent on you for support and maintenance":
                            if abs(widget.rect.x0 - 222.96) < 1.0:  # YES button
                                widget.field_value = True
                                widget.update()
                                actions.append({"field": "Dependent Support", "action": "radio_yes", "pg": 2})
                                break
                
                # Stepchildren
                if has_stepchildren:
                    self._set_checkbox(page2, "Yes", True)
                    self._set_text_field(page2, "If yes indicate names", stepchildren_names[:100])
                    actions.append({"field": "Stepchildren", "action": "yes", "pg": 2})
                else:
                    self._set_checkbox(page2, "No_2", True)
                    actions.append({"field": "Stepchildren", "action": "no", "pg": 2})
                
                # Signature date
                if signed_date:
                    self._set_text_field(page2, "Date", self._fmt_date(signed_date))
                    actions.append({"field": "Signature Date", "action": "text", "pg": 2})
                
                # Handle signature image if provided
                if not preview and signature_b64:
                    try:
                        sig_img = _load_signature_image(signature_b64)
                        if sig_img is not None:
                            # The signature field location
                            sig_rect = fitz.Rect(188.28, 615.6, 486.0, 652.92)
                            
                            # Convert image to bytes
                            img_buffer = io.BytesIO()
                            sig_img.save(img_buffer, format='PNG')
                            img_buffer.seek(0)
                            
                            # Insert the image
                            page2.insert_image(sig_rect, stream=img_buffer.read())
                            actions.append({"field": "Signature", "action": "image", "pg": 2})
                    except Exception as e:
                        warnings.append(f"Could not add signature: {str(e)}")
            
            # Save the modified PDF
            pdf_buffer = io.BytesIO()
            doc.save(pdf_buffer)
            pdf_bytes = pdf_buffer.getvalue()
            
            if return_details:
                return pdf_bytes, warnings, actions
            return pdf_bytes
            
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")
        finally:
            doc.close()
    
    def _get_medical_tier_checkbox_name(self, medical_plan: str, tier: str) -> List[str]:
        """Get the checkbox field names for medical plan and tier."""
        # Normalize tier
        tier_map = {
            'employee': 'Employee Only',
            'employee_spouse': 'Employee  Spouse',
            'employee_children': 'Employee  Children',
            'family': 'Employee  Family'
        }
        
        tier_name = tier_map.get(tier, 'Employee Only')
        
        # Determine which row based on plan (frontend sends hra6k, hra4k, hra2k)
        if medical_plan in ['hra6k', 'hra_6k']:
            # First row - HRA $6K
            if tier == 'employee':
                return ["Employee Only  5991"]
            elif tier == 'employee_spouse':
                return ["Employee  Spouse"]
            elif tier == 'employee_children':
                return ["Employee  Children"]
            elif tier == 'family':
                return ["Employee  Family"]
        elif medical_plan in ['hra4k', 'hra_4k']:
            # Second row - HRA $4K
            if tier == 'employee':
                return ["Employee Only  13684"]
            elif tier == 'employee_spouse':
                return ["Employee  Spouse 39621"]
            elif tier == 'employee_children':
                return ["Employee  Children_2"]
            elif tier == 'family':
                return ["Employee  Family_2"]
        elif medical_plan in ['hra2k', 'hra_2k']:
            # Third row - HRA $2K
            if tier == 'employee':
                return ["Employee Only"]
            elif tier == 'employee_spouse':
                return ["Employee  Spouse_2"]
            elif tier == 'employee_children':
                return ["Employee  Children_3"]
            elif tier == 'family':
                return ["Employee  Family_3"]
        elif medical_plan in ['minimum_essential', 'mec']:
            # Limited Medical - MEC (first row)
            if tier == 'employee':
                return ["Employee Only_2"]
            elif tier == 'employee_spouse':
                return ["Employee  Spouse_3"]
            elif tier == 'employee_children':
                return ["Employee  Children_4"]
            elif tier == 'family':
                return ["Employee  Family_4"]
        elif medical_plan in ['indemnity']:
            # Limited Medical - Indemnity (second row)
            if tier == 'employee':
                return ["Employee Only_3"]
            elif tier == 'employee_spouse':
                return ["Employee  Spouse_4"]
            elif tier == 'employee_children':
                return ["Employee  Children_5"]
            elif tier == 'family':
                return ["Employee  Family_5"]
        
        # Default fallback
        return [tier_name]
    
    def _get_dental_tier_checkbox_name(self, tier: str) -> str:
        """Get the checkbox field name for dental tier."""
        tier_map = {
            'employee': 'Employee Only_6',
            'employee_spouse': 'Employee  Spouse_7',
            'employee_children': 'Employee  Children_8',
            'family': 'Employee  Family_8'
        }
        return tier_map.get(tier, 'Employee Only_6')
    
    def _get_vision_tier_checkbox_name(self, tier: str) -> str:
        """Get the checkbox field name for vision tier.
        Note: These are the same as dental checkboxes in the PDF."""
        tier_map = {
            'employee': 'Employee Only_6',
            'employee_spouse': 'Employee  Spouse_7',
            'employee_children': 'Employee  Children_8',
            'family': 'Employee  Family_8'
        }
        return tier_map.get(tier, 'Employee Only_6')