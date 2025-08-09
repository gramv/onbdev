# Product Roadmap

## Phase 0: Already Completed

The following features have been implemented:

- [x] FastAPI backend with Supabase integration
- [x] React/TypeScript frontend with routing
- [x] I-9 Section 1 form with PDF generation (working perfectly)
- [x] W-4 tax form with PDF generation (working perfectly)
- [x] Company Policies PDF with complete content (20+ policies)
- [x] JWT-based 7-day token system for employees
- [x] Manager role and authentication
- [x] Email notification service
- [x] Digital signature capture
- [x] Multi-step onboarding flow UI
- [x] Property-specific application links (/apply/{property_id})
- [x] All PDF generation endpoints created

## Phase 1: Critical Fixes (Current - 4 Hours)

**Goal:** Fix employee name propagation and missing generators
**Success Criteria:** All documents show correct employee names and all pages generate

### Features

- [ ] Set up test property in database - Create demo property for testing `XS`
- [ ] Create manager account for test property - Enable manager login and approval `XS`
- [ ] Fix employee name propagation (non-I-9/W-4) - Pull from PersonalInfoStep data `S`
- [ ] Create HumanTraffickingDocumentGenerator - Pages 19, 21 with hotline info `S`
- [ ] Test all document preview endpoints - Verify base64 PDF generation `XS`
- [ ] Verify document accessibility for managers - Ensure managers can view all PDFs `XS`

### Dependencies

- PersonalInfoStep data structure
- Hire packet pages 19, 21 for content
- Existing working generators as templates

## Phase 2: Manager Workflow (Next Priority)

**Goal:** Complete manager dashboard and document access
**Success Criteria:** Managers can approve applications and access all documents

### Features

- [ ] Enhanced manager approval dashboard - Better UI for application review `M`
- [ ] Bulk document download - Download all employee documents as ZIP `S`
- [ ] Application status filtering - View by pending/approved/rejected `S`
- [ ] Employee search functionality - Find employees by name or ID `S`
- [ ] Document completion tracking - Visual progress indicators `S`

### Dependencies

- Phase 1 fixes complete
- Manager authentication working

## Phase 3: Production Readiness

**Goal:** Prepare for real hotel deployment
**Success Criteria:** System ready for first customer

### Features

- [ ] Production database setup - Configure production Supabase instance `S`
- [ ] Backup and recovery procedures - Automated daily backups `S`
- [ ] Manager training materials - Video tutorials and guides `M`
- [ ] Performance monitoring - Response time tracking `S`
- [ ] Error logging and alerts - Sentry or similar integration `S`

### Dependencies

- All phases complete
- Customer feedback incorporated

## Phase 4: Scale & Enhance (Future)

**Goal:** Add advanced features based on customer needs
**Success Criteria:** System scales to multiple properties

### Features

- [ ] Multi-property support - Manage multiple hotels from one account `XL`
- [ ] Mobile-responsive manager dashboard - Full functionality on tablets/phones `L`
- [ ] Bulk operations - Process multiple employees simultaneously `L`
- [ ] Advanced reporting - Compliance reports, hiring analytics `L`
- [ ] API integrations - Payroll, background checks, E-Verify `XL`

### Dependencies

- Production deployment successful
- Customer demand validated
- Additional resources available

## Effort Scale
- XS: 1 day
- S: 2-3 days
- M: 1 week
- L: 2 weeks
- XL: 3+ weeks