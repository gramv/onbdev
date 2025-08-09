# Spec Tasks

## Tasks

- [ ] 1. Setup Test Property and Manager
  - [ ] 1.1 Create test property in database
  - [ ] 1.2 Create manager account for test property
  - [ ] 1.3 Verify manager can login
  - [ ] 1.4 Test application link /apply/{property_id}
  - [ ] 1.5 Verify manager can approve applications

- [ ] 2. Fix Employee Name Propagation (Non-I-9/W-4)
  - [ ] 2.1 Update Company Policies PDF to use PersonalInfoStep data
  - [ ] 2.2 Update Direct Deposit PDF to use PersonalInfoStep data
  - [ ] 2.3 Update Health Insurance PDF to use PersonalInfoStep data
  - [ ] 2.4 Update Weapons Policy PDF to use PersonalInfoStep data
  - [ ] 2.5 Test all documents show correct employee names
  - [ ] 2.6 Verify names persist across all forms

- [ ] 3. Create Human Trafficking Document Generator
  - [ ] 3.1 Create HumanTraffickingDocumentGenerator class
  - [ ] 3.2 Map content from hire packet pages 19, 21
  - [ ] 3.3 Include hotline number 1-888-373-7888
  - [ ] 3.4 Add signature acknowledgment section
  - [ ] 3.5 Connect to existing endpoint
  - [ ] 3.6 Test PDF generation and preview

- [ ] 4. Verify All Document Previews
  - [ ] 4.1 Test Direct Deposit preview endpoint
  - [ ] 4.2 Test Health Insurance preview endpoint
  - [ ] 4.3 Test Weapons Policy preview endpoint
  - [ ] 4.4 Verify all return base64 PDFs
  - [ ] 4.5 Check preview displays in UI
  - [ ] 4.6 Ensure post-signature PDFs are complete

- [ ] 5. Manager Document Access
  - [ ] 5.1 Verify manager can view all employee documents
  - [ ] 5.2 Test document download functionality
  - [ ] 5.3 Check document list displays correctly
  - [ ] 5.4 Ensure property isolation works
  - [ ] 5.5 Test PDF preview in manager dashboard
  - [ ] 5.6 Verify access permissions

- [ ] 6. End-to-End Testing
  - [ ] 6.1 Apply at /apply/{property_id}
  - [ ] 6.2 Manager approves application
  - [ ] 6.3 Employee completes onboarding with JWT
  - [ ] 6.4 All documents generate correctly
  - [ ] 6.5 Manager can access all documents
  - [ ] 6.6 Verify complete workflow