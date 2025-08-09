---
description: Rules to initiate execution of a set of tasks using Agent OS
globs:
alwaysApply: false
version: 1.0
encoding: UTF-8
---

# Task Execution Rules

<ai_meta>
  <rules>Process XML blocks sequentially, use exact templates, request missing data</rules>
  <format>UTF-8, LF, 2-space indent, no header indent</format>
</ai_meta>

## Overview

Initiate execution of one or more tasks for a given spec.

<agent_detection>
  <check_once>
    AT START OF PROCESS:
    SET has_git_workflow = (Claude Code AND git-workflow agent exists)
    SET has_test_runner = (Claude Code AND test-runner agent exists)
    SET has_context_fetcher = (Claude Code AND context-fetcher agent exists)
    SET has_backend_api_builder = (Claude Code AND backend-api-builder agent exists)
    SET has_onboarding_form_builder = (Claude Code AND onboarding-form-builder agent exists)
    SET has_frontend_component_fixer = (Claude Code AND frontend-component-fixer agent exists)
    SET has_test_automation_engineer = (Claude Code AND test-automation-engineer agent exists)
    SET has_field_validation_tester = (Claude Code AND field-validation-tester agent exists)
    SET has_compliance_validator = (Claude Code AND compliance-validator agent exists)
    SET has_task_orchestrator = (Claude Code AND task-orchestrator agent exists)
    USE these flags throughout execution
  </check_once>
</agent_detection>

<process_flow>

<step number="1" name="task_assignment">

### Step 1: Task Assignment

<step_metadata>
  <inputs>
    - spec_srd_reference: file path
    - specific_tasks: array[string] (optional)
  </inputs>
  <default>next uncompleted parent task</default>
</step_metadata>

<task_selection>
  <explicit>user specifies exact task(s)</explicit>
  <implicit>find next uncompleted task in tasks.md</implicit>
</task_selection>

<instructions>
  ACTION: Identify task(s) to execute
  DEFAULT: Select next uncompleted parent task if not specified
  CONFIRM: Task selection with user
</instructions>

</step>

<step number="2" name="context_analysis">

### Step 2: Context Analysis

<step_metadata>
  <reads_always>
    - spec tasks.md
  </reads_always>
  <reads_conditionally>
    - @.agent-os/product/mission-lite.md (if not already in context)
    - spec-lite.md (if not already in context)
    - sub-specs/technical-spec.md (if not already in context)
  </reads_conditionally>
  <purpose>minimal context for task understanding</purpose>
</step_metadata>

<instructions>
  IF has_context_fetcher:
    USE: @agent:context-fetcher for each file not in context:
    - REQUEST: "Get product pitch from mission-lite.md"
    - REQUEST: "Get spec summary from spec-lite.md" 
    - REQUEST: "Get technical approach from technical-spec.md"
    PROCESS: Returned information
  ELSE:
    PROCEED: To conditional loading below
</instructions>

<conditional-block context-check="fallback-context-loading">
IF NOT using context-fetcher agent:
  READ: The following fallback context loading

<conditional_loading>
  <mission_lite>
    IF NOT already in context:
      READ @.agent-os/product/mission-lite.md
  </mission_lite>
  <spec_lite>
    IF NOT already in context:
      READ spec-lite.md from spec folder
  </spec_lite>
  <technical_spec>
    IF NOT already in context:
      READ sub-specs/technical-spec.md
  </technical_spec>
</conditional_loading>
</conditional-block>

<context_gathering>
  <essential_docs>
    - tasks.md for task breakdown
  </essential_docs>
  <conditional_docs>
    - mission-lite.md for product alignment
    - spec-lite.md for feature summary
    - technical-spec.md for implementation details
  </conditional_docs>
</context_gathering>

<instructions>
  ACTION: Always read tasks.md
  CHECK: Which files are already in context
  USE: Context-fetcher if Claude Code, else fallback
  LOAD: Only files not already in context
  SKIP: Other sub-specs files and best practices for now
  ANALYZE: Requirements specific to current task
</instructions>

</step>

<step number="3" name="development_server_check">

### Step 3: Check for Development Server

