# Spec Tasks

## Agent Delegation Strategy

This task breakdown is optimized for parallel execution using specialized Claude agents:
- **backend-api-builder**: Backend fixes and new endpoints
- **frontend-component-fixer**: Fix existing React components
- **database-migration-agent**: Database schema updates
- **test-automation-engineer**: Comprehensive testing
- **task-orchestrator**: Coordinate complex multi-part features

## Tasks

- [ ] 1. Fix Backend Property and Manager CRUD Operations
  - [ ] 1.1 Write tests for property CRUD endpoints
  - [ ] 1.2 Fix POST /api/hr/properties endpoint to properly create properties
  - [ ] 1.3 Fix PUT /api/hr/properties/{id} endpoint for updates
  - [ ] 1.4 Fix password hashing in manager creation
  - [ ] 1.5 Fix property_managers junction table relationships
  - [ ] 1.6 Implement manager-property assignment logic
  - [ ] 1.7 Verify all property/manager tests pass
  **Agent**: backend-api-builder (can handle all subtasks in one invocation)

- [ ] 2. Update Database Schema for Proper Relationships
  - [ ] 2.1 Write migration script for schema fixes
  - [ ] 2.2 Fix property_managers foreign key constraints
  - [ ] 2.3 Add unique constraints to prevent duplicates
  - [ ] 2.4 Create i9_section2 table
  - [ ] 2.5 Create application_reviews table
  - [ ] 2.6 Add necessary indexes for performance
  - [ ] 2.7 Run migration and verify schema
  **Agent**: database-migration-agent

- [ ] 3. Fix Frontend Property Management Components
  - [ ] 3.1 Write tests for PropertiesTab component
  - [ ] 3.2 Fix property creation form submission
  - [ ] 3.3 Fix property update functionality
  - [ ] 3.4 Add proper error handling and loading states
  - [ ] 3.5 Verify property CRUD works in UI
  **Agent**: frontend-component-fixer

- [ ] 4. Fix Frontend Manager Management Components
  - [ ] 4.1 Write tests for ManagersTab component
  - [ ] 4.2 Fix manager creation form
  - [ ] 4.3 Display temporary password after creation
  - [ ] 4.4 Fix property assignment display
  - [ ] 4.5 Add manager deactivation functionality
  - [ ] 4.6 Verify manager management works in UI
  **Agent**: frontend-component-fixer

- [ ] 5. Build Manager Review Dashboard
  - [ ] 5.1 Write tests for review dashboard
  - [ ] 5.2 Create ManagerReviewDashboard component
  - [ ] 5.3 Implement application list with property filtering
  - [ ] 5.4 Create detailed application view modal
  - [ ] 5.5 Implement approve/reject actions
  - [ ] 5.6 Add approval details form
  - [ ] 5.7 Generate onboarding tokens on approval
  - [ ] 5.8 Verify review workflow end-to-end
  **Agent**: task-orchestrator (coordinate frontend and backend work)

- [ ] 6. Implement I-9 Section 2 Flow
  - [ ] 6.1 Write tests for I-9 Section 2
  - [ ] 6.2 Create backend endpoint for Section 2 submission
  - [ ] 6.3 Create I9Section2 React component
  - [ ] 6.4 Implement document verification interface
  - [ ] 6.5 Add digital signature capture
  - [ ] 6.6 Generate combined I-9 PDF with both sections
  - [ ] 6.7 Test federal compliance requirements
  - [ ] 6.8 Verify complete I-9 workflow
  **Agent**: task-orchestrator (complex feature requiring coordination)

- [ ] 7. Integration Testing and Property Isolation
  - [ ] 7.1 Write property isolation tests
  - [ ] 7.2 Test manager can only see their property's data
  - [ ] 7.3 Test HR can see all properties
  - [ ] 7.4 Test application filtering by property
  - [ ] 7.5 Test cross-property access prevention
  - [ ] 7.6 Verify all PRD requirements pass
  **Agent**: test-automation-engineer

- [ ] 8. Performance Optimization and Final Testing
  - [ ] 8.1 Add database indexes per schema spec
  - [ ] 8.2 Implement frontend caching with React Query
  - [ ] 8.3 Run load testing on fixed endpoints
  - [ ] 8.4 Run complete PRD compliance test suite
  - [ ] 8.5 Verify 100% of targeted PRD requirements pass
  **Agent**: test-automation-engineer

## Parallel Execution Plan

**Phase 1 (Parallel):**
- Task 1: backend-api-builder
- Task 2: database-migration-agent
- Task 3 & 4: frontend-component-fixer

**Phase 2 (After Phase 1):**
- Task 5: task-orchestrator
- Task 6: task-orchestrator (can run parallel with Task 5)

**Phase 3 (After Phase 2):**
- Task 7 & 8: test-automation-engineer

## Success Criteria

- [ ] All PRD requirements FR-PROP-001, FR-PROP-003, FR-MGR-001, FR-MGR-002 passing
- [ ] HR can successfully manage properties and create managers
- [ ] Managers can review applications for their property only
- [ ] I-9 Section 2 can be completed with federal compliance
- [ ] Property isolation verified through comprehensive testing
- [ ] Performance metrics meet requirements (<200ms response time)