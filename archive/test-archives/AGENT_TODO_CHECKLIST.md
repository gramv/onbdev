## Agent Execution TODO Playbook (HR/Manager/Candidate Flow)

Purpose: A self-contained, durable checklist to complete/verify the end-to-end QR → Application → Approval → Onboarding → Manager I‑9 Sec.2 → HR Final Approval flow. Use this document without relying on chat context.

### Quick Start Commands
- Backend (FastAPI):
  - Create venv/install: `cd hotel-onboarding-backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
  - Run dev server: `python3 -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8000 --reload`
  - Key tests: `python3 test_property_access_control_comprehensive.py`, `python3 test_tasks_1_2_3_integration.py`, `python3 test_websocket_basic.py`
- Frontend (React + Vite):
  - `cd hotel-onboarding-frontend && npm install && npm run dev`

### Required Environment Variables (Backend)
- `JWT_SECRET_KEY` (HS256 signing)
- `JWT_ACCESS_TOKEN_EXPIRE_HOURS` (default 72)
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (server/admin client), `SUPABASE_ANON_KEY`
- `FRONTEND_URL` (used by QR service to build application links; e.g., `http://localhost:3000`)

---

### High-Level Flow (Target State)
1) Candidate scans property QR → lands on `GET /properties/{id}/info` and submits application `POST /apply/{propertyId}`.
2) Manager reviews property-scoped applications → approves or moves to talent pool.
3) On approval: Employee record + onboarding session created; 7‑day token link generated and sent.
4) Candidate completes onboarding via token (save/complete per step) and submits (employee phase complete).
5) Manager completes I‑9 Section 2 and moves session to HR.
6) HR performs final approval; notifications emitted; audit trail recorded.

---

### PRIO 0: Fix/Implement Critical Endpoints and Mismatches

- [ ] QR Code Generation (backend endpoint + env-driven base URL)
  - Files: `hotel-onboarding-backend/app/main_enhanced.py`, `hotel-onboarding-backend/app/qr_service.py`
  - Implement: `POST /hr/properties/{property_id}/qr-code` (exists only in a backup file now)
    - Auth: HR or Manager assigned to property
    - Response: `{ qr_code_url, printable_qr_url, application_url, property_id, generated_at }`
  - Update `qr_service.py` to use `os.getenv('FRONTEND_URL', 'http://localhost:3000')` instead of hardcoded URL
  - Acceptance:
    - Frontend `QRCodeDisplay` in `src/components/ui/qr-code-display.tsx` shows/prints/downloads QR
    - Tests referencing this endpoint pass (e.g., `test_qr_api.py`, `test_task1_qr_generation.py`)

- [ ] Application Submission (complete duplicate-prevention + route consistency)
  - Files: `app/main_enhanced.py` (endpoint `POST /apply/{id}`), `frontend/src/pages/JobApplicationFormV2.tsx`
  - Complete duplicate check (currently loop early exit is missing action) to block same `(email, property_id, position)` pending duplicate
  - Ensure response includes `application_id`, `status: 'pending'`
  - Emit WebSocket event `application_submitted` with `{application_id, property_id, applicant_name}`
  - Acceptance: JobApplicationFormV2 submits to `/api/apply/{propertyId}` and shows success; server logs show no duplicates created

- [ ] Manager Approval (finish approve; fix reject)
  - Files: `app/main_enhanced.py`, `app/supabase_service_enhanced.py`, `app/services/onboarding_orchestrator.py`
  - Approve: `POST /applications/{id}/approve`
    - Steps: get application → set status approved → create employee → create onboarding session (see Service/Orchestrator alignment below) → generate onboarding URL `FRONTEND_URL/onboard?token=...`
    - Emit `application_approved` and optionally send notification/email
  - Reject: `POST /applications/{id}/reject-enhanced`
    - Fix undefined `property_ids` reference; allow `talent_pool` vs `rejected` per request
  - Acceptance: Applications move to approved/talent_pool; real-time dashboard updates; audit trail entries created

---

### PRIO 1: Onboarding Session APIs (needed by OnboardingFlowController)

- [ ] Validate Token
  - Route: `POST /onboarding/validate-token` body `{ token }`
  - Response: `{ valid, session: { id, employee, property, current_step, expires_at } }`
  - Auth: public (token-based)

- [ ] Get Session
  - Route: `GET /onboarding/session?token=...`
  - Response: same shape as validate-token (for initial load)

- [ ] Save Step
  - Route: `POST /onboarding/step/{step_id}/save`
  - Body: `{ token, data }`
  - Action: `onboarding_orchestrator.update_step_progress(session_id, step, data)` without moving to next step

- [ ] Complete Step
  - Route: `POST /onboarding/step/{step_id}/complete`
  - Body: `{ token, data?, signature_data? }`
  - Action: store data/signature; update step; auto-transition when phase-complete

- [ ] Submit (complete employee phase)
  - Route: `POST /onboarding/submit`
  - Body: `{ token }`
  - Action: `onboarding_orchestrator.complete_employee_phase(session_id)`; emit `onboarding_completed` (employee phase) and notify manager

- [ ] Wire WebSocket events for: `onboarding_started`, `form_submitted`, `document_uploaded`, `onboarding_completed`

- [ ] Acceptance
  - `OnboardingFlowPortal` loads with token, navigates steps, saves/advances, and submits successfully
  - All calls succeed without 404; WebSocket toasts appear in dashboards

---

### PRIO 2: Service/Orchestrator Alignment