<step_metadata>
  <checks>running development server</checks>
  <prevents>port conflicts</prevents>
</step_metadata>

<server_check_flow>
  <if_running>
    ASK user to shut down
    WAIT for response
  </if_running>
  <if_not_running>
    PROCEED immediately
  </if_not_running>
</server_check_flow>

<user_prompt>
  A development server is currently running.
  Should I shut it down before proceeding? (yes/no)
</user_prompt>

<instructions>
  ACTION: Check for running local development server
  CONDITIONAL: Ask permission only if server is running
  PROCEED: Immediately if no server detected
</instructions>

</step>

<step number="4" name="git_branch_management">

### Step 4: Git Branch Management

<step_metadata>
  <manages>git branches</manages>
  <ensures>proper isolation</ensures>
</step_metadata>

<instructions>
  IF has_git_workflow:
    USE: @agent:git-workflow
    REQUEST: "Check and manage branch for spec: [SPEC_FOLDER]
              - Create branch if needed
              - Switch to correct branch
              - Handle any uncommitted changes"
    WAIT: For branch setup completion
  ELSE:
    PROCEED: To manual branch management below
</instructions>

<conditional-block context-check="manual-branch-management">
IF NOT using git-workflow agent:
  READ: The following manual branch management

<branch_naming>
  <source>spec folder name</source>
  <format>exclude date prefix</format>
  <example>
    - folder: 2025-03-15-password-reset
    - branch: password-reset
  </example>
</branch_naming>

<branch_logic>
  <case_a>
    <condition>current branch matches spec name</condition>
    <action>PROCEED immediately</action>
  </case_a>
  <case_b>
    <condition>current branch is main/staging/review</condition>
    <action>CREATE new branch and PROCEED</action>
  </case_b>
  <case_c>
    <condition>current branch is different feature</condition>
    <action>ASK permission to create new branch</action>
  </case_c>
</branch_logic>

<case_c_prompt>
  Current branch: [CURRENT_BRANCH]
  This spec needs branch: [SPEC_BRANCH]

  May I create a new branch for this spec? (yes/no)
</case_c_prompt>

<instructions>
  ACTION: Check current git branch
  EVALUATE: Which case applies
  EXECUTE: Appropriate branch action
  WAIT: Only for case C approval
</instructions>
</conditional-block>

</step>

<step number="5" name="task_execution_with_agents">

### Step 5: Task Execution with Specialized Agents

<step_metadata>
  <executes>parent tasks using specialized agents when available</executes>
  <delegates>to appropriate agents based on task type</delegates>
  <parallelizes>independent tasks for efficiency</parallelizes>
  <fallback>manual execution if no agent matches</fallback>
</step_metadata>

<agent_delegation_rules>
  <backend_tasks>
    PATTERN: "Fix.*PDF|Create.*Generator|Update.*endpoint|Setup.*database|Fix.*propagation.*PDF"
    IF has_backend_api_builder:
      USE: @agent:backend-api-builder
      REQUEST: Complete task description with context
  </backend_tasks>
  
  <frontend_form_tasks>
    PATTERN: "Create.*form|Update.*Step|Build.*component.*form"
    IF has_onboarding_form_builder:
      USE: @agent:onboarding-form-builder
      REQUEST: Form requirements and compliance needs
  </frontend_form_tasks>
  
  <frontend_fix_tasks>
    PATTERN: "Fix.*component|Update.*props|Refactor.*frontend|Fix.*name.*propagation"
    IF has_frontend_component_fixer:
      USE: @agent:frontend-component-fixer
      REQUEST: Component issues and TypeScript requirements
  </frontend_fix_tasks>
  
  <test_tasks>
    PATTERN: "Test.*endpoint|Verify.*preview|Test.*functionality|Test.*document"
    IF has_test_automation_engineer:
      USE: @agent:test-automation-engineer
      REQUEST: Testing requirements and expected outcomes
  </test_tasks>
  
  <validation_tasks>
    PATTERN: "Validate.*fields|Check.*consistency|Verify.*data"
    IF has_field_validation_tester:
      USE: @agent:field-validation-tester
      REQUEST: Field validation requirements
  </validation_tasks>
  
  <compliance_tasks>
    PATTERN: "Verify.*compliance|Check.*federal|Validate.*I-9|Validate.*W-4"
    IF has_compliance_validator:
      USE: @agent:compliance-validator
      REQUEST: Compliance requirements and regulations
  </compliance_tasks>
  
  <complex_orchestration>
    CONDITION: Task has 4+ subtasks OR requires multiple system changes
    IF has_task_orchestrator:
      USE: @agent:task-orchestrator
      REQUEST: Full task breakdown for delegation
  </complex_orchestration>
