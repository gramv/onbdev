# WebSocket Integration Documentation

## Overview

The Hotel Onboarding System uses WebSocket connections to provide real-time updates to both Manager and HR dashboards. This ensures that users see immediate updates when important events occur in the system.

## Implementation Details

### WebSocket Hook (`src/hooks/use-websocket.ts`)

A custom React hook that manages WebSocket connections with the following features:
- Automatic connection management based on authentication status
- Automatic reconnection with exponential backoff
- Heartbeat mechanism to keep connections alive (every 30 seconds)
- Token-based authentication via query parameters
- Event message parsing and handling

### Dashboard Integration

#### Manager Dashboard (`src/components/layouts/ManagerDashboardLayout.tsx`)
Connected to handle the following real-time events:
- `new_application` - New job application submitted for their property
- `application_status_change` - Application status updates
- `manager_review_needed` - Alert when manager action is required
- `onboarding_completed` - Employee completes onboarding process
- `notification` - General notifications

#### HR Dashboard (`src/components/layouts/HRDashboardLayout.tsx`)
Connected to handle the following real-time events:
- `new_application` - New applications across all properties
- `application_status_change` - Status changes system-wide
- `manager_assigned` - New manager assignments to properties
- `property_created` - New properties added to the system
- `onboarding_completed` - Onboarding completions across all properties
- `compliance_alert` - Compliance-related alerts

## Connection Details

- **Endpoint**: `ws://localhost:8000/ws/dashboard`
- **Authentication**: JWT token passed as query parameter (`?token={jwt_token}`)
- **Heartbeat Interval**: 30 seconds
- **Reconnection**: Automatic with 3-second delay, max 5 attempts

## Visual Indicators

In development mode, both dashboards display:
- A pulsing green dot when connected
- A pulsing red dot when disconnected
- Connection status text below the dashboard title

## Usage

The WebSocket connection is automatically established when:
1. User is authenticated (has valid JWT token)
2. User has appropriate role (manager or hr)
3. Dashboard component is mounted

The connection automatically:
- Reconnects if disconnected unexpectedly
- Sends heartbeat messages to maintain connection
- Closes when user logs out or navigates away

## Event Handling

When a WebSocket event is received:
1. The event is logged to console (for debugging)
2. Dashboard stats are refreshed if needed
3. Toast notifications are shown for important events
4. Notification counts are updated

## Testing

Use the provided test script to verify WebSocket connectivity:

```bash
cd hotel-onboarding-backend
python3 test_websocket_connection.py
```

This script will:
- Create test JWT tokens
- Connect to the WebSocket endpoint
- Send test events
- Display received messages

## Monitoring

All WebSocket events are logged to the browser console with prefixes:
- `[WebSocket]` - Connection lifecycle events
- `[Manager Dashboard]` - Manager-specific events
- `[HR Dashboard]` - HR-specific events

## Troubleshooting

If WebSocket connection fails:
1. Check that backend is running on port 8000
2. Verify JWT token is valid and not expired
3. Check browser console for connection errors
4. Ensure no firewall/proxy blocking WebSocket connections
5. Verify user has appropriate role (manager or hr)