# Spec Tasks

## Phase 1: Foundation Setup (10 Bite-Sized Tasks)

### Parallel Group A - Database & Accounts
- [x] 1.1 Verify Existing Database Tables
  - Agent: database-migration-agent
  - Parallel: Group A
  - Action: Verify users, properties, property_managers tables exist
  - Test: Query tables in Supabase

- [x] 1.2 Create First HR Account
  - Agent: test-setup-agent  
  - Parallel: Group A
  - Action: Create HR user with credentials (hr@demo.com / Demo123!)
  - Test: Login with HR account via API

- [x] 1.3 Create Test Property
  - Agent: test-setup-agent
  - Parallel: Group A
  - Action: Insert test property "Demo Hotel" in database
  - Test: Query property exists

- [x] 1.4 Create Test Manager Account
  - Agent: test-setup-agent
  - Parallel: Group A
  - Action: Create manager linked to test property (manager@demo.com / Demo123!)
  - Test: Login with manager account and verify property_id

### Parallel Group B - Backend Endpoints
- [x] 1.5 Fix HR Dashboard Stats Endpoint
  - Agent: backend-api-builder
  - Parallel: Group B (after Group A)
  - Action: Ensure /api/hr/dashboard-stats returns system-wide data
  - Test: curl endpoint returns JSON with counts

- [x] 1.6 Fix Manager Dashboard Stats Endpoint
  - Agent: backend-api-builder
  - Parallel: Group B (after Group A)
  - Action: Ensure /api/manager/dashboard-stats filters by property
  - Test: curl endpoint returns property-specific JSON

- [x] 1.7 Fix Manager Property Endpoint
  - Agent: backend-api-builder
  - Parallel: Group B (after Group A)
  - Action: Ensure /api/manager/property returns manager's property
  - Test: curl returns correct property data

### Sequential Tasks
- [x] 1.8 Connect Manager Dashboard to API
  - Agent: frontend-component-fixer
  - Action: Wire up stats display in Manager dashboard
  - Test: Dashboard shows property info and stats

- [x] 1.9 Test Manager Login Flow
  - Agent: test-automation-engineer
  - Action: Test complete manager login and dashboard load
  - Test: Can login and see property-specific data

- [x] 1.10 **CHECKPOINT Alpha** - Verify Property Isolation ✅
  - Agent: test-automation-engineer
  - Checkpoint: Tag as `checkpoint-alpha-foundation`
  - Action: Verify manager can't access other property data
  - Test: API returns 403 for other properties
  - Rollback: `git reset --hard checkpoint-alpha-foundation` if needed

## Phase 2: Core Application Flow (8 Tasks)

- [x] 2.1 Create Test Job Application
  - Agent: test-setup-agent
  - Action: Insert test application for demo property
  - Test: Application exists in job_applications table

- [x] 2.2 Fix Applications List Endpoint
  - Agent: backend-api-builder
  - Action: Ensure /api/manager/applications returns property applications
  - Test: curl returns application list

- [x] 2.3 Connect Applications Tab
  - Agent: frontend-component-fixer
  - Action: Display applications in ApplicationsTab component
  - Test: Applications visible in manager UI

- [x] 2.4 Implement Application Approval
  - Agent: backend-api-builder
  - Action: Fix /api/applications/{id}/approve endpoint
  - Test: Can approve via API, status changes

- [x] 2.5 Add Approval Button UI
  - Agent: frontend-component-fixer
  - Action: Add working approve/reject buttons
  - Test: Buttons trigger API calls successfully

- [x] 2.6 Generate Onboarding Token
  - Agent: backend-api-builder
  - Action: Create JWT token on approval, save to onboarding_sessions
  - Test: Token generated and stored in database

- [x] 2.7 Test Onboarding Portal Access
  - Agent: test-automation-engineer
  - Action: Test /onboard?token={jwt} loads portal
  - Test: Portal loads with valid token

- [x] 2.8 **CHECKPOINT Beta** - End-to-End Application Test ✅
  - Agent: test-automation-engineer
  - Checkpoint: Tag as `checkpoint-beta-core-flow`
  - Action: Test full flow from application to onboarding start
  - Test: Complete flow works without errors
  - Rollback: `git reset --hard checkpoint-beta-core-flow` if needed

## Phase 2.5: Data Integrity Validation

- [x] 2.9 Cross-Property Data Isolation Check ✅
  - Agent: test-automation-engineer
  - Action: Verify complete data isolation between properties
  - Tests:
    - Create 3 test properties with different managers
    - Attempt cross-property application access (expect 403)
    - Verify managers only see their property's data
    - Test HR can see all properties
    - Ensure no data leakage in API responses
  - Critical: Must pass before proceeding to Phase 3
  - Status: SECURITY VERIFIED - All isolation tests passing

## Phase 3: HR Dashboard Implementation (6 Tasks)

- [x] 3.1 Create HR Dashboard Layout
  - Agent: frontend-component-fixer
  - Action: Create HRDashboardLayout component
  - Test: HR dashboard renders at /hr route

- [x] 3.2 Create Properties Overview Tab
  - Agent: frontend-component-fixer
  - Action: Create PropertiesOverviewTab showing all properties
  - Test: Properties list displays

- [x] 3.3 Create HR Applications Endpoint
  - Agent: backend-api-builder
  - Action: Create /api/hr/applications/all endpoint
  - Test: Returns all applications across properties

