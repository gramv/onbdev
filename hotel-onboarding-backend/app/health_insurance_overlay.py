from __future__ import annotations

import base64
import io
import os
import json
from typing import Any, Dict, List, Optional, Tuple, Union

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


def _center_text_in_rect(page: fitz.Page, rect: fitz.Rect, text: str, font_size: float = 10.5) -> None:
    # Use PyMuPDF utility to measure text width
    text_width = fitz.get_text_length(text, fontsize=font_size, fontname="helv")
    x = rect.x0 + (rect.width - text_width) / 2
    y = rect.y0 + (rect.height - font_size) / 2 + font_size
    page.insert_text((x, y), text, fontsize=font_size, color=(0, 0, 0))


def _draw_x_in_checkbox(page: fitz.Page, rect: fitz.Rect, font_size: float = 10.5) -> None:
    _center_text_in_rect(page, rect, "X", font_size=font_size)


def _draw_text_left(page: fitz.Page, rect: fitz.Rect, text: str, font_size: float = 9.0, pad: float = 1.0) -> None:
    # Left aligned with small padding, vertically near baseline
    x = rect.x0 + pad
    y = rect.y1 - pad
    page.insert_text((x, y), text, fontsize=font_size, color=(0, 0, 0))


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


def _pick_checkboxes_for_section(widgets: List[Dict[str, Any]], name_contains: str, y_min: float, y_max: float) -> List[Tuple[str, fitz.Rect, int]]:
    picks: List[Tuple[str, fitz.Rect, int]] = []
    for w in widgets:
        nm = (w.get("name") or "").strip()
        if name_contains.lower() in nm.lower():
            y0 = float(w["rect"][1])
            if y_min <= y0 <= y_max:
                rect = fitz.Rect(*w["rect"])
                picks.append((nm, rect, int(w["pg"])) )
    return picks


def _extract_widgets(doc: fitz.Document) -> List[Dict[str, Any]]:
    widgets: List[Dict[str, Any]] = []
    for page in doc:
        for w in page.widgets() or []:
            widgets.append({
                "name": w.field_name,
                "type": getattr(w, 'field_type_string', str(getattr(w, 'field_type', ''))),
                "rect": [round(w.rect.x0, 2), round(w.rect.y0, 2), round(w.rect.x1, 2), round(w.rect.y1, 2)],
                "pg": page.number + 1,
            })
    return widgets


