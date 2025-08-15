# Spec Requirements Document

> Spec: Fix Manager and HR Dashboards  
> Created: 2025-08-14
> Status: Planning

## Overview

Fix and enhance the Manager and HR dashboards to ensure proper functionality, data display, and property-based access control. Focus on making existing features work correctly without adding unnecessary complexity.

## User Stories

### Manager Dashboard Fix

As a Manager, I want to access my dashboard and see only my property's data, so that I can manage applications and employees effectively.

The manager logs in, sees their property information, views pending applications, can approve/reject applications, and access employee documents - all filtered to their specific property.

### HR Dashboard Implementation

As an HR user, I want a functional dashboard to oversee all properties and manage the entire onboarding workflow, so that I can ensure compliance and track system-wide metrics.

The HR user logs in, sees all properties, can filter by property, view all applications across the system, track onboarding progress, and generate reports.

## Spec Scope

1. **Fix Manager Dashboard API Integration** - Ensure all API calls work correctly with property filtering
2. **Implement HR Dashboard Components** - Create working HR dashboard with proper data display
3. **Add Property Access Control** - Ensure managers only see their property's data
4. **Implement Notification System** - Add basic email notifications for key events
5. **Add Real-time Updates** - Implement WebSocket connections for live dashboard updates

## Out of Scope

- Complex analytics and reporting features
- Bulk import/export functionality
- Advanced role customization
- Third-party integrations
- Mobile app development

## Expected Deliverable

1. Manager dashboard loads and displays property-specific data correctly
2. HR dashboard shows all properties with filtering capability
3. Email notifications work for application approval/rejection
4. Real-time updates show new applications immediately
5. All existing onboarding functionality remains intact