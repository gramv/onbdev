# Spec Tasks

## Tasks

- [x] 1. Setup Test Property and Manager
  - [x] 1.1 Create test property in database
  - [x] 1.2 Create manager account for test property
  - [x] 1.3 Verify manager can login
  - [x] 1.4 Test application link /apply/{property_id}
  - [x] 1.5 Verify manager can approve applications

- [x] 2. Fix Employee Name Propagation (Non-I-9/W-4)
  - [x] 2.1 Update Company Policies PDF to use PersonalInfoStep data
  - [x] 2.2 Update Direct Deposit PDF to use PersonalInfoStep data
  - [x] 2.3 Update Health Insurance PDF to use PersonalInfoStep data
  - [x] 2.4 Update Weapons Policy PDF to use PersonalInfoStep data
  - [x] 2.5 Test all documents show correct employee names
  - [x] 2.6 Verify names persist across all forms

- [x] 3. Create Human Trafficking Document Generator
  - [x] 3.1 Create HumanTraffickingDocumentGenerator class
  - [x] 3.2 Map content from hire packet pages 19, 21
  - [x] 3.3 Include hotline number 1-888-373-7888
  - [x] 3.4 Add signature acknowledgment section
  - [x] 3.5 Connect to existing endpoint
  - [x] 3.6 Test PDF generation and preview

- [x] 4. Verify All Document Previews
  - [x] 4.1 Test Direct Deposit preview endpoint
  - [x] 4.2 Test Health Insurance preview endpoint
  - [x] 4.3 Test Weapons Policy preview endpoint
  - [x] 4.4 Verify all return base64 PDFs
  - [x] 4.5 Check preview displays in UI
  - [x] 4.6 Ensure post-signature PDFs are complete

- [x] 5. Manager Document Access
  - [x] 5.1 Verify manager can view all employee documents
  - [x] 5.2 Test document download functionality
  - [x] 5.3 Check document list displays correctly
  - [x] 5.4 Ensure property isolation works
  - [x] 5.5 Test PDF preview in manager dashboard
  - [x] 5.6 Verify access permissions

- [x] 6. End-to-End Testing
  - [x] 6.1 Apply at /apply/{property_id}
  - [x] 6.2 Manager approves application
  - [x] 6.3 Employee completes onboarding with JWT
  - [x] 6.4 All documents generate correctly
  - [x] 6.5 Manager can access all documents
  - [x] 6.6 Verify complete workflow