class HealthInsuranceFormOverlay:
    """Overlay selections onto the official HI Form_final3.pdf template.

    Strategy:
      - Always draw visible overlays (text/X) instead of setting field values, so all viewers show them.
      - Use coarse y-bands to associate tier checkboxes with sections (medical vs dental). Vision appears to only have decline.
      - Support preview (no signature) and final (with signature/date text if provided).
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
            from datetime import datetime
            return datetime.now().strftime('%m/%d/%Y')
        try:
            from datetime import datetime
            # Try ISO
            return datetime.fromisoformat(date_str.replace('Z','+00:00')).strftime('%m/%d/%Y')
        except Exception:
            # fallback pass-through
            return date_str

    def generate(self, form_data: Dict[str, Any], employee_first: str, employee_last: str,
                 signature_b64: Optional[str] = None, signed_date: Optional[str] = None,
                 preview: bool = True, return_details: bool = False) -> Union[bytes, Tuple[bytes, List[str], List[Dict[str, Any]]]]:

        doc = fitz.open(HI_TEMPLATE_PATH)
        try:
            page1 = doc[0]
            widgets = _extract_widgets(doc)
            # Load authoritative mapping (no heuristics)
            with open(HI_MAPPING_PATH, 'r') as f:
                mapping: Dict[str, Any] = json.load(f)

            # Header/boxes: use mapped rects for employee name/date boxes
            actions: List[Dict[str, Any]] = []
            warnings: List[str] = []
            emp_map = mapping.get("employee", {})
            if emp_map.get("name_box"):
                nb = emp_map["name_box"]
                rect = fitz.Rect(*nb["rect"]) if isinstance(nb.get("rect"), list) else fitz.Rect(*nb)
                _draw_text_left(page1, rect, f"{employee_first} {employee_last}", font_size=10)
                actions.append({"field": "employee_name", "action": "text", "pg": nb.get("pg", 1)})
            if emp_map.get("date_box"):
                db = emp_map["date_box"]
                rect = fitz.Rect(*db["rect"]) if isinstance(db.get("rect"), list) else fitz.Rect(*db)
                _draw_text_left(page1, rect, self._fmt_date(signed_date), font_size=10)
                actions.append({"field": "employee_date", "action": "text", "pg": db.get("pg", 1)})

            # Read FE data
            is_waived = _normalize_bool(form_data.get("isWaived", False))
            medical_tier = (form_data.get("medicalTier") or form_data.get("medical_tier") or "employee").lower()
            dental_on = _normalize_bool(form_data.get("dentalCoverage", False))
            dental_tier = (form_data.get("dentalTier") or form_data.get("dental_tier") or "employee").lower()
            vision_on = _normalize_bool(form_data.get("visionCoverage", False))
            # Personal info - check nested structure first, then flat structure
            personal_info = form_data.get("personalInfo", {})
            address = (personal_info.get("address") or form_data.get("address") or "").strip()
            city = (personal_info.get("city") or form_data.get("city") or "").strip()
            state = (personal_info.get("state") or form_data.get("state") or "").strip()
            zip_code = (
                personal_info.get("zip")
                or personal_info.get("zip_code")
                or personal_info.get("zipCode")
                or form_data.get("zip")
                or form_data.get("zip_code")
                or form_data.get("zipCode")
                or ""
            ).strip()
            phone = (personal_info.get("phone") or personal_info.get("phone_number") or form_data.get("phone") or form_data.get("phone_number") or "").strip()
            email = (personal_info.get("email") or form_data.get("email") or "").strip()
            gender = (personal_info.get("gender") or form_data.get("gender") or "").strip().upper()
            dependents = form_data.get("dependents") or []
            irs_affirm = _normalize_bool(form_data.get("irsDependentConfirmation", False))
            has_stepchildren = _normalize_bool(form_data.get("hasStepchildren", False))
            dependents_supported = _normalize_bool(form_data.get("dependentsSupported", False))
            stepchildren_names = (form_data.get("stepchildrenNames") or "").strip()

            # Personal info mapped placements
            def _from_field(fdef: Dict[str, Any]) -> Tuple[fitz.Rect, int]:
                if 'rect' in fdef:
                    return fitz.Rect(*fdef['rect']), int(fdef.get('pg', 1))
                # direct widget entry
                return fitz.Rect(*fdef['rect']), int(fdef['pg'])

            # Removed duplicate field population - handled by fill_text_by_exact() calls below

            # Decline checkboxes from mapping
            def _check_first(entries: List[Dict[str, Any]], label: str):
                if entries:
                    fdef = entries[0]
                    rect, pg = fitz.Rect(*fdef['rect']), int(fdef['pg'])
                    _draw_x_in_checkbox(doc[pg - 1], rect)
                    actions.append({"field": label, "action": "check", "pg": pg})

            if is_waived:
                _check_first(mapping.get("medical", {}).get("decline", []), "medical_decline")
            if not dental_on:
                _check_first(mapping.get("dental", {}).get("decline", []), "dental_decline")
            if not vision_on:
                _check_first(mapping.get("vision", {}).get("decline", []), "vision_decline")

            # Tier selection heuristics by Y bands
            # Medical/Dental tiers from mapping
            def _check_tier(section: str, tier: str, row_index: int = 0):
                sec = mapping.get(section, {})
                tlist = (sec.get("tiers", {}) or {}).get(tier, [])
                if tlist:
                    idx = min(max(int(row_index), 0), len(tlist) - 1)
                    fdef = tlist[idx]
                    rect, pg = fitz.Rect(*fdef['rect']), int(fdef['pg'])
                    _draw_x_in_checkbox(doc[pg - 1], rect)
                    actions.append({"field": f"{section}:{tier}", "action": "check", "pg": pg})
            if not is_waived:
                # Determine if UHC or ACI plan
                medical_plan = (form_data.get("medicalPlan") or form_data.get("medical_plan") or "").lower()
                is_aci_plan = medical_plan in ['minimum_essential', 'indemnity', 'minimum_indemnity', 
                                                'aci_minimum', 'aci_indemnity', 'aci_minimum_indemnity',
                                                'minimum_essential_indemnity']
                
                if is_aci_plan:
                    # Use limited_medical section for ACI plans
                    aci_row = {
                        'minimum_essential': 0, 
                        'aci_minimum': 0,
                        'indemnity': 1,
                        'aci_indemnity': 1, 
                        'minimum_indemnity': 2,
                        'aci_minimum_indemnity': 2,
                        'minimum_essential_indemnity': 2
                    }.get(medical_plan, 0)
                    _check_tier("limited_medical", medical_tier, row_index=aci_row)
                else:
                    # Use existing medical section for UHC HRA plans
                    hra_row = {"hra_6k": 0, "hra_4k": 1, "hra_2k": 2}.get(medical_plan, 0)
                    _check_tier("medical", medical_tier, row_index=hra_row)
            if dental_on:
                _check_tier("dental", dental_tier)

            # Vision tier selection
            if vision_on:
                vision_tier = (form_data.get("visionTier") or form_data.get("vision_tier") or "employee").lower()
                _check_tier("vision", vision_tier)

            # Place personal info fields on page 1 using exact rectangles from widget map
            def fill_text_by_exact(name_contains: str, value: str):
                if not value:
                    return
                matches = [(fitz.Rect(*w["rect"]), w["pg"]) for w in widgets if (w.get("name") or "").strip() == name_contains]
                if matches:
                    rect, pg = matches[0]
                    doc[pg - 1].insert_text((rect.x0 + 1, rect.y1 - 2), value, fontsize=9, color=(0, 0, 0))
                    actions.append({"field": name_contains, "action": "text", "pg": pg})

            def fill_text_with_fallback(map_key: str, widget_name: str, value: str):
                if not value:
                    return
                # Try widget match first
                matches = [(fitz.Rect(*w["rect"]), w["pg"]) for w in widgets if (w.get("name") or "").strip() == widget_name]
                if matches:
                    rect, pg = matches[0]
                    doc[pg - 1].insert_text((rect.x0 + 1, rect.y1 - 2), value, fontsize=9, color=(0, 0, 0))
                    actions.append({"field": widget_name, "action": "text", "pg": pg})
                    return
                # Fallback to mapping rectangle if provided
                emp_map = mapping.get("employee", {})
                fdef = emp_map.get(map_key)
                if fdef and fdef.get("rect"):
                    rect = fitz.Rect(*fdef["rect"]) if isinstance(fdef.get("rect"), list) else fitz.Rect(*fdef)
                    pg = int(fdef.get("pg", 1))
                    doc[pg - 1].insert_text((rect.x0 + 1, rect.y1 - 2), value, fontsize=9, color=(0, 0, 0))
                    actions.append({"field": map_key, "action": "text_map", "pg": pg})

            fill_text_with_fallback("address", "Employees Address", address)
            fill_text_with_fallback("city", "City", city)
            fill_text_with_fallback("state", "State", state)
            fill_text_with_fallback("zip", "Zip", zip_code)
            fill_text_with_fallback("phone", "Phone Number", phone)
            fill_text_with_fallback("email", "Email Address", email)

            # Additional personal fields on Page 1 top row: Name, SSN, Birth Date
            try:
                # Name formatted as "Last, First MI" if possible - check nested structure first
                personal_info = form_data.get("personalInfo", {})
                mi = (personal_info.get("middleInitial") or personal_info.get("middle_initial") or form_data.get("middleInitial") or form_data.get("middle_initial") or "").strip()
                name_line = f"{employee_last or ''}, {employee_first or ''}{(' ' + mi) if mi else ''}"
                name_line = name_line.strip().strip(',')
                if name_line:
                    fill_text_by_exact("Employees Name Last First MI", name_line)
            except Exception:
                pass
            try:
                # SSN - check nested structure first
                personal_info = form_data.get("personalInfo", {})
                ssn_value = personal_info.get("ssn") or form_data.get("ssn") or ""
                if ssn_value:
                    fill_text_by_exact("Social Security", self._mask_ssn(ssn_value, mask_all=True if preview else False))
            except Exception:
                pass
            try:
                # Date of Birth - check nested structure first
                personal_info = form_data.get("personalInfo", {})
                dob_raw = personal_info.get("dateOfBirth") or personal_info.get("date_of_birth") or form_data.get("dateOfBirth") or form_data.get("date_of_birth")
                if dob_raw:
                    fill_text_by_exact("Birth Date", self._fmt_date(dob_raw))
            except Exception:
                pass

            # Gender radios: two widgets for Gender band (M/F). Place X in appropriate position (centered).
            gender_M = [(fitz.Rect(*w["rect"]), w["pg"]) for w in widgets if (w.get("name") or "").strip() == "Gender" and abs(float(w["rect"][0]) - 523.08) < 1.0]
            gender_F = [(fitz.Rect(*w["rect"]), w["pg"]) for w in widgets if (w.get("name") or "").strip() == "Gender" and abs(float(w["rect"][0]) - 557.28) < 1.5]
            if gender in {"M", "MALE"} and gender_M:
                r, pg = gender_M[0]
                _draw_x_in_checkbox(doc[pg - 1], r, font_size=9)
                actions.append({"field": "gender", "action": "radio_M", "pg": pg})
            elif gender in {"F", "FEMALE"} and gender_F:
                r, pg = gender_F[0]
                _draw_x_in_checkbox(doc[pg - 1], r, font_size=9)
                actions.append({"field": "gender", "action": "radio_F", "pg": pg})

            # Affirmations from mapping
            def _radio_pair(entries: List[Dict[str, Any]], yes: bool, label: str):
                if len(entries) >= 2:
                    yes_def, no_def = entries[0], entries[1]
                    target = yes_def if yes else no_def
                    rect, pg = fitz.Rect(*target['rect']), int(target['pg'])
                    _draw_x_in_checkbox(doc[pg - 1], rect, font_size=9)
                    actions.append({"field": label, "action": "radio_yes" if yes else "radio_no", "pg": pg})
            aff = mapping.get("affirmations", {})
            _radio_pair(aff.get("irs_yes_no", []), irs_affirm, "irs_affirmation")
            _radio_pair(aff.get("support_yes_no", []), dependents_supported, "dependent_support")
            # Stepchildren yes/no
            if has_stepchildren:
                step_entries = aff.get("step_yes", [])
            else:
                step_entries = aff.get("step_no", [])
            if step_entries:
                fdef = step_entries[0]
                rect, pg = fitz.Rect(*fdef['rect']), int(fdef['pg'])
                _draw_x_in_checkbox(doc[pg - 1], rect, font_size=9)
                actions.append({"field": "stepchildren", "action": "radio", "pg": pg})

            # Stepchildren names text if provided
            if stepchildren_names and aff.get("step_names"):
                fdef = aff["step_names"][0]
                rect, pg = fitz.Rect(*fdef['rect']), int(fdef['pg'])
                _draw_text_left(doc[pg - 1], rect, stepchildren_names[:40])
                actions.append({"field": "stepchildren_names", "action": "text", "pg": pg})

            # Dependents (first three lines if present)
            if dependents:
                rows = mapping.get("dependents", {}).get("rows", [])
                for idx, dep in enumerate(dependents[:len(rows) ]):
                    row_map = rows[idx]
                    full_name = f"{(dep.get('lastName') or dep.get('last_name') or '').strip()} {(dep.get('firstName') or dep.get('first_name') or '').strip()} {(dep.get('middleInitial') or dep.get('middle_initial') or '').strip()}".strip()
                    dep_dob = dep.get("dateOfBirth") or dep.get("dob") or ""
                    dep_ssn = self._mask_ssn(dep.get("ssn") or "", mask_all=True if preview else False)
                    # Name
                    nrect, pg = fitz.Rect(*row_map['name']), int(row_map['pg'])
                    _draw_text_left(doc[pg - 1], nrect, full_name[:40])
                    actions.append({"field": "dependent_name", "row": idx + 1, "pg": pg})
                    # DOB
                    drect = fitz.Rect(*row_map['dob'])
                    _draw_text_left(doc[pg - 1], drect, self._fmt_date(dep_dob))
                    actions.append({"field": "dependent_dob", "row": idx + 1, "pg": pg})
                    # SSN
                    srect = fitz.Rect(*row_map['ssn'])
                    _draw_text_left(doc[pg - 1], srect, dep_ssn)
                    actions.append({"field": "dependent_ssn", "row": idx + 1, "pg": pg})
                if len(dependents) > len(rows):
                    warnings.append("More dependents than available lines; overflow page not yet rendered")

            # Signature on page 2 if provided and not preview
            if not preview and signature_b64:
                try:
                    sig_img = _load_signature_image(signature_b64)
                    if sig_img is not None:
                        page2 = doc[1] if doc.page_count >= 2 else page1
                        sig_map = mapping.get("signature", {})
                        sig_rect = fitz.Rect(*sig_map.get("rect", {}).get("rect", [188.28, 615.6, 486.0, 652.92]))
                        # Fit into rect while keeping aspect
                        img_w, img_h = sig_img.size
                        rect_w, rect_h = sig_rect.width, sig_rect.height
                        scale = min(rect_w / img_w, rect_h / img_h)
                        draw_w, draw_h = img_w * scale, img_h * scale
                        draw_x0 = sig_rect.x0 + (rect_w - draw_w) / 2
                        draw_y0 = sig_rect.y0 + (rect_h - draw_h) / 2
                        draw_rect = fitz.Rect(draw_x0, draw_y0, draw_x0 + draw_w, draw_y0 + draw_h)
                        out_buf = io.BytesIO()
                        sig_img.save(out_buf, format='PNG')
                        out_buf.seek(0)
                        page2.insert_image(draw_rect, stream=out_buf.getvalue(), keep_proportion=False)
                        if signed_date:
                            date_rect_def = sig_map.get("date")
                            if date_rect_def:
                                drect = fitz.Rect(*date_rect_def['rect'])
                                _draw_text_left(page2, drect, self._fmt_date(signed_date), font_size=10)
                            actions.append({"field": "signature_date", "action": "text", "pg": (2 if doc.page_count>=2 else 1)})
                except Exception:
                    pass

            # Warnings based on completeness
            if not (employee_first and employee_last):
                warnings.append("Employee name missing")
            if is_waived is False and medical_tier == "":
                warnings.append("Medical tier missing")
            if dependents and not irs_affirm:
                warnings.append("IRS affirmation not checked with dependents present")

            # Export PDF bytes
            try:
                pdf_bytes = doc.tobytes()
            except Exception:
                # Fallback for older PyMuPDF versions
                pdf_bytes = doc.write()
            if return_details:
                return pdf_bytes, warnings, actions
            return pdf_bytes
        finally:
            doc.close()