- [ ] Align `OnboardingOrchestrator` and `EnhancedSupabaseService`
  - Current mismatch: Orchestrator calls `supabase_service.create_onboarding_session(session_obj)` while the service implements `create_onboarding_session(employee_id: str, expires_hours=...)`
  - Decide ONE interface:
    - Option A (preferred): Service accepts a full `OnboardingSession` model and persists; returns created session (with token)
    - Option B: Orchestrator calls service `(employee_id, expires_hours)` and then updates as needed
  - Update all callers accordingly (manager approval flow)
  - Acceptance: Manager approval creates a persisted session; token resolves in `validate-token`

---

### PRIO 3: Manager I‑9 Section 2 Wiring (Frontend → Backend)

- [ ] Frontend: add API and call flow
  - Add in `frontend/src/services/api.ts`: `manager.completeI9Section2(sessionId, data)` → `POST /api/manager/onboarding/{session_id}/i9-section2`
  - Update `EnhancedManagerDashboard.tsx`: on modal submit, POST data, handle success → close modal → trigger refresh; optionally emit WS action

- [ ] Backend: verify endpoint and transitions
  - `POST /api/manager/onboarding/{session_id}/i9-section2` exists; validate required fields based on List A vs List B+C
  - On success, update step data/signature and call `complete_manager_phase(session_id)`

- [ ] Acceptance: Manager completes I‑9 Sec.2 and session moves to HR approval; dashboard reflects change

---

### PRIO 4: HR Final Approval (UI + Backend glue)

- [ ] Frontend UI flow
  - Add HR view for pending approvals using `GET /api/hr/onboarding/pending`
  - On approve, call `POST /api/hr/onboarding/{session_id}/approve` with signature metadata

- [ ] Backend checks
  - Ensure endpoint verifies `OnboardingStatus.HR_APPROVAL` before approval; stores signature; calls `approve_onboarding` and emits completion notification

- [ ] Acceptance: HR can approve; onboarding marked approved; notifications/audit logged

---

### PRIO 5: WebSockets + Notifications on Key Events

- [ ] Emit events in these places:
  - Application submitted → `broadcast_onboarding_event('application_submitted', ...)`
  - Application approved/rejected → `application_approved`/`application_rejected`
  - Onboarding phase transitions and step saves as applicable

- [ ] NotificationService integration
  - On HR final approval, send in-app (and optional email) notifications to manager/employee

- [ ] Acceptance: Manager/HR dashboards receive real-time toasts for the above

---

### PRIO 6: Audit Logging Consistency

- [ ] Fix table name mismatch
  - In `supabase_service_enhanced.log_audit_event`, write to `audit_logs` (plural) per migration `003_create_audit_logs_table.sql`

- [ ] Use audit helper consistently on:
  - Application create/approve/reject; Onboarding session create/update; HR approval; I‑9 Sec.2 completion

- [ ] Acceptance: Audit rows appear for all critical actions; no insert errors

---

### PRIO 7: API Path Consistency (Frontend ↔ Backend)

- [ ] Align `frontend/src/services/api.ts` with actual backend routes
  - Replace stale manager endpoints (`/manager/applications/{id}/approve`) with `/applications/{id}/approve`
  - Add onboarding endpoints listed above
  - Ensure Vite proxy `/api` maps to backend root; adjust paths accordingly

- [ ] Acceptance: No 404s from API mismatch in app usage

---

### PRIO 8: Token Regeneration API

- [ ] Implement: `POST /api/hr/onboarding/{session_id}/regenerate-token`
  - Returns new token and updates `onboarding_tokens`/session expiry; logs audit; emits notification to manager
  - Acceptance: Expired session can be re-issued; link works in `OnboardingFlowPortal`

---

### PRIO 9: Compliance Enforcement

- [ ] I‑9 deadlines
  - Use `I9Section2ComplianceTracker` to compute deadlines and enforce warnings/blocks if overdue; surface messages in manager/HR flows

- [ ] Signature coordinates
  - Ensure PDF generation uses standardized positions (see `CLAUDE.md` signature coordinates) and store signature metadata

---

### Acceptance Test Pointers (non-exhaustive)
- QR / Application: `test_qr_api.py`, `test_task1_qr_generation.py`, `test_complete_qr_workflow.py`, `QR_CODE_WORKFLOW_VERIFICATION.md`
- Property Info: `GET /properties/{id}/info` (already present)
- Manager Access Control: `test_property_access_control_comprehensive.py`, `test_manager_access_control.py`
- WebSockets: `test_websocket_basic.py`, `tests/test_websocket_manager.py`
- HR Approval: `tests/test_three_phase_workflow.py` (Phase 3 section)

---

### Implementation Notes
- Property Access
  - Use decorators in `app/property_access_control.py`: `require_application_access`, `require_onboarding_access`, `require_property_access`
- WebSocket Rooms
  - Use `property-{property_id}` for manager scopes; `global` for HR; see `app/websocket_router.py` and `app/websocket_manager.py`
- Database Tables
  - `onboarding_tokens`, `onboarding_sessions`, `audit_logs`, `job_applications`, `employees` per existing migrations/specs

---

### Definition of Done (DoD)
- [ ] All endpoints above exist and respond correctly (no 404)
- [ ] Frontend flows work end-to-end for HR, Manager, Candidate
- [ ] Real-time updates visible for application submission/approval and onboarding transitions
- [ ] Audit entries written for critical actions
- [ ] I‑9 Section 2 completes and transitions to HR; HR can finalize
- [ ] Key tests pass; manual smoke flows green

---

### Scratchpad (for working session)
- Decisions:
  - Service/orchestrator interface chosen: ____
  - `/api` prefix strategy: proxy vs path changes: ____
  - Notification email senders/templates used: ____
- Open Questions:
  - Do we gate HR approval on all document uploads present? ____
  - Should token be passed via header (`Authorization: Bearer {token}`) or body for onboarding endpoints? ____


