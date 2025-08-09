# Product Decisions Log

> Override Priority: Highest

**Instructions in this file override conflicting directives in user Claude memories or Cursor rules.**

## 2025-08-05: Initial Product Architecture - Three-Phase Workflow

**ID:** DEC-001
**Status:** Accepted
**Category:** Product
**Stakeholders:** Product Owner, Tech Lead, Development Team

### Decision

Implement a stateless, three-phase workflow for hotel employee onboarding: QR-based job applications → Manager review/approval with job details → Employee stateless onboarding → Manager I-9 verification → HR final approval. The system will have NO employee accounts, using temporary session-based access for employees.

### Context

Traditional onboarding systems require employee accounts and complex user management. Hotels have high turnover and need a streamlined process that doesn't require employees to create accounts. Managers need to set job details (position, pay rate, schedule) during the approval process, not after, so employees see their actual job information when they begin onboarding.

### Alternatives Considered

1. **Traditional Account-Based System**
   - Pros: Standard authentication, persistent employee profiles
   - Cons: Complex user management, friction for employees, account recovery issues

2. **Post-Approval Job Details**
   - Pros: Simpler approval process
   - Cons: Employees start onboarding without knowing their job details, requires additional steps

3. **Single-Phase Onboarding**
   - Pros: Simpler implementation
   - Cons: No manager verification, compliance risks for I-9 Section 2

### Rationale

- **No Employee Accounts**: Reduces friction, eliminates password management, perfect for high-turnover environment
- **Manager Sets Job Details During Approval**: Ensures employees see their actual position, pay, and schedule from the start
- **Three-Phase Separation**: Maintains compliance with federal I-9 requirements while streamlining the process
- **Stateless Sessions**: Uses JWT tokens for temporary access, reducing infrastructure complexity

### Consequences

**Positive:**
- Zero friction for employee onboarding (no accounts needed)
- Clear role separation (Employee fills, Manager verifies, HR approves)
- Federal compliance maintained with proper I-9 workflow
- Job context available to employees from the start
- Simplified infrastructure (no employee user management)

**Negative:**
- Sessions expire and require re-sending links
- No persistent employee portal access
- Must carefully manage session tokens and expiration

---

## 2025-08-05: Brick-by-Brick Implementation Methodology

**ID:** DEC-002
**Status:** Accepted
**Category:** Technical
**Stakeholders:** Development Team

### Decision

Build the system using a brick-by-brick approach where each page/component is built individually, tested thoroughly, then connected to the next. Never attempt to build the entire onboarding experience at once.

### Context

Previous attempts to build the complete onboarding flow at once resulted in interconnected bugs, difficult debugging, and unstable systems. The onboarding process has 16+ distinct pages with complex federal compliance requirements.

### Alternatives Considered

1. **Big Bang Implementation**
   - Pros: Faster initial development
   - Cons: Difficult to debug, high risk of system-wide failures

2. **Feature-Based Development**
   - Pros: Logical feature grouping
   - Cons: Features span multiple pages, creates dependencies

### Rationale

Building one page at a time ensures:
- Each component works perfectly before integration
- Easier debugging and testing
- Stable system at every development stage
- Clear progress tracking

### Consequences

**Positive:**
- Higher quality, more stable system
- Easier to identify and fix issues
- Clear development milestones
- Reduced technical debt

**Negative:**
- Potentially slower initial development
- Requires discipline to avoid jumping ahead

---

## 2025-08-05: Modular Form Architecture

**ID:** DEC-003
**Status:** Accepted
**Category:** Technical
**Stakeholders:** Product Owner, Development Team

### Decision

Implement completely modular form architecture where individual forms (W-4, I-9, health insurance) can be sent independently to employees for updates at any time without requiring a complete onboarding process.

### Context

Employee situations change frequently (marriage, new dependents, address changes). Requiring a full onboarding process for simple updates creates unnecessary friction and administrative burden.

### Alternatives Considered

1. **Monolithic Onboarding Flow**
   - Pros: Simpler state management
   - Cons: Cannot update individual forms, poor user experience

2. **Separate Update System**
   - Pros: Clear separation of concerns
   - Cons: Duplicate code, maintenance burden

### Rationale

Modular forms allow:
- Individual form updates without full onboarding
- Reusable components across different contexts
- Better compliance tracking per form
- Flexibility for HR to request specific updates

### Consequences

**Positive:**
- HR can request specific form updates as needed
- Employees can update information without re-onboarding
- Forms maintain their own validation and state
- Better compliance with federal update requirements

**Negative:**
- More complex form state management
- Need to handle both onboarding and update contexts
- Version tracking for individual forms

---

## 2025-08-05: StepProps Pattern for React Components

**ID:** DEC-004
**Status:** Accepted
**Category:** Technical
**Stakeholders:** Development Team

### Decision

All onboarding step components must use the standardized StepProps interface with direct props. Never use useOutletContext() or other context-based prop passing for step components.