</agent_delegation_rules>

<parallel_execution_strategy>
  ANALYZE tasks for independence:
    - Group tasks with no dependencies
    - Identify tasks in different system areas
    - Find tests that can run concurrently
  
  EXAMPLE for name propagation fixes:
    IF multiple "Fix employee name propagation" tasks:
      LAUNCH in parallel:
        - @agent:backend-api-builder for each PDF fix
      WAIT for all to complete
      THEN test all together
</parallel_execution_strategy>

<execution_flow>
  # First try intelligent orchestration for complex tasks
  IF has_task_orchestrator AND total_subtasks >= 4:
    USE: @agent:task-orchestrator
    REQUEST: "Coordinate execution of tasks from [SPEC_PATH]/tasks.md
              Parent task: [TASK_NAME]
              Subtasks: [LIST_ALL_SUBTASKS]
              Use available specialized agents for delegation
              Execute independent tasks in parallel where possible"
    WAIT: For orchestrator completion
    UPDATE: tasks.md with results
  
  # Otherwise delegate individual tasks
  ELSE:
    FOR each parent_task assigned:
      ANALYZE: Task description against delegation rules
      
      # Check for agent match
      IF task matches backend_pattern AND has_backend_api_builder:
        USE: @agent:backend-api-builder
      ELIF task matches frontend_form_pattern AND has_onboarding_form_builder:
        USE: @agent:onboarding-form-builder
      ELIF task matches frontend_fix_pattern AND has_frontend_component_fixer:
        USE: @agent:frontend-component-fixer
      ELIF task matches test_pattern AND has_test_automation_engineer:
        USE: @agent:test-automation-engineer
      ELIF task matches validation_pattern AND has_field_validation_tester:
        USE: @agent:field-validation-tester
      ELIF task matches compliance_pattern AND has_compliance_validator:
        USE: @agent:compliance-validator
      ELSE:
        # Fallback to manual execution
        LOAD @~/.agent-os/instructions/execute-task.md
        EXECUTE manually with task details
      
      UPDATE: tasks.md status after completion
    END FOR
</execution_flow>

<batch_execution_example>
  # Example: Multiple similar tasks can be batched
  IF tasks include multiple "Fix employee name propagation for X PDF":
    COLLECT all similar tasks
    USE: @agent:backend-api-builder (single invocation)
    REQUEST: "Fix employee name propagation for ALL of these:
              1. Company Policies PDF
              2. Direct Deposit PDF
              3. Health Insurance PDF
              4. Weapons Policy PDF
              Pull names from PersonalInfoStep data
              Update all endpoints to use consistent pattern"
    WAIT: For batch completion
    UPDATE: All related tasks in tasks.md
</batch_execution_example>

<instructions>
  ACTION: Analyze each task for agent delegation potential
  PRIORITIZE: Agent delegation over manual execution
  BATCH: Similar tasks for efficient execution
  PARALLELIZE: Independent tasks when possible
  MONITOR: Agent progress and collect results
  FALLBACK: To manual execution only if no agent available
  UPDATE: Task status immediately after each completion
</instructions>

</step>

<step number="6" name="comprehensive_testing_with_agents">

### Step 6: Comprehensive Testing with Specialized Agents

<step_metadata>
  <runs>targeted tests using multiple specialized agents</runs>
  <parallelizes>different test types for efficiency</parallelizes>
  <ensures>complete coverage and compliance</ensures>
</step_metadata>

