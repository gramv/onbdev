# Port Standardization and QR Code Fix - Requirements

## Introduction

The QR code functionality is completely broken due to inconsistent port usage across the system. Multiple components are using different ports, causing QR codes to generate URLs that don't work. This spec establishes a systematic approach to fix port standardization and ensure QR codes work properly.

## Requirements

### Requirement 1: Port Standardization

**User Story:** As a system administrator, I want consistent port usage across all components so that the system works reliably.

#### Acceptance Criteria

1. WHEN the system starts THEN the backend SHALL always use port 8000
2. WHEN the frontend starts THEN it SHALL always use port 3000
3. WHEN port 3000 is occupied THEN the system SHALL kill conflicting processes or use port 3001 as fallback
4. WHEN any component references frontend URLs THEN it SHALL use the standardized port
5. WHEN configuration files are updated THEN all port references SHALL be consistent

### Requirement 2: QR Code URL Generation

**User Story:** As an HR manager, I want QR codes to generate correct URLs so that candidates can access job applications.

#### Acceptance Criteria

1. WHEN a QR code is generated THEN it SHALL contain the correct frontend URL with proper port
2. WHEN the QR service initializes THEN it SHALL detect the actual frontend port
3. WHEN the frontend port changes THEN the QR service SHALL update automatically
4. WHEN a QR code is scanned THEN it SHALL navigate to a working job application form
5. WHEN the job application form loads THEN it SHALL display the correct property information

### Requirement 3: Frontend Server Reliability

**User Story:** As a developer, I want the frontend server to start reliably so that the application is accessible.

#### Acceptance Criteria

1. WHEN the frontend server starts THEN it SHALL bind to the specified port successfully
2. WHEN the frontend server is running THEN it SHALL respond to HTTP requests within 2 seconds
3. WHEN the frontend server encounters port conflicts THEN it SHALL resolve them automatically
4. WHEN the frontend server crashes THEN it SHALL restart automatically
5. WHEN the frontend serves routes THEN React Router SHALL handle SPA routing correctly

### Requirement 4: System Health Monitoring

**User Story:** As a system administrator, I want to monitor system health so that I can identify issues quickly.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL verify all services are running on correct ports
2. WHEN a service fails THEN the system SHALL log the error and attempt recovery
3. WHEN ports are checked THEN the system SHALL report which processes are using which ports
4. WHEN the QR functionality is tested THEN it SHALL verify end-to-end workflow
5. WHEN issues are detected THEN the system SHALL provide clear diagnostic information

### Requirement 5: Configuration Management

**User Story:** As a developer, I want centralized port configuration so that changes are applied consistently.

#### Acceptance Criteria

1. WHEN port configurations are defined THEN they SHALL be stored in environment variables
2. WHEN the backend starts THEN it SHALL read port configuration from environment
3. WHEN the frontend starts THEN it SHALL read port configuration from environment
4. WHEN the QR service initializes THEN it SHALL read frontend URL from environment
5. WHEN configuration changes THEN all components SHALL use the updated values

## Success Criteria

- ✅ Backend consistently runs on port 8000
- ✅ Frontend consistently runs on port 3000 (or documented fallback)
- ✅ QR codes generate working URLs that open job application forms
- ✅ All HTTP requests to frontend complete within 2 seconds
- ✅ System can recover from port conflicts automatically
- ✅ End-to-end QR workflow works from generation to form submission

## Out of Scope

- Changing the overall system architecture
- Implementing new QR code features
- Modifying the job application form functionality
- Adding new ports or services

## Dependencies

- Backend server (FastAPI)
- Frontend server (Vite/React)
- QR code generation service
- Job application form component
- HR dashboard QR generation feature

## Assumptions

- Port 8000 is available for backend use
- Port 3000 is preferred for frontend (with 3001 as fallback)
- System has permission to kill conflicting processes
- Environment variables can be used for configuration
- React Router is properly configured for SPA routing