- [x] 3.4 Create System Applications Tab
  - Agent: frontend-component-fixer
  - Action: Create SystemApplicationsTab with property filter
  - Test: Shows all applications with filtering

- [x] 3.5 Add HR Stats Display
  - Agent: frontend-component-fixer
  - Action: Display system-wide stats in HR dashboard
  - Test: Stats cards show correct totals

- [x] 3.6 **CHECKPOINT Gamma** - Test HR Complete Workflow ✅
  - Agent: test-automation-engineer
  - Checkpoint: Tag as `checkpoint-gamma-hr-system`
  - Action: Test HR can view all properties and applications
  - Test: HR has full system visibility
  - Rollback: `git reset --hard checkpoint-gamma-hr-system` if needed

## Phase 4: Email & Notifications (6 Tasks)

- [x] 4.1 Setup Email Configuration
  - Agent: email-notification-builder
  - Action: Add email config to .env (use console.log for now)
  - Test: Can log email content

- [x] 4.2 Create Welcome Email Template
  - Agent: email-notification-builder
  - Action: Create simple HTML email template
  - Test: Template renders with variables

- [x] 4.3 Send Email on Approval
  - Agent: backend-api-builder
  - Action: Trigger email when application approved
  - Test: Email logged with onboarding link

- [x] 4.4 Add Manager Welcome Email
  - Agent: backend-api-builder
  - Action: Send credentials when manager created
  - Test: Manager creation triggers email

- [x] 4.5 Create Notification Record
  - Agent: backend-api-builder
  - Action: Save notification to existing notifications table
  - Test: Notification saved on events

- [x] 4.6 Display Notifications Count
  - Agent: frontend-component-fixer
  - Action: Show notification badge in dashboard
  - Test: Badge shows unread count

## Phase 5: Real-time Updates (5 Tasks) ✅

- [x] 5.1 Fix WebSocket Connection
  - Agent: backend-api-builder
  - Action: Ensure WebSocket endpoint works
  - Test: Can establish WS connection

- [x] 5.2 Add Application Created Event
  - Agent: backend-api-builder
  - Action: Broadcast when new application submitted
  - Test: Event received by connected clients

- [x] 5.3 Connect Frontend to WebSocket
  - Agent: frontend-component-fixer
  - Action: Establish WebSocket in dashboard
  - Test: Connection established on load

- [x] 5.4 Update Dashboard on Events
  - Agent: frontend-component-fixer
  - Action: Refresh stats when events received
  - Test: Dashboard updates without refresh

- [x] 5.5 Test Real-time Flow
  - Agent: test-automation-engineer
  - Action: Submit application and verify dashboard updates
  - Test: All dashboards update in real-time

## Phase 6: Final Testing & Validation (4 Tasks)

- [ ] 6.1 Test Manager Complete Flow
  - Agent: test-automation-engineer
  - Action: Login, view applications, approve, check documents
  - Test: All manager features work

- [ ] 6.2 Test HR Complete Flow
  - Agent: test-automation-engineer
  - Action: Login, view all properties, filter applications
  - Test: All HR features work

- [ ] 6.3 Verify Onboarding Still Works
  - Agent: test-automation-engineer
  - Action: Complete employee onboarding with token
  - Test: Full onboarding flow functional

- [ ] 6.4 Document Working Features
  - Agent: test-automation-engineer
  - Action: Create summary of all working features
  - Test: All documented features verified

- [ ] 6.5 API Performance Baseline Check
  - Agent: test-automation-engineer
  - Action: Measure response times for all critical endpoints
  - Performance Targets:
    - `/api/manager/dashboard-stats` < 100ms
    - `/api/hr/dashboard-stats` < 150ms
    - `/api/hr/applications/all` < 200ms
    - `/api/applications/{id}/approve` < 150ms
    - Document generation endpoints < 500ms
  - Test: All endpoints meet performance targets
  - Critical: Block deployment if targets not met

- [ ] 6.6 Frontend Load Performance Check
  - Agent: test-automation-engineer
  - Action: Measure dashboard load times
  - Performance Targets:
    - Manager dashboard initial load < 2 seconds
    - HR dashboard with 100+ applications < 3 seconds
    - WebSocket connection established < 500ms
    - Application form submission < 1 second
  - Test: All UI operations meet performance targets
  - Document: Create performance baseline report

## Execution Notes

### Agent OS Optimizations
- **Parallel Execution:** Tasks in same group (A, B, etc.) run simultaneously
- **Checkpoints:** Alpha, Beta, Gamma provide rollback points
- **Agent Batching:** Similar tasks combined into single agent requests
- **Performance Gates:** No progression if response times exceed limits

### Execution Guidelines
- Each task should take 15-30 minutes maximum
- Test immediately after each task
- Do not proceed if test fails
- Use existing database tables (no new tables needed)
- Focus on making existing features work
- Keep solutions simple and direct

### Rollback Procedures
- **Checkpoint Alpha Failed:** `git reset --hard checkpoint-alpha-foundation`
- **Checkpoint Beta Failed:** `git reset --hard checkpoint-beta-core-flow`
- **Checkpoint Gamma Failed:** `git reset --hard checkpoint-gamma-hr-system`

### Agent Delegation Command
Execute with: `/execute-tasks` to automatically:
1. Detect available agents
2. Match tasks to appropriate agents
3. Execute parallel groups simultaneously
4. Consolidate results and update task status