<parallel_test_strategy>
  IF specialized test agents available:
    LAUNCH in parallel:
      
      IF has_test_automation_engineer:
        USE: @agent:test-automation-engineer
        REQUEST: "Test all document generation endpoints:
                  - Verify PDF generation for all forms
                  - Test preview endpoints return base64
                  - Validate document accessibility
                  - Check error handling"
      
      IF has_field_validation_tester:
        USE: @agent:field-validation-tester  
        REQUEST: "Validate data flow and consistency:
                  - Test employee name propagation across forms
                  - Verify PersonalInfoStep data usage
                  - Check cross-form data consistency
                  - Validate all field requirements"
      
      IF has_compliance_validator:
        USE: @agent:compliance-validator
        REQUEST: "Verify federal compliance:
                  - Check I-9 Section 1 requirements
                  - Validate W-4 current year format
                  - Verify digital signature compliance
                  - Ensure document retention policies"
      
      IF has_test_runner:
        USE: @agent:test-runner
        REQUEST: "Run existing test suites:
                  - Backend unit tests
                  - Frontend component tests
                  - Integration tests"
    
    WAIT: For all test agents to complete
    CONSOLIDATE: Results from all agents
    
    IF any_failures:
      ANALYZE: Failure patterns
      DELEGATE: Fixes to appropriate agents
      RETEST: After fixes applied
  
  ELSE:
    # Fallback to single test runner or manual
    IF has_test_runner:
      USE: @agent:test-runner
      REQUEST: "Run the full test suite"
      WAIT: For test-runner analysis
      PROCESS: Fix any reported failures
      REPEAT: Until all tests pass
    ELSE:
      PROCEED: To manual test execution
</parallel_test_strategy>

<instructions>
  ACTION: Deploy multiple test agents in parallel
  COVERAGE: Different aspects tested simultaneously
  CONSOLIDATE: Gather results from all agents
  FIX: Delegate fixes to specialized agents
  VERIFY: All tests pass before proceeding
</instructions>

<conditional-block context-check="fallback-full-test-execution">
IF NOT using test-runner agent:
  READ: The following fallback test execution instructions

<fallback_test_execution>
  <test_execution>
    <order>
      1. Run entire test suite
      2. Fix any failures
    </order>
    <requirement>100% pass rate</requirement>
  </test_execution>

  <failure_handling>
    <action>troubleshoot and fix</action>
    <priority>before proceeding</priority>
  </failure_handling>

  <instructions>
    ACTION: Run complete test suite
    VERIFY: All tests pass including new ones
    FIX: Any test failures before continuing
    BLOCK: Do not proceed with failing tests
  </instructions>
</fallback_test_execution>
</conditional-block>

</step>

<step number="7" name="agent_result_consolidation">

### Step 7: Agent Result Consolidation

<step_metadata>
  <consolidates>results from all delegated agents</consolidates>
  <monitors>task completion status</monitors>
  <handles>any failures or blockers</handles>
</step_metadata>

<consolidation_process>
  COLLECT results from all agents used:
    - Execution status (success/failure/partial)
    - Files modified or created
    - Tests passed/failed
    - Warnings or recommendations
    - Time taken for each task
  
  VERIFY task completion:
    CHECK tasks.md for status updates
    CONFIRM all assigned tasks marked complete
    IDENTIFY any blocked or failed tasks
  
  HANDLE failures:
    IF task_failed:
      ANALYZE: Failure reason from agent report
      DETERMINE: If fixable with another agent
      IF fixable_with_agent:
        DELEGATE: Fix to appropriate specialist
        RETRY: Original task after fix
      ELSE:
        DOCUMENT: Blocker in tasks.md
        NOTIFY: User of manual intervention needed
</consolidation_process>

<success_criteria>
  ALL of the following must be true:
    - All parent tasks marked complete
    - All subtasks marked complete  
    - No blocking issues remain
    - All tests passing (if applicable)
    - Documentation updated
</success_criteria>

<instructions>
  ACTION: Gather all agent results
  VERIFY: Complete task execution
  DOCUMENT: Any issues or blockers
  ENSURE: Ready for commit/PR
</instructions>

</step>

<step number="8" name="git_workflow">

