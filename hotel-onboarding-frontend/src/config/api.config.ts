/**
 * API Configuration
 * Centralized configuration for all API endpoints
 * Ensures consistent /api/ prefix usage across the application
 */

// API base prefix - all API endpoints should start with this
export const API_PREFIX = '/api';

/**
 * Helper function to create consistent API paths
 * Ensures all paths have the /api prefix and are properly formatted
 */
export const apiPath = (path: string): string => {
  // Remove any leading /api or api to avoid duplication
  let cleanPath = path.replace(/^\/?(api\/)?/, '');
  
  // Ensure path starts with /
  if (!cleanPath.startsWith('/')) {
    cleanPath = '/' + cleanPath;
  }
  
  // Return with API prefix
  return `${API_PREFIX}${cleanPath}`;
};

/**
 * Helper to build URL with query parameters
 */
export const apiUrl = (path: string, params?: Record<string, any>): string => {
  const url = apiPath(path);
  
  if (!params) return url;
  
  const queryString = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join('&');
  
  return queryString ? `${url}?${queryString}` : url;
};

/**
 * API endpoint definitions
 * All endpoints should be defined here for consistency
 */
export const API_ENDPOINTS = {
  // Authentication
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    me: '/auth/me',
    refresh: '/auth/refresh',
  },
  
  // HR endpoints
  hr: {
    dashboardStats: '/hr/dashboard-stats',
    properties: '/hr/properties',
    managers: '/hr/managers',
    employees: '/hr/employees',
    applications: '/hr/applications',
    analytics: '/hr/analytics',
    talentPool: '/hr/applications/talent-pool',
  },
  
  // Manager endpoints
  manager: {
    applications: '/manager/applications',
    property: '/manager/property',
    dashboardStats: '/manager/dashboard-stats',
    employeeSetup: '/manager/employee-setup',
  },
  
  // Onboarding endpoints
  onboarding: {
    start: '/onboarding/start',
    session: (token: string) => `/onboarding/session/${token}`,
    welcome: (token: string) => `/onboarding/welcome/${token}`,
    progress: (employeeId: string, stepId: string) => `/onboarding/${employeeId}/progress/${stepId}`,
    complete: (employeeId: string, stepId: string) => `/onboarding/${employeeId}/complete/${stepId}`,
    submit: (employeeId: string) => `/onboarding/${employeeId}/submit`,
    
    // Form data endpoints
    personalInfo: (employeeId: string) => `/onboarding/${employeeId}/personal-info`,
    i9Section1: (employeeId: string) => `/onboarding/${employeeId}/i9-section1`,
    i9Section2: (employeeId: string) => `/onboarding/${employeeId}/i9-section2`,
    i9Complete: (employeeId: string) => `/onboarding/${employeeId}/i9-complete`,
    w4Form: (employeeId: string) => `/onboarding/${employeeId}/w4-form`,
    directDeposit: (employeeId: string) => `/onboarding/${employeeId}/direct-deposit`,
    healthInsurance: (employeeId: string) => `/onboarding/${employeeId}/health-insurance`,
    
    // PDF generation endpoints
    generatePdf: {
      i9Section1: (employeeId: string) => `/onboarding/${employeeId}/i9-section1/generate-pdf`,
      w4Form: (employeeId: string) => `/onboarding/${employeeId}/w4-form/generate-pdf`,
      directDeposit: (employeeId: string) => `/onboarding/${employeeId}/direct-deposit/generate-pdf`,
      healthInsurance: (employeeId: string) => `/onboarding/${employeeId}/health-insurance/generate-pdf`,
      weaponsPolicy: (employeeId: string) => `/onboarding/${employeeId}/weapons-policy/generate-pdf`,
      humanTrafficking: (employeeId: string) => `/onboarding/${employeeId}/human-trafficking/generate-pdf`,
      companyPolicies: (employeeId: string) => `/onboarding/${employeeId}/company-policies/generate-pdf`,
    },
  },
  
  // Application endpoints
  applications: {
    submit: (propertyId: string) => `/apply/${propertyId}`,
    approve: (id: string) => `/applications/${id}/approve`,
    reject: (id: string) => `/applications/${id}/reject`,
    checkDuplicate: '/applications/check-duplicate',
  },
  
  // Property endpoints
  properties: {
    list: '/properties',
    info: (id: string) => `/properties/${id}/info`,
    stats: (id: string) => `/hr/properties/${id}/stats`,
    managers: (id: string) => `/hr/properties/${id}/managers`,
  },
  
  // Document endpoints
  documents: {
    upload: '/api/documents/upload',
    download: (id: string) => `/api/documents/${id}/download`,
    process: '/api/documents/process',
  },
  
  // Notification endpoints
  notifications: {
    list: '/notifications',
    count: '/notifications/count',
    markRead: '/notifications/mark-read',
  },
  
  // Compliance endpoints
  compliance: {
    auditTrail: '/compliance/audit-trail',
    dashboard: '/compliance/dashboard',
    i9Deadlines: (id: string) => `/compliance/i9-deadlines/${id}`,
  },
};

// Export for backward compatibility
export default {
  API_PREFIX,
  apiPath,
  apiUrl,
  endpoints: API_ENDPOINTS,
};