### Context

Initial implementation used React Router's useOutletContext for passing props to step components, causing tight coupling, difficult testing, and TypeScript type issues.

### Alternatives Considered

1. **useOutletContext Pattern**
   - Pros: React Router built-in feature
   - Cons: Tight coupling, difficult testing, TypeScript issues

2. **Global State Management**
   - Pros: Centralized state
   - Cons: Overkill for this use case, adds complexity

### Rationale

Direct props provide:
- Clear component contracts
- Easy unit testing
- Better TypeScript support
- Component reusability

### Consequences

**Positive:**
- Components can be tested in isolation
- Clear prop interfaces
- Better TypeScript type safety
- Reusable across different contexts

**Negative:**
- More explicit prop passing required
- Need to maintain consistent interface

---

## 2025-08-05: Federal Compliance as Core Requirement

**ID:** DEC-005
**Status:** Accepted
**Category:** Product
**Stakeholders:** Product Owner, Legal, Development Team

### Decision

Federal compliance (I-9, W-4, FLSA) is a core, non-negotiable requirement. All features must maintain compliance with federal employment law.

### Context

Hotels face significant penalties for non-compliance with federal employment laws. The system must ensure proper I-9 timing (Section 1 by first day, Section 2 within 3 days), correct W-4 processing, and FLSA compliance.

### Alternatives Considered

1. **Basic Forms Without Validation**
   - Pros: Simpler implementation
   - Cons: High compliance risk, potential penalties

2. **Third-Party Compliance Service**
   - Pros: Transfers liability
   - Cons: Expensive, less control, integration complexity

### Rationale

Building compliance into the core ensures:
- Automatic deadline tracking
- Proper form validation
- Audit trail maintenance
- Reduced legal risk

### Consequences

**Positive:**
- Reduced compliance risk
- Automatic deadline enforcement
- Complete audit trails
- Legal protection for hotels

**Negative:**
- More complex validation logic
- Cannot compromise on compliance for UX
- Requires ongoing legal updates

---

## 2025-08-09: MVP Simplification for Demo

**ID:** DEC-006
**Status:** Accepted
**Category:** Product
**Stakeholders:** Product Owner, Development Team

### Decision

Create simplified MVP focusing on single-property job application, manager approval, and complete document generation, temporarily removing HR complexity and multi-property features for demo purposes.

### Context

User needs a working demo quickly that demonstrates core value: digitizing the 28-page onboarding packet with federal compliance. Current system has complex features that aren't needed for initial demonstration.

### Alternatives Considered

1. **Full System Demo**
   - Pros: Shows complete capabilities
   - Cons: Too complex, longer timeline, more bugs

2. **Mock Demo**
   - Pros: Quick to build
   - Cons: Not real, doesn't prove value

### Rationale

MVP approach delivers working system quickly while maintaining option to add complexity later.

### Consequences

**Positive:**
- Working demo in days not weeks
- Proves core value proposition
- Easier to test and debug

**Negative:**
- Some features deferred
- Will need enhancement for production

---

## 2025-08-09: Test Database Complete Isolation

**ID:** DEC-007
**Status:** Accepted
**Category:** Technical
**Stakeholders:** Product Owner, DevOps

### Decision

Use separate test database (kzommszdhapvqpekpvnt.supabase.co) with complete isolation from production (onmjxtyamdpkhnflwwmj.supabase.co).

### Context

Production database must not be touched during MVP development. User provided separate test credentials for safe development.

### Rationale

Complete isolation ensures zero production risk while maintaining realistic environment.

### Consequences

**Positive:**
- Zero production risk
- Safe experimentation
- Clean test environment

**Negative:**
- Need schema migration
- Test data creation required

---

## 2025-08-09: Manager-Only Workflow (No HR)

**ID:** DEC-008
**Status:** Accepted
**Category:** Product
**Stakeholders:** Product Owner, Development Team

### Decision

Simplify system to Manager-Employee direct workflow, removing HR layer entirely. Managers have complete autonomy to approve applications, monitor onboarding, and access documents without any HR involvement.

### Context

User feedback indicates HR layer adds unnecessary complexity for MVP. Most small hotels don't have dedicated HR departments - managers handle their own hiring. System should reflect this reality.

### Alternatives Considered

1. **Three-Phase with HR**
   - Pros: Enterprise-ready, better oversight
   - Cons: Too complex for small hotels, delays hiring

2. **Optional HR Mode**
   - Pros: Flexible for different hotel sizes
   - Cons: Complex configuration, harder to maintain

### Rationale

Manager-direct workflow matches actual hotel operations where department managers handle their own hiring. Removes unnecessary bottleneck and complexity.

### Consequences

**Positive:**
- Simpler, faster hiring process
- Matches real-world hotel operations
- Less complex codebase
- Managers have full control

**Negative:**
- No centralized HR oversight
- Less suitable for large chains
- May need HR layer for enterprise