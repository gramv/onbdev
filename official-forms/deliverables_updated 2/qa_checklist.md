# QA Checklist – HI Form Fillable Conversion

| Requirement | Verification Procedure | Result |
|---|---|---|
| **Pixel‑perfect placement** | Visually inspected the filled PDF generated via `sample_data.json`. All form fields align with the printed lines and boxes on the original form. Text fields do not overlap the labels or lines; checkboxes/radio buttons sit inside the printed check boxes (e.g., coverage elections and dependent coverage). | ✅ Passed |
| **No overlap of fields with printed text/boxes** | Checked every field’s rectangle coordinates to ensure at least 2 pt of padding from printed lines. In the sample render no field obscured any printed label or border. | ✅ Passed |
| **Field sizes** | Text fields are ~12–14 pt high; radio/checkbox hit‑areas are ≥10 pt square. Signature field spans the signature line. | ✅ Passed |
| **Tab order follows reading order** | Fields were added sequentially according to the specified reading order (meta header → Reason for Request → Personal Info → Coverage sections → Dependents → Stepchildren/IRS → Signature). A manual check of the tab order in Acrobat confirms that focus moves left‑to‑right and top‑to‑bottom through the form. | ✅ Passed |
| **Radio/checkbox exclusivity logic** | Added JavaScript actions to each Decline checkbox to clear its corresponding radio group when checked, and to each radio button to uncheck its Decline checkbox upon selection. This ensures mutual exclusivity for Medical, Limited Medical, Dental and Vision elections, as well as the dependent action selections. | ✅ Passed |
| **Format validations** | Applied Adobe standard date validation scripts (`AFDate_FormatEx("mm/dd/yyyy")`) and keystroke scripts to all date fields. SSN, phone, ZIP and email fields use custom keystroke/format scripts enforcing the specified regex patterns (e.g., `^\d{3}-?\d{2}-?\d{4}$` for SSN). Dependent SSN fields share the same mask. | ✅ Passed |
| **Tooltips for accessibility** | Set the `field_label` (tooltip/alternate text) of each field to the printed label (e.g., “Effective Date”, “Employee Phone Number”). Screen readers will announce meaningful labels rather than internal IDs. | ✅ Passed |
| **Radio export values** | For every radio group the export values are defined exactly as specified (e.g., `H6K_EO`, `MEC_ES`, `PPO_EC`, `VIS_EF`, `ENROLL`, `CANCEL`, `CHANGE`, etc.) in `fieldmap.json` and in the AcroForm fields. | ✅ Passed |
| **Signature field** | Inserted an Acrobat‐compatible signature field (`employee_signature`) spanning the signature line. Tested in Acrobat to ensure signatures can be applied without altering field layout. | ✅ Passed |
| **Dependents section** | Added four complete dependent rows (Spouse/Child) with action radio buttons, coverage checkboxes, name fields, gender radio buttons, DOB and SSN fields, and an optional address field. Verified that sample data populates correctly and aligns with the blank lines. | ✅ Passed |
| **Conditional show/hide** | Implemented scripts to show/hide the New Hire date and Qualifying Event description/date fields based on the selected Reason for Request. | ✅ Passed |
| **Sample data populates cleanly** | Filled the form using `sample_data.json` and flattened it. All fields display the sample values cleanly without truncation. Decline/selection logic behaved as expected. | ✅ Passed |

**Summary:** The converted PDF meets all layout, validation, accessibility and logic requirements. Tab order matches the reading order and the form behaves like a native Acrobat form. The accompanying `fieldmap.json`, `qa_checklist.md` and `sample_data.json` provide a complete record of field definitions and testing.  

