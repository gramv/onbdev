# Sub-Agent Definitions for Hotel Onboarding System

## Overview

These are the specialized sub-agents needed to execute the bite-sized tasks in our plan. Each agent has a specific domain and limited scope to ensure focused, accurate execution.

## 1. test-setup-agent

**Purpose**: Create test data and accounts in the database

**Capabilities**:
- Create user accounts (HR, Manager, Employee)
- Insert test properties
- Create test job applications
- Setup initial data relationships

**Tools Needed**:
- Bash (for Python scripts)
- Read (to check existing data)
- Write (to create setup scripts)

**Example Tasks**:
- Create HR user with credentials
- Create test property "Demo Hotel"
- Link manager to property
- Insert test job application

**Success Criteria**:
- Data exists in database
- Can query and verify data
- Relationships are correct

## 2. backend-api-builder

**Purpose**: Build, fix, and enhance backend API endpoints

**Capabilities**:
- Create new FastAPI endpoints
- Fix existing endpoint issues
- Add business logic
- Implement data filtering
- Add email triggers

**Tools Needed**:
- Read (to understand existing code)
- MultiEdit (to modify endpoints)
- Write (for new files if needed)

**Example Tasks**:
- Fix /api/manager/dashboard-stats endpoint
- Create /api/hr/applications/all endpoint
- Add JWT token generation
- Implement email sending

**Success Criteria**:
- Endpoints return correct data
- Proper HTTP status codes
- Data filtering works
- No breaking changes

## 3. frontend-component-fixer

**Purpose**: Fix and enhance React frontend components

**Capabilities**:
- Fix component rendering issues
- Connect components to APIs
- Handle error states
- Update UI elements
- Wire up event handlers

**Tools Needed**:
- Read (to understand components)
- MultiEdit (to fix components)
- Write (for new components)

**Example Tasks**:
- Fix ApplicationsTab display
- Connect dashboard to stats API
- Add approve/reject buttons
- Display notification badges

**Success Criteria**:
- Components render without errors
- Data displays correctly
- User interactions work
- Proper error handling

## 4. test-automation-engineer

**Purpose**: Test functionality end-to-end

**Capabilities**:
- Test API endpoints
- Verify UI flows
- Check data persistence
- Test authentication
- Validate workflows

**Tools Needed**:
- Bash (to run curl/tests)
- Read (to check results)

**Example Tasks**:
- Test login flows
- Verify property isolation
- Test application approval
- Check document generation

**Success Criteria**:
- All tests pass
- Expected data returned
- Workflows complete
- No errors in console

## 5. email-notification-builder

**Purpose**: Implement email and notification services

**Capabilities**:
- Setup email configuration
- Create email templates
- Implement notification triggers
- Handle email errors gracefully

**Tools Needed**:
- Read (existing email code)
- Write (email templates)
- MultiEdit (add email triggers)

**Example Tasks**:
- Configure email service
- Create welcome email template
- Add approval email trigger
- Save notifications to database

**Success Criteria**:
- Emails send (or log in dev)
- Templates render correctly
- Notifications saved
- No email errors

## 6. database-migration-agent

**Purpose**: Verify and setup database tables

**Capabilities**:
- Check existing tables
- Create indexes if needed
- Verify relationships
- Setup test data

**Tools Needed**:
- Bash (to run SQL)
- Read (check schema)
- Write (migration scripts)

**Example Tasks**:
- Verify tables exist
- Check foreign keys
- Create indexes
- Verify RLS policies

**Success Criteria**:
- All tables accessible
- Queries run fast
- Relationships work
- No permission errors

## Agent Coordination Rules

1. **Sequential Execution**: Agents work on one task at a time
2. **Immediate Testing**: Each agent tests their work before marking complete
3. **Error Handling**: If test fails, agent fixes and retests
4. **Clean Handoff**: Agent documents what was done for next agent
5. **No Scope Creep**: Agents only do their assigned task

## Communication Protocol

When invoking an agent:
```
Agent: [agent-name]
Task: [specific task from tasks.md]
Context: [relevant file paths and current state]
Success Criteria: [what must work after]
Test Command: [exact test to run]
```

## Error Recovery

If an agent fails:
1. Agent reports specific error
2. Orchestrator decides: retry, skip, or get user help
3. Never leave system in broken state
4. Roll back changes if needed

## Important Constraints

- Agents must NOT create new database tables (use existing ones)
- Agents must NOT break existing onboarding functionality
- Agents must NOT add complex features (keep it simple)
- Agents must complete tasks in 15-30 minutes
- Agents must test immediately after changes