### Step 8: Git Workflow

<step_metadata>
  <creates>
    - git commit
    - github push
    - pull request
  </creates>
</step_metadata>

<instructions>
  IF has_git_workflow:
    USE: @agent:git-workflow
    REQUEST: "Complete git workflow for [SPEC_NAME] feature:
              - Spec: [SPEC_FOLDER_PATH]
              - Changes: All modified files
              - Target: main branch
              - Description: [SUMMARY_OF_IMPLEMENTED_FEATURES]"
    WAIT: For workflow completion
    PROCESS: Save PR URL for summary
  ELSE:
    PROCEED: To manual git workflow below
</instructions>

<conditional-block context-check="manual-git-workflow">
IF NOT using git-workflow agent:
  READ: The following manual git workflow

<commit_process>
  <commit>
    <message>descriptive summary of changes</message>
    <format>conventional commits if applicable</format>
  </commit>
  <push>
    <target>spec branch</target>
    <remote>origin</remote>
  </push>
  <pull_request>
    <title>descriptive PR title</title>
    <description>functionality recap</description>
  </pull_request>
</commit_process>

<pr_template>
  ## Summary

  [BRIEF_DESCRIPTION_OF_CHANGES]

  ## Changes Made

  - [CHANGE_1]
  - [CHANGE_2]

  ## Testing

  - [TEST_COVERAGE]
  - All tests passing ✓
</pr_template>

<instructions>
  ACTION: Commit all changes with descriptive message
  PUSH: To GitHub on spec branch
  CREATE: Pull request with detailed description
</instructions>
</conditional-block>

</step>

<step number="9" name="roadmap_progress_check">

### Step 9: Roadmap Progress Check (Conditional)

<step_metadata>
  <condition>only if tasks may have completed roadmap item</condition>
  <checks>@.agent-os/product/roadmap.md (if not in context)</checks>
  <updates>if spec completes roadmap item</updates>
</step_metadata>

<conditional_execution>
  <preliminary_check>
    EVALUATE: Did executed tasks potentially complete a roadmap item?
    IF NO:
      SKIP this entire step
      PROCEED to step 9
    IF YES:
      CONTINUE with roadmap check
  </preliminary_check>
</conditional_execution>

<conditional_loading>
  IF roadmap.md NOT already in context:
    LOAD @.agent-os/product/roadmap.md
  ELSE:
    SKIP loading (use existing context)
</conditional_loading>

<roadmap_criteria>
  <update_when>
    - spec fully implements roadmap feature
    - all related tasks completed
    - tests passing
  </update_when>
  <caution>only mark complete if absolutely certain</caution>
</roadmap_criteria>

<instructions>
  ACTION: First evaluate if roadmap check is needed
  SKIP: If tasks clearly don't complete roadmap items
  CHECK: If roadmap.md already in context
  LOAD: Only if needed and not in context
  EVALUATE: If current spec completes roadmap goals
  UPDATE: Mark roadmap items complete if applicable
  VERIFY: Certainty before marking complete
</instructions>

</step>

<step number="10" name="completion_notification">

### Step 10: Task Completion Notification

<step_metadata>
  <plays>system sound</plays>
  <alerts>user of completion</alerts>
</step_metadata>

<notification_command>
  afplay /System/Library/Sounds/Glass.aiff
</notification_command>

<instructions>
  ACTION: Play completion sound
  PURPOSE: Alert user that task is complete
</instructions>

</step>

<step number="11" name="completion_summary">

### Step 11: Completion Summary

<step_metadata>
  <creates>summary message</creates>
  <format>structured with emojis</format>
</step_metadata>

<summary_template>
  ## ✅ What's been done

  1. **[FEATURE_1]** - [ONE_SENTENCE_DESCRIPTION]
  2. **[FEATURE_2]** - [ONE_SENTENCE_DESCRIPTION]

  ## ⚠️ Issues encountered

  [ONLY_IF_APPLICABLE]
  - **[ISSUE_1]** - [DESCRIPTION_AND_REASON]

  ## 👀 Ready to test in browser

  [ONLY_IF_APPLICABLE]
  1. [STEP_1_TO_TEST]
  2. [STEP_2_TO_TEST]

  ## 📦 Pull Request

  View PR: [GITHUB_PR_URL]
