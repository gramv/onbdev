# Spec Requirements Document

> Spec: Manager-Employee Onboarding MVP
> Created: 2025-08-09
> Status: In Progress

## Overview

Complete the Manager-Employee onboarding flow with exact 28-page packet replication, focusing on manager autonomy, employee name propagation, and universal document preview capability.

## User Stories

### Manager Direct Control

As a hotel manager, I want to approve applications and track onboarding without HR involvement, so that I can hire quickly.

The system provides managers complete autonomy: they review applications for their property, approve candidates which generates 7-day JWT tokens, and monitor progress through their dashboard. No HR intermediary required.

### Employee Name Propagation

As an employee, I want my name to appear correctly on all documents after entering it once, so that I don't have to re-enter information.

When employees complete PersonalInfoStep, their name should automatically populate across ALL generated documents (Company Policies, Direct Deposit, Health Insurance, Weapons Policy, Human Trafficking). Currently working for I-9 and W-4, needs fixing for others.

### Universal Document Preview

As a manager, I want to preview every document before employees sign them, so that I can ensure accuracy.

Every single form must have preview capability showing the exact PDF that will be generated. This allows managers to verify document accuracy before sending to employees.

## Spec Scope

1. **Test Property Setup** - Create demo property with manager account for testing
2. **Employee Name Fix** - Pull names from PersonalInfoStep for all non-I-9/W-4 documents  
3. **Human Trafficking Generator** - Create missing generator for pages 19, 21
4. **Document Preview Testing** - Verify all endpoints return proper base64 PDFs
5. **Manager Document Access** - Ensure managers can view/download all employee documents

## Out of Scope

- Changes to I-9 or W-4 (already working perfectly)
- HR dashboard or features
- Multi-property support
- Bulk operations
- Production deployment

## Expected Deliverable

1. Manager can approve applications for their test property
2. Employee names populate correctly across ALL documents
3. Every document has working preview functionality
4. Complete 28-page packet generates matching exact format