</summary_template>

<summary_sections>
  <required>
    - functionality recap
    - pull request info
  </required>
  <conditional>
    - issues encountered (if any)
    - testing instructions (if testable in browser)
  </conditional>
</summary_sections>

<instructions>
  ACTION: Create comprehensive summary
  INCLUDE: All required sections
  ADD: Conditional sections if applicable
  FORMAT: Use emoji headers for scannability
</instructions>

</step>

</process_flow>

## Error Handling

<error_protocols>
  <blocking_issues>
    - document in tasks.md
    - mark with ⚠️ emoji
    - include in summary
  </blocking_issues>
  <test_failures>
    - fix before proceeding
    - never commit broken tests
  </test_failures>
  <technical_roadblocks>
    - attempt 3 approaches
    - document if unresolved
    - seek user input
  </technical_roadblocks>
</error_protocols>

<final_checklist>
  <verify>
    - [ ] Task implementation complete
    - [ ] All tests passing
    - [ ] tasks.md updated
    - [ ] Code committed and pushed
    - [ ] Pull request created
    - [ ] Roadmap checked/updated
    - [ ] Summary provided to user
  </verify>
</final_checklist>

## Agent Delegation Examples

<concrete_example>

### Example: Hotel Onboarding MVP Tasks

Given the tasks in `.agent-os/specs/2025-08-09-mvp-test-database-setup/tasks.md`:

1. **Setup Test Property and Manager**
   - Agent: `backend-api-builder`
   - Request: "Create test property in database with manager account. Property ID: test-prop-001, Manager: manager@demo.com"

2. **Fix Employee Name Propagation (Non-I-9/W-4)**
   - Agent: `backend-api-builder` (batch execution)
   - Request: "Fix employee name propagation for Company Policies, Direct Deposit, Health Insurance, and Weapons Policy PDFs. Pull names from PersonalInfoStep saved data instead of hardcoded values."

3. **Create Human Trafficking Document Generator**
   - Agent: `backend-api-builder`
   - Request: "Create HumanTraffickingDocumentGenerator class with content from hire packet pages 19, 21. Include hotline 1-888-373-7888 and signature section."

4. **Test All Document Previews**
   - Agent: `test-automation-engineer`
   - Request: "Test that Direct Deposit, Health Insurance, and Weapons Policy preview endpoints return valid base64 PDFs"

5. **Manager Document Access**
   - Agents: Multiple in parallel
     - `test-automation-engineer`: "Verify manager can view all employee documents"
     - `field-validation-tester`: "Check property isolation works correctly"

6. **End-to-End Testing**
   - Agent: `task-orchestrator`
   - Request: "Coordinate full workflow test: application, approval, onboarding, document generation"

### Parallel Execution Groups

**Group 1** (All name propagation fixes - parallel):
- backend-api-builder: Fix Company Policies PDF
- backend-api-builder: Fix Direct Deposit PDF  
- backend-api-builder: Fix Health Insurance PDF
- backend-api-builder: Fix Weapons Policy PDF

**Group 2** (After Group 1 completes):
- backend-api-builder: Create HumanTraffickingDocumentGenerator
- test-automation-engineer: Test all preview endpoints

**Group 3** (Final validation - parallel):
- test-automation-engineer: End-to-end testing
- field-validation-tester: Data consistency checks
- compliance-validator: Federal compliance verification

</concrete_example>

<usage_instructions>

### How to Use with /execute-tasks

1. **Simple Usage**: Just run `/execute-tasks` and the system will:
   - Detect available agents
   - Match tasks to appropriate agents
   - Execute in parallel where possible
   - Consolidate results

2. **Override Agent Selection**: If needed, specify preferred agent:
   ```
   /execute-tasks --prefer-agent=backend-api-builder
   ```

3. **Disable Agent Delegation**: For manual execution:
   ```
   /execute-tasks --no-agents
   ```

4. **Monitor Progress**: Agents will update tasks.md in real-time

</usage_instructions>
